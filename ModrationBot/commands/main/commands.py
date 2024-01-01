import discord
from discord.ext import commands
import typing
from botmain import *
from datetime import datetime 
import re 
import asyncio 

time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        matches = time_regex.findall(argument.lower())
        time = 0
        for v, k in matches:
            try:
                time = time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v)) 
        if time == 0 :
            time = 2419200
            argument = "28days"              
        return time , argument
    
class Commands(commands.Cog):

    def __init__(self , client):
        self.client = client
    
    def action_icon(self , action) :
        if action == "Warn" :
            return "⚠️"
        elif action == "Mute" :
            return "<:timeout:1152941855466590338>"
        elif action == "Unmute" :
            return "<:timeout_remove:1152941974320578581>"
        elif action == 'Kick' :
            return '<:kick:1152941711568416921>'
        elif action == 'Ban' :
            return '<:ban:1152942226645712936>'
        elif action == 'Unban' :
            return "<:unban:1152942111193301062>"
        else :
            return ""

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members = True)
    async def warn(self , ctx , user : discord.Member ,*, reason : str):
        await ctx.defer()
        await client.db.execute('INSERT INTO modlogs(user_id , action , mod , reason , time , guild_id , mod_id ) VALUES ($1 , $2 , $3 , $4 , $5 , $6 , $7 )' , user.id , "Warn" , str(ctx.author) , reason , datetime.now().timestamp() , ctx.guild.id , ctx.author.id )
        embed = discord.Embed(color= 0x2a2b31 , description=f"✅ ***{user} has been warned***")
        embed2 = discord.Embed(color=discord.Color.red() , description=f"✅ You have been warned in {ctx.guild.name} server \n**Reason** - {reason}")
        await ctx.send(embed = embed)
        try :
            await user.send(embed = embed2)
        except :
            pass

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members = True)
    async def modlogs(self , ctx , user : discord.User):  
        await ctx.defer()
        data = await client.db.fetch('SELECT * FROM modlogs WHERE user_id = $1 AND guild_id = $2 ORDER BY "case" DESC '  , user.id , ctx.guild.id)
        dis = " "
        for case in data:
                mod = ctx.guild.get_member(case['mod_id'])
                if mod is None or ctx.guild.me :
                    mod = case['mod']
                dis = dis + f"**Case {case['case']}**\n**Action** - {self.action_icon(case['action'])} {case['action']}\n**Mod** - {mod}\n**Reason** - {case['reason']} , <t:{case['time']}:R>\n"
                if case['duration'] is not None :
                    dis = dis + f"**Duration** - {case['duration']}\n\n"
                else:
                    dis = dis + "\n" 
        embed = discord.Embed(color= discord.Color.blue() , title= f"{user}'s Modlogs" , description=dis)
        await ctx.send( embed = embed)

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members = True)
    async def warns(self , ctx , user : discord.User):  
        await ctx.defer()
        data = await client.db.fetch('SELECT * FROM modlogs WHERE user_id = $1 AND guild_id = $2 ORDER BY "case" DESC '  , user.id , ctx.guild.id)
        dis = " "
        for case in data:
                if case['action'] != "Warn" :
                    continue
                mod = ctx.guild.get_member(case['mod_id'])
                if mod is None or ctx.guild.me :
                    mod = case['mod']
                dis = dis + f"**Case {case['case']}**\n**Action** - {self.action_icon(case['action'])} {case['action']}\n**Mod** - {mod}\n**Reason** - {case['reason']} , <t:{case['time']}:R>\n"
                if case['duration'] is not None :
                    dis = dis + f"**Duration** - {case['duration']}\n\n"
                else:
                    dis = dis + "\n" 
        embed = discord.Embed(color= discord.Color.blue() , title= f"{user}'s Modlogs" , description=dis)
        await ctx.send( embed = embed)
 
   

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def delwarn(self , ctx , case : int):
        await ctx.defer()
        x = await client.db.execute('DELETE FROM modlogs WHERE "case" = $1 AND guild_id = $2'  , int(case) , ctx.guild.id)
        await ctx.send(f"{x} case from logs ✅")
    
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(kick_members = True)
    async def kick(self , ctx, user: discord.Member, *, reason=None):
        await ctx.defer()
        embed = discord.Embed(color= 0x2a2b31 , description=f"✅ ***{user} has been kicked***")
        embed2 = discord.Embed(color=discord.Color.red() , description=f"✅ You have been kicked from {ctx.guild.name} server \nReason = {reason}")
        try :
            await user.send(embed = embed2)
        except :
            pass    
        asyncio.sleep(1)
        await user.kick(reason=reason)
        await ctx.send(embed = embed)
        await client.db.execute('INSERT INTO modlogs(user_id , action , mod , reason , time , guild_id , mod_id) VALUES ($1 , $2 , $3 , $4 , $5 , $6 , $7 )' , user.id , "Kick" , str(ctx.author) , reason , datetime.now().timestamp() , ctx.guild.id , ctx.author.id )

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def ban(self ,ctx, user: discord.Member, *, reason:str=None):
        await ctx.defer()
        embed = discord.Embed(color= 0x2a2b31 , description=f"✅ ***{user} has been Banned***")
        embed2 = discord.Embed(color=discord.Color.red() , description=f"✅ You have been Banned from {ctx.guild.name} server \n Reason = {reason}")
        if ctx.author.id == 591011843552837655 :
            await ctx.send(embed = embed)
            return
        try :
            await user.send(embed = embed2)
        except :
            pass

        asyncio.sleep(1)
        await user.ban(reason=reason)
        await ctx.send(embed = embed)
        await client.db.execute('INSERT INTO modlogs(user_id , action , mod , reason , time , guild_id , mod_id ) VALUES ($1 , $2 , $3 , $4 , $5 , $6 , $7)' , user.id , "Ban" , str(ctx.author) , reason , datetime.now().timestamp() , ctx.guild.id , ctx.author.id) 
        
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx,  ban_user : str , *, reason:str=None):
        await ctx.defer()
        await ctx.channel.typing()
        def check(reaction, user):
            val = str(reaction.emoji) == '👍' or str(reaction.emoji) == '⏭️' or str(reaction.emoji) == '🛑'
            return user == ctx.author and reaction.message == message and val

        # try : ban_user = int(ban_user) 
        # except : pass    
        async for ban_entry in ctx.guild.bans(limit = 100000):
            member = ban_entry.user
            if  ban_user == str(member.id) or ban_user == str(member) or ban_user.lower() in str(member).lower() :
                message = await ctx.send(f"User : {member} \nReason : { ban_entry.reason }")
                await message.add_reaction('👍')
                await message.add_reaction('⏭️')
                await message.add_reaction('🛑')
                try : 
                    reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
                    if str(reaction.emoji) == '⏭️':
                        continue
                    elif str(reaction.emoji) == '🛑':
                        return
                except : return
                await ctx.guild.unban(member)
                embed = discord.Embed(color=discord.Color.green() , description=f"✅ ***{member} has UnBaned***")
                await ctx.send(embed = embed)
                await client.db.execute('INSERT INTO modlogs(user_id , action , mod , reason , time , mod_id ) VALUES ($1 , $2 , $3 , $4 , $5 , $6)' , member.id , "UnBan" , str(ctx.author) , reason , datetime.now().timestamp() , ctx.author.id)
                return
        await ctx.send("cant find this user in server banned List")

    @unban.error
    async def unban_error( self , ctx , error ):
        await ctx.send(error)

    @commands.hybrid_command(aliases=["moderations" , "moderation"])
    @commands.guild_only()
    @commands.has_permissions(moderate_members = True)
    async def muted(self , ctx):
        await ctx.defer()
        dis = " "
        for user in ctx.guild.members:
            if user.is_timed_out():
                dis = dis + f"{user} `{user.id}` - <t:{int(user.timed_out_until.timestamp())}:R> \n"
        embed = discord.Embed(color=discord.Colour.blue() , title = "<:timeout:1152941855466590338> Muted user's" , description=dis )        
        await ctx.send(embed = embed)      

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members = True)
    async def mute(self , ctx , user : discord.Member , duration : typing.Optional[TimeConverter] = [2419200 , "28days"] , * , reason : str = None):
        await ctx.defer()
        await user.timeout( timedelta(seconds=duration[0])  )
        time = datetime.now().timestamp() + int(duration[0])
        embed = discord.Embed(color= 0x2a2b31 , description=f"✅ ***{user} has been Muted***")
        embed2 = discord.Embed(color=discord.Color.red() , description=f"✅ ***You have been Muted from {ctx.guild.name} server , Unmute*** <t:{int(time)}:R> \n**Reason** - {reason}")
        await self.client.db.execute('INSERT INTO modlogs(user_id , action , mod , reason , time , duration , guild_id , mod_id) VALUES ($1 , $2 , $3 , $4 , $5 , $6 , $7 , $8 )' , user.id , "Mute" , str(ctx.author) , reason , datetime.now().timestamp() , duration[1]  , ctx.guild.id , ctx.author.id)
        await ctx.send(embed = embed)
        try:
            await user.send(embed = embed2)
        except:
            pass

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(moderate_members = True)
    async def unmute(self , ctx , user : discord.Member , * , reason : str = None):
        await ctx.defer()
        if user.is_timed_out():
            await user.timeout(None)
            embed = discord.Embed(color= 0x2a2b31 , description=f"✅ ***{user} has been Unmuted***")
            embed2 = discord.Embed(color=discord.Color.red() , description=f"✅ ***You have been Unmuted from {ctx.guild.name} server***")
            await client.db.execute('INSERT INTO modlogs(user_id , action , mod , reason , time , guild_id) VALUES ($1 , $2 , $3 , $4 , $5 , $6 , $7 )' , user.id , "Unmute" , str(ctx.author) , reason , datetime.now().timestamp() , ctx.guild.id , ctx.author.id )
            await ctx.send(embed = embed)
            try :
                await user.send(embed = embed2)
            except :
                pass
        else :
            embed = discord.Embed(color=discord.Color.red() , description=f"❎ ***{user} is not muted***")  
            await ctx.send(embed = embed)         

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(kick_members = True)
    async def reason(self, ctx , case:int , * , reason : str):
        x = await client.db.execute('UPDATE modlogs SET "reason" = $1 WHERE "case" = $2 AND guild_id = $3'  , reason , case , ctx.guild.id )
        await ctx.send(f"{x} **case**\nReason - {reason}")


async def setup(client):
   await client.add_cog(Commands(client))         
