# Captive Portal Auto-Login

A lightweight, background Windows application written in Python that automatically detects and logs you into captive portals. It hides in your system tray and quietly connects you whenever it detects a portal intercepting your web traffic.

## Features

- **Automated Login**: Detects captive portals using Apple's reliable hotspot detection endpoint (`http://captive.apple.com/hotspot-detect.html`). It automatically clicks "Accept" links or submits login forms.
- **UniFi Support**: Includes specific fallback logic for modern React-based UniFi Hotspot Controllers, ensuring compatibility where standard HTML forms are missing.
- **Silent Operation**: Runs completely in the background without opening distracting console windows.
- **System Tray Integration**: Features a minimalist system tray icon for manual control.
- **Settings GUI**: Includes a built-in Tkinter UI to customize background check intervals and log file locations.
- **Granular Logging**: Keeps detailed connection state logs (connects/disconnects) to track uptime and login success.

## Usage

You have two options to use the app:

### 1. Download the Standalone Executable
You can download and run the pre-packaged `CaptivePortalLogin.exe` (found in the `dist` folder if built locally). 
- Double click it to start the background process. 
- You will see a small blue square icon appear in your Windows System Tray (bottom right).
- Right-click the icon to:
  * Force an immediate check.
  * Open the Settings UI.
  * Exit the application safely.

### 2. Run from Source / Build it Yourself

**Prerequisites:** Python 3.8+

1. Clone this repository:
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/captive-portal-login.git
cd captive-portal-login
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

4. **(Optional) Build the `.exe` yourself:**
You can use the included `build.ps1` PowerShell script or run PyInstaller manually to build a standalone, silent executable:
```bash
python -m PyInstaller --onefile --name=CaptivePortalLogin --noconsole main.py
```
The compiled executable will be placed in the `dist/` directory.

## Configuration

Settings are saved in `%USERPROFILE%\.captive_portal_config.json`. You can edit this file directly, or simply right-click the system tray icon and select **Settings...** to configure:

- **Check Interval:** How often the app pings to check for a captive portal (default 30 seconds).
- **Log Path:** Where the application writes its granular history.

## How it Works

1. The `main.py` script spawns an invisible background thread.
2. Every X seconds (based on your settings), `portal_checker.py` resolves a public DNS to check for total network failure.
3. If connected, it requests the Apple Hotspot URL.
4. If the response is intercepted (does not return the expected "Success"), parsing begins.
5. It looks for `<form>` tags and `<a>` links containing keywords like "accept", "login", or "connect".
6. If a UniFi portal is detected instead, a specifically crafted REST `POST` request is sent directly to the controller.
