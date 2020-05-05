######### Bot V0.2.1 created by Kiran Wallace #########
#### - created 8th April 2020 - last edit 13th April
#
######### API Created by Rapptz on GitHub #########
#https://github.com/Rapptz/discord.py
# This bot is for the intent to be used as a fun resource for Discord servers and is a work in progress
#
# In this section of code, you will find the following:
### Events:
# on_ready, on_command_error, on_member_join, on_member_remove
### Commands:
# .load, .unload, .reload
### Functions:
# add_usage, ConsoleMessage, ErrorLog, has_channel_perms, deLeetSpeak
### Objects:
# User
################################################################################################################

import discord
import os
import sys
import json
import random
import time
import asyncio
import webbrowser
from datetime import datetime
from discord.ext import commands
from discord.utils import get

#prefix needed before a command is called
#(Changing this may make a few things not make sense as the bot will tell you to use '.' in some of its messages. It will work though)
client = commands.Bot(command_prefix = '.')

#directory for the bot
PATH = (os.path.dirname(os.path.realpath(__file__)))[:-4]

#initialise a list for banned words
wordlist = []
#initialise an object list for users to keep track of message count for anti-spamming
users = []

#user object for preventing spam
class User(object):
    def __init__(self,id):
        #the user id is initialised with the object, this is used to identify the user and if they have been previously noted in the list
        self.id = id
        #last time the user messaged
        self.last_msg_time = 0
        #the time of when the user was initially cautioned by the bot, used to see if the user is allowed to message yet
        self.purge_time = 0
        #amount of time before the user can message again if the user has been banned from messaging
        self.timeout = 0
        #number of times the bot has recorded the user spamming messages. Used as a multiplier for self.timeout
        self.offences = 0
        #message counter, if this exceeds 10 then the bot will place the "Heretic" role on the user
        self.msg_spam = 0
        #the "isPurged" check is different to the "botplaced" check. This is a temporary placement to prevent duplicate messages from the bot.
        #once the bot has set the role and sent the message, this will be set to false
        self.isPurged = False
        #a string that is set as the users last message, if it is the same as the current message and not enough time has passed in order for it not to be considered spam, an additional point is placed in self.msg_spam
        self.last_msg = ''
        #this is a check as it tells the bot that the demotion role was placed by the bot itself and will therefore look at the time left for the silence
        #if this is false but the user has the role, it must have been placed by an admin/moderator
        self.botplaced = False


#function for adding stats to "usage.json" for  ".stats" command in Utility.
def add_usage(use,add=1):
    #will attempt to find and open "usage.json"
    try:
        with open(f'{PATH}\\data\\usage.json','r') as f:
            stats = json.load(f)
        #will attempt to add to existing stat from the json file
        try:
            stats[use] += add
        #upon failing, assume stat does not exist yet and create a new one
        except:
            stats[use] = add
        #overwrites the file with the new usage data
        with open(f'{PATH}\\data\\usage.json','w') as f:
            json.dump(stats, f, indent=4)
    #upon failing, will create a new dictionary with the data to add and create a new file called "usage.json"
    except:
        stats = {}
        stats[use] = add
        with open(f'{PATH}\\data\\usage.json','w') as f:
            json.dump(stats, f, indent=4)

#function for printing to the console and appending data to "../data/user logs/"
def ConsoleMessage(message):
    #formatting for the console with the time, a separator and the message
    message = f'{datetime.now().strftime("%H:%M:%S")}¦ {message}'
    #appends to existing or creates a new file with date formatting. If one does not exist for that day then will create a new log
    with open(f'{PATH}\\data\\user logs\\{datetime.today().strftime("%d-%m-%Y")}.txt','a',encoding='UTF-8') as f:
        #due to some channels containing emojis, an error can be thrown for the unicode
        try:
            f.write(f'{message}\n')
        except UnicodeEncodeError:
            message = message.encode('unicode_escape').decode('utf-8')
            message = message.replace('\\xa6','¦')
            f.write(f'{message}\n')
    print(message)

