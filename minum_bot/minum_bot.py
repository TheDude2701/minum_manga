import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
from minum_bot.minumanga import send_id_query, send_img_query, send_desc_query, random_code, send_status_query
from pathlib import Path
from typing import Optional
from datetime import date
from minum_bot.message_store import load_storage, save_storage


dotenv_path = Path(__file__).resolve().parent.parent / "config.env"
load_dotenv(dotenv_path=dotenv_path)
GUILD_ID = int(os.getenv("SERVER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
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
        
@bot.tree.command(name="update", description="Update your reading progress on the manga", guild = discord.Object(id=GUILD_ID))
async def update(interaction: discord.Interaction,
    manga_id: int,
    compl_date: Optional[str], 
    rating :Optional [float], 
    review: Optional[str], 
    status: Optional[str],
    chapter: Optional[float],
    manual: bool
):
    await interaction.response.defer(ephemeral=True)
    storage = load_storage()
    user = interaction.user
    key = f"{int(manga_id)}:{int(user.id)}"
    entry = storage.get(key)
    if not entry:
        await interaction.edit_original_response(content="None of your tracked mangas matched with that ID.")
        return
    if  not user.id == entry["sender"]:
        await interaction.edit_original_response(
            content="Nice try... You weren't the one that added that entry!"
        )
        return
    review_flag = entry["reviewed"]
    channel = bot.get_channel(entry["channel_id"])
    if not channel:
        await interaction.edit_original_response(
            content="Channel no longer exists."
        )
        return
    try:
        message = await channel.fetch_message(entry["message_id"])
    except discord.NotFound:
        await interaction.edit_original_response(
            content="Original message was deleted."
        )
        return
    if not manual:
        manga = send_status_query(manga_id)
        manga_status = manga[1]
        manga_chapters = manga[0]
    embed = message.embeds[0]
    if chapter:
        embed.set_field_at(index= 0 ,name = f"**Chapters: **", value = f"{chapter}" , inline= True)
        storage[key]["total"] = chapter
        save_storage(storage)
        progress = entry["progress"]
        embed.set_field_at(index = 4, name = f"**Progress: **", value = f"{progress}/{chapter}" )
    else:
        if not manual:
            embed.set_field_at(index= 0 ,name = f"**Chapters: **", value = f"{manga_chapters}" , inline= True)
            storage[key]["total"] = manga_chapters
            save_storage(storage) 
            progress = entry["progress"]
            embed.set_field_at(index = 4, name = f"**Progress: **", value = f"{progress}/{chapter}" )
    if status:
        embed.set_field_at(index= 1, name = f"**Status: **", value = f"{status}" , inline= True)
    else:
        if not manual:
            embed.set_field_at(index= 1, name = f"**Status: **", value = f"{manga_status}" , inline= True)
    if compl_date:
        embed.set_field_at(index= 2, name = "**Date finished reading: **" , value = f"{compl_date}" , inline= True)
    if rating:
        embed.set_field_at(index = 3, name = f"**Rating:**", value = f"{rating}⭐" , inline= False)
    
    if review:
        if review_flag == True:
            embed.set_field_at(index = 5, name = "**Review: **", value =f"||{review}||"  , inline= False)
        else:
            embed.add_field(name = "**Review: **", value =f"||{review}||"  , inline= False)
            storage[key]["reviewed"] = True
            save_storage(storage)
    await message.edit(embed=embed)
    await interaction.edit_original_response(
        content="Progress updated!"
    )
     
@bot.tree.command(name="updateprogress", description="Update your reading progress on the manga", guild = discord.Object(id=GUILD_ID))
async def updateprogress(
    interaction: discord.Interaction,
    manga_id: int,
    new_progress: float
):
    await interaction.response.defer(ephemeral=True)
    storage = load_storage()
    user = interaction.user
    key = f"{int(manga_id)}:{int(user.id)}"
    entry = storage.get(key)
    if not entry:
        await interaction.edit_original_response(
            content="None of your tracked mangas matched with that ID."
        )
        return
    if not user.id == entry["sender"]:
        await interaction.edit_original_response(
            content="Nice try... You weren't the one that added that entry!"
        )
        return
    channel = bot.get_channel(entry["channel_id"])
    if not channel:
        await interaction.edit_original_response(
            content="Channel no longer exists."
        )
        return
    try:
        message = await channel.fetch_message(entry["message_id"])
    except discord.NotFound:
        await interaction.edit_original_response(
            content="Original message was deleted."
        )
        return
    embed = message.embeds[0]
    total = entry["total"]
    embed.set_field_at(
        index=4,
        name="**Progress**",
        value=f"{new_progress}/{total}",
        inline=True
    )
    storage[key]["progress"] = new_progress
    save_storage(storage)
    await message.edit(embed=embed)
    await interaction.edit_original_response(
        content="Progress updated!"
    )

    
@bot.tree.command(name="add", description="Add manga by providing the name, rating, and a short review", guild = discord.Object(id=GUILD_ID))
async def add(
    interaction: discord.Interaction, 
    manga_name: str, 
    compl_date: Optional[str], 
    rating :Optional [float], 
    review: Optional[str], 
    manga_url: str,
    progress: float):
    await interaction.response.defer(ephemeral=True)
    manga = send_id_query(manga_title = manga_name)
    reviewed = False
    manga_id = int(manga[0])
    manga_title = manga[1]
    manga_chapters = manga[2]
    manga_status = manga[3]
    if not manga or not manga[0]:
        await interaction.edit_original_response(content="No manga found by that title")
        return
    cover_img_link = send_img_query(manga_id)
    if not compl_date:
        today = date.today()
        formatted_date = today.strftime("%d/%m/%y")
    else:
         formatted_date = compl_date
    if rating:
         usr_rating = str(rating) + "⭐"
    else:
         usr_rating = "*"
    
    description = send_desc_query(manga_id)
    storage = load_storage()
    if interaction.channel_id == CHANNEL_ID: 
        count = 1 + sum(
            1
            for entry in storage.values()
            if entry["channel_id"] == CHANNEL_ID
        )
        embed = discord.Embed(
            title= f"{count}. {manga_title}",
            url = f"{manga_url}",
            description= f"{description}",
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title= f"{manga_title}",
            url = f"{manga_url}",
            description= f"{description}",
            color=discord.Color.blue()
        )
    author_name = interaction.user.display_name
    author_avatar_url = interaction.user.display_avatar.url
    user = interaction.user
    embed.set_author(name = author_name, icon_url = author_avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1368305647115829248/1470479316428128472/toppng.com-anime-loli-kawaii-chibi-cute-nice-books-niconiconii-sleeping-cute-animated-girl-499x452_2.png?ex=698b7215&is=698a2095&hm=4a42f6418b9fcf3c865984c6bdbcbef6ba6930e854dea4dc586625eec584ac8c&")
    embed.set_image(url= cover_img_link)
    embed.add_field(name = f"**Chapters: **", value = f"{manga_chapters}" , inline= True)
    embed.add_field(name = f"**Status: **", value = f"{manga_status}" , inline= True)
    embed.add_field(name = "**Date finished reading: **" , value = f"{formatted_date}" , inline= True)
    embed.add_field(name = f"**Rating:**", value = f"{usr_rating}" , inline= False)
    embed.add_field(name = "**Progress: **", value = f"{progress}/{manga_chapters}", inline= True)
    if review:
        embed.add_field(name = "**Review: **", value =f"||{review}||"  , inline= False)
        reviewed = True
    embed.set_footer(text = f"https://github.com/TheDude2701/minum_manga                                MangaID: {manga_id}")
    try:
        message = await interaction.channel.send(embed=embed)
        key = f"{int(manga_id)}:{int(user.id)}"
        storage[key] = {
            "channel_id": interaction.channel.id,
            "message_id": message.id,
            "total": manga_chapters,
            "reviewed": reviewed,
            "sender": user.id,
            "progress": progress
        }
        save_storage(storage)
        await interaction.edit_original_response(content="Completed")
    except Exception as e:
        await interaction.channel.send(
            f"Failed to send embed: Invalid URL or other error.\nDetails: {e}"
        )

@bot.tree.command(name="manualadd", description="Manually add a manga by providing the name, rating, and a short review", guild = discord.Object(id=GUILD_ID))
async def manualadd(
    interaction: discord.Interaction, 
    manga_name: str, 
    manga_status: str,
    compl_date: Optional[str], 
    rating :Optional [float], 
    review: Optional[str], 
    manga_url: str,
    progress: float,
    descr: str,
    chap_num: float,
    img_url: Optional[str]
    ):
    await interaction.response.defer(ephemeral=True)
    reviewed = False
    if not compl_date:
        today = date.today()
        formatted_date = today.strftime("%d/%m/%y")
    else:
         formatted_date = compl_date
    if rating:
         usr_rating = str(rating) + "⭐"
    else:
         usr_rating = "*"
    storage = load_storage()
    if interaction.channel_id == CHANNEL_ID: 
        count = 1 + sum(
            1
            for entry in storage.values()
            if entry["channel_id"] == CHANNEL_ID
        )
        embed = discord.Embed(
            title= f"{count}. {manga_name}",
            url = f"{manga_url}",
            description= f"{descr}",
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title= f"{manga_name}",
            url = f"{manga_url}",
            description= f"{descr}",
            color=discord.Color.blue()
        )
    manga_id = random_code()
    user = interaction.user
    author_name = interaction.user.display_name
    author_avatar_url = interaction.user.display_avatar.url
    embed.set_author(name = author_name, icon_url = author_avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1368305647115829248/1470479316428128472/toppng.com-anime-loli-kawaii-chibi-cute-nice-books-niconiconii-sleeping-cute-animated-girl-499x452_2.png?ex=698b7215&is=698a2095&hm=4a42f6418b9fcf3c865984c6bdbcbef6ba6930e854dea4dc586625eec584ac8c&")

    if img_url:
        embed.set_image(url= img_url)
    embed.add_field(name = f"**Chapters: **", value = f"{chap_num}" , inline= True)
    embed.add_field(name = f"**Status: **", value = f"{manga_status}" , inline= True)
    embed.add_field(name = "**Date finished reading: **" , value = f"{formatted_date}" , inline= True)
    embed.add_field(name = f"**Rating:**", value = f"{usr_rating}" , inline= False)
    embed.add_field(name = "**Progress: **", value = f"{progress}/{chap_num}", inline= True)
    if review:
        embed.add_field(name = "**Review: **", value =f"||{review}||"  , inline= False)
        reviewed = True
    embed.set_footer(text = f"https://github.com/TheDude2701/minum_manga                                MangaID: {manga_id}")
    try:
        message = await interaction.channel.send(embed=embed)
        key = f"{manga_id}:{user.id}"
        storage[key] = {
            "channel_id": interaction.channel.id,
            "message_id": message.id,
            "total": chap_num,
            "reviewed": reviewed,
            "sender": user.id,
            "progress": progress
        }
        save_storage(storage)
        await interaction.edit_original_response(content="Completed")
    except Exception as e:
        await interaction.channel.send(
            f"Failed to send embed: Invalid URL or other error.\nDetails: {e}"
        )    

@bot.tree.command(name="search", description="Search up a manga in anilist by name", guild = discord.Object(id=GUILD_ID))
async def search(
    interaction: discord.Interaction, 
    manga_name: str, 
):
    await interaction.response.defer(ephemeral=True)
    manga = send_id_query(manga_title = manga_name)
    if not manga or not manga[0]:
        await interaction.edit_original_response(content="No manga found by that title")
        return
    manga_id = int(manga[0])
    manga_title = manga[1]
    manga_chapters = manga[2]
    manga_status = manga[3]
    cover_img_link = send_img_query(manga_id)
    description = send_desc_query(manga_id)
    author_name = interaction.user.display_name
    author_avatar_url = interaction.user.display_avatar.url
    url_clean = manga_name.replace(" ", "-")
    manga_url = f"https://anilist.co/manga/{manga_id}/{url_clean}/"
    embed = discord.Embed(
            title= f"{manga_title}",
            url = f"{manga_url}",
            description= f"{description}",
            color=discord.Color.blue()
    )
    embed.set_author(name = author_name, icon_url = author_avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1368305647115829248/1470479316428128472/toppng.com-anime-loli-kawaii-chibi-cute-nice-books-niconiconii-sleeping-cute-animated-girl-499x452_2.png?ex=698b7215&is=698a2095&hm=4a42f6418b9fcf3c865984c6bdbcbef6ba6930e854dea4dc586625eec584ac8c&")
    embed.set_image(url= cover_img_link)
    embed.add_field(name = f"**Chapters: **", value = f"{manga_chapters}" , inline= True)
    embed.add_field(name = f"**Status: **", value = f"{manga_status}" , inline= True)
    embed.set_footer(text = f"https://github.com/TheDude2701/minum_manga                                MangaID: {manga_id}")
    try:
        await interaction.channel.send(embed=embed) 
        await interaction.edit_original_response(content="Completed")
    except Exception as e:
        await interaction.channel.send(
            f"Failed to send embed: Invalid URL or other error.\nDetails: {e}"
        )
