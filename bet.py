from toolbox import get_total

class Bet: 
    def __init__(self, _id_proposeur, _sujet : str, _sujet1 : str, _sujet2 : str, _durée : int):
        self.id_proposeur = _id_proposeur
        self.sujet = _sujet
        self.durée = _durée
        self.sujet1 = _sujet1
        self.sujet2 = _sujet2
        self.bet1 = {}
        self.bet2 = {}

    def parier(self, id_parieur, montant, option, Banque):
        if (id_parieur == self.id_proposeur):
            return "Vous avez proposé le pari, vous ne pouvez pas bet :'("
        if (self.durée <= 0 ):
            return "Les jeux sont faits, vous ne pouvez plus bet :'("
        if (option == 1):
            if (id_parieur in self.bet1):
                tmp = self.bet1[id_parieur]
            else:
                tmp = 0
            self.bet1[id_parieur] = tmp +  montant
        else:
            if (id_parieur in self.bet2):
                tmp = self.bet2[id_parieur]
            else:
                tmp = 0
            self.bet2[id_parieur] = tmp +  montant
        Banque[id_parieur] -= montant
        return "Le bet à été ajouté"
    
    def fin(self, option_gagnante):
        ret = []
        if (option_gagnante == 1):
            total_looser = get_total(self.bet2)
            total_gagant = get_total(self.bet1)
            if (total_looser == 0):
                for _id in self.bet1:
                    ret.append((_id, self.bet1[_id]))
            else:
                for _id in self.bet1:
                    gain = (self.bet1[_id] * total_looser) / total_gagant
                    ret.append((_id, gain))
        else:
            total_looser = get_total(self.bet1)
            total_gagant = get_total(self.bet2)
            if (total_looser == 0):
                for _id in self.bet2:
                    ret.append((_id, self.bet2[_id]))
            else:
                for _id in self.bet2:
                    gain = (self.bet2[_id] * total_looser) / total_gagant
                    ret.append((_id, gain))
        return ret