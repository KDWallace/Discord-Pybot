######### Bot V0.4 created by Kiran Wallace #########
### NOTE: This is not the main module. Please run main.py
# This is an extension of main.py
# This bot is for the intent to be used as a fun resource for Discord servers and is a work in progress
#
# In this section of code, you will find the following:
### Events:
# on_raw_reaction_add, on_raw_reaction_remove
### Commands:
# .autoroles, .addrole, .rolemessage, .removerole
### Functions:
# setup
################################################################################################################

import os
import json
from main import ConsoleMessage, ErrorLog, PATH
from discord.ext import commands
from discord.utils import get, find

class Roles(commands.Cog):
    #initialises object with client from main
    def __init__(self, client):
        self.client = client
        self.roleData = {}
        self.messageID = 0
        #host is informed that the bot is active
        try:
            with open(f'{PATH}\\config\\roles.json','r') as f:
                data = json.load(f)
            tmp1 = []
            tmp2 = []
            for rls in data['roles']:
                try:
                    tmp1.append(rls['reaction'])
                    tmp2.append(rls['role name'])
                except:
                    print(f'   - There appears to be a typo for either "role name" or "reaction"\n in {PATH}\\config\\roles.json')
            self.roleData = dict(zip(tmp1,tmp2))
            self.messageID = data['message id']
        except:
            data = {'message id': 0,'channel id': 0,'message':'Hey @everyone!\nPlease react to this message if you would like access to other parts of the server with the reactions shown below! :smile:\n','roles':[]}
            with open(f'{PATH}\\config\\roles.json','w') as f:
                json.dump(data,f,indent=4)
            print(f'   - file {PATH}\\config\\roles.json\n appeared to be missing and has been regenerated')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,ctx):
        #ignores bot
        if ctx.user_id == self.client.user.id:
            return
        if ctx.message_id == self.messageID:
            if ctx.emoji.name in self.roleData:
                server = find(lambda g : g.id == ctx.guild_id, self.client.guilds)
                role = get(server.roles,name=self.roleData[ctx.emoji.name])
                if role != None:
                    author = find(lambda a : a.id == ctx.user_id, server.members)
                    await author.add_roles(role)
                    ConsoleMessage(f'{author} has been self-assigned the role {self.roleData[ctx.emoji.name]}')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,ctx):
        #ignores bot
        if ctx.user_id == self.client.user.id:
            return
        if ctx.message_id == self.messageID:
            if ctx.emoji.name in self.roleData:
                server = find(lambda s : s.id == ctx.guild_id, self.client.guilds)
                role = get(server.roles,name=self.roleData[ctx.emoji.name])
                if role != None:
                    author = find(lambda a : a.id == ctx.user_id, server.members)
                    await author.remove_roles(role)
                    ConsoleMessage(f'{author} has removed their self-assigned role {self.roleData[ctx.emoji.name]}')

