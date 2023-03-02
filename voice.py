import wave
import pydub
import subprocess
import pathlib
import os
import requests
import discord
import aiohttp
import asyncio

BASE_URL = "https://api.elevenlabs.io"
STABILITY = 0.7
SIMILARITY_BOOST = 0.7


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


async def voice_to_pcm(text, voice_id):
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
        process.stdin.close()

    asyncio.create_task(write_to_process())

    return audio
