'This module consists of commonly used functions and classes.'

""" =================================================================
| base.py
|
| Created by Jack on 01/20, 2024
| Copyright © 2024 jacktogon. All rights reserved.
================================================================= """

#NOTE: `base.py` will not be importing anything else other than the standard library

import os, sys, time, re
import subprocess
from pathlib import Path
from datetime import datetime, timezone

__all__ = (
    'TermArtist', 'TimeConverter',
    'get_venv_path', 'try_import_or_install',
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
        def move_up(lines=1):
            print(TermArtist.Cursor.UP.format(lines), end='')

        @staticmethod
        def move_down(lines=1):
            print(TermArtist.Cursor.DOWN.format(lines), end='')

        @staticmethod
        def move_forward(columns=1):
            print(TermArtist.Cursor.FORWARD.format(columns), end='')

        @staticmethod
        def move_back(columns=1):
            print(TermArtist.Cursor.BACK.format(columns), end='')
            
        @staticmethod
        def set_pos(line: int, column: int):
            print(TermArtist.Cursor.SET_POSITION.format(line, column), end="")

        @staticmethod
        def save_pos():
            print(TermArtist.Cursor.SAVE_POSITION, end='')

        @staticmethod
        def restore_pos():
            print(TermArtist.Cursor.RESTORE_POSITION, end='')

        @staticmethod
        def hide():
            print(TermArtist.Cursor.HIDE, end='')

        @staticmethod
        def show():
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
        >>> print(TrueColor.FG(255, 0, 0) + "This text is red")
        >>> print(TrueColor.BG(0, 0, 255) + "This text has a blue background")
        '''
        FG = lambda r, g, b: f'\033[38;2;{r};{g};{b}m'
        BG = lambda r, g, b: f'\033[48;2;{r};{g};{b}m'
        
    class Composition():
        ''' Jack's combinations '''
        DEBUG = "\x1b[1;90;43m"
        ERROR = "\x1b[1;97;101m"        


class TimeConverter:
    ''' Convert time to certain format '''
    
    @staticmethod
    def second_to_standard(sec: float) -> str:
        '''
        Convert seconds to a ISO 8601 time format, without timezone
        If provided seconds is smaller, don't show.

        Parameters:
        -----------
        - `sec`: Number of seconds

        Returns:
        --------
        - `str`: [yy:][mm:][dd:]hh:mm:ss[.ssss]
        '''
        # Constants for time conversion
        seconds_in_minute = 60
        seconds_in_hour   = 3600
        seconds_in_day    = 86400
        seconds_in_month  = 2629743     # Average month length in seconds (30.44 days)
        seconds_in_year   = 31556926    # Average year length in seconds (365.25 days)

        # Calculate each time component
        years, remainder          = divmod(sec, seconds_in_year)
        months, remainder         = divmod(remainder, seconds_in_month)
        days, remainder           = divmod(remainder, seconds_in_day)
        hours, remainder          = divmod(remainder, seconds_in_hour)
        minutes, seconds          = divmod(remainder, seconds_in_minute)
        int_seconds, frac_seconds = divmod(seconds, 1)

        res = ""
        if years > 0:
            res += f"{int(years):02}-"
        if months > 0:
            res += f"{int(months):02}-"
        if days > 0:
            res += f"{int(days):02}T"
            
        res += f"{int(hours):02}h:{int(minutes):02}m:"
        
        if frac_seconds > 0:
            res += f"{int(int_seconds):02}.{int(frac_seconds * 1e4):04}s"
        else:
            res += f"{int(int_seconds):02}s"

        return res


    @staticmethod
    def unix_to_datestring(unix: float) -> str:
        ''' 
        Convert unix time to date string based on current system time zone
        
        Params:
        -------
        - `unix`: unix time
        
        Returns:
        --------
        - `str`: %Y-%m-%d %H:%M:%S.%f
        '''
        sys_timezone = datetime.now().astimezone().tzinfo               # Get the local timezone of the system
        utc_time     = datetime.fromtimestamp(unix, tz=timezone.utc)    # Get the current time in UTC
        local_date   = utc_time.astimezone(sys_timezone)                # Convert to the local timezone
        date_string  = local_date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Format datetime object, including milliseconds
        return f"{date_string} {local_date.tzname()}"
    
    @staticmethod
    def time_to_seconds(time_str):
        parts = time_str.split(":")

        # Initialize hours, minutes, and seconds
        hours, minutes, seconds = 0, 0, 0

        if len(parts) == 3:
            # Format is hours:minutes:seconds
            hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
        elif len(parts) == 2:
            # Format is minutes:seconds
            minutes, seconds = int(parts[0]), int(parts[1])
        else:
            raise ValueError("Invalid time format")

        # Convert everything to seconds
        total_seconds = hours * 3600 + minutes * 60 + seconds

        return total_seconds
    

# ============================================================================
# Functions
# ============================================================================
def get_venv_path() -> str | None:
    ''' Get path to current venv '''
    return os.environ.get('VIRTUAL_ENV')

def try_import_or_install(
    module:     str,
    package:    str     = None,
    version:    str     = None
) -> None:
    '''
    Attempts to import a module. If not present, attempts to install it.
    
    Params:
    -------
    - `module`:  name of the module to try to import.
    - `package`: name of the package to try to install. Defaults to the module name if not provided.
    - `version`: version of the package to install. If not provided, the latest version is installed.
    '''
    package = package or module
    if version: package += f'=={version}'

    try:
        __import__(module)
    except ImportError:
        print(f"Module {TermArtist.Foreground.BRIGHT_CYAN}{module}{TermArtist.RESET} not found and will be installed")
        if not (
            get_venv_path() or hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        ):
            print("It's recommended to run this script in a virtual environment.")

        match sys.platform:
            case "win32":
                print("Performing installation on Windows OS")
            case "darwin":
                print("Performing installation on macOS")
            case "linux":
                print("Performing installation on Linux")

        # Ensure pip is available
        try:
            subprocess.check_call([sys.executable, '-m', 'ensurepip'])
        except subprocess.CalledProcessError as e:
            print(f"ensurepip failed: {e.with_traceback()}")

        # Try to install the package
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            __import__(module)
        except subprocess.CalledProcessError as e:
            print(f"Installation of {package} failed with error: {e.with_traceback()}")
        except ImportError as e:
            print(f"Module {module} could not be imported after installation: {e.with_traceback()}")

    print(f"Module {TermArtist.Foreground.BRIGHT_CYAN}{module}{TermArtist.RESET} is now imported and ready to use.")