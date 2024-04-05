from rcon.source import Client
from .Runtime import AppSettings
import json


class RconUtils():
    def __init__(self) -> None:
        servers = AppSettings().servers
        self.matches_url = AppSettings().matches_url
        self.servers: dict[int, Client] = {server.get('Id'): Client(server.get('IP'), server.get('RconPort'), passwd=server.get('RconPassword'), timeout=1.5) for server in servers}
        self.clients: dict[int, Client] = {i: client for i, client in enumerate(self.servers)}
        
    @classmethod
    def _connect_all(cls, *, servers: dict[int, Client]) -> None:
        for id, client in servers.items():
            client.connect(login=True)
    
    @classmethod
    def _close_all(cls, *, servers: dict[int, Client]) -> None:
        for id, client in servers.items():
            client.close()
        
        
    def query_all(self) -> dict[int, dict]:
        self._connect_all(servers=self.servers)
        
        responses: dict[int, dict] = {}
        for id, client in self.servers.items():
            response = json.loads(client.run('get5_status'))
            responses[id] = response
        
        self._close_all(servers=self.servers)
        return responses
    
    async def get_free_server(self) -> int:
        from . import logger
        for id, client in self.servers.items():
            try:
                client.connect(login=True)
                response: dict = json.loads(client.run('get5_status'))
                if response.get('gamestate') == 'none':
                    client.close()
                    return id
                
            except Exception as error:
                client.close()
                logger.error(f"An error has occured while querying servers: {error}")
                return -1
        client.close()
        return -1
                
    async def generic_rcon(self, *, server_id: int, command: str, name: str = 'not specified') -> str | bool:
        from . import logger
        server = self.servers.get(server_id)
        server.connect(login=True)
        try:
            response = server.run(command)
            server.close()
            return response
        except Exception as error:
            logger.error(f'Something went wrong during an rcon request with {name = }: {error = }')
            server.close()
            return None
                
    async def push_match(self, *, server_id: int, match_file: str) -> bool:
        from . import logger
        server = self.servers.get(server_id)
        server.connect(login=True)
        try:
            server.run(f'matchzy_loadmatch_url "{self.matches_url}{match_file}"')
            logger.info(f"Match {match_file} was loaded onto server #{server_id}")
            server.close()
            return True
        except Exception as error:
            server.close()
            logger.error(f'Something went wrong during a match push rcon: {error = }')
            return False