#!/usr/bin/env python3

# Stdlib imports
import time
import curses
import threading
from queue import Empty

# Internal imports
from megamaid.edict import *
from megamaid.utils import *


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
        self.stats = Edict(
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
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(12, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(13, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(14, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(15, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(16, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(17, curses.COLOR_WHITE, curses.COLOR_BLACK)

    def _draw_stats_box(self):
        (y, x) = self._stdscr.getmaxyx()
        hpad = self.shoulders.horizLine * (x - 3)
        ehpad = " " * (x - 3)
        self._stdscr.addstr(
            y - 9,
            1,
            f"{self.shoulders.upperLeft}{hpad}{self.shoulders.upperRight}",
            curses.color_pair(13),
        )
        for n in range(1, 8):
            self._stdscr.addstr(
                y - (9 - n),
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
        while len(self.stats.lines) > (y - 11):
            self.stats.lines.pop(0)
        idx = 2
        for line in self.stats.lines:
            try:
                padd = " " * (x - (len(line) + 2))
                self._stdscr.addstr(idx, 1, line + padd)
                idx += 1
            except TypeError as e:
                raise

    def _draw_stats(self):
        (y, x) = self._stdscr.getmaxyx()
        cols = int((x - 6) / 3)
        self._stdscr.addstr(y - 7, 3, f"Total Fetched: ")
        self._stdscr.addstr(
            f"{self.stats.have} {humanize_bytes(self.stats.size):<10}",
            curses.color_pair(16),
        )
        self._stdscr.addstr(y - 7, cols, f"Indexing sites: ")
        self._stdscr.addstr(str(self.stats.site), curses.color_pair(16))
        self._stdscr.addstr(y - 7, cols * 2, f"Links found / matched: ")
        self._stdscr.addstr(f"{str(self.stats.link):^6}", curses.color_pair(16))
        self._stdscr.addstr(" / ")
        self._stdscr.addstr(f"{str(self.stats.match):^6}", curses.color_pair(16))

    def draw_screen(self):
        self._stdscr.clear()
        self._draw_stats_box()
        self._draw_entries()
        self._draw_stats()
        self._stdscr.refresh()

    def _update_status(self, status):
        for k, v in status.items():
            if k == "filename":
                self.stats.lines.append(v)
            elif k in self.stats.keys():
                self.stats[k] += v

    def run(self):
        stamp = time.time()
        while True:
            try:
                self._sig_q.get(False)
                self._log.info("Tui() thread exit")
                self._sig_q.task_done()
                self._sig_q.put(True)
                return
            except Empty:
                pass

            try:
                update = self._event_q.get()
                # self._update_status(update)
                if time.time() - stamp >= 2:
                    self.draw_screen()
                    stamp = time.time()
                self.draw_screen()
            except Empty:
                pass
