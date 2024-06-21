# Stdlib imports
import os
import time
import threading

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

    def __init__(self, fetch_q, log_q, chop_l=False):
        threading.Thread.__init__(self)
        self.fetch_q = fetch_q
        self.log_q = log_q
        if chop_l and type(chop_l) is int:
            self.chop_l = chop_l
        else:
            self.chop_l = False

    def fetch(self, site):
        url = urlparse(site)
        _fetch = True
        tfn = url.hostname + url.path
        if self.chop_l:
            ofn = f'./{"/".join(tfn.split("/")[self.chop_l:])}'
        else:
            ofn = tfn

        if not os.path.exists(os.path.dirname(ofn)):
            os.makedirs(os.path.dirname(ofn))

        if os.path.isfile(ofn):
            con_l = int(http_head(site).getheader("Content-Length"))
            loc_l = int(os.stat(ofn).st_size)
            if con_l == loc_l:
                _fetch = False

        if _fetch:
            with open(ofn, "wb+") as fp:
                fp.write(http_get(site))

            sz = humanize_bytes(os.stat(ofn).st_size)
            self.log_q.put(f"Saved {ofn} ({sz})")

    def run(self):
        while True:
            site = self.fetch_q.get()
            if site == "EXIT":
                return
            self.fetch(site)
