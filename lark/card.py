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


def markdown(content):
    return {
        "config": {
            "wide_screen_mode": True
        },
        "elements": [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": content}
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


def answer(content, fresh=False):
    answer_card = {
        "config": {
            "wide_screen_mode": True
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": content}},
        ]
    }

    if fresh:
        fresh_msg = [
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": "<font color='green'>Loading...</font>"}},
        ]
        answer_card["elements"].extend(fresh_msg)
    return answer_card


def work_order_build():
    """  build work order card """
    return {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue", "title": {"content": "Work Order", "tag": "plain_text"}},
        "elements": [
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"content": "Artificial Service", "tag": "plain_text"},
                        "type": "primary",
                        "value": {
                            "action": "work_order",
                        }
                    }
                ]
            }
        ]
    }


def work_order_show(chats_name: str, user_id: str, assist_id: str, description: str):
    now = datetime.datetime.now()
    localtime = now.strftime("%Y-%m-%d %H:%M:%S")
    create_time = f"🕗︎ **Create      : **{localtime}"
    applicant = f"🗣 **Applicant   : **<at id={user_id}></at>"
    operator = f"👨‍🔧 **Operator    : **<at id={assist_id}></at>"
    order_content = f"🔖 **Description : **{description}"
    work_order_show_card = {
        "config": {"wide_screen_mode": True},
        "header": {"template": "turquoise", "title": {"content": f"🚨 {chats_name}", "tag": "plain_text"}},
        "elements": [
            {
                "tag": "div",
                "fields": [
                    {"is_short": False, "text": {"tag": "lark_md", "content": create_time}},
                    {"is_short": False, "text": {"tag": "lark_md", "content": applicant}},
                    {"is_short": False, "text": {"tag": "lark_md", "content": operator}},
                ]
            },
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": order_content}}
        ]
    }
    return work_order_show_card


WORK_ORDER_LIST = [
    {
        "value": "permission",
        "content": "Access Request",
        "order_list": [
            {"content": "OTA", "value": "permission_ota"},
            {"content": "DIY", "value": "permission_diy"},
        ]
    },
    {
        "value": "bug",
        "content": "Bug Feedback",
        "order_list": [
            {"content": "platform bug", "value": "bug_platform"},
            {"content": "integration bug", "value": "bug_integration"},
        ]
    },
    {
        "value": "other",
        "content": "Others",
        "order_list": [
            {"content": "Other Work Order", "value": "other_work_order"},
        ]
    }
]


def work_order_select():
    """选择工单类型"""
    select_card = {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue", "title": {"content": "Choose Service", "tag": "plain_text"}},
        "elements": [
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "select_static",
                        "placeholder": {"content": "Choose Service", "tag": "plain_text"},
                        "value": {"action": "work_order_type"},
                        "options": []
                    }
                ]
            }
        ]
    }

    for i in WORK_ORDER_LIST:
        content = i["content"]
        value = i["value"]
        select_card["elements"][0]["actions"][0]["options"].append({
            "text": {"content": content, "tag": "plain_text"}, "value": value
        })
    return select_card


def work_order_list(work_order_type):
    """工单类型子列表"""
    list_card = {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue", "title": {"content": "Choose Service", "tag": "plain_text"}},
        "elements": [
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "select_static",
                        "placeholder": {"content": "Choose Service", "tag": "plain_text"},
                        "value": {"action": "work_order_submit"},
                        "options": [],
                        "confirm": {
                            "title": {"content": "Confirm Service", "tag": "plain_text"},
                            "text": {"content": "Continue to submit?", "tag": "plain_text"},
                        }
                    }
                ]
            }
        ]
    }

    for i in WORK_ORDER_LIST:
        if i["value"] == work_order_type:
            list_card["elements"][0]["actions"][0]["placeholder"]["content"] = f"Choose {i['content']} Type"
            for j in i["order_list"]:
                content = j["content"]
                value = j["value"]
                list_card["elements"][0]["actions"][0]["options"].append({
                    "text": {"content": content, "tag": "plain_text"}, "value": value
                })
    return list_card
