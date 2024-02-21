import asyncio

from .base import TermArtist as ta
from .logger import *

print("Running package", ta.TrueColor.FG(255, 120, 50), "pytools", ta.RESET)

from .fileconverter import FileConverter

try: 
    FileConverter.pdf2ppt("test.pdf", True)
except ImportError as e:
    print(e)
    
from .foldertree import *

print(get_folderTree_list("~/Desktop/Official_docs")[:2], "...")

from .system import *

print(get_disk_usage("/"))