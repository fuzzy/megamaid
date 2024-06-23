#!/usr/bin/env python3

# Stdlib imports
import os
import sys
import time
import curses
import logging
import argparse
import threading

from queue import Queue, LifoQueue

# Internal imports
from megamaid import *

# External imports

# Globals
SITE_Q = Queue()
LINK_Q = Queue()
FETCH_Q = Queue()
GUI_Q = Queue()
SIG_Q = Queue()
LOG_Q = logging.getLogger("MegaMaid")

STATS = Edict(
    **{
        "site": 0,
        "link": 0,
        "match": 0,
        "fetch": 0,
        "have": 0,
        "size": 0,
        "speed": 0,
        "lines": [],
    }
)


class Updater(threading.Thread):

    def __init__(self, event_q, sig_q, log):
        threading.Thread.__init__(self, daemon=True)
        self._event_q = event_q
        self._sig_q = sig_q
        self._log = log

    def run(self):
        while True:
            try:
                self._sig_q.get(False)
                self._log.info("Updater() thread exit")
                self._sig_q.task_done()
                self._sig_q.put(True)
                return
            except Empty:
                pass

            try:
                update = self._event_q.get(False)
                for k, v in update.items():
                    if k == "filename":
                        STATS.lines.append(v)
                    elif k in STATS.keys():
                        STATS[k] += v
            except Empty:
                pass


