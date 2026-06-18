import sys
import os

bg_color = "\033[49m"

def clear(n=""):
    print(end=bg_color)
    os.system("cls")
    return n    

def leadZero (i, d):
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

def rgb(r,g,b,m):
    return f"\033[38;2;{r};{g};{b}m" if m.lower() == "f" else "\033[48;2;{r};{g};{b}m" if m.lower() == "b" else ""

class cursor:
    def invis():
        print("\033[?25l")
    def vis():
        print("\033[?25h")
    def up(n=1):
        print(f"\033[{n}A")
    def down(n=1):
        print(f"\033[{n}B")
    def left(n=1):
        print(f"\033[{n}C")
    def right(n=1):
        print(f"\033[{n}D")
    def nextLine(n=1):
        print(f"\033[{n}E")
    def prevLine(n=1):
        print(f"\033[{n}F")
    def colum(n):
        print(f"\033[{n}G")
    def setPos(x="",y=""):
        print(f"\033[{y};{x}H")
    def savePos():
        print("\033[s")
    def loadPos():
        print("\033[u")
    def saveAll():
        print("\0337")
    def loadAll():
        print("\0338")

def main():
    global bg_color
    bg_color = "\033[42m"
    clear()
    print("i like green")

if __name__ == "__main__":
    main()
    clear(input("clear: "))