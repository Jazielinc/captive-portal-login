import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import config

def save_and_close(root, interval_var, logpath_var):
    try:
        new_interval = int(interval_var.get())
        if new_interval < 5:
             messagebox.showerror("Error", "Interval must be at least 5 seconds.")
             return
    except ValueError:
        messagebox.showerror("Error", "Interval must be a valid number.")
        return
        
    new_logpath = logpath_var.get().strip()
    if not new_logpath:
        messagebox.showerror("Error", "Log path cannot be empty.")
        return

    new_config = {
        "check_interval_seconds": new_interval,
        "log_path": new_logpath
    }
    
    if config.save_config(new_config):
        messagebox.showinfo("Success", "Settings saved! They will apply immediately to the background process.")
        root.destroy()
    else:
        messagebox.showerror("Error", "Failed to save settings to configuration file.")

def browse_log_file(logpath_var):
    filename = filedialog.asksaveasfilename(
        defaultextension=".log",
        filetypes=[("Log Files", "*.log"), ("All Files", "*.*")],
        title="Select Log File Location"
    )
    if filename:
        logpath_var.set(filename)

def run_settings_ui():
    current_config = config.load_config()
    
    root = tk.Tk()
    root.title("Captive Portal Auto-Login Settings")
    root.geometry("450x200")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    
    # Configure grid layout
    root.columnconfigure(1, weight=1)
    
    # Check Interval setup
    tk.Label(root, text="Check Interval (Seconds):", anchor="w").grid(row=0, column=0, padx=10, pady=(20, 10), sticky="w")
    interval_var = tk.StringVar(value=str(current_config.get("check_interval_seconds", 30)))
    interval_entry = tk.Entry(root, textvariable=interval_var, width=10)
    interval_entry.grid(row=0, column=1, padx=10, pady=(20, 10), sticky="w")
    
    # Log File setup
    tk.Label(root, text="Log File Path:", anchor="w").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    logpath_var = tk.StringVar(value=current_config.get("log_path", config.DEFAULT_LOG_PATH))
    logpath_entry = tk.Entry(root, textvariable=logpath_var)
    logpath_entry.grid(row=1, column=1, padx=(10, 0), pady=10, sticky="ew")
    
    browse_btn = tk.Button(root, text="Browse...", command=lambda: browse_log_file(logpath_var))
    browse_btn.grid(row=1, column=2, padx=10, pady=10)

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.grid(row=2, column=0, columnspan=3, pady=(20, 10))
    
    save_btn = tk.Button(btn_frame, text="Save Settings", width=15, bg="#006fff", fg="white", 
                         command=lambda: save_and_close(root, interval_var, logpath_var))
    save_btn.pack(side=tk.LEFT, padx=10)
    
    cancel_btn = tk.Button(btn_frame, text="Cancel", width=10, command=root.destroy)
    cancel_btn.pack(side=tk.LEFT)

    root.mainloop()

if __name__ == "__main__":
    run_settings_ui()
