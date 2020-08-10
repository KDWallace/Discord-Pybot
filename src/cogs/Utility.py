######### Bot V0.4 created by Kiran Wallace #########
### NOTE: This is not the main module. Please run main.py
# This is an extension of main.py
# This bot is for the intent to be used as a fun resource for Discord servers and is a work in progress
#
# In this section of code, you will find the following:
### Commands:
# .clear, .changestatus, .help2, .stats, .addcmd, .rmvcmd
### Functions:
# setup
################################################################################################################

import discord, random, json
from main import ConsoleMessage, ErrorLog, add_usage, has_botrank
from discord.ext import commands

class Utility(commands.Cog):
    #initialises object with client from main
    def __init__(self, client):
        self.client = client


    #@commands.Cog.listener()
    #async def on_member_update(self,before,after):
    #    print(after.author)

########################################################################################################
#############################################   COMMANDS   #############################################
#This section is for command calling, all functions with the decorator @client.command() will be called
#if typed into discord with the prefix '.'

    #simply sends a message "pong" with the latency between the server and client in milliseconds
    #not massivly useful, just interesting
    #@commands.command()
    #async def ping(self, ctx):
    #    await ctx.send(f'pong! {round(self.client.latency * 1000)}ms')
    #    add_usage("pings")

    #clean up tool that deletes a specified amount of messages, default 1
    #must have admin privileges to use
    @commands.command(description='A quick method of removing a number of messages quickly')
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, amount=1):
        await ctx.channel.purge(limit=amount+1)
        #informs the console of the changes and adds to clear counter in "usage.json"
        if amount > 1:
            ConsoleMessage(f'{ctx.author} cleared {amount} messages from channel #{ctx.channel.name}')
            add_usage("messages cleared",amount)
        elif amount == 1:
            ConsoleMessage(f'{ctx.author} cleared 1 message from channel #{ctx.channel.name}')
            add_usage("messages cleared")

    #if an error is thrown for using .clear
    @clear.error
    async def clear_error(self, ctx, error):
        #if the user does not have the required permissions, inform the console
        if isinstance(error, commands.CheckFailure):
            ConsoleMessage(f'{ctx.author} failed to use .clear due to lack of privileges')
        #otherwise, assume poor input
        elif isinstance(error, commands.BadArgument):
            randval = random.randint(2,20)
            await ctx.send(f'Sorry {ctx.author.mention}, I don\'t think I understand. Try `.clear {randval}` to remove {randval} messages')
        else:
            ErrorLog(error)

    @commands.command(aliases=['cn','nick','nickname','changenick'])
    @commands.check(has_botrank)
    async def changenickname(self,ctx,user,*,nickname):
        if int(user[3:-1]) != ctx.author.id:
            user = ctx.guild.get_member(int(user[3:-1]))
            if user != None:
                ConsoleMessage(f'{ctx.author} changed {user}\'s name to {nickname}')
                if len(nickname) > 32:
                    await ctx.send(f'Sorry {ctx.author.mention}, but that nickname is too long (32 character limit, `{nickname}` has {len(nickname)} characters) :sweat_smile:')
                else:
                    await user.edit(nick=nickname)# client.change_nickname(user,nick)
            else:
                await ctx.send(f'Sorry {ctx.author.mention}, but I couldn\'t find that user :frown:\nPlease use the format of `.nick @username nickname`')
        else:
            await ctx.send(f'{ctx.author.mention} tried to change their own nickname, they should be ashamed! :angry:')

    #changes the status of the bot on discord below the bots name. The user can choose from either "playing", "watching" or "listening to"
    #must have admin privileges to use
    @commands.command(description='Allows for the status of the bot to be changed\nExample: .changestatus playing with scissors\n.changestatus watching the world burn\n.changestatus listening (to) the good noises')
    @commands.has_permissions(administrator=True)
    async def changestatus(self, ctx, statType, *, status):
        #creates the action that the bot is doing based on input
        if statType.lower() == 'watching':
            customAct = discord.Activity(type=discord.ActivityType.watching, name = status)
        elif statType.lower() == 'listening':
            customAct = discord.Activity(type=discord.ActivityType.listening, name = status)
        elif statType.lower() == 'playing':
            customAct = discord.Game(status)

        #if the inputted action is not on the valid list, inform user and give valid examples
        else:
            await ctx.send(f'Sorry {ctx.author.mention}, but I need to be playing, watching or listening to something\nE.g: `.changestatus playing Mario` means that I can play Mario! :smile:')
            return

        #changes the status of the bot
        await self.client.change_presence(status=discord.Status.idle, activity=customAct)

        #informs the console of the change and adds data to "usage.json"
        ConsoleMessage(f'{ctx.author} changed the status to {statType} {status}')
        add_usage("status changes")

    #upon error for .changestatus
    @changestatus.error
    async def changestatus_error(self, ctx, error):
        #if the error is due to lack of privileges, inform console
        if isinstance(error, commands.CheckFailure):
            ConsoleMessage(f'{ctx.author} failed to use .changestatus due to lack of privileges')
        #otherwise, add errorlog
        else:
            ErrorLog(error)

    @commands.command(description='Help page for the custom commands')
    async def help2(self, ctx, *, commandname=None):
        with open('../config/custom commands.json', 'r', encoding = 'UTF-8') as f:
            cmds = json.load(f)
        string = ''
        if commandname == None:
            string += '```'
            for cmd in cmds:
                #if the command is restricted to admin only, it will not print if the user is not an admin
                if 'admin' in cmds[cmd] and cmds[cmd]['admin'] == True:
                    if not ctx.channel.permissions_for(ctx.author).administrator:
                        continue
                    else:
                        string += f'\n{cmd} - [admin only]'
                else:
                    string += f'\n{cmd}'
            string += '\n\nType .help2 command for more info on a command```'
        else:
            found = False
            if not commandname.startswith('.'):
                commandname = '.' + commandname
            for cmd in cmds:
                if cmd == commandname:
                    found = True
                    string += f'```\nName: {commandname}'
                    if 'desc' in cmds[cmd] and len(cmds[cmd]['desc']) > 0:
                        string += f"\nDescription: {cmds[cmd]['desc']}"
                    if 'format' in cmds[cmd] and len(cmds[cmd]['format']) > 0:
                        string += f"\nUsage: {cmds[cmd]['format']}"
                    string += '```'
            if not found:
                string = f'Cound not find a custom command called `{commandname}`\nIf you think this is a mistake or an error, contact an admin on the server'
        await ctx.send(string)

    @help2.error
    async def help2_error(self, ctx, error):
        ErrorLog(error)

    @commands.command(description='Presents the usage stats of the bot')
    async def stats(self,ctx):
        string = '``` ==== Bot Usage Stats ===='
        try:
            with open('../data/usage.json', 'r', encoding='UTF-8') as f:
                data = json.load(f)
            string = '``` ==== Bot Usage Stats ===='
            for stat in data:
                string += f'\n{stat}: {data[stat]}'
        except:
            pass
        if string == '``` ==== Bot Usage Stats ====':
            string = 'Hmm, there doesn\'t seem to be any data saved yet...'
        else:
            string += '```'
        await ctx.send(string)

    @stats.error
    async def stats_error(self,ctx,error):
        ErrorLog(error)

    @commands.command(description='Allows admin to create a command\nUsage: make sure multi word strings used for the options is inside of "" and that requireAdmin is either "true" or "false"\nFor random choice response, separate the choices with ".+"\n\nExample: .addcmd randmessage "Hello there.+This is a random message.+I am also random"\n\nThis gives 3 possible responses that the bot will randomly choose from when someone types .randmessage\n\nFor extra fun, use {user.mention} to mention the user, {user.name} for their username or {message} if you would like it to use the message after the command.\nExample: .addcmd hello "Hey there {user.mention}! :smile:"\n\nOnly the command name and the response(s) are required to make a command. The rest are for extra features')
    @commands.has_permissions(administrator=True)
    async def addcmd(self,ctx,cmdName,response,error=None,desc=None,format=None,requireAdmin=False,usage=None):
        with open('../config/custom commands.json', 'r', encoding = 'UTF-8') as f:
            cmds = json.load(f)
        if cmdName.startswith('.') == False:
            cmdName = '.' + cmdName
        if cmdName in cmds:
            await ctx.send(f'Sorry {ctx.author.mention}, but there is already a command called `{cmdName}`')
            return
        if '.+' in response:
            response = response.split('.+')
        if requireAdmin.tolower() == 'true':
            requireAdmin = True
        else:
            requireAdmin = False
        newcmd = {'response': response}
        if (error == 'None' or error == None) and '{message}' in response:
            error = f'Missing required message after `{cmdName}`'
        if error != 'None' and error != None:
            newcmd['error'] = error
        if desc != 'None' and desc != None:
            newcmd['desc'] = desc
        if (format == 'None' or format == None) and '{message}' in response:
            format = f'{cmdName} [message]'
        if format != 'None' and format != None:
            newcmd['format'] = format
        if requireAdmin:
            newcmd['admin'] = True
        if usage != 'None' and usage != None:
            newcmd['usage'] = usage
        cmds[cmdName] = newcmd
        with open('../config/custom commands.json', 'w', encoding = 'UTF-8') as f:
            json.dump(cmds,f,indent=4)
        await ctx.send(f'Successfully created `{cmdName}` command! :smile:')
        ConsoleMessage(f'{ctx.author} created new command: {cmdName}')

    @addcmd.error
    async def addcmd_error(self,ctx,error):
        await ctx.send(f'Sorry {ctx.author.mention}, but I think you inputted that command in wrong. Try adding a response after the command! :sweat_smile:')
        ErrorLog(error)

    @commands.command(description='This is used to remove a custom command. (Note: Some commands are protected and cannot be removed without dev permission)')
    @commands.has_permissions(administrator=True)
    async def rmvcmd(self,ctx,name):
        with open('../config/custom commands.json', 'r', encoding = 'UTF-8') as f:
            cmds = json.load(f)
        if name.startswith('.') == False:
            name = '.' + name
        if name in cmds:
            if 'protected' in cmds[name] and cmds[name]['protected'] == True:
                await ctx.send(f'Sorry {ctx.author.mention} but this is a protected command. You need to contact the developer to remove this one')
                ConsoleMessage(f'{ctx.author} attempted to remove command {name}')
                return
            else:
                del cmds[name]
                ConsoleMessage(f'{ctx.author} removed the custom command: {name}')
                await ctx.send(f'{name} has been successfully removed from the custom commands list!')
                return
        else:
            await ctx.send(f'I\'m sorry {ctx.author.mention} but the custom command {name} doesn\'t appear to exist')

    @rmvcmd.error
    async def rmvcmd_error(self,ctx,error):
        await ctx.send(f'You need to enter the name of the command after `.rmvcmd`')
        ErrorLog(error)


#adds extension to client when called
def setup(client):
    client.add_cog(Utility(client))
