import json
from rcon.source import Client
from typing import Any, List, Dict, Union


def get_server_ids():
    with open('static/servers.json', 'r') as file:
        data = json.load(file)
        serverlist = data['Servers']
        server_ids = [server['Id'] for server in serverlist]
    return server_ids


async def get_servers() -> List[Dict[str, Union[int, str]]]:
    '''
    Expected result:
    [
        {
            "Id": int,
            "IP": str|int,
            "Port": int,
            "Password": str,
            "RconPort": int,
            "RconPassword": str
        }
    ]
    '''
    with open('static/servers.json', 'r') as file:
        data: dict = json.load(file)
        serverlist: List[Dict[str, Union[int, str]]] = data.get("Servers", [])
    return serverlist

async def query_servers(serverlist: list) -> int | None:
    from . import logger
    for server in serverlist:
        try:
            with Client(server['IP'], server['RconPort'], passwd=server['RconPassword'], timeout=1.5) as client:
                response = client.run('get5_status')
            response = json.loads(response)
            if response['gamestate'] == 'none':
                return server['Id']

            if response['gamestate'] != 'none':
                return -1
        
        except Exception as error:
            logger.error(f"An error has occured while querying servers: {error}")
            
    return None

async def fetch_server_data(server_id: int) -> dict[str, Any]:
    with open('static/servers.json', 'r') as file:
        data = json.load(file)
        servers = data['Servers']
        for server in servers:
            if server['Id'] == server_id:
                server_ip: str = server['IP']
                server_port: int = server['Port']
                passwd: str = server['Password']
                rcon_port: int = server['RconPort']
                rcon_passwd: str = server['RconPassword']
                return {'IP':server_ip, 'PORT':server_port, 'PASSWD': passwd,'RCON_PORT':rcon_port, 'RCON_PASSWD':rcon_passwd}
        else:
            return None