#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    robot apis
"""
import os
import json
import uuid

from typing import Any, List

import lark_oapi as lark
from lark_oapi import logger

from lark_oapi.api.im.v1 import (
    CreateMessageRequest, CreateMessageRequestBody, CreateMessageResponse, CreateMessageResponseBody,
    ReplyMessageRequest, ReplyMessageRequestBody, ReplyMessageResponse, ReplyMessageResponseBody,
    CreateChatRequest, CreateChatRequestBody, CreateChatResponse,
    CreateChatResponseBody, DeleteChatRequest, DeleteChatResponse, UpdateChatRequest, UpdateChatRequestBody,
    UpdateChatResponse, UserId,
    ListChat, ListChatRequest, ListChatResponse, ListChatResponseBody, UpdateChatRequestBody, UpdateChatResponse
)

from utils.config import app_config

APP_ID = os.environ.get('APP_ID', '123456')
APP_SECRET = os.environ.get('APP_SECRET', '123456')


def __create_client():
    """
    Creates and configures a new Lark client.

    Returns:
        The configured Lark client.
    """
    client = lark.Client.builder() \
        .app_id(app_config().APP_ID) \
        .app_secret(app_config().APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()
    return client


def __send_msg(id_type: str = 'user_id', id_to: str = None, content: dict = None, msg_type: str = 'text') -> bool:
    """
    Send a message.

    Args:
        id_type (str): The type of ID to send the message to. Defaults to 'user_id'.
        id_to (str): The ID of the recipient.
        content (dict): The content of the message.
        msg_type (str): The type of the message. Defaults to 'text'.

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    # Create the client
    cli = __create_client()

    # Build the request
    request = CreateMessageRequest.builder() \
        .receive_id_type(id_type) \
        .request_body(CreateMessageRequestBody.builder()
                      .receive_id(id_to)
                      .content(json.dumps(content))
                      .msg_type(msg_type)
                      .uuid(str(uuid.uuid4()))
                      .build()).build()

    # Send the message
    response = cli.im.v1.message.create(request)

    # Check if the message was sent successfully
    if not response.success():
        logger.error(f"send msg failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return False

    return True


def send_text(id_type: str = 'user_id', id_to: str = None, message: str = None) -> bool:
    content_dict = {'text': message}
    return __send_msg(id_type, id_to, content_dict)


def send_rich(id_type: str = 'user_id', id_to: str = None, content: dict = None) -> bool:
    return __send_msg(id_type, id_to, content, 'post')


def send_card(id_type: str = 'user_id', id_to: str = None, content: dict = None) -> bool:
    return __send_msg(id_type, id_to, content, msg_type='interactive')


def __reply_msg(msg_id: str, content: dict = None, msg_type: str = 'text') -> ReplyMessageResponseBody:
    """
    Reply to a message.
    Args:
        msg_id (str): The ID of the message to reply to.
        content (dict, optional): The content of the reply message. Defaults to None.
        msg_type (str, optional): The type of the reply message. Defaults to 'text'.
    Returns:
        bool: True if the reply is successful, False otherwise.
    """
    # Create a client
    cli = __create_client()

    request: ReplyMessageRequest = ReplyMessageRequest.builder() \
        .message_id(msg_id) \
        .request_body(ReplyMessageRequestBody.builder()
                      .content(json.dumps(content))
                      .msg_type(msg_type)
                      .uuid(str(uuid.uuid4()))
                      .build()).build()
    response: ReplyMessageResponse = cli.im.v1.message.reply(request)
    if not response.success():
        logger.error(f"reply msg failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}")
        return null
    return response.data


def reply_text(msg_id: str, message: str = None) -> ReplyMessageResponseBody:
    content_dict = {'text': message}
    return __reply_msg(msg_id, content_dict)


def reply_rich(msg_id: str, content: dict = None) -> ReplyMessageResponseBody:
    return __reply_msg(msg_id, content, msg_type='post')


def reply_card(msg_id: str, content: dict = None) -> ReplyMessageResponseBody:
    return __reply_msg(msg_id, content, msg_type='interactive')


def refresh_card(id_to: str = None, content: dict = None) -> bool:
    """
    Refreshes a card message.

    Args:
        id_to (str): The ID of the message to refresh.
        content (dict): The updated content of the message.

    Returns:
        bool: True if the message was successfully refreshed, False otherwise.
    """
    # Create a client
    cli = __create_client()

    # Build the request object
    request: PatchMessageRequest = PatchMessageRequest.builder() \
        .message_id(id_to) \
        .request_body(PatchMessageRequestBody.builder()
                      .content(json.dumps(content))
                      .build()).build()

    # Send the patch request
    response: PatchMessageResponse = cli.im.v1.message.patch(request)

    # Check if the response was successful
    if not response.success():
        logger.error(
            f"refresh card failed: code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
        return False

    return True


def create_group(chat_name: str, id_list: list, chat_description: str) -> CreateChatResponseBody:
    """
    Create a group chat.

    Args:
        chat_name (str): The name of the chat.
        id_list (list): A list of user IDs to add to the chat.
        chat_description (str): The description of the chat.

    Returns:
        CreateChatResponseBody: The response body of the create chat API.

    """
    # Create a client
    cli = __create_client()

    # Build the request object
    request: CreateChatRequest = (
        CreateChatRequest.builder()
        .uuid(str(uuid.uuid4()))
        .user_id_type('user_id')
        .set_bot_manager(True)
        .request_body(
            CreateChatRequestBody.builder()
            .avatar('default-avatar_44ae0ca3-e140-494b-956f-78091e348435')
            .name(chat_name)
            .description(chat_description)
            .user_id_list(id_list)
            .chat_mode('group')
            .chat_type('private')
            .join_message_visibility('all_members')
            .leave_message_visibility('all_members')
            .membership_approval('no_approval_required')
            .build()
        )
        .build()
    )

    # Make the API request
    response: CreateChatResponse = cli.im.v1.chat.create(request)

    # Log an error if the API call was not successful
    if not response.success():
        logger.error(
            f"create group failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )

    # Return the response data
    return response.data


def delete_group(chat_id: str) -> bool:
    """
    Deletes a group.

    Args:
        chat_id (str): The ID of the group to delete.

    Returns:
        bool: True if the group was deleted successfully, False otherwise.
    """
    # Create a client
    cli = __create_client()

    # Create a delete chat request
    request: DeleteChatRequest = DeleteChatRequest.builder().chat_id(chat_id).build()

    # Send the delete chat request
    response: DeleteChatResponse = cli.im.v1.chat.delete(request)

    # Check if the delete chat request was successful
    if not response.success():
        logger.error(
            f"delete group failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
        return False

    return True


def update_group_name(chat_id: str, chat_name: str) -> bool:
    """
    Update the name of a group chat.

    Args:
        chat_id (str): The ID of the group chat.
        chat_name (str): The new name for the group chat.

    Returns:
        bool: True if the group name is successfully updated, False otherwise.
    """
    # Create the client
    cli = __create_client()

    # Build the request object
    request: UpdateChatRequest = UpdateChatRequest.builder() \
        .chat_id(chat_id) \
        .user_id_type('user_id') \
        .request_body(UpdateChatRequestBody.builder()
                      .name(chat_name).build()).build()

    # Send the update request to the client
    response: UpdateChatResponse = cli.im.v1.chat.update(request)

    # Check if the update was successful
    if not response.success():
        # Log the error message
        logger.error(
            f"update group name failed, code: {response.code}, msg: {response.msg},log_id: {response.get_log_id()}"
        )
        return False

    return True


def get_group_list() -> List[ListChat]:
    """
    Retrieves the list of group chats which robot in.
    Returns:
        A list of group chat items.
    Raises:
        Exception: If there is an error retrieving the group chat list.
    """
    cli = __create_client()

    request: ListChatRequest = ListChatRequest.builder() \
        .user_id_type('user_id') \
        .sort_type('ByCreateTimeAsc') \
        .build()

    response: ListChatResponse = cli.im.v1.chat.list(request)
    if not response.success():
        logger.error(
            f"get group list failed:: code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
        return []

    group_list = response.data.items
    while response.data.has_more:
        request: ListChatRequest = (
            ListChatRequest.builder()
            .user_id_type('user_id')
            .sort_type('ByCreateTimeAsc')
            .page_token(response.data.page_token)
            .build()
        )

        response: ListChatResponse = cli.im.v1.chat.list(request)
        if not response.success():
            logger.error(
                f"get group list failed: code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            )
            return []
        group_list.extend(response.data.items)
    return group_list
