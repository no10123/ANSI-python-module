# Full list of all features and stuff included in the package:
everything that's included. 

## Demos:
name - description - how to quit (auto = can't quit until finished)
rhythmGame - a simple rhythm game with coloring and d/f/j/k inputs - esc

rinpDemo - shows how you can get full words from the terminal buffer - enter

wrapDemo - shows off the warp function - auto

tableDemo - the first Demo, and is a table for the ANSI escape codes (kinda a tool of sorts.) - auto

Demo256 - a basic demo of the color256 function - auto

clickDemo - a cool clicking demo (sometimes right click will overide with paste) - q

clockDemo - similar to click demo except with a active clock so custom positioned animations - q

controllerDemo - shows of controller inputs (make sure your controller is plugged in before running) - q

canvasDemo - shows off the canvas - auto 

randDemo - random colors to show how you could make pixel art - auto

arrowsDemo - allows you to use arrows and clicks and shows off how you can add custom uses for the tab key - tab

devDashboard - a loop that exec's your input, usefull for running demos one after another - quit

btopPy - a python btop clone, shows off a lot of the features in one demo - a lot of things (click)

themeDemo(theme) - shows off the color palette of a theme in the themes folder - auto

themeselect - a theme selector, where you can use arrow keys, (left/right - change themes, up - favroite, down - quit and see favorites.) - down

fDemo - shows compatibility for different ANSI features in a table format - auto

rDemo - prints links to recourses I used - auto

donutDemo - a spinning torus that is shaded in grayscale - esc

gradientDemo - shows a cool animated gradient for a set duration - auto

> Note: some of the demos also show up in the Features list, they will typically just have extra info about what exactly they do.



## Files and Folders

-- folders --


themes - a copy of btop4win's  themes folder and is used by themeParser.py to create color palettes for tui's. 

-- files (in src/colorful_swiss) --


DataFetcher.py - a file that interacts with the  windows api to grab hardware data, which can be used to create terminal applications that can easily use the device's information. 

clock.py - a simple single-file demo which uses the cursor class and shows how you can make simple applications that have color. 

displays.py - a helper file which is used to render GIF's, videos, and audio. And images in multiple formats; for example, you can show an image using Kitty protocol, sixel, ASCII grayscale, or ANSI ASCII. Honestly, one of the more impressive tools. 

donut.py - a single-file demo of how cool animations can be made with the color tools like rgb, which shows a spinning grayscale donut/torus. It is also in module.py separately. 

example.md - a Markdown file used to test and show off terminal.py and how it renders different Markdown effects. 

flipper.py - a separate file similar to DataFetcher.py, which interacts with the windows api to see ports and connected devices and uses a Flipper Zero CLI as an example for sending data through ports with this tool. 

module.py - arguably the main and biggest file; due to its size, I have listed its features in the section below labeled features. 

spotlight.py - a file that puts Windows Spotlight images in a folder (default is the wallpapers folder). This allows you to easily access these images for bg's or other uses. 

themeParser.py - creates color palettes for tui's using the themes folder.

Features (module.py)
---
### COLOR STUFF: 

- rgb() with fg/bg and custom ranges through Max. 

- color() - base 8 color set fg/bg with bright variants. 

- color256() - 256 color palette codes 

- graphics class of dictionaries for adding and removing codes (bold, dim, italic, blink, reverse, hidden, strikethrough) 

- setMode() - screen mode 

- color converters - HSVtoRGB, HEXtoRGB, CMYKtoRGB, Irgb (ANSI to RGB) 

- Catppuccin_mocha_rgb - Catppuccin color palette in RGB. 

- Cursor stuff, and screen stuff: 

- cursor class - show/hide, move up/down/left/right, next/prev line, set column, set pos, get pos query, save/load pos, save/load all attributes. 

- screen/line classes - erase codes (to end/to start/all/saved) and alt-screen save/load. 

- place(x, y, msg) - prints text at a custom position with optional clear screen, save/restore cursor, and clear line. 

- renameTerminal() - renames the terminal's title. 

- chars dict - control characters like BEL, HT, ESC, etc. 

### Console Inspection: 

- get_cursor_position() - returns the cursor pos X/Y. 

- get_char_at_cursor() / get_char_at(x, y) - reads charer at that position of the console buffer 

- get_word() - reads words of the console buffer 

- get_cell_color_at() / attr_to_ansi() reads a cell's fg/bg attributes and converts them to ANSI or RGB. 

### Text Rendering tools: 

- bd() - dynamic box drawing tool (corners, joins, multi-line paths, lengths, and color) 

- ps() - shaded block drawing characters for simple gradients. 

- rainbowify() - helps make rainbow colored text for fg/bg/both 

- wrap() - applies a list of colors cyclically to (characters, words, or lines)/strings (works well with gradients) 

- load_bar() - animated rainbow progress bar 

- BIG_CLOCK() - large ANSI clock demo with AM/PM and date. 

- divider(), leadZero, loop_, iprint - small utilities / helper functions. 

### Gradients and Interpolation (uses data, not colors, so can make more custom gradients): 

- lerp() - interpolates numbers, lists, or tuples. 

- gradient2() - creates a linear gradient between 2 values.  

- gradient4() - four-color bilinear gradient, flat or matrix output.  

### Graphing:   

- cpu_graph() - history-based bar graph with precision, single color, or per row color list.  

- clear_graph_area() - clears out a rectangular area  

- cava_graph() - audio visualizer spectrum bars. (based on cava)  

- audio_listener() - audio capturer with FFT, Hanning window, and smoothing.  

### Canvas Class:  

- per-cell char and color buffers,  

- set_pixel, line, rect, circle, draw (2d list to color map)  

- doubleX mode for 2-cell-wide square pixels.  

- uses a renderer for fast output.  

### Better Input system:  

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

### Interactive documentation repl (doc_cmd) (has a couple of mini tools in it): 

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

### Media tools: 

- playFile - pygame playback with  pause support. 

- mediaControl class - thread safe pause / seek state. 

- reset_audio() 

- video, k_img,loadFile, stream_window - video/img rendering. (through the displays.py file) 

### Hardware tools: 

- lsDevices() - shows all HID devices and copies the list to the clipboard. 

- listen() - reads raw HID reports. 

- copy() - copies to clipboard through clip.exe 

### btopPy(): 

- Note: Made for terminals 170x40 or larger, and it warns you if yours is smaller
- a. CPU graph, core based stat bars, load averages, CPU name/GHz 

- b. Memory and page-file stats, per-disk usage with HDD/SSD detection (through a background thread). (up to 6 disks) 

- c. cava panel 

- d. Matrix rain panel. 

- e. Adjustable refresh rate (-/+) 

- f. Theme cycling (k/l) 

- g. Controller shortcuts. 

### Theme tools: 

- ThemeEngine -uses, loads, and builds palettes from .theme files in the themes folder. 

- themeDemo() - preview table for a theme 

- themeselect() -  arrow key theme viewer with favorites system. 

-  

### Demos + Games (keep in mind not product just shows off product): 

- rhythmGame - 4-lane (d/f/j/k) rhythm game with scoring system. 

- aimGameDemo - mouse click game with cps stats. 

- donutDemo - a spinning donut/torus in grayscale (same as donut.py) 

- gradientDemo - animated 4-color gradient. Looks really cool. 

- clock() - simple clock rendered through canvas. 

- clickDemo, clockDemo, arrowsDemo, controllerDemo - input demos (for controllerDemo, make sure your controller is plugged in before running the file with the Demo.) 

- canvasDemo, randDemo, wrapDemo, tableDemo, Demo256, fDemo - rendering/ANSI demos 

- musicDemo, ytDemo, videoDemo, slideshowDemo, mirrorDemo - media demos. 
