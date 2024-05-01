# IMPORT PKG
import discord
import os
import requests
from discord.ext import commands, tasks
from discord import File
from dotenv import load_dotenv
from easy_pil import Editor, load_image_async, Font
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import asyncio

# PARAMS
load_dotenv()
intents = discord.Intents.default()
intents.members =True
bot = commands.Bot(command_prefix='/', intents=intents)

# KEYS
riot_key = os.getenv("RIOT_KEY")
discord_key = os.getenv("DISCORD_KEY")

# INIT DICTIONARIES
user_id = {}
user_secret = {}
user_data = {}
user_profile = {}

# ON BOT STARTUP, DO...
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="/help"))
    # autoTracker.start()
    synced = await bot.tree.sync()
    print(f"Synchronisation de {len(synced)} commandes")

# HELP CMD
@bot.tree.command(name="help", description="Afficher l'aide du bot TeamTracker")
async def helpme(interaction):
    try:
        await interaction.response.send_message(f"Aide TeamTracker \n\nCommandes : \n**/helpme ** : Afficher aide bot TT \n**/ping ** : Ping TT \n**/define ** : Ajouter utilisateur discord dans TT \n**/display ** : Afficher utilisateur TT \n**/erase ** : Effacer mémoire TT \n**/infos** : Afficher stats actuelles mention Discord ")
    except:
        await interaction.response.send_message(f"Erreur lors de l'affichage de l'aide")

# PING CMD
@bot.tree.command(name="ping", description="Effectuer un ping vers le bot TeamTracker")
async def ping(interaction):
    try:
        await interaction.response.send_message(f"TftTracker est bien opérationnel !")
    except:
        await interaction.response.send_message(f"Erreur lors du ping")

# DEFINE CMD
@bot.tree.command(name="define", description="Ajouter un utilisateur Discord à TeamTracker")
async def define(interaction, member: discord.Member, riot_name: str, tag: str, region: str, status: bool):
    try:
        global user_secret
        if status != False:
            status = False
        user_data[member.id] = {"riot_name": riot_name, "tag": tag, "region": region, "status": status}
        try:
            puid = 'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/' + riot_name + "/" + tag + '?api_key=' + riot_key
            res = requests.get(puid, timeout = 127)
            user_secret[member.id] = [dict(res.json())]
        except:
            interaction.response.send_message(f"Erreur lors de la requete API pour user_secret")
        try:
            puid = user_secret[member.id][0]['puuid']
        except:
            interaction.response.send_message(f"Erreur lors de la manipulation du PUUID RIOT")
        try:
            id = 'https://euw1.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/' + puid + '?api_key=' + riot_key
            res2 = requests.get(id, timeout=127)
            user_id[member.id] = [dict(res2.json())]
        except:
            interaction.response.send_message(f"Erreur lors de la requete API pour user_id")
        try:
            username = member.name
            user_id[member.id][0]["discord_member"] = username
        except:
            interaction.response.send_message(f"Erreur lors de l'ajout du nom utilisateur Discord dans user_id")
        try:
            user_secret = {}
        except:
            interaction.response.send_message(f"Erreur lors de la suppression de la lib user_secret")
        try:
            await interaction.response.send_message(f"Id du membre Discord : {member.display_name} \nRiot username = {riot_name}\nTag = {tag}\nRegion = {region}\nStatus = {status}")
        except:
            interaction.response.send_message("Erreur lors de l'envoie du message de la commande define")
    except:
        interaction.response.send_message("Erreur majeure lors de l'ajout de la mention Discord")

# IMAGE CMD
@bot.tree.command(name="image", description="Image")
async def image(interaction, member: discord.Member):
    # print("user_profile")
    # print(user_profile)
    # print("user_id")
    # print(user_id)
    # print("user_data")
    # print(user_data)
    # print("user_secret")
    # print(user_secret)
    id = user_id[member.id][0]['id']
    profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
    res = requests.get(profile_data, timeout=127)
    user_profile = res.json()
    print(user_data[member.id]["riot_name"])
    print(user_profile)
    for profile in user_profile:
        if profile["queueType"] == "RANKED_TFT":
            ranked_profile = profile
            break
    else:
        await interaction.response.send_message("Profil RANKED_TFT introuvable.")
        return
    totalGame = str(ranked_profile['wins'] + ranked_profile['losses'])
    winGame = str(ranked_profile['wins'])
    topGame = str(ranked_profile['wins'] / int(totalGame) * 100)
    label = ImageFont.truetype("./assets/fonts/inter.ttf", 38)
    userfont = ImageFont.truetype("./assets/fonts/inter.ttf", 50)
    descfont = ImageFont.truetype("./assets/fonts/inter.ttf", 42)
    card = Editor("./assets/png/card.png")
    card.text((90,730), text=totalGame, color="#ffffff", font=label)
    card.text((270,730), text=winGame, color="#ffffff", font=label)
    card.text((405,730), text=topGame, color="#ffffff", font=label)
    card.text((95,500), text=f"{user_data[member.id]['riot_name']}#{user_data[member.id]['region']}", color="#ffffff", font=userfont)
    card.text((110,580), text=f"{ranked_profile['tier']} {ranked_profile['rank']} {ranked_profile['leaguePoints']} LP", color="#ffffff", font=descfont)
    card.rectangle((50,190),width=480,height=260,fill="red")
    card.ellipse((230,50),width=120,height=120,fill="blue")
    file = File(fp=card.image_bytes, filename="pic.png")
    await interaction.response.send_message(file=file)

