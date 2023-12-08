#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    database for work order
"""
import os
import sqlite3
import dataclasses
import datetime

CHAT_P2P_DB_FILE = '/tmp/chat_p2p.db'


@dataclasses.dataclass(init=False)
class ChatP2PEvent:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    id: int
    user_id: str
    model: str
    prompts: str
    content: str
    create_time: int
    update_time: int


def init_db_if_required():
    """
    Initializes the database if it is required.

    Returns:
        None
    """
    if not os.path.exists(CHAT_P2P_DB_FILE):
        open(CHAT_P2P_DB_FILE, 'w').close()
    conn = sqlite3.connect(CHAT_P2P_DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_p2p (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id TEXT UNIQUE NOT NULL,
        model TEXT,
        prompts TEXT, 
        content TEXT, 
        create_time TIMESTAMP, 
        update_time TIMESTAMP
    )''')
    conn.commit()
    conn.close()


def insert_chat_p2p(chat_p2p: ChatP2PEvent):
    """
    Insert a p2p chat into the chat_p2p table in the database.

    Parameters:
        chat_p2p (ChatP2PEvent): The chat p2p object to be inserted.

    Returns:
        None
    """
    with sqlite3.connect(CHAT_P2P_DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO chat_p2p
            (user_id, model, prompts, content, create_time, update_time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                chat_p2p.user_id,
                chat_p2p.model,
                chat_p2p.prompts,
                chat_p2p.content,
                chat_p2p.create_time,
                chat_p2p.update_time
            ),
        )
        conn.commit()


def update_chat_p2p_by_user_id(user_id: str,  key: str, content: str):
    """
    Updates user chat data in the database based on the given user ID.

    Parameters:
        user_id (str): The user ID of the person to update.
        key (str): The key of the field to update.
        content (str): The new content for the specified field.

    Returns:
        None
    """
    conn = sqlite3.connect(CHAT_P2P_DB_FILE)
    c = conn.cursor()
    c.execute(
        f"UPDATE chat_p2p SET {key} = ?, update_time = ? WHERE user_id = ?",
        (content, datetime.datetime.now().timestamp(), user_id))
    conn.commit()
    conn.close()


def select_chat_p2p_all() -> list:
    """
    Selects all work orders from the database.
    """
    conn = sqlite3.connect(CHAT_P2P_DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM chat_p2p")
    result = c.fetchall()
    conn.close()
    return result


def select_chat_p2p_by_user_id(user_id: str) -> ChatP2PEvent:
    """
    Selects a work order from the database based on the given chat ID.

    Parameters:
        user_id (str): The user ID of the chat person.

    Returns:
        tuple: A tuple containing the selected work order or None if not found.
    """
    conn = sqlite3.connect(CHAT_P2P_DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM chat_p2p WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result


def clear_chat_p2p_by_user_id(user_id):
    conn = sqlite3.connect(CHAT_P2P_DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM chat_p2p WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
