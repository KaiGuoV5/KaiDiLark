#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is a sample chat api for lark
"""
import time
from openai import OpenAI

import utils.config as config
import utils.robot as robot
import lark.card as card
from lark_oapi import logger
import store.db_chat_p2p as db_chat_p2p


def clear_chat_p2p(user_id: str):
    """
    Clears chat data in the database based on the given user ID.
    """
    new_data = db_chat_p2p.ChatP2P(
        user_id=user_id,
        prompts="",
        content="",
    )
    if db_chat_p2p.select_chat_p2p_by_user_id(user_id) is not None:
        db_chat_p2p.clear_chat_p2p_by_user_id(user_id)

    db_chat_p2p.insert_chat_p2p(new_data)


def insert_prompt(user_id: str, prompt: str):
    clear_chat_p2p(user_id)
    db_chat_p2p.update_chat_p2p_by_user_id(user_id, "prompts", prompt)


def set_chat_model(user_id: str, model: str):
    clear_chat_p2p(user_id)
    db_chat_p2p.update_chat_p2p_by_user_id(user_id, "model", model)


def get_completion_from_messages(messages,
                                 model="gpt-3.5-turbo",
                                 temperature=0,
                                 max_tokens=500,
                                 stream=False):
    client = OpenAI(
        api_key=config.app_config().CHAT_KEY,
    )
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream
    )
    return response


def get_gpt3_response(user_id: str, message_id: str, context):
    card_send = robot.reply_card(message_id, card.answer("Waiting a moment...", fresh=True))
    card_id = card_send.message_id
    data = db_chat_p2p.select_chat_p2p_by_user_id(user_id)
    if data is not None:
        prompt = data.prompts
        history_context = data.content
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
    stream = get_completion_from_messages(messages, stream=True)
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            stream_message = chunk.choices[0].delta.content
            stream_messages += stream_message
        current_time = time.time()
        if current_time - start_time > 0.7:
            robot.refresh_card(card_id, card.answer(stream_messages, fresh=True))
            start_time = current_time

    robot.refresh_card(card_id, card.answer(stream_messages, fresh=False))


def summary(chat_id: str, context):
    sys_content = "Please summarize the following dialog and return the summary in markdown format."
    messages = [
        {"role": "system", "content": sys_content},
        {"role": "user", "content": context},
    ]
    response = get_completion_from_messages(messages)
    robot.send_card("chat_id", chat_id, card.markdown(response.choices[0].message.content))


if __name__ == '__main__':
    pass
