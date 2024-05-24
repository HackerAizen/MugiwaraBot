import discord
from discord.ext import commands
import asyncio

import json
from discord.utils import get

class moderator_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Give a warn to user")
    @commands.has_permissions(manage_channels=True)
    async def warn(self, ctx, member: discord.Member, reason: str):
        if reason.lower() == "badwords" or reason.lower() == "links":
            with open('users.json', 'r') as file:
                data = json.load(file)
                file.close()
                
            with open('users.json', 'w') as file:
                data[str(member.id)]['WARNS'] += 1
                json.dump(data, file, indent=4)
                file.close()
                
            emb = discord.Embed(
                title="Нарушение правил сервера",
                description=f"*Пользователь был замечен за нарушеним {data[str(member.id)]['WARNS'] - 1} раз. После 5 нарушения последует бан!*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(255, 51, 51)
            )

            emb.add_field(name="Канал:", value='не определён', inline=True)
            emb.add_field(name="Пользователь:", value=member.mention, inline=True)
            emb.add_field(name="Тип нарушения:", value="Употребление ненормативной лексики/публикация ссылок", inline=True)

            await get(ctx.guild.text_channels, id=1192452700365930526).send(embed=emb)

            if data[str(member.id)]['WARNS'] >= 5:
                await member.ban(reason="Превышено допустимое кол-во нарушений на сервере.")
            
            await ctx.message.reply(embed=discord.Embed(
                title="Успешно",
                description="*Предупреждение выдано*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(0, 0, 255)
            ))
        elif reason.lower() == "caps":
            with open('users.json', 'r') as file:
                data = json.load(file)
                file.close()
            
            with open('users.json', 'w') as file:
                data[str(member.id)]['CAPS'] = 0
                data[str(member.id)]['WARNS'] += 1
                json.dump(data, file, indent=4)
                file.close()

            emb = discord.Embed(
                title="Нарушение правил сервера",
                description=f"*Пользователь был замечен за нарушеним {data[str(member.id)]['WARNS'] - 1} раз. После 5 нарушения последует бан!*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(255, 51, 51)
            )

            emb.add_field(name="Канал:", value='не определён', inline=True)
            emb.add_field(name="Пользователь:", value=member.mention, inline=True)
            emb.add_field(name="Тип нарушения:", value="КАПС использование", inline=True)

            await get(ctx.guild.text_channels, id=1192452700365930526).send(embed=emb)

            if data[str(member.id)]['WARNS'] >= 5:
                await member.ban(reason="Превышено допустимое кол-во нарушений на сервере.")
            
            await ctx.message.reply(embed=discord.Embed(
                title="Успешно",
                description="*Предупреждение выдано*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(48, 25, 52)
            ))
        else:
            await ctx.message.reply(embed=discord.Embed(
                title="Ошибка",
                description="Причина упущения",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(0, 102, 204)
            ))

    @warn.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(
                title="Ошибка потери",
                description="*Использование команды: !warn (@Участник) (Причина)*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(128, 255, 0)
            ))
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title="Ошибка доступа",
                description="*Вам недоступна данная команда из-за нехватки прав*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(128, 255, 0)
            ))

    @commands.command(help="Remove a warn from user")
    @commands.has_permissions(manage_channels=True)
    async def unwarn(self, ctx, member: discord.Member):
        with open('users.json', 'r') as file:
            data = json.load(file)
            file.close()

        with open('users.json', 'w') as file:
            if data[str(member.id)]['WARNS'] > 0:
                data[str(member.id)]['WARNS'] -= 1
                await ctx.send(embed=discord.Embed(
                    title="Снятие предупреждения",
                    description=f"C @{member.name} снято одно предупреждение! Теперь их {data[str(member.id)]['WARNS']}",
                    timestamp=ctx.message.created_at,
                    color=discord.Color.from_rgb(128, 255, 0)
                ))
            else:
                emb = discord.Embed(
                    title="Нарушение правил сервера",
                    description=f"*У пользователя @{member.name} итак 0 нарушений. Снимать нечего*"
                )
                await ctx.send(embed=emb)
            json.dump(data, file, indent=4)
            file.close()

    @unwarn.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(
                title="Ошибка потери",
                description="*Использование команды: !unwarn (@Участник)*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(128, 255, 0)
            ))
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title="Ошибка доступа",
                description="*Вам недоступна данная команда из-за нехватки прав*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(128, 255, 0)
            ))

    @commands.command(help="Remove all warns from user")
    @commands.has_permissions(administrator=True)
    async def clear_warns(self, ctx, member: discord.Member):
        with open('users.json', 'r') as file:
            data = json.load(file)
            file.close()

        with open('users.json', 'w') as file:
            data[str(member.id)]['WARNS'] = 0
            json.dump(data, file, indent=4)
            file.close()
        
        await ctx.send(embed=discord.Embed(
            title="Снятие всех предупреждений",
            description=f"C @{member.name} сняты все предупреждения!",
            timestamp=ctx.message.created_at,
            color=discord.Color.from_rgb(128, 255, 0)
        ))

    @clear_warns.error
    async def error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(
                title="Ошибка потери",
                description="*Использование команды: !clear_warns (@Участник)*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(128, 255, 0)
            ))
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title="Ошибка доступа",
                description="*Вам недоступна данная команда из-за нехватки прав*",
                timestamp=ctx.message.created_at,
                color=discord.Color.from_rgb(128, 255, 0)
            ))