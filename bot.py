import discord, os, asyncio, schedule
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
github = "https://github.com/Corente"
#Le bet en cours
current_bet = None


def get_total(tab):
    res = 0
    for key in tab:
        res += tab[key]
    return res

def find_richets():
    argent_max = 0
    id_max = 0
    for i in Banque:
        if (Banque[i] > argent_max):
            argent_max = Banque[i]
            id_max = i
    return (id_max, argent_max)

def show_bet():
    res = ""
    global current_bet
    if (current_bet == None):
        res =  "Il n'y a aucun bet en cours"
    else:
        res = "```Le bet en cours est: " + current_bet.sujet + "\n"
        res += "\t Option 1 : " + current_bet.sujet1 + " | Total sur ce pari = " + str(get_total(current_bet.bet1)) + "\n"
        res += "\t Option 2 : " + current_bet.sujet2 + " | Total sur ce pari = " + str(get_total(current_bet.bet2)) + "\n"
        res += "il reste " + str(current_bet.durée) + " minutes avant la fin```"
    return res

def end_bet_message(option_gagnante):
    global current_bet
    global logo_argent
    total = get_total(current_bet.bet1) if (option_gagnante == 1) else get_total(current_bet.bet2)
    res = "@everyone OYE OYE le bet est fini !!\n"
    res += "Le gagnant est : " + (current_bet.sujet1 if (option_gagnante == 1) else current_bet.sujet2) + "\n"
    res += "Ceux qui ont gagné se repartissent " + str(total) + " " + logo_argent
    return res


class Bet: 
    def __init__(self, _id_proposeur, _sujet : str, _sujet1 : str, _sujet2 : str, _durée : int):
        self.id_proposeur = _id_proposeur
        self.sujet = _sujet
        self.durée = _durée
        self.sujet1 = _sujet1
        self.sujet2 = _sujet2
        self.bet1 = {}
        self.bet2 = {}

    def add_better(self, _id, montant, option):
        if (_id == self.id_proposeur):
            return "Vous avez proposez le pari, vous ne pouvez pas bet :'("
        if (self.durée <= 0 ):
            return "Les jeux sont faits, vous ne pouvez pas bet :'("
        if (option == 1):
            self.bet1[_id] += montant
        else:
            self.bet2[_id] += montant
        return "Le bet à été ajouté"
    
    def fin(self, option_gagnante):
        if (option_gagnante == 1):
            total_looser = get_total(self.bet2)
            total_gagant = get_total(self.bet1)
            for _id in _bet1:
                Banque[_id] +=  (self.bet1[_id] * total_looser) / total_gagant
        else:
            total_looser = get_total(self.bet1)
            total_gagant = get_total(self.bet2)
            for _id in self.bet2:
                Banque[_id] +=  (self.bet2[_id] * total_looser) / total_gagant


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='Faire des paris endiablés'))
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
#Fonction qui ajoute tous les jours de l'argents aux users inscrits
async def daily_money():
    await bot.wait_until_ready()
    while not bot.is_closed():
        mtn = datetime.strftime(datetime.now(),'%M')
        if (mtn == '00'):
            for i in Banque:
                i[1] = i[1] + 10 
            t = 90
        else:
            t = 1
        await asyncio.sleep(t)

#Fonction reduit le temps pour le bet en cours
async def durée_bets():
    await bot.wait_until_ready()
    while not bot.is_closed():
        global current_bet
        if (current_bet != None and current_bet.durée > 0):
            current_bet.durée -= 1
            t = 60
        else:
            t = 1
        await asyncio.sleep(t)

@bot.command()
async def inscription(ctx):
    """T'ajoute au systeme de bet avec 100$ si tu n'es pas dedant"""
    if ctx.message.author.id not in Banque:
        Banque[ctx.message.author.id] =  100
        await ctx.send("Bienvenue Au casino")
    else:
        await ctx.send("Tu es deja au casino")

@bot.command()
async def mon_argent(ctx):
    """Donne ton argent perso"""
    if ctx.message.author.id not in Banque:
        await ctx.send("Tu n'es pas inscrit au casino")
    else:
        global logo_argent
        argent = Banque[ctx.message.author.id]
        message = "Bravo " + ctx.message.author.name + " tu as " + str(argent) + " " + logo_argent
        await ctx.send(message)

@bot.command()
async def leaderboard(ctx):
    """Affiche les plus Blindaxxx"""
    t = find_richets()
    #user = await bot.fetch_user(t[0])
    user = await ctx.guild.fetch_member(t[0])
    name = user.name
    global logo_argent
    message = "WOWOWO @everyone regardez comment " + name + " est ultra BLINDAXXX, il a " + str(t[1]) + " " + logo_argent
    await ctx.send(message)

@bot.command()
async def start_bet(ctx, sujet, option1, option2, durée):
    """Commence un bet avec sujet option1, option, durée (en minute)"""
    global current_bet
    current_bet = Bet(ctx.message.author.id, sujet, option1, option2, int(durée))
    await ctx.send("Le bet a été créer")

@bot.command()
async def bet_en_cours(ctx):
    """liste le bet en cours"""
    await ctx.send(show_bet()) 

@bot.command()
async def parier(ctx, option, montant):
    """parie sur le bet en cours"""
    global current_bet
    if (current_bet == None):
        await ctx.send("Il n'y a aucun bet en cours")
    elif (Banque[ctx.message.author.id] < montant):
        await ctx.send("Tu n'as pas assez d'argent sale pauvre")
    elif (option_gagnante != 1 or option_gagnante != 2):
        await ctx.send("Ce n'est pas une option valide")
    else:
        current_bet.parier(ctx.message.author.id , montant, option)

@bot.command()
async def stop_bet(ctx, option_gagnante):
    """Arrete le bet en cours"""
    global current_bet
    numero = int(option_gagnante)
    if (current_bet == None):
        await ctx.send("Il n'y a aucun bet en cours")
    elif (numero != 1 and numero != 2):
        await ctx.send("Ce n'est pas une option valide")
    elif (ctx.message.author.id != current_bet.id_proposeur):
        await ctx.send("Vous n'avez pas créer le pari vous ne pouvez pas le finir")
    else:
            current_bet.fin(numero)
            message = end_bet_message(numero)
            current_bet = None
            await ctx.send(message)

@bot.command()
async def change_money(ctx, signe):
    """Change le signe de l'argent"""
    global logo_argent
    if (ctx.message.author.guild_permissions.administrator):
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
bot.run(TOKEN)
