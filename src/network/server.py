# -*- coding: utf-8 -*-
"""
Created on Sun May 16 18:46:57 2021

@author: Korean_Crimson
"""

import json
import datetime
import uuid
import socket
from _thread import start_new_thread
import network.config
from network.config import MAX_CHAT_RESP
from network.util import Response, parse_json_str, get_host_ip

#pylint: disable=invalid-name

socket_ = None
clients = {}
chat = []
killed = False

def threaded_client(conn):
    """Tries to receive data from the client connection until the connection is
    terminated. Currently sends back the data received to all clients, unless
    the data received is equal to 'get', in which case it sends the last reply.
    """

    new_client_id = str(uuid.uuid4())
    clients[new_client_id] = f'user{new_client_id[:7]}'
    response = Response(200, body=new_client_id)
    conn.sendall(response.encode())

    while True:
        print(killed)
        if killed:
            break

        try:
            data = conn.recv(network.config.CHUNKSIZE)
            decoded = data.decode("utf-8")
        except Exception as e:
            raise e

        if not data:
            print("Disconnected")
            break

        try:
            message = json.loads(decoded)
        except json.JSONDecodeError:
            print('message in wrong format!')
            break
        print('Received', message)

        if message['head'].lower() == 'get':
            if message['body'].lower() == 'clients':
                response = Response(200, list(clients.values()))
            elif message['body'].lower() == 'chat':
                chat_messages = chat[-MAX_CHAT_RESP:] if len(chat) > MAX_CHAT_RESP else chat
                chat_messages = [{k: v for k, v in chat_message.items() if k != 'userid'}
                                 for chat_message in chat_messages]
                response = Response(200, chat_messages)
            else:
                response = Response(400, body='Invalid request')
        elif message['head'].lower() == 'post':
            if message['body'].lower().startswith('clientname'):
                *_, client_name = message['body'].split(';')
                clients[new_client_id] = client_name
                response = Response(200, body='Updated client name')
            elif message['body'].lower().startswith('chatmessage'):
                *_, chat_message = message['body'].split(';')
                chat_message_d = parse_json_str(chat_message)
                user_id = chat_message_d.get('userid')
                if user_id:
                    user_name = clients.get(user_id)
                    if user_name:
                        chat_message_d['username'] = user_name
                        chat_message_d['abstimestamp'] = datetime.datetime.utcnow().timestamp()
                        response = Response(200, body='Received chat message')
                        chat.append(chat_message_d)
                    else:
                        response = Response(400, body='Invalid chat message: unknown user id')
                else:
                    response = Response(400, body='Invalid chat message: no user id specified')
            else:
                response = Response(400, body='Invalid request')
        elif message['head'].lower() == 'put':
            if message['body'].lower().startswith('clientname'):
                *_, client_name = message['body'].split(';')
                old_client_name = clients.get(new_client_id)
                if old_client_name:
                    clients[new_client_id] = client_name
                    response = Response(200, body='Updated client name;{old_client_name}')
                else:
                    response = Response(400, body='Invalid request: user does not exist')
            else:
                response = Response(400, body='Invalid request')
        else:
            response = Response(400, body='Invalid request')
        print(f"Sending : {response}")
        conn.sendall(response.encode())

        print()
        print(clients, chat)

    print("Lost connection")
    conn.close()

    try:
        del clients[new_client_id]
    except ValueError:
        pass
    print(clients, chat)

def init():
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
    conn, addr = socket_.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn,))

def run_forever():
    """Main function"""
    while True:
        run()
        if killed:
            if socket_:
                socket_.close()
            break

if __name__ == '__main__':
    init()
    run()
