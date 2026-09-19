import os
import shutil
import tempfile
from PIL import Image, ImageChops

def are_images_identical(img1_path, img2_path):
    try:
        with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
            if img1.size != img2.size or img1.mode != img2.mode:
                return False
            return ImageChops.difference(img1, img2).getbbox() is None
    except (OSError, ValueError):
        return False


def is_duplicate(image_path, dest_folder):
    return any(
        are_images_identical(image_path, entry.path)
        for entry in os.scandir(dest_folder)
        if entry.is_file()
    )


def clean_and_rename_images(dest_folder="./wallpapers"):
    if not os.path.isdir(dest_folder):
        return

    image_paths = []
    for entry in sorted(os.scandir(dest_folder), key=lambda item: item.name.lower()):
        if not entry.is_file():
            continue
        try:
            with Image.open(entry.path):
                pass
        except (OSError, ValueError):
            continue

        duplicate_of = next(
            (path for path in image_paths if are_images_identical(entry.path, path)),
            None,
        )
        if duplicate_of is not None:
            os.remove(entry.path)
            print(f" [-] Removed duplicate: {entry.name} (matches {os.path.basename(duplicate_of)})")
        else:
            image_paths.append(entry.path)

    temporary_paths = []
    for image_path in image_paths:
        temporary_file, temporary_path = tempfile.mkstemp(
            prefix=".spotlight-rename-",
            suffix=".tmp",
            dir=dest_folder,
        )
        os.close(temporary_file)
        os.replace(image_path, temporary_path)
        temporary_paths.append(temporary_path)

    for count, temporary_path in enumerate(temporary_paths, start=1):
        new_path = os.path.join(dest_folder, f"{count}.jpg")
        os.replace(temporary_path, new_path)
        print(f" [*] Renamed: {os.path.basename(new_path)}")


def fetch_spotlight(dest_folder="./wallpapers"):
    # The Windows Spotlight hidden assets path
    src = os.path.expandvars(r"%LocalAppData%\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets")
    
    if not os.path.exists(src):
        print(f"[!] cannot find spotlight folder. enable spotlight in windows settings.")
        return
    
    count = 1
    if os.path.exists(dest_folder):
        count = sum(1 for entry in os.scandir(dest_folder) if entry.is_file()) + 1
    else:
        os.makedirs(dest_folder)

    files = os.listdir(src)
    
    print(f"[*] Loading...")
    
    for filename in files:
        path = os.path.join(src, filename)
        if os.path.getsize(path) > 150000:
            try:
                with Image.open(path) as img:
                    if img.width > img.height:
                        if is_duplicate(path, dest_folder):
                            continue
                        new_name = f"{count}.jpg"
                        shutil.copy(path, os.path.join(dest_folder, new_name))
                        print(f" [+] Exported: {new_name}")
                        count += 1
            except (OSError, ValueError):
                continue
                
    print("[*] Complete!")

#clean_and_rename_images("./wallpapers")

if __name__ == "__main__":
    fetch_spotlight()
    pass