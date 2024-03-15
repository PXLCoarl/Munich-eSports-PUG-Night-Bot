from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import discord



@dataclass(frozen=True)
class MapPools:
    custom_map_pool: Optional[list[str]] = None
    mapcore_list: List[Tuple[str, int]] = field(default_factory=lambda: [("de_mutiny", 3070766070), ("de_biome", 3075706807), ("de_dharma", 3070706420), ("de_iris", 3116932017), ("de_outlaw", 3096484739), ("de_akiba", 3108513658), ("de_scotland", 3090090471)])
    active_duty: list[str] = field(default_factory=lambda: ["de_mirage", "de_vertigo", "de_nuke", "de_ancient", "de_anubis", "de_inferno", "de_overpass"])
    all_maps: list[str] = field(default_factory=lambda: ["de_dust2", "de_mirage", "de_vertigo", "de_nuke", "cs_italy", "de_overpass", "de_ancient", "cs_office", "de_anubis", "de_inferno"])

@dataclass
class MatchContext:
    map_pool: List = field(default_factory=list)
    interaction: discord.Interaction = None
    players: List[Dict[int, int]] = field(default_factory=list)
    teams: List = field(default_factory=list)
    team1: List[int] = field(default_factory=list)
    team2: List[int] = field(default_factory=list)
    

@dataclass
class MatchData:
    id: int
    interaction: discord.Interaction
    people_in_queue: Dict[int, str] = field(default_factory=dict)
    
    
@dataclass
class PugContext:
    queue_flag: bool = False
    people_in_queue: Dict[int, str] = field(default_factory=dict)
    
@dataclass
class TestData:
    optionlist: List[int]