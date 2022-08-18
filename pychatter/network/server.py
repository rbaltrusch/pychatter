# -*- coding: utf-8 -*-
"""
Created on Sun May 16 18:46:57 2021

@author: Korean_Crimson
"""
import datetime
import json
import logging
import socket
import uuid
from _thread import start_new_thread
from typing import Any, Callable, Dict, List

from pychatter.network import config
from pychatter.network.config import MAX_CHAT_RESP
from pychatter.network.util import Response, get_host_ip, parse_json_str

# pylint: disable=unused-argument
# pylint: disable=global-statement
# pylint: disable=invalid-name

ResponseFunction = Callable[[Dict[str, Any], str], Response]

socket_ = None
clients: Dict[str, str] = {}
chat: List[Dict[str, str]] = []
killed = False


class DecodeError(Exception):
    """Exception to be thrown when received messages cannot be decoded"""


class DisconnectionException(Exception):
    """Exception to be thrown when clients disconnect from a Connection"""


class ConnectionClosedException(Exception):
    """Exception to be throw for closed sockets"""


class ServerStartupException(Exception):
    """Exception to be thrown if server cannot startup in init"""


class Client:
    """Client contextmanager, adds new client ids when entered and removes them on exit"""

    def __init__(self):
        self.client_id = None

    def __enter__(self):
        self.client_id = str(uuid.uuid4())
        clients[self.client_id] = f"user{self.client_id[:7]}"
        return self.client_id

    def __exit__(self, *_):
        clients.pop(self.client_id, None)


class Connection:
    """Connection context manager, sends the new client id to every client on enter
    and closes the socket on exit.
    """

    def __init__(self, connection: socket.socket, client_id: str):
        self._conn = connection
        self.client_id = client_id

    def __enter__(self):
        response = Response(200, body=self.client_id)
        self._conn.sendall(response.encode())
        return self

    def __exit__(self, *_):
        logging.info("Lost connection to client. Killed = %s", killed)
        self._conn.close()

    def handle(self, response_functions: Dict[str, ResponseFunction]) -> None:
        """Handles the connection using the response_functions provided"""
        data = self._conn.recv(config.CHUNKSIZE)
        if not data:
            logging.info("Client disconnected: %s", self.client_id)
            raise DisconnectionException

        try:
            message = decode_message(data)
        except DecodeError:
            return

        response = determine_response(message, self.client_id, response_functions)
        logging.info("Sending response to all clients: %s", response)
        self._conn.sendall(response.encode())


def decode_message(data: bytes) -> Dict[str, Any]:
    """Decodes encoded json data into string"""
    decoded = data.decode("utf-8")
    try:
        message = json.loads(decoded)
    except json.JSONDecodeError as exc:
        logging.info("Client request in wrong format!")
        raise DecodeError from exc
    logging.info("Received client request: %s", message)
    return message


def get_clients_response(message: Dict[str, Any], client_id: str) -> Response:
    """Responds with a list of clients"""
    return Response(200, list(clients.values()))


def get_chat_response(message: Dict[str, Any], client_id: str) -> Response:
    """Responds with a list of older chat messages"""
    chat_messages_ = chat[-MAX_CHAT_RESP:] if len(chat) > MAX_CHAT_RESP else chat
    chat_messages = [
        {k: v for k, v in chat_message.items() if k != "userid"}
        for chat_message in chat_messages_
    ]
    return Response(200, chat_messages)


def post_client_name(message: Dict[str, Any], client_id: str) -> Response:
    """Adds the client id to clients, then sends a 200 Response"""
    clients[client_id] = message["body"]
    return Response(200, body="Updated client name")


def post_chat_message(message: Dict[str, Any], client_id: str) -> Response:
    """Appends the chat message to the chat, then sends a 200 Response"""
    chat_message: Dict = parse_json_str(message["body"])
    user_id = chat_message.get("userid")
    if not user_id:
        return Response(400, body="Invalid chat message: no user id specified")

    user_name = clients.get(user_id)
    if not user_name:
        return Response(400, body="Invalid chat message: unknown user id")

    chat_message["username"] = user_name
    chat_message["abstimestamp"] = datetime.datetime.utcnow().timestamp()
    chat.append(chat_message)
    return Response(200, body="Received chat message")


def put_client_name(message: Dict[str, Any], client_id: str) -> Response:
    """Updates the client name for the corresponding id, then sends a 200 Response"""
    old_client_name = clients.get(client_id)
    if not old_client_name:
        return Response(400, body="Invalid request: user does not exist")
    clients[client_id] = message["body"]
    return Response(200, body="Updated client name;{old_client_name}")


def get_responses_functions() -> Dict[str, ResponseFunction]:
    """Returns a mapping of request header to repective function to be called"""
    return {
        "get/clients": get_clients_response,
        "get/chat": get_chat_response,
        "post/clientname": post_client_name,
        "post/chatmessage": post_chat_message,
        "put/clientname": put_client_name,
    }


def determine_response(
    message: Dict[str, Any],
    client_id: str,
    response_functions: Dict[str, ResponseFunction],
) -> Response:
    """Returns a response by looking up the message head from the specified response_functions
    Returns an invalid request response if a valid response function cannot be found.
    """
    head = message["head"].lower().strip()
    response_function = response_functions.get(head)
    response = (
        Response(400, body="Invalid request")
        if response_function is None
        else response_function(message, client_id)
    )
    return response


def threaded_client(conn):
    """Tries to receive data from the client connection until the connection is
    terminated. Currently sends back the data received to all clients, unless
    the data received is equal to 'get', in which case it sends the last reply.
    """
    with Client() as new_client_id, Connection(conn, new_client_id) as connection:
        while not killed:
            try:
                connection.handle(response_functions=get_responses_functions())
            except DisconnectionException:
                break


def init(port=config.PORT):
    """Initialises the server"""
    global socket_, killed
    logging.info("Waiting for a connection, server started")
    killed = False
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # unblock address immediately once socket is closed
    ip_address = get_host_ip()
    logging.info("Hosting server on: %s", ip_address)
    try:
        socket_.bind((ip_address, port))
        socket_.listen(config.MAX_CLIENTS)
    except (socket.error, OverflowError) as exc:
        logging.exception("Could not initialise socket", exc_info=exc)
        raise ServerStartupException from exc


def run():
    """Tries to accept a connection from the socket. If possible, starts a new
    server thread that deals with the socket until the connection is closed.
    """
    try:
        conn, addr = socket_.accept()
    except socket.error as exc:
        raise ConnectionClosedException from exc

    logging.info("Connected to client address: %s", addr)
    start_new_thread(threaded_client, (conn,))


def run_forever():
    """Runs the server until it is killed"""
    while not killed:
        try:
            run()
        except ConnectionClosedException:
            break

    if socket_:
        socket_.close()


def kill():
    """Kills the server."""
    global killed
    killed = True
