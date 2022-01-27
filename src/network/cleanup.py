# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 17:15:08 2022

@author: richa
"""

class SocketCleanup:
    """Context manager for socket cleanup. Takes a list of getter functions that
    either return None or a socket that can be closed.
    """

    def __init__(self, *callables):
        self.callables = callables

    def __enter__(self):
        return self

    def __exit__(self, *_):
        for func in self.callables:
            try:
                connection = func()
            except TypeError:
                print('Invalid cleanup function. Does not run with no parameters')
                continue

            if connection:
                try:
                    connection.close()
                except Exception as exc: #pylint: disable=broad-except
                    print(f'Failed to cleanup socket connection: {str(exc)}')
