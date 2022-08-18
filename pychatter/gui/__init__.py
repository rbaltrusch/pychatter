# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 15:13:17 2021

@author: Korean_Crimson
"""

# pylint: disable=E0611,E0401
import tkinter as tk

from pychatter.gui.components import Gui, Tk

root = Tk()
app = Gui(root)

# tk variable declarations
app.data["error"] = tk.StringVar()
app.data["status"] = tk.StringVar()
app.data["hosting"] = tk.StringVar()

app.data["delay_ms"] = 1000  # time between server updates
app.data["server_ip"] = tk.StringVar()
app.data["connection"] = None
app.data["chat"] = []
app.data["clients"] = []

app.data["server_thread"] = None  # for hosting

app.data["username"] = tk.StringVar()
app.data["username"].set("User")
app.data["config"] = {}
app.data["config"]["chat_format"] = "%T: %U: %M"
app.data["message_length_message"] = tk.StringVar()
app.data["message_length"] = tk.IntVar()
