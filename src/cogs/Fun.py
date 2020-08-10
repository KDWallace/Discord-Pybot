######### Bot V0.4 created by Kiran Wallace #########
### NOTE: This is not the main module. Please run main.py
# This is an extension of main.py
# This bot is for the intent to be used as a fun resource for Discord servers and is a work in progress
#
# In this section of code, you will find the following:
### Commands:
# .roll, .statgen, .youtube
### Functions:
# rollSingleDice, fitbox, setup
################################################################################################################

import discord, random, os, math, requests, urllib, asyncio, json
from bs4 import BeautifulSoup as bs
from main import has_channel_perms, ConsoleMessage, add_usage, PATH
from PIL import Image, ImageFont, ImageDraw
from time import sleep
from datetime import datetime
from discord.ext import commands

class Fun(commands.Cog):
    #initialises object with client from main
    def __init__(self, client):
        self.client = client
        self.channel = None
        self.meabhuser = None
        self.timestamp = ''
        self.BOXFIT = 340
        self.arial = ImageFont.truetype(f'{PATH}\\resources\\fonts\\arial.ttf',24)
        with open(f'{PATH}\\data\\tmpdata\\timestamps.json','r') as f:
            self.timestamp = json.load(f)
            self.meabh = self.timestamp['Meabhs 16']
            self.timestamp = self.timestamp['16 personality']


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

    def fitbox(self,string):
        retlist = []
        size = self.arial.getsize(string)[0]
        i = 0
        line = ''
        if size > self.BOXFIT:
            size = 0
            while size < self.BOXFIT and i < len(string):
                line = line + string[i]
                size = self.arial.getsize(line)[0]
                i += 1
                if size >= self.BOXFIT:
                    while not(line.endswith(' ')):
                        line = line[:-1]
                    string = string[len(line):]
                    retlist.append(line)
                    if len(string) > 0:
                        if self.arial.getsize(string)[0] > self.BOXFIT:
                            size = 0
                            line = ''
                            i = 0
                        else:
                            retlist.append(string)
                            break
                    else:
                        break
            return retlist
        else:
            return [string]

