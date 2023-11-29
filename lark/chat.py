#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This is a sample chat api for lark
"""
import time
import openai

import utils.config as config
import utils.robot as robot
import lark.card as card


openai.api_key = config.app_config().CHAT_KEY


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


def get_gpt3_response(message_id, context):
    card_send = robot.reply_card(message_id, card.answer("Waiting a moment...", fresh=True))
    card_id = card_send.message_id
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
