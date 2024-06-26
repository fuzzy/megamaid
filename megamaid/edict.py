# Copyright (c) 2024 Mike 'Fuzzy' Partin <mike.partin32@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Edict provides attribute style access to dictionaries and nested dictionaries.
"""


class Edict(dict):
    """
    A dictionary subclass that allows attribute-style access to dictionary keys.
    Nested dictionaries are also converted to Edict instances.
    """

    def __init__(self, **kwargs):
        """
        Initialize the Edict instance.

        Parameters:
        kwargs (dict): Keyword arguments to initialize the dictionary.
        """
        super().__init__()  # Use super() for better compatibility
        self.update(**kwargs)

    def update(self, **kwargs):
        """
        Update the Edict instance with key-value pairs.

        Parameters:
        kwargs (dict): Keyword arguments to update the dictionary.
        """
        for key, value in kwargs.items():
            if isinstance(value, dict):  # Use isinstance() for type checking
                value = Edict(**value)
            super().__setitem__(key, value)  # Use super() for item setting

    def __getattr__(self, key):
        """
        Get an attribute from the Edict instance.

        Parameters:
        key (str): The key to access the value.

        Returns:
        The value associated with the key.

        Raises:
        AttributeError: If the key does not exist in the dictionary.
        """
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'Edict' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        """
        Set an attribute in the Edict instance.

        Parameters:
        key (str): The key to set the value.
        value: The value to set.
        """
        if key in self.__dict__:  # Check if key is in instance attributes
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __delattr__(self, key):
        """
        Delete an attribute from the Edict instance.

        Parameters:
        key (str): The key to delete.
        """
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"'Edict' object has no attribute '{key}'")
