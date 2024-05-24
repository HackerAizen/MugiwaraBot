import json
import discord
from datetime import datetime
import constants
import random
from datetime import datetime
from discord.ext import commands, tasks

class SoloLeveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(constants.WELCOME_CHANNEL)
        embed = discord.Embed(
            description=f'Welcome **{member.mention}** to the server! Join my crew!',
            color=0xff55ff,
            timestamp=datetime.datetime.now()
        )
        role = discord.utils.get(member.guild.roles, name='TonyTonyChopper')
        await member.add_roles(role)
        await channel.send(embed=embed)
        with open('users.json', 'r') as file:
            data = json.load(file)
            file.close()
                
        with open('users.json', 'w') as file:
            data[str(member.id)] = {
                "WARNS": 0,
                "CAPS": 0,
                "experience": 0,
                "level": 1,
                "LastMessage": await self.to_integer(datetime.now())
            }

            json.dump(data, file, indent=4)
            file.close()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            with open('users.json','r')as f:
                users = json.load(f)
            await self.update_data(users, message.author)
            if(users[str(message.author.id)]['LastMessage'] < await self.to_integer(datetime.now())):
                await self.add_experience(users, message.author)
            await self.level_up(users, message.author, message.channel)


            with open('users.json', 'w')as f:
                json.dump(users, f)
                f.close()
        
    async def update_data(self, users, user):
        if not str(user.id) in users:
            users[str(user.id)] = {}
            users[str(user.id)]['experience'] = 0
            users[str(user.id)]['level'] = 1
            users[str(user.id)]['LastMessage'] = await self.to_integer(datetime.now())

    async def add_experience(self, users, user):
        users[str(user.id)]['experience'] += random.randint(15,25)
        users[str(user.id)]['LastMessage'] = await self.to_integer(datetime.now())


    async def level_up(self, users, user, message):
        experience = users[str(user.id)]['experience']
        lvl = users[str(user.id)]['level']
        lvl_end = 5 * (lvl ** 2) + (50 * lvl) + 100
        print(user)
        print(f"Level:{lvl}")
        print(f"experience:{experience}")
        print(f"lvl_end: {lvl_end} ")



        if lvl_end <= experience:
            channel=self.bot.get_channel(1240683206961795162)
            await channel.send('{} has leveld up to level {}'.format(user.mention, lvl+1))
            users[str(user.id)]['level'] = lvl+1
            users[str(user.id)]['experience'] -= lvl_end



    async def to_integer(self, dt_time):
        answer = 100000000 * dt_time.year + 1000000 * dt_time.month + 10000 * dt_time.day + 100 * dt_time.hour + dt_time.minute
        return int(answer)

    @commands.command()
    async def rank(self,ctx, user: discord.Member = None):
        with open('users.json','r')as f:
            users = json.load(f)

        if user is None:
            if not str(ctx.author.id) in users:
                users[str(ctx.author.id)] = {}
                users[str(ctx.author.id)]['experience'] = 0
                users[str(ctx.author.id)]['level'] = 0
                users[str(ctx.author.id)]['LastMessage'] = await self.to_integer(datetime.now())
            user=ctx.author
            lvl = int(users[str(ctx.author.id)]['level'])
            exp = int(5 * (lvl ** 2) + (50 * lvl) + 100)
            embed = discord.Embed(
                title=f"*{user}'s Rang*", 
                description=f"Experience: {lvl}/{5 * (lvl ** 2) + (50 * lvl) + 100}", 
                color=0x0091ff
            )
            print("OK")
            print("OK")
            embed.add_field(name=f"**{user}'s Rang**", value="💪  ", inline=False)
            print("OK")
            embed.add_field(name="Level", value=f"**{users[str(user.id)]['level']}**", inline=True)
            print("OK")
            embed.add_field(name="Experience", value=f"**{str(int(users[str(user.id)]['experience']))} / {exp}**",inline=True)
            print("OK")
            embed.set_footer(text="Type more to level up!\nSpam is useless")
            print("OK")
            await ctx.send(embed=embed)
            print("OK")
            await ctx.send(embed = discord.Embed(Title="OK"))

        else:
            print("NOT OK")
            if not str(user.id) in users:
                users[str(user.id)] = {}
                users[str(user.id)]['experience'] = 0
                users[str(user.id)]['level'] = 0
                users[str(user.id)]['LastMessage'] = await self.to_integer(datetime.now())
                print("NOT OK")
            lvl = int(users[str(user.id)]['level'])
            exp=int(5 * (lvl ** 2) + (50 * lvl) + 100)
            print("NOT OK")
            embed=discord.Embed(
                title=f"*{user}'s Rang*", 
                description=f"Experience: {lvl}/{5 * (lvl ** 2) + (50 * lvl) + 100}", 
                color=0x0091ff
            )
            embed.add_field(name=f"**{user}'s Rang**", value="💪  ", inline=False)
            embed.add_field(name="Level",value=f"**{users[str(user.id)]['level']}**",inline=True)
            embed.add_field(name="Experience", value=f"**{str(int(users[str(user.id)]['experience']))} / {exp}**", inline=True)
            embed.set_footer(text="Type more to level up!\nSpam is useless")
            await ctx.send(embed=embed)
            await ctx.send(embed = discord.Embed(Title="OK"))
            with open('users.json', 'w') as f:
                json.dump(users, f, indent=4)
                f.close()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_exp(self, ctx, user: discord.Member,nummer:int):
        with open('users.json', 'r')as f:
            users = json.load(f)
        if not ctx.author.bot:
            users[str(user.id)]['experience']+=int(nummer)
            await ctx.send("exp added")
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
            f.close()

    @commands.command()
    async def add_lvl(self, ctx, user: discord.Member,nummer:int):
        with open('users.json', 'r')as f:
            users = json.load(f)
        if not ctx.author.bot:
            users[str(user.id)]['level'] += int(nummer)
            await ctx.send("level added")
        with open('users.json', 'w')as f:
            json.dump(users, f, indent=4)
            f.close()

    @commands.command()
    async def add_database(self,ctx, user: discord.Member):
        with open('users.json', 'r')as f:
            users = json.load(f)
        if not str(user.id) in users:
            users[str(user.id)] = {}
            users[str(user.id)]['experience'] = 0
            users[str(user.id)]['level'] = 0
            users[str(user.id)]['LastMessage'] = await self.to_integer(datetime.now())
            await ctx.send("added to database!")
        else:
            await ctx.send("already in database!")

        with open('users.json', 'w')as f:
            json.dump(users, f, indent=4)
            f.close()