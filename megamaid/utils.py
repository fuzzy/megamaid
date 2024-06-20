import os
import re

from urllib.parse import urlparse
from http.client import HTTPConnection, HTTPSConnection


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
