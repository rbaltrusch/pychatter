# -*- coding: utf-8 -*-
"""network.server module tests"""

# pylint: disable=missing-function-docstring, missing-class-docstring

import json
from dataclasses import dataclass
from typing import ByteString, Optional

import pytest
from localchat.network import config, server, util


@dataclass
class MockSocket:
    request: Optional[ByteString] = None

    def __post_init__(self):
        self.closed = False
        self.response = None

    def close(self):
        self.closed = True

    def recv(self, chunk_size) -> ByteString:
        if self.request is None:
            return bytes()
        return self.request

    def sendall(self, data: bytes):
        self.response = util.parse_json_str(data.decode())


def teardown():
    server.clients = {}
    if server.socket_:
        server.socket_.close()


def test_client():
    with server.Client() as id_:
        assert isinstance(id_, str)
        assert id_ in server.clients
        assert len(id_) > 1
    assert id_ not in server.clients


def test_run_fail():
    server.init()
    server.socket_.close()
    with pytest.raises(server.ConnectionClosedException):
        server.run()


def test_init_fail(monkeypatch):
    monkeypatch.setattr(config, "MAX_CLIENTS", 1_000_000_000_000)
    with pytest.raises(server.ServerStartupException):
        server.init()


def test_determine_response_invalid_message():
    with pytest.raises(KeyError):
        server.determine_response(
            message={"body": "a"},
            client_id="1",
            response_functions=server.get_responses_functions(),
        )


def test_determine_response_invalid_request():
    response = server.determine_response(
        message={"head": "abc"},
        client_id="1",
        response_functions=server.get_responses_functions(),
    )
    assert response.status == 400


@pytest.mark.parametrize(
    "data, exception",
    [
        ("a", AttributeError),
        ('{"a":[}'.encode("utf-8"), server.DecodeError),
    ],
)
def test_decode_message_fail(data, exception):
    with pytest.raises(exception):
        server.decode_message(data)


def test_connection_context_manager():
    socket_ = MockSocket()
    client_id = "1256"
    with server.Connection(connection=socket_, client_id=client_id):
        pass

    assert socket_.closed
    assert socket_.response.get("status") == 200
    assert socket_.response.get("body") == client_id


@pytest.mark.parametrize(
    "socket_, exception",
    [
        (MockSocket(request=None), server.DisconnectionException),
    ],
)
def test_connection_handle_fail(socket_: MockSocket, exception):
    client_id = "1256"
    with pytest.raises(exception):
        with server.Connection(connection=socket_, client_id=client_id) as conn:
            conn.handle(response_functions=server.get_responses_functions())


@pytest.mark.parametrize(
    "socket_",
    [
        MockSocket(request="ab{".encode("utf-8")),
    ],
)
def test_connection_handle_data_fail(socket_: MockSocket):
    with server.Connection(connection=socket_, client_id="123") as conn:
        socket_.response = None
        conn.handle(response_functions=server.get_responses_functions())
        assert socket_.response is None


def test_connection_handle():
    client_id = "36292"
    chat_message = json.dumps(
        {
            "text": "test",
            "userid": client_id,
            "timestamp": util.get_timestamp(),
        }
    )

    for request_name, callback in server.get_responses_functions().items():
        body = chat_message if request_name == "post/chatmessage" else client_id
        request = util.Request(head=request_name, body=body).encode()
        socket_ = MockSocket(request=request)
        with server.Connection(socket_, client_id=client_id) as conn:
            conn.handle(response_functions=server.get_responses_functions())
            expected_response = callback(
                message=server.decode_message(request), client_id=client_id
            )
            assert util.Response(**socket_.response) == expected_response


@pytest.mark.parametrize("body", [{}, {"userid": "34242342"}])
def test_post_chat_message_fail(body):
    server.clients = {}
    request = util.Request(head="post/chatmessage", body=body).encode()
    socket_ = MockSocket(request=request)
    with server.Connection(socket_, client_id="1") as conn:
        conn.handle(response_functions=server.get_responses_functions())
        assert socket_.response.get("status") == 400


@pytest.mark.parametrize("client_name", ["a"])
def test_put_client_name_fail(client_name):
    request = util.Request(head="put/clientname", body=client_name).encode()
    socket_ = MockSocket(request=request)
    with server.Connection(socket_, client_id="1") as conn:
        conn.handle(response_functions=server.get_responses_functions())
        assert socket_.response.get("status") == 400
