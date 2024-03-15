import sqlite3
from functools import partial
from .get_logger import setup_logger
from .dataclasses import MapPools, MatchContext, MatchData, PugContext, TestData
from .database import query_db, inject_db, query_app_context, update_match_context, insert_message_id
from .server import get_servers, query_servers, fetch_server_data, get_server_ids
from .rcon import push_match, generic_rcon
from .appsettings import get_appsettings


logger = setup_logger()

#-----------------------------------------------------------
class DBOps:
    path = "static/app.db"
    get_steam_id = partial(query_db, path=path, query='steam_id64', table='user_links', query_param='discord_id')
    insert_match_data = partial(inject_db, path=path, table='match', columns='uuid')
    get_message_id = partial(query_db, path=path, query='message_id', table='match', query_param='id')
    get_match_id = partial(query_db, path=path, query='id', table='match', query_param='uuid')
    get_match_uuid = partial(query_db, path=path, query='uuid', table='match', query_param='id')
    insert_message_id = partial(insert_message_id, path=path)
    
    async def save_user(discord_user_id: int, steam_id64: str, path: str = path):
        try:
            with sqlite3.connect(path) as con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM user_links WHERE discord_id = ?", (discord_user_id,))
                user = cursor.fetchone()
                if user:
                    cursor.execute("UPDATE user_links SET steam_id64 = ? WHERE discord_id = ?", (steam_id64, discord_user_id))
                else:
                    cursor.execute("INSERT INTO user_links (discord_id, steam_id64) VALUES (?, ?)", (discord_user_id, steam_id64))
                con.commit()
        except Exception as error:
            logger.error(f"An error occured during database operation: {error = }")