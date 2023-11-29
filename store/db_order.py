#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    database for work order
"""
import os
import sqlite3
import dataclasses
import datetime

WORK_ORDER_DB_FILE = '/tmp/work_order.db'


@dataclasses.dataclass(init=False)
class WorkOrderEvent:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    id: int
    chat_id: str
    applicant: str
    operator: str
    status: bool
    classify: str
    description: str
    create_time: int
    update_time: int
    deadline: int


def init_db_if_required():
    """
    Initializes the database if it is required.

    Returns:
        None
    """
    if not os.path.exists(WORK_ORDER_DB_FILE):
        open(WORK_ORDER_DB_FILE, 'w').close()
    conn = sqlite3.connect(WORK_ORDER_DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS work_order (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        chat_id TEXT, 
        applicant TEXT, 
        operator TEXT, 
        status INTEGER, 
        classify TEXT, 
        description TEXT, 
        create_time TIMESTAMP, 
        update_time TIMESTAMP, 
        deadline TIMESTAMP
    )''')
    conn.commit()
    conn.close()


def insert_work_order(work_order: WorkOrderEvent):
    """
    Insert a work order into the work_order table in the database.

    Parameters:
        work_order (WorkOrderEvent): The work order object to be inserted.

    Returns:
        None
    """
    with sqlite3.connect(WORK_ORDER_DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO work_order
            (chat_id, applicant, operator, status, classify, description, create_time, update_time, deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                work_order.chat_id,
                work_order.applicant,
                work_order.operator,
                work_order.status,
                work_order.classify,
                work_order.description,
                work_order.create_time,
                work_order.update_time,
                work_order.deadline,
            ),
        )
        conn.commit()


def update_work_order_by_id(order_id: int, key: str, content):
    """
    Updates a work order in the database by its ID.

    Parameters:
        order_id (int): The ID of the work order to be updated.
        key (str): The field to be updated in the work order.
        content (Any): The new content to be assigned to the specified field.

    Returns:
        None

    Raises:
        None
    """
    conn = sqlite3.connect(WORK_ORDER_DB_FILE)
    c = conn.cursor()
    c.execute(
        f"UPDATE work_order SET {key} = ?, update_time = ? WHERE id = ?",
        (content, datetime.datetime.now().timestamp(), order_id))
    conn.commit()
    conn.close()


def update_work_order_by_chat_id(chat_id: str,  key: str, content: str):
    """
    Updates a work order in the database based on the given chat ID.

    Parameters:
        chat_id (str): The chat ID of the work order to update.
        key (str): The key of the field to update.
        content (str): The new content for the specified field.

    Returns:
        None
    """
    conn = sqlite3.connect(WORK_ORDER_DB_FILE)
    c = conn.cursor()
    c.execute(
        f"UPDATE work_order SET {key} = ?, update_time = ? WHERE chat_id = ?",
        (content, datetime.datetime.now().timestamp(), chat_id))
    conn.commit()
    conn.close()


def select_work_order_all() -> list:
    """
    Selects all work orders from the database.
    """
    conn = sqlite3.connect(WORK_ORDER_DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM work_order")
    result = c.fetchall()
    conn.close()
    return result


def select_work_order_by_chat_id(chat_id: str) -> WorkOrderEvent:
    """
    Selects a work order from the database based on the given chat ID.

    Parameters:
        chat_id (str): The chat ID of the work order to select.

    Returns:
        tuple: A tuple containing the selected work order or None if not found.
    """
    conn = sqlite3.connect(WORK_ORDER_DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM work_order WHERE chat_id = ?", (chat_id,))
    result = c.fetchone()
    conn.close()
    return result


def select_work_order_by_status_time(status: bool, time: float) -> list[WorkOrderEvent]:
    """
    Selects a work order from the database based on the given status and time.

    Parameters:
        status (bool): The status of the work order to select.
        time (int): The time of the work order to select.

    Returns:
        tuple: A tuple containing the selected work order or None if not found.
    """
    conn = sqlite3.connect(WORK_ORDER_DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM work_order WHERE status = ? AND deadline < ?", (status, time))
    result = c.fetchall()
    conn.close()
    return result


if __name__ == '__main__':
    # init_db_if_required()
    # new = WorkOrderEvent()
    # new.chat_id = "123"
    # new.applicant = "123"
    # new.operator = "123"
    # new.status = False
    # new.classify = "123"
    # new.description = "123"
    # new.create_time = datetime.datetime.now().timestamp()
    # new.update_time = datetime.datetime.now().timestamp()
    # new.deadline = (datetime.datetime.now()+datetime.timedelta(days=1)).timestamp()
    # insert_work_order(new)
    ret = select_work_order_all()
    # ret = select_work_order_by_status_time(False, (datetime.datetime.now()+datetime.timedelta(days=1)).timestamp())
    print(ret)
    ret = select_work_order_by_chat_id("123")
    print(ret)

    # get_all_chat_events()
    # app_logger.info(get_chat_context_by_user_id("ab1cd2ef"))
