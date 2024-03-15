import discord, os
from discord.ext import commands
from datetime import datetime
from utilities import logger
from .bot import bot, PugBot


class EmbedBuilder:
    @staticmethod
    def default_embed(match_id: int, desc: str, match_uuid:str) -> discord.Embed:
        '''
        Returns the default Embed for:
        'PUG | Queue'
        '''
        url: str = "https://images.nightcafe.studio/jobs/bwGzjleUBydQZWQW907U/bwGzjleUBydQZWQW907U--3--obyiw.jpg?tr=w-1600,c-at_max"
        color: discord.Color = discord.Color.blurple()
        time: datetime = datetime.now()
        embed: discord.Embed = discord.Embed(
            title = f'PUG | Queue #{match_id}',
            description = desc,
            color = color,
            timestamp = time
        )
        embed.set_footer(
            text=match_uuid
        )
        embed.set_author(
            icon_url=url, 
            name='Pug Bot'
        )
        return embed
    
    
    @staticmethod
    def build_embed(title, desc, username):
        url = "https://images.nightcafe.studio/jobs/bwGzjleUBydQZWQW907U/bwGzjleUBydQZWQW907U--3--obyiw.jpg?tr=w-1600,c-at_max"
        color = discord.Color.blurple()  
        time = datetime.now()
        embed = discord.Embed(
            title=title,
            description=desc,
            color=color,
            timestamp=time
            )
        embed.set_footer(
            text=username
            )
        embed.set_author(
            icon_url=url,
            name="Pug Bot"
            )
        return embed
    
    @staticmethod
    def error_embed(desc: str, username: str, title: str | None = None) -> discord.Embed:
        url = "https://images.nightcafe.studio/jobs/bwGzjleUBydQZWQW907U/bwGzjleUBydQZWQW907U--3--obyiw.jpg?tr=w-1600,c-at_max"
        color = discord.Color.brand_red()
        time = datetime.now()
        error_embed = discord.Embed(
            title='PUG | Error',
            description=desc,
            color=color,
            timestamp=time
        )
        error_embed.set_footer(
            text=username
        )
        error_embed.set_author(
            icon_url=url,
            name="Pug Bot"
        )
        return error_embed
    
    @staticmethod
    def info_embed(desc: str, username: str) -> discord.Embed:
        url = "https://images.nightcafe.studio/jobs/bwGzjleUBydQZWQW907U/bwGzjleUBydQZWQW907U--3--obyiw.jpg?tr=w-1600,c-at_max"
        color = discord.Color.gold()
        time = datetime.now()
        info_embed = discord.Embed(
            title='PUG | Info',
            description=desc,
            color=color,
            timestamp=time
        )
        info_embed.set_footer(
            text=username
        )
        info_embed.set_author(
            icon_url=url,
            name="Pug Bot"
        )
        return info_embed
    
