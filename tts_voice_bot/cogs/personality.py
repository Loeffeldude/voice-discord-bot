from typing import Dict
import discord
import tts_voice_bot.personalities as personalities_mod
from tts_voice_bot.personalities.personality import Personality
import inspect


class PersonalityCog(discord.Cog):
    personalities: Dict[str, Personality]

    def __init__(self, bot):
        self.bot = bot
        self.personalities = {}
        self._load_personalities()

    @classmethod
    def get_personalities(cls):
        result = {}
        for _, obj in inspect.getmembers(personalities_mod):
            if inspect.isclass(obj) and issubclass(obj, Personality):
                personality_name = obj.name
                result[personality_name] = obj

        return result

    def _load_personalities(self):
        self.personalities = self.get_personalities()

    @discord.slash_command()
    @discord.default_permissions(manage_messages=True)
    async def list_personalities(self, ctx: discord.context.ApplicationContext):
        embed = discord.Embed(
            title="List of personalities",
            description="The following personalities are available:",
        )
        for name, personality in self.personalities.items():
            embed.add_field(name=name, value=personality.description, inline=False)

        await ctx.respond(embed=embed)
