import os
import re
import logging

from ftplib import FTP
from urllib.parse import urlparse
from http.client import HTTPConnection, HTTPSConnection


def log_setup(name, level=logging.INFO, fname=False, fmatter=False):
    retv = logging.getLogger(name)
    retv.setLevel(level)

    # setup our logfile
    if not fname:
        fname = f"/tmp/megamaid-{str(name).lower()}.log"
    fh = logging.FileHandler(fname)
    fh.setLevel(level)

    # and our default formatter
    if not fmatter:
        fmatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s - %(message)s")
    fh.setFormatter(fmatter)
    retv.addHandler(fh)

    return retv


def log_cleanup(name):
    ln = f"/tmp/megamaid-{str(name).lower()}.log"
    if os.path.isfile(ln):
        os.unlink(ln)


def ftp_get(site, fp):
    url = urlparse(site)
    with FTP(url.netloc) as ftp:
        ftp.login()
        ftp.cwd(os.path.dirname(url.path))
        ftp.retrbinary(f"RETR {os.path.basename(url.path)}", fp.write)
        ftp.quit()


def http_get(site):
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537."
    }
    url = urlparse(site)
    conn = None
    if len(os.getenv("http_proxy", "")) > 0:
        proxy = urlparse(os.getenv("http_proxy"))
        (host, port) = proxy.netloc.split(":")
        if url.scheme == "https":
            conn = HTTPSConnection(host, port)
            conn.set_tunnel(url.hostname, 443)
        else:
            conn = HTTPConnection(host, port)
        headers["Host"] = url.hostname
    else:
        if url.scheme == "https":
            conn = HTTPSConnection(url.hostname)
        else:
            conn = HTTPConnection(url.hostname)
    if len(os.getenv("http_proxy", "")) > 0:
        if url.scheme == "http":
            conn.request("GET", site, headers=headers)
        elif url.scheme == "https":
            conn.request("GET", url.path)
    else:
        conn.request("GET", url.path, headers=headers)

    return conn.getresponse().read()


def http_head(site):
    conn = None
    url = urlparse(site)
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537."
    }
    if len(os.getenv("http_proxy", "")) > 0:
        proxy = urlparse(os.getenv("http_proxy"))
        (host, port) = proxy.netloc.split(":")
        if url.scheme == "https":
            conn = HTTPSConnection(host, port)
            conn.set_tunnel(url.hostname, 443)
        else:
            conn = HTTPConnection(host, port)
        headers["Host"] = url.hostname
    else:
        if url.scheme == "https":
            conn = HTTPSConnection(url.hostname)
        else:
            conn = HTTPConnection(url.hostname)
    if len(os.getenv("http_proxy", "")) > 0:
        if url.scheme == "http":
            conn.request("HEAD", site, headers=headers)
        elif url.scheme == "https":
            conn.request("HEAD", url.path)
    return conn.getresponse()


# Normalize URLs, changing `//` to `/`
def normalize_url(url):
    parts = url.split("://")
    if len(parts) > 1:
        return f'{parts[0]}://{re.sub("//", "/", parts[1])}'
    else:
        return re.sub("//", "/", f"{url}")


# Humanize file sizes
def humanize_bytes(b):
    if b < 1024:
        return f"{b}B"

    s = ("B", "KB", "MB", "GB", "TB")
    d = list(range(0, len(s)))
    for r in d:
        if b >= 1024**r and b <= (1024 ** (r + 1)):
            return f"{b/(1024**r):.1f}{s[r]}"
