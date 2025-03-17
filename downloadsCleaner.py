# Elise Bourgoignie
"""
Downloads Cleaner Script with GUI
---------------------------------
This Python script organizes files in a user-selected directory by categorizing them into
folders (Images, Music, Videos, Documents, and Others). It also detects inactive files
and prompts the user for deletion.

Features:
- Select any folder to scan (default: Downloads)
- Categorizes files into specific folders
- Detects old/inactive files and prompts user for deletion
- Logs all actions in a GUI window
- Test mode available (to simulate actions without making changes)
"""

import os
import shutil
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from send2trash import send2trash

class DownloadsCleaner:
    """A class to scan and organize a selected directory by categorizing and managing files."""

    def __init__(self, directory, test_mode=True):
        """Initialize with the selected directory and test mode setting."""
        self.test_mode = test_mode
        self.directory = directory

        # Log file path (inside selected directory)
        self.log_file = os.path.join(self.directory, "download_organizer_log.txt")

        # Time threshold for inactive files (in months)
        self.months_threshold = 3
        self.seconds_threshold = self.months_threshold * 30 * 24 * 60 * 60  # Convert to seconds

        # File categories
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
        self.music_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        self.document_extensions = {'.pdf', '.docx', '.xlsx', '.pptx', '.txt'}

        # Mapping file types to folders
        self.folder_mapping = {
            "Images": self.image_extensions,
            "Music": self.music_extensions,
            "Videos": self.video_extensions,
            "Documents": self.document_extensions,
            "Others": set()  # Catch-all
        }

        # UI reference (will be set in the GUI)
        self.log_widget = None

    def log_action(self, message):
        """Log an action to the log file and update the UI log box."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        if self.test_mode:
            print(f"[TEST MODE] {message}")
        else:
            with open(self.log_file, "a", encoding="utf-8") as log:
                log.write(log_entry)
            print(message)

        # Update log box in the UI if available
        if self.log_widget:
            self.log_widget.insert(tk.END, log_entry)
            self.log_widget.see(tk.END)  # Auto-scroll to the bottom

    def file_has_expired(self, file_path):
        """Check if a file hasn't been accessed within the threshold."""
        last_access_time = os.path.getatime(file_path)
        current_time = time.time()
        return (current_time - last_access_time) >= self.seconds_threshold

    def show_popup(self, file_path):
        """Prompt the user to decide whether to delete an old file."""
        file_name = os.path.basename(file_path)
        root = tk.Tk()
        root.withdraw()

        result = messagebox.askyesno(
            "Inactive File Detected",
            f"Hey! The file '{file_name}' hasn't been opened in {self.months_threshold} months.\n\n"
            "Would you like to DELETE it? (It will go to the Recycle Bin)."
        )

        if result:
            self.log_action(f"Deleted: {file_path}")
            if not self.test_mode:
                send2trash(file_path)
            return False  # File deleted
        else:
            self.log_action(f"Kept: {file_path}")
            return True  # File kept

    def move_file(self, file_path):
        """Move the file to its designated folder."""
        file_ext = os.path.splitext(file_path)[1].lower()
        dest_folder = None

        for folder, extensions in self.folder_mapping.items():
            if file_ext in extensions:
                dest_folder = os.path.join(self.directory, f"Downloaded {folder}")
                break

        if not dest_folder:
            dest_folder = os.path.join(self.directory, "Downloaded Others")

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        dest_path = os.path.join(dest_folder, os.path.basename(file_path))
        self.log_action(f"Moved: {file_path} → {dest_path}")

        if not self.test_mode:
            shutil.move(file_path, dest_path)

    def organize_downloads(self):
        """Scan the directory and process files."""
        if not os.path.exists(self.directory):
            self.log_action(f"ERROR: Directory '{self.directory}' not found.")
            return

        self.log_action("\n=== File Organization Started ===")

        with os.scandir(self.directory) as entries:
            for entry in entries:
                if entry.is_file():
                    file_path = os.path.join(self.directory, entry.name)

                    if self.file_has_expired(file_path):
                        keep_file = self.show_popup(file_path)
                        if not keep_file:
                            continue

                    self.move_file(file_path)

        self.log_action("=== File Organization Completed ===\n")


class CleanerApp:
    """GUI Application for the Downloads Cleaner."""

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Downloads Cleaner")
        self.root.geometry("500x400")

        # Folder Selection
        self.selected_folder = tk.StringVar()
        self.selected_folder.set(str(Path.home() / "Downloads"))

        tk.Label(root, text="Select Folder to Scan:").pack(pady=5)
        tk.Entry(root, textvariable=self.selected_folder, width=50).pack(pady=5)
        tk.Button(root, text="Browse", command=self.browse_folder).pack(pady=5)

        # Test Mode Toggle
        self.test_mode_var = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="Enable Test Mode", variable=self.test_mode_var).pack(pady=5)

        # Scan Button
        tk.Button(root, text="Scan & Organize", command=self.start_scan).pack(pady=10)

        # Log Display
        tk.Label(root, text="Log Output:").pack(pady=5)
        self.log_text = scrolledtext.ScrolledText(root, height=10, width=60)
        self.log_text.pack(pady=5)

    def browse_folder(self):
        """Open a dialog for the user to select a folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.selected_folder.set(folder_selected)

    def start_scan(self):
        """Start the scan process."""
        selected_dir = self.selected_folder.get()
        test_mode = self.test_mode_var.get()

        cleaner = DownloadsCleaner(selected_dir, test_mode)
        cleaner.log_widget = self.log_text  # Connect UI log box
        cleaner.organize_downloads()


# === MAIN EXECUTION ===
if __name__ == "__main__":
    root = tk.Tk()
    app = CleanerApp(root)
    root.mainloop()
