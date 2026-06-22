import sys
import os
import random
import time
import re
import threading
from inputs import get_gamepad, UnpluggedError
import subprocess
import hid
import pyperclip
import serial.tools.list_ports
import shutil
import ctypes
import colorsys
from DataFetcher import *
from themeParser import *

class RawTerminal():
    def __init__(self):
        self.original_stdin_state = None
        self.original_stdout_state = None
        self.fd_in = sys.stdin.fileno() if sys.stdin.isatty() else None

    def __enter__(self):
        if self.fd_in is None:
            print("\033[31m[ERROR]\033[0m this terminal has mouse events disabled.\nplease use a diffrent terminal, to be able to use mouse.")
            return self
            
        if os.name == 'nt':
            import ctypes
            from ctypes import wintypes
            
            self.h_stdin = ctypes.windll.kernel32.GetStdHandle(-10)
            self.h_stdout = ctypes.windll.kernel32.GetStdHandle(-11)
            
            self.original_stdin_state = wintypes.DWORD()
            self.original_stdout_state = wintypes.DWORD()
            
            ctypes.windll.kernel32.GetConsoleMode(self.h_stdin, ctypes.byref(self.original_stdin_state))
            ctypes.windll.kernel32.GetConsoleMode(self.h_stdout, ctypes.byref(self.original_stdout_state))
            
            # input config
            in_mode = wintypes.DWORD(self.original_stdin_state.value)
            in_mode.value &= ~(0x0002 | 0x0004 | 0x0010 | 0x0040)
            in_mode.value |= (0x0080 | 0x0200)
            ctypes.windll.kernel32.SetConsoleMode(self.h_stdin, in_mode)
            
            # output config
            out_mode = wintypes.DWORD(self.original_stdout_state.value)
            out_mode.value |= (0x0001 | 0x0004)
            ctypes.windll.kernel32.SetConsoleMode(self.h_stdout, out_mode)
            
        else:
            import tty, termios
            self.old_settings = termios.tcgetattr(self.fd_in)
            tty.setraw(self.fd_in)
            
        return self

    def __exit__(self, type, value, traceback):
        if os.name == 'nt':
            import ctypes
            if self.original_stdin_state is not None:
                ctypes.windll.kernel32.SetConsoleMode(self.h_stdin, self.original_stdin_state)
            if self.original_stdout_state is not None:
                ctypes.windll.kernel32.SetConsoleMode(self.h_stdout, self.original_stdout_state)
        else:
            if self.fd_in is not None:
                import termios
                termios.tcsetattr(self.fd_in, termios.TCSADRAIN, self.old_settings)

# basic comands
ENABLE_MOUSE = "\x1b[?1000h\x1b[?1006h"
DISABLE_MOUSE = "\x1b[?1000l\x1b[?1006l"

ENABLE_MOUSE_D = "\x1b[?1002h\x1b[?1006h"
DISABLE_MOUSE_D = "\x1b[?1002l\x1b[?1006l"
CLEAR_SCREEN = "\033[H\033[J"
DoubleX = True

Debug = False

bg_color = ""


def clear(n=""):
    print(end=bg_color)
    os.system("cls" if os.name == "nt" else "clear")
    return n

def leadZero (i:int, d:int) -> str:
    """number, digits. (1,3) -> '001'"""
    return "0" * (d - len(str(i))) + str(i)

def rgb(r,g,b,m="f"):
    """0 to 255 for each color, foreground/background"""
    return f"\033[38;2;{r};{g};{b}m" if m.lower()[0] == "f" else "\033[48;2;{r};{g};{b}m" if m.lower() == "b" else ""

class cursor:
    """invis() and vis() may not cetain terminals."""
    def invis(self):
        return ("\033[?25l")
    def vis(self):
        return ("\033[?25h")
    def up(self, n=1):
        return (f"\033[{n}A")
    def down(self, n=1):
        return (f"\033[{n}B")
    def left(self, n=1):
        return (f"\033[{n}D")
    def right(self, n=1):
        return (f"\033[{n}C")
    def nextLine(self, n=1):
        return (f"\033[{n}E")
    def prevLine(self, n=1):
        return (f"\033[{n}F")
    def collum(self, n):
        return (f"\033[{n}G")
    def getPos(self):
        return ("\033[6n")
    def up1(self):
        return ("\033 M")
    def setPos(self, x="",y=""):
        return (f"\033[{y};{x}H")
    def savePos(self):
        return ("\033[s")
    def loadPos(self):
        return ("\033[u")
    def saveAll(self):
        return ("\0337")
    def loadAll(self):
        return ("\0338")
c = cursor()

