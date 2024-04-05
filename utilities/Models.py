from sqlalchemy import ForeignKey, Column, String, Integer, VARCHAR
from sqlalchemy.orm import declarative_base, relationship
from typing import Type

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    
    discord_id = Column('discord_id', String, primary_key=True)
    discord_name = Column('discord_name', String)
    steam_id64 = Column('steam_id64', String, unique=True)
    steam_name = Column('steam_name', String)
    steam_url = Column('steam_url', String)
    



class Match(Base):
    __tablename__ = 'match'
    
    match_id = Column('match_id', Integer, primary_key=True)
    match_uuid = Column('match_uuid', String, unique=True)
    players = relationship('Player', back_populates='match')
    maps = relationship('Map', back_populates='match')
    
class Player(Base):    
    __tablename__ = 'players'
    
    row = Column('row', Integer, primary_key=True)
    match_uuid = Column('match_uuid', String, ForeignKey('match.match_uuid'))
    discord_name = Column('discord_name', String)
    discord_id = Column('discord_id', String)
    
    match = relationship('Match', back_populates='players')
    
class Map(Base):
    __tablename__ = 'maps'
    
    row = Column('row', Integer, primary_key=True)
    match_uuid = Column('match_uuid', String, ForeignKey('match.match_uuid'))
    map_name = Column('map_name', String)
    
    match = relationship('Match', back_populates='maps')