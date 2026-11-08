# colorful-swiss
A Python module focused on creating more colorful and interactive TUIs within the terminal

![alt text](image.png)

easy install:

Requires Windows 10/11 and python version 3.10+, and a fullscreen terminal for best results.

```powershell
pip install colorful-swiss
colorful-swiss
```
The second command will open up doc_cmd a interactive docstring viewer. Type a functions name or id to see what it does or .? to see all of the functions / features of this demo. 

The main purpose of this project is to be used as a library / tool: 

you can create a new py file with the below code to test it out: 

```
from colorful_swiss import rgb, rainbowify

print(rgb(255, 100, 0) + "orange text" + "\033[0m")
print(rainbowify("super cool rainbow text"))
```

## Features

[full list](https://github.com/no10123/ANSI-python-module/blob/main/features.md)
 
- colors - 8 base colors, the 256 color and color based helpers, HSV/HEX/CMYK conversions, gradients
- a cursor class, and canvas class, and you can read characters and colors off the terminal buffer.
- finput - keyboard inputs, mouse, esc key, arrows, gamepad controller (w/ deadzones)
- doc_cmd - a docstring based repl with stylized doc cards, and other tools
- img, video, GIF, audio rendering - img can be shown via kitty,sixel,colored ascii, and normal ascii

## Demos

the tools are the product but the demos show off the tools, for ex (same format): 
```powershell
python -c "from colorful_swiss import donutDemo; donutDemo()"

python -c "from colorful_swiss import btopPy; btopPy()"

python -c "from colorful_swiss import gradientDemo; gradientDemo()"
```
 
- Esc quits donutDemo, rhythmGame, and btopPy.
- q quits clickDemo and controllerDemo.
- Tab quits arrowsDemo.
- gradientDemo ends itself after its 10-second default.

- Demo - what it does
1. `donutDemo`    - spinning donut using `rgb()` and shading
2. `gradientDemo` - animated gradient
3. `rhythmGame`   - a mini game that shows off finput
4. `btopPy`       - a btop inspired dashboard that looks cool
5. `clickDemo`, `arrowsDemo`, `controllerDemo` - mouse, arrow, and gamepad input, so just showing off finput.

`btopPy` is made for larger terminals (170x40 or bigger) and has builtin warning. Some terminals don't support every escape code, and Kitty/Sixel image output needs a terminal that supports those protocols. VS Code's integrated terminal blocks some of the demos, so please use Windows Powershell. Also before running `controllerDemo` make sure to plug in your controller.
 
## How it works
 
finput - reads incoming input bytes and adds custom functions, and uses SGR for mouse.

doc_cmd - uses AST for many things and reads the docstring attribute of functions, and uses globals to find said functions.

why btop clone - mainly cause it does good job of showing off every tool in one demo, and looks cool, since I mainly wanted it to look cool I dropped the proc area and network graph and replaced it with a python remake of cava I did and a Matrix rain effect.
 
## Why is it Windows only
 
I mainly wanted a Windows library, cause guess what I use windows, but also because Linux has many Tui helpers (due to a lot of linux being in the terminal), while windows doesn't have many. This is also due to the code having to talk to the windows api to get hardware info to make it easier for people to make cool projects with this module.

## project files
```
src/colorful_swiss/
 module.py           main module (colors, cursor, input, canvas, docs browser, demos)
 DataFetcher.py      Windows api and gets hardware info
 displays.py         renders image, GIF, video, and plays audio
 terminal.py         A Markdown renderer
 themeParser.py      theme loader
 spotlight.py        gets Windows Spotlight images
 flipper.py          A Port Demo through Flipper Zero
 clock.py, donut.py  single-file demos
 themes/             Btop's theme folder
```

## Built with

Python, `ctypes` and `pywin32` for the Windows console and hardware APIs, NumPy for the audio FFT, Pillow and OpenCV for image and video rendering, pygame for audio playback, yt-dlp for downloads.

## Credits
 
- ANSI reference: [fnky's gist](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797)
- Themes are from [btop4win](https://github.com/aristocratos/btop4win)
- Music by [Mikhail Smusev](https://pixabay.com/users/sigmamusicart-36860929/) from [Pixabay](https://pixabay.com/)
Built for Stardance.