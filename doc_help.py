import inspect
import re
import textwrap
import os
from typing import Callable, Any, Dict, List
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

def lerp(a:float|tuple|list, b:float|tuple|list, t:float) -> float|list|tuple:
    """
    takes 2 numbers, and returns a number between them at place t

    Args:
        a:
            The starting number.
        b:
            The end number.
        t:
            percent as a decimal, of the new numbers place between a and b.
    Returns:
        Returns a number that is t% between a and b.
    
    Example:
        >>> lerp(0,[10,12,16],0.5) # -> [5,6,8]
    
    Notes:
        mainly used by gradients, also make sure that if both a and b are lists / tuples,
        that they have the same length.  
        also if either a or b is a list the return value is a list,
        if neither is a list and one is a tuple the return value is a tuple.
    """
    is_list = isinstance(a,list) or isinstance(b,list)
    if isinstance(a,float|int) and isinstance(b,float|int):
        return a + (b - a) * t
    else:
        if isinstance(a, int|float) and not isinstance(b,float|int):
            return list(a + (b[i] - a) * t for i in range(len(b))) if is_list else tuple(a + (b[i] - a) * t for i in range(len(b)))   
        elif isinstance(b, int|float) and not isinstance(a,float|int):
            return list(a[i] + (b - a[i]) * t for i in range(len(a))) if is_list else tuple(a[i] + (b - a[i]) * t for i in range(len(b)))
        elif not (isinstance(b,float|int) or isinstance(a,float|int)):
            return list(a[i] + (b[i] - a[i]) * t for i in range(len(min(a,b,key=len)))) if is_list else tuple(a[i] + (b[i] - a[i]) * t for i in range(len(b)))
        else:
            return () # this should never run

def gradient4(TL=(255,0,0),TR=(0,0,255),BL=(0,255,0),BR:tuple[int,int,int]=(255,255,0),w:int=10,h:int=10,matrix=False) -> list:
    """
    a 4 color gradient maker 

    Args:
        TL:
            The top left color as a rgb tuple
        TR:
            The top right color as a rgb tuple
        BL:
            The bottom left color as a rgb tuple
        BR:
            The bottom right color as a rgb tuple
        w:
            width of the gradient
        h:
            the height of the gradient
        matrix:
            returns the list as a 2d array, instead of a 1d list.
            As of currently, it is slower than normal.
    
    Returns:
        a 1d list of the gradient
        if matrix == True:
            it returns a 2d list instead.
            [[TL...TR]...[BL...BR]]

    Example:
        >>> g = gradient4()
        >>> for i in range(10): # (height of the gradient)
        >>>     for j in range(10): # (width of the gradient)
        >>>         print(rgb(g[j + 10 * i],"b") + "  ", end=color(m="b")) # (10 is width)
        >>>     print()
    Example2:
        >>> # yeah im spoiling you with a second example. (but this is one of my favorite functions)
        >>> chars = ".,-~:;=!*#$@"
        >>> g = gradient4(0,4,7,11)
        >>> for i in range(10): # (height of the gradient)
        >>>     for j in range(10): # (width of the gradient)
        >>>         print(chars[round(g[j + 10 * i])] * 2, end="") # (10 is width)
        >>>     print()

    Notes:
        like gradient2(), 
        use rgb to convert it into ansi strings.
        Also you can make the tuples longer or shorter or make them an int|float, for other cases,
        but its kinda complex, if you do try it, make sure A and B have the same length.
    """
    grid = [(0,0,0)] * w * h
    grid[0] = TL
    grid[w - 1] = TR
    grid[w * (h - 1)] = BL
    grid[-1] = BR
    for i in range(w):
        grid[i] = lerp(TL,TR,i/(w-1))
        grid[i + w * (h-1)] = lerp(BL,BR,i/(w-1))
        for j in range(h - 2):
            j += 1
            A, B = grid[i], grid[i + w * (h-1)]
            grid[i + w * j] = lerp(A,B,j/(h-1))
    if matrix:
        m = []
        for i in range(h):
            M = []
            for j in range(w):
                M.append(grid[j + w * i])
            m.append(M)
        return m
    else:
        return grid

