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
    entry = storage.get(str(manga_id))
    if not entry:
        await interaction.edit_original_response(content="No tracked manga with that ID.")
        return
    review_flag = entry["reviewed"]
    if not entry:
        await interaction.edit_original_response(
            content="No tracked manga with that ID."
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
    if not manual:
        manga = send_status_query(manga_id)
        manga_status = manga[1]
        manga_chapters = manga[0]
    embed = message.embeds[0]
    if chapter:
        embed.set_field_at(index= 0 ,name = f"**Chapters: **", value = f"{chapter}" , inline= True)
    else:
        if not manual:
            embed.set_field_at(index= 0 ,name = f"**Chapters: **", value = f"{manga_chapters}" , inline= True) 
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
        if review_flag:
            embed.set_field_at(index = 5, name = "**Review: **", value =f"||{review}||"  , inline= False)
        else:
            embed.add_field(name = "**Review: **", value =f"||{review}||"  , inline= False)
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
    entry = storage.get(str(manga_id))

    if not entry:
        await interaction.edit_original_response(
            content="No tracked manga with that ID."
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
        await interaction.response.send_message("No manga found by that title!")
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
    author_name = interaction.user.display_name
    author_avatar_url = interaction.user.display_avatar.url
    embed = discord.Embed(
            title= f"{manga_title}",
            url = f"{manga_url}",
            description= f"{description}",
            color=discord.Color.blue()
    )
    embed.set_author(name = author_name, icon_url = author_avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1368305647115829248/1470477856995016902/toppng.com-anime-loli-kawaii-chibi-cute-nice-books-niconiconii-sleeping-cute-animated-girl-499x452.png?ex=698b70b9&is=698a1f39&hm=81c1b99e896957bbcde34f67ec5d814b950c8f0136b80f27185c9a4048b1f63b&")
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
        storage = load_storage()
        storage[str(manga_id)] = {
            "channel_id": interaction.channel.id,
            "message_id": message.id,
            "total": manga_chapters,
            "reviewed": reviewed
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
    manga_id = random_code()
    author_name = interaction.user.display_name
    author_avatar_url = interaction.user.display_avatar.url
    embed = discord.Embed(
            title= f"{manga_name}",
            url = f"{manga_url}",
            description= f"{descr}",
            color=discord.Color.blue()
    )
    embed.set_author(name = author_name, icon_url = author_avatar_url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1368305647115829248/1470477856995016902/toppng.com-anime-loli-kawaii-chibi-cute-nice-books-niconiconii-sleeping-cute-animated-girl-499x452.png?ex=698b70b9&is=698a1f39&hm=81c1b99e896957bbcde34f67ec5d814b950c8f0136b80f27185c9a4048b1f63b&")

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
        storage = load_storage()
        storage[str(manga_id)] = {
            "channel_id": interaction.channel.id,
            "message_id": message.id,
            "total": chap_num,
            "reviewed": reviewed
        }
        save_storage(storage)
        await interaction.edit_original_response(content="Completed")
    except Exception as e:
        await interaction.channel.send(
            f"Failed to send embed: Invalid URL or other error.\nDetails: {e}"
        )    

