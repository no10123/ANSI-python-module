import sys
import os

bg_color = "\033[49m"

def clear(n=""):
    print(end=bg_color)
    os.system("cls")
    return n    

def leadZero (i, d):
    """number, digits. (1,3) -> '001'"""
    i = str(i)
    i = "0" * (d - len(i)) + i
    return i

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


    # dosent move cursor

class screen:
    class erase:
        def CtoEnd():
            return "\0330J"
        def CtoStart():
            return "\0331J"
        def all():
            return "\0332J"
        def saved():
            return "\0333J"
    def save():
        return "\033[?47h"
    def load():
        return "\033[?47l"

class line:
    class erase:
        def CtoEnd():
            return "\0330K"
        def CtoStart():
            return "\0331K"
        def all():
            return "\0332K"

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

def main():
    global bg_color
    bg_color = "\033[42m"
    clear()
    print("i like green")

if __name__ == "__main__":
    tableDemo()
    clear(input("clear: "))