import win32gui
import win32ui
from ctypes import windll
import win32api
import win32con
import sys
from PIL import Image, ImageSequence
import cv2
import time
import pygame
import threading
import base64
from io import BytesIO
import pygetwindow as gw

class mediaControl:
    def __init__(self):
        self.paused = False
        self.seek_frame = 0
        self.lock = threading.Lock()
    def pause(self):
        with self.lock:
            self.paused = not self.paused
            #print(f"\n{self.paused=}")
    def seek(self, n):
        with self.lock:
            print(f"\n{n=}")
            self.seek_frame = n

control = mediaControl()

pygame.init()
pygame.mixer.init()
def playFile(path:str):
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)
    while pygame.mixer.music.get_busy():
        if control.paused:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
            while control.paused:
                time.sleep(0.1)
            pygame.mixer.music.unpause()
        time.sleep(0.1)

def rgb(*args, m:str="f", Max:float=255) -> str:
    """
    returns the ANSI escape sequence for a rgb color.
    can be for foreground (text color) or background (bg color)

    Args:
        r:
            the amount of red (0 - 255)
        g:
            the amount of green (0 - 255)
        b:
            the amount of blue (0 -255)
        m:
            determines weather the color will be applied to the text or bg. 
            ("f" for text/"b" for back ground)
        Max:
            determines the range of r,g,b, and can allow for normalized inputs
            keep in mind once r,g,b have been formatted to the range (0-255) 
            they will be rounded to the nearest int.

    Returns:
        a ANSI escape sequence of the rgb color.

    Example:
        >>> print(f'{rgb(100, 0, 200, "b")} hello')
        >>> # prints hello highlighted with a puprle color

    Notes:
        values outside the valid range are clamped.
    """
    if not args:
        return ""

    if isinstance(args[0], tuple):
        tup = args[0]
        r, g, b = tup[0], tup[1], tup[2]
        if len(tup) > 3: m = tup[3]
        if len(tup) > 4: Max = tup[4]
        if len(args) > 1: m = args[1]
        if len(args) > 2: Max = args[2]
    elif isinstance(args[0], (int, float)):
        r, g, b = args[0], args[1], args[2]
        if len(args) > 3: m = args[3]
        if len(args) > 4: Max = args[4]
    
    else:
        return ""
    r_calc = int(round(255 * r / Max))
    g_calc = int(round(255 * g / Max))
    b_calc = int(round(255 * b / Max))
    
    r = max(0, min(255, r_calc))
    g = max(0, min(255, g_calc))
    b = max(0, min(255, b_calc))
    return f"\033[38;2;{r};{g};{b}m" if m.lower()[0] == "f" else f"\033[48;2;{r};{g};{b}m" if m.lower()[0] == "b" else ""


# sixel

def matrix_to_sixel(matrix, w, h, sx=1, sy=1):
    """[(r,g,b)...] -> 'sixtel'"""
    sixel_chars = ['@', 'A', 'C', 'G', 'O', '_']
    payload = [f"\033[{sy};{sx}H\033Pq"]
    
    for y_band in range(0, h, 6):
        for sub_y in range(6):
            actual_y = y_band + sub_y
            if actual_y >= h:
                break
                
            for x in range(w):
                r, g, b = matrix[actual_y][x]
                r_pct = r * 100 // 255
                g_pct = g * 100 // 255
                b_pct = b * 100 // 255
                payload.append(f"#0;2;{r_pct};{g_pct};{b_pct}#0{sixel_chars[sub_y]}")
            payload.append("$")
        payload.append("-")
        
    payload.append("\033\\")
    return "".join(payload)

def img_pixel_matrix(path, max_width=None, sharpen=False):
    """takes img, and converts it to array"""
    try:
        img = Image.open(path).convert('RGB')
    except Exception as e:
        print(f"Error loading image: {e}")
        return None, 0, 0
    
    # resize img
    w, h = img.size
    aspect_ratio = h / w
    if max_width: w = max_width
    h = int(w * aspect_ratio)
    resample_filter = Image.Resampling.NEAREST if sharpen else Image.Resampling.LANCZOS
    img = img.resize((w, h), resample_filter)
    
    img_data = img.load()
    matrix = []
    
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = img_data[x, y]
            row.append((r, g, b))
        matrix.append(row)

    return matrix, w, h