#very similar to ConsoleMessage(message) above
#function for printing a warning on the console and appending data to "../data/error logs/", bug fixing purposes
def ErrorLog(error):
    #adds to "Errors caught" stat in "usage.json"
    add_usage("Errors caught")
    #formatting for the console with the time, a separator and the message
    message = f'{datetime.now().strftime("%H:%M:%S")}¦ '
    #appends to existing or creates a new file with date formatting. If one does not exist for that day then will create a new log
    with open(f'{PATH}\\data\\error logs\\{datetime.today().strftime("%d-%m-%Y")}.txt','a') as f:
        #due to some channels containing emojis, an error can be thrown for the unicode
        try:
            f.write(f'{message}{error}\n')
        except UnicodeEncodeError:
            message = message.encode('unicode_escape').decode('utf-8')
            message = message.replace('\\xa6','¦')
            f.write(f'{message}{error}\n')
    print(f'{message}== An error occured == Please see the updated error logs at ..\\data\\error logs\\{datetime.today().strftime("%d-%m-%Y")}.txt')

#function for checking if the command in question can be used in the current server channel/category
def has_channel_perms(ctx):
    #opens location for the json with the command permissions data
    with open(f'{PATH}\\config\\command locations.json', 'r') as f:
        cmds = json.load(f)
    #cycles through all of the commands that are found in the json until the command in question is found
    for command in cmds["commands"]:
        if ctx.message.content.startswith(command["name"]):
            #if the whitelist is enabled, only channels/categorys found in the whitelists are permitted to use the command
            if command["whitelist"]:
                #searches permitted channels for channel command was used in, if found will return true
                for channel in command["whitelist channels"]:
                    if ctx.channel.id == channel["id"]:
                        return True
                #searches permitted categorys for category command was used in, if found will return true
                for category in command["whitelist category"]:
                    if ctx.channel.category_id == category["id"]:
                        return True
                #if current channel/category was not found in either list and "whitelist" is active, assume not permitted and return false
                return False
            #if the whitelist is not enabled but blacklist is enabled, channels/categorys found in these lists are not permitted to use the command but all others are
            elif command["blacklist"]:
                #searches non-permitted channels for channel command was used in, if found will return false
                for channel in command["blacklist channels"]:
                    if ctx.channel.id == channel["id"]:
                        return False
                #searches non-permitted categorys for category command was used in, if found will return false
                for category in command["blacklist category"]:
                    if ctx.channel.category_id == category["id"]:
                        return False
                #if current channel/category was not found in either list and "blacklist" is active, assume permitted and return true
                return True
            break
    #if command is not found or there is no whitelist and blacklist enabled, assume has permissions
    return True

#function used in removing banned words as users may attempt to bypass the wordcheck by disguising symbols as other letters, or using "1337" (leet) speak
#the reason this adds a new version of the word rather than replacing the symbol for what it represents is that the same symbol can represent the same thing
#E.G: 1 could represent either i or l
def deLeetSpeak(word):
    out = []
    if 'i' in word:
        out.append(word.replace('i','1'))
        out.append(word.replace('i','l'))
    if 'l' in word:
        out.append(word.replace('l','i'))
        out.append(word.replace('l','1'))
    if 'e' in word:
        out.append(word.replace('e','3'))
    if 'b' in word:
        out.append(word.replace('b','3'))
    return out

#function used for loading the banned words list
def loadWordDict():
    #loads the words list from the file
    bannedwords = []
    with open(f'{PATH}\\config\\forbidden words.txt','r') as f:
        for line in f:
            bannedwords.append(line.replace('\n',''))
    #initialised value for how many letters can be swapped for "leet" speak. This will be used to iterate through the for loop
    leetables = 0
    newlist = []
    for word in bannedwords:
        if 'i' in word:
            leetables += 1
        if 'l' in word:
            leetables += 1
        if 'e' in word:
            leetables += 1
        if 'b' in word:
            leetables += 1
        
        tmp = [word]
        tmp1 = [word]
        #as multiple letters can be encrypted in the same word, the for loop creates a new version of the word for every letter that can be disguised
        for i in range(leetables):
            for item in tmp1:
                newitemlist = deLeetSpeak(item)
                for newitem in newitemlist:
                    if newitem not in tmp:
                        tmp.append(newitem)
            tmp1 = tmp

    return list(dict.fromkeys(tmp))