# SHOWSECRET CMD
@bot.tree.command(name="showsecret", description="show")
async def showsecret(interaction):
    try:
        await interaction.response.send_message(user_secret)
    except:
        interaction.response.send_message(f"Erreur lors de l'affichage de user_secret")

# DISPLAY CMD
@bot.tree.command(name="display", description="Afficher les données de TftTracker")
async def display(interaction):
    try:
        await interaction.response.send_message(user_data)
    except:
        interaction.response.send_message("Erreur lors de l'affichage des données avec cmd display")

# ERASE CMD
@bot.tree.command(name="erase", description="Effacer les données de TeamTracker (DEBUG)")
async def erase(interaction):
    try:
        global user_data
        await interaction.response.send_message(f"Mémoire effacée !")
        user_data = {}
    except:
        interaction.response.send_message("Erreur lors de la suppresion de user_data")

# INFOS CMD
@bot.tree.command(name="infos", description="Afficher les statistiques générales de la mention")
async def infos(interaction, member: discord.Member):
    try:
        try:
            id = user_id[member.id][0]['id']
        except:
            interaction.response.send_message(f"Erreur lors de la définition de l'ID")
        try:
            profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
            res = requests.get(profile_data, timeout=127)
            user_profile = res.json()
        except:
            interaction.response.send_message(f"Erreur lors de la requete API pour la récupération et/ou l'affichage des infos")
        for item in user_profile:
            temp_dict = {
                "queueType": item["queueType"],
                "tier": item["tier"],
                "rank": item["rank"],
                "leaguePoints": item["leaguePoints"],
                "wins": item["wins"],
                "losses": item["losses"]
            }
        await interaction.response.send_message(temp_dict)
    except:
        interaction.response.send_message(f"Erreur de récupération et/ou affichage infos joueur")

# INFOSDOUBLEUP CMD
@bot.tree.command(name="infosdoubleup", description="Afficher les statistiques générales de la mention")
async def infosdoubleup(interaction, member: discord.Member):
    try:
        try:
            id = user_id[member.id][0]['id']
        except:
            interaction.response.send_message(f"Erreur lors de la définition de l'ID")
        try:
            profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
            res = requests.get(profile_data, timeout=127)
            user_profile = res.json()
        except:
            interaction.response.send_message(f"Erreur lors de la requete API pour la récupération et/ou l'affichage des infos")
        for item in user_profile:
            temp_dict = {
                "queueType": item["queueType"],
                "tier": item["tier"],
                "rank": item["rank"],
                "leaguePoints": item["leaguePoints"],
                "wins": item["wins"],
                "losses": item["losses"]
            }
            await interaction.response.send_message(temp_dict)
    except:
        interaction.response.send_message(f"Erreur de récupération et/ou affichage infos joueur")

# INGAME CMD
@bot.tree.command(name="ingame", description="Voir les joueurs ingame")
async def ingame(interaction):
    ladder = []
    players = []
    ingame = []
    compt = 0

    for user_key in user_id.keys():
        temp = []
        name = user_id[user_key][0]["discord_member"]
        puuid = user_id[user_key][0]["puuid"]

        temp.append(name)
        temp.append(puuid)
        players.append(temp)

    for player in players:
        current = 'https://euw1.api.riotgames.com/lol/spectator/tft/v5/active-games/by-puuid/' + player[1] + '?api_key=' + riot_key
        res = requests.get(current, timeout = 127)
        res = [dict(res.json())]

        try:
            message = res[0]['status']['message']
        except KeyError:
            message = res[0]['gameId']

        if message == "Data not found - spectator game info isn't found":
            ingame.append(player[0])
            ingame.append(False)
        else :
            ingame.append(player[0])
            ingame.append(True)
            compt += 1

    await interaction.response.send_message(ingame)