chars = {
    #custom chars
    "BEL" : "\a",    # terminal bell
    "BS"  : "\b",    # backspace
    "HT"  : "\t",    # horizontal tab
    "LF"  : "\n",    # linefeed (newline)
    "VT"  : "\v",    # vertical tab
    "FF"  : "\f",    # formfeed (also: new page NP)
    "CR"  : "\r",    # carriage return
    "ESC" : "\x1B", # escape charater
    "DEL" : "\x7F"  # delete charater
}

class screen:
    class erase:
        def CtoEnd(self):
            return "\033[0J"
        def CtoStart(self):
            return "\033[1J"
        def all(self):
            return "\033[2J"
        def saved(self):
            return "\033[3J"
    def save(self):
        return "\033[?47h"
    def load(self):
        return "\033[?47l"

class line:
    class erase:
        def CtoEnd(self):
            return "\033[0K"
        def CtoStart(self):
            return "\033[1K"
        def all(self):
            return "\033[2K"

class graphics:
    """text decorators, add/remove"""
    add = {
        "none"          : "\033[0m",
        "bold"          : "\033[1m",
        "dim"           : "\033[2m",
        "italic"        : "\033[3m",
        "underline"     : "\033[4m",
        "Blink"         : "\033[5m",
        "Reverse"       : "\033[7m",
        "hidden"        : "\033[8m",
        "strikethrough" : "\033[9m"}
    remove = {
        "bold"          : "\033[22m",
        "dim"           : "\033[22m",
        "italic"        : "\033[23m",
        "underline"     : "\033[24m",
        "Blink"         : "\033[25m",
        "Reverse"       : "\033[27m",
        "hidden"        : "\033[28m",
        "strikethrough" : "\033[29m"}

def color(name="default", m="f", bright=False):
    """name, foreground/background (f,b), bright (true/false)"""
    names = ["black","red","green","yellow","blue","magenta","cyan","white",None,"default"]
    return f"\033[{names.index(name.lower()) + 30 + (10 if m.lower()[0] == 'b' else 0) + (60 if bright else 0)}m" if name else ""
   
def color256(id, m="f"):
    """
    0-7: standard colors (as in ESC [ 30-37 m)
    8-15: high intensity colors (as in ESC [ 90-97 m)
    16-231: 6 * 6 * 6 cube (216 colors): 16 + 36 * r + 6 * g + b (0 ≤ r, g, b ≤ 5)
    232-255: grayscale from dark to light in 24 steps.
    """
    return f"\033[{38 if m.lower()[0] == 'f' else 48};5;{id}m"

def setMode(id, m="add"):
    """0 <= id <= 7 or 13 <= id <= 19 , add/remove (a/r)
    Changes the screen width or type to the mode specified by id.
    0 - 40 x 25 monochrome (text)
    1 - 40 x 25 color (text)
    2 - 80 x 25 monochrome (text)
    3 - 80 x 25 color (text)
    4 - 320 x 200 4-color (graphics)
    5 - 320 x 200 monochrome (graphics)
    6 - 640 x 200 monochrome (graphics)
    7 - Enables line wrapping

    13 - 320 x 200 color (graphics)
    14 - 640 x 200 color (16-color graphics)
    15 - 640 x 350 monochrome (2-color graphics)
    16 - 640 x 350 color (16-color graphics)
    17 - 640 x 480 monochrome (2-color graphics)
    18 - 640 x 480 color (16-color graphics)
    19 - 320 x 200 color (256-color graphics)
    1049 - alternative buffer
    """
    return f"\033[{'=' if id != 1049 else '?'}{id}{'h' if m.lower()[0] == 'a' else 'l'}"

def divider(char="-"):
    terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
    print(char * terminal_width)

lsbd = ["TL","TR","BL","BR","H","V","LT","RT","TT","BT","C"]
symbolList = ["\u250c","\u2510","\u2514","\u2518","\u2500","\u2502","\u251c","\u2524","\u252c","\u2534","\u253c"]
# box drawings
def bd(id=lsbd,length=1,CC:str=color("default")):
    if len(id[0]) > 1:
        if len(id) == 2:
            id = [id[0],("H" if id[0][0] == id[1][0] else "V"),id[1]]
        elif len(id) > 2 and len(id[1]) > 1:
            lengths = length if isinstance(length, list) else [length] * (len(id) - 1)
            if len(lengths) < len(id) - 1:
                return ""
            result = CC + symbolList[lsbd.index(id[0])]
            for i in range(len(id) - 1):
                if id[i][0] != id[i+1][0]:
                    result += ((c.down(1) if id[i][0] == "T" else c.up(1)) + c.left(1) + symbolList[lsbd.index("V")]) * lengths[i]
                    result += (c.down(1) if id[i][0] == "T" else c.up(1)) + c.left(1) + symbolList[lsbd.index(id[i+1])]
                else:
                    result += ((c.left(2) if id[i][1] == "R" else "") + symbolList[lsbd.index("H")]) * lengths[i]
                    result += (c.left(2) if id[i][1] == "R" else "") + symbolList[lsbd.index(id[i+1])]        
            return result + "\033[0m"
    if id == lsbd:
        return ""
    elif len(id) == 3:
        return CC + symbolList[lsbd.index(id[0])] + symbolList[lsbd.index(id[1])] * length + symbolList[lsbd.index(id[2])] + "\033[0m"
    elif id == "V":
        return CC + (symbolList[lsbd.index(id)] + c.down(1) + c.left(1)) * length + "\033[0m"
    else:
        return CC + symbolList[lsbd.index(id)] * length + "\033[0m"

