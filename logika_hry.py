# -*- coding: utf-8 -*-
import unicodedata as ud
import graphics as gr
import pygame
import sys

from skore import Score


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
        self.pocet_kol=0
        self.skore_modry=Score(self.POCET_RIADKOV,self.POCET_STLPCOV)
        self.skore_cerveny=Score(self.POCET_RIADKOV,self.POCET_STLPCOV)
        for i in range(self.POCET_RIADKOV):
            self.zoznam_policok.append([])
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)
        self.running=True
        self.state = "main_menu"



    #Metóda na vymazanie dát zo zoznamu
    def obnovHru(self):
        self.pocet_kol=0
        for i in range(self.POCET_RIADKOV):
            self.zoznam_policok[i] = []
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)


    #Metóda na vymazanie dát hry
    def restartHru(self):
        self.pocet_kol=0
        for i in range(self.POCET_RIADKOV):
            self.zoznam_policok.append([])
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)
        self.VYHRA_CERVENA = 0
        self.VYHRA_MODRA = 0

    #Nastavenie hodu na správne miesto a priradenie správnej farby
    def nastavHod(self,riadok, stlpec, farba):
        self.pocet_kol +=1
        if farba == LogikaHry.CERVENA :
            self.zoznam_policok[riadok][stlpec] = LogikaHry.CERVENA
        elif farba == LogikaHry.MODRA :
            self.zoznam_policok[riadok][stlpec] = LogikaHry.MODRA
        self.vyhodnotHru()

    def kliknutie(self, x_pozicia):
        """Spracuje kliknutie hráča a spustí animáciu pádu žetónu."""

        # Určí šírku hracej plochy
        sirka_hracej_plochy = self.gra.cols * self.gra.CELL_SIZE
        offset = 250  # Posun hracej plochy doprava o 250 px

        # Skontroluje, či kliknutie je v rámci hracej plochy
        if offset <= x_pozicia <= offset + sirka_hracej_plochy:
            stlpec = (x_pozicia - offset) // self.gra.CELL_SIZE  # Výpočet stĺpca
            volny_riadok = self.prazdnyRiadok(stlpec)

            if volny_riadok is not None:
                self.gra.animate_fall(stlpec, volny_riadok, self.hrac,self.VYHRA_MODRA, self.VYHRA_CERVENA,self.skore_modry.get_celkove_skore(),self.skore_cerveny.get_celkove_skore(),self.skore_cerveny.max_skore())
                self.nastavHod(volny_riadok, stlpec, self.hrac)
                self.hrac = 2 if self.hrac == 1 else 1
    def prazdnyRiadok(self, stlpec):
        """Vráti prvý voľný riadok v danom stĺpci, alebo None ak je plný."""
        # Prechádza všetky riadky v danom stĺpci (odspodu).
        for row in reversed(range(len(self.zoznam_policok))):
            if self.zoznam_policok[row][stlpec] == 0:  # Ak je pole prázdne (0), vracia tento riadok.
                return row
        return None  # Ak nie je voľný riadok, vracia None.

    def run(self):

        """Spustí hlavný cyklus hry."""
        self.gra.draw_board(self.VYHRA_MODRA, self.VYHRA_CERVENA,self.skore_modry.get_celkove_skore(),self.skore_cerveny.get_celkove_skore(),self.skore_cerveny.max_skore())

        while self.running:
            self.gra.clock.tick(60)
            if self.state == "main_menu":
                buttons = self.gra.show_main_menu()
            elif self.state == "play_menu":
                buttons = self.gra.show_play_menu()
            elif self.state == "about":
                self.gra.show_about()
            elif self.state == "game":
                leave_button = self.gra.draw_board()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "main_menu":
                        if buttons[0].collidepoint(event.pos):
                            self.state = "play_menu"
                        elif buttons[1].collidepoint(event.pos):
                            self.state = "about"
                        elif buttons[2].collidepoint(event.pos):
                            self.running = False

                    elif self.state == "play_menu":
                        if buttons[0].collidepoint(event.pos):
                            self.gra.clear_board()
                            self.state = "game"
                            self.gra.draw_board()
                        elif buttons[1].collidepoint(event.pos):
                            pass  # Online not implemented

                    elif self.state == "about":
                        self.state = "main_menu"

                    elif self.state == "game":
                        if leave_button.collidepoint(event.pos):
                            self.gra.clear_board()
                            self.state = "main_menu"
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

    def dosadenie_cervena(self):
        self.VYHRA_CERVENA += 1
        self.skore_cerveny.set_celkove_skore(self.pocet_kol)
        self.gra.winAnimation("cervena")
        self.obnovHru()
        self.gra.clear_board(self.VYHRA_MODRA, self.VYHRA_CERVENA,self.skore_modry.get_celkove_skore(),self.skore_cerveny.get_celkove_skore(),self.skore_cerveny.max_skore())

    def dosadenie_modra(self):
        self.VYHRA_MODRA += 1
        self.gra.winAnimation("modra")
        self.skore_modry.set_celkove_skore(self.pocet_kol)
        self.obnovHru()
        self.gra.clear_board(self.VYHRA_MODRA, self.VYHRA_CERVENA,self.skore_modry.get_celkove_skore(),self.skore_cerveny.get_celkove_skore(),self.skore_cerveny.max_skore())



    def vyhodnotHru(self):
        #Kontrola Vodorovne
        # i = riadok, j = stlpec
        for i in range(6):
            for j in range(4):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i][j + 1] == self.zoznam_policok[i][j + 2]
                        == self.zoznam_policok[i][j + 3] != LogikaHry.PRAZDNO):

                    #Vyhodnotenie vodorovne
                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.dosadenie_cervena()

                    else:
                        self.dosadenie_modra()


        #Kontrola Vertikálne
        for i in range(3):
            for j in range(7):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i+1][j] == self.zoznam_policok[i+2][j] ==
                        self.zoznam_policok[i+3][j] != LogikaHry.PRAZDNO):

                    # Vyhodnotenie vertikálne
                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.dosadenie_cervena()
                    else:
                        self.dosadenie_modra()

        #Kontrola Krížom
        for i in range(3):
            for j in range(4):
                if (self.zoznam_policok[i][j]==self.zoznam_policok[i+1][j+1]==self.zoznam_policok[i+2][j+2]==
                        self.zoznam_policok[i+3][j+3]!=LogikaHry.PRAZDNO):

                    # Vyhodnotenie krížom

                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.dosadenie_cervena()
                    else:
                        self.dosadenie_modra()
        for i in range(3):
            for j in range(3, 7):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i + 1][j - 1] ==
                        self.zoznam_policok[i + 2][j - 2] == self.zoznam_policok[i + 3][j - 3] != LogikaHry.PRAZDNO):

                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.dosadenie_cervena()
                    else:
                        self.dosadenie_modra()




if __name__ == "__main__":
    hra = LogikaHry(2)
    hra.run()
