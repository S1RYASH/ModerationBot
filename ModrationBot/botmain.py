import discord
from discord.ext import commands
import asyncpg
import socket
from discord.ui import View  , Button , Select

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):

        self.db = await asyncpg.create_pool(dsn= f"postgres://XXX:XXX@3.7.241.46:5432/pg_mod")
        print("Connection to db DONE!")
        guilds = await self.db.fetch("SELECT * FROM guilds")
        self.data = { guild['id'] : dict(guild) for guild in guilds }

async def get_prefix(client , message):  
    try :
        prefix = client.data[message.guild.id]['prefix']
        if not prefix :
            raise Exception
    except Exception:
        prefix = "!"
    finally :
        return commands.when_mentioned_or(prefix)(client , message)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = MyBot( command_prefix =  get_prefix , strip_after_prefix =True, case_insensitive=True, intents=intents , help_command=None )

embed_color = 0x2b2d31

class Confirm(discord.ui.View):
    def __init__(self , user = None , role = None):
        super().__init__()
        self.value = None
        self.user = user
        self.role = role

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user and self.user != interaction.user :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        if self.role and self.role not in interaction.user.roles :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user and self.user != interaction.user :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        if self.role and self.role not in interaction.user.roles :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()

def bembed(message) :
    return discord.Embed( description= message , color= embed_color )

class SingleInput(discord.ui.Modal, title='...'):
    def __init__(self, question, placeholder):
        super().__init__()
        self.question = question
        self.placeholder = placeholder
        self.value = None
        self.input = discord.ui.TextInput(
            label=self.question, placeholder=self.placeholder)
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        self.value = self.input.value
        await interaction.response.defer()

def bembed(message=None) :
    return discord.Embed( description= message , color= 0x2b2d31 )
