#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    lark.work_order
"""
import datetime

from lark_oapi import logger

import lark.card as card
import utils.robot as robot
import utils.config as config
import store.db_order as db_order

DEFAULT_DEADLINE = (datetime.datetime.now() + datetime.timedelta(minutes=2)).timestamp()


def reply(msg_id: str):
    """ reply work order request """
    robot.reply_card(msg_id, card.work_order_build())


def build(user_id: str, description: str):
    """ build work order """
    format_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    chats_name = f"⌛️Process-Order-{format_time}"
    assist_id = config.app_config().ORDER_ASSISTANT
    id_lists = [assist_id]
    if user_id not in id_lists:
        id_lists.append(user_id)
    res = robot.create_group(chats_name, id_lists, "Work Order")
    robot.send_card("chat_id", res.chat_id, card.work_order_show(chats_name, user_id, assist_id, description))

    new_order = db_order.WorkOrderEvent()
    new_order.chat_id = res.chat_id
    new_order.applicant = user_id
    new_order.operator = assist_id
    new_order.status = False
    new_order.classify = "Work Order"
    new_order.description = description
    new_order.create_time = datetime.datetime.now().timestamp()
    new_order.update_time = datetime.datetime.now().timestamp()
    new_order.deadline = DEFAULT_DEADLINE

    db_order.insert_work_order(new_order)


def check():
    """
    Check the work orders and update their deadlines if necessary.
    """
    localtime = datetime.datetime.now()
    data = db_order.select_work_order_by_status_time(False, localtime.timestamp())
    if not data:
        logger.debug("No work order to check.")
        return

    for result in data:
        order_id = result[0]
        chat_id = result[1]
        operator = result[3]
        db_order.update_work_order_by_id(order_id, "deadline", DEFAULT_DEADLINE)
        # msg = f"<at id={operator}></at> What's going on now?"
        # robot.send_card("chat_id", chat_id, card.markdown(msg))
        robot.send_card("chat_id", chat_id, card.how(operator))


def done(chat_id: str):
    """ update work order status """
    chat_name = robot.get_group_info(chat_id).name
    chat_name_list = chat_name.split('-')
    chat_name_done = "Done-Order-" + chat_name_list[2]
    data = db_order.select_work_order_by_chat_id(chat_id)
    if not data:
        logger.error(f"No this work order {chat_name}.")
        return

    order_id = data[0]
    applicant = data[2]
    robot.update_group_name(chat_id, chat_name_done)
    db_order.update_work_order_by_id(order_id, "status", True)
    msg = f"<at id={applicant}></at> The work order has been completed."
    robot.send_card("chat_id", chat_id, card.markdown(msg))


def change_operator(chat_id: str, operator_orig: str, operator: str):
    """ update work order operator """
    data = db_order.select_work_order_by_chat_id(chat_id)
    if not data:
        logger.error(f"No this work order {chat_id}.")
        return

    operator_now = data[3]
    if operator_orig == operator_now:
        msg = f"<at id={operator_orig}></at> The operator has changed to <at id={operator}></at>."
        robot.send_card("chat_id", chat_id, card.markdown(msg))
    else:
        msg = f"Sorry <at id={operator_orig}></at> you are not the operator, let <at id={operator_now}></at> try again"
        robot.send_card("chat_id", chat_id, card.markdown(msg))
