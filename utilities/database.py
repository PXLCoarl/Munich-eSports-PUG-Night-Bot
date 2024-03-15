from sqlite3 import connect
from typing import Any


db_path = 'static/app.db'

async def query_db(path: str, query: str, table: str, query_param: str, query_value: Any | None = None) -> list:
    from . import logger
    try:
        with connect(path) as con:
            cursor = con.cursor()
            cursor.execute(f'SELECT {query} FROM {table} WHERE {query_param} = ?', (query_value,))
            results = cursor.fetchall()
            data = [result[0] for result in results]
            return data
    except Exception as error:
        logger.error(f"An error occured during database lookup: {error = }")
        return []
    
async def inject_db(path: str, table: str, columns: list[str], data: tuple) -> bool:
    from . import logger
    try:
        with connect(path) as con:
            cursor = con.cursor()
            placeholders = ','.join(['?' for _ in range(len(data))])
            cursor.execute(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})', (data))
            con.commit()
            return True            
    except Exception as error:
        logger.error(f"An error occured during database injection: {error = }")
        return False
    
async def query_app_context(path: str) -> int:
        with connect(path) as con:
            cursor = con.cursor()
            cursor.execute("SELECT match_id FROM app_context WHERE row = 1")
            result = cursor.fetchone()
            if result is None:
                update_match_context(path, 1)
                return 1
            else:
                match_id = result[0] + 1
                update_match_context(path, match_id)
                return match_id
            
async def insert_message_id(path: str, match_id: int, values: int) -> None:
    try:
        with connect(path) as con:
            cursor = con.cursor()
            cursor.execute('UPDATE match SET message_id = ? WHERE id = ?', (values, match_id))
            con.commit()
    except Exception as error:
        from utilities import logger
        logger.error(f"Something went wrong during insert_message_id: {error}")
        
            
async def update_match_context(path: str, match_id: int) -> None:
        with connect(path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM app_context WHERE row = 1")
            existing_record = cursor.fetchone()
            if existing_record:
                cursor.execute("UPDATE app_context SET match_id = ? WHERE row = 1", (match_id,))
            else:
                cursor.execute("INSERT INTO app_context (row, match_id) VALUES (1, ?)", (match_id,))
            connection.commit()