######################################################################################################
#############################################   EVENTS   #############################################
#This section is for event checking and will call the below functions if the event in question occures
    async def person_16(self):
        while True:
            await asyncio.sleep(600)
            with open(f'{PATH}\\data\\tmpdata\\timestamps.json','r') as f:
                tmp = json.load(f)['16 personality']
            if tmp != datetime.today().strftime("%Y-%m-%d"):
                ConsoleMessage('Posted 16 personality MOTD on channel')
                self.timestamp = {'16 personality':datetime.today().strftime("%Y-%m-%d"),'Meabhs 16':self.meabh}
                with open(f'{PATH}\\data\\tmpdata\\timestamps.json','w') as f:
                    json.dump(self.timestamp,f,indent=4)

                try:
                    #moose, only1connor, spork, jallerston
                    userlist   = [474037926641008640,379373007896051712,581781390471725056,459404973583761429]
                    userimages = []
                    i = 1
                    for id in userlist:
                        user = self.client.get_user(id)
                        #urluser = f'https://cdn.discordapp.com/avatars/{id}/{user.avatar}.png?size=1024'
                        #userimages.append(urluser)
                        r = requests.get(f'https://cdn.discordapp.com/avatars/{id}/{user.avatar}.png?size=64')
                        if str(r) != '<Response [404]>':
                            with open(f'{PATH}\\resources\\images\\tmp\\avatar{i}.png','wb') as f:
                                f.write(r.content)
                            await asyncio.sleep(1)
                        i += 1
                except:
                    pass

                if self.channel == None:
                    self.channel = await self.client.fetch_channel(738807913971318805)

                url = 'https://www.16personalities.com/'
                perstypes = ['intp','infj','infp','istj']
                locs = [(203,166),(612,166),(203,458),(612,458)]

                img  = Image.open(f'{PATH}\\resources\\images\\personalities.png')
                draw = ImageDraw.Draw(img)

                k = 0
                for pers in perstypes:
                    src = requests.get(f'{url}{pers}-personality').text
                    soup = bs(src,'html.parser')
                    motd = soup.find('div',attrs={'class':'insight'})
                    motd = str(motd)[21:-6]
                    motd_lines = []
                    size = self.arial.getsize(motd)[0]
                    motd_lines = (self.fitbox(motd))
                    locframe = ((8,0),(412,0),(8,293),(412,293))

                    if os.path.isfile(f'{PATH}\\resources\\images\\tmp\\avatar{k+1}.png'):
                        avatar = Image.open(f'{PATH}\\resources\\images\\tmp\\avatar{k+1}.png')
                        frame = Image.open(f'{PATH}\\resources\\images\\persframe.png')
                        frame.convert('RGBA')

                        #avatar = avatar.crop((0,0,50,50))
                        #img.paste(avatar,(locs[k][0],locs[k][1]))
                        #mask = Image.new("L", avatar.size, 0)
                        #drawmask = ImageDraw.Draw(mask)
                        #drawmask.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)
                        #result = avatar.copy()
                        #result.putalpha(mask)
                        #result.convert('RGBA')
                        #result.save(f'{PATH}\\resources\\images\\tmp\\av{k+1}.png')
                        #await asyncio.sleep(1)
                        #newav = Image.open(f'{PATH}\\resources\\images\\tmp\\av{k+1}.png')
                        dx = 0
                        if k%2 != 0:
                            dx = 4

                        img.paste(frame,(locframe[k][0],locframe[k][1]))
                        img.paste(avatar,(locs[k][0]-32-dx,locs[k][1]-119))

                        draw.polygon([(locframe[k][0] + 195,locframe[k][1] + 110),(locframe[k][0] + 149,locframe[k][1] + 85),(locframe[k][0] + 149,locframe[k][1] + 110)],fill = (87,96,113))
                        draw.polygon([(locframe[k][0] + 194,locframe[k][1] + 110),(locframe[k][0] + 236,locframe[k][1] + 90),(locframe[k][0] + 236,locframe[k][1] + 110)],fill = (87,96,113))

                        os.remove(f'{PATH}\\resources\\images\\tmp\\avatar{k+1}.png')

                #        i += 1
                    j = 0
                    for line in motd_lines:
                        draw.text((locs[k][0]-(self.arial.getsize(line)[0]/2),locs[k][1] + ((self.arial.getsize('YE')[1]+3)*j)),line,font=self.arial,fill=(255,255,255))
                        j += 1
                    k += 1

                img.save(f'{PATH}\\resources\\images\\tmp\\tmppers.png')
                await self.channel.send(file=discord.File(f'{PATH}\\resources\\images\\tmp\\tmppers.png'))
                #await self.channel.send(f'Ignore this message, this is for testing purposes\n{urluser}')
                os.remove(f'{PATH}\\resources\\images\\tmp\\tmppers.png')

    async def meabhISFJ(self):
        while True:
            await asyncio.sleep(600)
            with open(f'{PATH}\\data\\tmpdata\\timestamps.json','r') as f:
                tmp = json.load(f)
            prev = tmp['16 personality']
            tmp = tmp['Meabhs 16']
            if tmp != datetime.today().strftime("%Y-%m-%d"):
                ConsoleMessage('Posted 16 personality MOTD to Meabh')
                self.timestamp = {'16 personality':prev,'Meabhs 16':datetime.today().strftime("%Y-%m-%d")}
                with open(f'{PATH}\\data\\tmpdata\\timestamps.json','w') as f:
                    json.dump(self.timestamp,f,indent=4)

                if self.meabhuser == None:
                    self.meabhuser = await self.client.fetch_user(185869510706855937)

                url = 'https://www.16personalities.com/isfj-personality'

                img  = Image.open(f'{PATH}\\resources\\images\\isfj.png')
                draw = ImageDraw.Draw(img)
                src = requests.get(url).text
                soup = bs(src,'html.parser')
                motd = soup.find('div',attrs={'class':'insight'})
                motd = str(motd)[21:-6]
                motd_lines = []
                size = self.arial.getsize(motd)[0]
                motd_lines = (self.fitbox(motd))
                j = 0
                for line in motd_lines:
                    draw.text((205-(self.arial.getsize(line)[0]/2),165 + ((self.arial.getsize('YE')[1]+3)*j)),line,font=self.arial,fill=(255,255,255))
                    j += 1

                img.save(f'{PATH}\\resources\\images\\tmp\\meabhmsg.png')
                try:
                    await self.meabhuser.send(file=discord.File(f'{PATH}\\resources\\images\\tmp\\meabhmsg.png'))
                except:
                    ConsoleMessage('MOTD failed to send to Meabh')
                #await self.channel.send(f'Ignore this message, this is for testing purposes\n{urluser}')
                os.remove(f'{PATH}\\resources\\images\\tmp\\meabhmsg.png')

