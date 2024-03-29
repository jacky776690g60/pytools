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

from .networkutils import *

from .shell import *
import sys
pe = PersistentShell(True)

try:
    while True:
        i = str(input("> "))
        print(pe.run_command(i))
except KeyboardInterrupt as e:
    print("Keyboard Interrupted.")
    
# nb = NonBlockingStreamReader(sys.stdin)