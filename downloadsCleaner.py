#Elise Bourgoignie
import os
import shutil
from pathlib import Path

# === CONFIGURATION ===
test_mode = True  # Set to False to actually move files
user = os.getenv("USERNAME")

# Get the Downloads folder path
downloads_path = os.path.join(Path.home(), "Downloads")
destination_base = downloads_path  # Organize within the Downloads folder

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

# === MAIN SCRIPT ===
def organize_downloads():
    if not os.path.exists(downloads_path):
        print(f"Downloads directory '{downloads_path}' not found.")
        return

    with os.scandir(downloads_path) as entries:
        for entry in entries:
            if entry.is_file():
                file_ext = os.path.splitext(entry.name)[1].lower()
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

                # Move or simulate move
                file_path = os.path.join(downloads_path, entry.name)
                dest_path = os.path.join(dest_folder, entry.name)

                if test_mode:
                    print(f"[TEST MODE] Would move: {file_path} → {dest_path}")
                else:
                    shutil.move(file_path, dest_path)
                    print(f"Moved: {file_path} → {dest_path}")

# Run the script
if __name__ == "__main__":
    organize_downloads()
