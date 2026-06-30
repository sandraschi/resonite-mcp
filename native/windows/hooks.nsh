!macro KillFleetProcesses
  DetailPrint "Stopping resonite MCP processes..."
  ExecWait 'powershell -NoProfile -Command "Stop-Process -Name resonite-mcp-backend -Force -ErrorAction SilentlyContinue; Stop-Process -Name resonite-mcp-native -Force -ErrorAction SilentlyContinue; taskkill /F /IM resonite-mcp-backend.exe /T 2>$null; taskkill /F /IM resonite-mcp-native.exe /T 2>$null"' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "resonite-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "resonite-mcp-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "resonite-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "resonite-mcp-native.exe"
    Pop $0
  !endif
  Sleep 3000
!macroend

!macro UninstallPrevious
  DetailPrint "Checking for previous installation..."
  !if "${INSTALLMODE}" == "currentUser"
    ReadRegStr $R0 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${IDENTIFIER}" "UninstallString"
  !else
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${IDENTIFIER}" "UninstallString"
  !endif
  ${If} $R0 != ""
    DetailPrint "Removing previous installation..."
    ExecWait '"$R0" /S' $0
    DetailPrint "Previous uninstall exit code: $0"
    Sleep 1500
  ${EndIf}
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillFleetProcesses
  !insertmacro UninstallPrevious
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillFleetProcesses
!macroend