######################################################################################################
#############################################   EVENTS   #############################################
#This section is for event checking and will call the below functions if the event in question occures

#function called if the bot successfully boots up and is ready for use
@client.event
async def on_ready():
    #will load all extensions of the bot that can be found in the dir ./cogs
    #cogs allow for commands to be split into sections to make fixing easier and allows for the unloading/reloading of said sections
    for filename in os.listdir('./cogs'):
        #extensions are only considered if it is a python program (.py suffix)
        if filename.endswith('.py'):
            print(f'        Loading extension: {filename[:-3]}...',end='')
            try:
                client.load_extension(f'cogs.{filename[:-3]}')
                print('Complete')
            except commands.ExtensionAlreadyLoaded as e:
                print('Extension previously loaded')
                continue
                
    #once all extensions are loaded, host is informed that the bot is active
    print(f'   - {client.user.name} is online!')
    print(' ------------------------------------------------------------------')
    #adds to "Successful bootups" stat in "usage.json"
    #originally for testing the add_usage() function but was kept for fun
    add_usage("Successful bootups")

#function called after every message
@client.event
async def on_message(ctx):
    #the bot will ignore any message made by itself
    if ctx.author.id == client.user.id:
        return
    #this may throw an error if the user does not have any permissions, hence the try/catch
    try:
        #checks if the user is an admin, if they are all further checks such as spam and badwords are bypassed
        if ctx.channel.permissions_for(ctx.author).administrator:
            await client.process_commands(ctx)
            return
    except:
        pass
    #check for spam
    #check if user can message (do they have the demotion role)
    if get(ctx.author.guild.roles, name='Heretic') in ctx.author.roles:
        #checks the list of users that have been monitored for the user
        for member in users:
            if member.id == ctx.author.id:
                #if the role was placed by the bot and the temporary silence time has passed
                if member.botplaced and time.time() - member.purge_time > member.timeout:
                    #remove the role and inform the user that they can now speak
                    role = get(ctx.author.guild.roles, name='Heretic')
                    await ctx.author.remove_roles(role)
                    member.botplaced = False
                    await ctx.channel.send(f'I hope you can behave now {ctx.author.mention}! Next time, I\'ll be meaner!')
                    return
        #if the role was not placed by the bot or it was but the silence time has not passed
        try:
            await ctx.delete()
            return
        #upon failing, assume message was removed
        except:
            ErrorLog(f'Failed to remove message for {ctx.author}')
            return

    #will attempt to process any command that is in the users message
    else:
        await client.process_commands(ctx)
                    
    #checks the list of users made by the bot for the member
    founduser = False
    for member in users:
        if member.id == ctx.author.id:
            founduser = True
            #check if the bot is still processing a user for spam
            if member.isPurged:
                return
            #if the user has no recorded messages, set the last time sent to now
            elif member.last_msg_time == 0:
                member.msg_spam = 0
            #if the user has not sent a message in 2 minutes, reset stats
            elif time.time() - member.last_msg_time > 120:
                member.msg_spam = 0
            #if the last mesasge is the same as the current message and it was within 1.5 seconds
            elif ctx.content == member.last_msg and time.time() - member.last_msg_time <= 1.5:
                #set last time to now and increase the spam counter
                member.msg_spam += 2
                #if the message is over 200 characters long, increase the counter further
                if len(ctx.content) > 200:
                    member.msg_spam += 1
            #if the time between now and the previous message is more than 1.5 seconds
            elif time.time() - member.last_msg_time > 1.5:
                #if this message is not the same as the last, set time to now and deduct 1 from spam counter
                if member.last_msg != ctx.content:
                    if member.msg_spam > 0:
                        member.msg_spam -= 1
                #if it is the same message but it's been more than 5 seconds, set time to now and deduct 1 from spam counter
                elif time.time() - member.last_msg_time > 5:
                    if member.msg_spam > 0:
                        member.msg_spam -= 1
                #if it has not been more than 5 seconds yet the message is the same as the last, increase counter by 1
                else:
                    member.msg_spam += 1
                    #if the message has more than 200 characters, increase counter by 1
                    if len(ctx.content) > 200:
                        member.msg_spam += 1
            #if the message is not the same but is within 1.5 seconds, set last time to now and 
            else:
                member.msg_spam += 1
                if len(ctx.content) > 200:
                    member.msg_spam += 1
            #sets last message time and the last message
            member.last_msg_time = time.time()
            member.last_msg = ctx.content

            #if the user has spammed the chat enough to make the counter reach 10
            if member.msg_spam >= 10:

                #temp check so the bot doesn't itterate through this function more than once if there is latency or the user is spamming quicker than the bot can silence
                #(without this, the bot will spam the message once or twice)
                member.isPurged = True
                #a check on the user to confirm that the role was placed automatically
                member.botplaced = True
                #adds to offences counter
                member.offences += 1
                #keeps track of time of disipline
                member.purge_time = time.time()
                #if the number of offences are 3 or less, the time out time is x minutes
                if member.offences < 4:
                    member.timeout = 60 * member.offences
                #if the user has done this more than 3 times, the time out time is 5 minutes * number of offences over 3
                else:
                    member.timeout = 300 * (member.offences-3)

                ###loop used to remove all roles from the user
                ###no longer in use now the bot checks for the heretic role and prevents messages
                #for role in ctx.author.roles:
                #    if role.name != '@everyone' and role.name != 'Heretic':
                #        try:
                #            await ctx.author.remove_roles(role)
                #        except:
                #            continue
                
                #obtains the demotion role and applies it to the user
                #TODO: make the name of the role configurable and allow the bot to make it if not already existing
                role = get(ctx.author.guild.roles, name='Heretic')
                await ctx.author.add_roles(role)
                #await asyncio.sleep(1)

                #simple grammar check. If the time out is 1 minute (first offence), it will say 1 minute as opposed to 1 minutes. It's predantic but kinda nice
                if member.timeout == 60:
                    await ctx.channel.send(f'Sorry {ctx.author.mention}, but I\'ve been told to demote anyone that\'s spamming the server!\nTry messaging in 1 minute to remove the @Heretic role\nIf something is wrong about this then just send a message to <@!474037926641008640>')
                else:
                    await ctx.channel.send(f'Sorry {ctx.author.mention}, but I\'ve been told to demote anyone that\'s spamming the server!\nTry messaging in {int(member.timeout/60)} minutes to remove the @Heretic role\nIf something is wrong about this then just send a message to <@!474037926641008640>')

                #sets the check to false, the bot is done dealing with the user at this point
                member.isPurged = False
                #resets the counters for the user
                member.msg_spam = 0
                member.last_msg_time = 0

                #logs the action of the bot to the console
                ConsoleMessage(f'{ctx.author} was automatically demoted for spam')

    #if the user has not been added to the list, create a new user object and add to the list
    if founduser == False:
        user = User(ctx.author.id)
        user.last_msg = ctx.content
        users.append(user)

    #banned word check
    #removes whitespace and replaces substitute symbols as attempts to bypass the checks
    msg = ctx.content.replace('\t','')
    msg = msg.replace('\n','')
    msg = msg.replace(' ','')
    exclude = set([' ','\n','\t','.',':','#','_','-','+','!'])
    msg = ''.join(ch for ch in msg if ch not in exclude)
    msg = msg.replace('4','a')
    msg = msg.replace('@','a')
    msg = msg.replace('Д','a')
    msg = msg.replace('£','e')
    msg = msg.replace('€','e')
    msg = msg.replace('()','o')
    msg = msg.replace('[]','o')
    msg = msg.replace('{}','o')
    msg = msg.replace('0','o')
    msg = msg.replace('8','b')
    msg = msg.replace('$','s')

    #changes message to lower case
    msg = msg.lower()
    #checks the banned words list and compares to the message
    for word in wordlist:
        #if the message is found, it is removed and logged
        if word in msg:
            await ctx.delete()
            ConsoleMessage(f'{ctx.author}\'s message: "{ctx.content}" was automatically removed by the bot as it was believed to contain the word "{wordlist[0]}"')
            add_usage("forbidden messages removed")
            return

