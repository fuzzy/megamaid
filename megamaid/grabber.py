#!/usr/bin/env python3

# Stdlib imports
import re
import threading

# URL and HTML parsing
from urllib.parse import urlparse
from html.parser import HTMLParser

# network clients
from ftplib import FTP, error_reply
from http.client import HTTPSConnection

# Internal imports
from megamaid.utils import *

_S = "\033[0;31m"
_L = "\033[1;33m"
_F = "\033[1;32m"
_C = "\033[1;36m"
_E = "\033[0m"

IN = "\033[1;35m>>>\033[0m"
OUT = "\033[1;34m<<<\033[0m"
YAY = "\033[1;36m!!!\033[0m"


class LinkParser(HTMLParser):

    site = None
    site_q = None
    link_q = None
    log_q = None
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


# a class that takes a ftp URI, parses it, and beings to walk
# the ftp site recursively from that point and send all
# links to files into a queue, including the full URI


class FtpWalker:

    def __init__(self, uri, link_q):
        self.uri = uri
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
                self.link_q.put(f"ftp://{ftp.host}{ftp.pwd()}/{item}")
                continue
            ftp.cwd("..")


class LinkFilter(threading.Thread):

    def __init__(self, link_q, fetch_q, log_q, pattern=False):
        threading.Thread.__init__(self)
        self.link_q = link_q
        self.fetch_q = fetch_q
        self.log_q = log_q
        self.pattern = pattern

    def run(self):
        while True:
            link = self.link_q.get()
            if link == "EXIT":
                self.link_q.put("EXIT")
                self.fetch_q.put("EXIT")
                return
            if self.pattern:
                for patt in self.pattern:
                    if re.compile(patt).match(link):
                        self.log_q.put(
                            {"level": "debug", "message": f"-> FETCH_Q {link}"}
                        )
                        self.fetch_q.put(link)
            elif not self.pattern:
                self.log_q.put({"level": "debug", "message": f"-> FETCH_Q {link}"})
                self.fetch_q.put(link)


class SiteScrubber(threading.Thread):

    def __init__(self, site_q, link_q, log_q, recursive=False):
        threading.Thread.__init__(self)
        self.site_q = site_q
        self.link_q = link_q
        self.log_q = log_q
        self.recursive = recursive

    def run(self):
        while True:
            site = self.site_q.get()
            scheme = urlparse(site).scheme
            if scheme in ("http", "https"):
                parser = LinkParser()
                if site == "EXIT":
                    self.site_q.put("EXIT")
                    self.link_q.put("EXIT")
                    return
                parser.site = site
                parser.site_q = self.site_q
                parser.link_q = self.link_q
                parser.log_q = self.log_q
                parser.recursive = self.recursive
                parser.feed(http_get(site).decode("utf-8"))
            elif scheme == "ftp":
                worker = FtpWalker(site, self.link_q)
                worker.walk()
