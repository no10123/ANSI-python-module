# the start of everything
from buffer import *
from DataFetcher import *
from displays import *
from flipper import *
from input import *
from spotlight import *
from style import *
from terminal import *
from themeParser import *
from utils import *
from module import *
"""
/module
├── __init__.py       # main file
├── terminal.py       # RawTerminal, cursor, screen, line, clear()
├── buffer.py         # Win32 ctypes: get_char_at, get_word, get_cursor_position
├── style.py          # color(), rgb(), color256(), attr_to_ansi, graphics dicts
├── draw.py           # bd() (box drawing), divider(), shaded dict
├── utils.py          # log(), leadZero(), toggle_item()
└── input.py          # Mouse sequence toggles, gamepad logic (from your inputs import)
"""