#function for informing what to do if a command throws an error, prevents spam in the console
@client.event
async def on_command_error(ctx,error):
    #ignores bot itself if it happenes to begin a message with '.'
    if ctx.author.id == client.user.id:
        return
    #checks for custom commands if not found
    elif isinstance(error, commands.CommandNotFound):
        #check for if the command has been found in the list of custom commands
        found = False
        #the message is split into a list and the json is opened and converted into a dictionary
        msg = ctx.message.content.split(' ')
        #easy formatting for .json users rather than having to deal with intimidating formats
        user = ctx.author
        if len(msg) > 1:
            message = ctx.message.content[(len(msg[0]) + 1):]
        with open(f'{PATH}\\config\\custom commands.json','r', encoding = 'UTF-8') as f:
            cmds = json.load(f)
        #go through all of the custom commands and find the custom command
        for cmd in cmds:
            #if the command is found in the list
            if cmd == msg[0]:
                found = True
                #if the command is restricted to admin only
                if 'admin' in cmds[cmd] and cmds[cmd]['admin'] == True:
                    if not ctx.channel.permissions_for(ctx.author).administrator:
                        return
                #if there is a counter for this custom command
                if 'counter' in cmds[cmd]:
                    add_usage(cmds[cmd]['counter'])
                ####command types result in different response types:
                #'simple' gives a single command output
                #'random' gives a random output
                #'user' gives a response based on the user
                if cmds[cmd]['type'] == 'simple':
                    out = cmds[cmd]['response']
                elif cmds[cmd]['type'] == 'random':
                    out = random.choice(cmds[cmd]['response'])
                elif cmds[cmd]['type'] == 'user':
                    userfound = False
                    #attempts to find the users id in the list
                    for member in cmds[cmd]['userlist']:
                        #if found, will respond with the user specific response
                        if ctx.author.id == member['id']:
                            out = member['response']
                            userfound = True
                            break
                    #if user could not be found, will respond with generic response found
                    if not userfound:
                        out = cmds[cmd]['generic']
                    #if no response, use None (null in json)
                    if out == None:
                        return

                #if invalid command type, inform errorlog
                else:
                    ErrorLog(f'Invalid cmd type for {msg[0]}: {cmds[cmd]["type"]}')
                    return
                break
        #if the command has been found, send output
        if found:
            try:
                out = eval(f'f"""{out}"""')
            except Exception as e:
                error = e
                try:
                    out = eval(f'f"""{cmds[msg[0]]["error"]}"""')
                except:
                    ErrorLog(error)
            await ctx.send(out)

