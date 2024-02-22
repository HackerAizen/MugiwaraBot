import discord
from discord.ext import commands
import asyncio

from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key="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",
)

class gpt_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command(name="gpt", help="Use to call gpt response")
    async def gpt(self, ctx, *, args):
        print(args)
        result = str(args)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": result,
                }
            ],
            model="gpt-3.5-turbo",
        )
        await ctx.send(embed=discord.Embed(title=f'{result}', description=response.choices[0].message.content))