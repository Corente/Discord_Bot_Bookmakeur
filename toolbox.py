import os, pickle

def get_total(tab):
    res = 0
    for key in tab:
        res += tab[key]
    return res

def show_bet(serveur_bet):
    res = ""
    if (serveur_bet == None):
        res =  "Il n'y a aucun bet en cours"
    else:
        res = "```Le bet en cours est: " + serveur_bet.sujet + "\n"
        res += "\t Option 1 : " + serveur_bet.sujet1 + " | Total sur ce pari = " + str(get_total(serveur_bet.bet1)) + "\n"
        res += "\t Option 2 : " + serveur_bet.sujet2 + " | Total sur ce pari = " + str(get_total(serveur_bet.bet2)) + "\n"
        res += "il reste " + str(serveur_bet.durée) + " minutes avant la fin```"
    return res

def end_bet_message(option_gagnante, serveur_bet, serveur_money):
    total = get_total(serveur_bet.bet2) if (option_gagnante == 1) else get_total(serveur_bet.bet1)
    res = "@Beters OYE OYE le bet est fini !!\n"
    res += "Le gagnant est : " + (serveur_bet.sujet1 if (option_gagnante == 1) else serveur_bet.sujet2) + "\n"
    res += "Ceux qui ont gagné se repartissent " + str(total) + " " + serveur_money
    return res

def apply_gain(Banque, list_of_winners, id_serveur):
    for t in list_of_winners:
        t[0] = id_winner
        t[1] = gains
        Banque[id_winner] += gains

def save(path, Banque):
    for key in Banque:
        filename = os.path.join(path, (str(key) + ".pkl"))
        file = open(filename, "wb")
        pickle.dump(Banque[key], file, pickle.HIGHEST_PROTOCOL)
        file.close()
        print("its saved")

def load(path):
    Banque =  {}
    for filename in os.listdir(path):
        f = open(os.path.join(path, filename), "rb")
        servername = int(os.path.splitext(filename)[0])
        Banque[servername] = {}
        Banque[servername] = pickle.load(f)
        f.close()
        print("its loaded")
    return Banque