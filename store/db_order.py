#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    database for work order
"""
import datetime
from typing import List, Type, Optional

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, func, event
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

WORK_ORDER_DB_FILE = '/tmp/work_order.db'


class WorkOrder(Base):
    __tablename__ = 'work_order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(255), nullable=True, default="")
    applicant = Column(String(255), nullable=True, default="")
    operator = Column(String(255), nullable=True, default="")
    status = Column(Boolean, nullable=True, default=False)
    classify = Column(String(255), nullable=True, default="")
    description = Column(String(255), nullable=True, default="")
    create_time = Column(DateTime, default=func.current_timestamp())
    update_time = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    deadline = Column(DateTime, nullable=True, default=func.current_timestamp())


engine_work_order = create_engine(f"sqlite:///{WORK_ORDER_DB_FILE}")
# Create the tables if they don't exist
Base.metadata.create_all(engine_work_order)
# Create a session
SessionWorkOrder = sessionmaker(bind=engine_work_order)
# Set the session
session_work_order = SessionWorkOrder()


# Define a listener function to update the timestamp before a WorkOrder is updated
@event.listens_for(WorkOrder, "before_update")
def update_time(target):
    """
    Update the timestamp of a WorkOrder before it is updated.

    Args:
        target: The WorkOrder instance being updated.
    """
    target.update_time = func.current_timestamp()


def insert_work_order(work_order: WorkOrder):
    """
    Insert a work order into the work_order table in the database.

    Parameters:
        work_order (WorkOrder): The work order to be inserted.

    Returns:
        None
    """
    session_work_order.add(work_order)
    session_work_order.commit()


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
    session_work_order.query(WorkOrder).filter_by(id=order_id).update({key: content})
    session_work_order.commit()


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
    session_work_order.query(WorkOrder).filter_by(chat_id=chat_id).update({key: content})
    session_work_order.commit()


def select_work_order_all() -> List[Type[WorkOrder]]:
    """
    Selects all work orders from the database.

    Returns:
        list[WorkOrder]: A list of selected work orders or an empty list if not found.
    """
    return session_work_order.query(WorkOrder).all()


def select_work_order_by_chat_id(chat_id: str) -> Optional[Type[WorkOrder]]:
    """
    Selects a work order from the database based on the given chat ID.

    Parameters:
        chat_id (str): The chat ID of the work order to select.

    Returns:
        Optional[WorkOrder]: A selected work order or None if not found.
    """
    return session_work_order.query(WorkOrder).filter_by(chat_id=chat_id).first()


def select_work_order_by_status_time(status) -> List[Type[WorkOrder]]:
    """
    Selects a work order from the database based on the given status and time.

    Parameters:
        status (bool): The status of the work order to select.

    Returns:
        list[WorkOrder]: A list of selected work orders or an empty list if not found.
    """
    localtime = datetime.datetime.now()
    return (
        session_work_order.query(WorkOrder)
        .filter(WorkOrder.status == status)
        .filter(WorkOrder.deadline <= localtime)
        .all()
    )


if __name__ == '__main__':

    ret = select_work_order_all()
    for i in ret:
        print(i.chat_id, i.applicant, i.operator, i.status, i.classify,
              i.description, i.create_time, i.update_time, i.deadline)
