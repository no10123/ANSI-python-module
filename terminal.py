import shutil,os
W, H = shutil.get_terminal_size()

def color(name:str="default", m:str="f", bright:bool=False) -> str:
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

# red, yellow, green, cyan, blue, magenta

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


# python leper. 
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
        if isinstance(a, int|float):
            return list(a + (b[i] - a) * t for i in range(len(b))) if is_list else tuple(a + (b[i] - a) * t for i in range(len(b)))   
        elif isinstance(b, int|float):
            return list(a[i] + (b - a[i]) * t for i in range(len(a))) if is_list else tuple(a[i] + (b - a[i]) * t for i in range(len(b)))
        else:
            return list(a[i] + (b[i] - a[i]) * t for i in range(len(min(a,b,key=len)))) if is_list else tuple(a[i] + (b[i] - a[i]) * t for i in range(len(b)))


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

text = rgb(200,200,200) + color(m="b")
STYLEa = {"CLEAR" :["\033[0m"],
         "#":[color("red"),color("yellow"),color("green"),color("cyan"),color("blue"),color("magenta"),text],
         "*":[add["italic"],add["bold"],add["bold"] + add["italic"],None],
         "_":[add["italic"],add["bold"],add["bold"] + add["italic"],None],
         "~":[None,add["strikethrough"],None],
         "=":[None,color("yellow","b"),None],
         "`":[color("red")+rgb(30,30,46,"b"),None,"```",None]}
STYLEr = {"CLEAR" :["\033[0m"],
         "#":[None],
         "*":[remove["italic"],remove["bold"],remove["bold"] + remove["italic"],None],
         "_":[remove["italic"],remove["bold"],remove["bold"] + remove["italic"],None],
         "~":[None,remove["strikethrough"],None],
         "=":[None,text,None],
         "`":[text,None,"```",None]}
STYLER = {"<!--":add["hidden"],
          "-->": remove["hidden"],
          "* ":"• ",
          "- ":"• ",
          "+ ":"• ",
          ">":"│ ",
          "---":"-" * W,}
STYLEm = {"```":color("red")+rgb(30,30,46,"b"),}
mlb = {k:False for k, _ in STYLEm.items()}

usingThemes = True
if usingThemes:
    import themeParser as t
    Theme = t.ThemeEngine()
    TL = Theme.get_available_themes()

def setTheme(TN:str="nord"):
    Theme.get_available_themes()
    Theme.load_theme(TN)
    TRGB = t.ThemeEngine()
    TRGB.load_theme(TN,False,True)
    text = Theme.get("main_bg") + Theme.get("main_fg")
    code = Theme.get("hi_fg")+rgb(lerp(TRGB.get("proc_misc"),TRGB.get("main_bg"),0.9),m="b")
    headings = [rgb(TRGB.get("title")),rgb(TRGB.get("cpu_box")),rgb(lerp(TRGB.get("cpu_box"),TRGB.get("mem_box"),0.5)),rgb(TRGB.get("mem_box")),rgb(lerp(TRGB.get("mem_box"),TRGB.get("net_box"),0.5)),rgb(TRGB.get("net_box")),rgb(lerp(TRGB.get("net_box"),TRGB.get("proc_box"),0.5)),rgb(TRGB.get("proc_box")),text]
    STYLEa = {"CLEAR" :["\033[0m" + Theme.get("main_bg")],
            "#":headings,
            "*":[add["italic"],add["bold"],add["bold"] + add["italic"],None],
            "_":[add["italic"],add["bold"],add["bold"] + add["italic"],None],
            "~":[None,add["strikethrough"],None],
            "=":[None,Theme.get("selected_fg")+Theme.get("selected_bg"),None],
            "`":[code,None,"```",None]}
    STYLEr = {"CLEAR" :["\033[0m" + Theme.get("main_bg")],
            "#":[None],
            "*":[remove["italic"],remove["bold"],remove["bold"] + remove["italic"],None],
            "_":[remove["italic"],remove["bold"],remove["bold"] + remove["italic"],None],
            "~":[None,remove["strikethrough"],None],
            "=":[None,text,None],
            "`":[text,None,"```",None]}
    STYLER = {"<!--":add["hidden"],
            "-->": remove["hidden"],
            "* ":"• ",
            "- ":"• ",
            "+ ":"• ",
            ">":"│ ",
            "---":"-" * W,}
    STYLEm = {"```":code,}
    mlb = {k:False for k, _ in STYLEm.items()}
    return text, STYLEa, STYLEr, STYLER, STYLEm, mlb



IGNORE = ["\\"[0]]

def mdGlow(filename:str="README.md"):
    K = STYLEa.keys()
    styles = []
    out = []
    I = False
    with open(filename, "r") as file:
        for line in file:
            row = text
            line = line.rstrip("\n")
            TT = False
            if line.lstrip().startswith(tuple(k for k in STYLEm.keys())):
                for m in mlb.keys():
                    if line.lstrip().startswith(m):
                        mlb[m] = not mlb[m]
                        if mlb[m]:
                            out.append(STYLEm[m] + line + STYLEa["CLEAR"][0])
                            TT = True
                        else:
                            row += STYLEm[m] + "```" + STYLEa["CLEAR"][0]
                            line = line[len(m):]
                        break
                if TT: continue
            if sum([1 if i else 0 for i in mlb.values()]) > 0:
                S = ""
                for k, v in mlb.items():
                    if v:
                        S += STYLEm[k]
                out.append(S + line + STYLEa["CLEAR"][0])
                continue
            for k, v in STYLER.items():
                line = line.replace(k,v)
            mode = ""
            mult = 0
            styles = []
            for char in line:
                if I:
                    I = False
                    row += char
                    continue
                if mode != "":
                    if char == mode:
                        mult += 1
                    else:
                        state_key = (mode, mult)
                        
                        if state_key in styles:
                            idx = min(mult - 1, len(STYLEr.get(mode, [None])) - 1)
                            RS = STYLEr.get(mode, STYLEr["CLEAR"])[idx]
                            styles.remove(state_key)
                        else:
                            idx = min(mult - 1, len(STYLEa.get(mode, [None])) - 1)
                            RS = STYLEa.get(mode, STYLEa["CLEAR"])[idx]
                            styles.append(state_key)                        
                        if RS is None:
                            row += mode * mult
                        else:
                            row += RS                        
                        if char in K:
                            mode = char
                            mult = 1
                        else:
                            row += char
                            mode = ""
                            mult = 0
                elif char in K:
                    mode = char
                    mult = 1
                elif char in IGNORE:
                    I = True
                else:
                    row += char             
            row += STYLEa["CLEAR"][0]
            out.append(row)
        
    print("\n".join(out))

if __name__ == "__main__":
    if usingThemes:
        for i in TL:
            try:
                text, STYLEa, STYLEr, STYLER, STYLEm, mlb = setTheme(i)
                mdGlow("example.md")
                print(f"theme: {i}")
                i = input("next theme: ")
                if i  in ["q","quit"]: break
            except: pass
    else:
        mdGlow("example.md")