def wrap(colors:list, s:str=" ",p:str|tuple[str]|None=None, end:str="\033[0m") -> str:
    """
    wraps a piece of text, with a list of colors.
    
    Args:
        colors:
            a list of colors you want applied to the text, keep
            in mind the colors list is on a modules if the index,
            is greater then len(colors) it will loop.
            Also "" as a color is just default.
        s:
            The text your adding the color too.
        p:
            custom split for colors, 
            typically not needed, but if you
            want specific coloring, it is useful.
        end:
            the reset code used, 
            change if you want the default color to be something
            else.
    
    Returns:
        a printable string
    
    Example:
        >>> # prints the text with a block font and 4 color gradient.
        >>> banner = text2art("HELLO \n WORLD", font="block")
        >>> lines = banner.splitlines()
        >>> w = max(len(line) for line in lines)
        >>> h = len(lines)
        >>> 
        >>> g = gradient4((255, 0, 140),(70, 0, 255),(0, 255, 220),(255, 230, 0),w,h,matrix=True)
        >>> for y, line in enumerate(lines):
        >>>     ansi_colors = [rgb(int(r), int(g_), int(b))for r, g_, b in g[y]]
        >>>     print(wrap(ansi_colors, line))
    
    Notes:
        p is auto defined when None. Also try using the gradient tools,
        as they generate lists that can be used by wrap.
    """
    sp = 0
    S = []
    if isinstance(p,tuple):
        ss = p[0]
    elif p and not isinstance(p,tuple):
        S = s.split(p)
    else:
        ss = []
        if s:
            ss.append(list(s[i] for i in range(len(s))))
        if " " in s:
            ss.append(re.split(r'(?<= )', s))
        if "\n" in s:
            ss.append(re.split(r'(?<=\n)', s))
    if isinstance(ss, list):
        if len(ss) == 1:
            S = ss[0]
        else:
            for item in ss:
                if len(colors) == len(item):
                    S = item
                    break
    else:
        S = s.split("")

    R = ""
    for i in S:
        if i.endswith("\n"):
            R += colors[sp] + i[:-1] + end + "\n"
        else:
            R += colors[sp] + i + end
        sp = (sp + 1) % len(colors)
    return R + end

def Irgb(s:str) -> tuple:
    """
    returns a rgb tuple for a ANSI rgb color.
    
    Args:
        s:
            The string.
    
    Returns:
        a rgb tuple of the ANSI rgb color.
    
    Example:
        >>> print(Irgb(rgb(98,43,21)))
    
    Notes:
        Has no error handling.
    """
    return tuple(int(i) for i in list(s[7:-1].split(";")))

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def clear(n:str="", bg_c:str="") -> str:
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

