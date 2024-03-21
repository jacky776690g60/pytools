#!/usr/bin/env python3

''' =================================================================
| healthcheck.py -- pytools/healthcheck.py
|
| Created by Jack on 07/11/2023
| Copyright © 2023 jacktogon. All rights reserved.
================================================================= '''
from typing import List
import shutil
# import psutil

__all__ = (
    'get_disk_usage',
)

def get_disk_usage(path="/") -> float:
    '''
    Get the disk usage percentage of a specified disk.

    Params:
    -------
    - `path`: The disk/path for which the usage percentage is to be calculated.

    Returns:
    --------
    - The disk usage percentage.
    '''
    disk_usage    = shutil.disk_usage(path)
    usage_percent = (disk_usage.used / disk_usage.total) * 100
    return usage_percent


# def get_cpu_usage(sec=0.1, percpu=True) -> List[float]:
#     '''
#     Get the CPU usage percentage.

#     Params:
#     -------
#     - `sec`: The interval in seconds to calculate the CPU usage over.
#     - `percpu`: If True, returns a list of CPU usage percentages for each CPU core. 
#                 If False, returns the overall CPU usage percentage.

#     Returns:
#     float or list: The CPU usage percentage(s).
#     '''
#     cpu_usage = psutil.cpu_percent(interval=sec, percpu=percpu)
#     return cpu_usage


# =============================
# Main
# =============================
if __name__ == "__main__":
    print("Disk Usage: {:.2f}%".format(get_disk_usage("/")))
