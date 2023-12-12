#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    database for work order
"""
from typing import Type, Optional

from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, event
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

CHAT_P2P_DB_FILE = '/tmp/chat_p2p.db'


class ChatP2P(Base):
    __tablename__ = 'chat_p2p'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=True, default="")
    model = Column(String(255), nullable=True, default="")
    prompts = Column(String(1024), nullable=True, default="")
    content = Column(String(1024), nullable=True, default=False)
    create_time = Column(DateTime, default=func.current_timestamp())
    update_time = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


engine_chat_p2p = create_engine(f"sqlite:///{CHAT_P2P_DB_FILE}")
# Create the tables if they don't exist
Base.metadata.create_all(engine_chat_p2p)
# Create a session
SessionChatP2P = sessionmaker(bind=engine_chat_p2p)
# Set the session
session_chat_p2p = SessionChatP2P()


# Define a listener function to update the timestamp before a WorkOrder is updated
@event.listens_for(ChatP2P, "before_update")
def update_time(target):
    """
    Update the timestamp of a WorkOrder before it is updated.

    Args:
        target: The WorkOrder instance being updated.
    """
    target.update_time = func.current_timestamp()


def insert_chat_p2p(chat_p2p: ChatP2P):
    """
    Insert a p2p chat into the chat_p2p table in the database.

    Parameters:
        chat_p2p (ChatP2P): The chat p2p object to be inserted.

    Returns:
        None
    """
    session_chat_p2p.add(chat_p2p)
    session_chat_p2p.commit()


def update_chat_p2p_by_user_id(user_id: str, key: str, content: str):
    """
    Updates user chat data in the database based on the given user ID.

    Parameters:
        user_id (str): The user ID of the person to update.
        key (str): The key of the field to update.
        content (str): The new content for the specified field.

    Returns:
        None
    """
    session_chat_p2p.query(ChatP2P).filter_by(user_id=user_id).update({key: content})
    session_chat_p2p.commit()


def select_chat_p2p_all() -> list[Type[ChatP2P]]:
    """
    Selects all work orders from the database.

    Returns:
        list[ChatP2P]: A list of selected work orders or an empty list if not found.
    """
    return session_chat_p2p.query(ChatP2P).all()


def select_chat_p2p_by_user_id(user_id: str) -> Optional[Type[ChatP2P]]:
    """
    Selects a work order from the database based on the given chat ID.

    Parameters:
        user_id (str): The user ID of the chat person.

    Returns:
        Optional[ChatP2PEvent]: A selected chat p2p or None if not found.
    """
    return session_chat_p2p.query(ChatP2P).filter_by(user_id=user_id).first()


def clear_chat_p2p_by_user_id(user_id):
    """
    Clears chat data in the database based on the given user ID.
    """
    session_chat_p2p.query(ChatP2P).filter_by(user_id=user_id).delete()
    session_chat_p2p.commit()