def pretty_doc(
    func: Callable[..., Any],
    width: int = 70,                   # colors:
    cT: str      = rgb(0, 255, 255),   # Title
    cs: str      = rgb(255, 180, 0),   # section
    cn: str      = rgb(255, 100, 180), # name
    ct: str      = rgb(220, 220, 220), # text
    cb: str|list = rgb(100, 100, 100), # border
    cc: str      = rgb(100, 255, 150), # code
    # -- color_d is how each section is styled off of indentation, and headers is the name of each section --
    color_d:dict = {"Desc": ["ct"],"Args:": ["cn", "ct"],"Returns:": ["ct"],"Example:": ["cc"],"Notes:": ["ct"]},
    headers:list = ["Args:", "Arguments:", "Returns:", "Yields:", "Raises:", "Example:", "Examples:", "Notes:"],
    typed:str|None = "Args:", # this is your argument section, will auto apply types if wanted (if not use None).
    chrome: bool = False
) -> str:
    """
    a helper func that can be used as a stylized help func.

    Args:
        func:
            the function you want to see the doc's of.
        width:
            the width of the box
        cT:
            color of the Title
        cs:
            color of the section Titles
        cn:
            color for name of the function
        cb:
            color of the border
        cc:
            color of code
        color_d:
            color coding based on indentation for each section.
        headers:
            the names of each section
        typed:
            your argument section, will auto apply types if wanted (if not use None).

    Returns:
        A printable card
    
    Example:
        >>> print(pretty_doc(pretty_doc, 120))

    Notes:
        Use a list in the colors for cool text, uses wrap.
        """
    doc = inspect.getdoc(func)
    name = getattr(func, "__name__", type(func).__name__)

    if not doc:
        doc = "*No docstring provided for this function.*"

    try:
        sig = inspect.signature(func)
        types = {name: (param.annotation if param.annotation != inspect.Parameter.empty else None) for name, param in sig.parameters.items()}
    except (ValueError, TypeError):
        types = {}
    sg = str(sig)
    R = "\033[0m"
    LD = doc.expandtabs(4).split("\n")
    COLORS = {"cT":cT,"cs":cs,"cn":cn,"ct":ct,"cb":cb,"cc":cc}
    color_d = {k: [COLORS.get(c, c) for c in v] for k, v in color_d.items()}
    data = {"Desc": []}
    mode = "Desc"
    for d in LD:
        if d.strip() in headers:
            mode = d.strip()
            if mode not in data:
                data[mode] = []
        else:
            data[mode].append(d)
    total_rows = 3
    for m, lines in data.items():
        if m != "Desc":
            total_rows += 1
        total_rows += len(lines)
    CB = cb[0] if isinstance(cb, list) else cb
    if chrome:
        raw_grad = gradient4(
            Irgb(cT),
            Irgb(cc),
            Irgb(cn),
            Irgb(cs),
            width, max(2,total_rows), matrix=True
        )
        cb = [[rgb(*color) for color in i] for i in raw_grad]    
    cbl = [row[0] for row in cb] if isinstance(cb, list) else cb
    cbr = [row[-1] for row in cb] if isinstance(cb, list) else cb
    cbi = 3

    out = []
    # "╭─╮╰╯│"
    O = []
    for mode, lines in data.items():
        Row = ""
        if mode != "Desc":
            Row += (cbl[cbi % len(cbl)] if isinstance(cbl,list) else cbl) + "│ " + cs + "-- " + mode + " " + "-" * max(0, width - 8 - len(mode)) + (cbr[cbi % len(cbr)] if isinstance(cbr,list) else cbr) + " │\n"
            cbi += 1            
        cl = color_d.get(mode, [ct])
        
        for j in lines:
            j = j[4:] if j [:4] == "    " else j
            I = sum(1 for i in range(0, len(j), 4) if j[i:i+4] == "    ")
            if mode == typed and I == 0:
                arg_name = j.split(":")[0].strip()
                if arg_name in types and types[arg_name]:
                    type_str = f" [{types[arg_name]}]"
                    j = j.replace(f"{arg_name}:", f"{arg_name}{type_str}:", 1)
            Row += (cbl[cbi % len(cbl)] if isinstance(cbl,list) else cbl) + "│ " + cl[min(I, len(cl) - 1)] + j + R + " " * max(0, width - 4 - len(j)) + (cbr[cbi % len(cbr)] if isinstance(cbr,list) else cbr) + " │\n"
            cbi += 1
        if Row:
            O.append(Row[:-1])
    if isinstance(cb, list):
        out.append(wrap(cb[0], "╭" + "─" * (width - 2) + "╮"))
    else:
        out.append(cb + "╭" + "─" * (width - 2) + "╮")
    out.append((cbl[0] if isinstance(cbl,list) else cbl) + "│ " + cT + name + R + " " * (width - 4 - len(name))  + (cbr[0] if isinstance(cbr,list) else cbr) + " │")
    out.append((cbl[1] if isinstance(cbl,list) else cbl) + "│ " + cc + sg   + R + " " * (width - 4 - len(sg))    + (cbr[1] if isinstance(cbr,list) else cbr) + " │")
    out.append((cbl[2] if isinstance(cbl,list) else cbl) + "│ " +                 " " * (width - 4)              + (cbr[2] if isinstance(cbr,list) else cbr) + " │")
    for i in O: out.append(i)
    pal = "".join(c + "██\033[0m" for c in [cT,cs,cn,ct,CB,cc])
    BL = "╰" + "─" * max(0, width - (2 * 6) - 9) + " [ "
    BR = " ] ─╯"
    if isinstance(cb, list):
        out.append(wrap(cb[-1][:len(BL)], BL) + pal + wrap(cb[-1][-len(BR):], BR))
    else:
        out.append(cb + BL + pal + cb + BR)
    out.append(R)
    return "\n".join(out)

if __name__ == "__main__":
    print(pretty_doc(rgb, 120, chrome=True))
input()

functions = None

