"""
MIT License

Copyright (c) 2024 Mike 'Fuzzy' Partin <mike.partin32@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Standard library imports
import argparse
from inspect import currentframe, getframeinfo


def apgen(d):
    """
    Generates an argparse.ArgumentParser instance based on a provided dictionary configuration.

    Parameters:
    d (dict): A dictionary containing configuration for the argument parser. Expected keys include:
        - description: A string description for the argument parser.
        - groups: A list of dictionaries, each representing an argument group with keys:
            - title: The title of the group.
            - description: The description of the group.
            - arguments: A list of dictionaries, each representing an argument with keys:
                - short: The short option (e.g., '-h').
                - long: The long option (e.g., '--help').
                - type: The type of the argument (e.g., 'int').
                - Other argparse-specific keyword arguments.

    Returns:
    argparse.Namespace: The parsed arguments as a namespace object.
    """
    try:
        frameinfo = getframeinfo(currentframe())  # Get current frame info for debugging
        parser = argparse.ArgumentParser(
            description=d.get("description", "")
        )  # Create argument parser with description

        for group in d.get("groups", []):
            frameinfo = getframeinfo(currentframe())
            g_name = group.pop(
                "title", "parent"
            )  # Get group title or default to 'parent'
            g_desc = group.pop("description", False)  # Get group description

            frameinfo = getframeinfo(currentframe())
            g = None
            if g_name and g_desc and g_name != "parent":
                frameinfo = getframeinfo(currentframe())
                g = parser.add_argument_group(
                    g_name, g_desc
                )  # Add argument group with name and description
            elif g_name and not g_desc and g_name != "parent":
                frameinfo = getframeinfo(currentframe())
                g = parser.add_argument_group(
                    g_name
                )  # Add argument group with name only
            else:
                frameinfo = getframeinfo(currentframe())
                g = parser  # Use parser directly if no group name or description

            for arg in group["arguments"]:
                frameinfo = getframeinfo(currentframe())
                t_short = arg.pop("short", False)  # Get short option
                t_long = arg.pop("long", False)  # Get long option
                t_type = arg.pop("type", False)  # Get type

                frameinfo = getframeinfo(currentframe())
                if t_short and t_short[0] != "-":
                    o_short = f"-{t_short}"  # Ensure short option starts with '-'
                else:
                    o_short = t_short

                frameinfo = getframeinfo(currentframe())
                if t_long and t_long[0:2] != "--":
                    o_long = f"--{t_long}"  # Ensure long option starts with '--'
                else:
                    o_long = t_long

                frameinfo = getframeinfo(currentframe())
                if t_type:
                    arg["type"] = eval(t_type)  # Evaluate type string to actual type

                frameinfo = getframeinfo(currentframe())
                g.add_argument(
                    o_short, o_long, **arg
                )  # Add argument to group or parser
    except Exception as e:
        print(f"{frameinfo.filename}, {frameinfo.lineno}: {e}")
        raise  # Re-raise exception after printing error details

    return parser.parse_args()  # Parse and return arguments


def argparse_constructor(d):
    """
    Constructs an argument parser from a dictionary configuration.

    Parameters:
    d (dict): A dictionary containing configuration for the argument parser.

    Returns:
    argparse.Namespace: The parsed arguments as a namespace object.
    """
    return apgen(d)
