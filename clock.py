import os
import sys
import time
from datetime import datetime

if os.name == 'nt':
    os.system('cls')

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




def BIG_CLOCK(
        cd = "\033[1;36m",
        cc = "\033[1;35m",
        cD  = "\033[1;32m",):
    print(end=c.invis())
    RESET = "\033[0m"
    
    DW = 12
    AW = 30
    FONT = ["""
    █████   
  ███░░░███ 
 ███    ░░███
░███    ░███
░███    ░███
░░███   ███ 
 ░░░█████░  
    ░░░░░░   ""","""
████ 
░░███ 
 ░███ 
 ░███ 
 ░███ 
 ░███ 
 █████
░░░░░ ""","""
  ████████ 
 ███░░░░███
░░░    ░███
   ███████ 
 ███░░░░  
 ███    █
░██████████
░░░░░░░░░░ ""","""
  ████████ 
 ███░░░░███
░░░    ░███
   ██████░ 
  ░░░░░░███
 ███    ░███
░░████████ 
 ░░░░░░░░  """, """
 █████ █████ 
░░███ ░░███  
 ░███  ░███ █
 ░███████████
 ░░░░░░░███░█
       ░███░ 
       █████ 
      ░░░░░  """, """
 ██████████
░███░░░░░░█
░███    ░ 
░█████████ 
░░░░░░░░███
 ███    ░███
░░████████ 
 ░░░░░░░░  """, """
  ████████ 
 ███░░░░███
░███   ░░░ 
░█████████ 
░███░░░░███
░███   ░███
░░████████ 
 ░░░░░░░░  """, """
 ██████████
░███░░░░███
░░░    ███ 
     ███   
    ███    
   ███     
  ███      
 ░░░       """, """
  ████████  
 ███░░░░███ 
░███   ░███ 
░░████████  
 ███░░░░███ 
░███   ░███ 
░░████████  
 ░░░░░░░░   """, """
  ████████ 
 ███░░░░███
░███   ░███
░░█████████
 ░░░░░░░███
 ███   ░███
░░████████ 
 ░░░░░░░░  """, """
   
   
 ██
░░ 
   
   
 ██
░░ 
   
   
""", """
   █████████   ██████   ██████
  ███░░░░░███ ░░██████ ██████ 
 ░███    ░███  ░███░█████░███ 
 ░███████████  ░███░░███ ░███ 
 ░███░░░░░███  ░███ ░░░  ░███ 
 ░███    ░███  ░███      ░███ 
 █████   █████ █████     █████
░░░░░   ░░░░░ ░░░░░     ░░░░░ ""","""
 ███████████  ██████   ██████
░░███░░░░░███░░██████ ██████ 
 ░███    ░███ ░███░█████░███ 
 ░██████████  ░███░░███ ░███ 
 ░███░░░░░░   ░███ ░░░  ░███ 
 ░███         ░███      ░███ 
 █████        █████     █████
░░░░░        ░░░░░     ░░░░░ """]

    
    try:
        while True:
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S %p")
            date = now.strftime("%A, %B %d, %Y")
            tp = time_str.split(" ")
            
            output = ["\033[H\033[2J\033[3J"]
            digits = []
            
            for char in tp[0]:
                if char == ":":
                    digits.append((FONT[10].strip('\n').split('\n'), cc, DW))
                else:
                    digits.append((FONT[int(char)].strip('\n').split('\n'), cd, DW))
            
            if tp[1] == "AM":
                digits.append((FONT[11].strip('\n').split('\n'), cd, AW))
            else:
                digits.append((FONT[12].strip('\n').split('\n'), cd, AW))
                
            max_lines = max(len(d[0]) for d in digits)
            for line_idx in range(max_lines):
                ls = "   "
                for d_arr, color, width in digits:
                    if line_idx < len(d_arr):
                        ls += color + d_arr[line_idx].ljust(width) + RESET + " "
                    else:
                        ls += " " * (width + 1)
                output.append(ls + "\n")
                
            output.append(f"\n   {cD}{date}{RESET}\n")
            
            print("".join(output))
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(c.vis() + RESET + "\n")
        print("Clock stopped.")
        sys.stdout.flush()

if __name__ == "__main__":
    BIG_CLOCK()