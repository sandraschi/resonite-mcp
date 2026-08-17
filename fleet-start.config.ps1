# Per-repo fleet start config for resonite-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'resonite-mcp'
    BackendPort  = 10979
    FrontendPort = 10978
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\resonite-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'resonite_mcp.http_server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10979' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
