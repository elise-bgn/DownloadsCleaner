# Elise Bourgoignie
import os
import shutil
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
from send2trash import send2trash

class DownloadsCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Downloads Organizer")

        # === Default Settings ===
        self.user = os.getenv("USERNAME")
        self.downloads_path = os.path.join(Path.home(), "Downloads")  # Default directory
        self.test_mode = tk.BooleanVar(value=True)  # Default: Test Mode ON
        self.months_threshold = tk.IntVar(value=3)  # Default: 3 months
        self.log_file = self.create_log_file_path(self.downloads_path)  # Default log path based on initial directory

        # === File Type Categories ===
        self.folder_mapping = {
            "Images": {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'},
            "Music": {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'},
            "Videos": {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'},
            "Documents": {'.pdf', '.docx', '.xlsx', '.pptx', '.txt'},
            "Others": set()  # Catch-all
        }

        # === UI Elements ===
        self.create_ui()

    def create_ui(self):
        """Creates the UI elements."""
        # Directory selection
        tk.Label(self.root, text="Select Folder to Scan:").grid(row=0, column=0, sticky="w")
        self.dir_entry = tk.Entry(self.root, width=50)
        self.dir_entry.grid(row=0, column=1, padx=5)
        self.dir_entry.insert(0, self.downloads_path)  # Default path
        tk.Button(self.root, text="Browse", command=self.browse_directory).grid(row=0, column=2)

        # Months Threshold
        tk.Label(self.root, text="Delete files older than (months):").grid(row=1, column=0, sticky="w")
        self.months_entry = tk.Entry(self.root, width=5, textvariable=self.months_threshold)
        self.months_entry.grid(row=1, column=1, sticky="w")

        # Test Mode Checkbox
        self.test_checkbox = tk.Checkbutton(self.root, text="Enable Test Mode", variable=self.test_mode)
        self.test_checkbox.grid(row=2, column=0, columnspan=2, sticky="w")

        # Scan Button
        tk.Button(self.root, text="Scan & Organize", command=self.organize_downloads, bg="green", fg="white").grid(row=3, column=0, columnspan=3, pady=10)

    def browse_directory(self):
        """Allows the user to choose a directory to scan."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder_selected)

    def create_log_file_path(self, directory):
        """Creates a unique log file path with a timestamp in the name."""
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")  # Format the current timestamp
        return os.path.join(directory, f"download_organizer_log_{timestamp}.txt")

    def log_action(self, message):
        """Logs actions to the file or prints them in test mode."""
        if self.test_mode.get():
            print(f"[TEST MODE] {message}")
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as log:
                log.write(f"[{timestamp}] {message}\n")
            print(message)

    def file_has_expired(self, file_path):
        """Checks if the file hasn't been accessed within the threshold."""
        try:
            last_access_time = os.path.getatime(file_path)
            last_access_date = time.strftime("%B %d, %Y", time.localtime(last_access_time))
            current_time = time.time()
            threshold_seconds = self.months_threshold.get() * 30 * 24 * 60 * 60  # Convert months to seconds
            return (current_time - last_access_time) >= threshold_seconds, last_access_date
        except Exception as e:
            print(f"Error checking file access time: {e}")
            return False, "Unknown"

    def show_popup(self, file_path, last_access_date):
        """Shows a pop-up window with the file name and last accessed date."""
        file_name = os.path.basename(file_path)
        result = messagebox.askyesno(
            "Inactive File Detected",
            f"📁 **{file_name}**\n\nLast accessed on: {last_access_date}\n\nWould you like to DELETE it?\n(It will go to the Recycle Bin)."
        )

        if result:
            self.log_action(f"Deleted: {file_path}")
            if not self.test_mode.get():
                send2trash(file_path)
            return False  # File deleted
        else:
            self.log_action(f"Kept: {file_path}")
            return True  # File kept

    def move_file(self, file_path, destination_base):
        """Moves a file to the appropriate folder."""
        file_ext = os.path.splitext(file_path)[1].lower()
        dest_folder = None

        for folder, extensions in self.folder_mapping.items():
            if file_ext in extensions:
                dest_folder = os.path.join(destination_base, f"Downloaded {folder}")
                break

        if not dest_folder:
            dest_folder = os.path.join(destination_base, "Downloaded Others")

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        dest_path = os.path.join(dest_folder, os.path.basename(file_path))
        self.log_action(f"Moved: {file_path} → {dest_path}")

        if not self.test_mode.get():
            shutil.move(file_path, dest_path)

    def organize_downloads(self):
        """Scans the selected directory, checks file activity, and organizes files."""
        scan_path = self.dir_entry.get()

        if not os.path.exists(scan_path):
            self.log_action(f"ERROR: Directory '{scan_path}' not found.")
            return

        # Update the log file location based on the new directory
        self.log_file = self.create_log_file_path(scan_path)

        try:
            self.log_action("\n=== File Organization Started ===")

            with os.scandir(scan_path) as entries:
                for entry in entries:
                    if entry.is_file():
                        file_path = os.path.join(scan_path, entry.name)

                        expired, last_access_date = self.file_has_expired(file_path)
                        if expired:
                            keep_file = self.show_popup(file_path, last_access_date)
                            if not keep_file:
                                continue  # Skip moving if deleted

                        self.move_file(file_path, scan_path)

            self.log_action("=== File Organization Completed ===\n")
            messagebox.showinfo("Process Complete", "File organization has finished successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

# === RUN THE PROGRAM ===
if __name__ == "__main__":
    root = tk.Tk()
    app = DownloadsCleaner(root)
    root.mainloop()
