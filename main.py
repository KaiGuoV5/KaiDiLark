#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is a sample Python project for lark robot.
    This project is executed when you run `python main.py`.
"""
import argparse
import os
import re
from concurrent.futures import ThreadPoolExecutor

from flask import Flask
from typing import Any

import lark_oapi as lark
from lark_oapi import logger
from lark_oapi.adapter.flask import parse_req, parse_resp
from lark_oapi.api.application.v6 import P2ApplicationBotMenuV6
from lark_oapi.api.im.v1 import P2ImChatMemberBotAddedV1, P2ImMessageReceiveV1, P2ImMessageReceiveV1Data

import utils.robot as robot
import lark.card as card

app = Flask(__name__)

executor = ThreadPoolExecutor(8)

ROBOT_NAME = os.environ.get("ROBOT_NAME", "KaiDiLark")


def handle_text_received_p2p(event_p2p: P2ImMessageReceiveV1Data) -> None:
    """
    This function handles private chat messages.
    It receives an event_p2p object and extracts the text content from the message.
    It then performs different actions based on the content of the text.
    """
    logger.debug("p2p text received")
    msg_id = event_p2p.message.message_id
    content = lark.json.loads(event_p2p.message.content)
    text = content['text']
    if text.split(' ')[0] == "id":
        if event_p2p.message.mentions is None or len(event_p2p.message.mentions) < 1:
            mentions = False
            at_user_id = event_p2p.sender.sender_id.user_id
            at_open_id = event_p2p.sender.sender_id.open_id
        else:
            mentions = True
            at_user_id = event_p2p.message.mentions[0].id.user_id
            at_open_id = event_p2p.message.mentions[0].id.open_id
        robot.reply_card(msg_id, card.uid(at_user_id, at_open_id, mentions))
        return


def handle_text_received_group(event_group: P2ImMessageReceiveV1Data) -> None:
    """
    This function handles group chat messages.
    It receives an event_group object and extracts the text content from the message.
    It then performs different actions based on the content of the text.
    """
    logger.debug("group text received")
    msg_id = event_group.message.message_id
    content = lark.json.loads(event_group.message.content)
    text = content['text']
    if len(text.split(' ')) < 2:
        logger.error("invalid text")
        robot.reply_text(msg_id, "What can I do for you?")
        return
    cmd = text.split(' ')[1:]
    if cmd.split(' ')[0] == "id":
        robot.reply_text(msg_id, "group ID: " + event_group.message.chat_id)
        return


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    """message receive event"""
    data_str = lark.JSON.marshal(data)
    logger.debug("receive message\n" + data_str)

    event_: P2ImMessageReceiveV1Data = data.event
    if event_ is None or event_.message is None:
        return
    chat_type = event_.message.chat_type
    msg_type = event_.message.message_type
    mentions = event_.message.mentions

    if msg_type == 'text':
        if chat_type == 'p2p':
            executor.submit(handle_text_received_p2p, event_)
            return
        elif chat_type == 'group':
            pattern = re.compile(ROBOT_NAME)
            if mentions is None or re.search(pattern, mentions[0].name) is None:
                logger.error(f"this message not for robot: {event_.message.content}")
                return
            executor.submit(handle_text_received_group, event_)
            return
        else:
            logger.error("not support chat type: {chat_type}")
            return
    else:
        logger.error("not support message type: {msg_type}")
        return


def do_p2_application_bot_menu_v6(data: P2ApplicationBotMenuV6) -> None:
    """ menu event """
    if data.event is None:
        logger.error("menu data is None")
        return
    logger.debug(f"menu event: {data.event.event_key}")


def do_p2_im_chat_member_bot_added_v1(data: P2ImChatMemberBotAddedV1) -> None:
    """ event for add this robot to a group """
    if data.event is None:
        logger.error("robot add group data is None")
        return
    robot.send_card('chat_id', data.event.chat_id, card.hello())


handler_event = lark.EventDispatcherHandler.builder(
    lark.ENCRYPT_KEY,
    lark.VERIFICATION_TOKEN,
    lark.LogLevel.DEBUG) \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p2_application_bot_menu_v6(do_p2_application_bot_menu_v6) \
    .register_p2_im_chat_member_bot_added_v1(do_p2_im_chat_member_bot_added_v1) \
    .build()


def do_interactive_card(data: lark.Card) -> Any:
    """card event"""
    data_str = lark.JSON.marshal(data)
    logger.debug("receive card\n" + data_str)


handler_card = lark.CardActionHandler.builder(
    lark.ENCRYPT_KEY,
    lark.VERIFICATION_TOKEN,
    lark.LogLevel.DEBUG) \
    .register(do_interactive_card).build()


@app.route('/event', methods=['POST'])
def events():
    response = handler_event.do(parse_req())
    return parse_resp(response)


@app.route('/card', methods=['POST'])
def cards():
    response = handler_card.do(parse_req())
    return parse_resp(response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=7788, type=int, help='port number')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)
