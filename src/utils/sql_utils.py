import sqlite3

import pandas as pd


def execute_sql_update(db_name: str, statement: str) -> None:
    try:
        with sqlite3.connect(db_name) as conn:
            conn.execute(statement)
    except sqlite3.OperationalError as e:
        print(f"Failed to open database:\n{e}\n\nStatement:{statement}")


def execute_sql_select(db_name: str, statement: str, unpack_first_value: bool = False) -> list:
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
            df.to_sql(con=conn, name=db_cfg["table_name"], if_exists="append", index=False)
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)