''' This module contains functions/classes related to i/o '''

""" =================================================================
| io.py
|
| Created by Jack on 01/23, 2024
| Copyright © 2024 jacktogon. All rights reserved.
================================================================= """
import os, sys, re, json
from typing import *
from pathlib import Path

from .base import *

__all__ = (
    'read_file_generator', 'write_filebytes', 'JSONLoader'
)

# ===========================================================================
# Classes
# ===========================================================================
class JSONLoader():
    
    @staticmethod
    def read_jsonc(file_path: str, necessary_keys: List[str]=[]) -> Dict:
        '''
        Load json data from .jsonc file
        
        Sample .jsonc:
        ------------
        ```
        {
            "key1": "abc", // comments
            "key2": 123,   /* ... */
            ...
        }
        ```
        '''
        with open(Path(file_path), 'r') as f:
            jsonc_data   = f.read()
            jsonc_data   = re.sub(r"//.*", "", jsonc_data) # //                 
            cleaned_data = re.sub(r"/\*.*?\*/", "", jsonc_data, flags=re.DOTALL) # /* */
            m_json       = json.loads(cleaned_data)
            if necessary_keys:
                #TODO: can only do the first layer right now
                assert all(
                    key in m_json for key in necessary_keys
                ), "Not all keys are presented in the file: {}".format(file_path)
            return m_json
        

# ===========================================================================
# Functions
# ===========================================================================
def read_file_generator(file_path: str, chunk_size: int):
    '''
    Creates a generator and read file path chunk by chunk
    
    Examples:
    ---------
    >>> for _bytes in read_file_generator("abc/large.csv", self.buffer_size)
    ...     print(_bytes)
    ... 
    The 2nd and 3rd parameters from generator are less commonly used.
    But you can do something like this:
    ...
    >>> gen = read_file_generator("~/Desktop/icons.ai", 1024)
    ... chunk1 = next(gen) 
    '''
    file_path = Path(file_path).resolve()
    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk: break
            yield chunk

def write_filebytes(save_path: str, chunk: bytes, append=True):
    '''
    Writing/appending bytes to file efficiently
    
    Params:
    -------
    - `save_path`: path to the file
    - `chunk`: bytes chunk
    - `append`: if false, it willoverwrite the original file 
    
    NOTE:
    -----
    Both modes (writing/appending) consume memory based on the size of chunk.
    
    Examples:
    ---------
    >>> path = Path("/abc/test.txt")
    ... write_filebytes(f"upload/{path.stem}{path.suffix}", mybytes)
    '''
    _save_path = Path(save_path)
    _save_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
    _save_path = _save_path.resolve()
    
    with open(_save_path, 'ab' if append else 'wb') as file:
        file.write(chunk)
        
