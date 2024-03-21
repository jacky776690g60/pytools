'contains tools for interacting with shell/cmd prompt'

""" =================================================================
| pytools/shell.py
|
| Created by Jack on 01/24, 2024
| Copyright © 2024 jacktogon. All rights reserved.
================================================================= """
import os
import subprocess
import queue, threading
from typing import *

from .base import TermArtist as ta

__all__ = (
    'get_valid_input', 
    'NonBlockingStreamReader',
    'PersistentShell',
)

def get_valid_input(
    prompt:     str,
    validator:  Callable[[str], bool],
    transform:  Callable[[str], Any]    = str
) -> Any | None:
    """
    1. Get user input 
    2. validate it using a callback
    3. return the result.

    Params:
    -------
    - `prompt`:    The question or prompt to display to the user.
    - `validator`: A callback function that validates the user's input.
        * It should return `True`; `False` if it's not.
    - `transform`: A callback function to transform the user's input.
        * By default, it converts the input to a string.

    Returns:
    --------
    - Transformed user input.

    Examples:
    ---------
    >>> get_valid_input(
    ...     prompt    = "Give a positive int: ",
    ...     validator = lambda x: x > 0 
    ...     transform = int
    ... )
    """
    user_input        = input(prompt)
    transformed_input = transform(user_input)
    return transformed_input if validator(transformed_input) else None


# =================================================
# Classes
# =================================================
class NonBlockingStreamReader:
    '''
    use threading to read stdin
    
    Examples:
    ---------
    >>> nbsr = NonBlockingStreamReader(sys.stdin)
    ... try:
    ...     while True:
    ...         # Do your stuff here
    ...         # Check for new stdin line
    ...         input_line = nbsr.read()
    ...         if input_line:
    ...             print(f"Received input: {input_line.strip()}")
    ...             # Clear the input after processing
    ...             nbsr._input = None
    ...
    ...         # Rest of your loop here
    ...
    ... except KeyboardInterrupt:
    ...     # Stop the reader thread when done
    ...     nbsr.stop()
    '''
    
    # =============================
    # dunders
    # =============================
    def __init__(self, stream, max_queue_size=1000):
        self._stream = stream
        self._queue  = queue.Queue(maxsize=max_queue_size)
        self._alive  = threading.Event()
        self._alive.set()
        self._thread = threading.Thread(target=self._reader_thread, daemon=True)
        self._thread.start()
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        
    # =============================
    # private
    # =============================
    def _reader_thread(self):
        while self._alive.is_set():
            try:
                line = self._stream.readline()
                if line:
                    self._queue.put(line.strip(), timeout=0.1)
            except Exception as e:
                pass

    # =============================
    # public
    # =============================
    def read(self, timeout=None) -> str:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        self._alive.clear()
        self._thread.join()

    def read_blocking(self) -> str:
        '''
        read from the stream in a blocking manner
        '''
        return self._stream.readline().strip()
    


class PersistentShell:
    '''
    Works on bash and Powershell
    
    Examples:
    ---------
    >>> pe = PersistentShell()
    ... print(pe.run_command("cd /tmp"))
    ... print(pe.run_command("pwd"))
    ... pe.close()
    '''
    
    # =============================
    # dunders
    # =============================
    def __init__(self, debug=False):
        self.debug   = debug
        self.os_name = os.name
        self.output_queue = queue.Queue()
        
        if self.os_name == 'posix': self.args = ["/bin/bash"]      # macOS, linux
        elif self.os_name == 'nt':  self.args = ["powershell.exe"] # windows
        self.process = subprocess.Popen(
            args    = self.args,
            stdin   = subprocess.PIPE, 
            stdout  = subprocess.PIPE, 
            stderr  = subprocess.STDOUT, 
            text    = True,               # the input and output will be handled as string
            bufsize = 1                   # allow reading process output line by line (\n) instead of waiting for the large chunk
        )
        
        self.__start_output_thread()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    # =============================
    # private
    # =============================
    def __start_output_thread(self):
        def enqueue_output():
            try:
                for line in iter(self.process.stdout.readline, ''):
                    self.output_queue.put(line)
            except Exception as e:
                self.__error(f"Error reading output: {e}")
            finally:
                self.process.stdout.close()

        self.output_thread        = threading.Thread(target=enqueue_output)
        self.output_thread.daemon = True
        self.output_thread.start()
        
        
    def __debug(self, *val):
        message = ' '.join(str(v) for v in val)
        if self.debug: print(f"{ta.FG.BRIGHT_YELLOW}{message}{ta.RESET}")
        
    def __error(self, *val):
        message = ' '.join(str(v) for v in val)
        print(f"{ta.FG.BRIGHT_RED}{message}{ta.RESET}")
    
    # =============================
    # public
    # =============================
    def run_command(self, command: str) -> str | None:
        command         = command.strip()
        end_marker      = "END_OF_COMMAND"
        cmd_with_marker = f"{command}; echo {end_marker}\n"
        
        try:
            self.__debug("Running command")
            self.process.stdin.write(cmd_with_marker)
            self.__debug("Flushing stdin")
            self.process.stdin.flush()

            output = ""
            self.__debug("reading stdout lines...")
            while True:
                try:
                    line = self.output_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                if end_marker in line:
                    self.__debug("-- end marker reached in stdout --")
                    break
                output += line

            self.__debug("Command Output:\n" + output)
            self.__debug("command end")
            return output if output else None
        
        except Exception as e:
            self.__error(f"Error executing command: {e}")
            return "Error in PersistentShell"
    
    
    def close(self):
        try:
            self.process.stdin.close()
            self.process.terminate()
            self.process.wait(timeout=5)
        except Exception as e:
            print(f"Error closing shell: {e}")
            self.process.kill()


