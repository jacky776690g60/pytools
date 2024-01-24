'contains tools for interacting with shell/cmd prompt'

""" =================================================================
| shell.py
|
| Created by Jack on 01/24, 2024
| Copyright © 2024 jacktogon. All rights reserved.
================================================================= """

from typing import *

__all__ = 'get_valid_input', 

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