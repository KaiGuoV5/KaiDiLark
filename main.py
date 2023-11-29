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
from flask_apscheduler import APScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Any, List

import lark_oapi as lark
from lark_oapi import logger
from lark_oapi.adapter.flask import parse_req, parse_resp
from lark_oapi.api.application.v6 import P2ApplicationBotMenuV6
from lark_oapi.api.im.v1 import P2ImChatMemberBotAddedV1, P2ImMessageReceiveV1, P2ImMessageReceiveV1Data, ListChat

from utils.config import app_config
import utils.robot as robot
import lark.card as card
import lark.chat as chat
import lark.work_order as order
import store.db_order as db_order

app = Flask(__name__)

executor = ThreadPoolExecutor(8)

scheduler = APScheduler()

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

    command, *cmd_args = text.split()

    if command == "id":
        mentions = event_p2p.message.mentions is not None and len(event_p2p.message.mentions) >= 1
        at_user_id = event_p2p.sender.sender_id.user_id if not mentions else event_p2p.message.mentions[0].id.user_id
        at_open_id = event_p2p.sender.sender_id.open_id if not mentions else event_p2p.message.mentions[0].id.open_id
        robot.reply_card(msg_id, card.uid(at_user_id, at_open_id, mentions))
        return

    if command == "group":
        if len(cmd_args) < 1:
            robot.reply_text(msg_id, "group list/delete")
            return
        sub_command = cmd_args[0]
        if sub_command == "list":
            group_list: List[ListChat] = robot.get_group_list()
            robot.reply_card(event_p2p.message.message_id, card.groups(group_list))
            return
        if sub_command == "delete":
            if len(cmd_args) != 2:
                robot.reply_text(event_p2p.message.message_id, "group delete <group_id>")
                return
            chat_id = cmd_args[1]
            ret_msg = "delete group failed" if not robot.delete_group(chat_id) else "delete group success"
            robot.reply_text(event_p2p.message.message_id, ret_msg)
            return
        return

    if command == "order":
        order.reply(msg_id)
        return

    chat.get_gpt3_response(msg_id, text)


def handle_text_received_group(event_group: P2ImMessageReceiveV1Data) -> None:
    """
    This function handles group chat messages.
    It receives an event_group object and extracts the text content from the message.
    It then performs different actions based on the content of the text.
    """
    logger.debug("group text received")
    message = event_group.message
    msg_id = message.message_id
    content = lark.json.loads(message.content)
    text = content['text']
    words = text.split()
    if len(words) < 2:
        logger.error("invalid text")
        robot.reply_text(msg_id, "What can I do for you?")
        return
    cmd = words[1:]
    if cmd[0] == "id":
        robot.reply_text(msg_id, message.chat_id)
        return
    if cmd[0] == "done" or cmd[0] == "close":
        order.done(message.chat_id)
        return
    if cmd[0] == "operator":
        if len(cmd) != 2:
            robot.reply_text(msg_id, "operator <@operator>")
            return
        order.change_operator(message.chat_id, event_group.sender.sender_id.user_id, message.mentions[1].id.user_id)
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

    if msg_type != 'text':
        logger.error("not support message type: {msg_type}")
        return

    if chat_type == 'p2p':
        executor.submit(handle_text_received_p2p, event_)
        return

    if chat_type == 'group':
        pattern = re.compile(app_config().ROBOT_NAME)
        if mentions is None or re.search(pattern, mentions[0].name) is None:
            logger.error(f"this message not for robot: {event_.message.content}")
            return
        executor.submit(handle_text_received_group, event_)
        return

    logger.error("not support chat type: {chat_type}")
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
    app_config().ENCRYPT_KEY,
    app_config().VERIFICATION_TOKEN,
    lark.LogLevel.DEBUG) \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p2_application_bot_menu_v6(do_p2_application_bot_menu_v6) \
    .register_p2_im_chat_member_bot_added_v1(do_p2_im_chat_member_bot_added_v1) \
    .build()


def do_interactive_card(data: lark.Card) -> Any:
    """card event"""
    data_str = lark.JSON.marshal(data)
    logger.debug("receive card\n" + data_str)
    action = data.action
    action_value = action.value
    action_val_str = lark.JSON.marshal(action_value)
    action_val_json = lark.json.loads(action_val_str)
    action_text = action_val_json["action"]
    if action_text == "work_order":
        logger.debug("work order select")
        return card.work_order_select()
    if action_text == "work_order_type":
        logger.debug("work order type select")
        return card.work_order_list(action.option)
    if action_text == "work_order_submit":
        logger.debug("work order submit")
        executor.submit(order.build, data.user_id, action.option)
    if action_text == "done":
        logger.debug("work order done")
        executor.submit(order.done, data.open_chat_id)


handler_card = lark.CardActionHandler.builder(
    app_config().ENCRYPT_KEY,
    app_config().VERIFICATION_TOKEN,
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

    db_order.init_db_if_required()

    scheduler.init_app(app)
    scheduler.add_job(id='check_order', func=order.check, trigger=CronTrigger.from_crontab('* 1-18 * * *'))
    scheduler.start()

    app.run(host='0.0.0.0', port=args.port)
