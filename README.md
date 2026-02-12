# minum_manga

A simple discord bot you use to post reviews and info, uses anilist api to pull info on the manga based on manga name.

# FEATURES


The bot fetches manga info (title, chapters, status, cover image, description) from anilist API (Some manga might not be on there)

Add manga with /add, bot will send an embed message containing info about the anime and the details you add

/update to update an existing post from the bot

/search to search for the manga from the anilist manga database, returns the top search result

/updateprogress to update the progress read on the manga


## SETUP

Python 3.11+

Discord bot token

Required Python libraries:
    1. discord.py
    2. python-dotenv
    3. requests

1. Clone the repository
    ```bash
    git clone https://github.com/TheDude2701/minum_manga.git
    cd minum_manga 
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Add your Discord Bot Token (Inside the config.env file):
    ```bash
    API_KEY=your_discord_bot_token_here
    SERVER_ID=your_server_id_here
    CHANNEL_ID=your_channel_id_here
    ```
4. Run the bot:
    ```bash
    python main.py
    ```
