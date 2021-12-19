class Joueur:
    def __init__(self,nom,symb):
        self.nom = nom
        self.symb = symb
    
    def __str__(self, nom, symb):
        print("nom: ",nom,"\n symbole:",symb)

class Case:
    def __init__(pos, val):
        self.pos = pos
        self.val = val


class Grille:
    def __init__(self, table):
        self.table = table
    
    def is_empty(self, case):
        return table[n] == None

    def change_val(self,case,symbole):
        table[case] = symbole
    



