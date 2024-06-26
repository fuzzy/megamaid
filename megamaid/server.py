# Copyright (c) 2024 Mike 'Fuzzy' Partin <mike.partin32@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Socket Servers for MegaMaid. TCP and UNIX domain sockets are supported, but it
can be extended to support UDP sockets as well.
"""


# Stdlib imports
import os
import json
import socket
import select
import logging

# Internal imports
from megamaid.utils import log_setup

# Globals
SOCK_FILE = "/tmp/megamaid-{name}.sock"


class MaidServer:
    """
    Base server class to handle Unix domain socket connections and data xfer.
    """

    def _handler(self, conn):
        """
        Handle incoming data from a client connection.

        Args:
            conn (socket.socket): The client connection socket.

        Returns:
            bool: True if data was handled successfully, None otherwise.
        """

        try:
            s_data = ""
            while len(s_data) == 0 or s_data[-1] != "\n":
                data = conn.recv(1024)
                if not data:
                    return None
                s_data += data.decode()

            if not data:
                return None

            jdata = json.loads(s_data)
            self._log.debug(f"Received: {jdata}")

            for k, v in self._cbmap.items():
                self._log.debug(f"Checking for key: {k}")
                if jdata.get("command", False) == k:
                    self._log.debug(f"Found key: {k}")
                    v(conn, jdata)
            return True
        except socket.error as e:
            self._log.error(f"Error handling client connection: {e}")
            return None

    def add_handler(self, key=False, cback=False):
        """
        Add a command handler.

        Args:
            key (str): The command key.
            handler (callable): The handler function for the command.

        Returns:
            bool: True if the handler was added successfully, False otherwise.

        Note:
            The handler function should take two arguments: the client socket and
            the data received from the client (result of json.reads()).
        """

        if key and cback and key not in self._cbmap.keys() and callable(cback):
            self._cbmap[key] = cback
            return True
        return False

    def run(self):
        """
        Run the server, handling multiple clients using select().
        """

        s_list = [self._sock_file]
        while True:
            r_list, _, e_list = select.select(s_list, [], s_list)
            for n_sock in r_list:
                if n_sock == self._sock_file:
                    c_sock, c_addr = self._sock_file.accept()
                    s_list.append(c_sock)
                    self._clmap[c_sock] = c_addr
                    self._log.debug(f"Accepted new connection from: {c_addr}")
                else:
                    msg = self._handler(n_sock)
                    if msg is None:
                        self._log.debug("Connection closed")
                        s_list.remove(n_sock)
                        n_sock.close()
                        del self._clmap[n_sock]
                    else:
                        self._log.debug("Sending: 'OK'")
                        n_sock.sendall("OK".encode())

            for n_sock in e_list:
                self._log.error(f"Error with socket: {n_sock}")
                s_list.remove(n_sock)
                n_sock.close()
                del self._clmap[n_sock]


class TcpServer(MaidServer):
    """
    TCP server class that extends MaidServer.
    """

    def __init__(self, host=False, port=9765, name="tcpserver", conns=25):
        """
        Initialize the TcpServer.

        Args:
            name (str, optional): The name of the server. Defaults to
            "tcpserver".
            listeners (int, optional): Number of listeners. Defaults to 25.
        """

        MaidServer.__init__(self)

        self._clmap = {}
        self._sock_name = None
        self._cbmap = {}

        if host:
            self._host = host
        else:
            self._host = "localhost"
        self._port = port
        self._log = log_setup(host.lower(), logging.DEBUG)

        self._log.debug("Starting TcpServer instance")
        self._sock_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock_file.bind((self._host, self._port))
        self._sock_file.listen(conns)
        self._log.debug(
            f"Listening on {self._host}:{self._port} with {conns} listeners"
        )


class SockServer(MaidServer):
    """
    Unix domain socket server class that extends MaidServer.
    """

    def __init__(self, name=False, listeners=25):
        """
        Initialize the SockServer.

        Args:
            name (str, optional): The name of the server. Defaults to
            "unixserver".
            listeners (int, optional): Number of listeners. Defaults to 25.
        """

        MaidServer.__init__(self)

        self._sock_name = None
        self._sock_file = None
        self._cbmap = {}
        self._clmap = {}

        if name:
            self._name = name
        else:
            self._name = "unixserver"

        self._log = log_setup(name.lower(), logging.DEBUG)

        try:
            os.unlink(self.sock_name)
        except OSError:
            if os.path.exists(self.sock_name):
                raise

        self._log.debug(f"Starting server with name: {name}")
        self._sock_file = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock_file.bind(self.sock_name)
        self._log.debug(f"Server bound to: {self.sock_name}")

        self._sock_file.listen(listeners)
        self._log.debug(f"Using {listeners} listeners.")

    @property
    def sock_name(self):
        """
        Get the formatted socket file path.

        Returns:
            str: The formatted socket file path.
        """

        return SOCK_FILE.format(name=self._name)
