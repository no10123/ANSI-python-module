import colorsys, time 
from math import sin, cos

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

def HSVtoRGB(*args) -> tuple[int,int,int]:
    """
        converts to hsv to rgb.
    
        Args:
            H:
                Hue of the color.
            S:
                Saturation of the color.
            V:
                Value of the color
        Returns:
            A rgb tuple
    
        Example:
            >>> HSVtoRGB(100, 1,1)
    
        Notes:
            only really useful for rainbow stuff.
    """
    if len(args) == 3:
        H, S, V = args[0], args[1], args[2]
    else:
        H, S, V = args[0]
    r, g, b = colorsys.hsv_to_rgb(H / 360, S, V)
    return (int(255 * r), int(255 * g), int(255 * b))


def donutDemo():
    RAINBOW = False
    HOLO = False
    hue = 0
    FPS = 60
    print("\033]0;Donut\007", end="")
    
    global running, paused
    running = True

    WIDTH =  30
    HEIGHT = 30

    T = 10
    P = 3

    chars = ".,-~:;=!*#$@"
    chars = list(rgb(255/12 * i, 255/12 * i, 255/12 * i, "b") + " \033[0m" for i in range(12))
    if RAINBOW:
        chars = list(rgb(HSVtoRGB(360/12 * i,1,1),"b") + " \033[0m" for i in range(12))

    A, B = 0,0

    R1 = 10
    R2 = 20
    K2 = 200
    K1 = HEIGHT * K2 * 3 / (8 * (R1 + R2))

    while running:
        time.sleep(1/FPS)
        print(end="\033[H")
        out = [" "] * WIDTH * HEIGHT
        zbuffer = [0] * WIDTH * HEIGHT

        for theta in range(0, 628, T):
            for phi in range(0, 628, P):

                cosA = cos(A)
                sinA = sin(A)
                cosB = cos(B)
                sinB = sin(B)

                costheta = cos(theta)
                sintheta = sin(theta)
                cosphi   = cos(phi)
                sinphi   = sin(phi)

                CX = R2 + R1 * costheta
                CY = R1 * sintheta

                x = CX * (cosB * cosphi + sinA * sinB * sinphi) - CY * cosA * sinB
                y = CX * (sinB * cosphi - sinA * cosB * sinphi) + CY * cosA * cosB
                z = K2 + cosA * CX * sinphi + CY * sinA
                ooz = 1/z

                xp = int(WIDTH / 2 + K1 * ooz * x)
                yp = int(HEIGHT / 2 - K1 * ooz * y)

                position = xp + WIDTH * yp

                L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi)

                if ooz > zbuffer[position]:
                    zbuffer[position] = ooz
                    LI = int(L * 8)
                    out[position] = chars[max(LI, 0)]

        for i in range(HEIGHT):
            for j in range(WIDTH):
                print(end=out[j + WIDTH * i] * 2)
            print()
        
        A += 0.15
        B += 0.035
        if HOLO:
            chars = chars[1:] + chars[:1]

donutDemo()