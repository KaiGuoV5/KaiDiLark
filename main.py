#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 This is a sample Python project for lark robot.
 This project is executed when you run `python main.py`.
"""
import argparse
import os
import re

from flask import Flask
from typing import Any

import lark_oapi as lark
from lark_oapi import logger
from lark_oapi.adapter.flask import parse_req, parse_resp
from lark_oapi.api.application.v6 import P2ApplicationBotMenuV6
from lark_oapi.api.im.v1 import P2ImChatMemberBotAddedV1, P2ImMessageReceiveV1, P2ImMessageReceiveV1Data

app = Flask(__name__)

ROBOT_NAME = os.environ.get("ROBOT_NAME", "KaiDiLark")


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
            logger.debug("receive p2p message: {event_.message.content}")
            return
        elif chat_type == 'group':
            pattern = re.compile(ROBOT_NAME)
            if mentions is None or re.search(pattern, mentions[0].name) is None:
                logger.error(f"this message not for robot: {event_.message.content}")
                return
            logger.debug("receive group message: {event_.message.content}")
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
    """ add this robot to a group """
    if data.event is None:
        logger.error("robot add group data is None")
        return
    logger.debug(f"robot add group: {data.event.chat_id}")


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
def event():
    response = handler_event.do(parse_req())
    return parse_resp(response)


@app.route('/card', methods=['POST'])
def card():
    response = handler_card.do(parse_req())
    return parse_resp(response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=7788, type=int, help='port number')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)
