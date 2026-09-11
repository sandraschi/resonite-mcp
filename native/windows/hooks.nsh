; Fleet Tauri: kill UI + backend before install/uninstall (backend locks resources/*.exe).
!macro KillFleetProcesses
  DetailPrint "Stopping resonite MCP processes..."
  ExecWait 'taskkill /F /IM resonite-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM resonite-mcp-native.exe /T' $0
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillFleetProcesses
!macroend
