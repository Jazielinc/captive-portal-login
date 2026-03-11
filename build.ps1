Param(
    [switch]$NoConsole = $true
)

Write-Host "Building Captive Portal Auto-Login App..."

$pyinstallerArgs = @("--onefile", "--name=CaptivePortalLogin")

if ($NoConsole) {
    $pyinstallerArgs += "--noconsole"
}

# Run PyInstaller
Write-Host "Running: pyinstaller $pyinstallerArgs main.py"
pyinstaller $pyinstallerArgs main.py

Write-Host "Build complete! Check the 'dist' folder for CaptivePortalLogin.exe."
