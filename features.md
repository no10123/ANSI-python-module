## Files and Folders

-- folders -- <br>
themes - a copy of btop4win's  themes folder and is used by themeParser.py to create color palettes for tui's. <br>
-- files (in src/colorful-swiss) -- <br>
DataFetcher.py - a file that interacts with the  windows api to grab hardware data, which can be used to create terminal applications that can easily use the device's information. <br>
clock.py - a simple single-file demo which uses the cursor class and shows how you can make simple applications that have color. <br>
displays.py - a helper file which is used to render GIF's, videos, and audio. And images in multiple formats; for example, you can show an image using Kitty protocol, sixel, ASCII grayscale, or ANSI ASCII. Honestly, one of the more impressive tools. <br>
donut.py - a single-file demo of how cool animations can be made with the color tools like rgb, which shows a spinning grayscale donut/torus. It is also in module.py separately. <br>
example.md - a Markdown file used to test and show off terminal.py and how it renders different Markdown effects. <br>
flipper.py - a separate file similar to DataFetcher.py, which interacts with the windows api to see ports and connected devices and uses a Flipper Zero CLI as an example for sending data through ports with this tool. <br>
module.py - arguably the main and biggest file; due to its size, I have listed its features in the section below labeled features. <br>
spotlight.py - a file that puts Windows Spotlight images in a folder (default is the wallpapers folder). This allows you to easily access these images for bg's or other uses. <br>
themeParser.py - creates color palettes for tui's using the themes folder.

