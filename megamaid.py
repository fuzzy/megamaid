#!/usr/bin/env python3

# Stdlib imports
import os
import sys
import time
import argparse

from queue import Queue
from inspect import currentframe, getframeinfo

# Internal imports
from megamaid import *

# External imports

# Globals
SITE_Q = Queue()
LINK_Q = Queue()
FETCH_Q = Queue()
LOG_Q = Queue()


def main(args):
    print(args)

    print("Starting SiteScrubber thread")
    link_t = SiteScrubber(SITE_Q, LINK_Q, LOG_Q, args.recursive)
    link_t.start()

    print("Starting LinkFilter thread")
    proxy_t = LinkFilter(LINK_Q, FETCH_Q, LOG_Q, args.pattern)
    proxy_t.start()

    print("Starting LinkFetcher thread")
    fetch_t = LinkFetcher(FETCH_Q, LOG_Q)
    fetch_t.start()

    frameinfo = getframeinfo(currentframe())
    for url in args.urls:
        print(f"{IN}SITE_Q {__name__:20} {frameinfo.lineno:4} {url}")
        SITE_Q.put(url)

    # Give the threads a bit to get started
    time.sleep(2)
    try:
        # drop in our exit signal
        SITE_Q.put("EXIT")
        # and wait for the cleanup
        link_t.join()
        proxy_t.join()
        fetch_t.join()
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
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively fetch files from the same site.",
    )
    parser.add_argument(
        "-tH",
        "--trim-host",
        action="store_true",
        help="Do not create host directory for output.",
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

    main(parser.parse_args())
