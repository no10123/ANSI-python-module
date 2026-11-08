# ANSI based python module
A Python module focused on creating better TUIs within the terminal
is NOT cross-terminal; WINDOWS ONLY!

> Why Windows only:
> This project is Windows-only, mainly because it's built so people can build better tui's for Windows, since there are already many Linux TUI tools/helpers but not much for Windows. Due to this, I have recorded a video of all the Demos which show off the features so you can see it working on any OS. If you have a non-Windows OS but still want to try to  install it, you can; however, you will only be able to run some of the single-file demos, and it might crash, and I cannot guarantee that anything will work on these OS's, and I'm perfectly fine if you just watch the YT video. I also wanted a toolset with lots of Demos and examples and documentation so you can easily see how you can use tools. 

yt demo: https://www.youtube.com/watch?v=CNtCzBxj1EU 

> NOTE: first and foremost, if you want to actually install and test the project, read the entire README; it will fully explain everything, all of the features, how to properly install, and how to test it. The README assumes you are using Windows, but it should be the same for Linux and Mac; however, I cannot guarantee that the same process will work for those OS's. Also some terminals do not have full support for all ANSI escape codes so please consider that while rating, also for the best experience please make sure that your terminal is in full screen. Also, all of the commands are for the Windows PowerShell terminal, which should be the default, but if not, please make sure that is the terminal that you use for the commands given. Also, some of the commands will be blocked by VS Code, so just know that what works can vary a lot.

> If you need help or get stuck installing it, paste the whole README into an AI and ask it to help you install it or help you with whatever step you might be on, but the README should be thorough enough so that you don't need to do this. 

