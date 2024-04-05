from .Logger import get_logger
from .Runtime import AppSettings, MapPools, create_db
from .rcon import RconUtils
from .Embeds import Embeds
from .database import DataBaseUtils
from .Models import Player, Match, Map, User
from .MatchHandler import Match_Handler

logger = get_logger(name=__name__)

appsettings = AppSettings()

create_db()
logger.info('Database initialized')