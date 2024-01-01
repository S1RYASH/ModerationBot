import discord
from discord.ext import commands
import typing
from botmain import *
from discord import app_commands


class Suggestion(commands.Cog):

    def __init__(self , client):
        self.client = client
        
    # suggestion = app_commands.Group(name="suggestion"  , description= "suggestion commands")
    
    @app_commands.command()
    @app_commands.guild_only()
    async def suggestion_channel( self , interaction , channel : discord.TextChannel ):
        client.data[interaction.guild.id]['suggestion'] = channel.id
        await client.db.execute("UPDATE guilds SET suggestion = $1 WHERE id = $2" , channel.id , interaction.guild.id)
        await interaction.response.send_message( embed = bembed(f"Done , {channel.mention} is set as suggestion channel.") )
    
    @app_commands.command()
    @app_commands.guild_only()
    async def suggest(self , interaction , suggestion : str , attachment : typing.Optional[discord.Attachment] = None):
        # Number = await self.client.db.fetchval("SELECT COUNT(*) FROM suggestion WHERE guild = $1" , interaction.guild.id)
        embed = bembed()
        embed.title = f"Suggestion."
        embed.description= suggestion
        embed.set_author(name = interaction.user , icon_url= interaction.user.display_avatar)
        embed.set_footer( text= "type /suggest to add suggestion here." )
        channel_id = client.data[interaction.guild.id]['suggestion']
        if channel_id is None : return 
        else : channel = interaction.guild.get_channel(channel_id)
        try:
            embed.set_image(url= attachment.url )
        except :
            pass    
        await interaction.response.send_message("Done!" , ephemeral = True)
        msg = await channel.send(embed = embed)
        # temp = await interaction.original_response()
        # msg = await temp.fetch()
        await msg.add_reaction("⬆️")
        await msg.add_reaction("⬇️")
        # await self.client.db.execute('INSERT INTO suggestion(no,guild , id ,message,channel) VALUES ($1 , $2 , $3 , $4 , $5 )' , (Number+1) , interaction.guild.id , interaction.user.id  , msg.id , interaction.channel.id )
    
    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def reply(self , interaction , message_id : str , action : typing.Literal['Implemented','Considered','Approved','Denied'] , reply : str):
        
        channel = interaction.guild.get_channel(client.data[interaction.guild.id]['suggestion'])
        message = await channel.fetch_message(int(message_id))
        embed = message.embeds[0]
        embed.title = embed.title + f" {action}"
        try :
            embed.set_field_at( 0 , name= f"Reason from {interaction.user}" , value = reply)
        except :
            embed.add_field( name= f"Reason from {interaction.user}" , value = reply)
        await message.edit(embed = embed)
        await interaction.response.send_message( f"[click here]({message.jump_url}) to seen orignal message"  ,  embed = embed , ephemeral = True)  
        
    @reply.error
    async def hello(self, interaction , error):
        try : 
            await interaction.response.send_message(error,ephemeral = True)
        except :
            await interaction.followup.send(error,ephemeral = True) 
    @suggest.error
    async def hello(self, interaction , error):
        try : 
            await interaction.response.send_message(error,ephemeral = True)
        except :
            await interaction.followup.send(error,ephemeral = True) 

async def setup(client):
   await client.add_cog(Suggestion(client))         
