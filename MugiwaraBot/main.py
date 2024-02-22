import discord
import os
import sys
import asyncio
import time
import json
import dhooks
import constants

from discord.ext import tasks, commands
from discord.utils import get

from string import ascii_uppercase as UPPERCASE_LETTERS
from quizfolder.quizgame import QuizGame
from quizfolder.question import Question
from quizfolder.visuals import optionsVisual, resultsVisual

from cogs.music_cog import music_cog
# from cogs.translate_cog import translate_cog
from cogs.gpt_cog import gpt_cog
# from cogs.help_cog import help_cog
from cogs.poll_cog import Poll

# командный префикс и подключение всех зависимостей для бота
bot = commands.Bot(command_prefix=constants.PREFIX, intents=discord.Intents().all())
quiz = QuizGame()
hook = dhooks.Webhook(constants.CHANNEL_WEBHOOK_URL)

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
    # await bot.add_cog(translate_cog(bot))
    await bot.add_cog(gpt_cog(bot))
    await bot.add_cog(Poll(bot))

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
                        "CAPS": 0
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
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    if not quiz.isActiveGame():
        return
    
    channel = message.channel
    answer_range = list(UPPERCASE_LETTERS[:quiz.getNumOptions()].lower())
    input_answer = message.content.strip().lower()
    player = message.author

    # Process answers
    if input_answer in answer_range:
        # Player has no joined the game registration
        if not quiz.checkPlayer(player):
            await channel.send(f"{player}, you have not joined the game yet! Type `!join` to join if registration is still open")
        elif time.time() - quiz.getQuestionStart() > quiz.getQuestionTimer():
            await channel.send(f"Sorry {player}, your answer is not within the response window! :clock10:")
        else:
            quiz.updateAnswerLog(player, input_answer)
        
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=discord.Embed(
            title="Ошибка поиска команды",
            description="*Такой команды не существует, напищите !help для просмотра комманд*",
            timestamp=ctx.message.created_at,
            color=discord.Color.from_rgb(128, 255, 0)
        ))

@bot.command(help="Give a warn to user")
@commands.has_permissions(manage_channels=True)
async def warn(ctx, member: discord.Member, reason: str):
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
async def error(ctx, error):
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

@bot.command(help="Remove a warn from user")
@commands.has_permissions(manage_channels=True)
async def unwarn(ctx, member: discord.Member):
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
async def error(ctx, error):
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

@bot.command(help="Remove all warns from user")
@commands.has_permissions(administrator=True)
async def clear_warns(ctx, member: discord.Member):
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
async def error(ctx, error):
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

@bot.command(help="Check to see if you have the role to host quizes")
async def checkhost(ctx):
    host_role = discord.utils.find(lambda r: r.name == constants.HOST_ROLE, ctx.message.guild.roles)
    if host_role in ctx.message.author.roles:
        await ctx.send("You have the appropriate host role!")
    else:
        await ctx.send("You do not have the appropriate host role.")
    
@bot.command(help="Check to see if a quiz is currently active")
async def checkgame(ctx):
    await ctx.send("A game is **active!**" if quiz.isActiveGame() else "No game is active!")

@bot.command(help="Check to see what players attend a quiz now")
async def checkplayers(ctx):
    if not quiz.isActiveGame():
        await ctx.send("There is no active game")
    else:
        await ctx.send(f"Players playing right now: {', '.join(map(str, quiz.getPlayers().keys()))}")

# Check the timer for how much time is left in a question
@bot.command(help="Check the timer for how much time is left to answer a question")
async def t(ctx):
    if not quiz.isActiveGame():
        await ctx.send("There is no active game")
        return
    cur_time = time.time()
    start, timer_length = quiz.getQuestionStart(), quiz.getQuestionTimer()
    if cur_time - start < timer_length:
        await ctx.send(f'**{round(timer_length - (cur_time - start), 1)} seconds left!** :clock10:')
    else:
        await ctx.send('**Time is up!** :alarm_clock:')

@bot.command(help="Join the current quiz")
async def join(ctx):
    if not quiz.isActiveGame():
        await ctx.send("There is no active game to join")
    elif not quiz.isActiveRegistration():
        await ctx.send("Sorry but registration isn't active/has ended!")
    elif quiz.addPlayer(ctx.message.author):
        await ctx.send("Join was successful! Happy playing")
    else:
        await ctx.send("You've already joined!")

# Host-specific functions for hosting a quiz game

# Helper function to create Question objects that are then added to QuizGame
async def getQuestionInputs(ctx, num_questions) -> None:
    num_options = quiz.getNumOptions()
    await ctx.send(f'Now, enter **{num_questions} questions** each with **{num_options} options**, one at a time.')
    option_prompt = "/".join([f"<option {l}>" for l in UPPERCASE_LETTERS[:num_options]])
    await ctx.send(f'Types questions in this format: `<question>/{option_prompt}/<correct letter answer choice>`')

    for question_num in range(1, num_questions + 1):
        await ctx.send(f'You are now entering **Question {question_num}**')
        while True:
            question_input = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
            try:
                question = Question(question_input, num_options)
                quiz.addQuestion(question)
                await ctx.send(f'Question {question_num} successfully entered!')
                break
            except:
                await ctx.send("That's an invalid question. Try again! Make sure to follow the syntax and the answer is an appropriate letter choice.")

