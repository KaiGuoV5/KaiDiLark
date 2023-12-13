#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is a command parser.
"""
import re
from abc import abstractmethod, ABC
from typing import List

import lark_oapi as lark
from lark_oapi import logger
from lark_oapi.api.im.v1 import P2ImMessageReceiveV1Data, ListChat

import utils.robot as robot
import lark.card as card
import lark.chat as chat
import lark.work_order as order
from utils.config import app_config


class BaseCommand(ABC):
    def __init__(self, event: P2ImMessageReceiveV1Data, cmd_args: List[str]):
        self.event = event
        self.message = event.message
        self.chat_type = self.message.chat_type
        self.content = lark.json.loads(self.message.content)
        self.text = self.content['text']
        self.mentions = self.message.mentions
        self.sender = self.event.sender
        self.args = cmd_args

    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError


class IDCommandP2P(BaseCommand):
    def execute(self) -> None:
        mentions = self.mentions is not None and len(self.mentions) >= 1
        at_user_id = self.sender.sender_id.user_id if not mentions else self.mentions[0].id.user_id
        at_open_id = self.sender.sender_id.open_id if not mentions else self.mentions[0].id.open_id
        robot.reply_card(self.message.message_id, card.uid(at_user_id, at_open_id, mentions))


class GroupCommand(BaseCommand):
    def execute(self) -> None:
        if len(self.args) < 1:
            robot.reply_text(self.message.message_id, "group list/delete")
            return
        sub_command = self.args[0]
        if sub_command == "list":
            group_list: List[ListChat] = robot.get_group_list()
            robot.reply_card(self.message.message_id, card.groups(group_list))
            return
        if sub_command == "delete":
            if len(self.args) < 2:
                robot.reply_text(self.message.message_id, "group delete <group_id>")
                return
            chat_ids = self.args[1:]
            ret_msg = ""
            for chat_id in chat_ids:
                if not robot.delete_group(chat_id):
                    ret_msg += f"delete group {chat_id} failed\n"
                else:
                    ret_msg += f"delete group {chat_id} success\n"
            robot.reply_text(self.message.message_id, ret_msg)
            return


class OtherCommand(BaseCommand):
    def execute(self) -> None:
        chat.get_gpt3_response(self.sender.sender_id.user_id, self.message.message_id, self.text)


class OrderCommand(BaseCommand):
    def execute(self) -> None:
        order.reply(self.message.message_id)


class PromptCommand(BaseCommand):
    def execute(self) -> None:
        if len(self.args) < 1:
            robot.reply_text(self.message.message_id, "prompt <prompt>")
            return
        if self.args[0] == "info":
            chat_p2p = chat.get_chat_p2p(self.sender.sender_id.user_id)
            robot.reply_text(self.message.message_id, chat_p2p)
        else:
            text = " ".join(self.args)
            chat.insert_prompt(self.sender.sender_id.user_id, text)
            robot.reply_text(self.message.message_id, "prompt success")


class ChatClearCommand(BaseCommand):
    def execute(self) -> None:
        chat.clear_chat_p2p(self.sender.sender_id.user_id)
        robot.reply_text(self.message.message_id, "clear success")


class IDCommand(BaseCommand):
    def execute(self) -> None:
        robot.reply_text(self.message.message_id, self.message.chat_id)


class DoneCommand(BaseCommand):
    def execute(self) -> None:
        order.done(self.message.chat_id)


class OperatorCommand(BaseCommand):
    def execute(self) -> None:
        if len(self.args) < 2:
            robot.reply_text(self.message.message_id, "operator <@operator>")
            return
        order.change_operator(self.message.chat_id, self.sender.sender_id.user_id, self.mentions[1].id.user_id)


COMMAND_P2P = [
    {
        "command": "id",
        "usage": "id [@user]: get yourself or other user id",
        "handler": IDCommandP2P,
    },
    {
        "command": "group",
        "usage": "group list: display group list\n\tgroup delete <group_id1 group_id2 ...>: delete group[s]",
        "handler": GroupCommand,
    },
    {
        "command": "order",
        "usage": "order: work order",
        "handler": OrderCommand,
    },
    {
        "command": "prompt",
        "usage": "prompt info: display prompt info\n\tprompt <prompt>: insert prompt",
        "handler": PromptCommand,
    },
    {
        "command": "clear",
        "usage": "clear: clear chat prompt and history and model",
        "handler": ChatClearCommand,
    }
]

COMMAND_GROUP = [
    {
        "command": "id",
        "usage": "id: get group id",
        "handler": IDCommand,
    },
    {
        "command": "done",
        "usage": "done: close work order",
        "handler": DoneCommand,
    },
    {
        "command": "close",
        "usage": "close: close work order",
        "handler": DoneCommand,
    },
    {
        "command": "operator",
        "usage": "operator <@operator>: change work order operator",
        "handler": OperatorCommand,
    },
]


def get_command_class_p2p(command: str):
    for p2p in COMMAND_P2P:
        if p2p['command'] == command:
            return p2p['handler']
    return None


def get_command_class_group(command):
    for group in COMMAND_GROUP:
        if group['command'] == command:
            return group['handler']
    return None


def usage(chat_type: str):
    display_usage = ""
    if chat_type == 'p2p':
        display_usage = "Usage:\n"
        for p2p in COMMAND_P2P:
            display_usage += f"\t{p2p['usage']}\n"
    if chat_type == 'group':
        display_usage = "Usage:\n"
        for group in COMMAND_GROUP:
            display_usage += f"\t{group['usage']}\n"
    return display_usage


def parse_command(chat_type: str, text: str):
    if chat_type == 'p2p':
        return text.split()[0]
    if chat_type == 'group':
        return text.split()[1]


def parse_args(chat_type: str, text: str):
    if chat_type == 'p2p':
        return text.split()[1:]
    if chat_type == 'group':
        return text.split()[2:]


def handle_text(event: P2ImMessageReceiveV1Data):
    content = lark.json.loads(event.message.content)
    text = content['text']
    chat_type = event.message.chat_type
    command = parse_command(chat_type, text)
    if command == 'help':
        robot.reply_text(event.message.message_id, usage(chat_type))
        return
    args = parse_args(chat_type, text)
    if event.message.chat_type == 'p2p':
        cmd_class = get_command_class_p2p(command)
        if cmd_class is None:
            cmd_class = OtherCommand
    else:
        pattern = re.compile(app_config().ROBOT_NAME)
        mentions = event.message.mentions
        if mentions is None or re.search(pattern, mentions[0].name) is None:
            logger.error(f"this message not for robot: {event.message.content}")
            return
        cmd_class = get_command_class_group(command)
        if cmd_class is None:
            return
    cmd = cmd_class(event, args)

    cmd.execute()


if __name__ == '__main__':
    print(usage('p2p'))
    print(usage('group'))
