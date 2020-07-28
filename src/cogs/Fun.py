######### Bot V0.4 created by Kiran Wallace #########
### NOTE: This is not the main module. Please run main.py
# This is an extension of main.py
# This bot is for the intent to be used as a fun resource for Discord servers and is a work in progress
#
# In this section of code, you will find the following:
### Commands:
# .roll, .statgen, .youtube
### Functions:
# rollSingleDice, setup
################################################################################################################

import discord, random, os, math, requests, urllib
from bs4 import BeautifulSoup as bs
from main import has_channel_perms, ConsoleMessage, add_usage, PATH
from PIL import Image, ImageFont, ImageDraw
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

    @commands.command()
    async def statgen(self,ctx,*,name=None):#,*,pref=None):
        pref = None
        stattypes = ['STR','DEX','CON','INT','WIS','CHA']
        if 'Stats:' in name:
            tmp = name.split('Stats:')
            tmp = tmp[1].split()

            for item in pref:
                for stat in stattypes:
                    if item.lower().startswith(stat):
                        if pref == None:
                            pref = []
                        pref.append(stat)
        #randomises alignment
        morals = ['Good','Neutral','Evil']
        method = ['Lawful','Neutral','Chaotic']
        alignment =  random.choice(method) + ' ' + random.choice(morals)

        #custom name for neutral neutral random choice
        if alignment == 'Neutral Neutral':
            alignment = 'True Neutral'

        #loads background image and crops to size
        img = Image.open(f'{PATH}\\resources\\images\\stained.png')
        img = img.crop((0,0,500,160))

        #loads stat separator made in paint.net
        separator = Image.open(f'{PATH}\\resources\\images\\statseps.png')

        #defines the different fonts that are being used
        title   = ImageFont.truetype(f'{PATH}\\resources\\fonts\\MrsEavesSmallCaps.ttf',34)
        italic  = ImageFont.truetype(f'{PATH}\\resources\\fonts\\ScalaSans Italic.ttf',16)
        regular = ImageFont.truetype(f'{PATH}\\resources\\fonts\\ScalaSans Regular.ttf',17)

        #obtains the height of the title text
        h = title.getsize(ctx.author.name)[1]

        #draws the background
        draw = ImageDraw.Draw(img)

        #obtains the most recently modified rank of the user
        latest_rank = str(ctx.author.roles[-1]).title()
        if latest_rank == '@Everyone':
            latest_rank = 'Player'

        #draws the name of the user to the background along with their rank and randomly chosen alignment underneith
        if name == None and ctx.author.nick == None:
            name = ctx.author.name
        elif name == None and ctx.author.nick != None:
            name = ctx.author.nick
        name = name.title()
        draw.text((20,20),name,font=title,fill=(88, 23, 13))
        draw.text((20,h+25),f'{latest_rank}, {alignment}',font=italic,fill=(0,0,0))

        #increases the height and adds the separator to the background
        h += italic.getsize('Player')[1] + 25
        img.paste(separator,(20,h+5))
        h += 10

        #stat generation with 4 dice rolls for each block (take the best 3)
        stats = []
        for i in range(6):
            rolls = [0,0,0]
            for k in range(4):
                rand = random.randint(1,6)
                if k < 3:
                    rolls[k] = rand
                else:
                    #sorts in ascending order so the lowest can be replaced if needed
                    rolls.sort()
                    if rolls[0] < rand:
                        rolls[0] = rand
            stats.append(sum(rolls))

        #draws the names of the stat types to the background using a for loop
        count = 0
        if pref != None:
            #try:
            tmpstats = stats
            stats.sort()
            stats = stats[::-1]
            pref = pref.split()
            preforder = [7,7,7,7,7,7]
            pref = [x.upper() for x in pref]
            for p in pref:
                print(p)
                for s in stattypes:
                    if s == p:
                        preforder[count] = stattypes.index(s)
                        count += 1
                        #preforder.append(stattypes.index(s))
            print(stats)
            counter = 0
            tmp = [0,0,0,0,0,0]
            tmp2 = []
            j = 0
            for i in preforder:
                if i < 6:
                    tmp[counter] = stats[i]
                else:
                    tmp2.append(stats[j])
                j += 1
            if len(tmp2) > 0:
                random.shuffle(tmp2)
                j = 0
                for i in range(len(tmp)):
                    if tmp[i] == 0:
                        tmp[i] = tmp2[j]
                        j += 1

            print(preforder)
            #stats = [x for y, x in sorted(zip(preforder, stats))]
            stats = tmp
            print(stats)
            #except:
            #    stats = tmpstats


        x = 40
        for stat in stattypes:
            draw.text((x,h+10),stat,font=regular,fill=(0,0,0))
            x += 75

        #increases the height
        h += 10 + regular.getsize('STR')[1]

        #calculates the stat bonus for each slot
        bonus = []
        print(stats)
        for stat in stats:
            string = ''
            if stat > 9:
                string = '+'
            string = string + str(math.floor((stat-10)/2))
            bonus.append(string)

        #draws the stat bonus underneith each stat
        x = 35
        for i in range(6):
            dx = 0
            if stats[i] < 10:
                dx = 5
            draw.text((x+dx,h+5),f'{stats[i]} ({bonus[i]})',font=regular,fill=(0,0,0))
            x += 75

        #increases the height value and adds another separator under the new stats
        h += regular.getsize('10')[1]
        img.paste(separator,(20,h+20))

        #the image is temp saved in the \tmp folder, sent to discord and then immediatelly deleted
        img.save(f'{PATH}\\resources\\images\\tmp\\stats.png')
        await ctx.send(file=discord.File(f'{PATH}\\resources\\images\\tmp\\stats.png'))
        os.remove(f'{PATH}\\resources\\images\\tmp\\stats.png')

    @commands.command(aliases=['yt'],description='Allows for users to quickly search something on youtube. The bot will retrieve the first result of the search')
    async def youtube(self,ctx,*,query):
        ConsoleMessage(f'{ctx.author} has requested for the youtube search: "{query}"')
        found = False
        for i in range(20):
            if found:
                break
            base="https://www.youtube.com/results?search_query="
            query = query.replace(' ','+')
            #query = urllib.parse.quote(query)
            r = requests.get(base+query)
            page=r.text
            soup=bs(page,'html.parser')

            vids = soup.findAll('a',attrs={'class':'yt-uix-tile-link'})

            for v in vids:
                if str(v['href']).startswith('/watch?v='):
                    result = 'https://www.youtube.com' + v['href']
                    found = True
                    ConsoleMessage(f'Requested video for {ctx.author} found: "{result}" in {i+1} attempts')
                    await ctx.send(result)
                    break
        if not(found):
            print('failed to find')
            await ctx.send(f'Sorry {ctx.author.mention}, but I was not able to find anything :frowning:')

    @youtube.error
    async def youtube_error(self,ctx,error):
        await ctx.send(f'Sorry {ctx.author.mention}, but I was not able to find anything :frowning:')


#adds extension to client when called
def setup(client):
    client.add_cog(Fun(client))
