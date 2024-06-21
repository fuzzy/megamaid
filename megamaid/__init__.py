# Stdlib Imports

# Internal Imports

from megamaid.edict import *
from megamaid.utils import *
from megamaid.logger import *
from megamaid.fetcher import *
from megamaid.grabber import *

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
        "license": "MIT",
        "copyright": "2020",
    }
)
