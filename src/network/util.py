# -*- coding: utf-8 -*-
"""
Created on Mon May 10 18:37:40 2021

@author: Korean_Crimson
"""
import datetime
import json
import socket
import threading
from abc import ABC
from dataclasses import dataclass
from typing import Any
from typing import Dict

class HttpMessage(ABC): #pylint: disable=too-few-public-methods
    """Encodable HttMessage that can be sent over a socket connection"""

    def encode(self) -> bytes:
        """Encodes the message and returns it"""
        return str.encode(json.dumps(self.__dict__))

@dataclass
class Response(HttpMessage):
    """Response class"""

    status: int
    body: Any = ""

@dataclass
class Request(HttpMessage):
    """Request class"""

    head: str
    body: str = ""

def parse_json_str(decoded: str) -> Dict:
    """Returns dict of specified string if possible, else empty dict"""
    try:
        dict_ = json.loads(decoded)
    except (ValueError, TypeError):
        dict_ = {}
    return dict_

class KillableThread(threading.Thread):
    """source: https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread#:~:text=In%20Python%2C%20you%20simply%20cannot,yourProcess.""" #pylint: disable=line-too-long

    def __init__(self, func, sleep_interval=1):
        super().__init__()
        self.func = func
        self._kill = threading.Event()
        self._interval = sleep_interval

    def run(self):
        """Runs the thread function until KillableThread.kill method gets called"""
        while True:
            self.func()

            # If no kill signal is set, sleep for the interval,
            # If kill signal comes in while sleeping, immediately
            #  wake up and handle
            is_killed = self._kill.wait(self._interval)
            if is_killed:
                break

        print("Killing Thread")

    def kill(self):
        """Kills the thread. This will break the KillableThread.run while loop."""
        self._kill.set()

def get_timestamp() -> str:
    """Returns a timestamp string of the current time with 1s resolution"""
    time_ = datetime.datetime.now()
    return time_.strftime('%H:%M:%S')

def get_host_ip():
    """Returns the ip address of the current host"""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address