def img(path, mw=None, sx=1, sy=1, sharpen=False):
    """Draws a static image instantly at targeted coordinates"""
    matrix, w, h = img_pixel_matrix(path, max_width=mw, sharpen=sharpen)
    if matrix:
        sys.stdout.write(matrix_to_sixel(matrix, w, h, sx, sy))
        sys.stdout.flush()

def GIF(path, mw=None, sx=0, sy=0, speed=10):
    """Plays a GIF smoothly"""
    try:
        gif = Image.open(path)
    except Exception as e:
        print(f"Error loading GIF: {e}")
        return

    print("\033[?25l")

    try:
        while True:
            for frame in ImageSequence.Iterator(gif):
                start_frame_time = time.time()
                duration = frame.info.get('duration', speed) / 1000.0
                frame = frame.convert('RGB')
                w, h = frame.size
                aspect = h / w
                
                if mw: w = mw
                h = int(w * aspect)
                frame = frame.resize((w, h), Image.Resampling.NEAREST)
                img_data = frame.load()
                matrix = [[img_data[x, y] for x in range(w)] for y in range(h)]
                
                sys.stdout.write(matrix_to_sixel(matrix, w, h, sx, sy))
                sys.stdout.flush()
                
                elapsed = time.time() - start_frame_time
                if elapsed < duration:
                    time.sleep(duration - elapsed)
    except KeyboardInterrupt:
        print("\033[?25h") # Show cursor

def video(path, mw=60, sx=1, sy=1, protocol="kitty"):
    """Plays a video file smoothly using Kitty or Sixel"""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / fps

    try:
        while cap.isOpened():
            start_time = time.time()
            ret, frame = cap.read()
            if not ret: break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame_rgb.shape
            aspect = h / w
            
            if mw: w = mw
            h = int(w * aspect)

            pil_img = Image.fromarray(frame_rgb).resize((w, h), Image.Resampling.NEAREST)
            if protocol == "kitty":
                render_str = k_img(pil_img, sx, sy)
            else:
                # Fallback to Sixel
                img_data = pil_img.load()
                matrix = [[img_data[x, y] for x in range(w)] for y in range(h)]
                render_str = matrix_to_sixel(matrix, w, h, sx, sy)
            
            sys.stdout.write(render_str)
            sys.stdout.flush()
            
            elapsed = time.time() - start_time
            if elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)
    finally:
        cap.release()


# kitty stuff

def k_img(img, sx=1, sy=1):
    """img to kitty so makes imgs look way better in terminal"""
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    png_data = buffer.getvalue()
    b64_data = base64.standard_b64encode(png_data).decode('ascii')
    payload = [f"\033[{sy};{sx}H"]
    chunk_size = 4096
    for i in range(0, len(b64_data), chunk_size):
        chunk = b64_data[i:i+chunk_size]
        m = 1 if i + chunk_size < len(b64_data) else 0
        if i == 0:
            payload.append(f"\033_Ga=T,f=100,m={m};{chunk}\033\\")
        else:
            payload.append(f"\033_Gm={m};{chunk}\033\\")
    return "".join(payload)

def get_window_image(hwnd):
    """asks Windows to render the window to a memory buffer"""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        return None
    
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

    img = None
    if result == 1:
        # bitmap -> PIL img
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB', 
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']), 
            bmpstr, 'raw', 'BGRX', 0, 1
        )
    # clean up
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img

