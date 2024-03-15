from rcon.source import Client
from .server import fetch_server_data


'''
ToDo:
- do something with the response and integrate proper error handling
'''
async def generic_rcon(ip: str, port: int, passwd: str, command: str, name: str | None = None) -> str:
    from . import logger
    try:
        with Client(ip, port, passwd=passwd, timeout=1.5) as client:
            response = str(client.run(f'{command}'))
            return response
    except Exception as error:
        logger.error(f"Something went wrong during an rcon {name if name is not None else {}} request: {error = }")
        
        
async def push_match(server_id, match_id):
    from . import logger
    server_data = await fetch_server_data(server_id)
    try:
        with Client(server_data['IP'], server_data['RCON_PORT'], passwd=server_data['RCON_PASSWD'], timeout=1.5) as client:
            client.run(f'matchzy_loadmatch_url "https://pugs.pxlcoarl.de/api/matches/match_{match_id}.json')
            logger.info(f"Match #{match_id} was loaded onto server #{server_id}")
    except Exception as error:
        logger.error(f"Something went wrong during a match push rcon: {error = }")