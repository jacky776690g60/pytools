#!/usr/bin/env python3

""" =================================================================
| foldertree.py -- tools/foldertree.py
|
| Created by Jack on 07/11/2023
| Copyright © 2023 jacktogon. All rights reserved.
================================================================= """

import os, argparse
from pathlib import Path
from typing import *

__all__ = (
    'get_folderTree_list',
)

__SPACE = ' ' * 3

def get_folderTree_list(
    root_dir:       Union[str, Path], 
    prefix:         str              = "", 
    subdir_prefix:  str              = "|-- ", 
    file_prefix:    str              = "|-- ",
    excluded_dirs:  Set[str]         = set(), 
    excluded_files: Set[str]         = set()
) -> List[str]:
    
    root_dir = Path(root_dir).expanduser()  # Ensure root_dir is a Path object
    entries = list(root_dir.iterdir())
    dirs, files = [], []

    for entry in entries:
        entry_name = entry.name
        if entry_name in excluded_dirs or entry_name in excluded_files:
            continue

        if entry.is_dir():
            dirs.append(entry_name)
        elif entry.is_file():
            files.append(entry_name)
        else: # symbolic links, sockets, and special device files (in Unix-like systems)
            continue

    res = []

    for dir in sorted(dirs):
        res.append(f"{prefix}{subdir_prefix}{dir}/")
        res.extend(
            get_folderTree_list(
                root_dir / dir, 
                prefix + f"|{__SPACE}", 
                subdir_prefix, 
                file_prefix, 
                excluded_dirs, 
                excluded_files
            )
        )

    for file in sorted(files):
        res.append(f"{prefix}{file_prefix}{file}")
    
    return res



# =============================
# Sample Entries
# =============================
def __main():
    parser = argparse.ArgumentParser(description='Display an indented tree representation of a directory and its contents.')
    parser.add_argument('-d', '--directory', type=str, required=True, help='The root directory')
    parser.add_argument('-ef', '--excludefolders', nargs='*', default=[".git", "__pycache__"], help='Folders to exclude')
    parser.add_argument('-efl', '--excludefiles', nargs='*', default=[".DS_Store"], help='Files to exclude')
    args   = parser.parse_args()

    excluded_folders = set(args.excludefolders)
    excluded_files   = set(args.excludefiles)
    root_directory   = args.directory
    project_name     = os.path.basename(os.path.normpath(root_directory))
    
    result = [f"/{project_name}"] + get_folderTree_list(root_directory, excluded_dirs=excluded_folders, excluded_files=excluded_files)
    print("\n".join(result))


# =============================
# Entry
# =============================
if __name__ == '__main__':
    __main()
