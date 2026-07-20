use std::fs;
use std::io::{BufRead, BufReader, Write};
use std::net::{SocketAddr, TcpStream};
#[cfg(windows)]
use std::os::windows::process::CommandExt;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::str::FromStr;
use std::sync::Mutex;
use std::thread;
use std::time::Duration;
use tauri::{path::BaseDirectory, AppHandle, Emitter, Manager};

#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x08000000;

pub struct BackendProcess(pub Mutex<Option<Child>>);

const BACKEND_NAME: &str = "resonite-mcp-backend.exe";
const BACKEND_PORT: u16 = 10979;

/// Multi-layer port-clearing before spawn (fleet standard, nsis-build skill
/// Phase 1: `native/src/backend.rs`). A single `Stop-Process` call is not
/// enough -- orphaned child processes (e.g. a `uv run` wrapper surviving its
/// parent, per TRAPS_AND_PITFALLS.md #8) can hold the port even after the
/// installer's hooks.nsh has killed the main process tree. This runs on
/// every launch, not just install/uninstall, so a quick app restart where
/// the previous backend hasn't fully exited doesn't produce a false
/// "ready" signal against the OLD process.
fn free_port(app: &AppHandle, port: u16) {
    log_line(app, &format!("free_port: checking port {port}"));

    // Layer 1: find and Stop-Process the owning PID via Get-NetTCPConnection.
    let find_and_kill = format!(
        "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | \
         ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"
    );
    let _ = Command::new("powershell")
        .args(["-NoProfile", "-Command", &find_and_kill])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();

    // Layer 2: plain taskkill by name, in case the PID lookup above missed
    // a process running under a different session.
    let _ = Command::new("taskkill")
        .args(["/F", "/IM", BACKEND_NAME, "/T"])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();

    // Layer 3: UAC-elevated taskkill, for processes started with elevated
    // privileges that a non-elevated taskkill can't touch.
    let elevated = format!(
        "Start-Process taskkill -ArgumentList '/F','/IM','{BACKEND_NAME}','/T' -Verb RunAs -WindowStyle Hidden"
    );
    let _ = Command::new("powershell")
        .args(["-NoProfile", "-Command", &elevated])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();

    // Poll up to 240s for the port to actually free.
    let addr = SocketAddr::from_str(&format!("127.0.0.1:{port}")).unwrap();
    for attempt in 0..120 {
        if TcpStream::connect_timeout(&addr, Duration::from_millis(500)).is_err() {
            log_line(app, &format!("free_port: port {port} free after {attempt} checks"));
            return;
        }
        thread::sleep(Duration::from_secs(2));
    }
    log_line(app, &format!("free_port: port {port} still occupied after 240s -- spawn will likely fail"));
}

fn dev_backend_path() -> Option<PathBuf> {
    if !cfg!(debug_assertions) { return None; }
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("binaries")
        .join("resonite-mcp-backend-x86_64-pc-windows-msvc.exe");
    path.exists().then_some(path)
}

fn resolve_bundled_backend(app: &AppHandle) -> Result<PathBuf, String> {
    let mut tried = Vec::new();
    if let Ok(path) = app.path().resolve(BACKEND_NAME, BaseDirectory::Resource) {
        tried.push(path.display().to_string());
        if path.exists() { return Ok(path); }
    }
    let resources_path = format!("resources/{BACKEND_NAME}");
    if let Ok(path) = app.path().resolve(&resources_path, BaseDirectory::Resource) {
        tried.push(path.display().to_string());
        if path.exists() { return Ok(path); }
    }
    Err(format!("bundled backend missing (tried: {})", tried.join("; ")))
}

fn log_line(app: &AppHandle, message: &str) {
    eprintln!("[backend] {message}");
    if let Ok(dir) = app.path().app_log_dir() {
        let _ = fs::create_dir_all(&dir);
        let log_path = dir.join("backend-spawn.log");
        if let Ok(mut file) = fs::OpenOptions::new().create(true).append(true).open(log_path) {
            let _ = writeln!(file, "{message}");
        }
    }
}

fn materialize_backend(app: &AppHandle) -> Result<PathBuf, String> {
    if let Some(dev_path) = dev_backend_path() {
        log_line(app, &format!("using dev backend: {}", dev_path.display()));
        return Ok(dev_path);
    }
    let bundled = resolve_bundled_backend(app)?;
    log_line(app, &format!("using bundled backend: {}", bundled.display()));
    Ok(bundled)
}

pub fn spawn_backend(app: AppHandle, state: &BackendProcess) -> Result<String, String> {
    free_port(&app, BACKEND_PORT);

    let path = materialize_backend(&app)?;
    let mut cmd = Command::new(&path);
    cmd.args(["--port", "10979", "--log-level", "INFO"])
        .env("RESONITE_TAURI", "1")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    #[cfg(windows)]
    cmd.creation_flags(CREATE_NO_WINDOW);
    let mut child = cmd.spawn().map_err(|e| format!("spawn failed: {e}"))?;

    // First confirmation: watch stdout/stderr for the Uvicorn startup line.
    // Second confirmation (belt and suspenders): TCP-connect poll below --
    // the log line can be missed if buffering delays it, so neither signal
    // alone is treated as sufficient on its own.
    let app_log_stdout = app.clone();
    if let Some(stdout) = child.stdout.take() {
        thread::spawn(move || {
            for line in BufReader::new(stdout).lines().map_while(Result::ok) {
                log_line(&app_log_stdout, &format!("[backend stdout] {line}"));
                if line.contains("Uvicorn running") {
                    let _ = app_log_stdout.emit("backend-status", "ready");
                }
            }
        });
    }
    let app_log_stderr = app.clone();
    if let Some(stderr) = child.stderr.take() {
        thread::spawn(move || {
            for line in BufReader::new(stderr).lines().map_while(Result::ok) {
                log_line(&app_log_stderr, &format!("[backend stderr] {line}"));
            }
        });
    }

    state.0.lock().unwrap().replace(child);

    let addr = SocketAddr::from_str(&format!("127.0.0.1:{BACKEND_PORT}")).unwrap();
    let app_health = app.clone();
    thread::spawn(move || {
        for _attempt in 0..30 {
            thread::sleep(Duration::from_secs(2));
            if TcpStream::connect_timeout(&addr, Duration::from_secs(2)).is_ok() {
                let _ = app_health.emit("backend-status", "ready");
                return;
            }
        }
        let _ = app_health.emit("backend-status", "error: backend not reachable");
    });

    Ok("Backend starting on port 10979".into())
}
