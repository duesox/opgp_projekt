# -*- coding: utf-8 -*-
import unicodedata as ud
import graphics as gr
import pygame
import sys

class LogikaHry :
    #Konštanty
    CERVENA=2
    MODRA=1
    PRAZDNO=0
    VYHRA_CERVENA=0
    VYHRA_MODRA=0
    POCET_RIADKOV=6
    POCET_STLPCOV=7

    #Zoznam na ukladanie hodov



    def __init__(self,hrac):
        self.hrac=hrac
        self.gra=gr.Graphics(self.POCET_RIADKOV, self.POCET_STLPCOV )
        self.zoznam_policok=[]
        for i in range(self.POCET_RIADKOV):
            self.zoznam_policok.append([])
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)
        self.running=True


    #Metóda na vymazanie dát zo zoznamu
    def obnovHru(self):
        for i in range(self.POCET_RIADKOV):
            self.zoznam_policok[i] = []
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)


    #Metóda na vymazanie dát hry
    def restartHru(self):
        for i in range(self.POCET_RIADKOV):
            self.zoznam_policok.append([])
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)
        self.VYHRA_CERVENA = 0
        self.VYHRA_MODRA = 0

    #Nastavenie hodu na správne miesto a priradenie správnej farby
    def nastavHod(self,riadok, stlpec, farba):
        if farba == LogikaHry.CERVENA :
            self.zoznam_policok[riadok][stlpec] = LogikaHry.CERVENA
        elif farba == LogikaHry.MODRA :
            self.zoznam_policok[riadok][stlpec] = LogikaHry.MODRA
        self.vyhodnotHru()


    def kliknutie(self, x_pozicia):
        """Spracuje kliknutie hráča a spustí animáciu pádu žetónu."""
        stlpec = x_pozicia // self.gra.CELL_SIZE  # Určí stĺpec, na ktorý bolo kliknuté (podľa X pozície kliknutia).
        volny_riadok = self.prazdnyRiadok(stlpec)  # Získa prvý voľný riadok v tomto stĺpci.
        if volny_riadok is not None:  # Ak je voľný riadok.
            self.gra.animate_fall(stlpec, volny_riadok, self.hrac)  # Spustí animáciu pádu žetónu.
            self.nastavHod(volny_riadok, stlpec, self.hrac)
            if self.hrac==1:
                self.hrac = 2
            else:
                self.hrac=1

    def prazdnyRiadok(self, stlpec):
        """Vráti prvý voľný riadok v danom stĺpci, alebo None ak je plný."""
        # Prechádza všetky riadky v danom stĺpci (odspodu).
        for row in reversed(range(len(self.zoznam_policok))):
            if self.zoznam_policok[row][stlpec] == 0:  # Ak je pole prázdne (0), vracia tento riadok.
                return row
        return None  # Ak nie je voľný riadok, vracia None.


    def run(self):
        """Spustí hlavný cyklus hry."""
        self.gra.draw_board()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running=False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.kliknutie(event.pos[0])

        pygame.quit()
        sys.exit()




    #Vráti aktuálny stav hodov
    def zoznamHodov(self):
        return self.zoznam_policok

    #Metóda na vymazanie hodu zo zoznamu
    def vymazHod(self,riadok, stlpec):
        self.zoznam_policok[riadok][stlpec] = LogikaHry.PRAZDNO
    #Vráti aktuálny stav hodov cervené farby
    def get_Cervena(self):
        return self.VYHRA_CERVENA
    #Vráti aktuálny stav hodov modrej farby
    def get_Modra(self):
        return self.VYHRA_MODRA


    def vyhodnotHru(self):
        #Kontrola Vodorovne
        # i = riadok, j = stlpec
        for i in range(6):
            for j in range(4):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i][j + 1] == self.zoznam_policok[i][j + 2]
                        == self.zoznam_policok[i][j + 3] != LogikaHry.PRAZDNO):

                    #Vyhodnotenie vodorovne
                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.VYHRA_CERVENA += 1
                        self.gra.winAnimation()
                        self.obnovHru()
                        self.gra.draw_board()
                    else:
                        self.VYHRA_MODRA += 1
                        self.gra.winAnimation()
                        self.obnovHru()
                        self.gra.draw_board()

        #Kontrola Vertikálne
        for i in range(3):
            for j in range(7):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i+1][j] == self.zoznam_policok[i+2][j] ==
                        self.zoznam_policok[i+3][j] != LogikaHry.PRAZDNO):

                    # Vyhodnotenie vertikálne
                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.VYHRA_CERVENA += 1
                        self.gra.winAnimation()
                        self.obnovHru()
                        self.gra.draw_board()
                    else:
                        self.VYHRA_MODRA += 1
                        self.gra.winAnimation()
                        self.obnovHru()
                        self.gra.draw_board()

        #Kontrola Krížom
        for i in range(3):
            for j in range(4):
                if (self.zoznam_policok[i][j]==self.zoznam_policok[i+1][j+1]==self.zoznam_policok[i+2][j+2]==
                        self.zoznam_policok[i+3][j+3]!=LogikaHry.PRAZDNO):

                    # Vyhodnotenie krížom

                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.VYHRA_CERVENA += 1
                        self.gra.winAnimation()
                        self.obnovHru()
                        self.gra.draw_board()
                    else:
                        self.VYHRA_MODRA += 1
                        self.gra.winAnimation()
                        self.obnovHru()
                        self.gra.draw_board()

                if (self.zoznam_policok[i][j+3]==self.zoznam_policok[i+1][j+2]==self.zoznam_policok[i+2][j+1]==
                        self.zoznam_policok[i+3][j]!=LogikaHry.PRAZDNO):

                    # Vyhodnotenie krížom
                    if self.zoznam_policok[i][j+3] == LogikaHry.CERVENA:
                        self.VYHRA_CERVENA += 1
                        self.gra.winAnimation()
                        self.obnovHru()
                        self.gra.draw_board()
                    else:
                        self.VYHRA_MODRA += 1
                        self.gra.winAnimation()
                        self.obnovHru()
                        self.gra.draw_board()


if __name__ == "__main__":
    hra = LogikaHry(2)
    hra.run()
