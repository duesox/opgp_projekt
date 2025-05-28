# -*- coding: utf-8 -*-
import unicodedata as ud
import graphics as gr
import pygame
import sys
import threading

from prepojenie import Networking
from skore import Score


class LogikaHry:
    # Konštanty
    CERVENA = 2
    ZLTA = 1
    PRAZDNO = 0
    POCET_RIADKOV = 6
    POCET_STLPCOV = 7

    # Zoznam na ukladanie hodov

    def __init__(self, hrac):
        self.vyhra_cervena = 0
        self.vyhra_zlta = 0
        self.net = Networking()
        self.net_thread = threading.Thread(target=self.discovering)
        self.hrac = hrac
        self.gra = gr.Graphics(self.POCET_RIADKOV, self.POCET_STLPCOV)
        self.zoznam_policok = []
        self.pocet_kol = 0
        self.skore_zlty = Score(self.POCET_RIADKOV, self.POCET_STLPCOV)
        self.skore_cerveny = Score(self.POCET_RIADKOV, self.POCET_STLPCOV)
        for i in range(self.POCET_RIADKOV):
            self.zoznam_policok.append([])
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)
        self.running = True
        self.state = "main_menu"

        self.players = dict()

        # network callbacky
        self.recv_move = self.net.on_move_recieved
        self.recv_sett = self.net.on_settings_changed
        self.recv_inv = self.net.on_game_invite
        self.recv_inv_rej = self.net.on_game_invite_rejected
        # start stop multiplayer hry
        self.start_mult = self.net.on_connect
        self.stop_mult = self.net.on_disconnect
        # updatenuty list hracov
        self.discovery_update = self.net.on_new_discovery
        # dlho nedonajdeni hraci
        self.no_players = self.net.no_devices_found

        self.restart_ask = self.net.on_request_restart
        self.retry_ask = self.net.on_request_retry
        self.restart_mult = self.net.on_game_restart
        self.retry_mult = self.net.on_game_retry

        self.mult_game = False
        self.mult_color = 0  # 0 - cervena, 1 zlta
        self.player_color = 0

        self.nickname = self.net.get_nickname()
        self.clock = pygame.time.Clock()

    # Metóda na vymazanie dát zo zoznamu
    def obnovHru(self):
        self.pocet_kol = 0
        for i in range(self.POCET_RIADKOV):
            self.zoznam_policok[i] = []
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)

    # Metóda na vymazanie dát hry
    def restartHru(self):
        self.pocet_kol = 0
        for i in range(self.POCET_RIADKOV):
            self.zoznam_policok.append([])
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)
        self.vyhra_cervena = 0
        self.vyhra_zlta = 0

    # Nastavenie hodu na správne miesto a priradenie správnej farby
    def nastavHod(self, riadok, stlpec, farba):
        self.pocet_kol += 1
        if farba == LogikaHry.CERVENA:
            self.zoznam_policok[riadok][stlpec] = LogikaHry.CERVENA
        elif farba == LogikaHry.ZLTA:
            self.zoznam_policok[riadok][stlpec] = LogikaHry.ZLTA
        self.vyhodnotHru()

    def kliknutie(self, x_pozicia, protihrac=False):
        if not self.mult_game or (self.mult_game and self.player_color == self.mult_color):
            """Spracuje kliknutie hráča a spustí animáciu pádu žetónu."""

            # Určí šírku hracej plochy
            sirka_hracej_plochy = self.gra.cols * self.gra.CELL_SIZE
            offset = 250  # Posun hracej plochy doprava o 250 px

            # Skontroluje, či kliknutie je v rámci hracej plochy
            if offset <= x_pozicia <= offset + sirka_hracej_plochy:
                stlpec = (x_pozicia - offset) // self.gra.CELL_SIZE  # Výpočet stĺpca
                volny_riadok = self.prazdnyRiadok(stlpec)

                if volny_riadok is not None:
                    self.gra.animate_fall(stlpec, volny_riadok, self.hrac, self.vyhra_zlta, self.vyhra_cervena,
                                          self.skore_zlty.get_celkove_skore(), self.skore_cerveny.get_celkove_skore(),
                                          self.skore_cerveny.max_skore())
                    self.nastavHod(volny_riadok, stlpec, self.hrac)
                    self.hrac = 2 if self.hrac == 1 else 1
        elif self.mult_game and not protihrac:
            stlpec = x_pozicia
            volny_riadok = self.prazdnyRiadok(stlpec)
            if volny_riadok is not None:
                self.gra.animate_fall(stlpec, volny_riadok, self.hrac, self.vyhra_zlta, self.vyhra_cervena,
                                      self.skore_zlty.get_celkove_skore(), self.skore_cerveny.get_celkove_skore(),
                                      self.skore_cerveny.max_skore())
                self.nastavHod(volny_riadok, stlpec, self.hrac)
                self.hrac = 2 if self.hrac == 1 else 1
                self.net.send_move(stlpec)

    def prazdnyRiadok(self, stlpec):
        """Vráti prvý voľný riadok v danom stĺpci, alebo None ak je plný."""
        # Prechádza všetky riadky v danom stĺpci (odspodu).
        for row in reversed(range(len(self.zoznam_policok))):
            if self.zoznam_policok[row][stlpec] == 0:  # Ak je pole prázdne (0), vracia tento riadok.
                return row
        return None  # Ak nie je voľný riadok, vracia None.

    # game type - 0 - offline, 1 - online
    def run(self):
        """Spustí hlavný cyklus hry."""
        self.gra.draw_board(self.vyhra_zlta, self.vyhra_cervena, self.skore_zlty.get_celkove_skore(),
                            self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)

        while self.running:
            self.gra.clock.tick(60)
            self.clock.tick(60)

            if self.state == "main_menu":
                buttons = self.gra.show_main_menu()
            elif self.state == "play_menu":
                buttons = self.gra.show_play_menu()
            elif self.state == "about":
                self.gra.show_about()
            elif self.state == "discovery":
                buttons = self.gra.show_network(self.players)
            elif self.state == "game":
                leave_button = self.gra.draw_board(self.vyhra_zlta, self.vyhra_cervena,
                                                   self.skore_zlty.get_celkove_skore(),
                                                   self.skore_cerveny.get_celkove_skore(),
                                                   self.skore_cerveny.max_skore(),self.hrac)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.state == "main_menu":


                        if buttons[0].collidepoint(event.pos):
                            self.state = "play_menu"


                        elif buttons[1].collidepoint(event.pos):
                            self.state = "about"

                            if self.gra.leave_button().collidepoint(event.pos):
                                self.state = "main_menu"


                        elif buttons[2].collidepoint(event.pos):
                            self.running = False
                        else:
                            self.gra.show_notification("Netrafil si tlačidlo, skus ešte raz")

                    elif self.state == "play_menu":

                        if buttons[0].collidepoint(event.pos):
                            self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena,
                                                 self.skore_zlty.get_celkove_skore(),
                                                 self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)
                            self.state = "game"
                            self.gra.draw_board(self.vyhra_zlta, self.vyhra_cervena,
                                                self.skore_zlty.get_celkove_skore(),
                                                self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)
                        elif buttons[1].collidepoint(event.pos):
                            self.state = "discovery"
                            self.start_mult()
                            self.gra.set_empty_text('Vyhľadávam hráčov...')
                        elif self.gra.leave_button().collidepoint(event.pos):
                            self.state = "main_menu"

                    elif self.state == "discovery":
                        if self.gra.leave_button().collidepoint(event.pos):
                            self.stop_mult()
                            self.state = "main_menu"
                        elif buttons[1].collidepoint(event.pos):
                            self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena,
                                                 self.skore_zlty.get_celkove_skore(),
                                                 self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)
                            self.state = "game"
                            self.gra.draw_board(self.vyhra_zlta, self.vyhra_cervena,
                                                self.skore_zlty.get_celkove_skore(),
                                                self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)

                    elif self.state == "about":
                        self.state = "main_menu"

                    elif self.state == "game":
                        # Kontrola kliknutia na tlačidlo Leave
                        if self.gra.leave_button().collidepoint(event.pos):
                            self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena,
                                                 self.skore_zlty.get_celkove_skore(),
                                                 self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)
                            self.state = "main_menu"
                        else:
                            # Inak spracuj kliknutie na hraciu plochu
                            self.kliknutie(event.pos[0])

            self.gra.draw_notifications(self.gra.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # Vráti aktuálny stav hodov
    def zoznamHodov(self):
        return self.zoznam_policok

    # Metóda na vymazanie hodu zo zoznamu
    def vymazHod(self, riadok, stlpec):
        self.zoznam_policok[riadok][stlpec] = LogikaHry.PRAZDNO

    # Vráti aktuálny stav hodov cervené farby
    def get_Cervena(self):
        return self.vyhra_cervena

    # Vráti aktuálny stav hodov zltej farby
    def get_Zlta(self):
        return self.vyhra_zlta

    def dosadenie_cervena(self):
        self.vyhra_cervena += 1
        self.skore_cerveny.set_celkove_skore(self.pocet_kol)
        self.gra.winAnimation("cervena")
        self.obnovHru()
        self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena, self.skore_zlty.get_celkove_skore(),
                             self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)

    def dosadenie_zlta(self):
        self.vyhra_zlta += 1
        self.gra.winAnimation("zlta")
        self.skore_zlty.set_celkove_skore(self.pocet_kol)
        self.obnovHru()
        self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena, self.skore_zlty.get_celkove_skore(),
                             self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)

    def vyhodnotHru(self):
        # Kontrola Vodorovne
        # i = riadok, j = stlpec
        for i in range(6):
            for j in range(4):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i][j + 1] == self.zoznam_policok[i][j + 2]
                        == self.zoznam_policok[i][j + 3] != LogikaHry.PRAZDNO):

                    # Vyhodnotenie vodorovne
                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.dosadenie_cervena()

                    else:
                        self.dosadenie_zlta()

        # Kontrola Vertikálne
        for i in range(3):
            for j in range(7):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i + 1][j] == self.zoznam_policok[i + 2][j] ==
                        self.zoznam_policok[i + 3][j] != LogikaHry.PRAZDNO):

                    # Vyhodnotenie vertikálne
                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.dosadenie_cervena()
                    else:
                        self.dosadenie_zlta()

        # Kontrola Krížom
        for i in range(3):
            for j in range(4):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i + 1][j + 1] == self.zoznam_policok[i + 2][
                    j + 2] ==
                        self.zoznam_policok[i + 3][j + 3] != LogikaHry.PRAZDNO):

                    # Vyhodnotenie krížom

                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.dosadenie_cervena()
                    else:
                        self.dosadenie_zlta()
        for i in range(3):
            for j in range(3, 7):
                if (self.zoznam_policok[i][j] == self.zoznam_policok[i + 1][j - 1] ==
                        self.zoznam_policok[i + 2][j - 2] == self.zoznam_policok[i + 3][j - 3] != LogikaHry.PRAZDNO):

                    if self.zoznam_policok[i][j] == LogikaHry.CERVENA:
                        self.dosadenie_cervena()
                    else:
                        self.dosadenie_zlta()

    def discovering(self):
        self.net.start_discovery()

    def discovery_update(self, devices):
        self.players = []
        for ip, info in devices:
            self.players.append([info['nick'], info['uuid'], info['timestamp']])
        self.gra.show_network(self.players)

    def recv_inv(self, nick, x_size, y_size, max_wins):
        # zobrazit upozornenie a moznosti hej a ne
        pass

    def recv_inv_rej(self):
        # zobrazit upozornenie, ze pozvanka bola odmietnuta
        pass

    def inv_react(self, uuid, reaction: bool):
        if reaction:
            self.net.connect_to_client(uuid, 0)
            self.player_color = 1
        else:
            self.net.game_accept(uuid, accept=2)

    def start_mult(self):
        self.net.start_tcp_listen()

    def stop_mult(self):
        self.net.stop_tcp_listen()

    def no_players(self, time):
        self.gra.set_empty_text(f'Už {time}s sa nenašli hráči.')

    def recv_move(self, x):
        # spracovanie a ukazanie tahu protihraca
        self.kliknutie(x, True)
        self.mult_color = 1 if self.hrac == 0 else 0

    def send_invite(self, uuid):
        self.net.game_accept(uuid)
        self.player_color = 0

    # asi toto skipneme
    def recv_sett(self):
        pass


if __name__ == "__main__":
    hra = LogikaHry(2)
    hra.run()
