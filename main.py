#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is a sample Python project for lark robot.
    This project is executed when you run `python main.py`.
"""
import argparse
import os

from concurrent.futures import ThreadPoolExecutor

from flask import Flask
from flask_apscheduler import APScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Any

import lark_oapi as lark
from lark_oapi import logger
from lark_oapi.adapter.flask import parse_req, parse_resp
from lark_oapi.api.application.v6 import P2ApplicationBotMenuV6
from lark_oapi.api.im.v1 import (
    P2ImChatMemberBotAddedV1, P2ImMessageReceiveV1, P2ImMessageReceiveV1Data
)

from lark.command import handle_text
from utils.config import app_config
import utils.robot as robot
import lark.card as card
import lark.work_order as order

app = Flask(__name__)

executor = ThreadPoolExecutor(8)

scheduler = APScheduler()

ROBOT_NAME = os.environ.get("ROBOT_NAME", "KaiDiLark")


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    """message receive event"""
    data_str = lark.JSON.marshal(data)
    logger.debug("receive message\n" + data_str)

    event_: P2ImMessageReceiveV1Data = data.event
    if event_ is None or event_.message is None:
        return
    msg_type = event_.message.message_type

    if msg_type != 'text':
        logger.error("not support message type: {msg_type}")
        return

    executor.submit(handle_text, event_)


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

    scheduler.init_app(app)
    scheduler.add_job(id='check_order', func=order.check, trigger=CronTrigger.from_crontab('* 1-18 * * *'))
    scheduler.start()

    app.run(host='0.0.0.0', port=args.port)
