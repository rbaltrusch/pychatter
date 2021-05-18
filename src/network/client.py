# -*- coding: utf-8 -*-
"""
Created on Sun May 16 18:46:57 2021

@author: Korean_Crimson
"""

import socket
import network.config
import network.util

class NetworkConnection:
    """Class used to connect to the server"""

    def __init__(self, ip_address):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (ip_address, network.config.PORT)
        response_str = self.connect() #pylint: disable=invalid-name
        response = network.util.parse_json_str(response_str)
        self.id = response.get('body')

    def connect(self):
        """Sends its address to the server and receives the server response"""
        try:
            self.socket.connect(self.addr)
            return self.socket.recv(network.config.CHUNKSIZE).decode()
        except:
            print('failed')

    def send(self, data):
        """Sends the data (bytes) and returns the server response (str)"""
        try:
            self.socket.send(data)
            return self.socket.recv(network.config.CHUNKSIZE).decode()
        except socket.error as exc:
            self.id = None
            print(exc)

    def close(self):
        self.socket.close()
        self.id = None

    def __bool__(self):
        return self.id is not None
