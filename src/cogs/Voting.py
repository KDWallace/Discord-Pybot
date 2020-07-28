import discord, json, os
from datetime import datetime
from main import ConsoleMessage, ErrorLog, has_channel_perms, add_usage, PATH
from discord.ext import commands

class Voting(commands.Cog):
    #initialises object with client from main
    def __init__(self, client):
        self.client = client

    #function for creating a new poll
    def createpolljson(self,ctx, question, limit, options):
        #if the file already exists, there is an ongoing poll and this new one will be ignored
        if os.path.isfile(f'{PATH}\\data\\polls\\poll{ctx.channel.id}.json'):
            return False
        #initialises a dicitonary that will be saved as a json
        out = {}
        out['question'] = question
        out['author'] = str(ctx.author)
        out['authorID'] = ctx.author.id
        out['started'] = str(datetime.now().strftime("%d-%m-%Y %H;%M;%S"))
        out['limit'] = int(limit)
        out['total votes'] = 0
        out['options'] = []
        out['voters'] = []
        #creates a new dictionary within a list for every option in the poll
        for item in options:
            new_dict = {}
            new_dict['name'] = item
            new_dict['votes'] = 0
            out['options'].append(new_dict)

        #will create a new poll with the new data created in the dictionary
        with open(f'{PATH}\\data\\polls\\poll{ctx.channel.id}.json','w') as f:
            json.dump(out, f, indent=4)
        return True

    #commands
    @commands.command(aliases=['startvote'],description='Allows for polls to be created. Use ".+" to separate options\n\nExample: .startpoll "Question here" 2 Yes.+No.+I don\'t know.+Maybe\n\nThis would give users the ability to vote for up to 2 different options')
    @commands.has_permissions(administrator=True)
    @commands.check(has_channel_perms)
    async def startpoll(self, ctx, question, limit, *, options):
        #This chunk of code is entirelly for common typos and users trying to mess with formatting
        question.replace('`','')
        question.replace('\n',' ')
        question.replace('\t',' ')
        #question = ' '.join(question)
        options.replace('`','')
        options.replace('\t',' ')
        options.replace('\n',' ')
        #options = ' '.join(options)
        if options.endswith('.+'):
            options = options[:-2]
        if options.endswith(' .+'):
            options = options[:-3]
        if options.startswith('.+'):
            options = options[2:]
        if options.startswith(' .+'):
            options = options[3:]

        #if the maxumum vote limit is set to 0 or below, a message is sent and the function ends
        if int(limit) < 1:
            await ctx.send(f'Hmmm...I think that people might want more than {limit} votes :sweat_smile:')
            return
        #opts = []
        out = f'@everyone\nPoll started by {ctx.author.mention}:\n\n{question}'
        #tmp = options.split('.+')
        i = 1
        opts = options.split('.+')
        for item in opts:#tmp::
            if item.isspace():
                del item
                pass
            out += f'\n\t`.vote {i}` for `{item}`'
        #    opts.append(item)
            i += 1
        if len(opts) <= 1:#tmp) <= 1:
            await ctx.send(f'Hmmm...I think people like more options than that')
            return
        if int(limit) > len(opts):
            limit = str(len(opts))
        out += f'\n\n(Note: you are only allowed {limit} '
        if int(limit) == 1:
            out += 'vote)'
        else:
            out += 'votes)'
        out += '\nTo see percentages for votes, type `.pollstats`\nTo see your previous votes in this poll, type `.myvotes`'
        if self.createpolljson(ctx, question, limit, opts):
            ConsoleMessage(f'{ctx.author} has created a new poll: "{question}" in #{ctx.channel.name} with options: {opts}')
            await ctx.message.delete()
            await ctx.send(out)
            add_usage("polls started")
        else:
            await ctx.message.delete()
            await ctx.send(f'Sorry {ctx.author.mention}, but there is still an ongoing poll in this channel. You can cancel it with .pollend')

    @startpoll.error
    async def startpoll_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            ConsoleMessage(f'{ctx.author} failed to use .startpoll in #{ctx.channel}')
        else:
            await ctx.send(f'Sorry {ctx.author.mention}, but I don\'t think I understand you. Try .startpoll Question NumberOfVotesEach option1.+option2.+option3')

    #function called for starting a new poll with the command
    @commands.command()
    @commands.check(has_channel_perms)
    async def pollstats(self, ctx):
        with open(f'{PATH}\\data\\polls\\poll{ctx.channel.id}.json', 'r') as f:
            stats = json.load(f)
        out = f'Current Poll by <@!{stats["authorID"]}>\nQuestion: {stats["question"]}\n'
        for item in stats["options"]:

            out += f'`{item["name"]}`: `{item["votes"]} vote'
            if item["votes"] != 1:
                 out += 's'
            if stats["total votes"] > 0:
                out += f' ({round(item["votes"]*100/stats["total votes"],2)}%)`\n'
            else:
                out += ' (0.0%)`\n'
        out += f'\nType `.myvotes` to see your previous votes'
        await ctx.send(f'{ctx.author.mention}\n{out}')

    @pollstats.error
    async def pollstats_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            ConsoleMessage(f'{ctx.author} attempted to use .pollstats in #{ctx.channel}')
        else:
            await ctx.send(f'There doesn\'t seem to be any active polls in this channel {ctx.author.mention}. If you have any suggestions then feel free to put them in #suggestions')

    #command that will send a private message to the user from the bot informing of their current votes
    @commands.command()
    async def myvotes(self, ctx):
        with open(f'{PATH}\\data\\polls\\poll{ctx.channel.id}.json', 'r') as f:
            stats = json.load(f)
        for voter in stats["voters"]:
            if ctx.author.id == voter["id"]:
                out = f'Hi {ctx.author.mention}! :smile:\nYour votes for "{stats["question"]}" in {ctx.channel.mention} were:'
                choices = sorted(voter["choices"])
                for i in choices:
                    out += f'\n\t`Option {i}`: {stats["options"][i-1]["name"]}'
                out += f'\n\nTo see how the vote is going, type `.pollstats` in {ctx.channel.mention}!'
                await ctx.author.send(out)
                return

    @myvotes.error
    async def myvotes_error(self, ctx, error):
        await ctx.send(f'You don\'t seem to be voting in any active polls in this channel {ctx.author.mention}. If you have any suggestions then feel free to put them in #suggestions')

    @commands.command()
    @commands.check(has_channel_perms)
    async def vote(self, ctx, *,value):
        if value.lower() == 'a real number' or value.lower() == 'real number':
            await ctx.send(f'Sorry {ctx.author.mention}, but you\'re not very funny')
            return
        try:
            with open(f'{PATH}\\data\\polls\\poll{ctx.channel.id}.json','r') as f:
                stats = json.load(f)
        except:
            await ctx.send(f'There doesn\'t seem to be any active polls in this channel {ctx.author.mention}. If you have any suggestions then feel free to put them in #suggestions')
            return
        try:
            val = int(value)
            if val < 1:
                await ctx.send(f'Sorry {ctx.author.mention}, but I don\'t think {val} is an actual option')
                return
        except:
            await ctx.send(f'Sorry {ctx.author.mention}, but you need to put a real number after the `.vote `')
            return
        userVoted = False
        for user in stats["voters"]:
            if user["id"] == ctx.author.id:
                userVoted = True
                for item in user["choices"]:
                    if item == val:
                        await ctx.send(f'Sorry {ctx.author.mention}, but you have already voted for this!')
                        return
                if len(user["choices"]) >= stats["limit"]:
                    await ctx.send(f'Sorry {ctx.author.mention}, but it looks like you have used the maximum number of votes for this poll!')
                    return
                else:
                    try:
                        stats["options"][val-1]["votes"] += 1
                        user["choices"].append(val)
                        break
                    except:
                        await ctx.send(f'Sorry {ctx.author.mention}, but there isn\'t really a number {val} option.\nHere, have a look at what\'s avaliable with `.pollstats`')
                        return
        if userVoted == False:
            try:
                stats["options"][val-1]["votes"] += 1
                voter = {}
                voter["name"] = str(ctx.author)
                voter["id"] = ctx.author.id
                voter["choices"] = [val]
                stats["voters"].append(voter)
            except:
                await ctx.send(f'Sorry {ctx.author.mention}, but there isn\'t really a number {val} option.\nHere, have a look at what\'s avaliable with `.pollstats`')
                return
        stats["total votes"] += 1
        with open(f'{PATH}\\data\\polls\\poll{ctx.channel.id}.json','w') as f:
            json.dump(stats,f,indent=4)
            add_usage("total votes")
            await ctx.message.delete()
            ConsoleMessage(f'{ctx.author} voted for "{stats["options"][val-1]["name"]}" in poll for "{stats["question"]}" on channel #{ctx.channel.name}')
            await ctx.send(f'Thank you for voting {ctx.author.mention}! :smile:')

    @vote.error
    async def vote_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            ConsoleMessage(f'{ctx.author} attempted to use .vote in #{ctx.channel}')
            await ctx.message.delete()
        else:
            await ctx.message.delete()

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.check(has_channel_perms)
    async def endpoll(self,ctx):
        voted = False
        try:
            with open(f'{PATH}\\data\\polls\\poll{ctx.channel.id}.json','r') as f:
                stats = json.load(f)
        except:
            await ctx.send(f'There doesn\'t seem to be any active polls in this channel {ctx.author.mention}.')
            return
        stats["finished"] = str(datetime.now().strftime("%d-%m-%Y %H;%M;%S"))
        stats["Ending Author"] = str(ctx.author)
        stats["Ending AuthorID"] = ctx.author.id
        with open(f'{PATH}\\data\\polls\\archived polls\\poll {stats["started"]} #{ctx.channel}.json','w') as f:
            json.dump(stats,f,indent=4)
        os.remove(f'{PATH}\\data\\polls\\poll{ctx.channel.id}.json')
        ConsoleMessage(f'{ctx.author} has ended the poll for {stats["question"]} in #{ctx.channel}')

        out = f'Hey @everyone!\nThe poll `{stats["question"]}` has ended!\nThe results are:'
        for item in stats["options"]:
            if item["votes"] != 0:
                voted = True
            out += f'\n\t\t`{item["name"]}` with {item["votes"]} '
            if item["votes"] == 1:
                out += 'vote!'
            else:
                out += 'votes!'
        if voted:
            add_usage("polls ended with votes")
            out += '\n\nThank you everyone for voting! :smile:'
        else:
            add_usage("polls ended without votes")
            out += '\n\nLooks like nobody wanted to vote today... :cry:'
        await ctx.send(out)

    @endpoll.error
    async def endpoll_error(self,ctx,error):
        if isinstance(error, commands.CheckFailure):
            ConsoleMessage(f'{ctx.author} attempted to use .endpoll in #{ctx.channel}')
        else:
            ErrorLog(error)

def setup(client):
    client.add_cog(Voting(client))
