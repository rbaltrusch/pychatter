# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 18:29:09 2021

@author: richa
"""
import json
import random
import threading

import pytest
from localchat.network import client, server, util

server_thread = None


def teardown():
    if server.socket_:
        server.socket_.close()


class ServerConnection:
    def __init__(self):
        self.connection = None
        self.server_thread = None

    def __enter__(self):
        port = random.randint(10000, 65535)
        server.init(port=port)
        self.server_thread = threading.Thread(target=server.run_forever, daemon=True)
        self.server_thread.start()

        ip_address = util.get_host_ip()
        self.connection = client.NetworkConnection(ip_address, port=port)
        self.connection.connect()
        print("id", self.connection.id)
        return self

    def __exit__(self, *_):
        print("Exiting ServerConnection")
        self.connection.close()
        server.socket_.close()
        server.kill()


class MockConnection:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass


def test_connection():
    with ServerConnection():
        pass


def test_get_clients_response():
    with ServerConnection() as conn:
        response = conn.connection.send_request("get/clients")
        print(response)
        assert response.get("status") == 200
        clients = response.get("body")
        assert isinstance(clients, list)
        assert len(clients) == 1


def test_get_chat_response():
    with ServerConnection() as conn:
        response = conn.connection.send_request("get/chat")
        assert response.get("status") == 200
        chat = response.get("body")
        assert isinstance(chat, list)
        assert len(chat) == 0


def test_post_client_name():
    with ServerConnection() as conn:
        username = "user123"
        response = conn.connection.send_request("post/clientname", body=username)
        assert response.get("status") == 200

        response = conn.connection.send_request("get/clients")
        assert response.get("status") == 200
        assert response.get("body") == [username]


def test_post_chat_message():
    with ServerConnection() as conn:
        text = "hello123"
        chat_message = {
            "text": text,
            "userid": conn.connection.id,
            "timestamp": util.get_timestamp(),
        }
        response = conn.connection.send_request(
            "post/chatmessage", body=json.dumps(chat_message)
        )
        assert response.get("status") == 200

        response = conn.connection.send_request(
            "post/chatmessage", body=json.dumps({"text": "123"})
        )
        assert response.get("status") == 400  # no userid

        response = conn.connection.send_request(
            "post/chatmessage", body=json.dumps({"text": "something", "userid": "123"})
        )
        assert response.get("status") == 400  # invalid userid

        response = conn.connection.send_request("get/chat")
        assert response.get("status") == 200
        body = response.get("body")
        assert len(body) == 1
        assert body[0]["text"] == text


@pytest.mark.parametrize("connection_type", [ServerConnection, MockConnection])
def test_put_client_name(connection_type):
    with ServerConnection() as conn:
        username = "user123"
        response = conn.connection.send_request("put/clientname", body=username)
        assert response.get("status") == 200

        new_username = "user1234"
        response = conn.connection.send_request("put/clientname", body=new_username)
        assert response.get("status") == 200

        response = conn.connection.send_request("get/clients")
        assert response.get("status") == 200
        assert response.get("body") == [new_username]
