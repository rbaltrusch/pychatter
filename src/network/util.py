# -*- coding: utf-8 -*-
"""
Created on Mon May 10 18:37:40 2021

@author: Korean_Crimson
"""
import datetime
import json
import socket
from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict


class HttpMessage(ABC):  # pylint: disable=too-few-public-methods
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


def get_timestamp() -> str:
    """Returns a timestamp string of the current time with 1s resolution"""
    time_ = datetime.datetime.now()
    return time_.strftime("%H:%M:%S")


def get_host_ip():
    """Returns the ip address of the current host"""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address
