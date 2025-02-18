import logging
import sqlite3
from datetime import datetime, timedelta

import pandas as pd

from temperature_control.utils.general_utils import get_timestamp


def execute_sql_update(
    db_name: str, statement: str, logger: logging.Logger | None = None
) -> None:
    try:
        with sqlite3.connect(db_name) as conn:
            conn.execute(statement)
    except sqlite3.OperationalError as e:
        if logger:
            logger.error(f"Failed to open database:\n{e}\n\nStatement:{statement}")


def execute_sql_select(
    db_name: str,
    statement: str,
    unpack_first_value: bool = False,
    logger: logging.Logger | None = None,
) -> list:
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(statement)
            result = cursor.fetchall()
            if unpack_first_value:
                result = result[0][0]
        return result
    except sqlite3.Error as e:
        if logger:
            logger.error(
                f"Error! {e} \n when executing {statement} \n in: execute_sql_select"
            )


def execute_sql_to_df(
    db_name: str, statement: str, logger: logging.Logger | None = None
) -> pd.DataFrame:
    try:
        with sqlite3.connect(db_name) as conn:
            df = pd.read_sql_query(statement, conn)
        return df
    except sqlite3.OperationalError as e:
        if logger:
            logger.error(
                f"Error! {e} \n when executing {statement} \n in: execute_sql_to_df"
            )


def execute_df_to_sql(
    db_cfg: dict, df: pd.DataFrame, logger: logging.Logger | None = None
) -> None:
    try:
        with sqlite3.connect(database=db_cfg["db_name"]) as conn:
            df.to_sql(
                con=conn, name=db_cfg["table_name"], if_exists="append", index=False
            )
    except sqlite3.OperationalError as e:
        if logger:
            logger.error(f"Error! {e} \n when executing execute_df_to_sql")


def fetch_newest_timestamp(
    db_cfg: dict, logger: logging.Logger | None = None
) -> datetime:
    try:
        statement = f"""SELECT {db_cfg["column_names"]["timestamp"]}
                        FROM {db_cfg["table_name"]} 
                        ORDER BY {db_cfg["column_names"]["timestamp"]}
                        DESC LIMIT 1"""
        timestamp_str = execute_sql_select(
            db_cfg["db_name"], statement, unpack_first_value=True
        )
        return datetime.fromisoformat(timestamp_str)
    except sqlite3.OperationalError as e:
        if logger:
            logger.error(
                f"Error! {e} \n when executing {statement} \n in: fetch_newest_timestamp"
            )


def fetch_oldest_timestamp(
    db_cfg: dict, logger: logging.Logger | None = None
) -> datetime:
    try:
        statement = f"""SELECT {db_cfg["column_names"]["timestamp"]}
                        FROM {db_cfg["table_name"]} 
                        ORDER BY {db_cfg["column_names"]["timestamp"]}
                        ASC LIMIT 1"""
        timestamp_str = execute_sql_select(
            db_cfg["db_name"], statement, unpack_first_value=True
        )
        return datetime.fromisoformat(timestamp_str)
    except sqlite3.OperationalError as e:
        if logger:
            logger.error(
                f"Error! {e} \n when executing {statement} \n in: fetch_oldest_timestamp"
            )


def fetch_df_for_time_interval(
    db_cfg: dict,
    start_date: datetime,
    end_date: datetime,
    logger: logging.Logger | None = None,
) -> pd.DataFrame:
    try:
        statement = f"""SELECT * 
                        FROM {db_cfg["table_name"]} 
                        WHERE {db_cfg["column_names"]["timestamp"]} >= '{start_date}' 
                        AND {db_cfg["column_names"]["timestamp"]} <= '{end_date}'"""
        return execute_sql_to_df(db_cfg["db_name"], statement)
    except sqlite3.OperationalError as e:
        if logger:
            logger.error(
                f"Error! {e} \n when executing {statement} \n in: fetch_df_for_time_interval"
            )


def table_maintenance(
    db_cfg: dict,
    logger: logging.Logger | None = None,
):
    try:
        retention_threshold = get_timestamp() - timedelta(days=db_cfg["retention_days"])
        statement = f"""DELETE
                        FROM {db_cfg["table_name"]}
                        WHERE {db_cfg["column_names"]["timestamp"]} < '{retention_threshold}'"""
        execute_sql_update(db_cfg["db_name"], statement, logger)

    except sqlite3.OperationalError as e:
        if logger:
            logger.error(
                f"Error! {e} \n when executing {statement} \n in: table_maintenance"
            )
