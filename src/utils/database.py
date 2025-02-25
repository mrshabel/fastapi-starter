import sqlite3
from sqlmodel import Table, func, col
from datetime import date
from enum import Enum


def build_query_filter(
    model: Table, query: dict[str, str | int | float | bool | date | Enum | list[int]]
) -> list:
    """Construct a query filter using SQL-like syntax for the different data types"""

    filter = []
    for field, value in query.items():
        column = col(getattr(model, field))

        # string instance
        if isinstance(value, str):
            filter.append(column.ilike(f"%{value}%"))
        # integer, float, boolean
        elif isinstance(value, (int, float, bool)):
            filter.append(column == value)
        # date. cast datetime or date field as a valid sql date
        elif isinstance(value, date):
            filter.append(func.date(column) == value)
        # enum
        elif isinstance(value, Enum):
            filter.append(column == value.value)
        # arrays
        elif isinstance(value, list):
            filter.append(column.in_(value))

    return filter


def parse_sqlite_integrity_error(e: sqlite3.IntegrityError) -> str:
    """Parses and sanitizes SQLite IntegrityError messages."""
    error_message = str(e)

    if "UNIQUE constraint failed" in error_message:
        # extract conflicting column
        try:
            column_name = (
                error_message.split("\n")[0]
                .split("UNIQUE constraint failed: ")[1]
                .split(".")[1]
            )
            return f"A record with that {column_name} already exists."
        except IndexError:
            return "A record with that value already exists."

    elif "FOREIGN KEY constraint failed" in error_message:
        # extract the failing table
        try:
            table_name = error_message.split("FOREIGN KEY constraint failed: ")[
                1
            ].split(".")[0]
            return f"The related {table_name} record does not exist."
        except IndexError:
            return "A related record does not exist."

    elif "CHECK constraint failed" in error_message:
        return "The provided data violates a check constraint."

    # return default response
    return "An unexpected error occurred."
