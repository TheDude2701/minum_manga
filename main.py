from minum_bot.minum_bot import bot
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).parent / "config.env"
load_dotenv(dotenv_path=dotenv_path)

def main():
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise RuntimeError("API_KEY is not set")
    bot.run(API_KEY)

if __name__ == "__main__":
    main()