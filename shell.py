'contains tools for interacting with shell/cmd prompt'

""" =================================================================
| shell.py
|
| Created by Jack on 01/24, 2024
| Copyright © 2024 jacktogon. All rights reserved.
================================================================= """
import os
import subprocess
import queue, threading
from typing import *

from .logger import Logger, LogLevel

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

    Parameters:
    - `prompt`: The question or prompt to display to the user.
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
    >>> shell = PersistentShell()
    ... print(shell.run_command("cd /tmp"))
    ... print(shell.run_command("pwd"))
    ... shell.close()
    '''
    
    # =============================
    # dunders
    # =============================
    def __init__(self, debug_mode=False):
        self.os_name = os.name
        
        if self.os_name == 'posix':     # macOS, linux
            self.args = ["/bin/bash"]
        elif self.os_name == 'nt':      # windows
            self.args = ["powershell.exe"]
        
        self.process = subprocess.Popen(
            args     =  self.args,
            stdin    =  subprocess.PIPE, 
            stdout   =  subprocess.PIPE, 
            stderr   =  subprocess.STDOUT, 
            text     =  True,               # the input and output will be handled as string
            bufsize  =  1                   # allow reading process output line by line (\n) instead of waiting for the large chunk
        )
        
        self.output_queue = queue.Queue()
        self.__start_output_thread()
        
        
        self.logger = Logger(LogLevel.DEBUG if debug_mode else LogLevel.ERROR)
        
        
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
                self.logger.error(f"Error reading output: {e}")
            finally:
                self.process.stdout.close()

        self.output_thread = threading.Thread(target=enqueue_output)
        self.output_thread.daemon = True
        self.output_thread.start()
        
    
    # =============================
    # public
    # =============================
    def run_command(self, command: str) -> str:
        command = command.strip()
        end_marker = "END_OF_COMMAND"
        command_with_marker = f"{command}; echo {end_marker}\n"
        
        try:
            self.logger.debug("Running command")
            self.process.stdin.write(command_with_marker)
            self.logger.debug("flushing stdin")
            self.process.stdin.flush()

            output = ""
            self.logger.debug("reading stdout lines...")
            while True:
                try:
                    line = self.output_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                if end_marker in line:
                    self.logger.debug("-- end marker reached in stdout --")
                    break
                output += line

            self.logger.debug("command output:\n" + output)
            self.logger.debug("command end")
            return output if output else ' '
        
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return "Error"
    
    
    def close(self):
        try:
            self.process.stdin.close()
            self.process.terminate()
            self.process.wait(timeout=5)
        except Exception as e:
            self.logger.error(f"Error closing shell: {e}")
            self.process.kill()