## How to install:
1. Install Python (if you don't have it already) from https://www.python.org/downloads/. If you have any trouble installing it, watch this video:  https://www.youtube.com/watch?v=H_4wrR3wWM8 <br> then pick your method of installing and follow the steps; you will only need to do one of the methods. (btw both methods are pretty similar, but I wanted it to be easy to install/use.)

-- install via pip/PyPI --
2. Create a new folder and open it.
3. Then open this folder in VS Code, or you can open your terminal in this location (for the terminal, you can also open it normally and cd to the folder)
4. If you opened the folder in VS Code, open a new terminal in it. (If needed, make sure to trust the folder)
5. Now you can run the commands. (Just paste it into the terminal and press Enter) (Keep in mind I use the keyword Python; based on how you installed it, you might have to use `py` or `python3` instead of python when running certain commands.) (Also, a reminder: these commands are for Windows, so you might have to run a different command to get the same results if you are on a different OS.) (And some commands can take a while to run, so just be patient)
6. Run `python -m venv .venv`
7. Run `.venv\Scripts\Activate.ps1`
8. Run `python -m pip install --upgrade pip --no-cache-dir`
9. Run `python -m pip install colorful-swiss`
10. Once it is done, create a new file named `main.py` in the folder (make sure it is adjacent to the .venv folder and not in the .venv folder).  (It doesn't have to be named this, but I will use this name in future commands).
11. -- not finished --

-- install via zip --
2. Download the zip
3. Extract the zip
4. Open the new extracted folder (it might be nested, so make sure you can see a README.md file).
5. Then open this folder in VS Code, or you can open your terminal in this location (for the terminal, you can also open it normally and cd to the folder)
6. If you opened the folder in VS Code, make sure you can see the README.md file at the base level of the file tab in the sidebar. Then open a new terminal and run `ls` and make sure you can see the files (like README.md). (If needed, make sure to trust the folder)
7. Now you can run the commands. (Keep in mind I use the keyword Python; based on how you installed it, you might have to use `py` or `python3` instead of python when running certain commands)
8. run `python -m venv .venv`
9. Run `.venv\Scripts\Activate.ps1`
10. Run `python -m pip install --upgrade pip`
11. Run `pip install -r requirements.txt`
12. Now you can run `python file.py` replacing file.py with the name of one of the Python files. 
13. For example, run `python main.py`

## Files and Folders

-- folders --
.vscode and __pycache__ - are extra folders which are not needed. <br>
downloads - a folder with a GIF file and a couple of images, videos, and audio files that can be used to test the displays.py file.<br>
themes - a copy of btop4win's  themes folder and is used by themeParser.py to create color palettes for tui's. <br>
wallpapers - a folder of images generated by spotlight.py which grabs the window spotlight files in an easily accessible place; these can also be used to test displays.py. btw. c.jfif is an extra img and not a spotlight img <br>
-- files --
DataFetcher.py - a file that interacts with the  windows api to grab hardware data, which can be used to create terminal applications that can easily use the device's information. <br>
README.md - this file / the readme for the project, which gives you all the info about it and how to use it. <br>
clock.py - a simple single-file demo which uses the cursor class and shows how you can make simple applications that have color. <br>
debug.log - a file which can be used to  log events which you can tail in the terminal to see log events while a program is running. <br>
displays.py - a helper file which is used to render GIF's, videos, and audio. And images in multiple formats; for example, you can show an image using Kitty protocol, sixel, ASCII grayscale, or ANSI ASCII. Honestly, one of the more impressive tools. <br>
donut.py - a single-file demo of how cool animations can be made with the color tools like rgb, which shows a spinning grayscale donut/torus. It is also in module.py separately. <br>
example.md - a Markdown file used to test and show off terminal.py and how it renders different Markdown effects. <br>
flipper.py - a separate file similar to DataFetcher.py, which interacts with the windows api to see ports and connected devices and uses a Flipper Zero CLI as an example for sending data through ports with this tool. <br>
module.py - arguably the main and biggest file; due to its size, I have listed its features in the section below labeled features. <br>
module.py.bak - a backup file of module.py. Probably used by PyPI. <br>
requirements.txt - a text file of all other required PyPI modules needed to run properly. <br> 
spotlight.py - a file that puts Windows Spotlight images in a folder (default is the wallpapers folder). This allows you to easily access these images for bg's or other uses. <br>
themeParser.py - creates color palettes for tui's using the themes folder.

Features (module.py)
---
- COLOR STUFF:
- rgb() with fg/bg and custom ranges through Max.
- color() - base 8 color set fg/bg with bright variants.
- color256() - 256 color palette codes
- graphics class of dictionaries for adding and removing codes (bold, dim, italic, blink, reverse, hidden, strikethrough)
- setMode() - screen mode
- color converters - HSVtoRGB, HEXtoRGB, CMYKtoRGM, Irgb (ANSI to RGB)
- catpuccin_mocha_rgb - catpuccin color palette in RGB.
- Cursor stuff, and screen stuff:
- cursor class - show/hide, move up/down/left/right, next/prev line, set column, set pos, get pos query, save/load pos, save/load all attributes.
- screen/line classes - erase codes (to end/to start/all/saved) and alt-screen save/load.
- place(x, y, msg) - prints text at a custom position with optional clear screen, save/restore cursor, and clear line.
- renameTerminal() - renames the terminal's title.
- chars dict - control characters like BEL, HT, ESC, etc.
- 
- Console Inspection:
- get_cursor_position() - returns the cursor pos X/Y.
- get_char_at_cursor() / get_char_at(x, y) - reads charer at that position of the console buffer
- get_word() - reads words of the console buffer
- get_cell_color_at() / attr_to_ansi() reads a cell's fg/bg attributes and converts them to ANSI or RGB.
- 
- Text Rendering tools:
- bd() - dynamic box drawing tool (corners, joins, multi-line paths, lengths, and color)
- ps() - shaded block drawing characters for simple gradients.
- rainbowify() - helps make rainbow colored text for fg/bg/both
- wrap() - applies a list of colors cyclically to (characters, words, or lines)/strings (works well with gradients)
- load_bar() - animated rainbow progress bar
- BIG_CLOCK() - large ANSI clock demo with AM/PM and date.
- divider(), leadZero, loop_, iprint - small utilities / helper functions.
- Gradients and Interpolation (uses data, not colors, so can make more custom gradients):
- lerp() - interpolates numbers, lists, or tuples.
- gradient2() - creates a linear gradient between 2 values.
- gradient4() - four-color bilinear gradient, flat or matrix output.
- 
- Graphing:
- cpu_graph() - history-based bar graph with precision, single color, or per row color list.
- clear_graph_area() - clears out a rectangular area
- cava_graph() - audio visualizer spectrum bars. (based on cava)
- audio_listener() - audio capturer with FTT, Hanning window, and smoothing.
- Canvas Class:
- per-cell char and color buffers,
- set_pixel, line, rect, circle, draw (2d list to color map)
- doubleX mode for 2-cell-wide square pixels.
- uses a renderer for fast output.
- 
- Better Input system:
- RawTerminal - context manager for raw mode.
- finput() - unified input function - supports:
- a. keyboard (max length, auto-submit, hidden input, custom enter/backspace/tab handling.)
- b. Mouse (clicks and scrolling),
- c. ESC key, Controller inputs (buttons, D-pad, and sticks with deadzones).
- d. custom_out hooks via @f_out which can exec code per input allowing for easy input threading.
- poll_controller() background thread reading gamepad inputs.
- get_char() / char_available() non blocking key  reading.
- floop() - loops any function in optionally raw mode to make it easier to thread functions.
- typed_str() - parses typed values (int, float, bool, list: int, tuple: str, etc.) from strings
- 
- Interactive documentation repl (doc_cmd) (has a couple of mini tools in it):
- a. .menu, .back, id/name, history, .debug - navigation commands
- b. stylized help cards made through pretty_doc, which has color-coded sections, type annotations, warped text, and optional chrome borders.
- c. main_menu() - multi-column function index, a-z sections, and docstring-aware color-coding.
- d. .run / .copy - execute or copy a docstring example block, and print return values.
- e. .call - calls a function with typed args from prompt.
- f. .f / .fm - allows you to favorite functions.
- g. .deps - view dependencies via AST (local, imported, builtin, unresolved calls).
- h. .form - interactive form that builds a docstring and applies it in memory, copies it, and optionally writes it to the source file.
- i. .cd / .ls / .pwd - move through the file system.
- j. .view - see images via kitty/sixel/ascii/gray, and markdown via mdGlow (mdGlow is the terminal.py tool).
- k. .color / .theme / .rgb / .chrome - allows you to change the theme colors to match your vibe.
- l. --a / --h / --A - flags that allow you to stop screen clearing, the help msg, or both.
- m. DOC_STYLE - allows for custom docstring types and formats.
- n. parse_doc, get_dependencies, getFuncs, _write_docstring_to_source, _build_docstring_body - helpers
- 
- Media tools:
- fetch_yt_audio() / fetch_yt_video() - downloads yt videos via yt-dlp (MP3/MP4)
- playFile - pygame playback with  pause support.
- mediaControl class - thread safe pause / seek state.
- reset_audio()
- video, k_img,loadFile, stream_window - video/img rendering. (through the displays.py file)
- 
- Hardware tools:
- lsDevices() - shows all HID devices and copies the list to the clipboard.
- listen() - reads raw HID reports.
- copy() - copies to clipboard through clip.exe
- 
- BIG DEMO (btopPy()):
- Note: this demo will probably (like a 1% chance it actually works) not work on many devices due to sizing issues. (please see the yt video for proof), This is because it is not a product and instead a demo used to show off what you can do with the tool, putting most of the tools into one big showcase, and is not intended for public use. But here are the features it has / shows off *[1]:
- a. CPU graph, per-core bars, load averages, CPU name/GHz
- b. Memory and page-file stats, per-disk usage with HDD/SSD detection (through a background thread).
- c. cava panel
- d. Matrix rain panel.
- e. Adjustable refresh rate (-/+)
- f. Theme cycling (k/l)
- g. Controller shortcuts.
- 
- Theme tools (there's more in themeParser.py):
- ThemeEngine -uses, loads, and builds palettes from .theme files in the themes folder.
- themeDemo() - preview table for a theme
- themeselect() -  arrow key theme viewer with favorites system.
- 
- Demos + Games (keep in mind not product just shows off product) (also most are in the yt vid):
- rhythmGame - 4-lane (d/f/j/k) rhythm game with scoring system.
- aimGameDemo - mouse click game with cps stats.
- donutDemo - a spinning donut/torus in grayscale (same as donut.py)
- gradientDemo - animated 4-color gradient. Looks really cool.
- clock() - simple clock rendered through canvas.
- clickDemo, clockDemo, arrowsDemo, controllerDemo - input demos (for controllerDemo, make sure your controller is plugged in before running the file with the Demo.)
- canvasDemo, randDemo, wrapDemo, tableDemo, Demo256, fDemo - rendering/ANSI demos
- musicDemo, ytDemo, videoDemo, slideshowDemo, mirrorDemo - media demos.

Example

>>> -- unfinished --

Extended Notes:
[1] - the reason I chose to clone btop was due to me liking it looking cool (I personally just use it cause it looks cool, not for its functionality), which is why I removed the network graph and had a cava and Matrix rain panel. It was also too hard to make it work on any size terminal, and all I wanted it to be was a big showcase of what it can do, as the final product is not the demos, but the tools that the demos use (I just have demos so people can easily see how the tools can be used). 

credits:

built by me

a Music file is by <a href="https://pixabay.com/users/sigmamusicart-36860929/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=525840">Mikhail Smusev</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=525840">Pixabay</a>

used [ANSI Escape Sequences](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797) a lot (ALSO is main source)
btop4win - for the themes folder.

built for stardance

