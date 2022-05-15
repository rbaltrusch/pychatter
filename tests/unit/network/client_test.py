# -*- coding: utf-8 -*-
"""network.client module tests"""

import socket
import threading

import pytest
from localchat.network import client, config, server


class ServerSocket:
    """Server socket. Runs the server on localhost (127.0.0.1)"""

    def __init__(self):
        self.server_thread = None

    def __enter__(self):
        server.init()
        self.server_thread = threading.Thread(target=server.run_forever, daemon=True)
        self.server_thread.start()
        return self

    def __exit__(self, *_):
        server.socket_.close()
        server.kill()


@pytest.mark.parametrize("ip_address", ["localhost", "127.0.0.1"])
def test_network_connection_fail(ip_address):
    with pytest.raises(client.StartConnectionError):
        client.NetworkConnection(ip_address, timeout=0.2).connect()


@pytest.mark.parametrize("ip_address", ["127.0.0.2"])
def test_wrong_server_ip(ip_address):
    with ServerSocket():
        with pytest.raises(client.StartConnectionError):
            client.NetworkConnection(ip_address, timeout=0.2).connect()


@pytest.mark.parametrize("ip_address", ["127.0.0.1"])
def test_connect(ip_address):
    conn = client.NetworkConnection(ip_address)
    with ServerSocket():
        conn.connect()
        assert conn.id is not None
        assert bool(conn)


@pytest.mark.parametrize("ip_address", ["127.0.0.1"])
def test_send_fail(ip_address):
    conn = client.NetworkConnection(ip_address, timeout=0.5)
    with ServerSocket():
        conn.connect()
        response = conn.send("abc".encode())
    assert response is None


@pytest.mark.parametrize(
    "ip_address, head, body, expected_response_status",
    [("127.0.0.1", "abc", "", 400), ("127.0.0.1", "get/clients", "", 200)],
)
def test_send_request(ip_address, head, body, expected_response_status):
    conn = client.NetworkConnection(ip_address)
    with ServerSocket():
        conn.connect()
        response = conn.send_request(head=head, body=body)
    assert response.get("status") == expected_response_status


@pytest.mark.parametrize("ip_address", ["127.0.0.1"])
def test_bool(ip_address):
    conn = client.NetworkConnection(ip_address)
    assert not bool(conn)


@pytest.mark.parametrize("ip_address", ["127.0.0.1"])
def test_close(ip_address):
    conn = client.NetworkConnection(ip_address, timeout=0.5)
    with ServerSocket():
        conn.connect()
        conn.close()
    assert conn.id is None
    with pytest.raises(socket.error):
        conn.socket.recv(config.CHUNKSIZE)
