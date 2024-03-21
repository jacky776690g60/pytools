'sync/async Logging classes'

""" =================================================================
| pytools/logger.py
|
| #Author Jack
| Created by Jack on 01/20, 2024
| Copyright © 2024 jacktogon. All rights reserved.
================================================================= """

import asyncio, time
from pathlib import Path
from typing import *
from enum import Enum
from functools import total_ordering

from .base import TermArtist as ta, TimeConverter as tc

__all__ = (
    'LogLevel', 'Logger'
)

@total_ordering
class LogLevel(Enum):
    '''
    Log Level for the custom `Logger` class
    
    Additional Tip:
    ---------------
    - We can also use auto() to remove manual comparison in Enum
    '''
    INFO  = 0
    WARN  = 1
    ERROR = 2
    DEBUG = 3
    ALL   = 4
    
    def __lt__(self, other: 'LogLevel'):
        if self.__class__ is other.__class__:
            return self.value < other.value
        raise TypeError(f"'<' not supported between instances of '{type(self).__name__}' and '{type(other).__name__}'")
    
    def __eq__(self, other: 'LogLevel'):
        if isinstance(other, LogLevel):
            return self.value == other.value
        raise TypeError(f"'==' not supported between instances of '{type(self).__name__}' and '{type(other).__name__}'")


class Logger:
    '''
    This class supports both sync and async operations.
    
    Examples:
    ---------
    >>> LOGGER = Logger(log_level=LogLevel.ALL, logfile_path="./output.log")
    '''
    def __init__(self,
        log_level:       LogLevel,
        logfile_path:    str        = None,
        overwrite:       bool       = True,
        daemon_name:     str        = '',
        print_time:      bool       = False
    ) -> None:
        self.log_level     = log_level
        self.logfile_path  = Path(logfile_path).resolve() if logfile_path else None
        self.daemon_name   = daemon_name
        self.print_time    = print_time
        
        self.MAX_TAG_LENGTH = max(len(s) for s in ["INFO", "DEBUG", "WARN", "ERROR"]) + 3 + len(daemon_name)
        
        if logfile_path:
            self.logfile_path.parent.mkdir(parents=True, exist_ok=True)
            if overwrite:
                self.logfile_path.write_text('')
    
    # =============================
    # Private Functions
    # =============================
    def __write_to_file(self, message: str):
        with open(self.logfile_path, 'a') as logfile:
            logfile.write(message)
    
    async def __save_async(self,
        level:      LogLevel,
        message:    str,
    ):
        if self.log_level >= level and self.logfile_path:
            # run the blocking file write operation in a separate thread
            await asyncio.to_thread(self.__write_to_file, message)
            
    def __save_sync(self,
        level:      LogLevel,
        message:    str,
    ):
        if self.log_level >= level and self.logfile_path:
            self.__write_to_file(message)
    
    def __log(self,
        level:      LogLevel,
        values:     Any,
        color:      str             = ta.RESET,
        start:      str             = "",
        end:        str             = "\n",
        is_async:   Optional[bool]  = None,
    ):
        strings     = []
        tag         = '[' + ((f"{self.daemon_name} " if self.daemon_name else "") + level.name + ']').ljust(self.MAX_TAG_LENGTH) 
        tag_colored = color + tag + ta.RESET
        cur_time    = tc.unix_to_datestring(time.time()).strip()
        
        if self.print_time: strings.append(cur_time)
        strings.append(start)
        strings.append(tag_colored)
        strings.extend(values)
        strings.append(end)
        
        msg_colored = ' '.join(map(str, strings))
        print(msg_colored, end="")
        
        if not self.logfile_path: return
        
        if self.print_time: 
            strings.pop(0)
        strings[1] = tag
        strings.insert(0, cur_time)
        msg_no_colored = ' '.join(map(str, strings))
        
        if is_async or (is_async is None and asyncio.iscoroutinefunction(values)):
            return self.__save_async(level, msg_no_colored)
        return self.__save_sync(level, msg_no_colored)
                
    # =============================
    # Public Functions
    # =============================
    def info(self, *values, start="", end="\n", is_async: Optional[bool]=None):
        return self.__log(LogLevel.INFO, values, ta.RESET, start, end, is_async)
    
    def warn(self, *values, start="", end="\n", is_async: Optional[bool]=None):
        return self.__log(LogLevel.WARN, values, ta.FG.BRIGHT_MAGENTA, start, end, is_async)
    
    def debug(self, *values, start="", end="\n", is_async: Optional[bool]=None):
        return self.__log(LogLevel.DEBUG, values, ta.FG.BRIGHT_YELLOW, start, end, is_async)
    
    def error(self, *values, start="", end="\n", is_async: Optional[bool]=None):
        return self.__log(LogLevel.ERROR, values, ta.Composition.ERROR, start, end, is_async)