# LADDER CMD
@bot.tree.command(name="ladder", description="Classement des joueurs")
async def ladder(interaction):
    ladder = []
    compt = 0
    for user_key in user_id.keys():
        id = user_id[user_key][0]["id"]
        profile_data = 'https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/' + id + '?api_key=' + riot_key
        res = requests.get(profile_data, timeout=127)
        user_profile = res.json()

        temp = []
        temp.append(str(user_id[list(user_id.keys())[compt]][0]["discord_member"]).capitalize())
        temp.append(str(user_profile[-1]['tier']))
        temp.append(str(user_profile[-1]['rank']))
        temp.append(str(user_profile[-1]['leaguePoints']) + " LP")
        ladder.append(temp)
        compt += 1


    division_order = {'CHALLENGER': 10, 'GRANDMASTER': 9, 'MASTER': 8, 'DIAMOND': 7, 'EMERALD': 6, 'PLATINUM': 5, 'GOLD': 4, 'SILVER': 3, 'BRONZE': 2, 'IRON': 1}

    def custom_sort(player):
        division_rank = division_order.get(player[1], 0)
        division_level = {'I': 4, 'II': 3, 'III': 2, 'IV': 1}.get(player[2], 0)
        lp = int(player[3].split()[0])
        return (division_rank, division_level, lp)

    sorted_ladder = sorted(ladder, key=custom_sort, reverse=True)
    await interaction.response.send_message(sorted_ladder)

# GAME CMD
@bot.tree.command(name="game", description="Afficher les statistiques générales de la mention")
async def game(interaction, member: discord.Member):
    puuid = user_id[member.id][0]['puuid']
    current = f"https://euw1.api.riotgames.com/lol/spectator/tft/v5/active-games/by-puuid/{puuid}?api_key={riot_key}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(current) as response:
            res = await response.json()

        if 'status' in res:
            message = res['status'].get('message')
            if message:
                await interaction.response.send_message(f"{user_id[member.id][0]['discord_member'].capitalize()} n'est actuellement pas en game !")
        else:
            players_ingame = []
            tasks = []
            for participant in res['participants']:
                player_id = participant['summonerId']
                task = asyncio.create_task(get_player_info(session, riot_key, player_id))
                tasks.append(task)

            player_infos = await asyncio.gather(*tasks)

            for participant, info in zip(res['participants'], player_infos):
                temp = [
                    participant['riotId'],
                    info[0]['tier'],
                    info[0]['rank'],
                    f"{info[0]['leaguePoints']} LP"
                ]
                players_ingame.append(temp)

            print(players_ingame)
            await interaction.response.send_message(players_ingame)

async def get_player_info(session, riot_key, player_id):
    url = f"https://euw1.api.riotgames.com/tft/league/v1/entries/by-summoner/{player_id}?api_key={riot_key}"
    async with session.get(url) as response:
        return await response.json()

# MATCHES CMD
@bot.tree.command(name="matches", description="Afficher les détails de la dernière partie jouée par le joueur")
async def matches(interaction, member: discord.Member, last: int):
    puuid = user_id[member.id][0]['puuid']
    matches_url = f"https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count=10&api_key={riot_key}"

    async with aiohttp.ClientSession() as session:
        async with session.get(matches_url) as response:
            matches_array = await response.json()

    match_details_url = f"https://europe.api.riotgames.com/tft/match/v1/matches/{matches_array[last]}?api_key={riot_key}"

    async with aiohttp.ClientSession() as session:
        async with session.get(match_details_url) as response:
            match_details = await response.json()

    participant_data = get_participant_data(match_details, puuid)
    participant_info = extract_participant_info(participant_data)

    print(participant_info)
    # await interaction.response.send_message(participant_info)
    await interaction.response.send_message("Data trop longue ! Check ton terminal.")

def get_participant_data(data, puuid):
    for participant in data['info']['participants']:
        if participant['puuid'] == puuid:
            return participant
    return None

def extract_participant_info(participant_data):
    extracted_info = {
        "augments": participant_data["augments"],
        "level": participant_data["level"],
        "placement": participant_data["placement"],
        "traits": participant_data["traits"],
        "units": participant_data["units"]
    }
    return extracted_info


# @tasks.loop(seconds = 60)
# async def autoTracker():
#     print("autoTracker")


bot.run(discord_key)

# ------------------------------------------------------------------------------------------

# Si les joueurs sont en game, alors afficher les datas de manière automatique sans commandes