def stream_window(name, mw=80, fps=20):
    frame_delay = 1.0 / fps
    print("\033[2J\033[?25l") 
    print(f"Waiting for window: '{name}'...")
    
    try:
        while True:
            start_time = time.time()
            
            windows = gw.getWindowsWithTitle(name)
            if not windows:
                sys.stdout.write(f"\r\033[K[!] Lost track of '{name}'. Waiting...")
                sys.stdout.flush()
                time.sleep(1)
                continue
            
            win = windows[0]
            hwnd = win._hWnd 

            img = get_window_image(hwnd)
            
            if img:
                aspect = img.height / img.width
                h = int(mw * aspect)
                img = img.resize((mw, h), Image.Resampling.LANCZOS)
                
                kitty_str = k_img(img, sx=1, sy=3)
                header = f"\033[1;1H\033[K[\033[1m {win.title} \033[0m]"
                
                sys.stdout.write(header + kitty_str)
                sys.stdout.flush()
            
            elapsed = time.time() - start_time
            if elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)
                
    except KeyboardInterrupt:
        print("\033[?25h\n\nStream stopped.")

def stream_screen(x,y,w,h,mw=80,fps=20):
    pass

def send_mouse_click(hwnd, tui_x, tui_y, terminal_w, terminal_h, win_rect):
    """mapper."""
    win_w = win_rect[2] - win_rect[0]
    win_h = win_rect[3] - win_rect[1]

    scale_x = win_w / terminal_w
    scale_y = win_h / terminal_h
    
    # coordinates
    lparam = win32api.MAKELONG(int(tui_x * scale_x), int(tui_y * scale_y))
    
    # send
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)

def send_key_press(hwnd, vk_code):
    """key presses."""
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)

def ascii_image_preview(path: str, width: int = 80, use_color: bool = True) -> str:
    with Image.open(path) as img:
        img = img.convert("RGB")
        
        if img.width <= 0 or img.height <= 0:
            return ""
        max_width = max(20, min(width, img.width))
        scale = max_width / img.width
        new_height = max(1, int(img.height * scale * 0.45))
        
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    chars = " .:-=+*#%@"
    num_chars = len(chars) - 1    
    pixels = img.getdata()
    lines = []
    row = []    
    for i, p in enumerate(pixels):
        lum = int(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2])
        idx = lum * num_chars // 255
        char = chars[idx]
        if use_color:
            char = rgb(p) + char
        row.append(char)        
        if (i + 1) % max_width == 0:
            if use_color:
                row.append("\033[0m") 
            lines.append("".join(row))
            row = []

    return "\n".join(lines) + "\n"

import os  # <-- was missing entirely

def loadFile(path, mw=None, sx=1, sy=1, p="k"):
    """
    Detects a file's type by extension and renders it in-terminal:
    images (kitty/sixel/ascii), animated gifs, video, or audio playback.

    Args:
        path:
            path to the file to load/display.
        mw:
            max render width, in terminal cells.
        sx:
            x cursor offset (images/video protocols only).
        sy:
            y cursor offset (images/video protocols only).
        p:
            render protocol: "k" kitty, "s" sixel, "a" ascii (color),
            "g" ascii (grayscale).

    Returns:
        None. Writes directly to stdout, or blocks while playing audio/video.

    Example:
        >>> loadFile("photo.png", 80, 1, 1, "k")

    Notes:
        Unrecognized extensions print a warning instead of failing silently.
    """
    f_img   = [".png", ".jpg", ".jpeg", ".jfif", ".bmp", ".webp"]
    f_video = [".mp4", ".mkv", ".mov"]
    f_gif   = [".gif"]
    f_audio = [".mp3", ".wav", ".ogg"]

    ext = os.path.splitext(path)[1].lower()

    if ext in f_img:
        if p in ("a", "g"):
            print(ascii_image_preview(path, mw if isinstance(mw, int) else 80, p == "a"))
        elif p == "s":
            img(path, mw, sx, sy)
        else:
            sys.stdout.write(k_img(Image.open(path).convert("RGB"), sx, sy))
            sys.stdout.flush()
    elif ext in f_gif:
        GIF(path, mw, sx, sy)
    elif ext in f_video:
        video(path, mw, sx, sy, "kitty" if p == "k" else "Sixel")
    elif ext in f_audio:
        playFile(path)
    else:
        print(f"{rgb(255, 100, 100)}Unsupported file type: '{ext}'\033[0m")