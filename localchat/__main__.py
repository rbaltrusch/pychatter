# -*- coding: utf-8 -*-
"""
Created on Mon May 10 00:12:31 2021

@author: Korean_Crimson
"""
from localchat import cli
from localchat.gui import app, init
from localchat.network import cleanup, server


def run_server():
    """Runs the chat server"""
    server.init()
    server.run_forever()


def run_application():
    """Runs the chat application"""
    init.init()
    app.pack_all()

    with cleanup.SocketCleanup(lambda: app.data["connection"], lambda: server.socket_):
        app.mainloop()
        server.kill()


def main():
    """Main function"""
    parser = cli.construct_parser()
    args = parser.parse_args()
    function = run_server if args.server else run_application
    function()


main()