def HSVtoRGB(H:int,S:int,V:int):
    r, g, b = colorsys.hsv_to_rgb(H / 360, S / 100, V / 100)
    return (255 * r, 255 * g, 255 * b)

def HEXtoRGB(hex:str):
    return tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
#useful fancy stuff

#non standered inputs
# fancy stuff
TARGET_VID = 0x1A2C
TARGET_PID = 0x4DBC

def lsDevices():
    devices = hid.enumerate()
    device_list = []
    
    for d in devices:
        vendor_id = d['vendor_id']
        product_id = d['product_id']
        path = d['path'].decode('utf-8') if isinstance(d['path'], bytes) else d['path']
        
        line = f"VID: {vendor_id} | PID: {product_id} | path: {path}"
        device_list.append(line)
        print(f"Found: {line}")
    pyperclip.copy("\n".join(device_list))

def listen(device_info):
    """Opens an HID device and prints raw reports.
    a.k.a - don't use it if you don't undertand it."""
    try:
        device = hid.device()
        device.open_path(device_info['path'])
        device.set_nonblocking(True)
        
        # make it short
        label = device_info['path'].decode('utf-8').split('#')[-2]
        
        while True:
            data = device.read(64)
            if data:
                print(f"[{label}]: {list(data)}")
            time.sleep(0.01)
    except Exception as e:
        print(f"no connection to {label}: {e}")


NSI = []
CONTROLLER_STATE = {}
def poll_controller():
    """
    Background thread, that polls for irrgular inputs.
    """
    global NSI, CONTROLLER_STATE
    
    while True:
        try:
            events = get_gamepad()
            for event in events:
                if event.ev_type == "Sync":
                    continue
                CONTROLLER_STATE[event.code] = event.state
                input_data = {"type": event.ev_type, "code": event.code, "state": event.state}
                NSI.append(input_data)
                if event.code and Debug:
                    print(f"\rDebug Input: {event.code} = {event.state}   ")
                
        except UnpluggedError:
            CONTROLLER_STATE.clear()
            time.sleep(2)
        except Exception:
            time.sleep(1)
                
gamepad_thread = threading.Thread(target=poll_controller, daemon=True)
gamepad_thread.start()


def get_char(n=1):
    """reads inputs char by char."""
    if os.name == 'nt':
        try:
            return os.read(0, n).decode('utf-8', errors='ignore')
        except Exception:
            return ""
    else:
        return sys.stdin.read(n)

def char_available():
    """buffers inputs, and can see queue"""
    if os.name == 'nt':
        import msvcrt
        return msvcrt.kbhit()
    else:
        import select
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(dr)

