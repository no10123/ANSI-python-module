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
import collections
import math
import pygame
import yt_dlp
import soundcard as sc
import numpy as np
import warnings
from PIL import Image, ImageSequence
import cv2
from functools import wraps
import base64
from io import BytesIO
import mss
import pygetwindow as gw
import win32gui
import win32ui
import win32api
import win32con
from spotlight import *
import ctypes
from ctypes import wintypes, windll
from displays import *
import colorsys

class RawTerminal():
    """
    a class that sets the state of the terminal to allow for cursor inputs.

    you must call it before all cursor inputs, 
    and is recommended for most input loops.

    Args:
        None

    Returns:
        a set of functions that are used by the with statement.

    Example:
        >>> with RawTerminal():
        >>>     i = finput(max_length=1, inputs=["mouse"])

        to get a mouse input of i. (read finput for details)

    Notes:
        __init__  is when called
        __enter__ is when the while happens  (sets terminal to raw mode)
        __exit__  is when the while finishes (resets terminal to normal mode)
    """
    def __init__(self) -> None:
        self.original_stdin_state = None
        self.original_stdout_state = None
        self.fd_in = sys.stdin.fileno() if sys.stdin.isatty() else None

    def __enter__(self) -> self:
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

    def __exit__(self, type, value, traceback)  -> None:
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

# basic commands
ENABLE_MOUSE = "\x1b[?1000h\x1b[?1006h"
DISABLE_MOUSE = "\x1b[?1000l\x1b[?1006l"

ENABLE_MOUSE_D = "\x1b[?1002h\x1b[?1006h"
DISABLE_MOUSE_D = "\x1b[?1002l\x1b[?1006l"
CLEAR_SCREEN = "\033[H\033[J"
DoubleX = True

Debug = False

BLOCKS = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
I_BLOCKS = [" ", "▔", "🮂", "🮃", "▀", "🮄", "🮅", "🮆", "█"]
W, H = shutil.get_terminal_size()

theme = ThemeEngine()

bg_color = ""

def ansi_doc_string():
    """\033[44mhello\033[0m world"""



def exampleDoc() -> None:
    """
    prints an example docstring template.
    
    Args:
        None
    
    Returns:
        None
    
    Example:
        >>> exampleDoc()
    
    Notes:
        it's just in here so i can easily copy paste it, not really intended for actual use.
    """
    print(
        """
small description

optional larger description

Args:
    parameter:
        Description.

    parameter:
        Description.

Returns:
    Description of the return value.

Example:
    >>> example()

Notes:
    Extra information
"""
    )

def clear(n:str="", bg_c:str=bg_color) -> str:
    """
    applies bg color and clears screen.
    This sets the main bg to that color.

    Args:
        n:
            value after clearing screen, 
            good for inline expressions.
        bg_c: 
            ANSI color for the terminal background color

    Returns: 
        the value of `n`

    Example:
        >>> clear(input(), color("green"))
        >>> # sets bg to green after input and returns input

    Notes:
        `bg_c` must be an ANSI background escape sequence. Use
        `color()` or another formatting helper to generate one.
    """
    print(end=bg_c)
    os.system("cls" if os.name == "nt" else "clear")
    return n

def leadZero (i:int, d:int) -> str:
    """
    takes a num (i) and pads it to a length (d)
    with 0's

    Args:
        i:
            the number you want to pad.

        d:
            the length you want str(i) to be

    Returns:
        a str of i with the length of d.

    Example:
        >>> print(leadZero(65, 6))
        >>> # output: 000065

    Notes:
        if d is <= len(str(i)) then it will just return str(i)
    """
    return "0" * (d - len(str(i))) + str(i)

