# bot.py

import os
import discord
import random
import json
import matplotlib.pyplot as plt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()

PARTICIPANT_EMOJI = '👍'
START_EMOJI = '✅'
LOCK_EMOJI = '🔒'

STATS_IMAGE_NAME = "stats.png"

allowed_emoji = [PARTICIPANT_EMOJI, START_EMOJI, LOCK_EMOJI]

stats = {}
try:
    with open('stats.json') as json_file:
        stats = json.load(json_file)
except:
    pass


def generate_stat_plot():
    with open('stats.json') as json_file:
        stats = json.load(json_file)
        player_stats = {}

        for game_id in stats.keys():
            for player in stats[game_id]["players"]:
                if player in player_stats:
                    player_stats[player]["total_rerolls"] += stats[game_id]["number_of_rerolls"]
                    player_stats[player]["total_game"] += 1
                    player_stats[player]["max_rerolls"] = max(player_stats[player]["max_rerolls"], stats[game_id]["number_of_rerolls"])
                else:
                    player_stats[player] = {}
                    player_stats[player]["total_game"] = 1
                    player_stats[player]["total_rerolls"] = stats[game_id]["number_of_rerolls"]
                    player_stats[player]["max_rerolls"] = stats[game_id]["number_of_rerolls"]
        player_names = list(player_stats.keys())
        player_rerolls = []
        player_games = []
        player_average = []
        player_max = []
        for name in player_names:
            player_rerolls.append(player_stats[name]["total_rerolls"])
            player_games.append(player_stats[name]["total_game"])
            player_average.append(player_stats[name]["total_rerolls"] * 1.0 / player_stats[name]["total_game"])
            player_max.append(player_stats[name]["max_rerolls"])

        fig, axs = plt.subplots(2, 2)
        axs[0, 0].set_title("Total rerolls")
        axs[0, 0].bar(player_names,player_rerolls)

        axs[0, 1].set_title("Total games")
        axs[0, 1].bar(player_names,player_games)

        axs[1, 0].set_title("Average rerolls")
        axs[1, 0].bar(player_names,player_average)

        axs[1, 1].set_title("Longest rerolls")
        axs[1, 1].bar(player_names,player_max)
        fig.tight_layout()
        fig.savefig(STATS_IMAGE_NAME)
        return discord.File(STATS_IMAGE_NAME)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '/loi-stats':
        print("{} called stats".format(message.author))
        try:
            discord_file = generate_stat_plot()
        except Exception as e:
            print(e)
            await message.channel.send(content="Stats are non existants")
            return
        await message.channel.send(file=discord_file)
        return

    if message.content == '/loi-rules':
        print("{} called rules".format(message.author))
        content = ("Règlement d'une loi :\n"
                    "\t- Une loi se termine seulement lors d'une victoire (victoire n'inclus pas un remake)\n"
                    "\t- Il n'est pas possible de quitter un loi\n"
                    "\t- Invade obligatoire\n"
                    "\t- Les rôles sont choisi avant une queue et aucun swap est accepté"
                    "\t- Le Jungle doit avoir smite, le Support doit acheter l'item support \n"
                    "\t- FF = ban à vie des lois\n"
                    "\t- Le personnage doit être choisis à l'aide du bouton aléatoire du client, aucun reroll accepté\n"
                    "\t- Le metton est l'un des calls les plus respecté\n"
                    "\t- Avec un accord des 5 membres une pause collation/souper/meditation/hydratation peut être prise, mais la loi doit se reprendre immédiatement après")
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

    print("{} reacted {} at game id {}".format(user, reaction.emoji, reaction.message.id ))

    lock_reactions =list(filter(lambda x: x.emoji == LOCK_EMOJI , reaction.message.reactions))[0]

    if reaction.emoji != LOCK_EMOJI and lock_reactions.count > 1:
        print("game id {} is locked".format( reaction.message.id ))
        await reaction.remove(user)
        return

    if reaction.emoji == START_EMOJI and lock_reactions.count < 2:
        
        
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