def finput(prompt:str="", max_length:int=-1, tick_func:str='pass', long:bool=False, vis=True, inputs:list=["keyboard","mouse","arrows","ESC","controller"],drag:bool=False):
    """Fancy input, input that allows mouse inputs."""
    sys.stdout.write(prompt)
    sys.stdout.write(ENABLE_MOUSE_D if drag else ENABLE_MOUSE)
    sys.stdout.flush()

    user_input = ""
    buffer = ""
    mouse_regex = re.compile(r'\x1b\[<(\d+);(\d+);(\d+)([mM])')
    hide  = "\033[8m" if not vis else ""
    reset = "\033[28m" if not vis else ""

    result = {}

    try:
        while True:
            # a tick so you dont need to use threading
            exec(tick_func)
            time.sleep(0.01)

            rc = {}
            controller_updated = False
            if "controller" in inputs:
                while len(NSI) > 0: 
                    NSI.pop(0) 
                    controller_updated = True
            else:
                NSI.clear()

            if controller_updated:
                rc = []
                letter_buttons = ["BTN_SOUTH","BTN_EAST","BTN_NORTH","BTN_WEST","BTN_TL","BTN_TR","START","SELECT","BTN_THUMBL","BTN_THUMBR"]
                buttons_name = ["A_BTN","B_BTN","X_BTN","Y_BTN","L_BUMPER","R_BUMPER","START","SELECT","L_STICK_C","R_STICK_C"]
                var_buttons = ["ABS_Z","ABS_RZ","ABS_X","ABS_Y","ABS_RX","ABS_RY"]
                var_names   = ["L_TRIGGER","R_TRIGGER","L_STICK_X","L_STICK_Y","R_STICK_X","R_STICK_Y"]

                for code, state in list(CONTROLLER_STATE.items()):
                    
                    # Buttons
                    if code in letter_buttons and state == 1:
                        rc.append(buttons_name[letter_buttons.index(code)])
                    
                    # D-Pad
                    elif code == "ABS_HAT0Y" and state != 0:
                        rc.append(["","DPAD_DOWN","DPAD_UP"][state])
                    elif code == "ABS_HAT0X" and state != 0:
                        rc.append(["","DPAD_RIGHT","DPAD_LEFT"][state])
                    
                    #
                    elif code in var_buttons: 
                        name = var_names[var_buttons.index(code)]
                        # add deadzones, for stick drift.
                        deadzone = 5 if "Z" in code else 2500 
                        if abs(state) > deadzone:
                            rc.append((name, state))
                            
                    # evrything else
                    elif code not in letter_buttons and code not in ["ABS_HAT0Y", "ABS_HAT0X"] and code not in var_buttons:
                        if state != 0:
                            rc.append((code, state))

                # fancy stuff for performance
                last_rc = getattr(finput, "last_rc", None)
                if rc != last_rc:
                    finput.last_rc = rc
                    result["controller"] = rc
                    return result

            if not char_available():
                continue
            char = get_char(1)
            if not char:
                continue

            if buffer or char == '\x1b':
                if not buffer and char == '\x1b' and "ESC" in inputs:
                    time.sleep(0.01)
                    if not char_available():
                        return {"ESC":"ESC"}
                buffer += char    
                # stuff for mouse
                if buffer.startswith('\x1b[<') and "mouse" in inputs:
                    match = mouse_regex.search(buffer)
                    if match:
                        button, t_col, t_row, action = match.groups()
                        buffer = ""
                        
                        # Determine which button was clicked
                        if   button == '0' : btn_name = "Left Click"   if long else "LC"
                        elif button == '1' : btn_name = "Middle Click" if long else "MC"
                        elif button == '2' : btn_name = "Right Click"  if long else "RC"
                        elif button == '32': btn_name = "Left Drag"    if long else "LD"
                        elif button == '33': btn_name = "Middle Drag"  if long else "MD"
                        elif button == '34': btn_name = "Right Drag"   if long else "RD"
                        elif button == '64': btn_name = "Scroll Up"    if long else "SU"
                        elif button == '65': btn_name = "Scroll Down"  if long else "SD"
                        elif button == '3' : btn_name = "Release"      if long else "R"
                        else: btn_name = "Unknown"

                        result["mouse"] = (action, btn_name,t_col,t_row) # (m/M) (name) (y) (x)
                        return result
                elif buffer.startswith('\x1b[') and "arrows" in inputs:
                    if len(buffer) == 3 and buffer[2] in ('A', 'B', 'C', 'D'):
                        direction = {'A': 'UP', 'B': 'DOWN', 'C': 'RIGHT', 'D': 'LEFT'}[buffer[2]]
                        buffer = ""
                        result["arrows"] = direction
                        return result
                    if char.isalpha() and char not in ('A', 'B', 'C', 'D'): 
                        buffer = ""
                # other stuff
                elif buffer.startswith('\x1b['):
                    if char.isalpha(): 
                        buffer = ""
                        
                # clean up
                elif len(buffer) > 1 and buffer[1] != '[':
                    buffer = ""
                    
                # stops weird stuff
                if len(buffer) > 15:
                    buffer = ""
                    
                continue

            # normie text
            if "keyboard" not in inputs:
                continue

            if char in ('\n', '\r'):
                sys.stdout.write(hide + '\n' + reset)
                sys.stdout.flush()
                result["keyboard"] = user_input
                return result
                
            elif char in ('\x08', '\x7f'): # backspace
                if len(user_input) > 0:
                    user_input = user_input[:-1]
                    sys.stdout.write(hide + '\b \b' + reset)
                    sys.stdout.flush()
                    
            elif char.isprintable():
                user_input += char
                sys.stdout.write(hide + char + reset)
                sys.stdout.flush()
                
                # auto submit feuture
                if max_length != -1 and len(user_input) >= max_length:
                    sys.stdout.write(hide + ('\n' if vis else "\x1b[1K\x1b[1G") + reset)
                    sys.stdout.flush()
                    time.sleep(0.5)
                    result["keyboard"] = user_input
                    return result

    
    finally:
        sys.stdout.write(DISABLE_MOUSE_D if drag else DISABLE_MOUSE)
        sys.stdout.flush()


