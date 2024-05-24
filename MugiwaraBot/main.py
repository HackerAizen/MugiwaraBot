import discord
import os
import sys
import asyncio
import json
import datetime
import constants

from discord.ext import tasks, commands
from discord.utils import get

from cogs.music_cog import music_cog
from cogs.gpt_cog import gpt_cog
from cogs.poll_cog import Poll
from cogs.moderator_cog import moderator_cog
from cogs.solo_leveling import SoloLeveling
from cogs.quizcog import quiz_cog

# командный префикс и подключение всех зависимостей для бота
bot = commands.Bot(command_prefix=constants.PREFIX, intents=discord.Intents().all())

async def to_integ(dt_time):
    answer = 100000000 * dt_time.year + 1000000 * dt_time.month + 10000 * dt_time.day + 100 * dt_time.hour + dt_time.minute
    return int(answer)

@bot.event
async def on_ready():
    print("- АККАУНТ БОТА -")
    print()
    print(f"Имя бота: {bot.user.name}")
    print(f"ID бота: {bot.user.id}")
    print(f"Токен бота: {constants.TOKEN}")
    print()

    # await bot.tree.sync()
    await bot.add_cog(music_cog(bot))
    await bot.add_cog(gpt_cog(bot))
    await bot.add_cog(Poll(bot))
    await bot.add_cog(moderator_cog(bot))
    await bot.add_cog(SoloLeveling(bot))
    await bot.add_cog(quiz_cog(bot))

    # хранение информации о пользователях
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as file:
            file.write('{}')
            file.close()

        for guild in bot.guilds:
            for member in guild.members:
                with open('users.json', 'r') as file:
                    data = json.load(file)
                    file.close()
                
                with open('users.json', 'w') as file:
                    data[str(member.id)] = {
                        "WARNS": 0,
                        "CAPS": 0,
                        "experience": 0,
                        "level": 1,
                        "LastMessage": await to_integ(datetime.datetime.now())
                    }

                    json.dump(data, file, indent=4)
                    file.close()
    # message = await bot.get_channel(1209855027498459136).send('Для получения роли поставьте реакцию одной из ролей:' + '\n' + '<:Student:1209854436621684756> Student' +'\n' + '<:Shanks:1209854160149811246> Shanks')
    # for item in ['<:Student:1209854436621684756>', '<:Shanks:1209854160149811246>']:
    #     await message.add_reaction(item)

@bot.event
async def on_message(message):
    WARN = constants.BADWORDS

    for iter in range(0, len(WARN)):
        if WARN[iter] in message.content.lower():
            await message.delete()
            with open('users.json', 'r') as file:
                data = json.load(file)
                file.close()
            
            with open('users.json', 'w') as file:
                data[str(message.author.id)]['WARNS'] += 1
                json.dump(data, file, indent=4)
                file.close()
            
            emb = discord.Embed(
                title="Нарушение правил сервера",
                description=f"*Пользователь был замечен за нарушеним {data[str(message.author.id)]['WARNS'] - 1} раз. После 5 нарушения последует бан!*",
                timestamp=message.created_at,
                color=discord.Color.from_rgb(255, 51, 51)
            )

            emb.add_field(name="Канал:", value=message.channel.mention, inline=True)
            emb.add_field(name="Пользователь:", value=message.author.mention, inline=True)
            emb.add_field(name="Тип нарушения:", value="Употребление ненормативной лексики/публикация ссылок", inline=True)

            await get(message.guild.text_channels, id=1192452700365930526).send(embed=emb)

            if data[str(message.author.id)]['WARNS'] >= 5:
                await message.author.ban(reason="Превышено допустимое кол-во нарушений на сервере.")
            break
    
    if message.content.isupper():
        with open('users.json', 'r') as file:
            data = json.load(file)
            file.close()
        
        with open('users.json', 'w') as file:
            data[str(message.author.id)]['CAPS'] += 1
            json.dump(data, file, indent=4)
            file.close()

        if data[str(message.author.id)]['CAPS'] >= 3:
            await message.delete()

            with open('users.json', 'w') as file:
                data[str(message.author.id)]['CAPS'] = 0
                data[str(message.author.id)]['WARNS'] += 1
                json.dump(data, file, indent=4)
                file.close()

            emb = discord.Embed(
                title="Нарушение правил сервера",
                description=f"*Пользователь был замечен за нарушеним {data[str(message.author.id)]['WARNS'] - 1} раз. После 5 нарушения последует бан!*",
                timestamp=message.created_at,
                color=discord.Color.from_rgb(255, 51, 51)
            )

            emb.add_field(name="Канал:", value=message.channel.mention, inline=True)
            emb.add_field(name="Пользователь:", value=message.author.mention, inline=True)
            emb.add_field(name="Тип нарушения:", value="КАПС использование", inline=True)

            await get(message.guild.text_channels, id=1192452700365930526).send(embed=emb)

            if data[str(message.author.id)]['WARNS'] >= 5:
                await message.author.ban(reason="Превышено допустимое кол-во нарушений на сервере.")
    
    # await bot.process_commands(message)
    await bot.process_commands(message)
        
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=discord.Embed(
            title="Ошибка поиска команды",
            description="*Такой команды не существует, напищите !help для просмотра комманд*",
            timestamp=ctx.message.created_at,
            color=discord.Color.from_rgb(128, 255, 0)
        ))

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == 1209874442092814376:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, bot.guilds)
        if payload.emoji.name == 'Shanks':
            role = discord.utils.get(guild.roles, name='Shanks')
        elif payload.emoji.name == 'Student':
            role = discord.utils.get(guild.roles, name='Student')
        if role is not None:
            member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
            if member is not None:
                await member.remove_roles(role)

bot.run(constants.TOKEN)