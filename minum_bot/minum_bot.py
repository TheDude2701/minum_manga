import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
from minum_bot.minumanga import send_id_query, send_img_query, send_desc_query
from pathlib import Path


dotenv_path = Path(__file__).resolve().parent.parent / "config.env"
load_dotenv(dotenv_path=dotenv_path)
GUILD_ID = int(os.getenv("SERVER_ID"))
if not GUILD_ID:
    raise RuntimeError("GUILD_ID is not set")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Connection successful as {bot.user}!")
    print('------')
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
        
@bot.tree.command(name="ping", description="Replies with pong!", guild = discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
        latency = round(bot.latency * 1000)
        await interaction.response.send_message(f"Pong! {latency}ms")
    
@bot.tree.command(name="add", description="Add manga by providing the name, rating, and a short review", guild = discord.Object(id=GUILD_ID))
async def add(
     interaction: discord.Interaction, 
     manga_name: str, 
     compl_date: str, 
     rating : int, 
     review: str, 
     manga_url: str):
    manga = send_id_query(manga_title = manga_name)
    manga_id = int(manga[0])
    print(f"MANGA ID: {manga_id}\n")
    manga_title = manga[1]
    manga_chapters = manga[2]
    manga_status = manga[3]
    if not manga or not manga[0]:
        await interaction.response.send_message("No manga found by that title!")
        return
    cover_img_link = send_img_query(manga_id)
    print(cover_img_link)
    description = send_desc_query(manga_id)
    author_name = interaction.user.display_name
    author_avatar_url = interaction.user.display_avatar.url
    embed = discord.Embed(
            title= f"{manga_title}",
            url = f"{manga_url}",
            description= f"{description}",
            color=discord.Color.blue()
    )
    embed.set_author(name = author_name, icon_url = author_avatar_url)
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/2/2d/Pok%C3%A9mon_Psyduck_art.png")
    embed.set_image(url= cover_img_link)
    embed.add_field(name = f"**Chapters: **", value = f"{manga_chapters}" , inline= True)
    embed.add_field(name = f"**Status: **", value = f"{manga_status}" , inline= True)
    embed.add_field(name = "**Date finshed reading: **" , value = f"{compl_date}" , inline= True)
    embed.add_field(name = f"**Rating:**", value = f"{rating}⭐" , inline= False)
    embed.add_field(name = "**Review: **", value =f"||{review}||"  , inline= False)
    embed.set_footer(text = "https:github.com/TheDude2701")
    try:
        await interaction.response.send_message(embed=embed)
    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"Failed to send embed: Invalid URL or other error.\nDetails: {e}"
        )

    

