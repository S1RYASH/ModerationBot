import discord
from discord.ext import commands
from botmain import *
from datetime import datetime 
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
from discord.ui import View , Button , Select
import chat_exporter
import io

class ControlView(View):

    def __init__(self):
        super().__init__( timeout=None )

    @discord.ui.button( label= "Transcript" , style= discord.ButtonStyle.secondary , emoji= "📃", row=None)
    async def transcript_ticket(self , interaction , button):
        await interaction.response.defer(ephemeral=True ,thinking=True)
        transcript = await chat_exporter.export(channel=  interaction.channel, limit = 100 , tz_info="Asia/Kolkata")
        transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                          filename=f"{interaction.channel.name}.html")
        await interaction.followup.send(file=transcript_file)

    @discord.ui.button( label= "Delete" , style= discord.ButtonStyle.secondary , emoji= "🚮", row=None)
    async def delete_ticket(self , interaction , button): 
        channel = interaction.channel
        await channel.delete()
        await interaction.response.defer()
        return     
      

class Mail(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.mails = { }
        self.claims = { }



    # @commands.hybrid_command(aliases= ["mailsetup"])
    # @commands.guild_only()
    # @commands.has_permissions(manage_guild = True)
    # async def backupchat(self, ctx , channel : discord.TextChannel = None):
    #     channel = channel or ctx.channel
    #     transcript = await chat_exporter.export(channel=  ctx.channel, limit = 100 , tz_info="Asia/Kolkata")
    #     transcript_file = discord.File(io.BytesIO(transcript.encode()),
    #                                       filename=f"{ctx.channel.name}.html")
    #     await ctx.send(file=transcript_file)


 

    @commands.hybrid_command(aliases= ["mailsetup"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def setupmail(self, ctx , logs : discord.TextChannel = None):
        
        if logs : 
            client.data[ctx.guild.id]["logs"] = logs.id
            await client.db.execute('UPDATE guilds SET logs = $1 WHERE id = $2', logs.id , ctx.guild.id)

        def setupmailEmbed():
            embed = discord.Embed(title="Mail SetUp")
            embed.description = f"{'`🟢`' if client.data[ctx.guild.id]['mail'] else '`🔴`' } : Mail Status\n\nMessage : {client.data[ctx.guild.id]['message']}"

            value = ''
            if client.data[ctx.guild.id]["s_roles"] and len(client.data[ctx.guild.id]["s_roles"]) > 0:
                for role in list(client.data[ctx.guild.id]["s_roles"]):
                    if ctx.guild.get_role(role):
                        value += f"{ctx.guild.get_role(role).mention}\n"
                    else:
                        client.data[ctx.guild.id]["s_roles"].remove(role)
            else :
                client.data[ctx.guild.id]["s_roles"] = None
                value = "No Support Role"
            embed.add_field(name='Support Team', value=value, inline=False)
            
            value = ''
            if client.data[ctx.guild.id]["a_roles"] and len(client.data[ctx.guild.id]["a_roles"]) > 0:
                for role in list(client.data[ctx.guild.id]["a_roles"]):
                    if ctx.guild.get_role(role):
                        value += f"{ctx.guild.get_role(role).mention}\n"
                    else:
                        client.data[ctx.guild.id]["a_roles"].remove(role)
            else:
                client.data[ctx.guild.id]["a_roles"] = None
                value = "No Additional Role"
            embed.add_field(name='Additional Team', value=value, inline=False)

            value = ''
            if client.data[ctx.guild.id]["o_category"] and ctx.guild.get_channel(client.data[ctx.guild.id]["o_category"]):
                value = ctx.guild.get_channel(
                    client.data[ctx.guild.id]["o_category"]).mention
            else:
                client.data[ctx.guild.id]["o_category"] = None
                value = "No Category"

            embed.add_field(name='Open Category',
                            value=value, inline=False)
            
            value = ''
            if client.data[ctx.guild.id]["c_category"] and ctx.guild.get_channel(client.data[ctx.guild.id]["c_category"]):
                value = ctx.guild.get_channel(
                    client.data[ctx.guild.id]["c_category"]).mention
            else:
                client.data[ctx.guild.id]["c_category"] = None
                value = "No Category"

            embed.add_field(name='Open Category',
                            value=value, inline=False)
            
            value = ''
            if client.data[ctx.guild.id]["logs"] and ctx.guild.get_channel(client.data[ctx.guild.id]["logs"]):
                value = ctx.guild.get_channel(
                    client.data[ctx.guild.id]["logs"]).mention
            else:
                client.data[ctx.guild.id]["logs"] = None
                value = "No Log Channel"

            embed.add_field(name='Log Channel',
                            value=value, inline=False)
            
            return embed
        
        view = discord.ui.View()
        
        async def update_s_roles(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            data = s_roles.values
           
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET s_roles = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["s_roles"] = None
            else :
                await client.db.execute('UPDATE guilds SET s_roles = $1 WHERE id = $2', [item.id for item in data], ctx.guild.id)
                client.data[ctx.guild.id]["s_roles"] = [
                    item.id for item in data]
             
            await interaction.response.edit_message(embed=setupmailEmbed())

        s_roles = discord.ui.RoleSelect(placeholder=" Support Role", min_values=0, max_values=10)
        s_roles.callback = update_s_roles
        view.add_item(s_roles)
        
        async def update_a_roles(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction")
                return
            data = a_roles.values
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET a_roles = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["a_roles"] = None
            else:
                await client.db.execute('UPDATE guilds SET a_roles = $1 WHERE id = $2', [item.id for item in data], ctx.guild.id)
                client.data[ctx.guild.id]["a_roles"] = [
                    item.id for item in data]
            await interaction.response.edit_message(embed=setupmailEmbed())

        a_roles = discord.ui.RoleSelect( placeholder=" Additional Role (View Perms)", min_values=0, max_values=10)
        a_roles.callback = update_a_roles
        view.add_item(a_roles)

        async def update_o_category(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            data = o_category.values
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET o_category = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["o_category"] = None
            else:
                await client.db.execute('UPDATE guilds SET o_category = $1 WHERE id = $2', data[0].id, ctx.guild.id)
                client.data[ctx.guild.id]["o_category"] = data[0].id
            await interaction.response.edit_message(embed=setupmailEmbed())

        o_category = discord.ui.ChannelSelect(channel_types=[
            discord.ChannelType.category], placeholder="Mail Open Category", min_values=0, max_values=1)
        o_category.callback = update_o_category
        view.add_item(o_category)
        
        async def update_c_category(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            data = c_category.values
            if len(data) == 0:
                await client.db.execute('UPDATE guilds SET c_category = $1 WHERE id = $2', None, ctx.guild.id)
                client.data[ctx.guild.id]["c_category"] = None
            else:
                await client.db.execute('UPDATE guilds SET c_category = $1 WHERE id = $2', data[0].id, ctx.guild.id)
                client.data[ctx.guild.id]["c_category"] = data[0].id
            await interaction.response.edit_message(embed=setupmailEmbed())

        c_category = discord.ui.ChannelSelect(channel_types=[
            discord.ChannelType.category], placeholder="Mail Close Category", min_values=0, max_values=1)
        c_category.callback = update_c_category
        view.add_item(c_category)

        mail = Button(style=discord.ButtonStyle.danger if client.data[ctx.guild.id]['mail']
                     else discord.ButtonStyle.green, label=f"{'Mail : OFF' if client.data[ctx.guild.id]['mail'] else 'Mail : ON'}")

        async def update_mail(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            if client.data[ctx.guild.id]['mail']:
                await client.db.execute('UPDATE guilds SET mail = $1 WHERE id = $2', False, ctx.guild.id)
                client.data[ctx.guild.id]['mail'] = False
                mail.style = discord.ButtonStyle.green
                mail.label = '   Mail : ON'
            else:
                await client.db.execute('UPDATE guilds SET mail = $1 WHERE id = $2', True, ctx.guild.id)
                client.data[ctx.guild.id]['mail'] = True
                mail.style = discord.ButtonStyle.danger
                mail.label = 'Mail : OFF'

            await interaction.response.edit_message(embed=setupmailEmbed(), view=view)

        mail.callback = update_mail
        view.add_item(mail)

        message = Button(style=discord.ButtonStyle.grey, label="Message")

        async def update_message(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            modal = SingleInput("Write A message",
                                "Message Will send on a Mail Open")
            await interaction.response.send_modal(modal)
            await modal.wait()
            if modal.value:
                try:
                    value = modal.value
                    client.data[ctx.guild.id]['message'] = value
                    await client.db.execute('UPDATE guilds SET message = $1 WHERE id = $2', value, ctx.guild.id)
                    await interaction.message.edit(embed=setupmailEmbed())
                except Exception as e:
                    await interaction.followup.send(f"Invalid Input {e}", ephemeral=True)
            else:
                await interaction.followup.send("No input", ephemeral=True)
        message.callback = update_message
        view.add_item(message)

        done = Button(style=discord.ButtonStyle.blurple, label="Done")

        async def update_done(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Not Your Interaction" , ephemeral = True)
                return
            await interaction.response.edit_message(view=None)
        done.callback = update_done
        view.add_item(done)
        await ctx.send(embed=setupmailEmbed(), view=view)

    async def openMail(self , user , guild):
        if user.id in [ self.mails[i] for i in self.mails ] :
            return
        overwrites = { guild.default_role : discord.PermissionOverwrite( view_channel = False , send_messages = False ) ,
                      guild.me : discord.PermissionOverwrite( view_channel = True , send_messages = True) }
        if client.data[guild.id].get("s_roles") :
            for role_id in client.data[guild.id].get("s_roles" , []) :
                if guild.get_role(role_id) :
                    overwrites[guild.get_role(role_id)]  = discord.PermissionOverwrite( view_channel = True , send_messages = True , attach_files = True )
        if client.data[guild.id].get("a_roles") :
            for role_id in client.data[guild.id].get("a_roles" , []) :
                if guild.get_role(role_id) :
                    overwrites[guild.get_role(role_id)]  = discord.PermissionOverwrite( view_channel = True )
        channel = await guild.create_text_channel( name = f"{random.randint(0,99)}-{user.name}" , overwrites = overwrites , category= guild.get_channel( client.data[guild.id]['o_category'] )  , topic = "Support Team")
        self.mails[channel.id] = user.id
        
        user = guild.get_member(user.id)
        embed = discord.Embed(color= embed_color , description = user.mention, timestamp = datetime.now())
        embed.set_author(name = user, icon_url = user.display_avatar)
        embed.add_field(name = "Joined", value = f"- <t:{int(user.joined_at.timestamp())}:F>\n- <t:{int(user.joined_at.timestamp())}:R>")
        embed.add_field(name = "Registered", value = f"- <t:{int(user.created_at.timestamp())}:F>\n- <t:{int(user.created_at.timestamp())}:R>")
        roles = " "
        for x in reversed(user.roles):
            roles = roles + f"{x.mention} "
        embed.add_field(name = f"Roles[{len(user.roles)}]", value = roles, inline = False)
        perms = " "
        for x in user.guild_permissions.elevated():
            if x[1] is True:
                perms = perms + f"{x[0].capitalize()} ,"
        # embed.add_field(name = "Key Permission", value = (perms.rstrip(",")).replace("_"," "), inline = False)
        embed.set_footer(text = f"{user.id} chaisuta op")
        embed.set_thumbnail(url = user.display_avatar)
        
        view = View()
        
        async def update_claim(interaction) :
            if interaction.channel.id in self.claims :
                self.claims[interaction.channel.id].append(interaction.user.id)
            else :
                self.claims[interaction.channel.id]=[interaction.user.id]
            claim.disabled = True
            await interaction.response.edit_message(view = view)
            await interaction.channel.send(embed = discord.Embed( description= f"This modmail has been claimed by {interaction.user.mention}" , color= discord.Color.green() ))
            try :
                await interaction.channel.edit(topic = " ,".join([ str(interaction.guild.get_member(id)) for id in self.claims[interaction.channel.id] ]))
            except :
                pass
        
        claim = Button( style=discord.ButtonStyle.blurple , label= "Claim" )
        claim.callback = update_claim
        view.add_item(claim)
        
        await channel.send( client.data[guild.id]['message'] , embed=embed , view = view)
        await user.send( embed= bembed("**We've opened a Mail, and the support team will get back to you as soon as they can.** \n\n!close - close the Mail"))    
    
    @setupmail.error
    async def setupmail_error(self , ctx , error) :
        await ctx.send(error)

    @commands.Cog.listener()
    async def on_message(self , message):
        if message.author.bot :
            return
        
        if message.guild is None and message.author.id in [ self.mails[i] for i in self.mails ] :
            # send the message in the Mail 
            if message.content.startswith("!") :
                return
            channel_id = next(key for key, value in self.mails.items() if value == message.author.id)
            channel = client.get_channel(channel_id)
            if channel is None :
                self.mails.pop(channel_id)
                return
            hook = None
            webhooks = await channel.webhooks() 
            for webhook in webhooks :
                if webhook.name == client.user.name :
                    hook = webhook
                    break
            
            files = [] 
            if message.attachments and len(message.attachments) > 0 :
                for attachment in message.attachments :
                    try :
                        files.append( await attachment.to_file() )
                    except :
                        files = [ await attachment.to_file() ]
            try :
                if hook is None :
                        hook = await channel.create_webhook(name = client.user.name)
                if message.stickers :
                    raise Exception
                await hook.send(content = message.content , files = files , username = message.author.name , avatar_url = message.author.display_avatar.url if message.author.display_avatar else None , allowed_mentions= discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False))
            except Exception as e :
                await channel.send(message.content , files = files, stickers= message.stickers , allowed_mentions= discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=False) )
                
        elif message.guild is None :
            if message.content.startswith("!") :
                return
            mail_guilds = [ guild.id for guild in message.author.mutual_guilds if client.data[guild.id]['mail']]
            if len(mail_guilds) == 0 :
                pass
            elif len(mail_guilds) == 1 :
                view = Confirm()
                await message.author.send( embed = discord.Embed( description=f"Do You Want To Open A Mail In **{(client.get_guild(mail_guilds[0])).name}**" , color= embed_color ) , view = view)
                await view.wait()
                if view.value :
                    await self.openMail( message.author , client.get_guild(mail_guilds[0]) )
            else :
                view1 = View()
                view1.value = None
                embed = discord.Embed(title = "Select Server" , color= embed_color)
                embed.description = ""
                options = [ ]
                for i , guild_id in enumerate(mail_guilds , 1) :
                    guild = client.get_guild(guild_id)
                    embed.description += f"{i}. **{guild.name}**\n\n"
                    options.append( discord.SelectOption( label=guild.name , value = i ))
                async def select_callback(interaction) :
                    view1.value = int(select.values[0])
                    await interaction.response.defer() 
                    view1.stop()
                select = Select(placeholder="Choose a server", min_values=1, max_values=1, options=options)
                select.callback = select_callback
                view1.add_item(select)
                
                await message.author.send( embed = embed , view = view1)
                await view1.wait()
                
                if not view1.value : 
                    return
                
                view = Confirm()
                await message.author.send( embed = discord.Embed( description=f"Do You Want To Open A Mail In **{(client.get_guild(mail_guilds[view1.value-1])).name}**" , color= embed_color ) , view = view)
                await view.wait()
                if view.value :
                    await self.openMail( message.author , client.get_guild(mail_guilds[view1.value-1]) )
        
        elif message.guild and client.data[message.guild.id]['mail'] and message.channel.id in self.mails :
            if message.content.startswith("!") :
                # await message.add_reaction("❌")
                return
            
            files = [] 
            if message.attachments and len(message.attachments) > 0 :
                for attachment in message.attachments :
                    try :
                        files.append( await attachment.to_file() )
                    except :
                        files = [ await attachment.to_file() ]

            if message.channel.id in self.claims :
                if message.author.id in self.claims[message.channel.id] :
                    await message.guild.get_member(self.mails[message.channel.id]).send(message.content , files = files , stickers = message.stickers)
            else :
                await message.guild.get_member(self.mails[message.channel.id]).send(message.content , files = files , stickers = message.stickers)
        
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild = True)
    async def claim(self, ctx ): 
        if ctx.channel.id not in self.mails :
               return
        if ctx.channel.id in self.claims :
            if ctx.author.id in self.claims[ctx.channel.id] :
                self.claims[ctx.channel.id].remove(ctx.author.id)
                await ctx.send(embed = discord.Embed( color = discord.Color.red() ,  description= f"Modmail claim Removed From {ctx.author.mention}"))
            else :
                self.claims[ctx.channel.id].append(ctx.author.id)
                await ctx.send(embed = discord.Embed( color = discord.Color.green() ,  description= f"Modmail has been claimed by {ctx.author.mention}"))
        else :
            self.claims[ctx.channel.id]=[ctx.author.id]
            await ctx.send(embed = discord.Embed( color = discord.Color.green() ,  description= f"Modmail has been claimed by {ctx.author.mention}"))
        try :
            await ctx.channel.edit(topic = " ,".join([ str(ctx.guild.get_member(id)) for id in self.claims[ctx.channel.id] ]))
        except :
            pass
            
    @claim.error
    async def setupmail_error(self , ctx , error) :
        await ctx.send(error)
    
    @commands.hybrid_command()
    async def close(self, ctx ): 
        
        if ctx.guild and ctx.channel.id in self.mails :
            value = self.mails[ctx.channel.id] 
            del self.mails[ctx.channel.id] 
            
            if client.data[ctx.guild.id]["logs"] and ctx.guild.get_channel(client.data[ctx.guild.id]["logs"]) :
                transcript = await chat_exporter.export(channel=  ctx.channel, limit = 100 , tz_info="Asia/Kolkata")
                transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                            filename=f"{ctx.channel.name}.html")
                await ctx.guild.get_channel(client.data[ctx.guild.id]["logs"]).send( value , file=transcript_file)
                
            if client.data[ctx.guild.id]["c_category"] and ctx.guild.get_channel(client.data[ctx.guild.id]["c_category"]) :
                await ctx.channel.edit( category  = ctx.guild.get_channel(client.data[ctx.guild.id]["c_category"]) )
                await ctx.channel.send( embed = bembed(f"This Mail Has Been Closed by {ctx.author.mention}")  , view= ControlView()  )
            else :
                await ctx.channel.delete()
            await client.get_user(value).send(embed = bembed("Your Mail Has Been Closed"))
            
        elif ctx.guild is None and ctx.author.id in [ self.mails[i] for i in self.mails ] :
            channel_id = next(key for key, value in self.mails.items() if value == ctx.author.id)
            del self.mails[channel_id]
            channel = client.get_channel(channel_id)
            if channel is None : 
                return

            if client.data[channel.guild.id]["logs"] and channel.guild.get_channel(client.data[channel.guild.id]["logs"]) :
                transcript = await chat_exporter.export(channel=  channel, limit = 100 , tz_info="Asia/Kolkata")
                transcript_file = discord.File(io.BytesIO(transcript.encode()),
                                            filename=f"{channel.name}.html")
                await channel.guild.get_channel(client.data[channel.guild.id]["logs"]).send( ctx.author.id , file=transcript_file)
                
            if client.data[channel.guild.id]["c_category"] and channel.guild.get_channel(client.data[channel.guild.id]["c_category"]) :
                await channel.edit( category  = channel.guild.get_channel(client.data[channel.guild.id]["c_category"]) )
                await channel.send( embed = bembed(f"This Mail Has Been Closed by {ctx.author.mention}") , view= ControlView() )
            else :
                await channel.send( embed = bembed(f"This Mail Has Been Closed by {ctx.author.mention}") , view= ControlView() )

            await ctx.send(embed = bembed("Your Mail Has Been Closed"))
    
    
        # if message.content.lower() not in self.tri:
        #     return
        # data = await client.db.fetchrow('SELECT * FROM triggers WHERE trigger = $1 AND guild_id = $2' , message.content.lower() , message.guild.id )
        # if data is None :
        #     return
        # for role in message.author.roles:
        #     if role.id in data["i_role"]:
        #         return
        #     if len(data['r_role']) == 0 or role.id in data['r_role'] :
        #         if data['avatar_url'] is not None:
        #             hook = None
        #             webhooks = await message.channel.webhooks() 
        #             for webhook in webhooks :
        #                 if webhook.name == client.user.name :
        #                     hook = webhook
        #                     break
        #             if hook is None :
        #                 hook = await message.channel.create_webhook(name = client.user.name)
        #             msg = await hook.send(content = data['message'] , username = data['username'] , avatar_url = data['avatar_url']) 
        #             return
        #         else :                
        #             msg = await message.channel.send(data['message']) 
        #             return 
        #         if data['delete_after'] is not None :
        #             await asyncio.sleep(data['delete_after']) 
        #             await message.delete()   

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.cooldown(1, 600 ,BucketType.user )
    # async def sayuser(self , ctx , user : discord.Member , * , message : str):
    #     await ctx.message.delete()
    #     hook = None
    #     webhooks = await ctx.channel.webhooks() 
    #     for webhook in webhooks :
        
    #         if webhook.name == client.user.name :
    #             hook = webhook
    #             break
    #     if hook is None :
    #             hook = await ctx.channel.create_webhook(name = client.user.name)
        
    #     def check(reaction, user):
    #         return str(reaction.emoji) == '👍'
        
    #     channel = ctx.guild.get_channel(976542645801328681)
    #     msg = await channel.send( f" user : {ctx.author} \nCommand : {ctx.message.content}")
    #     await msg.add_reaction("👍")
    #     await ctx.author.send(f'sended for mod approval\ncommand : {ctx.message.content}')
    #     reaction, user1 = await client.wait_for('reaction_add', timeout=600, check=check)   
    #     await hook.send(content = message , username = user.name , avatar_url = user.display_avatar.url )
        
    # @sayuser.error
    # async def cx(self , ctx , error)  :
        
    #     if isinstance(error, commands.CommandOnCooldown):
    #         await ctx.message.delete()
    #         await ctx.author.send("you are on cooldown")
    #         return
        
    #     await ctx.send(error)   
        
        
               
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.is_owner()
    # async def bol(self , ctx , user : discord.Member , * , message : str):
    #     await ctx.message.delete()
    #     hook = None
    #     webhooks = await ctx.channel.webhooks() 
    #     for webhook in webhooks :
    #         if webhook.name == client.user.name :
    #             hook = webhook
    #             break
    #     if hook is None :
    #             hook = await ctx.channel.create_webhook(name = client.user.name)
                
    #     await hook.send(content = message , username = user.name , avatar_url = user.display_avatar.url )
    
       

    # @bol.error
    # async def cx(self , ctx , error)  :
    #     await ctx.send(error)  
        
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.is_owner()
    # async def embed(self , ctx , username : typing.Optional[str] , pfp_url : typing.Optional[str] , * , message :  typing.Optional[str]):
    #     # await ctx.message.delete()
        
    #     if username is None :
    #         await ctx.send( message , embed = discord.Embed(description="Edit me") )
    #         return
        
    #     hook = None
    #     webhooks = await ctx.channel.webhooks() 
    #     for webhook in webhooks :
    #         if webhook.name == client.user.name :
    #             hook = webhook
    #             break
    #     if hook is None :
    #             hook = await ctx.channel.create_webhook(name = client.user.name)
                
    #     await hook.send(content = message , username = username , avatar_url = pfp_url , embed = discord.Embed(description="Edit me"))              
    
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.cooldown( 600 , 1 )
    # async def meme(self , ctx , message :str , meme : discord.Attachment , username : str , pfp : typing.Optional[str] = None ) :
         
    #     if ctx.guild.id != 966022734398246963 :
    #         return
        
    #     hook = None
        
    #     channel = ctx.guild.get_channel(966022735333572642)
        
    #     webhooks = await channel.webhooks() 
    #     for webhook in webhooks :
    #         if webhook.name == client.user.name :
    #             hook = webhook
    #             break
            
    #     if hook is None :
    #             hook = await channel.create_webhook(name = client.user.name)
        
    #     file = await meme.to_file()         
    #     await hook.send(content = message ,file = file  , username = username , avatar_url = pfp , allowed_mentions = discord.AllowedMentions(everyone=False, users=True, roles=False, replied_user=True) ) 
    #     await ctx.send("Done" , ephemeral=True )
    #     await self.client.application.owner.send(f"{ctx.author.id} {ctx.author}")
    
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.has_permissions(moderate_members = True)
    # async def triggeradd(self,ctx, trigger : str , r_role : discord.Role , avatar_url : typing.Optional[str] = None , username : typing.Optional[str] = None , delete_after : typing.Optional[int] = None, * , message : str):
    #     if username == None :
    #         username = client.user.name
    #     await client.db.execute('INSERT INTO triggers(trigger , message , r_role , i_role , guild_id , username , avatar_url , delete_after ) VALUES ($1 , $2 ,$3 ,$4 , $5 , $6 ,$7 , $8)' , trigger.lower() , message , [] , [] , ctx.guild.id , username , avatar_url , delete_after)
    #     await client.db.execute('UPDATE triggers SET r_role = array_append(r_role , $1) WHERE trigger = $2' , r_role.id , trigger)
    #     await ctx.send("tigger added")
    #     data2 =await client.db.fetch('SELECT trigger FROM triggers')
    #     z = []
    #     for i in data2:
    #         z.append(i['trigger'])
    #     self.tri = z

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.has_permissions(moderate_members = True)
    # async def triggers(self,ctx):
    #     data = await client.db.fetch('SELECT * FROM triggers WHERE guild_id = $1' , ctx.guild.id)
    #     x = " "
    #     for y in data :
    #         x = x + f"{y['s_no']}. {y['trigger']} - {y['message']} \n"
    #     embed = discord.Embed( description= x )    
    #     await ctx.send(embed = embed)  

    # # @commands.hybrid_command()
    # # @commands.guild_only()
    # # @commands.is_owner()
    # # async def triggerlist(self,ctx):
        
    # # #    filters = [{'Name': 'domain', 'Values': ['vpc']}]
    # # #    response = ec2.describe_addresses(Filters=filters)

    # #     # hostname = socket.gethostname()
    # #     # IP = socket.gethostbyname(hostname)
    # #     # await ctx.send(os.system('ipconfig'))
    # #     await ctx.send(self.tri)


    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.has_permissions(moderate_members = True)
    # async def triggerremove(self,ctx, trigger):
    #     await client.db.execute('DELETE FROM triggers WHERE trigger = $1 AND guild_id = $2'  , trigger , ctx.guild.id) 
    #     await ctx.send("tigger removed")
    #     data2 =await client.db.fetch('SELECT trigger FROM triggers')
    #     z = []
    #     for i in data2: 
    #         z.append(i['trigger'])
    #     self.tri = z
    

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.has_permissions(moderate_members = True) 
    # async def triggeredit(self,ctx, id : int , trigger : typing.Optional[str] = None , message : typing.Optional[str] = None , r_role : typing.Optional[discord.Role]  = None, i_role : typing.Optional[discord.Role] = None , cooldown : typing.Optional[int] = None ):
    #     data = await client.db.fetchrow('SELECT * FROM triggers  WHERE s_no = $1 AND guild_id = $2' , id , ctx.guild.id)
    #     if data is None : 
    #         await ctx.send("no data with this s_no")
    #         return 
    #     if trigger is not None :
    #         await client.db.execute('UPDATE triggers SET trigger = $1 WHERE s_no = $2' , trigger , id )
    #         self.tri.remove(datap['trigger'])
    #         self.tri.append(trigger)
    #     if message is not None :
    #         await client.db.execute('UPDATE triggers SET message = $1 WHERE s_no = $2' , message , id )
    #     if r_role is not None:
    #         if (data["r_role"] is not None) and (r_role.id in data["r_role"]):
    #             await client.db.execute('UPDATE triggers SET r_role = array_remove(r_role , $1) WHERE s_no = $2' , r_role.id , id)
    #         else :
    #             await client.db.execute('UPDATE triggers SET r_role = array_append(r_role , $1) WHERE s_no = $2' , r_role.id , id)
    #     if i_role is not None :
    #         if (data["r_role"] is not None)  and (i_role.id in data["i_role"]):
    #             await client.db.execute('UPDATE triggers SET i_role = array_remove(i_role , $1) WHERE s_no = $2' , i_role.id , id)
    #         else :
    #             await client.db.execute('UPDATE triggers SET i_role = array_append(i_role , $1) WHERE s_no = $2' , i_role.id , id)
    #     if cooldown is not None :
    #         await client.db.execute('UPDATE triggers SET cooldown = $1 WHERE s_no = $2' , cooldown ,id)

    #     data = await client.db.fetchrow('SELECT * FROM triggers  WHERE s_no = $1' , id)
    #     embed = discord.Embed()
    #     embed.add_field(name= "trigger" , value= data['trigger'])
    #     embed.add_field(name= "message" , value= data['message'])
    #     r_role_lis = f"{ctx.guild.default_role}"
    #     i_role_lis = f"."

    #     if data['r_role'] is not None and data['i_role'] is not None :

    #         for i in data['r_role']:
    #             x = ctx.guild.get_role(i)
    #             r_role_lis = r_role_lis + f" {x.mention}"
        
    #         for i in data['i_role']:
    #             x = ctx.guild.get_role(i)
    #             i_role_lis = i_role_lis + " " +  x.mention

    #     embed.add_field(name= "r_roles" , value= r_role_lis)
    #     embed.add_field(name= "i_roles" , value= i_role_lis)
    #     embed.add_field(name= "cooldown" , value= data['cooldown'])
    #     await ctx.send(embed = embed)
    #     data2 =await client.db.fetch('SELECT trigger FROM triggers')
    #     z = []
    #     for i in data2:
    #         z.append(i['trigger'])
    #     self.tri = z        
    #     await client.application.owner.send(z)    



async def setup(client):
   await client.add_cog(Mail(client))