from dotenv import load_dotenv

load_dotenv()

from voice import voice_to_pcm
import discord
from discord.ext import commands
import os
import asyncio

discord.opus.load_opus("libopus.so.0")

VOICE_ID = os.environ.get("VOICE_ID")
TALK_DISCONNECT_DELAY = 2

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def talk(ctx: commands.Context, *, text):

    voice_client = await ctx.author.voice.channel.connect()
    audio = await voice_to_pcm(text, VOICE_ID)

    async def after_playing(error):
        if error:
            print(error)
            await voice_client.disconnect()
            return

        await asyncio.sleep(TALK_DISCONNECT_DELAY)

        if not voice_client.is_playing():
            await voice_client.disconnect()

    # Start playing the audio and pass the after_playing function as the 'after' parameter
    voice_client.play(
        audio,
        after=lambda e: asyncio.run_coroutine_threadsafe(
            after_playing(e), loop=bot.loop
        ),
    )


if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_TOKEN"))
