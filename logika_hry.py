# -*- coding: utf-8 -*-
import unicodedata as ud

class LogikaHry:
    #Konštanty
    CERVENA=1
    MODRA=2
    PRAZDNO=0
    VYHRA_CERVENA=0
    VYHRA_MODRA=0

    #Zoznam na ukladanie hodov
    zoznam_policok=[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]


    def __init__(self):
        pass

    #Metóda na vymazanie dát zo zoznamu
    def ObnovHru(self):
        self.zoznam_policok=[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]
    def RestartHru(self):
        self.zoznam_policok=[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]
        self.VYHRA_CERVENA = 0
        self.VYHRA_MODRA = 0

    #Nastavenie hodu na správne miesto a priradenie správnej farby
    def NastavHod(self,riadok, stlpec, farba):
        farba=ud.normalize("NFKD", farba).lower()

        if farba == LogikaHry.CERVENA or farba=="cervena":
            self.zoznam_policok[riadok][stlpec] = LogikaHry.CERVENA
        elif farba == LogikaHry.MODRA or farba == "modra":
            self.zoznam_policok[riadok][stlpec] = LogikaHry.MODRA
        self.VyhodnotHru()


    #Vráti aktuálny stav hodov
    def ZoznamHodov(self):
        return self.zoznam_policok

    #Metóda na vymazanie hodu zo zoznamu
    def VymazHod(self,riadok, stlpec):
        self.zoznam_policok[riadok][stlpec] = LogikaHry.PRAZDNO


    def VyhodnotHru(self):
        #Kontrola Vodorovne
        # i = riadok, j = stlpec
        for i in range(6):
            for j in range(4):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i][j + 1] == self.zoznam_policok[i][j + 2]
                        == self.zoznam_policok[i][j + 3] != LogikaHry.PRAZDNO):

                    #Vyhodnotenie vodorovne
                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.VYHRA_CERVENA = 1
                    else:
                        self.VYHRA_MODRA = 1

        #Kontrola Vertikálne
        for i in range(3):
            for j in range(7):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i+1][j] == self.zoznam_policok[i+2][j] ==
                        self.zoznam_policok[i+3][j] != LogikaHry.PRAZDNO):

                    # Vyhodnotenie vertikálne
                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.VYHRA_CERVENA = 1
                    else:
                        self.VYHRA_MODRA = 1

        #Kontrola Krížom
        for i in range(3):
            for j in range(4):
                if (self.zoznam_policok[i][j]==self.zoznam_policok[i+1][j+1]==self.zoznam_policok[i+2][j+2]==
                        self.zoznam_policok[i+3][j+3]!=LogikaHry.PRAZDNO):

                    # Vyhodnotenie krížom

                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.VYHRA_CERVENA = 1
                    else:
                        self.VYHRA_MODRA = 1

                if (self.zoznam_policok[i][j+3]==self.zoznam_policok[i+1][j+2]==self.zoznam_policok[i+2][j+1]==
                        self.zoznam_policok[i+3][j]!=LogikaHry.PRAZDNO):

                    # Vyhodnotenie krížom
                    if self.zoznam_policok[i][j+3] == LogikaHry.CERVENA:
                        self.VYHRA_CERVENA = 1
                    else:
                        self.VYHRA_MODRA = 1










