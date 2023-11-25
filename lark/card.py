#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    lark.card
"""
from typing import List

from lark_oapi.api.contact.v3 import Department
from lark_oapi.api.im.v1 import ListChat

import datetime
import json


def hello():
    """Generate a welcome card for the robot in the group"""
    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "template": "green",
            "title": {"tag": "plain_text", "content": "Welcome to the KaiDiLark Robot"}},
        "elements": [
            {"tag": "div", "text":
                {
                    "tag": "lark_md",
                    "content": "You can learn more details about the robot through the following buttons"
                }
             },
            {"tag": "hr"},
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "ReadMe"},
                        "type": "primary",
                        "url": "https://github.com/KaiGuoV5/KaiDiLark/blob/main/README.md"
                    }
                ]
            }
        ]
    }


def uid(user_id: str, open_id: str, mentions: bool) -> dict:
    """
    Generates a dictionary containing user ID details.

    Args:
        user_id (str): The user ID.
        open_id (str): The open ID.
        mentions (bool): Title content display depends on whether to include mentions.

    Returns:
        dict: A dictionary with the user ID details.
    """
    if mentions:
        title_content = "Details of your search user ID"
    else:
        title_content = "Details of your user ID"
    return {
        "header": {"template": "blue", "title": {"content": title_content, "tag": "plain_text"}},
        "elements": [
            {"tag": "hr"},
            {"tag": "markdown", "content": "🆔 **USER_ID**"},
            {"tag": "markdown", "content": user_id},
            {"tag": "hr"},
            {"tag": "markdown", "content": "🆔 **OPEN_ID**"},
            {"tag": "markdown", "content": open_id}
        ],
    }