def clock_tick(x,y,c:str="\033[39m",cls:bool=True,b:bool=True,save:bool=False,CLS:bool=True):
    """Draws the time"""
    if b:
        place(int(x),int(y),c + f"[{time.strftime('%H:%M:%S')}]" + "\033[0m",cls=cls,save=save,CLS=CLS)
    else:
        place(int(x),int(y),c + f"{time.strftime('%H:%M:%S')}" + "\033[0m",cls=cls,save=save,CLS=CLS)

def place(x:int,y:int,msg:str,cls:bool=False,save:bool=False,CLS:bool=True):
    if cls: sys.stdout.write(CLEAR_SCREEN)
    if save: sys.stdout.write(c.savePos())
    CccC = '\x1b[K' if CLS else ''
    sys.stdout.write(f"\x1b[{y};{x}H{CccC}{msg}")
    if save: sys.stdout.write(c.loadPos())
    sys.stdout.flush()

# more ansi stuff:
class Canvas:
    def __init__(self,D=False):
        self.width, self.height = shutil.get_terminal_size()
        if D:
            if input(f"Canvas size initialized: {self.width}x{self.height}\nok: ") in ["overide","o"]:
                self.width, self.height = int(input("width: ")), int(input("height: "))
        self.buffer = [[" " for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [["\033[0m" for _ in range(self.width)] for _ in range(self.height)]

    def set_pixel(self, x, y, char, color="\033[0m"):
        if DoubleX:
            x *= 2
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y][x] = char
            self.colors[y][x] = color
            if DoubleX and (x + 1 < self.width):
                self.buffer[y][x + 1] = char
                self.colors[y][x + 1] = color

    def line(self, x1, y1, x2, y2, char="#", color="\033[0m"):
        """Bresenham's Line Algo"""
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            self.set_pixel(x1, y1, char, color)
            if x1 == x2 and y1 == y2: break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    def rect(self, x, y, w, h, char="#", color="\033[0m"):
        for i in range(w):
            self.set_pixel(x + i, y, char, color)
            self.set_pixel(x + i, y + h - 1, char, color)
        for i in range(h):
            self.set_pixel(x, y + i, char, color)
            self.set_pixel(x + w - 1, y + i, char, color)

    def circle(self, x, y, R, char="#",  color="\033[0m"):
        for i in range(2 * R):
            i += x - R
            for j in range(2 * R):
                j += y - R
                if (i - x)**2 + (j - y)**2 <= R:
                    self.set_pixel(i,j,char,color)

    def draw(self, L, char=" ", Color={"any":color("default")}):
        for y, row in enumerate(L):
            for x, Char in enumerate(row):
                color_code = Color.get(Char, Color.get("any", "\033[0m"))
                self.set_pixel(x, y, char, color_code)
                
    
    def render(self):
        """renders the stuff"""
        output = []
        output.append("\033[H") 
        for y in range(self.height - 1):
            for x in range(self.width):
                output.append(f"{self.colors[y][x]}{self.buffer[y][x]}")
        sys.stdout.write("".join(output))
        sys.stdout.flush()

#fav-color pallate, (in rgb)
catppuccin_mocha_rgb = {
    "rosewater": (245, 224, 220),
    "flamingo": (242, 205, 205),
    "pink": (245, 194, 231),
    "mauve": (203, 166, 247),
    "red": (243, 139, 168),
    "maroon": (235, 160, 172),
    "peach": (250, 179, 135),
    "yellow": (249, 226, 175),
    "green": (166, 227, 161),
    "teal": (148, 226, 213),
    "sky": (137, 220, 235),
    "sapphire": (116, 199, 236),
    "blue": (137, 180, 250),
    "lavender": (180, 190, 254),
    "text": (205, 214, 244),
    "subtext1": (186, 194, 222),
    "subtext0": (166, 173, 200),
    "overlay2": (148, 156, 187),
    "overlay1": (127, 132, 156),
    "overlay0": (108, 112, 128),
    "surface2": (88, 91, 112),
    "surface1": (69, 71, 90),
    "surface0": (49, 50, 68),
    "base": (30, 30, 46),
    "mantle": (24, 24, 37),
    "crust": (17, 17, 27),
}

C = Canvas()

# DEMOS

def aimGameDemo():
    if sys.stdin.fileno() is None or not sys.stdin.isatty():
        return

    with RawTerminal():
        start_time = time.perf_counter()
        
        targets = 5
        mp = 10
        sym = "x"
        score = 0
        r = 1
        xp = [random.randint(1, mp) for _ in range(targets)]
        yp = [random.randint(2, mp + 1) for _ in range(targets)]
        
        # cls + mouse tracking
        sys.stdout.write("\033[2J\033[H" + ENABLE_MOUSE)
        sys.stdout.flush()
        
        try:
            while True:
                for i in range(targets):
                    print(f"\033[{yp[i]};{xp[i]}H{sym}", end="")
                print(f"\033[{mp + 2};1HScore: {score}  ", end="")
                print(f"\033[{mp + 3};1HPress 'q' to quit: ", end="")
                sys.stdout.flush()
                
                char = get_char(1)
                
                if char == 'q':
                    break
                elif char == '\x1b':
                    seq1 = get_char(1)
                    if seq1 == '[':
                        seq2 = get_char(1)
                        if seq2 == '<':
                            mouse_data = ""
                            while True:
                                next_char = get_char(1)
                                mouse_data += next_char
                                if next_char in ('M', 'm'):
                                    break
                            
                            parts = mouse_data[:-1].split(';')
                            if len(parts) >= 3:
                                button = parts[0]
                                x = int(parts[1])
                                y = int(parts[2])
                                action = "Pressed" if mouse_data.endswith('M') else "Released"

                                if action == "Pressed" and button == '0': 
                                    for i in range(targets):
                                        if abs(xp[i] - x) <= r and abs(yp[i] - y) <= r:
                                            print(f"\033[{yp[i]};{xp[i]}H ", end="")
                                            xp[i] = random.randint(1, mp)
                                            yp[i] = random.randint(2, mp + 1)
                                            score += 1
        finally:
            # clean up stuff
            sys.stdout.write(DISABLE_MOUSE + "\033[2J\033[H")
            sys.stdout.flush()    
            
        print("Game Over!")
        print(f"Final Score: {score}")
        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"Time Taken: {duration:.2f} seconds")
        print(f"Clicks per second: {round(score / duration, 2) if duration > 0 else 0}")

