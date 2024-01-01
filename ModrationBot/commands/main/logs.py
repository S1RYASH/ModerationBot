import discord
from discord.ext import commands
import typing
from botmain import client
from datetime import datetime

class Logs(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.log_data = {457888455700119552 : {"timeout_log" : 1097146701493567611} , 966022734398246963 :  {"timeout_log" :966022736919035926} }

    # @commands.Cog.listener()
    # async def on_member_update(self, before, after):
    #     if before.timed_out_until != after.timed_out_until :
    #         if after.guild.id in self.log_data and self.log_data[after.guild.id].get('timeout_log' , None) != None :
    #             guild = self.client.get_guild(after.guild.id)
    #             channel = guild.get_channel(self.log_data[guild.id]['timeout_log'])
    #             embed = discord.Embed(timestamp= datetime.now() )
    #             embed.set_author( name= after , icon_url= after.avatar )
    #             if before.timed_out_until == None :
    #                 embed.description = f"  "

    @commands.Cog.listener()
    async def on_audit_log_entry_create(self , entry):
        if entry.guild.id in self.log_data and self.log_data[entry.guild.id].get('timeout_log' , None) != None and ( entry.changes.after.timed_out_until or entry.changes.before.timed_out_until)  :
            channel = entry.guild.get_channel(self.log_data[ entry.guild.id]['timeout_log'])
            embed = discord.Embed(timestamp= datetime.now() )
            embed.set_author( name= entry.target , icon_url= entry.target.avatar )
            if entry.changes.after.timed_out_until == None :
                embed.description = f"🛡️ : {entry.user}\n🎯 : {entry.target.mention}\n❓ : TimeOut Removed\n📃 : {entry.reason}"
            else :
                embed.description = f"🛡️ : {entry.user}\n🎯 : {entry.target.mention}\n⌚ : <t:{int(entry.changes.after.timed_out_until.timestamp()) }:R> ({ int(datetime.now().timestamp()) - int(entry.changes.after.timed_out_until.timestamp())} seconds)\n📃 : {entry.reason}"
            await channel.send(embed = embed )
    
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True) 
    async def addlogs(self , ctx , type : typing.Literal['timeout']  , channel : discord.TextChannel  ):
        self.log_data[ctx.guild.id] = { }
        self.log_data[ctx.guild.id]['timeout_log'] = channel.id
        await ctx.send("Done" + str(self.log_data))
        
            
            


async def setup(client):
   await client.add_cog(Logs(client))         
