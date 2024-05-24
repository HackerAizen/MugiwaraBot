import discord
from discord.ext import commands
import asyncio
import dhooks
import constants
import time

from string import ascii_uppercase as UPPERCASE_LETTERS
from quizfolder.quizgame import QuizGame
from quizfolder.question import Question
from quizfolder.visuals import optionsVisual, resultsVisual

class quiz_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.quiz = QuizGame()
        self.hook = dhooks.Webhook(constants.CHANNEL_WEBHOOK_URL)
    

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        # await self.bot.process_commands(message)

        if not self.quiz.isActiveGame():
            return
        
        channel = message.channel
        answer_range = list(UPPERCASE_LETTERS[:self.quiz.getNumOptions()].lower())
        input_answer = message.content.strip().lower()
        player = message.author

        # Process answers
        if input_answer in answer_range:
            # Player has no joined the game registration
            if not self.quiz.checkPlayer(player):
                await channel.send(f"{player}, you have not joined the game yet! Type `!join` to join if registration is still open")
            elif time.time() - self.quiz.getQuestionStart() > self.quiz.getQuestionTimer():
                await channel.send(f"Sorry {player}, your answer is not within the response window! :clock10:")
            else:
                self.quiz.updateAnswerLog(player, input_answer)

    @commands.command(help="Check to see if you have the role to host quizes")
    async def checkhost(self, ctx):
        host_role = discord.utils.find(lambda r: r.name == constants.HOST_ROLE, ctx.message.guild.roles)
        if host_role in ctx.message.author.roles:
            await ctx.send("You have the appropriate host role!")
        else:
            await ctx.send("You do not have the appropriate host role.")
        
    @commands.command(help="Check to see if a quiz is currently active")
    async def checkgame(self, ctx):
        await ctx.send("A game is **active!**" if self.quiz.isActiveGame() else "No game is active!")

    @commands.command(help="Check to see what players attend a quiz now")
    async def checkplayers(self, ctx):
        if not self.quiz.isActiveGame():
            await ctx.send("There is no active game")
        else:
            await ctx.send(f"Players playing right now: {', '.join(map(str, self.quiz.getPlayers().keys()))}")

    # Check the timer for how much time is left in a question
    @commands.command(help="Check the timer for how much time is left to answer a question")
    async def t(self, ctx):
        if not self.quiz.isActiveGame():
            await ctx.send("There is no active game")
            return
        cur_time = time.time()
        start, timer_length = self.quiz.getQuestionStart(), self.quiz.getQuestionTimer()
        if cur_time - start < timer_length:
            await ctx.send(f'**{round(timer_length - (cur_time - start), 1)} seconds left!** :clock10:')
        else:
            await ctx.send('**Time is up!** :alarm_clock:')

    @commands.command(help="Join the current quiz")
    async def join(self, ctx):
        if not self.quiz.isActiveGame():
            await ctx.send("There is no active game to join")
        elif not self.quiz.isActiveRegistration():
            await ctx.send("Sorry but registration isn't active/has ended!")
        elif self.quiz.addPlayer(ctx.message.author):
            await ctx.send("Join was successful! Happy playing")
        else:
            await ctx.send("You've already joined!")

    # Host-specific functions for hosting a quiz game

    # Helper function to create Question objects that are then added to QuizGame
    async def getQuestionInputs(self, ctx, num_questions) -> None:
        num_options = self.quiz.getNumOptions()
        await ctx.send(f'Now, enter **{num_questions} questions** each with **{num_options} options**, one at a time.')
        option_prompt = "/".join([f"<option {l}>" for l in UPPERCASE_LETTERS[:num_options]])
        await ctx.send(f'Types questions in this format: `<question>/{option_prompt}/<correct letter answer choice>`')

        for question_num in range(1, num_questions + 1):
            await ctx.send(f'You are now entering **Question {question_num}**')
            while True:
                question_input = (await self.bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
                try:
                    question = Question(question_input, num_options)
                    self.quiz.addQuestion(question)
                    await ctx.send(f'Question {question_num} successfully entered!')
                    break
                except:
                    await ctx.send("That's an invalid question. Try again! Make sure to follow the syntax and the answer is an appropriate letter choice.")

    # Enter quiz questions in a private channel to prevent players from seeing the game and question set up
    @commands.command(help="Set up a quiz. Bot will prompt you for all the necessary inputs")
    @commands.has_role(constants.HOST_ROLE)
    async def startgame(self, ctx):
        if self.quiz.isActiveGame():
            await ctx.send("Hold on. There is currently a game occuring right now or someone else is setting up a game. Wait until it is finished.")
            return
        self.quiz.setActiveGame()
        await ctx.send('**Registration started!** Try to enter all the information correctly. If you mess something up, you have to **follow through** and cancel all at the end and restart.')

        while True:
            await ctx.send('Now please enter how many questions you want.')
            num_questions = (await self.bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
            await ctx.send('Enter how many options you want for each question.')
            num_options = (await self.bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
            await ctx.send('Enter how many seconds you want the timer for each question to be')
            question_timer = (await self.bot.wait_for("message", check = lambda m: m.author == ctx.author)).content
            try:
                num_questions = int(num_questions)
                num_options = int(num_options)
                question_timer = float(question_timer)
                if num_questions < 1 or num_options < constants.MIN_OPTIONS or num_options > constants.MAX_OPTIONS or question_timer < 0:
                    raise ValueError()
                self.quiz.setNumQuestions(num_questions)
                self.quiz.setNumOptions(num_options)
                self.quiz.setQuestionTimer(question_timer)
                break
            except:
                await ctx.send('Something went wrong. Number of questions and question timer must be greater than 0 and number of options be between 2 and 26. Make sure to type in an integer for each input and nothing else. Try again.')

        print("OK")
        await self.getQuestionInputs(ctx, num_questions)
        print("OK")
        await ctx.send('Questions entered. Type `cancel` at this point if you wish to cancel. Otherwise, type anything that is not `cancel` to finish game registration.')
        cancel_flag = (await self.bot.wait_for("message", check = lambda m: m.author == ctx.author)).content.strip().lower()
        if cancel_flag == "cancel":
            self.quiz.resetQuizGame()
            await ctx.send('Quiz set up cancelled! Do **!startgame** to try again.')
        else:
            await ctx.send(f"Quiz has been all set up! Thank you {ctx.message.author.name}")

    @commands.command(help="Begin registration for a quiz")
    @commands.has_role(constants.HOST_ROLE)
    async def startreg(self, ctx):
        if not self.quiz.isActiveGame():
            await ctx.send("Game not active to start registration for.")
            return
        self.quiz.setActiveRegistration()
        await ctx.send('Game Registration Started! Type **!join** to join the game.')

    @commands.command(help="End registration for a quiz, preventing further players from joining")
    @commands.has_role(constants.HOST_ROLE)
    async def endreg(self, ctx):
        if not self.quiz.isActiveRegistration():
            await ctx.send("No active registration to end.")
            return
        self.quiz.endActiveRegistration()
        await ctx.send('Game Registration Ended!')

    @commands.command(help="Display the next question of a quiz")
    @commands.has_role(constants.HOST_ROLE)
    async def question(self, ctx):
        # Lots of error handling for bad timing of using this command
        if not self.quiz.isActiveGame():
            await ctx.send("Can't show question if no game is active")
            return
        if self.quiz.getCurQuestionNum() != self.quiz.getCurResultNum():
            await ctx.send("You can't move on to next question until you display results of last question using `!result`")
        cur_question = self.quiz.getNextQuestion()
        if cur_question is None:
            await ctx.send("All the questions have been shown! Type `!endgame` to end the game")
            return
        # Send the question to webhook
        embed = dhooks.Embed(color = constants.QUESTION_EMBED_COLOR)
        embed.set_author(name = "Discord Quiz Question")
        embed.add_field(name = f"{self.quiz.getCurQuestionNum() + 1}. {cur_question.getQuestion()}", value = optionsVisual(self.quiz))
        self.hook.send(embed = embed)
        self.quiz.setQuestionStart()

    @commands.command(help="Display the results of the most recent question")
    @commands.has_role(constants.HOST_ROLE)
    async def result(self, ctx):
        # Lots of error handling for bad timing of using this command
        if not self.quiz.isActiveGame():
            await ctx.send("Can't show results for a question if no game is active!")
            return
        if time.time() - self.quiz.getQuestionStart() < self.quiz.getQuestionTimer():
            await ctx.send("Question period has no ended!")
            return
        if self.quiz.getCurQuestionNum() != self.quiz.getCurResultNum() + 1:
            await ctx.send("You must display a question before showing its answer")
            return
        results = self.quiz.processResults()
        cur_question = self.quiz.getCurQuestion()
        if results is None:
            await ctx.send("All the answers have been shown! Type `!endgame` to end the game")
            return
        # Send the results to webhook
        embed = dhooks.Embed(color = constants.ANSWER_EMBED_COLOR)
        embed.set_author(name = "Discord Quiz Answer")
        embed.add_field(name = f"{self.quiz.getCurQuestionNum() + 1}. {cur_question.getQuestion()}", value = optionsVisual(self.quiz))
        embed.add_field(name = "Votes", value = resultsVisual(self.quiz, results))
        self.hook.send(embed = embed)

    @commands.command(help="End the current quiz and display the leaderboard")
    @commands.has_role(constants.HOST_ROLE)
    async def endgame(self, ctx):
        if not self.quiz.isActiveGame():
            await ctx.send("Can't end a game that is not active")
            return
        # Make sure that the result for every question that has been asked has been shown so far
        if self.quiz.getCurQuestionNum() != self.quiz.getCurResultNum():
            await ctx.send("Show the results of this question before ending the game.")
            return
        # Displays a visualization of the results of a game
        # Shows a player and how many questions they answered correctly, sorted by those who answered the most correctly
        leaderboard = dict(sorted(self.quiz.getPlayers().items(), key = lambda item: item[1], reverse = True))
        embed = dhooks.Embed(color = constants.LEADERBOARD_EMBED_COLOR)
        embed.set_author(name = "Discord Quiz Game Results")
        embed.add_field(name = "Players", value = "\n".join(map(lambda p: f"{':trophy:' if leaderboard[p] == max(leaderboard.values()) else ''} {p}", leaderboard.keys())))
        embed.add_field(name = "Points", value = "\n".join(map(str, leaderboard.values())))
        self.hook.send(embed = embed)
        self.quiz.resetQuizGame()

