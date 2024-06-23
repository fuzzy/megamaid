# Stdlib imports
import os
import threading
from queue import Empty

from urllib.parse import urlparse

# Internal imports
from megamaid.utils import *
from megamaid.edict import *


class LinkFetcher(threading.Thread):

    def __init__(self, fetch_q, log_q, sig_q, gui_q, chop_l=False):
        threading.Thread.__init__(self, daemon=True)
        self.fetch_q = fetch_q
        self.log_q = log_q
        self.sig_q = sig_q
        self.gui_q = gui_q
        if chop_l and type(chop_l) is int:
            self.chop_l = chop_l
        else:
            self.chop_l = False

    def fetch(self, site):
        _fetch = True
        exists = False
        ofn = ""
        try:
            url = urlparse(site)
        except TypeError:
            self.log_q.error(f"Failed to parse {site}")
            return False

        if self.chop_l:
            tfn = url.hostname + url.path
            ofn = f'./{"/".join(tfn.split("/")[self.chop_l:])}'
        else:
            ofn = url.hostname + url.path

        if not os.path.exists(os.path.dirname(ofn)):
            os.makedirs(os.path.dirname(ofn))

        if os.path.isfile(ofn):
            if url.scheme in ("http", "https"):
                con_l = int(http_head(site).getheader("Content-Length"))
                loc_l = int(os.stat(ofn).st_size)
                if con_l == loc_l:
                    _fetch = False
                    exists = True

        if _fetch:
            try:
                with open(ofn, "wb+") as fp:
                    if url.scheme in ("http", "https"):
                        fp.write(http_get(site))
                    elif url.scheme == "ftp":
                        ftp_get(site, fp)
            except Exception as e:
                self.log_q.critical(f"Error: {e}")
                return False
        return (ofn, exists)

    def run(self):
        while True:
            try:
                self.sig_q.get(False)
                self.log_q.info("LinkFetcher() thread exit")
                self.sig_q.task_done()
                self.sig_q.put(True)
                return
            except Empty:
                pass

            try:
                site = self.fetch_q.get()
                out, ex = self.fetch(site)
                self.fetch_q.task_done()
                # self.log_q.info(f"LinkFetcher().fetch(): Saved {out}")
                sz = os.stat(out).st_size
                tag = "(pre)" if ex else "(new)"
                self.gui_q.put(
                    {
                        "size": sz,
                        "have": 1,
                        "filename": f"{out} ({humanize_bytes(sz)}) {tag}",
                    }
                )
            except Empty:
                pass