class Tui:

    def __init__(self, stdscr, event_q, sig_q, log):
        self._stdscr = stdscr
        self.shoulders = Edict(
            **{
                "upperLeft": "╔",
                "upperRight": "╗",
                "lowerLeft": "╚",
                "lowerRight": "╝",
                "horizLine": "═",
                "vertLine": "║",
                "leftMiddle": "╠",
                "rightMiddle": "╣",
                "topMiddle": "╦",
                "bottomMiddle": "╩",
                "middleMiddle": "╬",
            }
        )
        self._sig_q = sig_q
        self._event_q = event_q
        self._log = log
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(12, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(13, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(14, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(15, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(16, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(17, curses.COLOR_WHITE, curses.COLOR_BLACK)
        # progress bar colors
        curses.init_pair(20, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(21, curses.COLOR_CYAN, curses.COLOR_CYAN)
        self._draw_stats_box()

    def _draw_stats_box(self):
        (y, x) = self._stdscr.getmaxyx()
        hpad = self.shoulders.horizLine * (x - 3)
        ehpad = " " * (x - 3)
        self._stdscr.addstr(
            y - 3,
            1,
            f"{self.shoulders.upperLeft}{hpad}{self.shoulders.upperRight}",
            curses.color_pair(13),
        )
        for n in range(1, 2):
            self._stdscr.addstr(
                y - (3 - n),
                1,
                f"{self.shoulders.vertLine}{ehpad}{self.shoulders.vertLine}",
                curses.color_pair(13),
            )
        try:
            self._stdscr.addstr(
                y - 1,
                1,
                f"{self.shoulders.lowerLeft}{hpad}{self.shoulders.lowerRight}",
                curses.color_pair(13),
            )
        except curses.error:
            pass

    def _draw_entries(self):
        (y, x) = self._stdscr.getmaxyx()
        self._stdscr.addstr(0, 0, "MegaMaid", curses.color_pair(13))
        self._stdscr.addstr(1, 0, self.shoulders.horizLine * x, curses.color_pair(13))
        while len(STATS.lines) > (y - 5):
            STATS.lines.pop(0)
        idx = 2
        for line in STATS.lines:
            try:
                padd = " " * (x - (len(line) + 2))
                if line.find("(pre)") != -1:
                    self._stdscr.addstr(idx, 1, line + padd, curses.color_pair(16))
                else:
                    self._stdscr.addstr(idx, 1, line + padd)
                idx += 1
            except TypeError as e:
                raise

    def _draw_stats(self):
        (y, x) = self._stdscr.getmaxyx()
        self._stdscr.addstr(y - 3, 3, f"[ Links: Found ")
        self._stdscr.addstr(f"{str(STATS.link):^6}", curses.color_pair(16))
        self._stdscr.addstr(" / ")
        self._stdscr.addstr("Matched ")
        self._stdscr.addstr(f"{str(STATS.match):^6}", curses.color_pair(16))
        self._stdscr.addstr(" / ")
        self._stdscr.addstr("Have ")
        self._stdscr.addstr(f"{str(STATS.have):^6}", curses.color_pair(16))
        self._stdscr.addstr(" ]")

    def _draw_progress(self):
        (y, x) = self._stdscr.getmaxyx()
        if STATS.match > 0 and STATS.have > 0:
            perc = int((float(STATS.have) / float(STATS.match)) * 100.0)
        else:
            perc = 0
        psze = int((x - 9) * (perc / 100))
        ppad = " " * (x - (20 + psze))
        self._stdscr.addstr(y - 2, 3, f"{perc:3}% ")
        self._stdscr.addstr(y - 2, 8, " " * psze, curses.color_pair(21))
        self._stdscr.addstr(ppad, curses.color_pair(20))
        self._stdscr.addstr(f" {humanize_bytes(STATS.size):^10}")

    def draw_screen(self):
        self._draw_stats_box()
        self._draw_entries()
        self._draw_stats()
        self._draw_progress()
        self._stdscr.refresh()

    def run(self):
        stamp = time.time()
        while True:
            try:
                self._sig_q.get(True, 0.25)
                self._log.info("Tui() thread exit")
                self._sig_q.task_done()
                self._sig_q.put(True)
                return
            except Empty:
                pass

            try:
                if float(time.time()) - float(stamp) >= 0.5:
                    self.draw_screen()
                    stamp = time.time()
            except Empty:
                pass


def tui(stdscr):
    tui = Tui(stdscr, GUI_Q, SIG_Q, LOG_Q)
    tui.run()


def main(args):
    # Preseed the queue with the URLs and data
    for url in args.urls:
        LOG_Q.info(f"-> SITE_Q {url}")
        SITE_Q.put(url)
        GUI_Q.put({"site": 1})

    LOG_Q.info("Starting Updater thread")
    updater_t = Updater(GUI_Q, SIG_Q, LOG_Q)
    updater_t.start()

    LOG_Q.info("Starting SiteScrubber thread")
    link_t = []
    for i in range(1):
        link_t.append(SiteScrubber(SITE_Q, LINK_Q, LOG_Q, SIG_Q, GUI_Q, args.recursive))
        link_t[-1].start()

    LOG_Q.info("Starting LinkFilter thread")
    proxy_t = []
    for i in range(1):
        proxy_t.append(LinkFilter(LINK_Q, FETCH_Q, LOG_Q, SIG_Q, GUI_Q, args.pattern))
        proxy_t[-1].start()

    LOG_Q.info("Starting LinkFetcher thread")
    fetch_t = LinkFetcher(FETCH_Q, LOG_Q, SIG_Q, GUI_Q, args.trim_lead)
    fetch_t.start()

    if args.tui:
        curses.wrapper(tui)

    # Give the threads a bit to get started
    time.sleep(2)
    try:

        SITE_Q.join()
        LINK_Q.join()
        FETCH_Q.join()

        SIG_Q.put(True)

        # Wait for the threads to exit
        for grp in (link_t, proxy_t, fetch_t, updater_t):
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

    # compress = parser.add_mutually_exclusive_group("Compression")
    # compress.add_argument(
    #     "-z",
    #     "--zlib",
    #     action="store_true",
    #     help="Compress any uncompressed files fetched, with zlib (gz)",
    # )
    # compress.add_argument("-b")

    display = parser.add_mutually_exclusive_group()
    display.add_argument(
        "-t",
        "--tui",
        action="store_true",
        help="Display progress with a TUI dialog. (TODO)",
    )
    # display.add_argument(
    #     "-g",
    #     "--gui",
    #     action="store_true",
    #     help="Display progress with a GUI dialog. (TODO)",
    # )

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