#Event for member joining the server
@client.event
async def on_member_join(member):
    ConsoleMessage(f'{member} has joined the server')

#Event for error leaving the server
@client.event
async def on_member_remove(member):
    ConsoleMessage(f'{member} has left the server')

########################################################################################################
#############################################   COMMANDS   #############################################
#This section is for command calling, all functions with the decorator @client.command() will be called
#if typed into discord with the prefix '.'

#function for loading and enabling extensions from ./cogs
#used for if new extension has been made or a previous one was unloaded/failed to load
#must have admin permissions
@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    print(f'        ¦ Loading extension: {extension}...',end='')
    client.load_extension(f'cogs.{extension}')
    print('Complete')
    ConsoleMessage(f'{ctx.author} loaded extension {extension}')
    await ctx.send(f'Extension {extension} has been enabled along with all of its associated commands.\nTo see avaliable commands, type `.help`')

#called upon error for .load
@load.error
async def load_error(ctx, error):
    #if the user does not have the appropriate permissions
    print()
    if isinstance(error, commands.CheckFailure):
        ConsoleMessage(f'{ctx.author} failed to use .load due to lack of privileges')
    #otherwise, add to error log
    elif isinstance(error, commands.ExtensionAlreadyLoaded):
        ConsoleMessage(f'{ctx.author} attempted to load an already loaded extension')
    elif isinstance(error, commands.ExtensionNotFound):
        ConsoleMessage(f'{ctx.author} attempted to load a none-existing extension: {ctx.content[6:]}')
    else:
        ErrorLog(error)

