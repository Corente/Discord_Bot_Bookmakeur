import discord, os, asyncio, schedule
from toolbox import get_total, show_bet, end_bet_message, apply_gain, load, save
from bet import Bet
from datetime import date, time, datetime
from discord.ext import commands

#Placer le token dans un fichier token.txt
f = open("token.txt", "r")
TOKEN = f.read()
f.close()

description = '''Le bot des Bets'''
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='*', description=description ,ntents=intents)


#La reserve d'agent des joueurs, sous forme de pairs (id, argent)
Banque = {}
#Le nom de la money default "$"
logo_argent = "$"
#Le lien pour acceder au code source
github = "https://github.com/Corente/Discord_Bot_Bookmakeur"
#Le bet en cours
current_bet = {}
#Le fichier de sauvegarde
path = "sauvegardes"


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Faire des paris endiablés'))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    global Banque
    Banque = load(path)
    print(Banque)

#Fonction qui ajoute tous les jours de l'argents aux users inscrits
async def daily_money():
    await bot.wait_until_ready()
    while not bot.is_closed():
        global Banque
        if (datetime.now().time().minute == 0):
            for i in Banque:
                for j in Banque[i]:
                    Banque[i][j] += 25
            t = 45
        else:
            t = 1
        await asyncio.sleep(t)

#Fonction reduit le temps pour le bet en cours
async def durée_bets():
    await bot.wait_until_ready()
    while not bot.is_closed():
        global current_bet
        for i in current_bet:
            if (current_bet[i].durée > 0):
                current_bet[i].durée -= 1
        t = 55
        await asyncio.sleep(t)

#Fonction qui sauvegarde la banque dans un fichier
async def sauvegarde():
    await bot.wait_until_ready()
    while not bot.is_closed():
        global Banque
        now = datetime.strftime(datetime.now(),'%H:%M')
        if (now == '23:42' or now == '11:42' or now == '18:42'):
            save(path, Banque)
            t = 60
        else:
            t = 1
        await asyncio.sleep(t)

@bot.command()
async def inscription(ctx):
    """T'ajoute au systeme de bet avec 100$ si tu n'es pas dedant"""
    global Banque
    if (ctx.message.author.guild.id not in Banque):
        Banque[ctx.message.author.guild.id] = {}
        Banque[ctx.message.author.guild.id][ctx.message.author.id] =  100
        await ctx.send("Bienvenue Au casino")
    elif (ctx.message.author.id not in Banque[ctx.message.author.guild.id]):
        Banque[ctx.message.author.guild.id][ctx.message.author.id] =  100
        await ctx.send("Bienvenue Au casino")
    else:
        await ctx.send("Tu es deja au casino")

@bot.command()
async def mon_argent(ctx):
    """Donne ton argent perso"""
    global Banque
    if (ctx.message.author.guild.id not in Banque or ctx.message.author.id not in Banque[ctx.message.author.guild.id]):
        await ctx.send("Tu n'es pas inscrit au casino")
    else:
        global logo_argent
        argent = Banque[ctx.message.author.guild.id][ctx.message.author.id]
        message = "Bravo " + ctx.message.author.name + " tu as " + str(argent) + " " + logo_argent
        await ctx.send(message)

