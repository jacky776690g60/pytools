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
    resolved_path = Path(file_path).resolve()
    write_headers = overwrite

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