########################################################################################################
#############################################   COMMANDS   #############################################
#This section is for command calling, all functions with the decorator @commands.command() will be called
#if typed into discord with the prefix '.'
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autoroles(self,ctx):
        try:
            with open(f'{PATH}\\config\\roles.json','r') as f:
                data = json.load(f)
            roles = []
            reacts = []
            svrFound = False
            message = 'Hey @everyone!\nPlease react to this message if you would like access to other parts of the server with the reactions shown below! :smile:\n'
            if 'message' in data:
                message = data['message']
            else:
                data['message'] = message
            for rls in data['roles']:
                if 'role name' in rls and 'reaction' in rls:
                    roles.append(rls['role name'])
                    reacts.append(rls['reaction'])
                    svrFound = True
            if svrFound:
                for i in range(len(roles)):
                    emoji = get(ctx.guild.emojis,name=reacts[i])
                    role = get(ctx.guild.roles,name=roles[i])
                    if emoji != None and role != None:
                        message += f'\n{emoji} - {role.mention}'
                    else:
                        del roles[i]
                        del reacts[i]

                msg = await ctx.send(message)

                #attempts to delete old message with reacts
                try:
                    ch = self.client.get_channel(data['channel id'])
                    oldmsg = await ch.fetch_message(data['message id'])
                    await oldmsg.delete()
                except:
                    pass
                #saves new data
                data['channel id'] = ctx.channel.id
                data['message id'] = msg.id
                with open(f'{PATH}\\config\\roles.json','w') as f:
                    json.dump(data,f,indent=4)
                self.roleData = dict(zip(reacts,roles))
                self.messageID = msg.id
                await ctx.message.delete()
                for symb in reacts:
                    if symb != None:
                        await msg.add_reaction(get(ctx.guild.emojis,name=symb))
            else:
                await ctx.send('There doesn\'t seem to be any roles to react to at the moment')
        except:
            try:
                data = {'message id': 0,'channel id': 0,'message':'Hey @everyone!\nPlease react to this message if you would like access to other parts of the server with the reactions shown below! :smile:\n','roles':[]}
                with open(f'{PATH}\\config\\roles.json','w') as f:
                    json.dump(data,f,indent=4)
                await ctx.send('There doesn\'t appear to be any role data avaliable at the moment. The file has been replaced with an example')
            except Exception as e:
                ErrorLog(e)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addrole(self,ctx,react,role):
        if react.startswith('<:') and react.endswith('>') and len(react) > 22:
            react = react.replace('<:','')
            react = react[:-20]
        if role.startswith('<@&') and role.endswith('>') and len(role) == 22:
            role = role[3:]
            tmp = get(ctx.guild.roles,id=int(role[:-1]))
            if tmp != None:
                role = tmp.name
        out = ''
        rl = get(ctx.guild.roles,name=role)
        em = get(ctx.guild.emojis,name=react)
        if rl == None:
            out = f'I\'m sorry {ctx.author.mention} but I couldn\'t find a role called "{role}"'
        if em == None:
            if out == '':
                out = f'I\'m sorry {ctx.author.mention} but I couldn\'t find an emoji called ":{react}:".\nMake sure that the reaction is a custom emoji and not a default emoji'
            else:
                out += f' or an emoji called ":{react}:".\nMake sure that the reaction is a custom emoji and not a default emoji'
        elif out == '':
            try:
                exists = False
                tmprl = list(self.roleData.values())
                tmpem = list(self.roleData.keys())
                if role in tmprl:
                    exists = True
                    out = 'This role is already on the list for autoassign roles'
                elif react in tmpem:
                    rlnew = get(ctx.guild.roles,name=self.roleData[react])
                    if rlnew != None:
                        out = f'This reaction is already being used for the role {rlnew.mention}'
                        exists = True
                if exists == False:
                    try:
                        with open(f'{PATH}\\config\\roles.json','r') as f:
                            data = json.load(f)
                        data['roles'].append({"role name": role,"reaction": react})
                        with open(f'{PATH}\\config\\roles.json','w') as f:
                            json.dump(data,f,indent=4)
                    except:
                        ConsoleMessage(f'{ctx.author} used .addrole but file was missing.')
                        data = {'message id': 0,'channel id': 0,'message':'Hey @everyone!\nPlease react to this message if you would like access to other parts of the server with the reactions shown below! :smile:\n','roles':[{"role name": role,"reaction": react}]}
                        with open(f'{PATH}\\config\\roles.json','w') as f:
                            json.dump(data,f,indent=4)
                        ConsoleMessage('Missing file "config/roles.json" successfully generated')
                    out = f'Successfully added the role {rl.mention} to the reaction {em}'
                    ConsoleMessage(f'{ctx.author} added "{role}" as an assignable role with reaction ":{react}:"')
                    self.roleData[react] = role
            except Exception as e:
                ErrorLog(e)
        await ctx.send(out)

    @addrole.error
    async def addrole_error(self,ctx,error):
        await ctx.send(f'Sorry {ctx.author.mention} but I don\'t think I understood\n Use: `.addrole reaction role` to assign a reaction to let users autoassign to this role')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rolemessage(self,ctx,*,msg):
        try:
            with open(f'{PATH}\\config\\roles.json','r') as f:
                data = json.load(f)
            data['message'] = msg
            with open(f'{PATH}\\config\\roles.json','w') as f:
                json.dump(data,f,indent=4)
            out = 'Message successfully changed!'
            ConsoleMessage(f'{ctx.author} changed the .rolemessage to "{msg}"')
        except Exception as e:
            ErrorLog(e)
        await ctx.send(out)

    @rolemessage.error
    async def rolemessage_error(self,ctx,error):
        await ctx.send('Requirements for message: `.rolemessage message`')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removerole(self,ctx,role):
        if role.startswith('<@&') and role.endswith('>') and len(role) == 22:
            role = role[3:]
            tmp = get(ctx.guild.roles,id=int(role[:-1]))
            if tmp != None:
                role = tmp.name
        found = False
        for react,rl in self.roleData.items():
            if role == rl:
                del self.roleData[react]
                found = True
                break
        if found:
            try:
                with open(f'{PATH}\\config\\roles.json','r') as f:
                    data = json.load(f)
                rolenames = list(self.roleData.values())
                reactnames = list(self.roleData.keys())
                data['roles'] = []
                for i in range(len(rolenames)):
                    data['roles'].append({'role name':rolenames[i],'reaction':reactnames[i]})
                with open(f'{PATH}\\config\\roles.json','w') as f:
                    json.dump(data,f,indent=4)
                rl = get(ctx.guild.roles,name=role)
                if rl != None:
                    out = f'Successfully removed {rl.mention} from the self assigning list'
                else:
                    out = f'Successfully removed {role} from the self assigning list'
                ConsoleMessage(f'{ctx.author} removed "{role}" as an assignable role')

            except Exception as e:
                ErrorLog(e)
        else:
            rl = get(ctx.guild.roles,name=role)
            if rl != None:
                out = f'I\'m sorry {ctx.author.mention} but the role {rl} doesn\'t appear to be assigned to anything'
                ConsoleMessage(f'{ctx.author} attempted to remove {role}" as an assignable role but it does not appear to be on the list')

            else:
                out = f'I\'m sorry {ctx.author.mention} but the role {role} doesn\'t appear to be assigned to anything'
                ConsoleMessage(f'{ctx.author} attempted to remove {role}" as an assignable role but it does not appear to exist')
        await ctx.send(out)

    @removerole.error
    async def removerole_error(self,ctx,error):
        await ctx.send(f'Sorry {ctx.author.mention} but I don\'t think I understood\n Use: `.removerole role` to prevent users from auto assigning as this role')

#adds extension to client when called
def setup(client):
    client.add_cog(Roles(client))
