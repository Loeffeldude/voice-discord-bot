from tts_voice_bot.cogs.conversation import ConversationCog
from tts_voice_bot.cogs.personality import PersonalityCog
from tts_voice_bot.settings import TALK_DISCONNECT_DELAY, VOICE_ID
from tts_voice_bot.voice import voice_to_pcm
import discord

import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

bot.add_cog(ConversationCog(bot))
bot.add_cog(PersonalityCog(bot))
