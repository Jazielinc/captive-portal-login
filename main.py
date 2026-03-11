import os
import sys
import threading
import time
import logging
import pystray
import subprocess
from PIL import Image, ImageDraw
from portal_checker import run_portal_check
import config

def setup_logging():
    cfg = config.load_config()
    log_path = cfg.get("log_path", config.DEFAULT_LOG_PATH)
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
    
    # Remove any existing handlers so we can reconfigure
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', filename=log_path, filemode='a')
    return log_path

def create_icon_image(color='blue'):
    """Creates a simple image for the system tray icon."""
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
        fill=color
    )
    return image

class PortalApp:
    def __init__(self):
        self.running = False
        self.thread = None
        self.icon = None
        self.last_connection_state = None

    def background_task(self):
        """The loop that periodically checks for captive portals."""
        logging.info("Background thread started. Captive Portal App is running.")
        while self.running:
            try:
                has_internet, is_captive, success = run_portal_check()
                
                if has_internet != self.last_connection_state:
                    if self.last_connection_state is not None:
                        if has_internet:
                            logging.info("PC re-connected to the network/internet.")
                        else:
                            logging.info("PC disconnected from the network.")
                    self.last_connection_state = has_internet
                    
            except Exception as e:
                logging.error(f"Error in background task: {e}")
            
            # Check interval dynamically based on config
            cfg = config.load_config()
            interval = cfg.get("check_interval_seconds", 30)
            
            for _ in range(interval):
                if not self.running:
                    break
                time.sleep(1)
        logging.info("Background thread stopped.")

    def run(self):
        """Starts the background thread and the system tray icon."""
        self.running = True
        self.thread = threading.Thread(target=self.background_task)
        self.thread.daemon = True
        self.thread.start()

        menu = pystray.Menu(
            pystray.MenuItem('Force Check Now', self.force_check),
            pystray.MenuItem('Settings...', self.open_settings),
            pystray.MenuItem('Exit', self.exit_action)
        )
        
        self.icon = pystray.Icon("name", create_icon_image("blue"), "Captive Login", menu)
        logging.info("System tray icon started.")
        self.icon.run()

    def force_check(self, icon, item):
        """Manually trigger a check."""
        logging.info("Manual check triggered.")
        # Visual feedback
        self.icon.icon = create_icon_image("green")
        try:
             has_internet, is_captive, success = run_portal_check()
             self.last_connection_state = has_internet
        except Exception as e:
             logging.error(f"Error in manual check: {e}")
        # Revert visually
        time.sleep(1)
        self.icon.icon = create_icon_image("blue")

    def open_settings(self, icon, item):
        """Opens the settings Tkinter UI in a separate process."""
        logging.info("Opening settings UI...")
        try:
            # sys.executable is the .exe when packaged, or python.exe when running script
            if getattr(sys, 'frozen', False):
                subprocess.Popen([sys.executable, "--settings"])
            else:
                subprocess.Popen([sys.executable, __file__, "--settings"])
        except Exception as e:
            logging.error(f"Error opening settings: {e}")

    def exit_action(self, icon, item):
        """Stops everything and exits."""
        logging.info("Exiting application...")
        self.running = False
        self.icon.stop()

if __name__ == "__main__":
    if "--settings" in sys.argv:
        import settings_ui
        settings_ui.run_settings_ui()
    else:
        setup_logging()
        app = PortalApp()
        app.run()
