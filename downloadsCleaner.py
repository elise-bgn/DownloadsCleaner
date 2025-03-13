#Elise Bourgoignie
import os
import shutil
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from send2trash import send2trash

# === CONFIGURATION ===
test_mode = True  # Set to False to actually move/delete files
user = os.getenv("USERNAME")

# Get the Downloads folder path
downloads_path = os.path.join(Path.home(), "Downloads")

# Time threshold for showing the pop-up (e.g., 6 months)
months_threshold = 3
seconds_threshold = months_threshold * 30 * 24 * 60 * 60  # Convert months to seconds

# File type categories
image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
music_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
document_extensions = {'.pdf', '.docx', '.xlsx', '.pptx', '.txt'}

# Folder names
folder_mapping = {
    "Images": image_extensions,
    "Music": music_extensions,
    "Videos": video_extensions,
    "Documents": document_extensions,
    "Others": set()  # Catch-all for unclassified files
}

# === FUNCTION TO CHECK LAST ACCESS TIME ===
def file_has_expired(file_path, threshold_seconds):
    """Check if the file hasn't been accessed within the threshold."""
    last_access_time = os.path.getatime(file_path)
    current_time = time.time()
    return (current_time - last_access_time) >= threshold_seconds

# === POP-UP DIALOG ===
def show_popup(file_path):
    """Show a pop-up window with options to keep or delete the file."""
    file_name = os.path.basename(file_path)

    # Create the pop-up window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Show a message box with yes/no options
    result = messagebox.askyesno(
        "Inactive File Detected",
        f"Hey! The file '{file_name}' hasn't been opened in {months_threshold} months.\n\nWould you like to DELETE it? (It will go to the Recycle Bin).",
    )

    if result:
        if test_mode:
            print(f"[TEST MODE] Would send to Recycle Bin: {file_path}")
        else:
            send2trash(file_path)
            print(f"Sent to Recycle Bin: {file_path}")
        return False  # File deleted, don't move it
    else:
        print(f"File kept: {file_path}")
        return True  # File kept, ready to be moved

# === FILE ORGANIZATION ===
def move_file(file_path, destination_base):
    """Move the file to the appropriate folder."""
    file_ext = os.path.splitext(file_path)[1].lower()
    dest_folder = None

    # Find the matching folder
    for folder, extensions in folder_mapping.items():
        if file_ext in extensions:
            dest_folder = os.path.join(destination_base, f"Downloaded {folder}")
            break

    # Handle uncategorized files
    if not dest_folder:
        dest_folder = os.path.join(destination_base, "Downloaded Others")

    # Create folder if it doesn't exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Move the file
    dest_path = os.path.join(dest_folder, os.path.basename(file_path))

    if test_mode:
        print(f"[TEST MODE] Would move: {file_path} → {dest_path}")
    else:
        shutil.move(file_path, dest_path)
        print(f"Moved: {file_path} → {dest_path}")

# === SCAN & PROCESS FILES ===
def organize_downloads():
    """Scan the downloads folder, check file activity, and organize the files."""
    if not os.path.exists(downloads_path):
        print(f"Downloads directory '{downloads_path}' not found.")
        return

    with os.scandir(downloads_path) as entries:
        for entry in entries:
            if entry.is_file():
                file_path = os.path.join(downloads_path, entry.name)

                # Check if the file is inactive
                if file_has_expired(file_path, seconds_threshold):
                    keep_file = show_popup(file_path)
                    if not keep_file:
                        continue  # Skip moving the file if deleted

                # Move the file if not deleted
                move_file(file_path, downloads_path)

# === MAIN EXECUTION ===
if __name__ == "__main__":
    organize_downloads()
