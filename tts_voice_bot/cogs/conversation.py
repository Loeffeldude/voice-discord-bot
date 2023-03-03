import asyncio
from typing import Union
import discord


from tts_voice_bot.cogs.personality import PersonalityCog, get_personality_options
from tts_voice_bot.personalities.personality import Personality


class ConversationCog(discord.Cog):
    bot: discord.Bot
    personality_cog: PersonalityCog

    def __init__(self, bot):
        self.bot = bot
        self.personality_cog = self.bot.get_cog(PersonalityCog.__name__)

    def get_personality(self, personality_name):
        if not self.personality_cog:
            self.personality_cog = self.bot.get_cog(PersonalityCog.__name__)

        return self.personality_cog.get_personality_cls(personality_name)

    def should_ignore_message(self, message: discord.Message):
        if message.author.bot:
            return True

        if not message.guild:
            return True

        if not message.channel.type == discord.ChannelType.public_thread:
            return True

        thread: discord.Thread = message.channel

        if thread.owner != self.bot.user:
            return True

        if thread.archived:
            return True

        return False

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        if self.should_ignore_message(message):
            return

        thread: discord.Thread = message.channel
        personality_name = thread.name[18:]
        personality_cls = self.get_personality(personality_name)

        if not personality_cls:
            return

        personality: Personality = personality_cls(self.bot)

        async with thread.typing():
            chat = await personality.create_chat(thread)
            response = chat.choices[0].message.content

            await thread.send(response)
        if message.author.voice and message.author.voice.channel:
            # await personality.talk(message.author.voice.channel, response)
            pass

    @discord.slash_command()
    @discord.default_permissions(manage_messages=True)
    async def start_convo(
        self,
        ctx: discord.context.ApplicationContext,
        personality_name: discord.Option(
            str,
            description="The personality to use for the conversation",
            choices=get_personality_options(),
            required=True,
        ),
    ):
        personality_cls = self.get_personality(personality_name)

        if personality_cls == None:
            await ctx.respond(
                "Personality not found. To get a list of all personalities, use /list_personalities"
            )
            return

        personality: Personality = personality_cls(self.bot)

        thread_name = f"Conversation with {personality.name}"

        if len(thread_name) > 100:
            thread_name = thread_name[:97] + "..."

        thread_cor = ctx.channel.create_thread(
            name=thread_name,
            auto_archive_duration=1440,
            message=ctx.message,
            type=discord.ChannelType.public_thread,
            reason=f"Conversation started by {ctx.author}",
        )
        edit_cor = ctx.guild.me.edit(nick=personality.name)

        thread, _ = await asyncio.gather(thread_cor, edit_cor)

        await personality.setup_thread(thread)
        await ctx.respond()
