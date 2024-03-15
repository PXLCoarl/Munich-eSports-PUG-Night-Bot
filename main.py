from utilities import logger
from DiscordBot import bot
from api import run_flask
import os, sqlite3, discord, threading, signal
from dotenv import load_dotenv


db_path = 'static/app.db'

def create_dotenv():
    if not os.path.exists('.env'):
        with open('.env', 'w') as file:
            file.write(
f'''# Settings:

# Enter your Discord Bot Token (https://discord.com/developers/applications)
DISCORD_TOKEN=None
# Enter your Faceit API Token (https://developers.faceit.com/)           
FACEIT_TOKEN=None
# Path to local database                                            
DB_PATH={db_path}
# Port on which the webinterface is running                                                                     
WEB_INTERFACE=5050 
'''
)
        logger.info("Created .env, please add your Discord Bot Token and your Faceit API Token or else the Bot wont run!")
        exit()
    else:
        load_dotenv('.env')

def create_pug_tables():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS
                            match(
                                id INTEGER PRIMARY KEY,
                                uuid TEXT UNIQUE,
                                message_id INTEGER,
                                voting_team INTEGER
                            )
                    """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS
                            queue(
                                row INTEGER PRIMARY KEY AUTOINCREMENT,
                                uuid TEXT,
                                name TEXT,
                                discord_id TEXT,  
                                
                                FOREIGN KEY (uuid) REFERENCES match(uuid) 
                            )                   
                    """)

        cursor.execute("""CREATE TABLE IF NOT EXISTS
                            map_pool(
                                row INTEGER PRIMARY KEY AUTOINCREMENT,
                                uuid TEXT,
                                map TEXT,
                                
                                FOREIGN KEY (uuid) REFERENCES match(uuid)
                            )
                        """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS
                            teams(
                                row INTEGER PRIMARY KEY AUTOINCREMENT,
                                uuid TEXT,
                                name TEXT,
                                discord_id TEXT,
                                team_flag TEXT,
                                captain_flag INTEGER,
                                
                                FOREIGN KEY (uuid) REFERENCES match(uuid)
                            )
                    """)
        
        conn.commit()

def create_db():
    database_folder = 'static'
    if not os.path.exists(database_folder):
        os.mkdir(database_folder)
        logger.info("Created Database Folder")

    #db_path = os.path.join(database_folder, 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_links (
            discord_id INTEGER PRIMARY KEY,
            steam_id64 INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Loaded Database")


create_dotenv()
create_db()
create_pug_tables()


flask_thread = threading.Thread(target=run_flask)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")



if __name__ == '__main__':    
    
    flask_thread.start()
    
    try:
        bot.run(token=DISCORD_TOKEN, log_handler=None)
    except discord.errors.HTTPException as e:
        logger.error(f"An HTTP error occurred: {e}")
    except discord.errors.LoginFailure as e:
        logger.error(f"Failed to log in: {e}")
    except discord.errors.RateLimited as e:
        logger.error(f"We are being rate limited: {e}")
    except discord.errors.GatewayNotFound as e:
        logger.error(f"Gateway not found: {e}")
    except discord.errors.DiscordException as e:
        logger.error(f"A Discord exception occurred: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    
    #flask_process.wait()
    flask_thread.join()
        
    