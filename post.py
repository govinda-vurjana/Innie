import os
import time
from pathlib import Path

try:
    from instagrapi import Client
except ImportError:
    print("Error: instagrapi not installed.")
    print("Install it with: pip install instagrapi")
    exit(1)


def get_grid_files(folder_path):
    """Get all grid_XX.png files sorted in reverse order for Instagram posting."""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' not found.")
        return []
    
    # Find all grid files
    grid_files = sorted(folder.glob("grid_*.png"))
    
    if not grid_files:
        print(f"Error: No grid_*.png files found in '{folder_path}'")
        return []
    
    # Reverse order (Instagram shows last posted at top-left)
    grid_files.reverse()
    
    return grid_files


def login_instagram(username, password, session_file="session.json"):
    """Login to Instagram and save/load session."""
    cl = Client()
    
    # Try to load existing session
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            cl.login(username, password)
            print("Logged in using saved session.")
            return cl
        except Exception as e:
            print(f"Saved session failed: {e}")
            print("Logging in fresh...")
    
    # Fresh login
    try:
        cl.login(username, password)
        cl.dump_settings(session_file)
        print("Logged in successfully and saved session.")
        return cl
    except Exception as e:
        print(f"Login failed: {e}")
        return None


def post_grid_images(folder_path, username, password, caption="", delay=5):
    """
    Post grid images to Instagram in reverse order.
    
    Args:
        folder_path: Path to folder containing grid_XX.png files
        username: Instagram username
        password: Instagram password
        caption: Caption for the posts (same for all)
        delay: Seconds to wait between posts (default: 5)
    """
    grid_files = get_grid_files(folder_path)
    if not grid_files:
        return
    
    print(f"\nFound {len(grid_files)} grid images to post.")
    print("Posting order (for correct grid alignment):")
    for i, file in enumerate(grid_files, 1):
        print(f"  {i}. {file.name}")
    
    confirm = input("\nProceed with posting? [y/n]: ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Cancelled.")
        return
    
    # Login
    cl = login_instagram(username, password)
    if not cl:
        return
    
    # Post each image
    print("\nStarting to post images...")
    for i, file_path in enumerate(grid_files, 1):
        try:
            print(f"\nPosting {i}/{len(grid_files)}: {file_path.name}")
            
            # Upload photo
            media = cl.photo_upload(
                path=str(file_path),
                caption=caption if i == 1 else ""  # Only caption on first post
            )
            
            print(f"✓ Posted successfully (Media ID: {media.pk})")
            
            # Wait between posts (except after last one)
            if i < len(grid_files):
                print(f"Waiting {delay} seconds before next post...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"✗ Failed to post {file_path.name}: {e}")
            retry = input("Continue with remaining posts? [y/n]: ").strip().lower()
            if retry not in ("y", "yes"):
                break
    
    print("\n✓ All done!")


def main():
    print("=== Instagram Grid Poster ===\n")
    
    folder_path = input("Enter folder path containing grid images: ").strip()
    username = input("Instagram username: ").strip()
    password = input("Instagram password: ").strip()
    caption = input("Caption for posts (optional): ").strip()
    
    try:
        delay = int(input("Delay between posts in seconds [default: 5]: ").strip() or "5")
    except ValueError:
        delay = 5
    
    post_grid_images(folder_path, username, password, caption, delay)


if __name__ == "__main__":
    main()
