import re

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

def style(line):
    """Apply terminal colors to common Markdown syntax on one line."""
    styles = {
        "heading": color("cyan", bright=True),
        "heading2": color("red", bright=True),
        "heading3": color("yellow", bright=True),
        "heading4": color("green", bright=True),
        "heading5": color("blue", bright=True),
        "heading6": color("magenta", bright=True),
        "bold": add["bold"],
        "italic": add["italic"],
        "code": color("yellow", bright=True),
        "link": color("cyan"),
        "quote": color("green"),
        "list": color("blue"),
        "comment": color("black", bright=True),
        "strike": add["strikethrough"],
        "highlight": color("yellow", m="b"),
    }
    resets = {
        "bold": remove["bold"],
        "italic": remove["italic"],
        "strike": remove["strikethrough"],
        "highlight": color("default", m="b"),
    }

    def wrap(match, style_name, group=0):
        reset = resets.get(style_name, color())
        return styles[style_name] + match.group(group) + reset

    heading_match = re.match(r"^(#{1,6})(?:\s+|$).*", line)
    if heading_match:
        heading_styles = {
            1: "heading", 2: "heading2", 3: "heading3",
            4: "heading4", 5: "heading5", 6: "heading6",
        }
        line = wrap(heading_match, heading_styles[len(heading_match.group(1))])
    elif re.match(r"^\s*(```|~~~)", line):
        print(color("magenta", bright=True) + line + color())
        return
    elif re.match(r"^\s*([-*_])(?:\s*\1){2,}\s*$", line):
        print(color("magenta", bright=True) + line + color())
        return
    elif re.match(r"^\s*(?:<!--|\[\^.*\]:)", line):
        print(color("black", bright=True) + line + color())
        return
    elif re.match(r"^\s*>", line):
        line = styles["quote"] + line + color()
    elif re.match(r"^\s*(?:[-+*]|\d+\.)\s+(?:\[[ xX]\]\s+)?", line):
        line = re.sub(
            r"^(\s*(?:[-+*]|\d+\.)(?:\s+\[[ xX]\])?)",
            lambda match: styles["list"] + match.group(1) + color(),
            line,
        )
    elif re.match(r"^\s*\|", line):
        line = color("cyan") + line + color()

    line = re.sub(r"(?<!\\)(\*\*|__)(.+?)\1", lambda match: wrap(match, "bold", 2), line)
    line = re.sub(r"(?<!\\)(~~)(.+?)\1", lambda match: wrap(match, "strike", 2), line)
    line = re.sub(r"(?<!\\)(==)(.+?)\1", lambda match: wrap(match, "highlight", 2), line)
    line = re.sub(r"(?<![\\*])\*([^*\n]+?)\*(?!\*)", lambda match: wrap(match, "italic", 1), line)
    line = re.sub(r"(?<![\\_])_([^_\n]+?)_(?!\_)", lambda match: wrap(match, "italic", 1), line)
    line = re.sub(r"(`+)(.+?)\1", lambda match: wrap(match, "code", 2), line)
    line = re.sub(
        r"(!?\[[^\]]+\]\([^\)]+\))",
        lambda match: wrap(match, "link", 1),
        line,
    )
    line = re.sub(r"(?<!\\)~([^~\n]+?)~", lambda match: wrap(match, "code", 1), line)
    line = re.sub(r"(?<!\\)\^([^\^\n]+?)\^", lambda match: wrap(match, "code", 1), line)
    print(line)

with open("README.md", "r") as file:
    for line in file:
        style(line.strip())  