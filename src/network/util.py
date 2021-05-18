# -*- coding: utf-8 -*-
"""
Created on Mon May 10 18:37:40 2021

@author: Korean_Crimson
"""

import json
import datetime
import socket
import threading

class HttpMessage:
    def encode(self):
        return str.encode(json.dumps(self.__dict__))

class Response(HttpMessage):
    def __init__(self, status, body):
        self.status = status
        self.body = body

class Request(HttpMessage):
    def __init__(self, head, body):
        self.head = head
        self.body = body

def parse_json_str(decoded):
    try:
        dict_ = json.loads(decoded)
    except ValueError:
        dict_ = {}
    except TypeError:
        dict_ = {}
    return dict_

class KillableThread(threading.Thread):
    """source: https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread#:~:text=In%20Python%2C%20you%20simply%20cannot,yourProcess."""
    def __init__(self, func, sleep_interval=1):
        super().__init__()
        self.func = func
        self._kill = threading.Event()
        self._interval = sleep_interval

    def run(self):
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
        self._kill.set()

def get_timestamp():
    time_ = datetime.datetime.now()
    return time_.strftime('%H:%M:%S')

def get_host_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address