Features (module.py)
--- <br>
- COLOR STUFF: <br>
- rgb() with fg/bg and custom ranges through Max. <br>
- color() - base 8 color set fg/bg with bright variants. <br>
- color256() - 256 color palette codes <br>
- graphics class of dictionaries for adding and removing codes (bold, dim, italic, blink, reverse, hidden, strikethrough) <br>
- setMode() - screen mode <br>
- color converters - HSVtoRGB, HEXtoRGB, CMYKtoRGM, Irgb (ANSI to RGB) <br>
- catpuccin_mocha_rgb - catpuccin color palette in RGB. <br>
- Cursor stuff, and screen stuff: <br>
- cursor class - show/hide, move up/down/left/right, next/prev line, set column, set pos, get pos query, save/load pos, save/load all attributes. <br>
- screen/line classes - erase codes (to end/to start/all/saved) and alt-screen save/load. <br>
- place(x, y, msg) - prints text at a custom position with optional clear screen, save/restore cursor, and clear line. <br>
- renameTerminal() - renames the terminal's title. <br>
- chars dict - control characters like BEL, HT, ESC, etc. <br>
-  <br>
- Console Inspection: <br>
- get_cursor_position() - returns the cursor pos X/Y. <br>
- get_char_at_cursor() / get_char_at(x, y) - reads charer at that position of the console buffer <br>
- get_word() - reads words of the console buffer <br>
- get_cell_color_at() / attr_to_ansi() reads a cell's fg/bg attributes and converts them to ANSI or RGB. <br>
-  <br>
- Text Rendering tools: <br>
- bd() - dynamic box drawing tool (corners, joins, multi-line paths, lengths, and color) <br>
- ps() - shaded block drawing characters for simple gradients. <br>
- rainbowify() - helps make rainbow colored text for fg/bg/both <br>
- wrap() - applies a list of colors cyclically to (characters, words, or lines)/strings (works well with gradients) <br>
- load_bar() - animated rainbow progress bar <br>
- BIG_CLOCK() - large ANSI clock demo with AM/PM and date. <br>
- divider(), leadZero, loop_, iprint - small utilities / helper functions. <br>
- Gradients and Interpolation (uses data, not colors, so can make more custom gradients): <br>
- lerp() - interpolates numbers, lists, or tuples. <br>
- gradient2() - creates a linear gradient between 2 values.  <br>
- gradient4() - four-color bilinear gradient, flat or matrix output.  <br>
- 
- Graphing:   <br>
- cpu_graph() - history-based bar graph with precision, single color, or per row color list.  <br>
- clear_graph_area() - clears out a rectangular area  <br>
- cava_graph() - audio visualizer spectrum bars. (based on cava)  <br>
- audio_listener() - audio capturer with FTT, Hanning window, and smoothing.  <br>
- Canvas Class:  <br>
- per-cell char and color buffers,  <br>
- set_pixel, line, rect, circle, draw (2d list to color map)  <br>
- doubleX mode for 2-cell-wide square pixels.  <br>
- uses a renderer for fast output.  <br>
- 
- Better Input system:  <br>
- RawTerminal - context manager for raw mode.  <br>
- finput() - unified input function - supports: <br>
- a. keyboard (max length, auto-submit, hidden input, custom enter/backspace/tab handling.)  <br>
- b. Mouse (clicks and scrolling), <br> 
- c. ESC key, Controller inputs (buttons, D-pad, and sticks with deadzones).  <br>
- d. custom_out hooks via @f_out which can exec code per input allowing for easy input threading.  <br>
- poll_controller() background thread reading gamepad inputs.  <br>
- get_char() / char_available() non blocking key  reading.  <br>
- floop() - loops any function in optionally raw mode to make it easier to thread functions.  <br>
- typed_str() - parses typed values (int, float, bool, list: int, tuple: str, etc.) from strings  <br>
-  <br>
- Interactive documentation repl (doc_cmd) (has a couple of mini tools in it): <br>
- a. .menu, .back, id/name, history, .debug - navigation commands <br>
- b. stylized help cards made through pretty_doc, which has color-coded sections, type annotations, warped text, and optional chrome borders. <br>
- c. main_menu() - multi-column function index, a-z sections, and docstring-aware color-coding. <br>
- d. .run / .copy - execute or copy a docstring example block, and print return values. <br>
- e. .call - calls a function with typed args from prompt. <br>
- f. .f / .fm - allows you to favorite functions. <br>
- g. .deps - view dependencies via AST (local, imported, builtin, unresolved calls). <br>
- h. .form - interactive form that builds a docstring and applies it in memory, copies it, and optionally writes it to the source file. <br>
- i. .cd / .ls / .pwd - move through the file system. <br>
- j. .view - see images via kitty/sixel/ascii/gray, and markdown via mdGlow (mdGlow is the terminal.py tool). <br>
- k. .color / .theme / .rgb / .chrome - allows you to change the theme colors to match your vibe. <br>
- l. --a / --h / --A - flags that allow you to stop screen clearing, the help msg, or both. <br>
- m. DOC_STYLE - allows for custom docstring types and formats. <br>
- n. parse_doc, get_dependencies, getFuncs, _write_docstring_to_source, _build_docstring_body - helpers <br>
-  <br>
- Media tools: <br>
- fetch_yt_audio() / fetch_yt_video() - downloads yt videos via yt-dlp (MP3/MP4) <br>
- playFile - pygame playback with  pause support. <br>
- mediaControl class - thread safe pause / seek state. <br>
- reset_audio() <br>
- video, k_img,loadFile, stream_window - video/img rendering. (through the displays.py file) <br>
-  <br>
- Hardware tools: <br>
- lsDevices() - shows all HID devices and copies the list to the clipboard. <br>
- listen() - reads raw HID reports. <br>
- copy() - copies to clipboard through clip.exe <br>
-  <br>
- BIG DEMO (btopPy()): <br>
- Note: this demo will probably (like a 1% chance it actually works) not work on many devices due to sizing issues. (please see the yt video for proof), This is because it is not a product and instead a demo used to show off what you can do with the tool, putting most of the tools into one big showcase, and is not intended for public use. But here are the features it has / shows off *[1]: <br>
- a. CPU graph, per-core bars, load averages, CPU name/GHz <br>
- b. Memory and page-file stats, per-disk usage with HDD/SSD detection (through a background thread). <br>
- c. cava panel <br>
- d. Matrix rain panel. <br>
- e. Adjustable refresh rate (-/+) <br>
- f. Theme cycling (k/l) <br>
- g. Controller shortcuts. <br>
-  <br>
- Theme tools (there's more in themeParser.py): <br>
- ThemeEngine -uses, loads, and builds palettes from .theme files in the themes folder. <br>
- themeDemo() - preview table for a theme <br>
- themeselect() -  arrow key theme viewer with favorites system. <br>
-  <br>
- Demos + Games (keep in mind not product just shows off product) (also most are in the yt vid): <br>
- rhythmGame - 4-lane (d/f/j/k) rhythm game with scoring system. <br>
- aimGameDemo - mouse click game with cps stats. <br>
- donutDemo - a spinning donut/torus in grayscale (same as donut.py) <br>
- gradientDemo - animated 4-color gradient. Looks really cool. <br>
- clock() - simple clock rendered through canvas. <br>
- clickDemo, clockDemo, arrowsDemo, controllerDemo - input demos (for controllerDemo, make sure your controller is plugged in before running the file with the Demo.) <br>
- canvasDemo, randDemo, wrapDemo, tableDemo, Demo256, fDemo - rendering/ANSI demos <br>
- musicDemo, ytDemo, videoDemo, slideshowDemo, mirrorDemo - media demos. <br>