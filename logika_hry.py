# -*- coding: utf-8 -*-


class LogikaHry:
    CERVENA=1
    MODRA=2
    PRAZDNO=0


    zoznam_policok=[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]


    def __init__(self):
        pass

    #Metóda na vymazanie dát zo zoznamu
    def ObnovHru(self):
        self.zoznam_policok=[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]

    #Nastavenie hodu na správne miesto a priradenie správnej farby
    def NastavHod(self,riadok, stlpec, farba):
        farba=ud.normalize("NFKD", farba).lower()

        if farba == LogikaHry.CERVENA or farba=="cervena":
            self.zoznam_policok[riadok][stlpec] = LogikaHry.CERVENA
        elif farba == LogikaHry.MODRA or farba == "modra":
            self.zoznam_policok[riadok][stlpec] = LogikaHry.MODRA

    

