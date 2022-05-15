# -*- coding: utf-8 -*-
"""
Created on Sun May 16 18:46:57 2021

@author: Korean_Crimson
"""
import socket
from typing import Any, Dict, Optional

from localchat.network import config, util


class NetworkConnection:
    """Class used to connect to the server"""

    def __init__(self, ip_address):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(config.TIMEOUT)
        self.addr = (ip_address, config.PORT)
        response_str = self.connect()
        response = util.parse_json_str(response_str)
        self.id = response.get("body")  # pylint: disable=invalid-name

    def connect(self) -> Optional[bytes]:
        """Sends its address to the server and receives the server response"""
        try:
            self.socket.connect(self.addr)
            return self.socket.recv(config.CHUNKSIZE).decode()
        except socket.error as exc:
            print(f"failed: {str(exc)}")
        return None

    def send_request(self, head="", body="") -> Dict[str, Any]:
        """Sends a request with given head and body and returns the server response"""
        request = util.Request(head, body)
        response_str = self.send(request.encode())
        if response_str is None:
            return {}
        return util.parse_json_str(response_str)

    def send(self, data: bytes) -> Optional[str]:
        """Sends the data (bytes) and returns the server response (str)"""
        try:
            print(data)
            self.socket.send(data)
            return self.socket.recv(config.CHUNKSIZE).decode()
        except socket.error as exc:
            print(f"Socket error {exc}")
        return None

    def close(self) -> None:
        """Closes the socket connection"""
        self.socket.close()
        self.id = None

    def __bool__(self):
        return self.id is not None