def tableDemo():
    """Prints a ansi demo table."""
    print("--- text styles ---")
    styles = {
        "0": "Reset",
        "1": "Bold",
        "2": "Dim",
        "3": "Italic",
        "4": "Underline",
        "5": "Blink",
        "7": "Reverse",
        "8": "Hidden (Invisible)",
        "9": "Strikethrough"
    }

    print(f"{'Code':<6} | {'Style Name':<20} | {'Visual Output'}")
    print("-" * 50)
    for code, name in styles.items():
        formatted_text = f"\033[{code}mThis is {name}\033[0m"
        print(f"{code:<6} | {name:<20} | {formatted_text}")
    print("\n")

    print("--- 8/16 colors ---")
    colors = [
        ("Black", 30, 40),
        ("Red", 31, 41),
        ("Green", 32, 42),
        ("Yellow", 33, 43),
        ("Blue", 34, 44),
        ("Magenta", 35, 45),
        ("Cyan", 36, 46),
        ("White", 37, 47),
        ("Bright Black", 90, 100),
        ("Bright Red", 91, 101),
        ("Bright Green", 92, 102),
        ("Bright Yellow", 93, 103),
        ("Bright Blue", 94, 104),
        ("Bright Magenta", 95, 105),
        ("Bright Cyan", 96, 106),
        ("Bright White", 97, 107),
    ]

    print(f"{'Color Name':<15} | {'FG Code'} | {'Foreground Demo':<20} | {'BG Code'} | {'Background Demo'}")
    print("-" * 80)
   
    for name, fg, bg in colors:
        fg_demo = f"\033[{fg}m{name} Text\033[0m"
        bg_demo = f"\033[{bg};30m {name} Background \033[0m"
        print(f"{name:<15} | {fg:<7} | {fg_demo:<29} | {bg:<7} | {bg_demo}")
    print()

def Demo256():
    for i in range(256):
        print(f"\033[48:5:{i}m{leadZero(i,3)},\033[0m", end="")
        if (i - 15) % 36 == 0 or i == 15:
            print("\n" if i == 15 else "")
        elif i == 7:
            print(end="\t")
        print(end=" " if i < 15 else "")

