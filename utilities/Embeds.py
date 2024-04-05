from datetime import datetime
from discord import Color, Embed
from datetime import datetime

class Embeds():
    """utility class that holds a bunch of predefined embeds:
    - queue
    - lobby
    - ingame
    - error
    """
    def __init__(self, *, match_id: int, match_uuid: str, info: str | None = None) -> None:
        icon = "https://images.nightcafe.studio/jobs/bwGzjleUBydQZWQW907U/bwGzjleUBydQZWQW907U--3--obyiw.jpg?tr=w-1600,c-at_max"
        name = 'Pug Bot'
        
        self.info: Embed = Info(info=info, timestamp=datetime.now())
        self.info.set_footer(text=match_uuid)
        self.info.set_author(icon_url=icon, name=name)
        
        self.queue: Embed = Queue(match_id=match_id, timestamp=datetime.now())
        self.queue.set_footer(text=match_uuid)
        self.queue.set_author(icon_url=icon, name=name)
        
        self.lobby: Embed = Lobby(match_id=match_id, timestamp=datetime.now())
        self.lobby.set_footer(text=match_uuid)
        self.lobby.set_author(icon_url=icon, name=name)
        
        self.ingame: Embed = Ingame(match_id=match_id, timestamp=datetime.now())
        self.ingame.set_footer(text=match_uuid)
        self.ingame.set_author(icon_url=icon, name=name)
        
        self.error: Embed = Error(timestamp=datetime.now())
        self.error.set_footer(text=match_uuid)
        self.error.set_author(icon_url=icon, name=name)
        
        
        
class Queue(Embed):
    def __init__(self, *, match_id: int, timestamp: datetime | None = datetime.now()) -> None:
        super().__init__(
            color=Color.blurple(),
            title=f'PUG | Queue #{match_id}',
            description="Ready to join the queue?\nIf you already have a profile, just press join, otherwise use </profile:1224853196988616825>.",
            timestamp=timestamp
        )
        
class Lobby(Embed):
    def __init__(self, *, match_id: int, timestamp: datetime | None = datetime.now()) -> None:
        super().__init__(
            color=Color.blurple(),
            title=f'PUG | Lobby #{match_id}',
            description='',
            timestamp=timestamp
        )
        
class Ingame(Embed):
    def __init__(self, *, match_id: int, timestamp: datetime | None = datetime.now()) -> None:
        super().__init__(
            color=Color.blurple(),
            title=f'PUG | Ingame #{match_id}',
            description='',
            timestamp=timestamp
        )
        
class Error(Embed):
    def __init__(self, *, timestamp: datetime | None = datetime.now()) -> None:
        super().__init__(
            color = Color.brand_red(),
            title=f'PUG | Error',
            description='',
            timestamp=timestamp
        )    
        
class Info(Embed):
    def __init__(self, *, info: str, timestamp: datetime | None = datetime.now()) -> None:
        super().__init__(
            color=Color.yellow(),
            title=f'PUG | Info',
            description=info,
            timestamp=timestamp
        )