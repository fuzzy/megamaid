#!/usr/bin/env python3

# Stdlib imports
import re
import time
import threading
from queue import Empty

# URL and HTML parsing
from urllib.parse import urlparse
from html.parser import HTMLParser

# network clients
from ftplib import FTP, error_reply
from http.client import HTTPSConnection

# Internal imports
from megamaid.utils import *


class LinkParser(HTMLParser):

    site = None
    site_q = None
    link_q = None
    log_q = None
    gui_q = None
    recursive = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            if attrs[0][1].endswith("/") and attrs[0][1] not in ("/", "../"):
                if (
                    self.recursive
                    and not attrs[0][1].startswith("/")
                    and not attrs[0][1].startswith("http")
                    and not attrs[0][1].startswith("mailto")
                    and not attrs[0][1].startswith("ftp")
                ):
                    s = normalize_url(f"{self.site}/{attrs[0][1]}")
                    self.site_q.put(s)
            else:
                url = normalize_url(f"{self.site}/{attrs[0][1]}")
                self.link_q.put(url)
                self.log_q.debug(f"LinkParser().handle_starttag(): {url}")
                self.gui_q.put({"link": 1})


class FtpWalker:

    def __init__(self, uri, link_q, log_q, gui_q):
        self.uri = uri
        self.log_q = log_q
        self.gui_q = gui_q
        self.link_q = link_q

    def walk(self):
        parsed = urlparse(self.uri)
        ftp = FTP(parsed.netloc)
        ftp.login()
        ftp.cwd(parsed.path)
        self._walk(ftp)
        ftp.quit()

    def _walk(self, ftp):
        for item in ftp.nlst():
            try:
                ftp.cwd(item)
                self._walk(ftp)
            except error_reply:
                continue
            except Exception as e:
                self.log_q.debug(
                    f"FtpWalker().walk(): ftp://{ftp.host}{ftp.pwd()}/{item}"
                )
                self.link_q.put(f"ftp://{ftp.host}{ftp.pwd()}/{item}")
                self.gui_q.put({"link": 1})
                continue
            ftp.cwd("..")


class LinkFilter(threading.Thread):

    def __init__(self, link_q, fetch_q, log_q, sig_q, gui_q, pattern=False):
        threading.Thread.__init__(self, daemon=True)
        self.link_q = link_q
        self.fetch_q = fetch_q
        self.log_q = log_q
        self.sig_q = sig_q
        self.gui_q = gui_q
        self.pattern = pattern

    def run(self):
        while True:
            try:
                sig = self.sig_q.get(False)
                self.log_q.info("LinkFilter() thread exit")
                self.sig_q.task_done()
                self.sig_q.put(True)
                return
            except Empty:
                pass

            st = time.time()
            try:
                link = self.link_q.get(True, 10)
                shipit = False
                if self.pattern:
                    for patt in self.pattern:
                        if re.compile(patt).match(link):
                            shipit = True
                elif not self.pattern:
                    shipit = True

                if shipit and type(link) == str:
                    self.log_q.debug(f"LinkFilter().run()[1]: -> FETCH_Q {link}")
                    self.fetch_q.put(link)
                    self.gui_q.put({"match": 1})
                self.link_q.task_done()
            except Empty:
                if time.time() - st >= 15:
                    self.log_q.info("No more work left. LinkFilter thread exiting.")
                    return
                st = time.time()


class SiteScrubber(threading.Thread):

    def __init__(self, site_q, link_q, log_q, sig_q, gui_q, recursive=False):
        threading.Thread.__init__(self, daemon=True)
        self.site_q = site_q
        self.link_q = link_q
        self.log_q = log_q
        self.sig_q = sig_q
        self.gui_q = gui_q
        self.recursive = recursive

    def run(self):
        while True:

            try:
                sig = self.sig_q.get(False)
                self.log_q.info("SiteScrubber() thread exit")
                self.sig_q.task_done()
                self.sig_q.put(True)
                return
            except Empty:
                pass

            st = time.time()
            try:
                st = time.time()
                site = self.site_q.get(True, 5)
                scheme = urlparse(site).scheme
                if scheme in ("http", "https"):
                    parser = LinkParser()
                    parser.site = site
                    parser.site_q = self.site_q
                    parser.link_q = self.link_q
                    parser.log_q = self.log_q
                    parser.gui_q = self.gui_q
                    parser.recursive = self.recursive
                    parser.feed(http_get(site).decode("utf-8"))
                elif scheme == "ftp":
                    worker = FtpWalker(site, self.link_q, self.log_q, self.gui_q)
                    worker.walk()
                self.site_q.task_done()
            except Empty:
                if time.time() - st >= 15:
                    self.log_q.info("No work left. SiteScrubber thread exiting.")
                    return
                st = time.time()