def clickDemo():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()
    print("Click anywhere.")
    print("Type 'q' to exit.\n")

    with RawTerminal():
        while True:
            response = finput(prompt="> ", max_length=1, inputs=["keyboard","mouse"])

            if "mouse" in response:
                action_char, btn_name, x, y = response["mouse"]
                action = "Pressed" if action_char == 'M' else "Released"
                place(int(x),int(y), f"[{btn_name} {action} at X:{x} Y:{y}]")
                sys.stdout.flush()
            elif "keyboard" in response:
                if response["keyboard"].strip().lower() == 'q':
                    print("\nExiting click demo...")
                    break

def clockDemo():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()
    print("Click anywhere.")
    print("Type 'q' to exit.\n" + cursor().invis())
    lx, ly = False, False

    with RawTerminal():
        while True:
            response = finput(max_length=1,vis=False,tick_func=f'clock_tick({lx},{ly},"\033[33m")' if lx and ly else 'pass',inputs=["keyboard","mouse"])

            if "mouse" in response:
                _, _, x, y = response["mouse"]
                place(int(x),int(y),f"[{time.strftime('%H:%M:%S')}]",cls=True)
                lx, ly = x,y
            elif "keyboard" in response:
                if response["keyboard"].strip().lower() == 'q':
                    print("\033[28m\nExiting click demo...")
                    break

def controllerDemo():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()
    print("Controller Demo: Press A, B, X, or Y on your gamepad.")
    print("Type 'q' on your keyboard to exit.\n" + cursor().invis())

    with RawTerminal():
        while True:
            response = finput(max_length=1, vis=False, inputs=["keyboard", "controller"])

            if "keyboard" in response:
                if response["keyboard"].strip().lower() == 'q':
                    print("\033[28m\nExiting controller demo..." + cursor().vis())
                    break
            
            elif "controller" in response:
                value = response["controller"]
                sys.stdout.write(f"\r\033[KGame pad input: [")
                for i in range(len(value)):
                    sys.stdout.write(f"{value[i]}" + ("," if i < len(value) - 1 else ""))
                sys.stdout.write("]") 
                sys.stdout.flush()
    print(CLEAR_SCREEN)

def DebugDemo():
    while input("") != "q" : pass

def canvasDemo():
    C.line(1, 2, 60, 15, char="*", color=rgb(255, 0, 0)) # Red line
    C.rect(10, 5, 20, 10, char="o", color=rgb(0, 255, 0)) # Green box
    C.circle(5,6,10)
    C.render()

def platformerDemo():
    level = ["1" * 12] + ["1" + "0" * 10 + "1"] * 10 + ["1" * 12]
    level[10] = "1" + "2" + "0" * 9 + "1"

def randDemo():
    rand = []
    P = 10
    Colors = dict(zip(list(str(i) for i in (range(P + 1))),list(color256(random.randint(16,231),"b") for _ in range(P + 1))))
    for i in range(500):
        rl = []
        for j in range(50):
            rl.append(str(random.randint(1,P)))
        rand.append(rl)
    C.draw(rand, Color=Colors)
    C.render()

def arrowsDemo():
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()
    print("Arrow Key Demo: Press arrow keys on your keyboard.")
    print("Type 'esc' on your keyboard to exit.\n" + cursor().vis())

    with RawTerminal():
        while True:
            response = finput(max_length=1, vis=True, inputs=["keyboard", "arrows", "ESC", "mouse"])
            if "ESC" in response:
                break

            if "keyboard" in response:
                pass
            
            elif "arrows" in response:
                value = response["arrows"].lower()
                move_sequence = getattr(c, value)()
                sys.stdout.write(move_sequence)
                sys.stdout.flush()
            
            if "mouse" in response:
                if "mouse" in response:
                    action_char, btn_name, x, y = response["mouse"]
                    if action_char == "M":
                        if btn_name == "LC":
                            sys.stdout.write(c.setPos(x,y))
                            sys.stdout.flush()
                        elif btn_name == "MC":
                            place(x=int(x),y=int(y),msg=" ",save=True)
                
    print(CLEAR_SCREEN)

def devDashboard():
    print("type 'quit()' to quit.")
    while True:
        if exec(input(">>> ")) == "quit":
            break

