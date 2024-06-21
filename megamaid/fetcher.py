# Stdlib imports
import os
import time
import threading

# debugging information
from inspect import currentframe, getframeinfo

from urllib.parse import urlparse

# Internal imports
from megamaid.utils import *

_S = "\033[0;31m"
_L = "\033[1;33m"
_F = "\033[1;32m"
_E = "\033[0m"

IN = "\033[1;35m>>>\033[0m"
OUT = "\033[1;34m<<<\033[0m"
YAY = "\033[1;36m!!!\033[0m"


class LinkFetcher(threading.Thread):

    def __init__(self, fetch_q, log_q, pattern=False):
        threading.Thread.__init__(self)
        self.fetch_q = fetch_q
        self.log_q = log_q
        self.pattern = pattern

    def fetch(self, site):
        url = urlparse(site)
        # check each element of the path and make sure the directories exist locally
        if not os.path.exists(url.hostname + os.path.dirname(url.path)):
            os.makedirs(url.hostname + os.path.dirname(url.path))
        _fetch = True
        if os.path.isfile(url.hostname + url.path):
            # if the file exists do a HEAD request and check the file sizes match against the local file
            # if the file sizes don't match, download the file
            con_l = int(http_head(site).getheader("Content-Length"))
            loc_l = int(os.stat(url.hostname + url.path).st_size)
            frameinfo = getframeinfo(currentframe())
            if con_l == loc_l:
                _fetch = False

        if _fetch:
            with open(url.hostname + url.path, "wb+") as fp:
                fp.write(http_get(site))

            self.log_q.put(f"DLOAD {site}")

    def run(self):
        while True:
            site = self.fetch_q.get()
            if site == "EXIT":
                return
            self.fetch(site)
