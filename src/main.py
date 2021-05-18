# -*- coding: utf-8 -*-
"""
Created on Mon May 10 00:12:31 2021

@author: Korean_Crimson
"""

import network
from gui import app, init

init.init()
app.pack_all()
app.mainloop()

#close socket connection
try:
    if app.data['connection']:
        app.data['connection'].close()
except:
    pass

#close server socket if hosting
try:
    if network.server._socket:
        network.server._socket.close()
except:
    pass
