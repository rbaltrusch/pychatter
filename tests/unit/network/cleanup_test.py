# -*- coding: utf-8 -*-
"""Network.cleanup module tests"""

# pylint: disable=missing-function-docstring, missing-class-docstring

from pychatter.network import cleanup


class Connection:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FailConnection:
    def close(self):
        raise Exception


def test_cleanup():
    conn = Connection()
    function = lambda: conn
    with cleanup.SocketCleanup(function):
        pass
    assert conn.closed


def test_cleanup_failing_callables():
    conn = Connection()
    failing_callables = [lambda _: Connection, FailConnection]
    passing_callables = [lambda: conn]
    with cleanup.SocketCleanup(*failing_callables, *passing_callables):
        pass
    assert conn.closed
