import time

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
        self.net.on_move_recieved = self.recv_move
        self.net.on_game_invite = self.recv_inv
        self.net.on_game_invite_rejected = self.recv_inv_rej
        # TODO implementovat start stop multiplayer hry
        # updatenuty list hracov
        self.net.on_new_discovery = self.discovery_update
        # dlho nenajdeni hraci
        self.net.no_devices_found = self.no_players

        # zapnutie servera
        self.net.on_connect = self.start_server
        # po tuknuti na invite notifikaciu
        self.gra.accept_invite = self.inv_react
        self.gra.reject_invite = self.inv_react

        self.net.on_disconnect = self.opp_stop_mult

        # spustenie online hry
        self.net.on_online_game_start = self.online_game

        self.mult_game = False
        self.mult_color = 0  # 0 - cervena, 1 zlta
        self.player_color = 0

        self.nickname = self.net.get_nickname()
        self.clock = pygame.time.Clock()
        print("N   N EEEE ZZZZZ  AA  TTTTTT V     V  AA  RRRR   AA  TTTTTT     TTTTTT  OOO  TTTTTT  OOO       OOO  K  K N   N  OOO")
        print("NN  N E       Z  A  A   TT   V     V A  A R   R A  A   TT         TT   O   O   TT   O   O     O   O K K  NN  N O   O")
        print("N N N EEE    Z   AAAA   TT    V   V  AAAA RRRR  AAAA   TT         TT   O   O   TT   O   O     O   O KK   N N N O   O")
        print("N  NN E     Z    A  A   TT     V V   A  A R R   A  A   TT         TT   O   O   TT   O   O     O   O K K  N  NN O   O")
        print("N   N EEEE ZZZZZ A  A   TT      V    A  A R  RR A  A   TT         TT    OOO    TT    OOO       OOO  K  K N   N  OOO")

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
            self.zoznam_policok[i] = []
            for j in range(self.POCET_STLPCOV):
                self.zoznam_policok[i].append(self.PRAZDNO)
        self.vyhra_cervena = 0
        self.vyhra_zlta = 0
        self.skore_zlty.vynulovat_skore()
        self.skore_cerveny.vynulovat_skore()

    # Nastavenie hodu na správne miesto a priradenie správnej farby
    def nastavHod(self, riadok, stlpec, farba):
        self.pocet_kol += 1
        if farba == LogikaHry.CERVENA:
            self.zoznam_policok[riadok][stlpec] = LogikaHry.CERVENA
        elif farba == LogikaHry.ZLTA:
            self.zoznam_policok[riadok][stlpec] = LogikaHry.ZLTA
        self.vyhodnotHru()

    def kliknutie(self, x_pozicia, protihrac=False, stlpec=0):
        if not self.mult_game:
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
        elif self.mult_game and not protihrac and self.hrac == self.mult_color:
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
                    self.hrac = 1 if self.hrac == 2 else 2
                    self.net.send_move(stlpec)
        elif self.mult_game and protihrac and self.hrac != self.mult_color:
            volny_riadok = self.prazdnyRiadok(stlpec)
            if volny_riadok is not None:
                self.gra.animate_fall(stlpec, volny_riadok, self.hrac, self.vyhra_zlta, self.vyhra_cervena,
                                      self.skore_zlty.get_celkove_skore(), self.skore_cerveny.get_celkove_skore(),
                                      self.skore_cerveny.max_skore())
                self.nastavHod(volny_riadok, stlpec, self.hrac)
                self.hrac = 2 if self.hrac == 1 else 1

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

            if self.state != "discovery" and self.net.get_discovering():
                self.net.stop_discovery()
            if self.state == "main_menu":
                buttons = self.gra.show_main_menu()
            elif self.state == "play_menu":
                buttons = self.gra.show_play_menu()
            elif self.state == "about":
                self.gra.show_about()
            elif self.state == "exit_menu":
                buttons = self.gra.exit_window()
            elif self.state == "menu":
                buttons = self.gra.menu_window()
            elif self.state == "discovery":
                if not self.net.get_discovering():
                    self.net.start_discovery()
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
                    if self.gra.handle_notif_clicks(event.pos):
                        continue
                    if self.state == "main_menu":


                        if buttons[0].collidepoint(event.pos):
                            self.state = "play_menu"


                        elif buttons[1].collidepoint(event.pos):
                            self.state = "about"

                            if self.gra.leave_button().collidepoint(event.pos):
                                self.state = "main_menu"


                        elif buttons[2].collidepoint(event.pos):
                            self.state="exit_menu"


                        else:
                            self.gra.show_notification("Netrafil si tlačidlo, skus ešte raz")

                    elif self.state == "play_menu":

                        if buttons[0].collidepoint(event.pos):
                            self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena,
                                                 self.skore_zlty.get_celkove_skore(),
                                                 self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)
                            self.restartHru()
                            self.state = "game"
                            self.gra.draw_board(self.vyhra_zlta, self.vyhra_cervena,
                                                self.skore_zlty.get_celkove_skore(),
                                                self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)

                        elif buttons[1].collidepoint(event.pos):
                            try:
                                self.state = "discovery"
                                self.gra.set_empty_text('Vyhľadávam hráčov...')
                            except ZeroDivisionError:
                                self.state = "main_menu"
                                self.gra.show_notification("Nemáte žiadne internetové rozhrania.")
                        elif self.gra.leave_button().collidepoint(event.pos):
                            self.state = "main_menu"

                    elif self.state == "discovery":
                        if self.gra.leave_button().collidepoint(event.pos):
                            self.gra.draw_text_centered("Ukončujem vyhľadávanie", 50)
                            self.state = "main_menu"
                        else:
                            for button in buttons:
                                if button[0].collidepoint(event.pos):
                                    try:
                                        self.send_invite(button[1])
                                        self.gra.show_notification("Bola odoslaná pozvánka.")
                                    except Exception:
                                        pass
                                    break

                    elif self.state == "about":
                        self.state = "main_menu"

                    elif self.state == "game":
                        # Kontrola kliknutia na tlačidlo Leave
                        if self.gra.leave_button().collidepoint(event.pos):
                            if self.mult_game:
                                self.state = "confirm_leave_mult"
                            else:
                                self.state = "menu"
                        else:
                            # Inak spracuj kliknutie na hraciu plochu
                            self.kliknutie(event.pos[0])
                    elif self.state == "exit_menu":
                        button_no, button_yes = self.gra.exit_window()
                        if button_yes.collidepoint(event.pos):
                            self.running = False  # Ukončí hru
                        elif button_no.collidepoint(event.pos):
                            self.state = "main_menu"
                    elif self.state == "confirm_leave_mult":
                        button_no, button_yes = self.gra.exit_window(text="Chcete opustiť online hru?", main=False)
                        if button_yes.collidepoint(event.pos):
                            self.net.send_disconnect()
                            self.stop_mult()
                            self.obnovHru()
                            self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena,
                                                 self.skore_zlty.get_celkove_skore(),
                                                 self.skore_cerveny.get_celkove_skore(),
                                                 self.skore_cerveny.max_skore(), self.hrac)
                            self.state = "main_menu"
                        elif button_no.collidepoint(event.pos):
                            self.state = "game"

                    elif self.state == "menu":
                        button_main_menu, button_obnov, button_restart = self.gra.menu_window()
                        if button_main_menu.collidepoint(event.pos):
                            self.state = "main_menu"
                        elif button_obnov.collidepoint(event.pos):
                            self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena,
                                                 self.skore_zlty.get_celkove_skore(),
                                                 self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)
                            self.obnovHru()
                            self.state = "game"
                        elif button_restart.collidepoint(event.pos):
                            self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena,
                                                 self.skore_zlty.get_celkove_skore(),
                                                 self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),self.hrac)
                            self.restartHru()
                            self.state = "game"
                        else:
                            self.state = "game"
            if not self.gra.animuje:
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
        a = False
        for i in range(6):
            for j in range(7):
                if self.zoznam_policok[i][j] != LogikaHry.PRAZDNO:
                    continue
                else:
                    a=True
        if not a:
            self.gra.draw_animation()
            self.obnovHru()
            self.gra.clear_board(self.vyhra_zlta, self.vyhra_cervena, self.skore_zlty.get_celkove_skore(),
                            self.skore_cerveny.get_celkove_skore(), self.skore_cerveny.max_skore(),
                            self.hrac)
            a=True


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
        print(devices)
        if len(devices) > 0:
            for ip, info in devices.items():
                self.players.append([info['nick'], info['uuid'], info['last_ping']])
            self.gra.show_network(self.players)
        if len(devices) == 0:
            self.gra.show_network([])

    def recv_inv(self, nick, uuid):  # mozno tu este max_wins
        # zobrazit upozornenie a moznosti hej a ne
        print(f'dosiel inv {nick}: {uuid}')
        self.gra.receive_invite(nick, uuid)

    def recv_inv_rej(self):
        # zobrazit upozornenie, ze pozvanka bola odmietnuta
        self.gra.show_notification("Pozvánka bola odmietnutá.")

    def inv_react(self, uuid, reaction):
        if reaction:
            self.net.game_accept(uuid, accept=1)
        else:
            self.net.game_accept(uuid, accept=2)

    def start_server(self, uuid):
        nick = "hráčom"
        self.mult_game = True
        self.net.start_tcp_listen(uuid)
        time.sleep(1.5)
        for player in self.players:
            if player[1] == uuid:
                nick = player[0]
        self.gra.show_notification(f"Spájam s {nick}...")
        self.net.game_accept(uuid, accept=3)

    def stop_mult(self):
        self.state = "menu"
        self.net.stop_tcp_listen()
        self.mult_game = False

    def no_players(self, cas):
        self.gra.show_notification(f'Už {cas}s sa nenašli hráči.')

    def recv_move(self, x):
        # spracovanie a ukazanie tahu protihraca
        self.kliknutie(x, True, stlpec=x)
        self.hrac = self.mult_color

    def send_invite(self, uuid):
        def _thread_invite():
            try:
                self.net.game_accept(uuid)
            except Exception as e:
                print(e)
                self.gra.show_notification(str(e))
        threading.Thread(target=_thread_invite, daemon=True).start()

    def online_game(self, zacinajuci):
        self.mult_game = True
        self.state = "game"
        if zacinajuci:
            self.mult_color = 1
        else:
            self.mult_color = 2
        self.hrac = 1

    def opp_stop_mult(self):
        self.gra.show_notification("Hráč nebol aktívny. Hra ukončená")
        self.state = "main_menu"
        self.mult_game = False




if __name__ == "__main__":
    try:
        hra = LogikaHry(2)
        hra.run()
    except KeyboardInterrupt:
        sys.exit(130)
