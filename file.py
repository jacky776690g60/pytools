""" =================================================================
| file.py  --  Projects/pytools/file.py
|
| #Author Jack
| Created on 03/21, 2024
| Copyright © 2024 jacktogon. All rights reserved.
================================================================= """

import os, csv, re, json
from pathlib import Path
from typing import Any, List, Tuple, Union, Callable, Literal, Dict

from .base import *

__all__ = (
    'read_file_generator', 'JSONLoader', 
    'write_filebytes', 'write_to_csv'
)
            
# ===========================================================================
# Classes
# ===========================================================================
class JSONLoader():
    '''Handle Tasks about JSON'''
    
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
    - `chunk`:     bytes chunk
    - `append`:    if false, it willoverwrite the original file 
    
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


def write_to_csv(
    headers:        List[str], 
    row_values:     List[Any], 
    file_path:      str, 
    overwrite:      bool = False,
) -> None:
    """
    Writes data to a CSV file.

    Params:
    -------
    - `headers`:    List of headers for the CSV file.
    - `row_values`: List of values to be written as a row in the CSV.
    - `file_path`:  The path of the file where data is to be written.
    - `overwrite`:  If True, the file will be overwritten. If False, data will be appended.
    """
    resolved_path = Path(file_path).resolve()
    write_headers = overwrite
    
    # Ensure the directory exists
    os.makedirs(resolved_path.parent, exist_ok=True)

    if not overwrite and not os.path.exists(resolved_path):
        write_headers = True
    elif not overwrite and os.path.getsize(resolved_path) > 0:
        with open(resolved_path, 'r', newline='') as file:
            existing_header = next(csv.reader(file), None)
            write_headers = existing_header != headers


    if write_headers:
        with open(resolved_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)


    mode = 'w' if overwrite else 'a'
    with open(resolved_path, mode, newline='') as file:
        writer = csv.writer(file)
        if not write_headers and not overwrite:
            # Append the row if the headers were not written and not overwriting
            writer.writerow(row_values)
        elif overwrite:
            # Overwrite the file with headers and the new row
            writer.writerow(row_values)