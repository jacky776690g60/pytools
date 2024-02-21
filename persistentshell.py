import os
import subprocess
import queue, threading

# ~~~~~~~~ same directory import  ~~~~~~~~
from .logger import Logger, LogLevel

__all__ = (
    'PersistentShell',
)

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


