# bot.py

import os
import discord
import random
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()

PARTICIPANT_EMOJI = '👍'
START_EMOJI = '✅'

allowed_emoji = [PARTICIPANT_EMOJI, START_EMOJI]

stats = {}
try:
    with open('stats.json') as json_file:
        stats = json.load(json_file)
except:
    pass



@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '/loi-stats':
        mes = await message.channel.send(content=json.dumps(stats))
        return

    if message.content == '/loi-rules':
        print("{} called rules".format(message.author))
        content = "Règlement d'une loi :\n"
        mes = await message.channel.send(content=content)
        return

    if message.content == '/loi':
        print("{} called loi".format(message.author))
        embed=discord.Embed(title="Loi des Norms", description="Attente de joueurs", color=0xe62828)
        mes = await message.channel.send(embed=embed)
        for emoji in allowed_emoji:
            await mes.add_reaction(emoji)
        await message.delete()
        return

@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return

    if len(reaction.message.embeds) != 1 or reaction.message.embeds[0].title != "Loi des Norms":
        return

    if reaction.emoji not in allowed_emoji:
        await reaction.remove(user)
        return

    if reaction.emoji == START_EMOJI:
        
        
        reroll_field = list(filter(lambda x: x.name == "Nombre de parties",  reaction.message.embeds[0].fields))
        if len(reroll_field) > 0:
            number_of_rerolls = int(reroll_field[0].value)
        else:
            number_of_rerolls = 0
        number_of_rerolls += 1
        embed=discord.Embed(title="Loi des Norms", color=0xe62828)
        all_reactions = list(filter(lambda x: x.emoji == PARTICIPANT_EMOJI , reaction.message.reactions))[0]
        players = []
        async for u in all_reactions.users():
            if u == client.user:
                continue
            players.append(u)

        if reaction.message.id not in stats:
            stats[reaction.message.id] = {} 
            stats[reaction.message.id]['timestamp'] = str(datetime.now())

        stats[reaction.message.id]['players'] = list(map(lambda x : x.name , players))
        stats[reaction.message.id]['number_of_rerolls'] = number_of_rerolls

        with open('stats.json', 'w') as outfile:
            json.dump(stats, outfile)

        while len(players) < 5:
            players.append(None)
        random.shuffle(players)
        embed.add_field(name="<:Top_icon:800219009580400650> Top", value="{}".format(players[0]), inline=False)
        embed.add_field(name="<:Jungle_icon:800219009555365943> Jungle", value="{}".format(players[1]), inline=False)
        embed.add_field(name="<:Middle_icon:800219009575288843> Mid", value="{}".format(players[2]), inline=False)
        embed.add_field(name="<:Bottom_icon:800219009588264981> ADC", value="{}".format(players[4]), inline=False)
        embed.add_field(name="<:Support_icon:800219009630732348> Sup", value="{}".format(players[3]), inline=False)
        embed.add_field(name="Nombre de parties", value="{}".format(number_of_rerolls), inline=False)

        await reaction.message.edit(content="",embed=embed)
        await reaction.remove(user)
        return

client.run(TOKEN)