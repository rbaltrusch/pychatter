# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 15:26:16 2021

@author: Korean_Crimson
"""

TITLE = "pychatter"
PORT = 5555
CONFIG_FILENAME = "config.json"
MAX_MESSAGE_LENGTH = 280
MAX_USERNAME_LENGTH = 30

# colours
FG = "#FFFFFF"
BG = "#121212"
BG2 = "#242424"
BG3 = "#363636"
BG4 = "#484848"
BG5 = "#606060"
PRIM = "#3700B3"
SEC = "#A172E1"
ERR = "#CF6679"

# themes
THEME = {"fg": FG, "bg": BG2, "highlightbackground": BG3}
_ACTIVE_THEME0 = {**THEME, "activebackground": BG3}

ENTRY_THEME = {**THEME, "insertbackground": FG, "selectbackground": BG5}
DYNAMIC_ENTRY_THEME = {**THEME, "state": "disabled", "disabledbackground": BG2}
LABEL_THEME = {"fg": FG, "bg": BG, "highlightbackground": BG2}
BUTTON_THEME = {**_ACTIVE_THEME0, "activeforeground": FG}
SCALE_THEME = {**_ACTIVE_THEME0, "troughcolor": BG5}
CHECKBOX_THEME = {**BUTTON_THEME, **LABEL_THEME, "selectcolor": BG5}

STATUS_THEME = {
    "fg": FG,
    "bg": BG,
    "highlightbackground": BG,
    "highlightcolor": BG,
    "state": "disabled",
    "disabledbackground": BG,
    "highlightthickness": 0,
    "bd": 0,
}
ERROR_STATUS_THEME = {**STATUS_THEME, "fg": ERR, "disabledforeground": ERR}  # type: ignore
