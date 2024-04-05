import os, json
from enum import Enum
from discord import Object
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_db() -> None:
    engine = create_engine(AppSettings().db_uri, echo=False)
    from .Models import Base
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.close()



def load_appsettings(appsettings_path: str) -> dict[str, tuple | list]:
    """loads appsettings

    Args:
        appsettings_path (str): path to appsettings

    Returns:
        dict[str, tuple|list]: {'roles': roles, 'guilds': guilds, 'servers': servers, 'matches_url': matches_url}
    """
    with open(appsettings_path, 'r') as file:
        data: dict = json.load(file)   
        roles: tuple = tuple(data['Settings']['priv_roles'])
        try:
            if roles == ():
                raise ValueError("No privileged roles specified in appsettings.json - please check your configuration!")
            guilds: tuple[Object] = tuple([Object(guild) for guild in data['Settings']['guilds']])
            if guilds == ():
                raise ValueError("No guilds specified in appsettings.json - please check your configuration!")
            servers: list[dict[str, str | int]] = data['Servers']
            if servers == []:
                raise ValueError("No servers specified in appsettings.json - please check your configuration!")
            matches_url: str = data.get("matches_url")
            if matches_url == '':
                raise ValueError("No api url specified in appsettings.json - please check your configuration!")
        except ValueError as error:
            print(f"{error = }")
            import sys
            sys.exit()
        except KeyError as error:
            print(f"{error = }")
            import sys
            sys.exit()
        
        appsettings: dict[str, tuple|list|str] = {'roles': roles, 'guilds': guilds, 'servers': servers, 'matches_url': matches_url}

        return appsettings



class AppSettings():
    def __init__(self) -> None:
        appsettings = load_appsettings(os.getenv('APP_SETTINGS'))
        self.token: str = os.getenv('TOKEN')
        self.faceit_token: str = os.getenv('FACEIT_TOKEN')
        self.db_uri: str = os.getenv('DB_URI')
        self.matches_url: str = appsettings.get('matches_url')
        self.roles: tuple = appsettings.get('roles')
        self.servers: list[dict[str, str | int]] = appsettings.get('servers')
        self.guilds: tuple[Object] = appsettings.get('guilds')
        
        
        
class MapPools(Enum):
    MAPCORE_LIST = [("de_mutiny", 3070766070), ("de_biome", 3075706807), ("de_dharma", 3070706420), ("de_iris", 3116932017), ("de_outlaw", 3096484739), ("de_akiba", 3108513658), ("de_scotland", 3090090471)]
    ALL_MAPS = ["de_dust2", "de_mirage", "de_vertigo", "de_nuke", "cs_italy", "de_overpass", "de_ancient", "cs_office", "de_anubis", "de_inferno"]
    ACTIVE_DUTY = ["de_mirage", "de_vertigo", "de_nuke", "de_ancient", "de_anubis", "de_inferno", "de_overpass"]
    
    def __iter__(self):
        return iter(self.value)