import os
import sys
from pathlib import Path
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import terminal as t

RESET = t.color("default")
CYAN = t.rgb(120, 220, 255)
GREEN = t.rgb(120, 255, 160)
YELLOW = t.rgb(255, 205, 90)
RED = t.rgb(255, 110, 110)
WHITE = t.rgb(230, 230, 230)


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def kitty_image(img, sx=1, sy=1):
    from io import BytesIO
    import base64

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    png_data = buffer.getvalue()
    b64_data = base64.standard_b64encode(png_data).decode('ascii')
    payload = [f"\033[{sy};{sx}H"]
    chunk_size = 4096
    for i in range(0, len(b64_data), chunk_size):
        chunk = b64_data[i:i + chunk_size]
        m = 1 if i + chunk_size < len(b64_data) else 0
        if i == 0:
            payload.append(f"\033_Ga=T,f=100,m={m};{chunk}\033\\")
        else:
            payload.append(f"\033_Gm={m};{chunk}\033\\")
    return "".join(payload)


def resolve_path(base_path, arg):
    if not arg:
        return base_path
    expanded = os.path.expanduser(arg)
    if os.path.isabs(expanded):
        return expanded
    return os.path.abspath(os.path.join(base_path, expanded))


def nested_dict_dir(path):
    tree = {}
    try:
        items = sorted(os.listdir(path))
    except (PermissionError, OSError):
        return []

    files_list = []
    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            tree[item] = nested_dict_dir(full_path)
        else:
            files_list.append(item)

    if files_list:
        tree["__files__"] = files_list

    return tree


def list_directory(path):
    try:
        entries = sorted(os.listdir(path))
    except OSError as exc:
        print(f"{RED}Cannot list directory: {exc}{RESET}")
        return

    for entry in entries:
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            print(f"{CYAN}{entry}{RESET}/")
        else:
            print(f"{WHITE}{entry}{RESET}")


def is_image_file(path):
    return Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".jfif", ".gif", ".bmp", ".webp"}


def view_file(path):
    if not os.path.exists(path):
        print(f"{RED}File not found: {path}{RESET}")
        return

    if os.path.isdir(path):
        list_directory(path)
        return

    if is_image_file(path):
        try:
            from PIL import Image
            image = Image.open(path)
            sys.stdout.write(kitty_image(image))
            sys.stdout.flush()
        except Exception as exc:
            print(f"{RED}Image preview failed: {exc}{RESET}")
        return

    name = os.path.basename(path).lower()
    if name.endswith(".md") or "readme" in name:
        try:
            print("\n".join(t.mdGlow(path)))
        except Exception as exc:
            print(f"{RED}Markdown preview failed: {exc}{RESET}")
        return

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            print(file.read())
    except Exception as exc:
        print(f"{RED}Could not read file: {exc}{RESET}")


path = os.getcwd()
print(f"{GREEN}ANSI Explorer{RESET}")
print(f"{YELLOW}Type 'help' for commands.{RESET}")

while True:
    command = input(f"{CYAN}{path}{RESET} >>> ")
    command = command.replace("\ufeff", "").replace("ï", "").replace("»", "").replace("¿", "").strip()
    if not command:
        continue

    parts = command.split()
    cmd = parts[0].lower()
    args = parts[1:]

    if cmd in {"quit", "exit"}:
        break
    elif cmd in {"cls", "clear"}:
        clear_screen()
    elif cmd in {"help", "?"}:
        print(f"{YELLOW}Commands:{RESET}")
        print("  ls, dir              - list the current directory")
        print("  cd <path>            - change directory")
        print("  cd ..                - go up one directory")
        print("  cls, clear           - clear the screen")
        print("  view <file>          - view a file or image")
        print("  pwd                  - print current directory")
        print("  help                 - show this help")
        print("  quit                 - exit")
    elif cmd in {"pwd", "printwd"}:
        print(path)
    elif cmd in {"ls", "dir"}:
        target = path if not args else resolve_path(path, args[0])
        if os.path.isdir(target):
            list_directory(target)
        else:
            print(f"{RED}Not a directory: {target}{RESET}")
    elif cmd == "cd":
        if not args:
            print(path)
            continue
        target = resolve_path(path, args[0])
        if os.path.isdir(target):
            path = target
        else:
            print(f"{RED}Directory not found: {target}{RESET}")
    elif cmd == "view":
        if not args:
            print(f"{RED}Usage: view <file>{RESET}")
            continue
        target = resolve_path(path, args[0])
        view_file(target)
    else:
        print(f"{RED}Unknown command: {cmd}{RESET}")