def main_menu(
    width: int = 120,                  # colors:
    cT: str|list = rgb(0, 255, 255),   # Title
    cs: str|list = rgb(255, 180, 0),   # section
    cn: str|list = rgb(255, 100, 180), # name
    ct: str|list = rgb(220, 220, 220), # text
    cb: str|list = rgb(100, 100, 100), # border
    cc: str|list = rgb(100, 255, 150), # code
    chrome: bool = False
    ):
    """
    a helper func that prints all funcs in the current file.

    Args:
        width:
            the width of the box
        cT:
            color of the Title
        cs:
            color of the section Titles
        cn:
            color for name of the function
        cb:
            color of the border
        cc:
            color of code
        chrome:
            if border is rainbow

    Returns:
        A printable menu
    
    Example:
        >>> print(main_menu())

    Notes:
        Use a list in the colors for cool text, uses wrap.
    """
    global functions
    if functions == None:
        functions = []        
        current_module = globals().get("__name__", "__main__")                
        for name, obj in globals().items():
            if inspect.isfunction(obj) and getattr(obj, "__module__", "") == current_module:    
                functions.append(name)
        functions.sort()
    
    if chrome:
        raw_grad = gradient4(
            Irgb(cT),
            Irgb(cc),
            Irgb(cn),
            Irgb(cs),
            width, max(2,total_rows), matrix=True
        )
        cb = [[rgb(*color) for color in i] for i in raw_grad]    
    cbl = [row[0] for row in cb] if isinstance(cb, list) else cb
    cbr = [row[-1] for row in cb] if isinstance(cb, list) else cb
    cbi = 3

    out = []
    # "╭─╮╰╯│"
    O = []
    n = 0
    R = "\033[0m"
    for f in functions:
        Row = ""
        
        Row += (cbl[cbi % len(cbl)] if isinstance(cbl,list) else cbl) + "│ " + cl[min(I, len(cl) - 1)] + j + R + " " * max(0, width - 4 - len(j)) + (cbr[cbi % len(cbr)] if isinstance(cbr,list) else cbr) + " │\n"
        cbi += 1
        if n == 3:
            O.append(Row[:-1])
            n = 0
        else:
            n += 1
    if isinstance(cb, list):
        out.append(wrap(cb[0], "╭" + "─" * (width - 2) + "╮"))
    else:
        out.append(cb + "╭" + "─" * (width - 2) + "╮")
    out.append((cbl[0] if isinstance(cbl,list) else cbl) + "│ " + cT + name + R + " " * (width - 4 - len(name))  + (cbr[0] if isinstance(cbr,list) else cbr) + " │")
    out.append((cbl[1] if isinstance(cbl,list) else cbl) + "│ " + cc + sg   + R + " " * (width - 4 - len(sg))    + (cbr[1] if isinstance(cbr,list) else cbr) + " │")
    out.append((cbl[2] if isinstance(cbl,list) else cbl) + "│ " +                 " " * (width - 4)              + (cbr[2] if isinstance(cbr,list) else cbr) + " │")
    for i in O: out.append(i)
    pal = "".join(c + "██\033[0m" for c in [cT,cs,cn,ct,CB,cc])
    BL = "╰" + "─" * max(0, width - (2 * 6) - 9) + " [ "
    BR = " ] ─╯"
    if isinstance(cb, list):
        out.append(wrap(cb[-1][:len(BL)], BL) + pal + wrap(cb[-1][-len(BR):], BR))
    else:
        out.append(cb + BL + pal + cb + BR)
    out.append(R)
    return "\n".join(out)

history = []
HI = -2
if __name__ == "__main__":
    
    current_view = ".menu"
    
    while True:
        clear()        
        b_col = rgb(100, 100, 100)
        txt_col = rgb(220, 220, 220)
        print(f"{b_col}╭{'─' * 118}╮\033[0m")
        msgs = [
            "  Type a function name to see the help card for that func.",
            "  Type '.menu' to see all functions, '.back' to go to the previous func",
            " or '.quit' to exit."
        ]
        for m in msgs:
            pad = 118 - len(m)
            print(f"{b_col}│{txt_col}{m}{' ' * pad}{b_col}│\033[0m")
        print(f"{b_col}╰{'─' * 118}╯\033[0m\n")
        BACK = False
        if current_view in [".back",".b"]:
            if history == [] or -1 * HI > len(history):
                print(f"{rgb(255, 100, 100)}[!] Error: no previous menu.\033[0m\n")
            current_view = history[HI]
            BACK = True
        if current_view in [".menu",".m"]:
            print(main_menu(120))
            HI = HI - 1 if BACK else -2
            if not BACK: history.append(current_view)
        elif current_view == ".h":
            print(history)
        else:
            func_obj = globals().get(current_view)
            if callable(func_obj):
                print(pretty_doc(func_obj, 120))
                HI = HI - 1 if BACK else -2
                if not BACK: history.append(current_view)
            else:
                print(f"{rgb(255, 100, 100)}[!] Error: No valid func found named '{current_view}'\033[0m\n")
        
        user_input = input("\n>>> ").strip()
        
        if user_input.lower() in [".quit", ".exit", ".q"]:
            break
        elif user_input:
            current_view = user_input