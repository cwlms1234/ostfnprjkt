import sqlite3
from datetime import datetime

import pandas as pd


def execute_sql_update(db_name: str, statement: str) -> None:
    try:
        with sqlite3.connect(db_name) as conn:
            conn.execute(statement)
    except sqlite3.OperationalError as e:
        print(f"Failed to open database:\n{e}\n\nStatement:{statement}")


def execute_sql_select(
    db_name: str, statement: str, unpack_first_value: bool = False
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
        print(e)


def execute_sql_to_df(db_name: str, statement: str) -> pd.DataFrame:
    try:
        with sqlite3.connect(db_name) as conn:
            df = pd.read_sql_query(statement, conn)
        return df
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)


def execute_df_to_sql(db_cfg: dict, df: pd.DataFrame) -> None:
    try:
        with sqlite3.connect(database=db_cfg["db_name"]) as conn:
            df.to_sql(
                con=conn, name=db_cfg["table_name"], if_exists="append", index=False
            )
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)

def fetch_newest_timestamp(db_cfg: dict) -> datetime:
    stmnt = f"""SELECT {db_cfg["column_names"]["timestamp"]}
                    FROM {db_cfg["table_name"]} 
                    ORDER BY {db_cfg["column_names"]["timestamp"]}
                    DESC LIMIT 1"""
    timestamp_str = execute_sql_select(db_cfg["db_name"], stmnt, unpack_first_value=True)
    return datetime.fromisoformat(timestamp_str)

def fetch_oldest_timestamp(db_cfg: dict) -> datetime:
    stmnt = f"""SELECT {db_cfg["column_names"]["timestamp"]}
                    FROM {db_cfg["table_name"]} 
                    ORDER BY {db_cfg["column_names"]["timestamp"]}
                    ASC LIMIT 1"""
    timestamp_str = execute_sql_select(db_cfg["db_name"], stmnt, unpack_first_value=True)
    return datetime.fromisoformat(timestamp_str)
    
def fetch_df_for_time_interval(db_cfg: dict, start_date: datetime, end_date:datetime) -> pd.DataFrame:
    stmnt = f"""SELECT * 
                    FROM {db_cfg["table_name"]} 
                    WHERE {db_cfg["column_names"]["timestamp"]} >= '{start_date}' 
                    AND {db_cfg["column_names"]["timestamp"]} <= '{end_date}'"""
    return execute_sql_to_df(db_cfg["db_name"], stmnt)

