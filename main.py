from tts_voice_bot.bot import bot
from tts_voice_bot.settings import DISCORD_TOKEN
import asyncio

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
