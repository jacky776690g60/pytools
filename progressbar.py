""" =================================================================
| progressbar.py  --  Projects/pytools/progressbar.py
|
| #Author Jack
| Created on 07/21, 2023
| Copyright © 2023 jacktogon. All rights reserved.
================================================================= """

import time, shutil, threading
from typing import Callable, Dict, Tuple

from .base import TermArtist as ta, TimeConverter as tc

__all__ = (
    'ProgressBar', 'MultiLineProgressBar'
)

class ProgressBar:
    '''
    Threading-safe progress bar

    Compatibility:
    --------------
    - Ubuntu
    - MacOS
    - Windows

    Examples:
    ---------
    >>> def on_completion():
    ...     print("Process completed!")
    ...
    ... numbers = [x * 5 for x in range(2000, 2200)]
    ...
    ... results = []
    ... pbar = ProgressBar(len(numbers), completion_callback=on_completion)
    ... pbar.use_interval_time = True
    ...
    ... for i, x in enumerate(numbers):
    ...     results.append(math.factorial(x))
    ...     pbar.draw(i, pre_str=i)
    '''
    
    # =============================
    # Class Variables
    # =============================
    #               0    1    2    3    4    5    6    7
    FILL_CHARS  = ['█', '■', '☒', '▮', '▀', '◉', '=', '+']
    TRACK_CHARS = ['░', '⣀', '□', '▯', '▄', '◌', '-']
    STYLES: Dict[int, Tuple[str, str, str, str]] = {
        0:  (ta.FG.WHITE,   TRACK_CHARS[0],     ta.FG.WHITE,    FILL_CHARS[1]),
        1:  (ta.FG.YELLOW,  TRACK_CHARS[0],     ta.FG.BLUE,     FILL_CHARS[1]),
        2:  (ta.FG.YELLOW,  TRACK_CHARS[0],     ta.FG.CYAN,     FILL_CHARS[1]),
        3:  (ta.FG.GREEN,   TRACK_CHARS[0],     ta.FG.WHITE,    FILL_CHARS[1]),
        4:  (ta.FG.WHITE,   TRACK_CHARS[0],     ta.FG.GREEN,    FILL_CHARS[1]),
        5:  (ta.FG.CYAN,    TRACK_CHARS[0],     ta.FG.WHITE,    FILL_CHARS[1]),
        6:  (ta.FG.WHITE,   TRACK_CHARS[2],     ta.FG.WHITE,    FILL_CHARS[2]),
        7:  (ta.FG.YELLOW,  TRACK_CHARS[2],     ta.FG.BLUE,     FILL_CHARS[2]),
        8:  (ta.FG.YELLOW,  TRACK_CHARS[2],     ta.FG.RED,      FILL_CHARS[2]),
        9:  (ta.FG.GREEN,   TRACK_CHARS[2],     ta.FG.WHITE,    FILL_CHARS[2]),
        10: (ta.FG.WHITE,   TRACK_CHARS[2],     ta.FG.GREEN,    FILL_CHARS[2]),
        11: (ta.FG.BLUE,    TRACK_CHARS[2],     ta.FG.WHITE,    FILL_CHARS[2]),
        12: (ta.FG.CYAN,    TRACK_CHARS[2],     ta.FG.WHITE,    FILL_CHARS[2]),
        13: (ta.FG.CYAN,    TRACK_CHARS[6],     ta.FG.YELLOW,   FILL_CHARS[6]),
        14: (ta.FG.CYAN,    TRACK_CHARS[6],     ta.FG.RED,      FILL_CHARS[6]),
        15: (ta.FG.CYAN,    TRACK_CHARS[6],     ta.FG.RED,      FILL_CHARS[7]),
        16: (ta.FG.CYAN,    TRACK_CHARS[4],     ta.FG.RED,      FILL_CHARS[4]),
    }
    '''
    - `track_color`
    - `track_char`
    - `fill_color`
    - `fill_char`
    '''

    # =============================
    # dunders
    # =============================
    def __init__(self, 
        total:                  int,
        bar_length:             int         = 0,
        use_interval_time:      bool        = False,
        completion_callback:    Callable    = None
    ) -> None:
        '''
        Params:
        -------
        - `total`: total length of tasks
        - `bar_length`: length of the progress bar
        - `use_interval_time`: If True, print the elapsed time in each interval
        - `completion_callback`: a callback on progress reaching 100%
        '''
        if total <= 0: raise ValueError("Total length of tasks must be > 0")
        self.total                = total
        self.bar_length           = bar_length
        self.use_interval_time    = use_interval_time
        self.completion_callback  = completion_callback
        
        # Initialize a lock for thread-safe operations
        self._lock = threading.Lock()
        
        self._use_dynamic_length    = bar_length == 0 # If bar_length is 0, set dynamic length
        if self._use_dynamic_length: self._update_bar_length()
        
        self._style                 = ProgressBar.STYLES[14]
        self._start_time            = time.time()
        self._percentage_breakpoint = 0
        
        

    def _update_bar_length(self):
        columns = shutil.get_terminal_size().columns # Get terminal width and adjust bar_length
        self.bar_length = max(10, columns // 4)

    # =============================
    # getters & setters
    # =============================
    @property
    def style(self):
        return self._style
    
    @style.setter
    def style(self, idx: int):
        if not (0 <= idx < len(ProgressBar.STYLES)):
            raise IndexError("Index out of range: (0 ~ {})".format(len(ProgressBar.STYLES) - 1))
        self._style = ProgressBar.STYLES[idx]
    
    @property
    def track_color(self):
        return self.style[0]
    
    @property
    def track_char(self):
        return self.style[1]
    
    @property
    def fill_color(self):
        return self.style[2]
    
    @property
    def fill_char(self):
        return self.style[3]
    
    @property
    def perc_bkpt(self):
        '''Define percentage of where a new line should occur'''
        return self._percentage_breakpoint

    @perc_bkpt.setter
    def perc_bkpt(self, value: float):
        '''
        correspond to percentage

        Params:
        -------
        - `value`: 0 ~ 100
        '''
        if not 0 <= value <= 100: raise ValueError("newline_at_percentage must be in the range 0 ~ 100")
        self._percentage_breakpoint = value 

    # =============================
    # Public Functions
    # =============================
    def draw(self, 
        progress: float, 
        pre_str:  str   = "", 
        post_str: str   = ""
    ) -> None:
        '''
        Print the progress to console based on condition

        Params:
        -------
        - `progress` current values (automatically adding 1 to this value)
        - `pre_str` string that will appear before the progress bar
        - `post_str` string that will appear after the progress bar
        '''
        with self._lock:
            if not 0 <= progress < self.total: raise ValueError("Progress value must be between 0 and max_value - 1")
            
            if self._use_dynamic_length: self._update_bar_length()

            # ~~~~~~~~ Perform min-max normalization ~~~~~~~~
            minmax_normalized = (progress + 1) / (self.total) # 0.0 ~ 1.0
            finished_bar      = int(self.bar_length * minmax_normalized)
            perc              = minmax_normalized * 100
            
            elapsed_time           = time.time() - self._start_time
            elapsed_time_formatted = tc.second_to_standard(elapsed_time)

            # ~~~~~~~~ Constructing progress bar ~~~~~~~~
            bar = ''.join([
                self.fill_color, (self.fill_char * finished_bar),
                self.track_color, (self.track_char * (self.bar_length - finished_bar)),
                ta.RESET
            ])
            
            print(f"\r{pre_str} {bar} {perc:.2f}% | Time: {elapsed_time_formatted} {'| ' + post_str if post_str else ''}", end="")
            
            if (self.perc_bkpt and perc % self.perc_bkpt == 0) or perc >= 100: 
                if self.use_interval_time: self._start_time = time.time()
                print(ta.Cursor.SHOW, ta.RESET)
                
            if perc >= 100 and self.completion_callback:
                self.completion_callback()



class MultiLineProgressBar:
    '''
    This class can print each thread's progress.
    
    Example:
    --------
    >>> def task(multi_progress_bar, start, end, bar_index):
    ...     for i in range(start, end):
    ...         time.sleep(random.uniform(0.01, 0.05)) # Simulating work
    ...         multi_progress_bar.update(bar_index, i - start)
    ...
    ... num_threads = 3
    ... total_work  = 100  # Total units of work per thread
    ...
    ... multi_progress_bar = MultiProgressBar(num_threads, total_work)
    ...
    ... # Clear screen and move cursor to top
    ... print("\033[2J\033[H", end="")
    ...
    ... # Creating and starting threads
    ... threads = []
    ... for n in range(num_threads):
    ...     thread = threading.Thread(target=task, args=(multi_progress_bar, 0, total_work, n))
    ...     threads.append(thread)
    ...     thread.start()
    ...
    ... # Waiting for all threads to complete
    ... for thread in threads:
    ...     thread.join()
    ...     
    ... # Move cursor to the line immediately after the last progress bar
    ... multi_progress_bar.finalize()
    '''
    def __init__(self, 
        num_bars:          int, 
        total_work:        float, 
        bar_length:        int      = 50, 
        use_interval_time: bool     = True
    ):
        self.bars = [ProgressBar(
                total             = total_work, 
                bar_length        = bar_length, 
                use_interval_time = use_interval_time
            ) for _ in range(num_bars)]
        self.lock = threading.Lock()
        self.completed_bars = 0  # Track the number of completed bars


    def update(self, bar_index: int, progress: float):
        with self.lock:
            ta.Cursor.save_pos()                # Save cursor position 
            ta.Cursor.set_pos(bar_index + 1, 1) # Move cursor to the correct line 
            self.bars[bar_index].draw(progress) # Update the specific progress bar 
            ta.Cursor.restore_pos()             # Restore cursor position 
            
            # Check if the current progress bar is complete
            if progress >= self.bars[bar_index].total - 1:
                self.completed_bars += 1
                if self.completed_bars == len(self.bars): # finalize on all completion
                    ta.Cursor.set_pos(len(self.bars) + 1, 1)