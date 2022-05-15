# -*- coding: utf-8 -*-
"""Constructs the cli argparser"""

import argparse


def construct_parser() -> argparse.ArgumentParser:
    """Constructs the cli argparser"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--server",
        action="store_true",
        default=False,
        help="Host the server instead of running the chat application",
    )

    return parser
