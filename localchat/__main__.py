# -*- coding: utf-8 -*-
"""
Created on Mon May 10 00:12:31 2021

@author: Korean_Crimson
"""
from localchat.gui import app, init
from localchat.network import cleanup, server

init.init()
app.pack_all()

with cleanup.SocketCleanup(lambda: app.data["connection"], lambda: server.socket_):
    app.mainloop()
    server.kill()
