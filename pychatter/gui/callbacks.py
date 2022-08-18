# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 15:17:38 2021

@author: Korean_Crimson
"""
import datetime
import json
import re
import socket
import threading
import tkinter as tk

from pychatter.gui import app, config, root
from pychatter.network import client, server, util


def set_error(*_):
    """Callback for error StringVar write trace"""
    background = config.ERR if app.data["error"].get() else config.BG2
    app["server"]["connect_button"].config(bg=background)


def set_status_message(message):
    """Sets the text of the status entry to the specified message"""
    app.data["status"].set(message)
    app["status"].hide_component("error_entry")
    app["status"].unhide_component("status_entry")
    app.data["error"].set("")


def set_error_message(message):
    """Sets the text of the error entry to the specified message"""
    if app.data["error"].get() == message:
        return

    app.data["error"].set(message)
    app["status"].hide_component("status_entry")
    app["status"].unhide_component("error_entry")


def update_message_length(*_, reset=False):
    """Callback for chat message write trace"""
    text = (
        app["chat"]["chat_window"].tk_component.get("1.0", tk.END) if not reset else ""
    )
    app.data["message_length_message"].set(f"{len(text)}/{config.MAX_MESSAGE_LENGTH}")
    app.data["message_length"].set(len(text))

    message = "Exceeded maximum message length!"
    if len(text) > config.MAX_MESSAGE_LENGTH:
        set_error_message(message)
    else:
        app["chat"]["send_button"].config(bg=config.BG2)


def update_username_button(*_):
    """Updates the colour of the username button, depending on the validity of the username"""
    username_too_long = len(app.data["username"].get()) > config.MAX_USERNAME_LENGTH
    colour = config.ERR if username_too_long else config.BG2
    app["server"]["update_button"].config(bg=colour)


def focus(event):
    """Callback for left-click -- stores the selected widget"""
    app.focused_widget_name = str(event.widget)


def host_server(*_):
    """Callback for the host button"""
    try:
        server.init()
        app.data["server_thread"] = threading.Thread(
            target=server.run_forever, daemon=True
        )
        app.data["server_thread"].start()
    except Exception:  # pylint: disable=broad-except
        set_error_message("Failed to host server!")
        return

    ip_address = util.get_host_ip()
    app.data["server_ip"].set(ip_address)
    set_status_message(f"Successfully hosted server. IP: {ip_address}")
    app.data["hosting"].set(f"Hosting. IP: {ip_address}.")
    app["server"].hide_component("host_button")
    app["server"].unhide_component("unhost_button")


def unhost_server(*_):
    """Closes the server socket and reverts the server view to not-hosting mode"""
    try:
        if server.socket_:
            server.socket_.close()
    except Exception as exc:  # pylint: disable=broad-except
        print(exc)
        return

    app.data["hosting"].set("")
    app["server"].hide_component("unhost_button")
    app["server"].unhide_component("host_button")
    set_status_message("Successfully unhosted.")


def update_username(*_):
    """Updates the username on the server and locally updates the clients list"""
    new_username = app.data["username"].get()
    if len(new_username) > config.MAX_USERNAME_LENGTH:
        set_error_message(
            "Maximum user name length exceeded "
            f"({len(new_username)}/{config.MAX_USERNAME_LENGTH})."
        )
        return

    connection = app.data["connection"]
    if not connection:
        set_status_message("Successfully updated username!")
        return

    # inform server
    response = connection.send_request(head="put/clientname", body=new_username)
    status = response.get("status")
    if status == 200:
        set_status_message("Successfully updated username!")
        old_username = response["body"]
    else:
        set_error_message("Failed to update username on server!")
        old_username = None  # get from server

    clients = app.data["clients"]
    if old_username in clients:
        clients.remove(old_username)
    clients.append(new_username)


def get_recurring_server_updates():
    """Gets updates from the server, then schedules another update in the future"""
    get_server_updates()
    delay_ms = app.data["delay_ms"]
    if app.data["connection"]:
        root.schedule(delay_ms, get_recurring_server_updates)


def get_server_updates():
    """Gets updated list of clients and chat messages from server"""
    if not app.data["connection"]:
        disconnect_from_server()
        set_error_message("Disconnected from server.")

    _get_updated_list_of_clients_from_server()
    _get_updated_chat_from_server()
    if not app.data["error"].get():
        set_status_message("Connected to server.")


def _get_updated_list_of_clients_from_server():
    """get full list of clients. This can be improved by only polling the full list once
    and only receiving client list changes after that.
    """
    connection = app.data["connection"]
    if not connection:
        set_error_message("Disconnected from server.")
        return

    response = connection.send_request(head="get/clients")
    status = response.get("status")
    if status != 200:
        set_error_message("Could not get an updated list of clients from the server.")
        return

    previous_clients = app.data["clients"]
    updated_clients = response["body"]
    for client_ in set(previous_clients) - set(updated_clients):
        _append_text_message(text=f"{client_} has left the chat.\n")

    for client_ in set(updated_clients) - set(previous_clients):
        _append_text_message(text=f"{client_} has joined the chat.\n")
    app.data["clients"] = updated_clients


def _get_updated_chat_from_server():
    """gets latest chat messages from server. This is limited on the server side to
    the latest few chat messages to avoid sending large messages.
    """
    connection = app.data["connection"]
    if not connection:
        set_error_message("Disconnected from server.")
        return

    response = connection.send_request(head="get/chat")
    status = response.get("status")
    if status != 200:
        set_error_message("Could not get chat updates from the server.")
        return

    current_utc_timestamp = datetime.datetime.utcnow().timestamp()
    for chat_message_d in response["body"]:
        partial_message = {
            k: v for k, v in chat_message_d.items() if k != "abstimestamp"
        }
        if partial_message in app.data["chat"]:
            continue

        two_seconds_ago = current_utc_timestamp - app.data["delay_ms"] * 2 / 1000
        if two_seconds_ago > chat_message_d.get("abstimestamp"):
            continue

        try:
            _append_formatted_text_message(
                chat_message_d["text"],
                chat_message_d["timestamp"],
                chat_message_d["username"],
            )
            app.data["chat"].append(partial_message)
        except Exception:  # pylint: disable=broad-except
            set_error_message("Failed to update chat history with new updates.")


def _append_text_message(text):
    """Appends the passed text to the chat history without formatting"""
    text_widget = app["chat"]["chat_history"].tk_component
    text_widget.config(state="normal")
    text_widget.insert(tk.END, text)
    text_widget.config(state="disabled")


def _append_formatted_text_message(text, timestamp, user_name):
    """Appends the passed text to the chat history with formatting"""
    config_ = app.data["config"]
    if config_ and config_.get("chat_format"):
        formatted = config_["chat_format"].replace("%T", timestamp)
        formatted = formatted.replace("%U", user_name)
        if "%M" in formatted:
            formatted = formatted.replace("%M", text)
        else:
            formatted += f" {text}"
        text = formatted
    _append_text_message(text)
    # app['chat']['chat_history'].tk_component.highlight_pattern(user_name, 'prim')


def _clear_chat_history():
    """Deletes all contents of the chat history Text widget"""
    text_component = app["chat"]["chat_history"].tk_component
    text_component.config(state="normal")
    text_component.delete("1.0", tk.END)  # delete all
    text_component.config(state="disabled")


def send_message(*_):
    """Callback for send button"""
    if app.data["message_length"].get() > config.MAX_MESSAGE_LENGTH:
        app["chat"]["send_button"].config(bg=config.ERR)
        return

    connection = app.data["connection"]
    if not connection:
        return

    text = app["chat"]["chat_window"].tk_component.get("1.0", tk.END)
    message = re.sub("\\s+$", "\n", text)  # trim trailing whitespace
    timestamp = util.get_timestamp()
    chat_message_d = {"text": message, "userid": connection.id, "timestamp": timestamp}
    chat_message = json.dumps(chat_message_d)

    response = connection.send_request(head="post/chatmessage", body=chat_message)
    status = response.get("status")
    if status != 200:
        set_error_message("Server error occured on sending the chat message.")
        return

    user_name = app.data["username"].get()
    _append_formatted_text_message(message, timestamp, user_name)
    app.data["chat"].append(
        {"text": message, "username": user_name, "timestamp": timestamp}
    )
    app["chat"]["chat_window"].tk_component.delete("1.0", tk.END)  # delete all contents
    update_message_length(reset=True)


def connect_to_server(*_):
    """Callback for connect button"""
    set_status_message("Connecting to server...")
    ip_address = app.data["server_ip"].get()
    if not ip_address:
        set_error_message("Please enter an IP address!")
        return

    connection = client.NetworkConnection(ip_address)
    try:
        connection.connect()
    except socket.timeout:
        set_error_message("Connection timed out.")

    app.data["connection"] = connection
    if not connection:
        set_error_message("Connecting to the specified server failed!")
        return

    app["server"].hide_component("connect_button")
    app["server"].unhide_component("disconnect_button")

    user_name = app.data["username"].get()
    if len(user_name) > config.MAX_USERNAME_LENGTH:
        set_error_message(
            "Maximum user name length exceeded "
            f"({len(user_name)}/{config.MAX_USERNAME_LENGTH})."
        )
        return

    response = connection.send_request(head="post/clientname", body=user_name)
    status = response.get("status")
    if status == 200:
        set_status_message("Connected to server.")
    else:
        set_error_message("Error setting username on server!")
    app.data["clients"].append(user_name)
    _clear_chat_history()
    app["chat"].activate()
    app["chat"].repack()
    get_recurring_server_updates()
    _append_text_message(text="You have joined the chat!\n")


def disconnect_from_server():
    """Callback for disconnect button"""
    connection = app.data["connection"]
    if connection:
        connection.close()
    set_status_message("Disconnected from server.")
    app["server"].hide_component("disconnect_button")
    app["server"].unhide_component("connect_button")
    app["chat"].deactivate()
    app["chat"].unpack()

    _clear_chat_history()
    app.data["chat"] = []
    app.data["clients"] = []
