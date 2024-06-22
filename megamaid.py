#!/usr/bin/env python3

# Stdlib imports
import os
import sys
import time
import logging
import argparse

from queue import Queue, LifoQueue

# Internal imports
from megamaid import *

# External imports

# Globals
SITE_Q = Queue()
LINK_Q = Queue()
FETCH_Q = Queue()
SIG_Q = Queue()
LOG_Q = logging.getLogger("MegaMaid")


def main(args):
    LOG_Q.info("Starting SiteScrubber thread")
    link_t = []
    for i in range(5):
        link_t.append(SiteScrubber(SITE_Q, LINK_Q, LOG_Q, SIG_Q, args.recursive))
        link_t[-1].start()

    LOG_Q.info("Starting LinkFilter thread")
    proxy_t = []
    for i in range(20):
        proxy_t.append(LinkFilter(LINK_Q, FETCH_Q, LOG_Q, SIG_Q, args.pattern))
        proxy_t[-1].start()

    LOG_Q.info("Starting LinkFetcher thread")
    fetch_t = []
    for i in range(1):
        fetch_t.append(LinkFetcher(FETCH_Q, LOG_Q, SIG_Q, args.trim_lead))
        fetch_t[-1].start()

    for url in args.urls:
        LOG_Q.info(f"-> SITE_Q {url}")
        SITE_Q.put(url)

    # Give the threads a bit to get started
    time.sleep(2)
    try:

        SITE_Q.join()
        LINK_Q.join()
        FETCH_Q.join()

        SIG_Q.put(True)

        # Wait for the threads to exit
        for grp in (link_t, proxy_t, fetch_t):
            for t in grp:
                t.join()

    except:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(os.path.basename(__file__))

    parser.add_argument(
        "-p",
        "--pattern",
        metavar="RE",
        type=str,
        default=False,
        nargs="+",
        help="Specify a pattern to match against links.",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output."
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively fetch files from the same site.",
    )
    parser.add_argument(
        "-tL",
        "--trim-lead",
        type=int,
        metavar="N",
        help="Strip `N` leading components from the output path.",
    )

    display = parser.add_mutually_exclusive_group()
    display.add_argument(
        "-t",
        "--tui",
        action="store_true",
        help="Display progress with a TUI dialog. (TODO)",
    )
    display.add_argument(
        "-g",
        "--gui",
        action="store_true",
        help="Display progress with a GUI dialog. (TODO)",
    )

    parser.add_argument(
        "urls", type=str, metavar="URL", nargs="+", help="URL(s) to traverse."
    )

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(filename="megamaid.log", level=logging.DEBUG)
    else:
        logging.basicConfig(filename="megamaid.log", level=logging.INFO)

    main(args)

    # If we aren't debugging get rid of the log
    if not args.debug:
        os.unlink("megamaid.log")
