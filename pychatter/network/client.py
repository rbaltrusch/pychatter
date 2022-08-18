# -*- coding: utf-8 -*-
"""
Created on Sun May 16 18:46:57 2021

@author: Korean_Crimson
"""
import logging
import socket
from typing import Any, Dict, Optional

from pychatter.network import config, util


class StartConnectionError(Exception):
    """Exception to be raised when a NetworkConnection cannot connect to its ip addresss"""


class NetworkConnection:
    """Class used to connect to the server"""

    def __init__(self, ip_address, port=config.PORT, timeout=5):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # unblock address immediately once socket is closed
        self.socket.settimeout(timeout)
        self.address = (ip_address, port)
        self.id = None  # pylint: disable=invalid-name

    def connect(self) -> None:
        """Sends its address to the server and receives the server response"""
        try:
            self.socket.connect(self.address)
            response_str = self.socket.recv(config.CHUNKSIZE).decode()
        except socket.error as exc:
            logging.exception("Failed to connect to %s", self.address, exc_info=exc)
            raise StartConnectionError from exc

        response = util.parse_json_str(response_str)
        self.id = response.get("body")

    def send_request(self, head="", body="") -> Dict[str, Any]:
        """Sends a request with given head and body and returns the server response"""
        request = util.Request(head, body)
        response_str = self.send(request.encode())
        return util.parse_json_str(response_str) if response_str is not None else {}

    def send(self, data: bytes) -> Optional[str]:
        """Sends the data (bytes) and returns the server response (str)"""
        try:
            self.socket.send(data)
            return self.socket.recv(config.CHUNKSIZE).decode()
        except socket.error as exc:
            logging.exception("Could not send data to %s", self.address, exc_info=exc)
        return None

    def close(self) -> None:
        """Closes the socket connection"""
        self.socket.close()
        self.id = None

    def __bool__(self):
        return self.id is not None