#function for unloading and disabling extensions from ./cogs
#used if admin user wants to prevent usage of certain commands
#must have admin permissions
@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    print(f'        ¦ Unloading extension: {extension}...',end='')
    client.unload_extension(f'cogs.{extension}')
    print('Complete')
    ConsoleMessage(f'{ctx.author} unloaded extension {extension}')
    await ctx.send(f'Extension {extension} has been disabled along with all of its associated commands.\nTo see avaliable commands, type `.help`')

#called upon error for .unload
@unload.error
async def unload_error(ctx, error):
    print()
    #if the user does not have the appropriate permissions
    if isinstance(error, commands.CheckFailure):
        ConsoleMessage(f'{ctx.author} failed to use .unload due to lack of privileges')
    #otherwise, add to error log
    else:
        ErrorLog(error)

#function for unloading and then loading extensions from ./cogs
#used for changing the code of an extension (mostly in "feature" fixing or adding features) and wanting to apply without closing the client
#must have admin permissions
@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    print(f'        ¦ Reloading extension: {extension}...',end='')
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    print(f'Complete\n        ¦ Extension {extension} reloaded')
    ConsoleMessage(f'{ctx.author} reloaded extension {extension}')
    await ctx.send(f'Extension {extension} has been reloaded along with all of its associated commands.\nTo see avaliable commands, type `.help`')

#called upon error for .reload
@reload.error
async def reload_error(ctx, error):
    print()
    #if the user does not have the appropriate permissions
    if isinstance(error, commands.CheckFailure):
        ConsoleMessage(f'{ctx.author} failed to use .reload due to lack of privileges')
    #otherwise, add to error log
    else:
        ErrorLog(error)
        await ctx.send(f'Extension has failed to reload. If the extension has been unloaded, try `.load` instead. Make sure it\'s an existing extension\n(Note: This is for code fixing without closing the client, you don\'t need to use this unless you know what you\'re doing)')

@client.command()
@commands.has_permissions(administrator=True)
async def dictreload(ctx):
    ConsoleMessage(f'{ctx.author} reloaded banned words file')
    wordlist = loadWordDict()

#if this program is called __main__ by the interperator, run the client
if __name__ == '__main__':
    #checks if any arguments have been passed through the terminal with the program (this can be done by running the progam in a cmd prompt, terminal or using a batch/script file to boot)
    #E.G: python ./main.py PyBot V0.3.0.0
    if len(sys.argv) > 1:
        #if so, use the arguments as the name and version
        version = ' '.join(sys.argv[1:])
    #if no arguments were passed (by most likely using an IDE), use the earliest update for this bot
    #(this most likely won't be updated much from now)
    else:
        version = 'PyBot V0.3.0.0'
    print(f' ========================= {version} ========================= ')
    print(f'   - Booted at {datetime.now().strftime("%H:%M:%S")}\n   - Please wait...')
    print('        Loading Dictionary...',end='')
    try:
        wordlist = loadWordDict()
        print('Complete')
    except:
        print('\n        [WARNING]: No values found in Dictionary')
    print('        Obtaining token from textfile...',end='')
    try:
        with open('TOKEN.txt','r') as f:
            TOKEN = f.read()
            if len(TOKEN) > 1:
                print('Token found')
                client.run(TOKEN)
            else:
                raise Exception()
    except:
        print('\n[ERROR]:  Token not found. Please paste your bot token in the TOKEN.txt file')
        print('                If you do not have a token, go to https://discordapp.com/developers/applications/ (This should automatically open in your browser)')
        print('                Select your application/bot and click "Bot" on the left hand side\n                You will find your Token under the Bots username\n                If the token is given out unintentionally, simply regenerate your Token\n[WARNING]: Do not share your token! This could grant anyone access to your bot')
        try:
            webbrowser.open('https://discordapp.com/developers/applications/')
        except:
            pass
    
    
