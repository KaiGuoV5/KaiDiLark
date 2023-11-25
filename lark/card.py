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


def groups(group_list: List[ListChat]):
    """
    Generates a group card based on the provided group list.

    Args:
        group_list (List[ListChat]): The list of groups.

    Returns:
        dict: The generated group card.
    """
    group_card = {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue", "title": {"content": "Groups", "tag": "plain_text"}},
        "elements": [
            {
                "tag": "column_set", "flex_mode": "none", "background_style": "indigo",
                "columns": [
                    {
                        "tag": "column", "width": "weighted", "weight": 2, "vertical_align": "top",
                        "elements": [{"tag": "markdown", "content": "**🗳 NAME**"}]
                    },
                    {
                        "tag": "column", "width": "weighted", "weight": 3, "vertical_align": "top",
                        "elements": [{"tag": "markdown", "content": "**🆔 ID**"}]
                    }
                ]
            }
        ]
    }
    group: ListChat
    for group in group_list:
        if group.name is None:
            group.name = ""
        if group.chat_id is None:
            group.chat_id = ""
        new_fields = [
            {
                "tag": "column_set", "flex_mode": "none", "background_style": "grey",
                "columns": [
                    {
                        "tag": "column", "width": "weighted", "weight": 2, "vertical_align": "top",
                        "elements": [{"tag": "markdown", "content": group.name}]
                    },
                    {
                        "tag": "column", "width": "weighted", "weight": 3, "vertical_align": "top",
                        "elements": [{"tag": "markdown", "content": group.chat_id}]
                    }
                ]
            }
        ]
        group_card["elements"].extend(new_fields)
    return group_card