@bot.command()
async def leaderboard(ctx):
    """Affiche les plus Blindaxxx"""
    global Banque
    global logo_argent

    if (ctx.message.author.guild.id not in Banque):
        await ctx.send("Personne n'est incrit ici :'(")
        return

    copie = Banque[ctx.message.author.guild.id].copy()
    tab = sorted(copie, key=copie.get, reverse=True)[:3]

    embed=discord.Embed(title="Learderboard de la thunas", description="quiquicest qui a le plus d'argent", color=0x87f500)
    embed.set_thumbnail(url="https://i.kym-cdn.com/photos/images/newsfeed/001/499/826/2f0.png")
    if (len(tab) >= 1):
        user = await ctx.guild.fetch_member(tab[0])
        money = str(Banque[ctx.message.author.guild.id][tab[0]]) + logo_argent
        embed.add_field(name=user.name, value=money, inline=False)
    if (len(tab) >= 2):
        user = await ctx.guild.fetch_member(tab[1])
        money = str(Banque[ctx.message.author.guild.id][tab[1]]) + logo_argent
        embed.add_field(name=user.name, value=money, inline=False)
    if (len(tab) >= 3):
        user = await ctx.guild.fetch_member(tab[2])
        money = str(Banque[ctx.message.author.guild.id][tab[2]]) + logo_argent
        embed.add_field(name=user.name, value=money, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def start_bet(ctx, sujet="", option1="", option2="", durée=""):
    """Commence un bet avec sujet option1, option, durée (en minute)"""
    global current_bet
    if (sujet == "" or option1 == "" or option2 == "" or durée == ""):
        await ctx.send("Il manque des arguments")
    elif (ctx.message.author.guild.id in current_bet):
        await ctx.send("Un bet est deja en cours !")
    elif (ctx.message.author.guild.id not in Banque):
        await ctx.send("Il manque des joueurs dans ce serveur, inscrivez vous !")
    else:
        current_bet[ctx.message.author.guild.id] = Bet(ctx.message.author.id, sujet, option1, option2, int(durée))
        await ctx.send("Le bet a été créer")

@bot.command()
async def bet_en_cours(ctx):
    """liste le bet en cours"""
    serveur_bet = current_bet[ctx.message.author.guild.id] if (ctx.message.author.guild.id in current_bet) else None
    await ctx.send(show_bet(serveur_bet)) 

@bot.command()
async def parier(ctx, option="", montant=""):
    """parie sur le bet en cours"""
    global current_bet
    global Banque
    if (option == "" or montant == ""):
        await ctx.send("Il manque des arguments")
        return
    m = int(montant)
    o = int(option)
    if (ctx.message.author.guild.id not in current_bet):
        await ctx.send("Il n'y a aucun bet en cours")
    elif (ctx.message.author.guild.id not in Banque or ctx.message.author.id not in Banque[ctx.message.author.guild.id]):
        await ctx.send("Tu n'es pas inscrit au casino")
    elif (Banque[ctx.message.author.guild.id][ctx.message.author.id] < m):
        await ctx.send("Tu n'as pas assez d'argent sale pauvre")
    elif (o != 1 and o != 2):
        await ctx.send("Ce n'est pas une option valide")
    else:
        message = current_bet[ctx.message.author.guild.id].parier(ctx.message.author.id , m, o, Banque[ctx.message.author.guild.id])
        await ctx.send(message)


@bot.command() 
async def stop_bet(ctx, option_gagnante = -1):
    """Arrete le bet en cours"""
    global current_bet
    global logo_argent
    if (option_gagnante == -1):
        await ctx.send("Il manque des arguments")
        return
    
    
    numero = int(option_gagnante)
    if (ctx.message.author.guild.id not in current_bet):
        await ctx.send("Il n'y a aucun bet en cours")
    elif (numero != 1 and numero != 2):
        await ctx.send("Ce n'est pas une option valide")    
    elif(ctx.message.author.id == current_bet[ctx.message.author.guild.id].id_proposeur or (current_bet[ctx.message.author.guild.id].durée < 1 and ctx.message.author.guild_permissions.administrator)):
            winners = current_bet[ctx.message.author.guild.id].fin(numero)
            serveur_bet = current_bet[ctx.message.author.guild.id]
            apply_gain(Banque[ctx.message.author.guild.id], winners, serveur_bet)
            message = end_bet_message(numero, serveur_bet, logo_argent)
            del current_bet[ctx.message.author.guild.id]
            await ctx.send(message)
    else:
        await ctx.send("Vous n'avez pas créer le pari vous ne pouvez pas le finir")

@bot.command()
async def change_money(ctx, signe=""):
    """Change le signe de l'argent"""
    global logo_argent
    if (signe == ""):
        await ctx.send("Il manque des arguments")
    elif (ctx.message.author.guild_permissions.administrator):
        logo_argent = signe
        await ctx.send("Le signe à été changé")
    else:
        await ctx.send("Demande à un adulte pour cela")
    
@bot.command()
async def credits(ctx):
    """Lien du code source"""
    await ctx.send(github)


bot.loop.create_task(daily_money())
bot.loop.create_task(durée_bets())
bot.loop.create_task(sauvegarde())
bot.run(TOKEN)
