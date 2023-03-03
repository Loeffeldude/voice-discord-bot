import subprocess
import os
import discord
import aiohttp
import asyncio
import concurrent.futures
from discord.opus import Encoder as OpusEncoder

from tts_voice_bot.settings import (
    ELEVEN_LABS_BASE_URL as BASE_URL,
    STABILITY,
    SIMULARITY_BOOST,
)


class ElevenLabsAudioSource(discord.AudioSource):
    def __init__(
        self,
        voice_id,
        text,
        stability=STABILITY,
        simularity_boost=SIMULARITY_BOOST,
        loop=None,
    ):
        self.voice_id = voice_id
        self.text = text
        self.stability = stability
        self.simularity_boost = simularity_boost
        self.loop = loop or asyncio.get_event_loop()

        self._create_stream()
        self._spawn_process()

        self._pipe_task = self.loop.create_task(self._pipe_stream())

    def _spawn_process(self):
        self.process = subprocess.Popen(
            ["mpg123", "-s", "-q", "--stereo", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    async def _voice_stream(self):
        if self.stability > 1 or self.stability < 0:
            raise ValueError("stability must be between 0 and 1")

        if self.simularity_boost > 1 or self.simularity_boost < 0:
            raise ValueError("simularity_boost must be between 0 and 1")

        request_url = f"{BASE_URL}/v1/text-to-speech/{self.voice_id}/stream"
        request_data = {
            "text": self.text,
            "voice_settings": {
                "stability": self.stability,
                "similarity_boost": self.simularity_boost,
            },
        }
        # TODO: too much nesting for my taste.
        async with aiohttp.ClientSession() as session:
            async with session.post(
                request_url,
                json=request_data,
                headers={"xi-api-key": os.getenv("ELEVEL_LABS_API_KEY")},
            ) as r:
                async for chunk in r.content.iter_chunked(OpusEncoder.FRAME_SIZE):
                    yield chunk

    def _create_stream(self):
        self.stream = self._voice_stream()

    async def _pipe_stream(self):
        async for chunk in self.stream:
            self.process.stdin.write(chunk)
            self.process.stdin.flush()

    def read(self):
        read =  self.process.stdout.read(OpusEncoder.FRAME_SIZE)
        if read == b"":
            return None
        return read


    def cleanup(self):
        self._pipe_task.cancel()
        self.process.stdin.close()
        self.process.wait()

    def is_opus(self):
        return False
