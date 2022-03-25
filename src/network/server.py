# -*- coding: utf-8 -*-
"""
Created on Sun May 16 18:46:57 2021

@author: Korean_Crimson
"""
import datetime
import json
import socket
import uuid
from _thread import start_new_thread
from typing import Any
from typing import Callable
from typing import Dict
from typing import List

import network.config
from network.config import MAX_CHAT_RESP
from network.util import get_host_ip
from network.util import parse_json_str
from network.util import Response

#pylint: disable=unused-argument
#pylint: disable=global-statement
#pylint: disable=invalid-name

socket_ = None
clients: Dict[str, str] = {}
chat: List[Dict[str, str]] = []
killed = False

def decode_message(data: bytes) -> Dict[str, Any]:
    """Decodes encoded json data into string"""
    decoded = data.decode("utf-8")
    try:
        message = json.loads(decoded)
    except json.JSONDecodeError:
        message = None
    return message

def get_clients_response(message: Dict[str, Any], client_id: str) -> Response:
    """Responds with a list of clients"""
    return Response(200, list(clients.values()))

def get_chat_response(message: str, client_id: str) -> Response:
    """Responds with a list of older chat messages"""
    chat_messages_ = chat[-MAX_CHAT_RESP:] if len(chat) > MAX_CHAT_RESP else chat
    chat_messages = [
        {k: v for k, v in chat_message.items() if k != 'userid'}
        for chat_message in chat_messages_
    ]
    return Response(200, chat_messages)

def post_client_name(message: Dict[str, Any], client_id: str) -> Response:
    """Adds the client id to clients, then sends a 200 Response"""
    clients[client_id] = message['body']
    return Response(200, body='Updated client name')

def post_chat_message(message: Dict[str, Any], client_id: str) -> Response:
    """Appends the chat message to the chat, then sends a 200 Response"""
    chat_message: Dict = parse_json_str(message['body'])
    user_id = chat_message.get('userid')
    if not user_id:
        return Response(400, body='Invalid chat message: no user id specified')

    user_name = clients.get(user_id)
    if not user_name:
        return Response(400, body='Invalid chat message: unknown user id')

    chat_message['username'] = user_name
    chat_message['abstimestamp'] = datetime.datetime.utcnow().timestamp()
    chat.append(chat_message)
    return Response(200, body='Received chat message')

def put_client_name(message: Dict[str, Any], client_id: str) -> Response:
    """Updates the client name for the corresponding id, then sends a 200 Response"""
    old_client_name = clients.get(client_id)
    if not old_client_name:
        return Response(400, body='Invalid request: user does not exist')
    clients[client_id] = message['body']
    return Response(200, body='Updated client name;{old_client_name}')

def threaded_client(conn, response_functions: Dict[str, Callable]):
    """Tries to receive data from the client connection until the connection is
    terminated. Currently sends back the data received to all clients, unless
    the data received is equal to 'get', in which case it sends the last reply.
    """

    new_client_id = str(uuid.uuid4())
    clients[new_client_id] = f'user{new_client_id[:7]}'
    response = Response(200, body=new_client_id)
    conn.sendall(response.encode())

    while not killed:
        data = conn.recv(network.config.CHUNKSIZE)
        if not data:
            print("Disconnected")
            break

        message = decode_message(data)
        if message is None:
            print('Message in wrong format!')
            continue
        print('Received', message)

        head = message['head'].lower().strip()
        response_function = response_functions.get(head)
        if response_function is None:
            response = Response(400, body='Invalid request')
        else:
            response = response_function(message, new_client_id)

        print(f"Sending : {response}")
        conn.sendall(response.encode())

    print("Lost connection")
    conn.close()
    clients.pop(new_client_id, None)
    print(clients, chat)

def init():
    """Initialises the server"""
    global socket_
    print("Waiting for a connection, Server Started")
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        ip_address = get_host_ip()
        print(f'Hosting on {ip_address}')
        socket_.bind((ip_address, network.config.PORT))
        socket_.listen(network.config.MAX_CLIENTS)
    except socket.error as e:
        str(e)

def run():
    """Tries to accept a connection from the socket. If possible, starts a new
    server thread that deals with the socket until the connection is closed.
    """
    response_functions = {
        'get/clients': get_clients_response,
        'get/chat': get_chat_response,
        'post/clientname': post_client_name,
        'post/chatmessage': post_chat_message,
        'put/clientname': put_client_name,
    }

    try:
        conn, addr = socket_.accept()
    except Exception as exc: #pylint: disable=broad-except
        print(str(exc))
        return
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn, response_functions))

def run_forever():
    """Runs the server until it is killed"""
    while True:
        run()
        if killed:
            if socket_:
                socket_.close()
            break

def kill():
    """Kills the server."""
    global killed
    killed = True

if __name__ == '__main__':
    init()
    run()