def rgb(r:int|float, g:int|float, b:int|float, m:str="f", Max:int|float=255):
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
        doesn't support floats.
    """
    r_calc = int(round(255 * r / Max))
    g_calc = int(round(255 * g / Max))
    b_calc = int(round(255 * b / Max))
    
    # 2. Clamp them between 0 and 255 so the terminal never breaks
    r = max(0, min(255, r_calc))
    g = max(0, min(255, g_calc))
    b = max(0, min(255, b_calc))
    return f"\033[38;2;{r};{g};{b}m" if m.lower()[0] == "f" else f"\033[48;2;{r};{g};{b}m" if m.lower()[0] == "b" else ""

class cursor:
    """
    applies affects to the terminal cursor.

    Returns:
        A printable escape code (for all functions)

    Example:
        >>> print(cursor().left(1))
        >>> #moves the cursor to the left

    Notes:
        vis and invis may not be supported on some terminals
    """
    def invis(self) -> str:
        """
        makes the cursor invisible
        Example: 
            >>> cursor().invis()
        """
        return ("\033[?25l")
    def vis(self) -> str:
        """
        makes the cursor visible
        Example: 
        >>> cursor().vis()
        """
        return ("\033[?25h")
    def up(self, n:int=1) -> str:
        """
        moves the cursor up `n` characters
        Example: 
        >>> cursor().up()
        """
        return (f"\033[{n}A")
    def down(self, n:int=1) -> str:
        """
        moves the cursor down `n` characters
        Example: 
        >>> cursor().down()
        """
        return (f"\033[{n}B")
    def left(self, n:int=1) -> str:
        """
        moves the cursor left `n` characters
        Example: 
        >>> cursor().left()
        """
        return (f"\033[{n}D")
    def right(self, n:int=1) -> str:
        """
        moves the cursor right `n` characters
        Example: 
        >>> cursor().right()
        """
        return (f"\033[{n}C")
    def nextLine(self, n:int=1) -> str:
        """
        moves the cursor down `n` characters and to start of Column
        Example: 
        >>> cursor().nextLine()
        """
        return (f"\033[{n}E")
    def prevLine(self, n:int=1) -> str:
        """
        moves the cursor up `n` characters and to start of Column
        Example: 
        >>> cursor().prevLine()
        """
        return (f"\033[{n}F")
    def column(self, n:int) -> str:
        """
        moves the cursor to the `n`th column
        Example: 
        >>> cursor().column()
        """
        return (f"\033[{n}G")
    def getPos(self) -> str:
        """
        gets the cursor pos in the form of \033[r;cR where r is row and c is column
        Example: 
        >>> cursor().getPos()
        """
        return ("\033[6n")
    def up1(self) -> str:
        """
        moves cursor up 1, just use up()
        Example: 
        >>> cursor().up1()
        """
        return ("\033 M")
    def setPos(self, x:int|str=0,y:int|str=0) -> str:
        """
        sets the cursor pos to (x,y)
        Example: 
        >>> cursor().setPos(3,7)
        """
        return (f"\033[{y};{x}H")
    def savePos(self) -> str:
        """
        saves the cursor pos
        Example: 
        >>> cursor().savePos()
        """
        return ("\033[s")
    def loadPos(self) -> str:
        """
        sets the cursor pos to the last saved cursor pos
        Example:
        >>> cursor().loadPos()
        """
        return ("\033[u")
    def saveAll(self) -> str:
        """
        saves all cursor attributes
        Example: 
        >>> cursor().saveAll()
        """
        return ("\0337")
    def loadAll(self) -> str:
        """
        sets all cursor attributes to the saved attributes
        Example: 
        >>> cursor().loadAll()
        """
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
    """
    funcs to manipulate lines
    Example:
        >>> screen().save
    Notes:
        it's not that useful, but it exists.
    """
    class erase:
        """
        C is cursor
        """
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

def color(name:str="default", m:str="f", bright:bool=False):
    """
    give the name of one of the 9 base colors, and get the ANSI escape code for it.
    
    Args:
        name:
            the name of the color (must be in list)
            ["black","red","green","yellow","blue","magenta","cyan","white",None,"default"]
        m:
            determines weather the color will be applied to the text or bg. 
            ("f" for text/"b" for back ground)
        bright:
            makes the color brighter if True, is not same as bold.
    
    Returns:
        The ANSI escape code for your color.
    Example:
        >>> print(color("red")+"hello"+color())
        >>> prints a red hello
    Notes:
        default is same as reset for `m` (so will reset foreground color if m == "f" else reset bg color)
    """
    names = ["black","red","green","yellow","blue","magenta","cyan","white",None,"default"]
    return f"\033[{names.index(name.lower()) + 30 + (10 if m.lower()[0] == 'b' else 0) + (60 if bright else 0)}m" if name else ""


# >>><<<
def color256(id:int, m:str="f"):
    """
    0-7: standard colors (as in ESC [ 30-37 m)
    8-15: high intensity colors (as in ESC [ 90-97 m)
    16-231: 6 * 6 * 6 cube (216 colors): 16 + 36 * r + 6 * g + b (0 ≤ r, g, b ≤ 5)
    232-255: grayscale from dark to light in 24 steps.
    """
    return f"\033[{38 if m.lower()[0] == 'f' else 48};5;{id}m"

def setMode(id:int, m:str="add"):
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

def divider(char:str="-"):
    terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
    print(char * terminal_width)

def log(msg:str):
    with open("debug.log", "a") as f:
        f.write(f"{msg}\n")
        f.flush()

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

shaded = {"none":" ","light":"\u2591","medium":"\u2592","dark":"\u2593"}
def ps(p:int=0,c:str=""):
    """0 <= p <= 3"""
    return c + list(shaded.values())[p] + "\033[0m"

def HSVtoRGB(H:int,S:int,V:int):
    r, g, b = colorsys.hsv_to_rgb(H / 360, S / 100, V / 100)
    return (255 * r, 255 * g, 255 * b)

def HEXtoRGB(hex:str):
    return tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def toggle_item(L:list, item):
    if item in L:
        L.remove(item)
    else:
        L.append(item)

#useful fancy stuff

def clear_graph_area(x:int, y:int, width:int, height:int):
    out = []
    for row in range(height):
        out.append(f"\x1b[{y + row};{x}H" + (" " * width))
    return "".join(out)

def cpu_graph(x:int, y:int, width:int, height:int, history:list, color, char:str="█", smooth:bool=True, max:float=100.0):
    if len(color[0]) == 1:
        color = [color] * (height)
    elif len(color) < height:
        c = color
        color = []
        for i in range(height):
            i = int(i // (height / len(c)))
            color.append(c[i])
    if width <= 0 or height <= 0: return ""
    samples = list(history)[-width:]
    out = []
    for col, value in enumerate(samples):
        bar_height = int((value / max) * height)
        extra = (value / max) * height - bar_height
        for row in range(bar_height + 1):
            current_row = (y + height - 1) - row
            if row < bar_height:
                out.append(f"\x1b[{current_row};{x + col}H{color[min(row, len(color) - 1)]}{char}\033[0m")
            elif int(7 * extra) != 0:
                out.append(f"\x1b[{current_row};{x + col}H{color[min(row, len(color) - 1)]}{BLOCKS[int(7 * extra)]}\033[0m")
    return "".join(out)

def dual_graph(x, y, width, height, c_up, c_down, color, char:str="█"):
    if len(color[0]) == 1:
        color = [color] * (height)
    elif len(color) < height:
        c = color
        color = []
        for i in range(height):
            i = int(i // (height / len(c)))
            color.append(c[i])
    if width <= 0 or height <= 0: return ""
    out = "color[min(row, len(color) - 1)]"
    mid_y = (y + height) / 2
    for i in range(max(len(c_up),len(c_down))):
        if (y % 2) == 1:
            out += f"\x1b[{math.ceil(mid_y)};{x + i}H{char}"
        py, my, pe, me = 0, 0, 0, 0
        if i < len(c_up) - 1:
            py = int(c_up[i])
            pe = c_up[i] - py
        if i < len(c_down):
            my = int(c_down[i])
            me = c_down[i] - my
        if int(7 * me) != 0:
            out += f"\x1b[{math.ceil(mid_y) - j};{x + i}H{I_BLOCKS[int(me * 7)]}"
        if my > 0: 
            for j in range(my):
                j += 1
                out += f"\x1b[{math.ceil(mid_y) - j};{x + i}H{char}"
        if py > 0:
            for j in range(py):
                j += 1
                out += f"\x1b[{math.floor(mid_y) + j};{x + i}H{char}"
        if int(7 * pe) != 0:
            out += f"\x1b[{math.ceil(mid_y) - j};{x + i}H{BLOCKS[int(pe * 7)]}"
        
        out += "\033[0m"
    return out
        
def iprint(msgs:list, end:str="\n", lend:str=""):
    for i in msgs:
        print(i,end=(end if i == msgs[-1] else lend))

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

#non standard inputs
# fancy stuff
def get_cursor_position(axsis:str="xy"):
    STD_OUTPUT_HANDLE = -11
    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    
    class COORD(ctypes.Structure):
        _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]
        
    class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
        _fields_ = [("dwSize", COORD),
                    ("dwCursorPosition", COORD),
                    ("wAttributes", wintypes.WORD),
                    ("srWindow", wintypes.SMALL_RECT),
                    ("dwMaximumWindowSize", COORD)]
                    
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, ctypes.byref(csbi))
    if axsis == "xy":
        return csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y
    elif axsis == "x":
        return csbi.dwCursorPosition.X
    elif axsis == "y":
        return csbi.dwCursorPosition.Y
    return (0,0)

def get_char_at_cursor():
    STD_OUTPUT_HANDLE = -11
    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    class COORD(ctypes.Structure):
        _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]
        
    class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
        _fields_ = [("dwSize", COORD),
                    ("dwCursorPosition", COORD),
                    ("wAttributes", wintypes.WORD),
                    ("srWindow", wintypes.SMALL_RECT),
                    ("dwMaximumWindowSize", COORD)]
                    
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, ctypes.byref(csbi))
    cursor_pos = csbi.dwCursorPosition
    char_buffer = ctypes.create_unicode_buffer(1)
    chars_read = wintypes.DWORD()
    
    ctypes.windll.kernel32.ReadConsoleOutputCharacterW(
        handle, 
        char_buffer, 
        1, 
        cursor_pos, 
        ctypes.byref(chars_read)
    )
    
    return char_buffer.value

def get_char_at(x:int, y:int):
    STD_OUTPUT_HANDLE = -11
    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    class COORD(ctypes.Structure):
        _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]        
    coord = COORD(x, y)
    char_buffer = ctypes.create_unicode_buffer(1)
    chars_read = wintypes.DWORD()
    ctypes.windll.kernel32.ReadConsoleOutputCharacterW(
        handle, 
        char_buffer, 
        1, 
        coord, 
        ctypes.byref(chars_read)
    )
    return char_buffer.value

def get_word(x:int=get_cursor_position()[0],y:int=get_cursor_position()[1],words:int=1):
    if get_char_at(x,y) == " ":
        x += 1
    word = ""
    while True:
        char = get_char_at(x,y)
        if (char == " " or not char):
            if words == 1:
                break
            else:
                words -= 1
        word += char
        x += 1
    return word

def attr_to_ansi(attr: int, out:str="ansi") -> str|tuple[tuple[int,int,int],tuple[int,int,int]]:
    def get_rgb(bits: int) -> tuple[int, int, int]:
        if bits == 7: return (192, 192, 192)
        if bits == 8: return (128, 128, 128)        
        intensity = 255 if (bits & 0x08) else 128
        r = intensity if (bits & 0x04) else 0
        g = intensity if (bits & 0x02) else 0
        b = intensity if (bits & 0x01) else 0        
        return r, g, b
    fg_bits = attr & 0x0F
    bg_bits = (attr >> 4) & 0x0F
    fr, fg, fb = get_rgb(fg_bits)
    br, bg, bb = get_rgb(bg_bits)
    if out == "ansi":
        return f"\033[38;2;{fr};{fg};{fb};48;2;{br};{bg};{bb}m"
    elif out == "rgb":
        return ((fr,fg,fb),(br,bg,bb)) 
    else:
        return ""

def get_cell_color_at(x: int, y: int, out:str="ansi") -> str|tuple[tuple[int,int,int],tuple[int,int,int]]:
    "out = [ansi, rgb]"
    STD_OUTPUT_HANDLE = -11
    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    class COORD(ctypes.Structure):
        _fields_ = [("X", wintypes.SHORT), ("Y", wintypes.SHORT)]

    attr_buffer = wintypes.WORD()
    read_count = wintypes.DWORD()

    ctypes.windll.kernel32.ReadConsoleOutputAttribute(
        handle,
        ctypes.byref(attr_buffer),
        1,
        COORD(x, y),
        ctypes.byref(read_count),
    )
    return attr_to_ansi(attr_buffer.value, out=out)

def fetch_yt_audio(url:str, name:str="music"):
    """converts YT link to .mp3 audio"""
    #yt-dlp config
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'downloads/{name}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    print(f"Fetching audio from {url}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    print("Download complete.")
    return f"downloads/{name}.mp3"

def fetch_yt_video(url: str, name: str = "video", audio:bool=True):
    """YT url -> .mp4"""
    
    # yt-dlp config for MP4 video
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'downloads/{name}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    print(f"Fetching video from {url}...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download complete.")
        return f"videos/{name}.mp4"
    except Exception as e:
        print(f"error: {e}")
        return None

def loop_(l:list, length:int, I:int=0):
    S = ""
    for i in range(length):
        i += I
        S += l[i % len(l)]
    return S

def rainbowify(s:str, i:int=1, m:str="f", h:int|float=0):
    S = ""
    l = len(s)
    for char in s:
        r,g,b = colorsys.hsv_to_rgb(h/360, 1, 1)
        if m == "fb":
            S += rgb(r,g,b,"f",1) + rgb(r,g,b,"b",1) + char 
        else:   
            S += rgb(r,g,b,m,1) + char
        h += (i * (360/len(s))) % 360
    return S + "\033[0m"

def load_bar(duration=10, length=100, bg:str|tuple[int,int,int]=(0,0,0), color="rainbow"):
    I = duration/length
    chars = BLOCKS[1:] + BLOCKS[::-1][1:-2]
    for i in range(length):
        i += 1
        time.sleep(I)
        r,g,b = colorsys.hsv_to_rgb(i/length, 1, 1)
        Color = rgb(r,g,b,"b",1)
        print(f" [ " + rainbowify(loop_(chars, i, i), 1, "f", 360 * i/length) + "\033[0m" + " " * (length - i) + " ] \n [ \033[8m" + rainbowify(loop_(chars, i, i), 1, "b", 360 * i/length) + "\033[0m\033[28m" + " " * (length - i) + " ] ", end="\r" + c.up())
    print("\n")

clear()
print("#", end="\r")
d = get_cell_color_at(0,0,"rgb")
print(rgb(int(d[0][0]),int(d[0][1]),int(d[0][2]), "f") + rgb(int(d[1][0]),int(d[1][1]),int(d[1][2]), "b") + "your terminal is lying to you\033[0m. Why?")
print(d)
input()
while True:
    clear()
    load_bar(duration=10, bg=get_cell_color_at(0,0,"rgb")[1])
    input("DONE.")
# more fancy stuff

"""

"""
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
        import msvcrt
        return msvcrt.getwch()
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

def f_out(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = kwargs.get("custom_out", {})
        result = func(*args, **kwargs)
        if data:
            for key, value in result.items():
                values = value if isinstance(value, list) else [value]
                for item in values:
                    if item in data:
                        exec(data[item], {"key": key, "value": item, "result": result}, globals())
                if key in data:
                    try:
                        exec(data[key], {"key": key, "value": item, "result": result}, globals())
                    except Exception as e:
                            print(f"\n[!] error: {key}: {e}")
        return result
    return wrapper

@f_out
def finput(prompt:str="", max_length:int=-1, tick_exec:str='pass', tick_func:callable=lambda: None, long:bool=False, vis:bool=True, 
           inputs:list=["keyboard","mouse","arrows","ESC","controller"],drag:bool=False, 
           custom_out:dict={}, custom_enter="\n"):
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
            exec(tick_exec)
            tick_func()
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

            if buffer or char in ('\x1b', '\xe0', '\x00'):
                
                if not buffer and char == '\x1b' and "ESC" in inputs:
                    time.sleep(0.01)
                    if not char_available():
                        return {"ESC":"ESC"}
                buffer += char    
                if buffer.startswith(('\xe0', '\x00')):
                    if len(buffer) == 2:
                        direction = {'H': 'UP', 'P': 'DOWN', 'M': 'RIGHT', 'K': 'LEFT'}.get(buffer[1])
                        buffer = ""
                        if direction and "arrows" in inputs:
                            result["arrows"] = direction
                            return result
                    elif len(buffer) > 2:
                        buffer = ""
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
                sys.stdout.write(hide + custom_enter + reset)
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
                    sys.stdout.write(hide + custom_enter + reset)
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
    def __init__(self, D=False):
        self.width, self.height = shutil.get_terminal_size()
        if D:
            if input(f"Canvas size initialized: {self.width}x{self.height}\nok: ") in ["overide", "o"]:
                self.width, self.height = int(input("width: ")), int(input("height: "))
        self.clear()

    def clear(self):
        """Re-blanking the arrays is much faster than creating a new Canvas every frame."""
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
        for i in range(2 * R + 1):
            curr_x = i + x - R
            for j in range(2 * R + 1):
                curr_y = j + y - R
                if (curr_x - x)**2 + (curr_y - y)**2 <= R**2: 
                    self.set_pixel(curr_x, curr_y, char, color)

    def draw(self, L, char=" ", Color={"any": "\033[0m"}):
        for y, row in enumerate(L):
            for x, Char in enumerate(row):
                color_code = Color.get(Char, Color.get("any", "\033[0m"))
                self.set_pixel(x, y, char, color_code)
                
    def render(self):
        output = ["\033[H"] 
        current_color = None
        for y in range(self.height - 1):
            for x in range(self.width):
                color = self.colors[y][x]                
                if color != current_color:
                    output.append(color)
                    current_color = color
                output.append(self.buffer[y][x])            
            if y < self.height - 2:
                output.append("\n")
        output.append("\033[0m")
        
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

def floop(func, args = (), kwargs = None, raw=True):
    if kwargs is None:
        kwargs = {}
    if raw:
        with RawTerminal():
            while True:
                func(*args, **kwargs)
    else:
        while True:
            func(*args, **kwargs)

class createQuiz():
    def __init__(self, c=[]):
        self.length = 0
        self.score = 0
        self.questions = []
        self.colors = c
        self.choices = []
        self.vote = []
    def colorPalate(self, c):
        self.colors = c
    def add(self, type, prompt, answer, settings):
        self.questions.append([type, prompt, answer, settings])
    def start(self):
        for i in self.questions:
            t, p, a, s = i
            if t.lower() in ["mc","multiple choice"]:
                correct = ""
                print(p)
                k, v, m, ex = [a.get(key,d) for key, d in [("k","error"), ("v","error"), ("m",100/len(self.questions)), ("ex",None)]]
                if k == "error" or v == "error":
                    input("[!] Error.\n> ")
                    continue
                
                if isinstance(v,int):
                    v = [v]
                if isinstance(v,list) and v and isinstance(v[0],int):
                    v = [k[i] for i in v]
                if isinstance(v,str):
                    v = [v]
                if isinstance(v,list) and v and isinstance(v[0],str):
                    v = [i in v for i in k]
                
                if isinstance(m,int) or isinstance(m,float):
                    m = [0,m]
                if isinstance(m,dict):
                    m = [m.get(v[i]) for i in range(len(v))]
                elif isinstance(m,list) and len(m) != len(v):
                    m = [max(m) if v[i] else min(m) for i in range(len(v))]
                
                if isinstance(ex,str) or ex in [None, False]:
                    ex = [ex] * len(v)
                elif isinstance(ex,dict):
                    ex = [ex.get(k[i]) for i in range(len(k))]
                elif isinstance(ex,tuple):
                    match len(ex):
                        case 1:
                            ex = [ex[0]] * len(v)
                        case 2:
                            if isinstance(ex[0],list):
                                ex = [ex[1] if i in ex[0] else None for i in (p if isinstance(ex[0][p],int) else k[p] for p in range(len(ex[0])))] + [None] * (len(v) - len(ex[0]))
                            if isinstance(ex[0],int):
                                ex = [ex[1] if i == ex[0] else None for i in range(len(v))]
                            elif isinstance(ex[0],str):
                                ex = [ex[1] if i == ex[0] else None for i in k]

                
                for i in range(len(k)):
                    print(k[i])
                    if v[i]: correct = k[i]
                while True:
                    i = input("")
                    if i in k:
                        break
                    else:
                        print(end=f"\033[1A\033[K")
                if i  == correct:
                    print("correct. :)")
                    if ex[k.index(i)]: print(ex[k.index(i)])
                else:
                    print("incorrect.")
                    if ex[k.index(i)]: print(ex[k.index(i)])
                self.score += m[k.index(i)]
                self.choices.append(i)
                self.vote.append(i == correct)
    def result(self,total=100,p=70,quiet=False):
        if not quiet:
            s = 100 * (self.score / total)
            print(f"score: {s}%")
            if s > p:
                print("you passed.")
            else:
                print("you no pass.")
        else:
            return self.score
    def tf_gen(self, p, a, loop=False, req=True, options:list=["T","F"]):
        S = len(max(p,key=len)) + 1
        for i in p:
            print(f"{i}{' ' * (S - len(i))} [{options[0]}/{options[1]}]: ")
        print(end=f"submit: {' ' * (S + len(options[0]) + len(options[1]) - 2)}")
        print(end=c.up(len(p) + 1))
        r = [""] * (len(p) + 1)
        y = 0
        while True:
            result = finput("",1,'pass',False,False,["keyboard","arrows"],False,{},c.left())
            if "keyboard" in result and result["keyboard"] in options:
                print(end=result["keyboard"]+c.down()+c.left())
                r[y] = result["keyboard"]
                y += 1
                c.down()
            elif "arrows" in result:
                if result["arrows"] == "UP" and (y > 0 or loop):
                    y = (y - 1) % len(r)
                    c.up()
                elif result["arrows"] == "DOWN"  and (y < len(r) or loop):
                    y = (y + 1) % len(r)
                    c.down()
                else:
                    a = {"LEFT":options[0],"RIGHT":options[1],"":""}.get(result["arrows"],"")
                    print(end=a)
                    r[y] = a
                    y += 1
            if y == len(r) and ("" not in r[:-2] or not req):
                return r[:-1]
            else:
                c.left()
                

                

#clear()
#quiz = createQuiz()
#quiz.add("tf","1 + 1 = ",{"k":["1","2","3","4"],"v":"2"},[])
#r = quiz.tf_gen(["1 == 1","2 == 1 + 2","3+4=6"],[True,False,False])
#print(r)
#quiz.start()
#quiz.result()
#input("quit")
#quit()

def reset_audio():
    pygame.mixer.quit()
    pygame.mixer.init()
C = Canvas()

#widgets (basically demos)

clear()

def clock(x: int, y: int, r: int):
    PI = math.pi
    RPI = math.pi/30
    S = None
    while True:
        if S != list(int(i) for i in time.strftime('%H:%M:%S').split(":"))[-1]:
            H, M, S = (int(i) for i in time.strftime('%H:%M:%S').split(":"))
            ir = r-2
            clear()
            C.circle(x,y,r)
            C.circle(x,y,ir,char=" ")
            C.line(x,y,int(ir*math.cos(S*RPI - PI/2)+x),int(ir*math.sin(S*RPI - PI/2)+y),"+",color("red"))
            C.line(x,y,int(ir*math.cos(M*RPI - PI/2)+x),int(ir*math.sin(M*RPI - PI/2)+y),"+",color("yellow"))
            C.line(x,y,int((ir/2)*math.cos(H*PI/6 + (M * math.pi / 360) - PI/2)+20),int((ir/2)*math.sin(H*PI/6 + (M * math.pi / 360) - PI/2)+20),"+",color("green"))
            C.set_pixel(x,y,"#",color("black"))
            C.render()
            print(f"{int(H)+1:>2}:{int(M):>2}:{int(S):>2}")


# DEMOS

class GameOver(Exception): pass
track, height, delay, Color = None, None, None, None
def rhythmGame(track:list=["d", "f", "j", "k", " ", "k", "df", " "],height:int=10,delay:float = 0.5, Color:str='\033[44m  \033[0m'):
    g = globals()
    for name, val in zip(["track", "height", "delay", "Color"], [track, height, delay, Color]):
        g[name] = val

    score = 0 
    first_frame = True 

    with RawTerminal():
        def play_game():
            global delay, Color, track, height, ltime
            nonlocal first_frame
            
            if len(track) == 0:
                raise GameOver()
            
            if not first_frame and (time.perf_counter() - ltime < delay): 
                return None
                        
            if not first_frame:
                track.pop(0)
                if len(track) == 0:
                    raise GameOver()
            
            first_frame = False
            ltime = time.perf_counter()            
            print(end="\033[H\033[J") 
            filler = height - len(track)

            for i in range(height):
                extra = [f'  score: {score}', f'  notes: {track[0] if track else ""}', '  '][min(i,2)]
                if i < filler:
                    print(f">>>  |             |  <<< {extra}")
                else:
                    notes = track[-(i - max(0, filler) + 1 + max(0, len(track) - height))]
                    d,f,j,k = [(Color if n in notes else '  ') for n in ['d','f','j','k']]
                    print(f">>>  | {d} {f} {j} {k} |  <<< {extra}")
                    
            return True 

        try:
            while True:
                result = finput("", 1, tick_func=play_game, long=False, vis=False, inputs=["keyboard","ESC"], drag=False)
                
                if "ESC" in result:
                    break
                elif "keyboard" in result:
                    k = result["keyboard"]
                    if len(track) > 0:
                        if k in track[0] and k != " ":
                            score += 20
                            track[0] = track[0].replace(k, "", 1)
                        else:
                            score -= 1
        except GameOver:
            print(f"\nGame Over! Final Score: {score}")

def rinpDemo():
    os.system("cls")
    print(" hello world ")
    print(" how are you")
    print("results: ")
    print(get_word(1,0,2))
    print(get_word(1,1,3))
    input()

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
            response = finput(max_length=1,vis=False,tick_exec=f'clock_tick({lx},{ly},"\033[33m")' if lx and ly else 'pass',inputs=["keyboard","mouse"])

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

def musicDemo():
    url = input("url: ")
    name = input("name: ")
    fetch_yt_audio(url, name)
    playFile(name)

def ytDemo():
    url = input("url: ")
    ap = fetch_yt_audio(url, "0")
    vp = fetch_yt_video(url, "0")
    t1 = threading.Thread(target=video, kwargs={"mw": 300, "path": vp},daemon=True)
    t2 = threading.Thread(target=playFile, kwargs={"path": ap},daemon=True)
    t1.start()
    t2.start()
    try:
        while t1.is_alive():
            t1.join(timeout=1.0)
    except KeyboardInterrupt:
        print("\nStopping...")

def videoDemo():
    global skip
    skip = 15
    name = "ex"
    ap = f"downloads/{name}.mp3"
    vp = f"downloads/{name}.mp4"
    t1 = threading.Thread(target=video, kwargs={"mw": 500, "path": vp},daemon=True)
    t2 = threading.Thread(target=playFile, kwargs={"path": ap},daemon=True)
    t3 = threading.Thread(
    target=floop,
    kwargs={
        "func": finput,
        "kwargs": {"max_length": 1,"inputs": ["keyboard", "arrows"],
            "custom_out": {
                " ": "control.pause()",
                "LEFT": f"control.seek({-skip})",
                "RIGHT": f"control.seek({skip})",},},},daemon=True,)
    t1.start()
    t2.start()
    t3.start()
    try:
        while t1.is_alive():
            t1.join(timeout=1.0)
    except KeyboardInterrupt:
        print("\nStopping...")

def slideshowDemo(folder="./wallpapers",t=3):
    i = 1
    while True:
        img = os.path.join(folder, f"{i}.jpg")
        if os.path.exists(img):
            sys.stdout.write(f"\033[1;1H\033[KWallpaper: {i}.jpg\n\n")
            img = Image.open(f"wallpapers/{i}.jpg")
            aspect = img.height / img.width
            img = img.resize((700, int(700 * aspect * 0.5)), Image.Resampling.LANCZOS)

            sys.stdout.write(k_img(img,sy=3+int(700 * aspect * 0.5) * i))
            sys.stdout.flush()
            time.sleep(t) 
            i += 1
        else:
            # loop
            i = 1

def btopPy():
    """A python btop4win clone
    nums: ⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹"""
    tbg = True
    global TI, themes, theme, p, useFavorites, favorites, TIF, cava_bins, Windows
    Windows = ["²mem","³net","⁴proc"] #["¹cpu","²mem","³net","⁴proc","cava"]
    cava_bins = [0] * (W - 3)
    threading.Thread(target=audio_listener, daemon=True).start()
    warnings.filterwarnings("ignore")
    useFavorites = False
    favorites = [3,5,7,12,40]
    TIF = 0
    theme = ThemeEngine()
    themes = theme.ls()
    TI = themes.index("nord")
    theme.load_theme(themes[TI],tbg)
    p = theme.newP()
    #input(p)
    def P (l):
        RR = ""
        for i in range(len(l)):
            RR += p[l[i]]
        return RR
    clear()
    def ft (t:str):
        return f'{p["hi_fg"]}{t[0]}{p["title"]}{t[1::]}{P(["r", ""])}'
    
    padding_len = max(1, W - 12)
    global ms
    ms = 1000
    cpuName, GHz = get_cpu_info()
    IC = get_per_core_load()
    update_load_history(get_cpu_load())
    current_queue = pdh.get_value(r"\System\Processor Queue Length")
    load_history.append(current_queue)

    print(end=
        f'{p["main_bg"]}{p["main_fg"]}' +
        f'{bd(["TL","TR"], CC=p["cpu_box"])}{ft("¹cpu")}{bd(["TL","TR"], CC=p["cpu_box"])}{ft("menu")}{bd(["TL","TR"], CC=p["cpu_box"])}{ft("preset *")}' +
        f'{bd(["TL","TR"], int(padding_len/2) - 24, p["cpu_box"])}{p["title"]}{time.strftime("%H:%M:%S")}{p["main_fg"]}' +
        f'{bd(["TL","TR"], int((padding_len-1)/2) - len(str(ms)) - 10, p["cpu_box"])}{p["r"]}' +
        f'{ft("-")}{ft(f" {ms}ms ")}{ft("+")}{p["main_fg"]} '
    )

    place(W-33, 3, f'{cpuName}{bd(["TL","TR"], 4, p["cpu_box"])}{GHz} GHz')
    place(W-35,4,f"CPU graph {get_cpu_load()}")
    for i in range(len(IC)):
        place(W-35,5+i,f"C{i}  graph {IC[i]}")
    GLA = get_load_averages()
    place(W-35, 5+len(IC), f"Load AVG: {GLA[0]:>5.2f}  {GLA[1]:>5.2f}  {GLA[2]:>5.2f}", save=True)
    place(W-3, 3, bd(["TL","TR","BR","BL","TL","TR"], [0,6,33,6,1], p["cpu_box"]), save=False)
    place(W-3, 1, bd(["TL","TR","BR","BL"], [1,H-3,W-2], CC=p["cpu_box"]), save=False)
    place(1,2,bd("V",H - 3,p["cpu_box"]),CLS=False)
    print()

    def switchTheme(n=(TIF if useFavorites else TI)):
        global TI, theme, p, TIF, useFavorites, favorites
        if useFavorites and favorites:
            TIF = n % len(favorites)
            TI = favorites[TIF]
        else:
            TI = n % len(themes)
        theme.load_theme(themes[TI],tbg)
        p = theme.newP()
        return TIF if useFavorites else TI

    

    #["¹cpu","²mem","³net","⁴proc","cava"]
    # shortcuts
    s = {"1":"toggle_item(Windows, '¹cpu')",
         "2":"toggle_item(Windows, '²mem')",
         "3":"toggle_item(Windows, '³net')",
         "4":"toggle_item(Windows, '⁴proc')",
         "c":"toggle_item(Windows, 'cava')",
         "t":"pass",
         "-":"global ms\nms = max(ms - 100, 100)",
         "+":"global ms\nms = min(ms + 100, 5000)",
         "k": "switchTheme((favorites.index(TI) - 1) % len(favorites) if useFavorites else TI - 1)",
         "l": "switchTheme((favorites.index(TI) + 1) % len(favorites) if useFavorites else TI + 1)",
         "j": "global favorites\nif TI in favorites:\n    favorites.remove(TI)\nelse:\n    favorites.append(TI)",
         "J":"global useFavorites\nuseFavorites = not useFavorites\nswitchTheme()",
         "q":"global quit\nquit = True"
    }
    Cs = {('BTN_START',1):s["-"],
          ('BTN_SELECT',1):s["+"],
          ('R_TRIGGER',255):s["q"],
          }
    infilter = False
    filter = ""
    global lastUpdate
    lastUpdate = time.time()
    cpu_width = 100
    global graph_w, graph_h, cpu_cache, D
    graph_w, graph_h = 90, 10
    cpu_cache = collections.deque(maxlen=max(200, graph_w))
    D = []
    def types():
        global D
        while True:
            new_D = []
            for part in psutil.disk_partitions(all=False):
                if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
                    continue
                drive_name = part.device.replace('\\', '')
                new_D.append(get_disk_type(drive_name[:-1]))
            D = new_D 
            time.sleep(10)
    threading.Thread(target=types, daemon=True).start()
    with RawTerminal():
        while True:
            # get inputs
            global update, quit
            
            def update():
                global lastUpdate
                csy = H - 2
                csx = 2
                ch  = H - 1
                cw  = W - 3
                if "¹cpu" in Windows:
                    ch -= 14
                if "⁴proc" in Windows:
                    cw -= 70
                if "³net" in Windows:
                    csy -= 12
                    ch  -= 12
                
                
                if "cava" in Windows:
                    sy = csy - 10
                    cava_graph(csy, csx ,ch , p["proc_misc"], cava_bins[0:cw])
                elif "²mem" in Windows:
                    sy = 13 if "¹cpu" in Windows else 2 
                    M = get_memory()
                    Disks = get_disks()
                    for i, j in enumerate(["total","used","avail","cache","commi"]):
                        place(csx, sy + 1 + i, f"{j[0].upper() + j[1:]}:{' ' * (11 - len(j))}{M[j]:>10}")
                    place(csx, sy + 7, f"Page files: {M['page_total']:>10}")
                    place(csx, sy + 8, f"Used:       {M['page_used']:>10}")
                    disk_x = min(cw - 4, W - 3) // 2
                    place(disk_x, sy + 1, "Letter-Total-used-avail-HDD/SDD", save=True)
                    for i, disk in enumerate(Disks):
                        y_offset = i * 2
                        place(disk_x, sy + 2 + y_offset, f'{(disk["name"]+":"):<3}|{disk["total"]:<10}|{disk["used"]:<10}|{disk["io_percent"]}')
                        place(disk_x, sy + 3 + y_offset, f'   |{disk["free"]:<10}|{D[i] if len(D) > i else "loading..."}')
                    if sy == 2:
                        cava_graph(csy + 3, csx, ch - 11, p["proc_misc"], cava_bins[0:cw])
                if "cava" in Windows or "²mem" in Windows:
                    sy = 13 if "¹cpu" in Windows else 2
                    place(1, 2, bd("V", H - 3, p["cpu_box"]), CLS=False)
                    place(1, sy, bd(["TL","TR","BR","BL","TL"], [min(cw+1, W-3), min(ch, H-2), min(cw+1, W-3), min(ch, H-2)], p["mem_box"]), save=True)
                    if "²mem" in Windows:
                        place(3, sy, f"{p['mem_box']}┐{ft('²mem')}{p['mem_box']}┌{bd('H', min(cw-14, W-3)//2, p['mem_box'])}{p['mem_box']}┬─┐Disks{bd(['TL','TR'], min(cw-15, W-3)//2, p['mem_box'])}")
                    else:
                        place(3, sy, f"{p['mem_box']}┐{ft('cava')}{bd(['TL','TR'], min(cw-6, W-3), p['mem_box'])}")
                    if "²mem" in Windows and sy == 2:
                        sy = csy - 9
                        place(1,sy,bd(["TL","TR"],2,p['mem_box']))
                        place(3, sy, f"{p['mem_box']}┐{ft('cava')}{bd(['TL','TR'], min(cw-6, W-3), p['mem_box'])}")
                place(0,0,
                    f'{p["main_bg"]}{p["main_fg"]}' +
                    f'{bd(["TL","TR"], CC=p["cpu_box"])}{ft("¹cpu")}{bd(["TL","TR"], CC=p["cpu_box"])}{ft("menu")}{bd(["TL","TR"], CC=p["cpu_box"])}{ft("preset *")}' +
                    f'{bd(["TL","TR"], int(padding_len/2) - 24, p["cpu_box"])}{p["title"]}{time.strftime("%H:%M:%S")}{p["main_fg"]}' +
                    f'{bd(["TL","TR"], int((padding_len-1)/2) - len(str(ms)) - 10, p["cpu_box"])}{p["r"]}'
                )
                
                place(W-14-(4-len(str(ms))), 1, f'{bd("H", 2 if len(str(ms)) == 3 else 0, p["cpu_box"]) + bd("TR", CC=p["cpu_box"])}{ft("-")}{ft(f" {ms}ms ")}{ft("+")}')
                clock_tick(int(padding_len/2) + 4, 1, p["title"], False, False, True, False)
                if time.time() - lastUpdate < (ms/1000):
                    if not ["¹cpu"] == Windows:
                        place(W-3, 3, bd(["TL","TR","BR","BL","TL","TR"], [0,6,33,6,1], p["cpu_box"]), save=True)
                        place(W-3, 1, bd(["TL","TR","BR","BL"], [1,10,W-2], CC=p["cpu_box"]), save=True)
                    #place(1, 13,  bd(["TL","TR"], W-3, p["cpu_box"]), save=True)
                    print("\n"*(H-2))
                    return None
                lastUpdate = time.time()
                cpul = get_cpu_load()
                cpu_cache.append(cpul)
                IC = get_per_core_load()
                GLA = get_load_averages()
                if ["¹cpu"] == Windows:
                    ey = 23
                    ex = 40
                    frame_buffer = []
                    frame_buffer.append(clear_graph_area(1, 2, graph_w + ex, graph_h + ey))
                    frame_buffer.append(cpu_graph(2, 2, graph_w + ex, graph_h + ey, cpu_cache, [p['cpu_start'],p['cpu_mid'],p['cpu_end']]))
                    sys.stdout.write("".join(frame_buffer))
                    sys.stdout.flush()
                    place(W-35,4,f"CPU {generate_cpu_bar(cpul,24,[p['cpu_start'],p['cpu_mid'],p['cpu_end']])} {int(cpul):>3}%",save=True)
                    for i in range(len(IC)):
                        place(W-35,5+i,f"C{i}  {generate_cpu_bar(IC[i],24,[p['cpu_start'],p['cpu_mid'],p['cpu_end']])} {int(IC[i]):>3}%",save=True)
                    place(W-35,5+len(IC),f"Load AVG: {GLA[0]:>4.2f}  {GLA[1]:>4.2f}  {GLA[2]:>4.2f}")
                
                    # Draw boxes
                    #place(W-3, 3, bd(["TL","TR","BR","BL","TL","TR"], [0,6,33 + ey,6,1], p["cpu_box"]), save=False)
                    #place(W-3, 1, bd(["TL","TR","BR","BL"], [1,H-3,W-2], CC=p["cpu_box"]), save=False)
                    print()
                elif "¹cpu" in Windows:
                    frame_buffer = []
                    frame_buffer.append(clear_graph_area(3, 2, graph_w, graph_h))
                    frame_buffer.append(cpu_graph(3, 2, graph_w, graph_h, cpu_cache, [p['cpu_start'],p['cpu_mid'],p['cpu_end']]))
                    sys.stdout.write("".join(frame_buffer))
                    sys.stdout.flush()
                    place(W-35,4,f"CPU {generate_cpu_bar(cpul,24,[p['cpu_start'],p['cpu_mid'],p['cpu_end']])} {int(cpul):>3}%",save=True)
                    for i in range(len(IC)):
                        place(W-35,5+i,f"C{i}  {generate_cpu_bar(IC[i],24,[p['cpu_start'],p['cpu_mid'],p['cpu_end']])} {int(IC[i]):>3}%",save=True)
                    place(W-35,5+len(IC),f"Load AVG: {GLA[0]:>4.2f}  {GLA[1]:>4.2f}  {GLA[2]:>4.2f}")
                
                    # Draw boxes
                    place(W-3, 3, bd(["TL","TR","BR","BL","TL","TR"], [0,6,33,6,1], p["cpu_box"]), save=False)
                    place(W-3, 1, bd(["TL","TR","BR","BL"], [1,H-3,W-2], CC=p["cpu_box"]), save=False)
                    print()
            
            response = finput(max_length=1, vis=False, tick_func=update, inputs=["keyboard", "mouse", "ESC", "arrows", "controller"])
            if "ESC" in response:
                break
            elif "controller" in response:
                response = response["controller"]
                sys.stdout.write("\x1b[2K\x1b[1G")
                for i in range(len(response)):
                    sys.stdout.write(f"{response[i]}" + ("," if i < len(response) - 1 else "")) 
                sys.stdout.flush()
                quit = False
                for r in response:
                    if r in Cs:
                        exec(Cs[r])
                if quit:
                    break
            elif "keyboard" in response:
                print(end=f'\x1b[2K\x1b[1G')
                response = response["keyboard"]
                if infilter:
                    filter += response
                elif response in s:
                    quit = False
                    exec(s[response])
                    if quit:
                        break
            elif "arrows" in response:
                response = response["arrows"]
                print(end=f'\x1b[2K\x1b[1G{response}')
            elif "mouse" in response:
                action_char, btn_name, x, y = response["mouse"]
                action = "Pressed" if action_char == 'M' else "Released"
                print(end=f'\x1b[2K\x1b[1G{action=},{btn_name=},{x=},{y=}')

ANSI = re.compile(r"\x1b\[[0-9;]*m")

def strip_ansi(s):
    return ANSI.sub("", s)

def themeDemo(t="nord"):
    """ANSI theme preview table (proper alignment)"""

    theme.load_theme(t,tbg=True)
    p = theme.newP()

    items = [
        [["main_bg", "main_fg", "title", "hi_fg"],
        ["selected_bg", "selected_fg", "inactive_fg"],
        ["proc_misc"],
        ["cpu_box", "mem_box", "net_box", "proc_box"],
        ["div_line"]],

        [["temp_start", "temp_mid", "temp_end"],
        ["cpu_start", "cpu_mid", "cpu_end"]],

        [["free_start", "free_mid", "free_end"],
        ["cached_start", "cached_mid", "cached_end"],
        ["available_start", "available_mid", "available_end"],
        ["used_start", "used_mid", "used_end"]],

        [["download_start", "download_mid", "download_end"],
        ["upload_start", "upload_mid", "upload_end"]],
    ]

    reset = p.get("r", "\033[0m")
    col_width = 16

    print("\n--- theme preveiw ---\n")

    for block in items:
        max_rows = max(len(row) for row in block)

        for i in range(max_rows):
            row_out = ""

            for row in block:
                if i < len(row):
                    k = row[i]
                    val = p.get(k, "")
                    cell = f"{val}{k}{reset}"

                    visible_len = len(strip_ansi(cell))
                    padding = col_width - visible_len

                    row_out += cell + (" " * max(padding, 1)) + "| "
                else:
                    row_out += (" " * col_width) + "| "

            print(row_out)

        print("-" * (col_width * len(block)))

    print("\n--- color blocks ---\n")

    groups = [
        ("UI", ["main_bg", "main_fg", "title", "hi_fg"]),
        ("Boxes", ["cpu_box", "mem_box", "net_box", "proc_box", "div_line"]),
        ("Selection", ["selected_bg", "selected_fg", "inactive_fg"]),
        ("Graphs CPU", ["cpu_start", "cpu_mid", "cpu_end"]),
        ("Graphs MEM", ["used_start", "used_mid", "used_end"]),
        ("Network", ["download_start", "download_mid", "download_end"]),
    ]

    for name, keys in groups:
        line = f"{name:<12} | "
        for k in keys:
            if k in p:
                line += f"{p[k]}█{reset}"
            else:
                line += " "
        print(line)

    print()

cava_bins = [0] * 50
def audio_listener():
    global cava_bins
    speaker = sc.default_speaker()
    mic = sc.get_microphone(speaker.id, include_loopback=True)

    with mic.recorder(samplerate=44100) as mic_stream: 
        while True:
            try:
                data = mic_stream.record(numframes=1024)
                mono_data = data[:, 0]

                windowed_data = mono_data * np.hanning(len(mono_data))
                fft_data = np.abs(np.fft.rfft(windowed_data))
                fft_data = fft_data[:len(fft_data)//2]
                bins = np.array_split(fft_data, len(cava_bins))
                new_volumes = [np.mean(b) * 1.5 for b in bins]
                
                # smoothing
                for i in range(len(cava_bins)):
                    # 70% old value, 30% new value
                    cava_bins[i] = (cava_bins[i] * 0.7) + (new_volumes[i] * 0.3)
            except Exception:
                pass

def cava_graph(bottom_row, start_col, max_height, color=color("default"), bins=cava_bins):
    if not bins or len(bins) == 0 or np.isnan(bins[0]):
        return
        
    frame_buffer = "\033[H" 
    
    for col_index, volume in enumerate(bins):
        val = min(max(float(volume), 0.0), float(max_height))

        # 9.8 -> (9, 0.8)
        full_blocks = int(val)
        fraction = val - full_blocks
        fraction_index = int(fraction * len(BLOCKS))
        
        for h in range(max_height):
            current_row = bottom_row - h

            if h < full_blocks:
                char = "█"
            elif h == full_blocks:
                char = BLOCKS[min(fraction_index, len(BLOCKS) - 1)]
            else:
                char = " "
                
            frame_buffer += f"\033[{current_row};{start_col + col_index}H{color}{char}\033[0m"
            
    sys.stdout.write(frame_buffer)
    sys.stdout.flush()

def cavaDemo():
    global cava_bins
    threading.Thread(target=audio_listener, daemon=True).start()
    warnings.filterwarnings("ignore")
    cava_bins = [0] * W
    while True:
        cava_graph(H,1,H)
        time.sleep(0.05)

import flipper
def main():
    flipper.start()
    if flipper.port:
        flipper.cli(flipper.port)
    else:
        print("no port")

def themeselect(themes = theme.ls()):
    i = 0
    favroites = []
    with RawTerminal():
        while True:
            clear()
            print(f"theme = {i}, {themes[i]}\n")
            themeDemo(themes[i])
            I = finput(inputs=["arrows"]).get("arrows")
            if I == "DOWN":
                break
            elif I == "UP":
                favroites.append(themes[i])
            elif I == "RIGHT":
                i = (i + 1) % len(themes)
            elif I == "LEFT":
                i = (i - 1) % len(themes)
        print(favroites)

def fDemo():
    print("""c
[0mnormal abc _ █▚[0m         normal abc _ █▚[0m   [0m[40m [0m[41m [0m[42m [0m[43m [0m[44m [0m[45m [0m[46m [0m[47m [0m[100m [0m[101m [0m[102m [0m[103m [0m[104m [0m[105m [0m[106m [0m[107m [0m
[0m faint [0m[2mabc _ █▚[0m        italic  [0m[3mabc _ █▚[0m   [0m[48;5;0m [0m[48;5;1m [0m[48;5;2m [0m[48;5;3m [0m[48;5;4m [0m[48;5;5m [0m[48;5;6m [0m[48;5;7m [0m[48;5;8m [0m[48;5;9m [0m[48;5;10m [0m[48;5;11m [0m[48;5;12m [0m[48;5;13m [0m[48;5;14m [0m[48;5;15m [0m  [0m[38;2;8;0;0;48;2;0;0;0m▄[0m[38;2;9;0;0;48;2;1;0;0m▄[0m[38;2;10;0;0;48;2;2;0;0m▄[0m[38;2;11;0;0;48;2;3;0;0m▄[0m[38;2;12;0;0;48;2;4;0;0m▄[0m[38;2;13;0;0;48;2;5;0;0m▄[0m[38;2;14;0;0;48;2;6;0;0m▄[0m[38;2;15;0;0;48;2;7;0;0m▄[0m[38;2;16;0;0;48;2;8;0;0m▄[0m[38;2;17;0;0;48;2;9;0;0m▄[0m[38;2;18;0;0;48;2;10;0;0m▄[0m[38;2;19;0;0;48;2;11;0;0m▄[0m[38;2;20;0;0;48;2;12;0;0m▄[0m[38;2;21;0;0;48;2;13;0;0m▄[0m[38;2;22;0;0;48;2;14;0;0m▄[0m[38;2;23;0;0;48;2;15;0;0m▄[0m [0m[38;2;153;0;0;48;2;152;0;0m▄[0m
[0mnormal abc _ █▚[0m      underline [0m[4mabc _ █▚[0m   [0m[48;5;16m [0m[48;5;17m [0m[48;5;18m [0m[48;5;19m [0m[48;5;20m [0m[48;5;21m [0m[48;5;22m [0m[48;5;23m [0m[48;5;24m [0m[48;5;25m [0m[48;5;26m [0m[48;5;27m [0m[48;5;28m [0m[48;5;29m [0m[48;5;30m [0m[48;5;31m [0m  [0m[38;2;24;0;0;48;2;16;0;0m▄[0m[38;2;25;0;0;48;2;17;0;0m▄[0m[38;2;26;0;0;48;2;18;0;0m▄[0m[38;2;27;0;0;48;2;19;0;0m▄[0m[38;2;28;0;0;48;2;20;0;0m▄[0m[38;2;29;0;0;48;2;21;0;0m▄[0m[38;2;30;0;0;48;2;22;0;0m▄[0m[38;2;31;0;0;48;2;23;0;0m▄[0m[38;2;32;0;0;48;2;24;0;0m▄[0m[38;2;33;0;0;48;2;25;0;0m▄[0m[38;2;34;0;0;48;2;26;0;0m▄[0m[38;2;35;0;0;48;2;27;0;0m▄[0m[38;2;36;0;0;48;2;28;0;0m▄[0m[38;2;37;0;0;48;2;29;0;0m▄[0m[38;2;38;0;0;48;2;30;0;0m▄[0m[38;2;39;0;0;48;2;31;0;0m▄[0m [0m[38;2;155;0;0;48;2;154;0;0m▄[0m
[0m  bold [0m[1mabc _ █▚[0m      underlinD [0m[21mabc _ █▚[0m   [0m[48;5;32m [0m[48;5;33m [0m[48;5;34m [0m[48;5;35m [0m[48;5;36m [0m[48;5;37m [0m[48;5;38m [0m[48;5;39m [0m[48;5;40m [0m[48;5;41m [0m[48;5;42m [0m[48;5;43m [0m[48;5;44m [0m[48;5;45m [0m[48;5;46m [0m[48;5;47m [0m  [0m[38;2;40;0;0;48;2;32;0;0m▄[0m[38;2;41;0;0;48;2;33;0;0m▄[0m[38;2;42;0;0;48;2;34;0;0m▄[0m[38;2;43;0;0;48;2;35;0;0m▄[0m[38;2;44;0;0;48;2;36;0;0m▄[0m[38;2;45;0;0;48;2;37;0;0m▄[0m[38;2;46;0;0;48;2;38;0;0m▄[0m[38;2;47;0;0;48;2;39;0;0m▄[0m[38;2;48;0;0;48;2;40;0;0m▄[0m[38;2;49;0;0;48;2;41;0;0m▄[0m[38;2;50;0;0;48;2;42;0;0m▄[0m[38;2;51;0;0;48;2;43;0;0m▄[0m[38;2;52;0;0;48;2;44;0;0m▄[0m[38;2;53;0;0;48;2;45;0;0m▄[0m[38;2;54;0;0;48;2;46;0;0m▄[0m[38;2;55;0;0;48;2;47;0;0m▄[0m [0m[38;2;157;0;0;48;2;156;0;0m▄[0m
[0m[0m                      overline [0m[53mabc _ █▚[0m   [0m[48;5;48m [0m[48;5;49m [0m[48;5;50m [0m[48;5;51m [0m[48;5;52m [0m[48;5;53m [0m[48;5;54m [0m[48;5;55m [0m[48;5;56m [0m[48;5;57m [0m[48;5;58m [0m[48;5;59m [0m[48;5;60m [0m[48;5;61m [0m[48;5;62m [0m[48;5;63m [0m  [0m[38;2;56;0;0;48;2;48;0;0m▄[0m[38;2;57;0;0;48;2;49;0;0m▄[0m[38;2;58;0;0;48;2;50;0;0m▄[0m[38;2;59;0;0;48;2;51;0;0m▄[0m[38;2;60;0;0;48;2;52;0;0m▄[0m[38;2;61;0;0;48;2;53;0;0m▄[0m[38;2;62;0;0;48;2;54;0;0m▄[0m[38;2;63;0;0;48;2;55;0;0m▄[0m[38;2;64;0;0;48;2;56;0;0m▄[0m[38;2;65;0;0;48;2;57;0;0m▄[0m[38;2;66;0;0;48;2;58;0;0m▄[0m[38;2;67;0;0;48;2;59;0;0m▄[0m[38;2;68;0;0;48;2;60;0;0m▄[0m[38;2;69;0;0;48;2;61;0;0m▄[0m[38;2;70;0;0;48;2;62;0;0m▄[0m[38;2;71;0;0;48;2;63;0;0m▄[0m [0m[38;2;159;0;0;48;2;158;0;0m▄[0m
[0mwhite on black[0m          blink  [0m[5mabc _ █▚[0m   [0m[48;5;64m [0m[48;5;65m [0m[48;5;66m [0m[48;5;67m [0m[48;5;68m [0m[48;5;69m [0m[48;5;70m [0m[48;5;71m [0m[48;5;72m [0m[48;5;73m [0m[48;5;74m [0m[48;5;75m [0m[48;5;76m [0m[48;5;77m [0m[48;5;78m [0m[48;5;79m [0m  [0m[38;2;72;0;0;48;2;64;0;0m▄[0m[38;2;73;0;0;48;2;65;0;0m▄[0m[38;2;74;0;0;48;2;66;0;0m▄[0m[38;2;75;0;0;48;2;67;0;0m▄[0m[38;2;76;0;0;48;2;68;0;0m▄[0m[38;2;77;0;0;48;2;69;0;0m▄[0m[38;2;78;0;0;48;2;70;0;0m▄[0m[38;2;79;0;0;48;2;71;0;0m▄[0m[38;2;80;0;0;48;2;72;0;0m▄[0m[38;2;81;0;0;48;2;73;0;0m▄[0m[38;2;82;0;0;48;2;74;0;0m▄[0m[38;2;83;0;0;48;2;75;0;0m▄[0m[38;2;84;0;0;48;2;76;0;0m▄[0m[38;2;85;0;0;48;2;77;0;0m▄[0m[38;2;86;0;0;48;2;78;0;0m▄[0m[38;2;87;0;0;48;2;79;0;0m▄[0m [0m[38;2;161;0;0;48;2;160;0;0m▄[0m
[0mnormal [0m[40m[37mabc _ █▚[0m        inverse [0m[7mabc _ █▚[0m   [0m[48;5;80m [0m[48;5;81m [0m[48;5;82m [0m[48;5;83m [0m[48;5;84m [0m[48;5;85m [0m[48;5;86m [0m[48;5;87m [0m[48;5;88m [0m[48;5;89m [0m[48;5;90m [0m[48;5;91m [0m[48;5;92m [0m[48;5;93m [0m[48;5;94m [0m[48;5;95m [0m  [0m[38;2;88;0;0;48;2;80;0;0m▄[0m[38;2;89;0;0;48;2;81;0;0m▄[0m[38;2;90;0;0;48;2;82;0;0m▄[0m[38;2;91;0;0;48;2;83;0;0m▄[0m[38;2;92;0;0;48;2;84;0;0m▄[0m[38;2;93;0;0;48;2;85;0;0m▄[0m[38;2;94;0;0;48;2;86;0;0m▄[0m[38;2;95;0;0;48;2;87;0;0m▄[0m[38;2;96;0;0;48;2;88;0;0m▄[0m[38;2;97;0;0;48;2;89;0;0m▄[0m[38;2;98;0;0;48;2;90;0;0m▄[0m[38;2;99;0;0;48;2;91;0;0m▄[0m[38;2;100;0;0;48;2;92;0;0m▄[0m[38;2;101;0;0;48;2;93;0;0m▄[0m[38;2;102;0;0;48;2;94;0;0m▄[0m[38;2;103;0;0;48;2;95;0;0m▄[0m [0m[38;2;163;0;0;48;2;162;0;0m▄[0m
[0m faint [0m[40m[37m[2mabc _ █▚[0m         strike [0m[9mabc _ █▚[0m   [0m[48;5;96m [0m[48;5;97m [0m[48;5;98m [0m[48;5;99m [0m[48;5;100m [0m[48;5;101m [0m[48;5;102m [0m[48;5;103m [0m[48;5;104m [0m[48;5;105m [0m[48;5;106m [0m[48;5;107m [0m[48;5;108m [0m[48;5;109m [0m[48;5;110m [0m[48;5;111m [0m  [0m[38;2;104;0;0;48;2;96;0;0m▄[0m[38;2;105;0;0;48;2;97;0;0m▄[0m[38;2;106;0;0;48;2;98;0;0m▄[0m[38;2;107;0;0;48;2;99;0;0m▄[0m[38;2;108;0;0;48;2;100;0;0m▄[0m[38;2;109;0;0;48;2;101;0;0m▄[0m[38;2;110;0;0;48;2;102;0;0m▄[0m[38;2;111;0;0;48;2;103;0;0m▄[0m[38;2;112;0;0;48;2;104;0;0m▄[0m[38;2;113;0;0;48;2;105;0;0m▄[0m[38;2;114;0;0;48;2;106;0;0m▄[0m[38;2;115;0;0;48;2;107;0;0m▄[0m[38;2;116;0;0;48;2;108;0;0m▄[0m[38;2;117;0;0;48;2;109;0;0m▄[0m[38;2;118;0;0;48;2;110;0;0m▄[0m[38;2;119;0;0;48;2;111;0;0m▄[0m [0m[38;2;165;0;0;48;2;164;0;0m▄[0m
[0m[0m                     invisible [0m[8mabc _ █▚[0m   [0m[48;5;112m [0m[48;5;113m [0m[48;5;114m [0m[48;5;115m [0m[48;5;116m [0m[48;5;117m [0m[48;5;118m [0m[48;5;119m [0m[48;5;120m [0m[48;5;121m [0m[48;5;122m [0m[48;5;123m [0m[48;5;124m [0m[48;5;125m [0m[48;5;126m [0m[48;5;127m [0m  [0m[38;2;120;0;0;48;2;112;0;0m▄[0m[38;2;121;0;0;48;2;113;0;0m▄[0m[38;2;122;0;0;48;2;114;0;0m▄[0m[38;2;123;0;0;48;2;115;0;0m▄[0m[38;2;124;0;0;48;2;116;0;0m▄[0m[38;2;125;0;0;48;2;117;0;0m▄[0m[38;2;126;0;0;48;2;118;0;0m▄[0m[38;2;127;0;0;48;2;119;0;0m▄[0m[38;2;128;0;0;48;2;120;0;0m▄[0m[38;2;129;0;0;48;2;121;0;0m▄[0m[38;2;130;0;0;48;2;122;0;0m▄[0m[38;2;131;0;0;48;2;123;0;0m▄[0m[38;2;132;0;0;48;2;124;0;0m▄[0m[38;2;133;0;0;48;2;125;0;0m▄[0m[38;2;134;0;0;48;2;126;0;0m▄[0m[38;2;135;0;0;48;2;127;0;0m▄[0m [0m[38;2;167;0;0;48;2;166;0;0m▄[0m
[0m[0m                     [0m                     [0m[48;5;128m [0m[48;5;129m [0m[48;5;130m [0m[48;5;131m [0m[48;5;132m [0m[48;5;133m [0m[48;5;134m [0m[48;5;135m [0m[48;5;136m [0m[48;5;137m [0m[48;5;138m [0m[48;5;139m [0m[48;5;140m [0m[48;5;141m [0m[48;5;142m [0m[48;5;143m [0m  [0m[38;2;136;0;0;48;2;128;0;0m▄[0m[38;2;137;0;0;48;2;129;0;0m▄[0m[38;2;138;0;0;48;2;130;0;0m▄[0m[38;2;139;0;0;48;2;131;0;0m▄[0m[38;2;140;0;0;48;2;132;0;0m▄[0m[38;2;141;0;0;48;2;133;0;0m▄[0m[38;2;142;0;0;48;2;134;0;0m▄[0m[38;2;143;0;0;48;2;135;0;0m▄[0m[38;2;144;0;0;48;2;136;0;0m▄[0m[38;2;145;0;0;48;2;137;0;0m▄[0m[38;2;146;0;0;48;2;138;0;0m▄[0m[38;2;147;0;0;48;2;139;0;0m▄[0m[38;2;148;0;0;48;2;140;0;0m▄[0m[38;2;149;0;0;48;2;141;0;0m▄[0m[38;2;150;0;0;48;2;142;0;0m▄[0m[38;2;151;0;0;48;2;143;0;0m▄[0m [0m[38;2;169;0;0;48;2;168;0;0m▄[0m
[0mcolors plus B N F[0m    B N F    B N F[0m       [0m[48;5;144m [0m[48;5;145m [0m[48;5;146m [0m[48;5;147m [0m[48;5;148m [0m[48;5;149m [0m[48;5;150m [0m[48;5;151m [0m[48;5;152m [0m[48;5;153m [0m[48;5;154m [0m[48;5;155m [0m[48;5;156m [0m[48;5;157m [0m[48;5;158m [0m[48;5;159m [0m  [0m[38;2;152;0;0;48;2;144;0;0m▄[0m[38;2;153;0;0;48;2;145;0;0m▄[0m[38;2;154;0;0;48;2;146;0;0m▄[0m[38;2;155;0;0;48;2;147;0;0m▄[0m[38;2;156;0;0;48;2;148;0;0m▄[0m[38;2;157;0;0;48;2;149;0;0m▄[0m[38;2;158;0;0;48;2;150;0;0m▄[0m[38;2;159;0;0;48;2;151;0;0m▄[0m[38;2;160;0;0;48;2;152;0;0m▄[0m[38;2;161;0;0;48;2;153;0;0m▄[0m[38;2;162;0;0;48;2;154;0;0m▄[0m[38;2;163;0;0;48;2;155;0;0m▄[0m[38;2;164;0;0;48;2;156;0;0m▄[0m[38;2;165;0;0;48;2;157;0;0m▄[0m[38;2;166;0;0;48;2;158;0;0m▄[0m[38;2;167;0;0;48;2;159;0;0m▄[0m [0m[38;2;171;0;0;48;2;170;0;0m▄[0m
[0m            [0m[30m[1mab[0m[30mab[0m[30m[2mab[0m   [0m[90m[1mab[0m[90mab[0m[90m[2mab   [0m[38;5;245m[1mab[0m[38;5;245mab[0m[38;5;245m[2mab[0m      [0m[48;5;160m [0m[48;5;161m [0m[48;5;162m [0m[48;5;163m [0m[48;5;164m [0m[48;5;165m [0m[48;5;166m [0m[48;5;167m [0m[48;5;168m [0m[48;5;169m [0m[48;5;170m [0m[48;5;171m [0m[48;5;172m [0m[48;5;173m [0m[48;5;174m [0m[48;5;175m [0m  [0m[38;2;168;0;0;48;2;160;0;0m▄[0m[38;2;169;0;0;48;2;161;0;0m▄[0m[38;2;170;0;0;48;2;162;0;0m▄[0m[38;2;171;0;0;48;2;163;0;0m▄[0m[38;2;172;0;0;48;2;164;0;0m▄[0m[38;2;173;0;0;48;2;165;0;0m▄[0m[38;2;174;0;0;48;2;166;0;0m▄[0m[38;2;175;0;0;48;2;167;0;0m▄[0m[38;2;176;0;0;48;2;168;0;0m▄[0m[38;2;177;0;0;48;2;169;0;0m▄[0m[38;2;178;0;0;48;2;170;0;0m▄[0m[38;2;179;0;0;48;2;171;0;0m▄[0m[38;2;180;0;0;48;2;172;0;0m▄[0m[38;2;181;0;0;48;2;173;0;0m▄[0m[38;2;182;0;0;48;2;174;0;0m▄[0m[38;2;183;0;0;48;2;175;0;0m▄[0m [0m[38;2;173;0;0;48;2;172;0;0m▄[0m
[0m            [0m[31m[1mab[0m[31mab[0m[31m[2mab[0m   [0m[91m[1mab[0m[91mab[0m[91m[2mab[0m               [0m[48;5;176m [0m[48;5;177m [0m[48;5;178m [0m[48;5;179m [0m[48;5;180m [0m[48;5;181m [0m[48;5;182m [0m[48;5;183m [0m[48;5;184m [0m[48;5;185m [0m[48;5;186m [0m[48;5;187m [0m[48;5;188m [0m[48;5;189m [0m[48;5;190m [0m[48;5;191m [0m  [0m[38;2;184;0;0;48;2;176;0;0m▄[0m[38;2;185;0;0;48;2;177;0;0m▄[0m[38;2;186;0;0;48;2;178;0;0m▄[0m[38;2;187;0;0;48;2;179;0;0m▄[0m[38;2;188;0;0;48;2;180;0;0m▄[0m[38;2;189;0;0;48;2;181;0;0m▄[0m[38;2;190;0;0;48;2;182;0;0m▄[0m[38;2;191;0;0;48;2;183;0;0m▄[0m[38;2;192;0;0;48;2;184;0;0m▄[0m[38;2;193;0;0;48;2;185;0;0m▄[0m[38;2;194;0;0;48;2;186;0;0m▄[0m[38;2;195;0;0;48;2;187;0;0m▄[0m[38;2;196;0;0;48;2;188;0;0m▄[0m[38;2;197;0;0;48;2;189;0;0m▄[0m[38;2;198;0;0;48;2;190;0;0m▄[0m[38;2;199;0;0;48;2;191;0;0m▄[0m [0m[38;2;175;0;0;48;2;174;0;0m▄[0m
[0m            [0m[32m[1mab[0m[32mab[0m[32m[2mab[0m   [0m[92m[1mab[0m[92mab[0m[92m[2mab[0m               [0m[48;5;192m [0m[48;5;193m [0m[48;5;194m [0m[48;5;195m [0m[48;5;196m [0m[48;5;197m [0m[48;5;198m [0m[48;5;199m [0m[48;5;200m [0m[48;5;201m [0m[48;5;202m [0m[48;5;203m [0m[48;5;204m [0m[48;5;205m [0m[48;5;206m [0m[48;5;207m [0m  [0m[38;2;200;0;0;48;2;192;0;0m▄[0m[38;2;201;0;0;48;2;193;0;0m▄[0m[38;2;202;0;0;48;2;194;0;0m▄[0m[38;2;203;0;0;48;2;195;0;0m▄[0m[38;2;204;0;0;48;2;196;0;0m▄[0m[38;2;205;0;0;48;2;197;0;0m▄[0m[38;2;206;0;0;48;2;198;0;0m▄[0m[38;2;207;0;0;48;2;199;0;0m▄[0m[38;2;208;0;0;48;2;200;0;0m▄[0m[38;2;209;0;0;48;2;201;0;0m▄[0m[38;2;210;0;0;48;2;202;0;0m▄[0m[38;2;211;0;0;48;2;203;0;0m▄[0m[38;2;212;0;0;48;2;204;0;0m▄[0m[38;2;213;0;0;48;2;205;0;0m▄[0m[38;2;214;0;0;48;2;206;0;0m▄[0m[38;2;215;0;0;48;2;207;0;0m▄[0m [0m[38;2;177;0;0;48;2;176;0;0m▄[0m
[0m            [0m[33m[1mab[0m[33mab[0m[33m[2mab[0m   [0m[93m[1mab[0m[93mab[0m[93m[2mab[0m               [0m[48;5;208m [0m[48;5;209m [0m[48;5;210m [0m[48;5;211m [0m[48;5;212m [0m[48;5;213m [0m[48;5;214m [0m[48;5;215m [0m[48;5;216m [0m[48;5;217m [0m[48;5;218m [0m[48;5;219m [0m[48;5;220m [0m[48;5;221m [0m[48;5;222m [0m[48;5;223m [0m  [0m[38;2;216;0;0;48;2;208;0;0m▄[0m[38;2;217;0;0;48;2;209;0;0m▄[0m[38;2;218;0;0;48;2;210;0;0m▄[0m[38;2;219;0;0;48;2;211;0;0m▄[0m[38;2;220;0;0;48;2;212;0;0m▄[0m[38;2;221;0;0;48;2;213;0;0m▄[0m[38;2;222;0;0;48;2;214;0;0m▄[0m[38;2;223;0;0;48;2;215;0;0m▄[0m[38;2;224;0;0;48;2;216;0;0m▄[0m[38;2;225;0;0;48;2;217;0;0m▄[0m[38;2;226;0;0;48;2;218;0;0m▄[0m[38;2;227;0;0;48;2;219;0;0m▄[0m[38;2;228;0;0;48;2;220;0;0m▄[0m[38;2;229;0;0;48;2;221;0;0m▄[0m[38;2;230;0;0;48;2;222;0;0m▄[0m[38;2;231;0;0;48;2;223;0;0m▄[0m [0m[38;2;179;0;0;48;2;178;0;0m▄[0m
[0m            [0m[34m[1mab[0m[34mab[0m[34m[2mab[0m   [0m[94m[1mab[0m[94mab[0m[94m[2mab[0m               [0m[48;5;224m [0m[48;5;225m [0m[48;5;226m [0m[48;5;227m [0m[48;5;228m [0m[48;5;229m [0m[48;5;230m [0m[48;5;231m [0m[48;5;232m [0m[48;5;233m [0m[48;5;234m [0m[48;5;235m [0m[48;5;236m [0m[48;5;237m [0m[48;5;238m [0m[48;5;239m [0m  [0m[38;2;232;0;0;48;2;224;0;0m▄[0m[38;2;233;0;0;48;2;225;0;0m▄[0m[38;2;234;0;0;48;2;226;0;0m▄[0m[38;2;235;0;0;48;2;227;0;0m▄[0m[38;2;236;0;0;48;2;228;0;0m▄[0m[38;2;237;0;0;48;2;229;0;0m▄[0m[38;2;238;0;0;48;2;230;0;0m▄[0m[38;2;239;0;0;48;2;231;0;0m▄[0m[38;2;240;0;0;48;2;232;0;0m▄[0m[38;2;241;0;0;48;2;233;0;0m▄[0m[38;2;242;0;0;48;2;234;0;0m▄[0m[38;2;243;0;0;48;2;235;0;0m▄[0m[38;2;244;0;0;48;2;236;0;0m▄[0m[38;2;245;0;0;48;2;237;0;0m▄[0m[38;2;246;0;0;48;2;238;0;0m▄[0m[38;2;247;0;0;48;2;239;0;0m▄[0m [0m[38;2;181;0;0;48;2;180;0;0m▄[0m
[0m            [0m[35m[1mab[0m[35mab[0m[35m[2mab[0m   [0m[95m[1mab[0m[95mab[0m[95m[2mab[0m               [0m[48;5;240m [0m[48;5;241m [0m[48;5;242m [0m[48;5;243m [0m[48;5;244m [0m[48;5;245m [0m[48;5;246m [0m[48;5;247m [0m[48;5;248m [0m[48;5;249m [0m[48;5;250m [0m[48;5;251m [0m[48;5;252m [0m[48;5;253m [0m[48;5;254m [0m[48;5;255m [0m  [0m[38;2;248;0;0;48;2;240;0;0m▄[0m[38;2;249;0;0;48;2;241;0;0m▄[0m[38;2;250;0;0;48;2;242;0;0m▄[0m[38;2;251;0;0;48;2;243;0;0m▄[0m[38;2;252;0;0;48;2;244;0;0m▄[0m[38;2;253;0;0;48;2;245;0;0m▄[0m[38;2;254;0;0;48;2;246;0;0m▄[0m[38;2;255;0;0;48;2;247;0;0m▄[0m[38;2;255;0;0;48;2;248;0;0m▄[0m[38;2;255;0;0;48;2;249;0;0m▄[0m[38;2;255;0;0;48;2;250;0;0m▄[0m[38;2;255;0;0;48;2;251;0;0m▄[0m[38;2;255;0;0;48;2;252;0;0m▄[0m[38;2;255;0;0;48;2;253;0;0m▄[0m[38;2;255;0;0;48;2;254;0;0m▄[0m[38;2;255;0;0;48;2;255;0;0m▄[0m [0m[38;2;183;0;0;48;2;182;0;0m▄[0m
[0m            [0m[36m[1mab[0m[36mab[0m[36m[2mab[0m   [0m[96m[1mab[0m[96mab[0m[96m[2mab[0m               [0m
[0m            [0m[37m[1mab[0m[37mab[0m[37m[2mab[0m   [0m[97m[1mab[0m[97mab[0m[97m[2mab[0m               [0m
[0m""")

def rDemo():
    print("recourcess - (go check them out): ")
    print("https://github.com/ClaireCJS/clairecjs_bat/tree/main")
    print("https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797")
    print("https://terminalguide.namepad.de/seq/")

def EDemo():
    print(end="\033#8")

def SR():
    print(end="\0331 q")




rlock = threading.Lock()
#fetch_yt_audio("https://www.youtube.com/watch?v=MM2-z8inpY8&list=PLfP6i5T0-DkLlj5LDluZcpP9n6YlATpSG&index=3", "ex")
#fetch_yt_video("https://www.youtube.com/watch?v=MM2-z8inpY8&list=PLfP6i5T0-DkLlj5LDluZcpP9n6YlATpSG&index=3", "ex")

#clear()
#slideshowDemo(t=0.1)
if __name__ == "__main__":
    clear()
    #playFile("bg_music")
    #btopPy()
    #sixtelDemo()
    #themeselect()
    #main()
    target = "steam"
    global mw, h
    mw = 500
    h = 40

    windows = gw.getWindowsWithTitle(target)
    if windows:
        hwnd = windows[0]._hWnd
        t = threading.Thread(target=floop, kwargs={"func": finput,
        "kwargs": {"inputs": ["keyboard", "mouse", "ESC"],
            "custom_out": {"mouse":"""
                           win32gui.SetForegroundWindow(hwnd)
                           action, btn_name, t_col, t_row = value
                           rect = win32gui.GetWindowRect(hwnd)
                           send_mouse_click(hwnd, int(t_col), int(t_row), mw, h, rect)
                           """, "keyboard":"""
                            for char in result["keyboard"]:
                                vk_code = ord(char.upper()) 
                                send_key_press(hwnd, vk_code)                           
                            """, "ESC": """os._exit()"""},},},daemon=True)
        t.start()

        stream_window(target, mw, 15)