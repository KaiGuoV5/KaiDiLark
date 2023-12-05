#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is a sample chat api for lark
"""
import time
import openai
import datetime

import utils.config as config
import utils.robot as robot
import lark.card as card
from lark_oapi import logger
import store.db_chat_p2p as db_chat_p2p


openai.api_key = config.app_config().CHAT_KEY


def clear_chat_p2p(user_id: str):
    """
    Clears chat data in the database based on the given user ID.
    """
    new_data = db_chat_p2p.ChatP2PEvent(
        user_id=user_id,
        prompts="",
        content="",
        create_time=datetime.datetime.now().timestamp(),
        update_time=datetime.datetime.now().timestamp()
    )
    if db_chat_p2p.select_chat_p2p_by_user_id(user_id) is not None:
        db_chat_p2p.clear_chat_p2p_by_user_id(user_id)

    db_chat_p2p.insert_chat_p2p(new_data)


def insert_prompt(user_id: str, prompt: str):
    clear_chat_p2p(user_id)
    db_chat_p2p.update_chat_p2p_by_user_id(user_id, "prompts", prompt)


def get_completion_from_messages(messages,
                                 model="gpt-3.5-turbo",
                                 temperature=0,
                                 max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True
    )
    return response


def get_gpt3_response(user_id: str, message_id: str, context):
    card_send = robot.reply_card(message_id, card.answer("Waiting a moment...", fresh=True))
    card_id = card_send.message_id
    data = db_chat_p2p.select_chat_p2p_by_user_id(user_id)
    if data is not None:
        prompt = data[2]
        history_context = data[3]
        context = prompt + history_context + context
    else:
        msg = "sorry,no chat p2p data"
        logger.error(msg)
        robot.refresh_card(card_id, card.answer(msg, fresh=False))
        return
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": context},
    ]
    stream_messages = ""
    start_time = time.time()
    response = get_completion_from_messages(messages)
    for chunk in response:
        delta = chunk["choices"][0]["delta"]
        if "content" in delta:
            stream_message = delta["content"]
            stream_messages += stream_message
        current_time = time.time()
        if current_time - start_time > 0.7:
            robot.refresh_card(card_id, card.answer(stream_messages, fresh=True))
            start_time = current_time

    robot.refresh_card(card_id, card.answer(stream_messages, fresh=False))
