import subprocess
import os
import discord
import aiohttp
import asyncio

from tts_voice_bot.settings import (
    ELEVEN_LABS_BASE_URL as BASE_URL,
    STABILITY,
    SIMILARITY_BOOST,
)


async def stream_voice(text, voice_id, chunck_size=1024):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/v1/text-to-speech/{voice_id}/stream",
            json={
                "text": text,
                "voice_settings": {
                    "stability": STABILITY,
                    "similarity_boost": SIMILARITY_BOOST,
                },
            },
            headers={"xi-api-key": os.getenv("ELEVEL_LABS_API_KEY")},
        ) as r:
            async for chunk in r.content.iter_chunked(chunck_size):
                if chunk:
                    yield chunk


def voice_to_pcm(text, voice_id):
    """
    Reads the voice from the API and returns a discord.PCMAudio object
    This function is blocking
    """
    stream = stream_voice(text, voice_id, chunck_size=7680)

    process = subprocess.Popen(
        ["mpg123", "-s", "-q", "--stereo", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    audio = discord.PCMAudio(process.stdout)

    async def write_to_process():
        async for chunk in stream:
            process.stdin.write(chunk)
            process.stdin.flush()
        # the mpg123 process will exit after everything is read from stdin
        # so we don't need to close it
        process.stdin.close()

    asyncio.run_coroutine_threadsafe(write_to_process(), loop=asyncio.get_event_loop())

    return audio
