import os
import shutil
from PIL import Image

def fetch_spotlight(dest_folder="./wallpapers"):
    # The Windows Spotlight hidden assets path
    src = os.path.expandvars(r"%LocalAppData%\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets")
    
    if not os.path.exists(src):
        print(f"[!] cannot find spotlight folder. enable spotlight in windows settings.")
        return
    
    if os.path.exists(dest_folder):
        for f in os.listdir(dest_folder):
            os.remove(os.path.join(dest_folder, f))
    else:
        os.makedirs(dest_folder)

    count = 1
    files = os.listdir(src)
    
    print(f"[*] Loading...")
    
    for filename in files:
        path = os.path.join(src, filename)
        if os.path.getsize(path) > 150000:
            try:
                img = Image.open(path)
                if img.width > img.height:
                    new_name = f"{count}.jpg"
                    shutil.copy(path, os.path.join(dest_folder, new_name))
                    print(f" [+] Exported: {new_name}")
                    count += 1
            except:
                continue
                
    print("[*] Complete!")

if __name__ == "__main__":
    fetch_spotlight()