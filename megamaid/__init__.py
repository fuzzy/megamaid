# Stdlib Imports

# Internal Imports

from megamaid.apgen import *
from megamaid.edict import *
from megamaid.utils import *
from megamaid.fetcher import *
from megamaid.grabber import *

# interface imports
# from megamaid.tui import *

# External Imports

# Globals

IN = "\033[1;32m>>>\033[0m"
OUT = "\033[1;33m<<<\033[0m"

METADATA = Edict(
    **{
        "program": "MegaMaid",
        "version": "0.1",
        "patchlevel": "0",
        "author": "Mike 'Fuzzy' Partin",
        "email": "mike.partin32@gmail.com",
        "license": "MIT",
        "copyright": "2024",
    }
)
