# Stdlib imports
import os
import threading
from queue import Empty

from urllib.parse import urlparse

# Internal imports
from megamaid.utils import *


class LinkFetcher(threading.Thread):

    def __init__(self, fetch_q, log_q, sig_q, chop_l=False):
        threading.Thread.__init__(self, daemon=True)
        self.fetch_q = fetch_q
        self.log_q = log_q
        self.sig_q = sig_q
        if chop_l and type(chop_l) is int:
            self.chop_l = chop_l
        else:
            self.chop_l = False

    def fetch(self, site):
        url = urlparse(site)
        _fetch = True
        try:
            tfn = url.hostname + url.path
        except TypeError:
            self.log_q.put(f"Failed to parse {site}")
            return

        if self.chop_l:
            ofn = f'./{"/".join(tfn.split("/")[self.chop_l:])}'
        else:
            ofn = tfn

        if not os.path.exists(os.path.dirname(ofn)):
            os.makedirs(os.path.dirname(ofn))

        if os.path.isfile(ofn):
            if url.scheme in ("http", "https"):
                con_l = int(http_head(site).getheader("Content-Length"))
                loc_l = int(os.stat(ofn).st_size)
                if con_l == loc_l:
                    _fetch = False

        if _fetch:
            with open(ofn, "wb+") as fp:
                if url.scheme in ("http", "https"):
                    fp.write(http_get(site))
                elif url.scheme == "ftp":
                    ftp_get(site, fp)

    def run(self):
        while True:
            try:
                sig = self.sig_q.get(True, 0.1)
                self.log_q.info("LinkFetcher() thread exit")
                self.sig_q.task_done()
                self.sig_q.put(True)
                return
            except Empty:
                pass

            try:
                site = self.fetch_q.get(True, 0.1)
                self.fetch(site)
                self.fetch_q.task_done()
                self.log_q.info(
                    f"LinkFetcher().fetch(): Saved {os.path.basename(site)}"
                )
            except Empty:
                pass
