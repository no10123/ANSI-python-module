import sys
 
if sys.platform != "win32":
    raise ImportError("colorful-swiss currently supports Windows only.")
 
from .module import *
 
__version__ = "0.1.2"
