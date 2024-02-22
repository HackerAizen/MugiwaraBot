import discord
from discord.ext import commands
import asyncio

import googletrans
import constants

class translate_cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.flags = constants.flag_emoji_dict

    @commands.command(name="translate", aliases=['tr'],help="Translate text to a required language")
    async def translate(self, ctx, lang_to, *args):
        langu = lang_to.lower()
        if langu not in googletrans.LANGUAGES and langu not in googletrans.LANGCODES:
            raise commands.BadArgument
        if lang_to and not args:
            raise commands.CommandInvokeError
        
        translator_machine = googletrans.Translator()
        text_to_trans = ' '.join(args)
        translated_text = translator_machine.translate(text_to_trans, dest=langu).text
        pron_mess = translator_machine.translate(text_to_trans, dest=langu).pronunciation
        det_langue = translator_machine.detect(text_to_trans)
        embed=discord.Embed(
            title="Спасибо за использование команды!",
            description=f"Перевод: **{translated_text}**",
            timestamp=ctx.message.created_at,
            color=discord.Color.from_rgb(51, 255, 255)
        )
        embed.add_field(name="Запрос перевода", value=text_to_trans, inline=False)
        embed.add_field(name="Переведено с:", value=f'{det_langue.lang.capitalize()} ({det_langue.confidence*100:.2f}%)')
        embed.add_field(name="Произношение:", value=pron_mess, inline=False)
        await ctx.message.reply(embed=embed)

    @translate.error
    async def error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(
                title="Ошибка перевода",
                description="**Invalid language to translate your text to! Rewrite**",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(128, 255, 0)
            ))

        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(embed=discord.Embed(
                title="Ошибка потери",
                description="**Использование команды: !tr (язык/код языка) (обязательно: текст на перевод)**",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(128, 255, 0)
            ))
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Check if the reaction is a flag emoji
        if reaction.emoji in self.flags:
            translator_machine = googletrans.Translator()
            # Get the language code corresponding to the flag emoji
            langu_code = self.flags[reaction.emoji]
            # Get the original message
            message = reaction.message
            # Translate the message to the desired language
            det_langu = translator_machine.detect(message.content)
            translated_text = translator_machine.translate(message.content, dest=langu_code).text
            pronunce_mess = translator_machine.translate(message.content, dest=langu_code).pronunciation
            embed = discord.Embed(title='Translated Text',
                                description=f'**{translated_text}**',
                                color=discord.Color.from_rgb(76, 0, 153))
            embed.add_field(name="Original Text", value=message.content, inline=False)
            embed.add_field(name="Translated from:", value=f'{det_langu.lang.capitalize()} ({det_langu.confidence*100:.2f}%)')
            embed.add_field(name="Pronunciation:", value=pronunce_mess, inline=False)
            await reaction.message.channel.send(content=f'{user.mention}',embed=embed)