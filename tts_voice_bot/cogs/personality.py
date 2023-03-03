from typing import Dict
import discord
import tts_voice_bot.personalities as personalities_mod
from tts_voice_bot.personalities.personality import Personality
import inspect


def get_personalities():
    result = {}
    for _, obj in inspect.getmembers(personalities_mod):
        if inspect.isclass(obj) and issubclass(obj, Personality):
            personality_name = obj.name
            result[personality_name] = obj

    return result


def get_personality_options():
    return [
        discord.OptionChoice(personality, personality)
        for personality in get_personalities().keys()
    ]


class PersonalityCog(discord.Cog):
    personalities: Dict[str, Personality]

    def __init__(self, bot):
        self.bot = bot
        self.personalities = {}
        self._load_personalities()

    def _load_personalities(self):
        self.personalities = get_personalities()

    def get_personality_cls(self, personality_name):
        return self.personalities.get(personality_name, None)

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

    @discord.slash_command()
    @discord.default_permissions(manage_messages=True)
    async def personality_talk(
        self,
        ctx: discord.context.ApplicationContext,
        personality_name: discord.Option(
            str,
            description="The personality to use for the conversation",
            choices=get_personality_options(),
            required=True,
        ),
        text: discord.Option(str, description="The text to say", required=True),
    ):
        personality_cls = self.get_personality_cls(personality_name)

        if not personality_cls:
            await ctx.respond(
                "Personality not found. To get a list of all personalities, use /list_personalities"
            )
            return

        personality: Personality = personality_cls(self.bot)

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.respond("You are not in a voice channel")
            return

        await ctx.defer()
        try:
            await personality.talk(ctx.author.voice.channel, text)
        except Exception as e:
            print(e)
            await ctx.send_followup(content=f"Error: {e}", ephemeral=True)
            return
        await ctx.send_followup(content="Done!", ephemeral=True, delete_after=5)
