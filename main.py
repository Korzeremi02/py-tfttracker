import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members =True

bot = commands.Bot(command_prefix='!', intents=intents)

riot_key = os.getenv("RIOT_KEY")
discord_key = os.getenv("DISCORD_KEY")

user_data = {}

# Faire help et init

@bot.command()
async def helpme(ctx,):
    await ctx.send(f"Aide TeamTracker \n\nCommandes : \n**!helpme @TeamTracker** : Afficher aide bot TT \n**!ping @TeamTracker** : Ping TT \n**!define @MentionDiscord NomUtilisateurRiot Region @TeamTracker** : Ajouter utilisateur discord dans TT \n**!display @TeamTracker** : Afficher utilisateur TT \n**!erase @TeamTracker** : Effacer mémoire TT \n**!stats @MentionDiscord @TeamTracker** : Afficher stats actuelles mention Discord ")

@bot.command()
async def ping(ctx):
  await ctx.send(f"TftTracker est bien opérationnel !")

@bot.command()
async def define(ctx, member: discord.Member, riot_name: str, region: str):
    user_data[member.id] = {"riot_name": riot_name, "region": region}
    await ctx.send(f"{member.display_name} : Riot username = {riot_name}; Region = {region}")

@bot.command()
async def display(ctx):
    await ctx.send(user_data)

@bot.command()
async def erase(ctx):
    global user_data
    await ctx.send(f"Mémoire effacée !")
    user_data = {}

@bot.command()
async def stats(ctx, member: discord.Member):
    if member.id in user_data:
        data = user_data[member.id]
        await ctx.send(f"Informations pour {member.display_name} : Nom d'utilisateur Riot = {data['riot_name']}, Région = {data['region']}")
    else:
        await ctx.send(f"Aucune information trouvée pour {member.display_name}. \nMerci de l'ajouter via la commande suivante : \n**!define @Mention NomUtilisateurRiot Region @TeamTracker**")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!helpme @TeamTracker"))
    print(f"Bot connecté en tant que {bot.user.name} ({bot.user.id})")

bot.run(discord_key)