# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 17:57:26 2021

@author: Korean_Crimson
"""
# pylint: disable=import-error
# pylint: disable=line-too-long
import json
import os
import tkinter as tk

from pychatter.gui import app, callbacks, components, config, root
from pychatter.gui.text import CustomText


def init():
    """Initializes root and all views of gui app"""
    init_root()
    server_view = init_server_view()
    chat_view = init_chat_view()
    status_view = init_status_view()
    init_config()
    app.views_dict = {"server": server_view, "chat": chat_view, "status": status_view}


def init_root():
    """Initialize tkinter root"""
    # configure root
    root.title(config.TITLE)
    root["bg"] = config.BG
    root.focus_force()

    # set trace callbacks
    root.bind_all("<Button-1>", callbacks.focus)
    root.bind("<Return>", callbacks.send_message)
    app.data["error"].trace_add("write", callbacks.set_error)
    app.data["username"].trace_add("write", callbacks.update_username_button)

    # set window icon
    try:
        icon_path = os.path.join("gui", "media", "icon.png")
        root.set_icon(icon_path)
    except Exception:  # pylint: disable=broad-except
        print("Couldnt set icon properly!")


def init_config():
    """Read config from config file, if present"""
    if os.path.isfile(config.CONFIG_FILENAME):
        try:
            with open(config.CONFIG_FILENAME, "r", encoding="utf-8") as file:
                dict_ = json.load(file)
        except (PermissionError, json.decoder.JSONDecodeError):
            dict_ = {}
        app.data["config"] = dict_


def init_server_view():
    """Initializes file select view"""
    view = components.View()
    view.activate()

    frame = tk.Frame(root, bd=0, bg=config.BG)
    component = components.Frame(
        frame,
        sticky="NSEW",
        row=0,
        column=0,
        row_span=2,
        column_span=3,
        padx=10,
        pady=10,
    )
    component.add_col(0)
    component.add_col(200)
    component.add_col(0)
    view.add_frame_component(component, "frame")

    # IP disp
    ip_label = tk.Label(frame, text="Server IP", **config.LABEL_THEME)
    component = components.Component(ip_label, sticky="NSE", row=0, column=0, padx=5)
    view.add_component(component, "ip_label")

    ip_entry = tk.Entry(frame, textvariable=app.data["server_ip"], **config.ENTRY_THEME)
    component = components.Component(ip_entry, sticky="NSEW", row=0, column=1)
    view.add_component(component, "ip_entry")

    # Connect button
    connect_button = tk.Button(
        frame,
        text="Connect",
        command=callbacks.connect_to_server,
        **config.BUTTON_THEME
    )
    component = components.Component(connect_button, sticky="NSEW", row=0, column=2)
    view.add_component(component, "connect_button")

    # Host button
    host_button = tk.Button(
        frame, text="Host", command=callbacks.host_server, **config.BUTTON_THEME
    )
    component = components.Component(host_button, sticky="NSEW", row=0, column=3)
    view.add_component(component, "host_button")

    # Unhost button
    unhost_button = tk.Button(
        frame, text="Unhost", command=callbacks.unhost_server, **config.BUTTON_THEME
    )
    component = components.Component(unhost_button, sticky="NSEW", row=0, column=3)
    view.add_component(component, "unhost_button")
    view.hide_component("unhost_button")

    # Disconnect button
    disconnect_button = tk.Button(
        frame,
        text="Disconnect",
        command=callbacks.disconnect_from_server,
        **config.BUTTON_THEME
    )
    component = components.Component(disconnect_button, sticky="NSEW", row=0, column=2)
    view.add_component(component, "disconnect_button")
    view.hide_component("disconnect_button")

    # username disp
    username_label = tk.Label(frame, text="Username", **config.LABEL_THEME)
    component = components.Component(
        username_label, sticky="NSE", row=1, column=0, padx=5
    )
    view.add_component(component, "username_label")

    username = app.data["username"]
    username_entry = tk.Entry(frame, textvariable=username, **config.ENTRY_THEME)
    component = components.Component(username_entry, sticky="NSEW", row=1, column=1)
    view.add_component(component, "username_entry")

    # update button
    update_button = tk.Button(
        frame, text="Update", command=callbacks.update_username, **config.BUTTON_THEME
    )
    component = components.Component(update_button, sticky="NSEW", row=1, column=2)
    view.add_component(component, "update_button")
    return view


def init_chat_view():
    """Initializes chat view"""
    view = components.View()

    frame = tk.Frame(root, bd=0, bg=config.BG)
    component = components.Frame(
        frame,
        sticky="NSEW",
        row=2,
        row_span=2,
        column=0,
        column_span=3,
        padx=10,
        pady=10,
    )
    component.add_col(0)
    component.add_col(200)
    component.add_col(0)
    view.add_frame_component(component, "frame")

    chat_history = CustomText(frame, width=50, **config.ENTRY_THEME, state="disabled")
    chat_history.tag_configure("prim", foreground=config.PRIM)
    component = components.Component(
        chat_history, sticky="NSEW", row=0, column_span=2, column=1
    )
    view.add_component(component, "chat_history")

    chat_window = CustomText(frame, width=50, height=3, **config.ENTRY_THEME)
    component = components.Component(
        chat_window, sticky="NSEW", row=1, column=1, pady=10
    )
    view.add_component(component, "chat_window")
    chat_window.bind("<KeyRelease>", callbacks.update_message_length)

    send_button = tk.Button(
        frame, text="Send", command=callbacks.send_message, **config.BUTTON_THEME
    )
    component = components.Component(send_button, sticky="NSEW", row=1, column=2)
    view.add_component(component, "send_button")

    message_length_entry = tk.Label(
        frame, textvariable=app.data["message_length_message"], **config.LABEL_THEME
    )
    component = components.Component(
        message_length_entry, sticky="NSE", row=2, column=1
    )
    view.add_component(component, "message_length_entry")
    return view


def init_status_view():
    """Initializes status view"""
    view = components.View()
    view.activate()

    frame = tk.Frame(root, bd=0, bg=config.BG)
    component = components.Frame(
        frame,
        sticky="NSEW",
        row=5,
        row_span=2,
        column=0,
        column_span=3,
        padx=17,
        pady=10,
    )
    component.add_col(300)
    component.add_col(0)
    view.add_frame_component(component, "frame")

    status_entry = tk.Entry(
        frame, textvariable=app.data["status"], **config.STATUS_THEME
    )
    component = components.Component(status_entry, sticky="NSEW", row=0, column=0)
    view.add_component(component, "status_entry")
    view.hide_component("status_entry")

    error_entry = tk.Entry(
        frame, textvariable=app.data["error"], **config.ERROR_STATUS_THEME
    )
    component = components.Component(error_entry, sticky="NSEW", row=0, column=0)
    view.add_component(component, "error_entry")

    hosting_entry = tk.Entry(
        frame, textvariable=app.data["hosting"], **config.STATUS_THEME
    )
    component = components.Component(hosting_entry, sticky="NSEW", row=1, column=0)
    view.add_component(component, "hosting_entry")
    return view
