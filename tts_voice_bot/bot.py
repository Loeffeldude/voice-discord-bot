from tts_voice_bot.cogs.conversation import ConversationCog
from tts_voice_bot.cogs.personality import PersonalityCog
import discord


intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

bot.add_cog(ConversationCog(bot))
bot.add_cog(PersonalityCog(bot))

