# Elise Bourgoignie
"""
Downloads Cleaner Script
------------------------
This Python script organizes files in the Downloads folder by categorizing them into
folders (Images, Music, Videos, Documents, and Others). It also checks if files
haven't been accessed in a specified time period (e.g., 3 months) and prompts the user
to either keep or delete them.

Features:
- Categorizes files into specific folders
- Detects old/inactive files and prompts user for deletion
- Logs all actions in a log file
- Test mode available (to simulate actions without making changes)
"""

import os
import shutil
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from send2trash import send2trash

class DownloadsCleaner:
    """
    A class to scan and organize the user's Downloads folder by moving files into categorized folders.
    It also checks file access times and prompts the user to delete old files.
    """

    def __init__(self):
        """
        Initializes configuration settings, file type categories, and log file location.
        """
        # === CONFIGURATION ===
        self.test_mode = True  # Set to False to actually move/delete files
        self.user = os.getenv("USERNAME")  # Get the logged-in username

        # Get the Downloads folder path dynamically
        self.downloads_path = os.path.join(Path.home(), "Downloads")

        # Log file path (inside Downloads folder)
        self.log_file = os.path.join(self.downloads_path, "download_organizer_log.txt")

        # Time threshold for considering a file "old" (in months)
        self.months_threshold = 3
        self.seconds_threshold = self.months_threshold * 30 * 24 * 60 * 60  # Convert months to seconds

        # File type categories with extensions
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
        self.music_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        self.document_extensions = {'.pdf', '.docx', '.xlsx', '.pptx', '.txt'}

        # Folder name mappings for categorized file organization
        self.folder_mapping = {
            "Images": self.image_extensions,
            "Music": self.music_extensions,
            "Videos": self.video_extensions,
            "Documents": self.document_extensions,
            "Others": set()  # Catch-all for unclassified files
        }

    def log_action(self, message):
        """
        Logs an action to the log file and optionally prints it to the console.

        Args:
            message (str): The message to log.
        """
        if self.test_mode:
            print(f"[TEST MODE] {message}")
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as log:
                log.write(f"[{timestamp}] {message}\n")
            print(message)  # Also print for visibility

    def file_has_expired(self, file_path):
        """
        Checks if a file hasn't been accessed in the defined time threshold.

        Args:
            file_path (str): The full path of the file.

        Returns:
            bool: True if the file is old, False otherwise.
        """
        last_access_time = os.path.getatime(file_path)  # Get last access timestamp
        current_time = time.time()  # Get current timestamp
        return (current_time - last_access_time) >= self.seconds_threshold

    def show_popup(self, file_path):
        """
        Displays a pop-up message asking the user if they want to delete an inactive file.

        Args:
            file_path (str): The full path of the file.

        Returns:
            bool: True if the user chooses to keep the file, False if deleted.
        """
        file_name = os.path.basename(file_path)  # Extract filename for display

        # Create a hidden root window for the pop-up
        root = tk.Tk()
        root.withdraw()

        # Ask user for deletion confirmation
        result = messagebox.askyesno(
            "Inactive File Detected",
            f"Hey! The file '{file_name}' hasn't been opened in {self.months_threshold} months.\n\n"
            "Would you like to DELETE it? (It will go to the Recycle Bin)."
        )

        if result:
            self.log_action(f"Deleted: {file_path}")
            if not self.test_mode:
                send2trash(file_path)  # Send to Recycle Bin
            return False  # File deleted, don't move it
        else:
            self.log_action(f"Kept: {file_path}")
            return True  # File kept, ready to be moved

    def move_file(self, file_path):
        """
        Moves a file to an appropriate folder based on its extension.

        Args:
            file_path (str): The full path of the file.
        """
        file_ext = os.path.splitext(file_path)[1].lower()  # Get file extension
        dest_folder = None  # Destination folder

        # Determine destination folder based on file type
        for folder, extensions in self.folder_mapping.items():
            if file_ext in extensions:
                dest_folder = os.path.join(self.downloads_path, f"Downloaded {folder}")
                break

        # Default to "Others" if file type is unknown
        if not dest_folder:
            dest_folder = os.path.join(self.downloads_path, "Downloaded Others")

        # Create the destination folder if it doesn't exist
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        # Define the new file destination path
        dest_path = os.path.join(dest_folder, os.path.basename(file_path))

        self.log_action(f"Moved: {file_path} → {dest_path}")

        if not self.test_mode:
            shutil.move(file_path, dest_path)

    def organize_downloads(self):
        """
        Scans the Downloads folder, checks file activity, prompts for deletion of inactive files,
        and moves the remaining files to appropriate folders.
        """
        if not os.path.exists(self.downloads_path):
            self.log_action(f"ERROR: Downloads directory '{self.downloads_path}' not found.")
            return

        self.log_action("\n=== File Organization Started ===")

        # Iterate through all files in the Downloads folder
        with os.scandir(self.downloads_path) as entries:
            for entry in entries:
                if entry.is_file():
                    file_path = os.path.join(self.downloads_path, entry.name)

                    # Check if the file is old
                    if self.file_has_expired(file_path):
                        keep_file = self.show_popup(file_path)
                        if not keep_file:
                            continue  # Skip moving if file was deleted

                    # Move the file to categorized folders
                    self.move_file(file_path)

        self.log_action("=== File Organization Completed ===\n")

# === MAIN EXECUTION ===
if __name__ == "__main__":
    cleaner = DownloadsCleaner()
    cleaner.organize_downloads()
