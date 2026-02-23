use zed_extension_api as zed;

struct ResoniteVRPlatformExtension;

impl zed::Extension for ResoniteVRPlatformExtension {
    fn new() -> Self {
        Self
    }

    fn context_server_command(
        &mut self,
        id: &zed::ContextServerId,
        _project: &zed::Project,
    ) -> zed::Result<zed::Command> {
        match id.as_ref() {
            "resonite-mcp" => Ok(zed::Command {
                command: "uv".to_string(),
                args: vec!["run".to_string(), "resonite-mcp".to_string()],
                env: Default::default(),
            }),
            _ => Err(format!("Unknown server: {}", id.as_ref())),
        }
    }
}

zed::register_extension!(ResoniteVRPlatformExtension);
