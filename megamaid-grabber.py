#!/usr/bin/env python3

# Stdlib imports
import os
import sys

# Internal imports
from megamaid import *

# Globals

LOG = log_setup("Main")


def main():
    args_d = dict(
        description="MegaMaid",
        version=f"{METADATA.version}.{METADATA.patchlevel}",
        author=METADATA.author,
        license=METADATA.license,
        groups=[
            {
                "arguments": [
                    {
                        "action": "version",
                        "help": "Show version information",
                        "long": "version",
                        "short": "v",
                        "version": f"%(prog)s v{METADATA.version}.{METADATA.patchlevel}",
                    }
                ]
            },
            {
                "arguments": [
                    {
                        "help": "Use UNIX domain sockets (/tmp/megamaid-grabber.sock)",
                        "long": "unix",
                        "metavar": "FNAME",
                        "short": "u",
                        "default": f"/tmp/megamaid-grabber.sock",
                        "type": "str",
                    },
                    {
                        "help": "Host and port for binding tcp sockets (0.0.0.0:9765)",
                        "long": "bind",
                        "metavar": "HOST:PORT",
                        "short": "b",
                        "default": "0.0.0.0:9765",
                        "type": "int",
                    },
                ],
                "mutually_exclusive": True,
                "title": "Server",
            },
            {
                "arguments": [
                    {
                        "action": "store_true",
                        "help": "Only log errors.",
                        "long": "quiet",
                        "short": "q",
                    },
                    {
                        "action": "store_true",
                        "help": "Excessively log everything.",
                        "long": "debug",
                        "short": "d",
                    },
                ],
                "mutually_exclusive": True,
                "title": "Logging",
            },
        ],
    )

    args = argparse_constructor(args_d)
    LOG.info("Starting MegaMaid")


if __name__ == "__main__":
    main()
