######### Bot V0.2.1 created by Kiran Wallace #########
### NOTE: This is not the main module. Please run main.py
# This is an extension of main.py
# This bot is for the intent to be used as a fun resource for Discord servers and is a work in progress
#
# In this section of code, you will find the following:
### Commands:
# .roll
### Functions:
# rollSingleDice, setup
################################################################################################################

import discord
import random
from main import has_channel_perms, ConsoleMessage, add_usage
from time import sleep
from discord.ext import commands

class Fun(commands.Cog):
    #initialises object with client from main
    def __init__(self, client):
        self.client = client

    #function called in .roll if a single dice is rolled (.roll dx or .roll 1dx)
    def rollSingleDice(self,ctx,dice_val):
        #checks that a valid option (2,4,8,10,12,20,100) has been entered
        if (dice_val == 2) or (dice_val == 4) or (dice_val == 6) or (dice_val == 8) or (dice_val == 10) or (dice_val == 12) or (dice_val == 20) or (dice_val == 100):
            #if dice is two sided, it is a coin
            if dice_val == 2:
                #adds to coin stats in "usage.json"
                add_usage("times coins used")
                add_usage("total coins used")
                #will randomise outcome and produce either heads or tails
                if (random.randint(0,1) == 0):
                    out = 'heads'
                else:
                    out = 'tails'
                #message that will be sent to the server
                out = f'{ctx.author.mention} flipped a coin and got `{out}`'
            #if it is not 2 sided
            else:
                #will add to dice stats in "usage.json"
                add_usage("times dice used")
                add_usage("total dice used")
                #will produce a random number between 1 to the maximum value on the dice
                randval = random.randint(1,dice_val)
                #custom message for rolling a 1 on a 20 sided dice
                if randval == 1 and dice_val == 20:
                    out = f'{ctx.author.mention} rolled a `natural 1` on a `d20`...'
                #custom message for rolling a 20 on a 20 sided dice
                elif randval == 20 and dice_val == 20:
                    out = f'{ctx.author.mention} rolled a `natural 20` on a `d20`!'
                #if not 1 or 20 on a 20 sided dice, will produce the default message
                else:
                    out = f'{ctx.author.mention} rolled `{randval}` on a `d{dice_val}`'
        #if it is not a 2,4,6,8,10,12,20 or 100 sided dice; will inform user of invalid input
        else:
            out = f'Hmmm...I don\'t think that\'s a real dice {ctx.author.mention}.\nTry one of these dice: `.d2, .d4, .d6, .d8, .d10, .d12, .d20, .d100`'
        return out

########################################################################################################
#############################################   COMMANDS   #############################################
#This section is for command calling, all functions with the decorator @client.command() will be called
#if typed into discord with the prefix '.'

    #command for rolling dice. Can roll up to 30 dice of sides 2,4,6,8,10,12,20 and 100
    #checks that it can be used in the requested channel by accessing "../config/command locations.json"
    @commands.command()
    @commands.check(has_channel_perms)
    async def roll(self, ctx, dice):
        #if the user does not specify the number of dice to use, will only use one
        if dice.startswith('d'):
            out = self.rollSingleDice(ctx,int(dice[1:]))

        #otherwise will split the input into a list based on 'd', so 2d6 will become [2,6]
        else:
            vals = dice.split('d')
            out = ''

            #if there are only 2 items in the list (prevents bad input)
            if len(vals) == 2:
                #the first value is taken as the number of dice to roll
                number = int(vals[0])
                #the second value is taken as the number of sides to the dice
                dice_val = int(vals[1])

                #if the number of dice is one, roll one dice
                if number == 1:
                    out = self.rollSingleDice(ctx,int(vals[1]))

                #if the user would like to roll multiple dice (max 30)
                elif number > 1 and number < 31:
                    #checks that a valid option (2,4,8,10,12,20,100) has been entered for the sides of the dice
                    if (dice_val == 2) or (dice_val == 4) or (dice_val == 6) or (dice_val == 8) or (dice_val == 10) or (dice_val == 12) or (dice_val == 20) or (dice_val == 100):
                        #if it is 2 sided, it is considered as a coin
                        if (dice_val == 2):
                            #adds to coin stats in "usage.json"
                            add_usage("times coins used")
                            add_usage("total coins used",number)

                            #counter for number of each output
                            heads = 0
                            tails = 0
                            #output message initialised
                            out = f'{ctx.author.mention} flipped {number} coins and got:\n'

                            #will randomise the output of either "heads" or "tails" and add to the counters for number of times specified
                            for i in range(number):
                                if random.randint(0,1) == 0:
                                    out += '`heads`'
                                    heads += 1
                                else:
                                    out += '`tails`'
                                    tails += 1
                                if i != number-1:
                                    out += ', '
                            #has a final counter for the total of each output
                            out += f'\n{heads} heads and {tails} tails'

                        #if it is not a coin
                        else:
                            #adds to the dice stats in "usage.json"
                            add_usage("times dice used")
                            add_usage("total dice used",number)
                            #initialises the total values rolled counter
                            total = 0
                            #initialises the output message
                            out = f'{ctx.author.mention} rolled {number}d{dice_val}\'s and got:\n'

                            #generated a random dice roll, adds the roll to the output and to the total
                            for i in range(number):
                                add = random.randint(1,dice_val)

                                #if the randomly rolled value is either a 20 or 1 on a d20, add data to "usage.json"
                                if add == 20 and dice_val == 20:
                                    add_usage("natural 20's")
                                elif add == 1 and dice_val == 20:
                                    add_usage("natural 1's")

                                total += add
                                out += f'`{add}`'
                                if i != number - 1:
                                    out += ', '
                            #displays the combined total of all of the rolls
                            out += f'\ntotal `{total}`'
                    #if an invalid dice value is entered, will inform the user
                    else:
                        out = f'Sorry {ctx.author.mention}, I don\'t think that\'s a real dice...'
                #if the user attempts to roll less than 1 dice or more than 30, will inform the user that it is an invalid input
                else:
                    out = f'Hmmm...I don\'t think I can possibly roll {number} dice. Sorry about that :sweat_smile:'

        #sends output message to server
        await ctx.send(out)

        ###SPECIAL CASES###
        #if the user rolls a 1 on a d20 or a 20 on a d20 for the single rolls, send additional message delayed by 1 second
        if out.endswith('`d20`...'):
            add_usage("natural 1's")
            sleep(1)
            await ctx.send('*...ouch*')
        elif out.endswith('`d20`!'):
            add_usage("natural 20's")
            sleep(1)
            await ctx.send(':partying_face:')

    #catches errors associated with .roll
    @roll.error
    async def roll_error(self, ctx, error):
        #will inform the console that the error is due to being used in a non-permitted channel (specified by ../config/command locations.json)
        if isinstance(error, commands.CheckFailure):
            ConsoleMessage(f'{ctx.author} attempted to use .roll in #{ctx.channel}')
        #otherwise, assume invalid input
        else:
            await ctx.send(f'Sorry {ctx.author.mention} but I don\'t think I understand you.\nTry typing `.roll` followed by the number of dice you would like to roll (max 30), then the dice you would like to use!\nE.g: if I wanted to roll 5, 6-sided dice, I would type `.roll 5d6`')

#adds extension to client when called
def setup(client):
    client.add_cog(Fun(client))