########################################################################################################
#############################################   COMMANDS   #############################################
#This section is for command calling, all functions with the decorator @client.command() will be called
#if typed into discord with the prefix '.'

    #command for rolling dice. Can roll up to 30 dice of sides 2,4,6,8,10,12,20 and 100
    #checks that it can be used in the requested channel by accessing "../config/command locations.json"
    @commands.command(aliases=['r'])
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

    @commands.command(aliases=['rg'])
    async def rollgen(self,ctx,dice):
        img  = Image.open(f'{PATH}\\resources\\images\\dice.png')

        val = 0
        accepted_dice = ((4,6,8),(10,12,20))
        locs = (0,118,230,348)

        try:
            val = int(dice)
            x = 0
            y = 0
            if val in accepted_dice[0] or val in accepted_dice[1]:
                if val in accepted_dice[1]:
                    y = 108
                    group = accepted_dice[1]
                else:
                    group = accepted_dice[0]
                x = locs[group.index(val)]
                img = img.crop((x,y,locs[locs.index(x)+1],108+y))

                dsize = 0
                if val == 20:
                    dsize = 10

                roll = random.randint(1,val)
                dshadow = 0
                if roll == val or roll == 1:
                    dshadow = 4

                italic  = ImageFont.truetype(f'{PATH}\\resources\\fonts\\ScalaSans Italic.ttf',34-dsize)
                shadow  = ImageFont.truetype(f'{PATH}\\resources\\fonts\\ScalaSans Italic.ttf',40-dsize + dshadow)

                draw = ImageDraw.Draw(img)
                dx = 0
                dy = 0
                if val == group[1]:
                    dx = 1
                    dy = 6
                if val == 8 or val == 10:
                    dy = 8
                colour = (180,180,180)
                if roll == val:
                    colour = (255,255,255)
                elif roll == 1:
                    colour = (100,0,0)
                draw.text((img.size[0]/2 - dx - shadow.getsize(str(roll))[0]/2, img.size[1]/2 - dy - italic.getsize(str(roll))[1]/2),str(roll),font=italic,fill=(100,100,100))
                draw.text((img.size[0]/2 - dx - italic.getsize(str(roll))[0]/2, img.size[1]/2 - dy - italic.getsize(str(roll))[1]/2),str(roll),font=italic,fill=colour)


                #draw.text((0,0),str(roll),font=italic,fill=(0,0,0))

                img.save(f'{PATH}\\resources\\images\\tmp\\roll.png')
                await ctx.send(file=discord.File(f'{PATH}\\resources\\images\\tmp\\roll.png'))
                os.remove(f'{PATH}\\resources\\images\\tmp\\roll.png')
        except:
            pass

    @commands.command()
    async def statgen(self,ctx,*,name=None):#,*,pref=None):
        pref = None
        nameOrig = None
        rolltype = 4
        stattypes = ['STR','DEX','CON','INT','WIS','CHA']

        #sets up preference for stats if any
        if name != None and 'stats:' in name.lower():
            nameOrig = name
            tmp = name.lower().split('stats:')
            name = tmp[0]

            #data for stat order
            tmp = tmp[1].split()
            tmp = [x.upper()[:3] for x in tmp]

            for item in tmp:
                for stat in stattypes:
                    #creates an order of preference for stats generated
                    if item == stat:
                        #changes type from NoneType to list if no previous enteries have been submitted
                        if pref == None:
                            pref = [stat]

                        #if the stat has not been added yet to the preference list, add
                        elif stat not in pref:
                            pref.append(stat)

            #checks if all stats have been listed in pref. If not, will be added in random order
            if pref != None and len(pref) < 6:
                stattmp = [x for x in stattypes if x not in pref]
                random.shuffle(stattmp)
                for stat in stattmp:
                    pref.append(stat)

        if name != None and ('roll:' in name.lower() or (nameOrig != None and 'roll:' in nameOrig)):
            if nameOrig != None and 'roll' not in name.lower():
                tmp = nameOrig.lower().split('roll:')
            else:
                nameOrig = name
                tmp = name.lower().split('roll:')
                name = tmp[0]

            #data for roll type
            rolls = tmp[1]
            tmp = tmp[1].split()[0]
            try:
                rolltmp = int(tmp[0])
                if rolltmp >= 3:
                    rolltype = rolltmp
            except:

                if rolls.lower() == 'array' or rolls.lower() == 'std' or rolls.lower().startswith('standard'):
                    rolltype = 'array'

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
        try:
            latest_rank = str(ctx.author.roles[-1]).title()
        except:
            latest_rank = 'Player'
        if latest_rank == '@Everyone':
            latest_rank = 'Player'

        #draws the name of the user to the background along with their rank and randomly chosen alignment undernieth
        if name == '':
            name = None
        if name == None and hasattr(ctx.author,'nick') and ctx.author.nick == None:
            name = ctx.author.name
        elif name == None and hasattr(ctx.author,'nick') and ctx.author.nick != None:
            name = ctx.author.nick
        elif name == None:
            name = ctx.author.name
        name = name.title()
        draw.text((20,20),name,font=title,fill=(88, 23, 13))
        draw.text((20,h+25),f'{latest_rank}, {alignment}',font=italic,fill=(0,0,0))

        #increases the height and adds the separator to the background
        h += italic.getsize('Player')[1] + 25
        img.paste(separator,(20,h+5))
        h += 10

        #stat generation with 4 dice rolls for each block (take the best 3)
        stats = []
        if rolltype == 'array':
            stats = [15,14,13,12,10,8]
            random.shuffle(stats)
        else:
            for i in range(6):
                rolls = [0,0,0]
                for k in range(rolltype):
                    rand = random.randint(1,6)
                    if k < 3:
                        rolls[k] = rand
                    else:
                        #sorts in ascending order so the lowest can be replaced if needed
                        rolls.sort()
                        if rolls[0] < rand:
                            rolls[0] = rand
                stats.append(sum(rolls))


        #orders the stats if there is a defined preference
        count = 0
        if pref != None:
            #try:
            tmpstats = stats
            #stats in ascending order
            stats.sort()
            #reverses the ordering
            stats = stats[::-1]
            preforder = [5,5,5,5,5,5]

            #ensures that all values in pref are uppercase
            for p in pref:
                for s in stattypes:
                    if s == p:
                        preforder[count] = stattypes.index(s)
                        count += 1
                        continue
            stats = [x for _,x in sorted(zip(preforder,stats))]

        #draws the names of the stat types to the background using a for loop
        x = 40
        for stat in stattypes:
            draw.text((x,h+10),stat,font=regular,fill=(0,0,0))
            x += 75

        #increases the height
        h += 10 + regular.getsize('STR')[1]

        #calculates the stat bonus for each slot
        bonus = []
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
        for i in range(10):
            if found:
                break
            base="https://www.youtube.com/results?search_query="
            query = query.replace(' ','+')
            #query = urllib.parse.quote(query)
            r = requests.get(base+query)
            page=r.text
            r.close()
            soup=bs(page,'html.parser')
            #vids = soup.findAll('a',attrs={'class':'yt-uix-tile-link'})
            vids = soup.findAll('a',attrs={'class':'yt-simple-endpoint style-scope ytd-video-renderer'})
            for v in vids:
                print(v)
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
    client.loop.create_task(client.get_cog('Fun').person_16())
    client.loop.create_task(client.get_cog('Fun').meabhISFJ())
