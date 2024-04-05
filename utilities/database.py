from .Models import Match, Map, Player, User
from .Runtime import AppSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List



class DataBaseUtils():
    def __init__(self) -> None:
        engine = create_engine(AppSettings().db_uri)
        self.Session = sessionmaker(bind=engine)
        self.Match = Match
        self.Map = Map
        self.Player = Player
        self.User = User
        
    
    def fetch_players(self, *, match_uuid: str) -> List[User] | None:
        from . import logger
        with self.Session() as session:
            try:
                players: List[Player] = session.query(Player).filter(Player.match_uuid == match_uuid).all()
                users: List[User] = [session.query(User).filter(User.discord_id == player.discord_id).first() for player in players]
                return users
                
            except Exception as error:
                logger.error(f'Somehting went wrong retrieving the players for {match_uuid = }: {error = }')
                return False
                
    def get_match_id(self, *, match_uuid: str) -> int | None:
        from . import logger
        with self.Session() as session:
            try:
                match: Match = session.query(Match).filter_by(match_uuid=match_uuid).first()
                return match.match_id
            except Exception as error:
                logger.error(f'Something went wrong retrieving the match id for {match_uuid = }: {error = }')
                return -1
    
    
    
    def get_queue_names(self, *, match_uuid: str) -> List[str] | bool:
        from . import logger
        with self.Session() as session:
            try:
                players: List[Player] = session.query(Player).filter(Player.match_uuid == match_uuid).all()
                names = [player.discord_name for player in players]
                return names
            except Exception as error:
                logger.error(f'Something went wrong querying Player names from {match_uuid}: {error = }')
                return False
            
    def _remove_player(self, *, userid: int) -> str:
        with self.Session() as session:
            user = session.query(Player).filter_by(discord_id=userid).first()
            username = user.discord_name
            session.delete(user)
            session.commit()
        return username
            
            
    def remove_player(self, *, match_uuid: str, userid: int) -> List[str] | bool:
        from . import logger
        try:
            username = self._remove_player(userid=userid)
            
            with self.Session() as session:
                players: List[Player] = session.query(Player).filter(Player.match_uuid == match_uuid).all()
                names = [player.discord_name for player in players if player.discord_name != username]
            
                
            return names

        except Exception as error:
            logger.error(f'Something went wrong removing a player from {match_uuid}: {error = }')
            return False
    
    
    def insert_player(self, *, match_uuid: str, userid: int, username: str) -> bool:
        from . import logger
        with self.Session() as session:
            try:
                player = Player(match_uuid = match_uuid, discord_id = userid, discord_name = username)
                session.add(player); session.commit()
                return True
            except Exception as error:
                logger.error(f'Something went wrong inserting player with name {username} into players: {error = }')
                return False
    
    
    def query_queue_for_player(self, *, match_uuid: str, userid: int) -> bool:
        with self.Session() as session:
            player = session.query(Player).filter(Player.discord_id == userid, Player.match_uuid == match_uuid).first()
            if player:
                return True
            else:
                return False
    def query_user(self, *, userid: int) -> bool:
        with self.Session() as session:
            user = session.query(User).filter(User.discord_id == userid).first()
            if user:
                return True
            else:
                return False
    
        
    def create_match(self, *, match_uuid: str, map_pool: list[str]) -> int:
        with self.Session() as session:
            match = Match(match_uuid=match_uuid)
            maps = [Map(match_uuid=match_uuid, map_name=map_name) for map_name in map_pool]
            session.add(match); session.add_all(maps)
            session.commit()
            return match.match_id
        
    def manage_user(self, *, discord_id: str, discord_name: str, steam_id64: str, steam_url: str, steam_name: str) -> bool:
        try:
            with self.Session() as session:
                user = session.query(User).filter(User.discord_id == discord_id).first()
                if user:
                    user.discord_name = discord_name
                    user.steam_id64 = steam_id64
                    user.steam_url = steam_url
                    user.steam_name = steam_name
                    session.commit()
                    return True
                else:
                    new_user = User(discord_id=discord_id, discord_name=discord_name, steam_id64=steam_id64, steam_url=steam_url, steam_name=steam_name)
                    session.add(new_user)
                    session.commit()
                    return True
        except Exception as error:
            from . import logger
            logger.error(f'An error has occured during user management: {error = }')
            return False
    
    