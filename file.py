import os, csv
from pathlib import Path
from typing import Any, List, Tuple, Union, Callable, Literal

__all__ = 'write_to_csv',

def write_to_csv(
    headers:    List[str], 
    row_values: List[Any], 
    file_path:  str, 
    overwrite:  bool=False):
    """
    Writes data to a CSV file.

    Params:
    -------
    - `headers`:    List of headers for the CSV file.
    - `row_values`: List of values to be written as a row in the CSV.
    - `file_path`:  The path of the file where data is to be written.
    - `overwrite`:  If True, the file will be overwritten. If False, data will be appended.
    """
    mode = 'w' if overwrite else 'a'

    with open(Path(file_path).resolve(), mode, newline='') as file:
        writer = csv.writer(file)

        if overwrite or not os.path.getsize(file_path): writer.writerow(headers)
        writer.writerow(row_values)