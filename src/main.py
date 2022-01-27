# -*- coding: utf-8 -*-
"""
Created on Mon May 10 00:12:31 2021

@author: Korean_Crimson
"""
from gui import app
from gui import init
from network import cleanup
from network import server

init.init()
app.pack_all()

with cleanup.SocketCleanup(
    lambda: app.data['connection'],
    lambda: server.socket_
):
    app.mainloop()
    server.kill()