# Enter quiz questions in a private channel to prevent players from seeing the game and question set up
@bot.command(help="Set up a quiz. Bot will prompt you for all the necessary inputs")
@commands.has_role(constants.HOST_ROLE)
async def startgame(ctx):
    if quiz.isActiveGame():
        await ctx.send("Hold on. There is currently a game occuring right now or someone else is setting up a game. Wait until it is finished.")
        return
    quiz.setActiveGame()
    await ctx.send('**Registration started!** Try to enter all the information correctly. If you mess something up, you have to **follow through** and cancel all at the end and restart.')

    while True:
        await ctx.send('Now please enter how many questions you want.')
        num_questions = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
        await ctx.send('Enter how many options you want for each question.')
        num_options = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
        await ctx.send('Enter how many seconds you want the timer for each question to be')
        question_timer = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
        try:
            num_questions = int(num_questions)
            num_options = int(num_options)
            question_timer = float(question_timer)
            if num_questions < 1 or num_options < constants.MIN_OPTIONS or num_options > constants.MAX_OPTIONS or question_timer < 0:
                raise ValueError()
            quiz.setNumQuestions(num_questions)
            quiz.setNumOptions(num_options)
            quiz.setQuestionTimer(question_timer)
            break
        except:
            await ctx.send('Something went wrong. Number of questions and question timer must be greater than 0 and number of options be between 2 and 26. Make sure to type in an integer for each input and nothing else. Try again.')

    await getQuestionInputs(ctx, num_questions)
    await ctx.send('Questions entered. Type `cancel` at this point if you wish to cancel. Otherwise, type anything that is not `cancel` to finish game registration.')
    cancel_flag = (await bot.wait_for("message", check = lambda m: m.author == ctx.author)).content.strip().lower()
    if cancel_flag == "cancel":
        quiz.resetQuizGame()
        await ctx.send('Quiz set up cancelled! Do **!startgame** to try again.')
    else:
        await ctx.send(f"Quiz has been all set up! Thank you {ctx.message.author.name}")

@bot.command(help="Begin registration for a quiz")
@commands.has_role(constants.HOST_ROLE)
async def startreg(ctx):
    if not quiz.isActiveGame():
        await ctx.send("Game not active to start registration for.")
        return
    quiz.setActiveRegistration()
    await ctx.send('Game Registration Started! Type **!join** to join the game.')

@bot.command(help="End registration for a quiz, preventing further players from joining")
@commands.has_role(constants.HOST_ROLE)
async def endreg(ctx):
    if not quiz.isActiveRegistration():
        await ctx.send("No active registration to end.")
        return
    quiz.endActiveRegistration()
    await ctx.send('Game Registration Ended!')

@bot.command(help="Display the next question of a quiz")
@commands.has_role(constants.HOST_ROLE)
async def question(ctx):
    # Lots of error handling for bad timing of using this command
    if not quiz.isActiveGame():
        await ctx.send("Can't show question if no game is active")
        return
    if quiz.getCurQuestionNum() != quiz.getCurResultNum():
        await ctx.send("You can't move on to next question until you display results of last question using `!result`")
    cur_question = quiz.getNextQuestion()
    if cur_question is None:
        await ctx.send("All the questions have been shown! Type `!endgame` to end the game")
        return
    # Send the question to webhook
    embed = dhooks.Embed(color = constants.QUESTION_EMBED_COLOR)
    embed.set_author(name = "Discord Quiz Question")
    embed.add_field(name = f"{quiz.getCurQuestionNum() + 1}. {cur_question.getQuestion()}", value = optionsVisual(quiz))
    hook.send(embed = embed)
    quiz.setQuestionStart()

@bot.command(help="Display the results of the most recent question")
@commands.has_role(constants.HOST_ROLE)
async def result(ctx):
    # Lots of error handling for bad timing of using this command
    if not quiz.isActiveGame():
        await ctx.send("Can't show results for a question if no game is active!")
        return
    if time.time() - quiz.getQuestionStart() < quiz.getQuestionTimer():
        await ctx.send("Question period has no ended!")
        return
    if quiz.getCurQuestionNum() != quiz.getCurResultNum() + 1:
        await ctx.send("You must display a question before showing its answer")
        return
    results = quiz.processResults()
    cur_question = quiz.getCurQuestion()
    if results is None:
        await ctx.send("All the answers have been shown! Type `!endgame` to end the game")
        return
    # Send the results to webhook
    embed = dhooks.Embed(color = constants.ANSWER_EMBED_COLOR)
    embed.set_author(name = "Discord Quiz Answer")
    embed.add_field(name = f"{quiz.getCurQuestionNum() + 1}. {cur_question.getQuestion()}", value = optionsVisual(quiz))
    embed.add_field(name = "Votes", value = resultsVisual(quiz, results))
    hook.send(embed = embed)

@bot.command(help="End the current quiz and display the leaderboard")
@commands.has_role(constants.HOST_ROLE)
async def endgame(ctx):
    if not quiz.isActiveGame():
        await ctx.send("Can't end a game that is not active")
        return
    # Make sure that the result for every question that has been asked has been shown so far
    if quiz.getCurQuestionNum() != quiz.getCurResultNum():
        await ctx.send("Show the results of this question before ending the game.")
        return
    # Displays a visualization of the results of a game
    # Shows a player and how many questions they answered correctly, sorted by those who answered the most correctly
    leaderboard = dict(sorted(quiz.getPlayers().items(), key = lambda item: item[1], reverse = True))
    embed = dhooks.Embed(color = constants.LEADERBOARD_EMBED_COLOR)
    embed.set_author(name = "Discord Quiz Game Results")
    embed.add_field(name = "Players", value = "\n".join(map(lambda p: f"{':trophy:' if leaderboard[p] == max(leaderboard.values()) else ''} {p}", leaderboard.keys())))
    embed.add_field(name = "Points", value = "\n".join(map(str, leaderboard.values())))
    hook.send(embed = embed)
    quiz.resetQuizGame()

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