def btopPy():
    #
    """A python btop4win clone
    nums: ⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹"""
    theme = ThemeEngine()
    theme.load_theme("nord")
    p = {
    "r" : theme.RESET,
    "bg" : theme.get("main_bg") if False else "",
    "t" : theme.get("main_fg"),
    "T" : theme.get("title"),
    "s" : theme.get("hi_fg"),
    "cb": theme.get("cpu_box")
    }
    def P (l):
        RR = ""
        for i in range(len(l)):
            RR += p[l[i]]
        return RR
    clear()
    def ft (t:str):
        return f'{p["s"]}{t[0]}{p["T"]}{t[1::]}{P(["r", "bg"])}'
    
    W, H = shutil.get_terminal_size()
    padding_len = max(1, W - 12)
    ms = 1000
    cpuName, GHz = get_cpu_info()
    IC = get_per_core_load()
    update_load_history(get_cpu_load())
    current_queue = pdh.get_value(r"\System\Processor Queue Length")
    load_history.append(current_queue)



    print(end=
        f'{p["bg"]}{p["t"]}' + 
        f'{bd(["TL","TR"], CC=p["cb"])}{ft("¹cpu")}{bd(["TL","TR"], 2, p["cb"])}{ft("menu")}{bd(["TL","TR"], 0, p["cb"])}{ft("preset *")}' + 
        f'{bd(["TL","TR"], int(padding_len/2) - 24, p["cb"])}{p["T"]}{time.strftime("%H:%M:%S")}{p["t"]}{bd(["TL","TR"], int((padding_len-1)/2) - len(str(ms)) - 10, p["cb"])}{p["r"]}' + 
        f'{ft("-")}{ft(f" {ms}ms ")}{ft("+")}{p["t"]} '
    )

    place(W-33, 3, f'{cpuName}{bd(["TL","TR"], 4, p["cb"])}{GHz} GHz')
    place(W-35,4,f"CPU graph {get_cpu_load()}")
    for i in range(len(IC)):
        place(W-35,5+i,f"C{i}  graph {IC[i]}")
    GLA = get_load_averages()
    place(W-35, 5+len(IC), f"Load AVG: {GLA[0]:>5.2f}  {GLA[1]:>5.2f}  {GLA[2]:>5.2f}", save=True)
    place(W-3, 3, bd(["TL","TR","BR","BL","TL","TR"], [0,6,33,6,1], p["cb"]), save=False)
    place(W-3, 1, bd(["TL","TR","BR","BL"], [1,H-3,W-2], CC=p["cb"]), save=False)
    place(1,2,bd("V",H - 3,p["cb"]),CLS=False)
    print()
    
    # shortcuts
    s = {"¹":"print(end='cpu box toggled.')","t":"pass"}
    Cs = {"NA":s["t"]}
    infilter = False
    filter = ""
    global lastUpdate
    lastUpdate = time.time()
    with RawTerminal():
        while True:
            # get inputs
            global update
            def update():
                global lastUpdate
                if time.time() - lastUpdate < (ms/1000): return None
                lastUpdate = time.time()
                cpul = get_cpu_load()
                IC = get_per_core_load()

                update_load_history(cpul)
                current_queue = pdh.get_value(r"\System\Processor Queue Length")
                load_history.append(current_queue)
                place(W-35,4,f"CPU {generate_cpu_bar(cpul,24)} {int(cpul):>3}%",save=True)
                for i in range(len(IC)):
                    place(W-35,5+i,f"C{i}  {generate_cpu_bar(IC[i],24)} {int(IC[i]):>3}%",save=True)
                GLA = get_load_averages()
                place(W-35, 5+len(IC), f"Load AVG: {GLA[0]:>5.2f}  {GLA[1]:>5.2f}  {GLA[2]:>5.2f}", save=True)
                place(W-3, 3, bd(["TL","TR","BR","BL","TL","TR"], [0,6,33,6,1], p["cb"]), save=False)
                place(W-3, 1, bd(["TL","TR","BR","BL"], [1,H-3,W-2], CC=p["cb"]), save=False)
                clock_tick(int(padding_len/2) + 4, 1, p["T"], False, False, True, False)
            
            response = finput(max_length=1, vis=False, tick_func=f'update()', inputs=["keyboard", "mouse", "ESC", "arrows", "controller"])
            if "ESC" in response:
                break
            elif "controller" in response:
                response = response["controller"]
                sys.stdout.write("\x1b[1K\x1b[1G")
                for i in range(len(response)):
                    sys.stdout.write(f"{response[i]}" + ("," if i < len(response) - 1 else "")) 
                sys.stdout.flush()
                for r in response:
                    if r in Cs.keys():
                        exec(s[r])
            elif "keyboard" in response:
                response = response["keyboard"]
                if infilter:
                    filter += response
                elif response in s.keys():
                    exec(s[response])
            elif "arrows" in response:
                response = response["arrows"]
                print(end=f'\x1b[1K\x1b[1G{response}')
            elif "mouse" in response:
                action_char, btn_name, x, y = response["mouse"]
                action = "Pressed" if action_char == 'M' else "Released"
                print(end=f'\x1b[1K\x1b[1G{action=},{btn_name=},{x=},{y=}')

                



import flipper
def main():
    flipper.start()
    if flipper.port:
        flipper.cli(flipper.port)


if __name__ == "__main__":
    btopPy()
