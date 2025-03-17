#Elise Bourgoignie
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
        self.downloads_path = str(Path.home() / "Downloads")  # Default directory as a string
        self.test_mode = tk.BooleanVar(value=False)  # Default: Test Mode OFF
        self.months_threshold = tk.IntVar(value=3)  # Default: 3 months

        # Generate a unique log file name with a timestamp
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = self.generate_log_file(timestamp)

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
        tk.Button(self.root, text="Scan & Organize", command=self.organize_downloads, bg="green", fg="white").grid(
            row=3, column=0, columnspan=3, pady=10)

    def browse_directory(self):
        """Allows the user to choose a directory to scan."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder_selected)

    def log_action(self, message):
        """Logs actions to the file or prints them in test mode."""
        if self.test_mode.get():
            print(f"[TEST MODE] {message}")
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as log:
                log.write(f"[{timestamp}] {message}\n")
            print(message)

    def generate_log_file(self, timestamp):
        """Generates a log file with timestamp."""
        return os.path.join(self.downloads_path, f"download_organizer_log_{timestamp}.txt")

    def file_has_expired(self, file_path):
        """Checks if the file hasn't been modified within the threshold."""
        try:
            last_modified_time = os.path.getmtime(file_path)  # Get the last modification time
            current_time = time.time()  # Current time in seconds since the epoch
            threshold_seconds = self.months_threshold.get() * 30 * 24 * 60 * 60  # Convert months to seconds

            expired = (current_time - last_modified_time) >= threshold_seconds  # Check if the file is expired
            last_modified_date = time.strftime("%B %d, %Y",
                                               time.localtime(last_modified_time))  # Format the last modified date
            return expired, last_modified_date
        except Exception as e:
            print(f"Error checking file modification time: {e}")
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
                try:
                    send2trash(str(file_path))  # Ensure file path is a string
                except Exception as e:
                    self.log_action(f"Error deleting file: {e}")
            return False  # File deleted
        else:
            self.log_action(f"Kept: {file_path}")
            return True  # File kept

    def move_item(self, item_path, destination_base, is_folder=False):
        """Moves a file or folder to the appropriate folder, skipping log files."""
        item_path = str(item_path)  # Ensure the path is a string
        item_name = os.path.basename(item_path)

        # Skip log files (those that start with 'download_organizer_log_')
        if item_name.startswith("download_organizer_log_"):
            self.log_action(f"Skipped moving log file: {item_path}")
            return  # Skip moving log files

        # Determine destination folder
        dest_folder = self.get_destination_folder(item_path, is_folder)

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        # Destination path for file/folder
        dest_path = os.path.join(dest_folder, item_name)
        self.log_action(f"Moved: {item_path} → {dest_path}")

        if not self.test_mode.get():
            try:
                if is_folder:
                    shutil.move(item_path, dest_path)  # Move folder
                else:
                    shutil.move(item_path, dest_path)  # Move file
            except Exception as e:
                self.log_action(f"Error moving item: {e}")

    def get_destination_folder(self, item_path, is_folder=False):
        """Returns the appropriate destination folder for a file or folder."""
        if is_folder:
            return os.path.join(self.dir_entry.get(), "Downloaded Folders")

        file_ext = os.path.splitext(item_path)[1].lower()
        for folder, extensions in self.folder_mapping.items():
            if file_ext in extensions:
                return os.path.join(self.dir_entry.get(), f"Downloaded {folder}")
        return os.path.join(self.dir_entry.get(), "Downloaded Others")

    def organize_downloads(self):
        """Scans the selected directory, checks file activity, and organizes files and folders."""
        scan_path = self.dir_entry.get()

        if not os.path.exists(scan_path):
            self.log_action(f"ERROR: Directory '{scan_path}' not found.")
            return

        try:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            self.log_file = self.generate_log_file(timestamp)
            self.log_action("\n=== File and Folder Organization Started ===")

            with os.scandir(scan_path) as entries:
                for entry in entries:
                    item_path = os.path.join(scan_path, entry.name)

                    if entry.is_file():
                        # Handle files
                        expired, last_access_date = self.file_has_expired(item_path)
                        if expired:
                            keep_file = self.show_popup(item_path, last_access_date)
                            if not keep_file:
                                continue  # Skip moving if deleted
                        self.move_item(item_path, scan_path)

                    elif entry.is_dir():
                        # Handle folders
                        self.move_item(item_path, scan_path, is_folder=True)

            self.log_action("=== File and Folder Organization Completed ===\n")
            messagebox.showinfo("Process Complete", "File and folder organization has finished successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")


# === RUN THE PROGRAM ===
if __name__ == "__main__":
    root = tk.Tk()
    app = DownloadsCleaner(root)
    root.mainloop()
