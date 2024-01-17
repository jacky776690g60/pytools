#NOTE: `base.py` will not be importing anything else other than the standard library

import os, sys, time, re
import subprocess
from pathlib import Path
from datetime import datetime, timezone

__all__ = (
    'TermArtist',       
)

class TermArtist:
    '''
    A class containing different ANSI Escape Codes for terminal graphics
    
    See Also
    --------
    - https://chrisyeh96.github.io/2020/03/28/terminal-colors.html
    - https://en.wikipedia.org/wiki/ANSI_escape_code
    
    >>> print(TermArtist.RED, "RED Text", TermArtist.RESET)
    >>> print(TermArtist.RED, "RED", "RED_again", TermArtist.RESET, "Is_Reset")
    '''
    
    RESET = ENDC = '\033[0m'
    "Reset"
    
    class Cursor:
        '''
        Cursor manipulation class for terminal control.
        
        Examples
        --------
        >>> print(Cursor.UP.format(2), end='')
        >>> print("Two lines up")
        ...
        >>> [print(i+1) for i in range(10)]
        >>> TermArtist.Cursor.move_cursor_up(4)
        >>> print(TermArtist.Color256.FG.format(179)+"Moved cursor up 4 lines..")
        '''
        UP               = '\033[{}A'
        DOWN             = '\033[{}B'
        FORWARD          = '\033[{}C'
        BACK             = '\033[{}D'
        NEXT_LINE        = '\033[{}E'
        PREV_LINE        = '\033[{}F'
        SET_COLUMN       = '\033[{}G'
        SET_POSITION     = '\033[{};{}H'
        SAVE_POSITION    = '\033[s'
        RESTORE_POSITION = '\033[u'
        HIDE             = '\033[?25l'
        SHOW             = '\033[?25h'
        
        @staticmethod
        def move_cursor_up(lines=1):
            print(TermArtist.Cursor.UP.format(lines), end='')

        @staticmethod
        def move_cursor_down(lines=1):
            print(TermArtist.Cursor.DOWN.format(lines), end='')

        @staticmethod
        def move_cursor_forward(columns=1):
            print(TermArtist.Cursor.FORWARD.format(columns), end='')

        @staticmethod
        def move_cursor_back(columns=1):
            print(TermArtist.Cursor.BACK.format(columns), end='')

        @staticmethod
        def save_cursor_position():
            print(TermArtist.Cursor.SAVE_POSITION, end='')

        @staticmethod
        def restore_cursor_position():
            print(TermArtist.Cursor.RESTORE_POSITION, end='')

        @staticmethod
        def hide_cursor():
            print(TermArtist.Cursor.HIDE, end='')

        @staticmethod
        def show_cursor():
            print(TermArtist.Cursor.SHOW, end='')
            
    class Screen:
        '''
        Examples:
        ---------
        >>> [print(i) for i in range(15)]
        >>> print(TermArtist.Screen.CLEAR)
        >>> empty screen...
        '''
        CLEAR      = '\033[2J'
        CLEAR_LINE = '\033[2K'
        
    class FontStyle():
        BOLD      = '\033[1m'
        FAINT     = '\033[2m'
        "Dim, decrease density"
        ITALIC    = '\033[3m'
        UNDERLINE = '\033[4m'
        CROSSOUT  = '\033[9m'
        "Characters legible but marked as if for deletion. Not supported in Terminal.app"
        OVERLINE  = '\033[53m'

    class Foreground():
        # Standard Colors
        BLACK           = "\033[30m"
        RED             = "\033[31m"
        GREEN           = "\033[32m"
        YELLOW          = "\033[33m"
        BLUE            = "\033[34m"
        MAGENTA         = "\033[35m"
        CYAN            = "\033[36m"
        WHITE           = "\033[37m"
        # Bright Colors
        BRIGHT_BLACK    = "\033[90m"
        BRIGHT_RED      = "\033[91m"
        BRIGHT_GREEN    = "\033[92m"
        BRIGHT_YELLOW   = "\033[93m"
        BRIGHT_BLUE     = "\033[94m"
        BRIGHT_MAGENTA  = "\033[95m"
        BRIGHT_CYAN     = "\033[96m"
        BRIGHT_WHITE    = "\033[97m"


    class Background():
        # Standard Colors
        BLACK         = "\033[40m"
        RED           = "\033[41m"
        GREEN         = "\033[42m"
        YELLOW        = "\033[43m"
        BLUE          = "\033[44m"
        MAGENTA       = "\033[45m"
        CYAN          = "\033[46m"
        WHITE         = "\033[47m"
        # Bright Colors
        BRIGHT_BLACK  = "\033[100m"
        BRIGHT_RED    = "\033[101m"
        BRIGHT_GREEN  = "\033[102m"
        BRIGHT_YELLOW = "\033[103m"
        BRIGHT_BLUE   = "\033[104m"
        BRIGHT_MAGENT = "\033[105m"
        BRIGHT_CYAN   = "\033[106m"
        BRIGHT_WHITE  = "\033[107m"
        
    class Effect():
        SLOWBLINK  = '\033[5m'
        RAPIDBLINK = '\033[6m'
        "MS-DOS ANSI.SYS, 150+ per minute; not widely supported"
        NOBLINK    = '\033[25m'
        "Turn off blinking"
        CONCEAL    = '\033[8m'
        "Not widely supported."
        
    class Color256:
        '''
        256-Color Mode
        
        NOTE:
        -----
        - `Supported`: GNOME Terminal, iTerm2, Konsole, Windows Terminal, Terminator, Alacritty, Hyper
        - `Limited Support`: macOS Terminal, older versions of Linux terminals
        - `Unsupported`: Command Prompt, older PowerShell versions without Windows Terminal
        
        Examples:
        ---------
        >>> print(Color256.FG(128) + "text colored with color code 128"')
        >>> print(Color256.BG(128) + "text colored with color code 128"')

        ''' 
        FG = lambda color_code: f'\033[38;5;{color_code}m'
        BG = lambda color_code: f'\033[48;5;{color_code}m'
        
    class TrueColor:
        '''
        24-bit True Color Mode
        
        NOTE:
        -----
        - `Supported`: GNOME Terminal (newer versions), iTerm2, Konsole, Windows Terminal, Alacritty, Hyper, Terminator
        - `Limited Support`: Older versions of popular Linux terminals
        - `Unsupported`: Command Prompt, macOS Terminal, older PowerShell versions without Windows Terminal
        
        Examples:
        ---------
        >>> print(ColorRGB.FG(255, 0, 0) + "This text is red")
        >>> print(ColorRGB.BG(0, 0, 255) + "This text has a blue background")
        '''
        FG = lambda r, g, b: f'\033[38;2;{r};{g};{b}m'
        BG = lambda r, g, b: f'\033[48;2;{r};{g};{b}m'
        
    class Composition():
        ''' Jack's combinations '''
        DEBUG = "\x1b[1;90;43m"
        ERROR = "\x1b[1;97;101m"
        
        
if __name__ == "__main__":
    print(TermArtist.Composition.DEBUG, "hej hej", TermArtist.RESET)