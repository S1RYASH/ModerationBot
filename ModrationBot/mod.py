import os
import asyncio
from discord.ext import commands
from botmain import *
from dotenv import load_dotenv
import google.generativeai as genai



load_dotenv()

@client.event
async def on_ready():
    print(f'bot logged in named : {client.user.name}')
    user = client.get_user(591011843552837655)
    await user.send(f"{client.user} is Online Now")

# @client.event
# async def on_message(message):
#     if message.channel.id == 1190823818298671164 :
#         genai.configure(api_key="AIzaSyAVfujh-LZTpI7rewy5YSAGi038le_T-d4")
#         model = genai.GenerativeModel('gemini-pro')
#         response = model.generate_content(f"{message.content}\n\nis the a bed word ? answer in  yes or no ")
#         if response.text == 'yes' or 'yes' in response.text :
#             await message.guild.get_channel(1190824661378940998).send(embed = discord.Embed(title = "Toxic Word" , description = f"{message.content}" , color = 0x2b2c31).set_footer(text = f"By {message.author}"))
#             await message.delete()
            
@client.command()
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def ping(ctx):
    ping = round(client.latency * 1000 , ndigits=2)
    await ctx.reply(f'pong! `{ping}ms`')

chats = { }

@client.command()
@commands.guild_only()
# @commands.has_permissions(administrator=True)
async def ask(ctx , * , msg):
    await ctx.channel.typing()
    genai.configure(api_key="AIzaSyAVfujh-LZTpI7rewy5YSAGi038le_T-d4")
    model = genai.GenerativeModel('gemini-pro')
    if ctx.channel.id not in chats:
        chats[ctx.channel.id] = model.start_chat(history=[])
        
    response = chats[ctx.channel.id].send_message(msg)
    await ctx.reply(str(response.text))
    
@ask.error
async def ask_error(ctx , error):
    if isinstance(error , commands.MissingRequiredArgument):
        await ctx.reply('Please provide a message to ask')
    elif isinstance(error , commands.MissingPermissions):
        await ctx.reply('You do not have the permission to use this command')
    else:
        await ctx.reply(error)

@client.command()
@commands.guild_only()
# @commands.has_permissions(administrator=True)
async def clear(ctx ):
    chats.pop(ctx.channel.id)
    await ctx.reply('Chat Cleared')

from pretty_help import PrettyHelp , AppMenu 
client.help_command = PrettyHelp( color= 0x2b2c31 , menu= AppMenu() , no_category= "Basic" , dm_help=True ,  )

async def load():

    await client.load_extension(f'commands.main.owner')
    await client.load_extension(f'commands.main.guild')

    await client.load_extension(f'commands.main.commands')
    await client.load_extension(f'commands.main.logs')
    # await client.load_extension(f'commands.main.mail')
    await client.load_extension(f'commands.main.modcommands')
    await client.load_extension(f'commands.main.suggestion')

asyncio.run(load())
client.run(os.environ.get("TOKEN"))