import asyncio
import openai
from discord.threads import Thread
import discord
from tts_voice_bot.settings import TALK_DISCONNECT_DELAY, THREAD_MESSAGE_LIMIT
from tts_voice_bot.voice import voice_to_pcm

ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"


class Personality:
    name: str
    description: str

    voice_id: str
    init_prompt: str
    # the response to the init prompt for the desired behavior
    intro_response: str

    bot: discord.Bot

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    async def setup_thread(self, thread: Thread):
        async with thread.typing():
            await thread.send(self.intro_response)

    def _get_init_messages(self):
        return [
            {"role": ROLE_SYSTEM, "content": self.init_prompt.replace("\n", " ")},
        ]

    async def _create_messages_from_thread(self, thread: Thread):
        history = thread.history(before=thread.last_message, limit=THREAD_MESSAGE_LIMIT)

        chat_messages = []

        def add_message(message: discord.Message):
            role = ROLE_ASSISTANT if message.author.id == thread.owner.id else ROLE_USER
            prefix = f"{message.author.display_name}: " if role == ROLE_USER else ""
            chat_messages.append(
                {
                    "role": role,
                    "content": f"{prefix}{message.content}",
                    "time": message.created_at,
                }
            )

        if thread.last_message:
            add_message(thread.last_message)

        async for message in history:
            add_message(message)

        chat_messages.sort(key=lambda message: message["time"])

        for message in chat_messages:
            del message["time"]

        return [*self._get_init_messages(), *chat_messages]

    async def create_chat(self, thread: Thread):
        chat_messages = await self._create_messages_from_thread(thread)
        chat = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=chat_messages,
        )
        return chat

    async def talk(self, channel: discord.VoiceChannel, text: str):
        try:
            voice_client = await channel.connect()
        except discord.ClientException:
            voice_client = self.bot.voice_clients[0]

        if voice_client.is_playing():
            voice_client.stop()

        audio = voice_to_pcm(text, self.voice_id)

        voice_client.play(audio)

    def transform_message(self, text: str):
        """Override this function to transform the message before it is sent to the chat engine."""
        return text
    
    def transform_to_tts(self, text: str):
        """Override this function to transform the text before it is sent to the TTS engine."""
        return text