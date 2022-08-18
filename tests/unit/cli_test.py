# -*- coding: utf-8 -*-
"""cli module tests"""

# pylint: disable=missing-function-docstring, missing-class-docstring

from localchat import cli


def test_server():
    parser = cli.construct_parser()
    args = parser.parse_args([])
    assert args.server is False

    args = parser.parse_args(["--server"])
    assert args.server is True
