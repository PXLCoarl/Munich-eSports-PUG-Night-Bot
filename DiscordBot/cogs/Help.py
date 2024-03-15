from discord.ext import commands
from discord import app_commands, Interaction, Object, Embed, Color
from utilities import get_appsettings

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="List of available commands")
    async def help(self, interaction: Interaction) -> None:
        appsettings = get_appsettings()
        for priv_role in appsettings['roles']:
            role = interaction.guild.get_role(priv_role)
            if role is not None:      
                embed = Embed(
                    type='rich',
                    title='Bot Commands',
                    description='Here are the commands available:',
                    color=Color.blurple()
                )
                embed.add_field(
                    name='/help',
                    value='Displays this help message.',
                    inline=False
                )
                embed.add_field(
                    name='/whoami',
                    value='Shows details about the Steam account linked to your Discord account.',
                    inline=False
                )
                embed.add_field(
                    name='/steam',
                    value='Links your Steam account to the bot.',
                    inline=False
                )
                embed.add_field(
                    name='/pug',
                    value=f'Initiates a new PUG queue. (requires {role.mention})',
                    inline=False
                )
                embed.add_field(
                    name='/rcon',
                    value=f'Send predefined RCON commands to a specific server for administrative purposes. (requires {role.mention})',
                    inline=False
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        
        
async def setup(bot):
    await bot.add_cog(Help(bot),guilds=[Object(id=1019608824023371866), Object(id=841127630564622366), Object(id=615552039027736595)])