import os
import re

class ThemeEngine:
    def __init__(self, theme_folder="themes"):
        self.theme_folder = theme_folder
        self.colors = {}
        self.RESET = "\033[0m"

    def hex_to_ansi(self, hex_code, is_background=False):
        """literally hex -> ANSI"""
        hex_code = hex_code.strip().strip('"').strip("'").lstrip('#')
        if len(hex_code) != 6:
            return "\033[49m" if is_background else "\033[39m"
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        layer = "48" if is_background else "38"
        return f"\033[{layer};2;{r};{g};{b}m"

    def get_available_themes(self):
        """returns all .theme's in themes folder"""
        if not os.path.exists(self.theme_folder):
            os.makedirs(self.theme_folder)
            return []
        return [f.replace('.theme', '') for f in os.listdir(self.theme_folder) if f.endswith('.theme')]

    def load_theme(self, theme_name):
        """creates a dict w/ colors in .theme"""
        file_path = os.path.join(self.theme_folder, f"{theme_name}.theme")
        
        if not os.path.exists(file_path):
            print(f"Theme '{theme_name}' not found.")
            return False
        self.colors = {}
        pattern = re.compile(r'^theme\[([^\]]+)\]=["\']?(#[A-Fa-f0-9]{6})["\']?')

        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                match = pattern.match(line)
                if match:
                    key = match.group(1)
                    hex_val = match.group(2)
                    is_bg = key.endswith('_bg')
                    self.colors[key] = self.hex_to_ansi(hex_val, is_background=is_bg)
        
        return True

    def get(self, key):
        """gets color for key"""
        return self.colors.get(key, "")