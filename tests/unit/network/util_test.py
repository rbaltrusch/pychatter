# -*- coding: utf-8 -*-
"""network.util module tests"""

import datetime
import ipaddress
import math

import pytest
from localchat.network import util


@pytest.mark.parametrize(
    "type_, arg1, arg2, expected",
    [
        (util.Response, 200, "test", '{"status": 200, "body": "test"}'),
        (
            util.Request,
            "post/something",
            "abc",
            '{"head": "post/something", "body": "abc"}',
        ),
    ],
)
def test_encode(type_, arg1, arg2, expected: str):
    message: util.HttpMessage = type_(arg1, arg2)
    encoded = message.encode()
    assert encoded == expected.encode()


@pytest.mark.parametrize(
    "string, expected",
    [
        ('{"a":1,"b":"c"}', {"a": 1, "b": "c"}),
        ("{a]", {}),
    ],
)
def test_json_decode(string, expected):
    dict_ = util.parse_json_str(string)
    assert dict_ == expected


def test_timestamp():
    def in_seconds(date_: datetime.datetime) -> int:
        return date_.hour * 3600 + date_.minute * 60 + date_.second

    now_ = datetime.datetime.now()
    timestamp_str = util.get_timestamp()
    time_ = datetime.datetime.strptime(timestamp_str, "%H:%M:%S")
    assert math.isclose(in_seconds(now_), in_seconds(time_), rel_tol=0.01)


def test_host_ip():
    ipaddress.ip_address(util.get_host_ip())
