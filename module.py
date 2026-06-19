import sys
import os
import random
import time
import re
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
CLEAR_SCREEN = "\033[H\033[J"

bg_color = ""


def clear(n=""):
    print(end=bg_color)
    os.system("cls" if os.name == "nt" else "clear")
    return n

def leadZero (i, d):
    """number, digits. (1,3) -> '001'"""
    i = str(i)
    i = "0" * (d - len(i)) + i
    return i

def rgb(r,g,b,m="f"):
    """0 to 255 for each color, foreground/background"""
    return f"\033[38;2;{r};{g};{b}m" if m.lower()[0] == "f" else "\033[48;2;{r};{g};{b}m" if m.lower() == "b" else ""

class cursor:
    """invis() and vis() may not cetain terminals."""
    def invis():
        return ("\033[?25l")
    def vis():
        return ("\033[?25h")
    def up(n=1):
        return (f"\033[{n}A")
    def down(n=1):
        return (f"\033[{n}B")
    def left(n=1):
        return (f"\033[{n}D")
    def right(n=1):
        return (f"\033[{n}C")
    def nextLine(n=1):
        return (f"\033[{n}E")
    def prevLine(n=1):
        return (f"\033[{n}F")
    def collum(n):
        return (f"\033[{n}G")
    def getPos():
        return ("\033[6n")
    def up1():
        return ("\033 M")
    def setPos(x="",y=""):
        return (f"\033[{y};{x}H")
    def savePos():
        return ("\033[s")
    def loadPos():
        return ("\033[u")
    def saveAll():
        return ("\0337")
    def loadAll():
        return ("\0338")

chars = {
    """custom chars"""
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
        def CtoEnd():
            return "\033[0J"
        def CtoStart():
            return "\033[1J"
        def all():
            return "\033[2J"
        def saved():
            return "\033[3J"
    def save():
        return "\033[?47h"
    def load():
        return "\033[?47l"

class line:
    class erase:
        def CtoEnd():
            return "\033[0K"
        def CtoStart():
            return "\033[1K"
        def all():
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


#useful fancy stuff

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

def finput(prompt="", max_length=-1, tick_func=lambda: 0, long=False):
    """Fancy input, input that allows mouse inputs."""
    sys.stdout.write(prompt)
    sys.stdout.write(ENABLE_MOUSE)
    sys.stdout.flush()

    user_input = ""
    buffer = ""
    mouse_regex = re.compile(r'\x1b\[<(\d+);(\d+);(\d+)([mM])')

    try:
        while True:
            # a tick so you don't need to use threading
            tick_func()
            time.sleep(0.01)
            # check if theirs an input, if so read it.
            if not char_available():
                continue
            char = get_char(1)
            if not char:
                continue

            if buffer or char == '\x1b':
                buffer += char    
                # stuff for mouse
                if buffer.startswith('\x1b[<'):
                    match = mouse_regex.search(buffer)
                    if match:
                        button, t_col, t_row, action = match.groups()
                        buffer = ""
                        
                        # Determine which button was clicked
                        if   button == '0' : btn_name = "Left Click"   if long else "LC"
                        elif button == '1' : btn_name = "Middle Click" if long else "MC"
                        elif button == '2' : btn_name = "Right Click"  if long else "RC"
                        elif button == '64': btn_name = "Scroll Up"    if long else "SU"
                        elif button == '65': btn_name = "Scroll Down"  if long else "SD"
                        else: btn_name = "Unknown"

                        return (action, btn_name,t_col,t_row) # (m/M) (name) (y) (x)
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
            if char in ('\n', '\r'):
                sys.stdout.write('\n')
                sys.stdout.flush()
                return user_input
                
            elif char in ('\x08', '\x7f'): # backspace
                if len(user_input) > 0:
                    user_input = user_input[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                    
            elif char.isprintable():
                user_input += char
                sys.stdout.write(char)
                sys.stdout.flush()
                
                # auto submit feuture
                if max_length != -1 and len(user_input) >= max_length:
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    time.sleep(0.5)
                    return user_input
    finally:
        sys.stdout.write(DISABLE_MOUSE)
        sys.stdout.flush()



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


def main():
    pass    

if __name__ == "__main__":
    aimGameDemo()