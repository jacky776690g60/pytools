import queue, threading

__all__ = (
    'NonBlockingStreamReader',
)

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
        self._queue = queue.Queue(maxsize=max_queue_size)
        self._alive = threading.Event()
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
                # Handle or log exception
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