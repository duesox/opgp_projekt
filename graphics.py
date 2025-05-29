import pygame
import random


class Graphics:
    CELL_SIZE = 100
    RADIUS = CELL_SIZE // 2 - 5
    BG_COLOR = (0, 0, 139)
    EMPTY_COLOR = (220, 220, 220)
    NOTIF_COLOR_INFO = (30, 30, 30)
    NOTIF_COLOR_INV = (30, 30, 80)
    NOTIF_COLOR_BORDER = (200, 200, 200)
    PLAYER_COLORS = [(255, 255,0), (255, 0, 0)]


    def set_empty_text(self, text):
        self.empty_text = text

    NOTIF_DURATION = 3000  # milliseconds
    NOTIF_WIDTH = 300
    NOTIF_HEIGHT = 50
    MARGIN = 10

    def __init__(self, rows, cols):
        pygame.init()  # Inicializuje Pygame knižnicu.

        self.font = pygame.font.SysFont("Arial", 80, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 50, bold=True)
        self.not_font = pygame.font.SysFont("Arial", 20,bold=True)
        self.rows = rows  # Nastaví počet riadkov na doske.
        self.cols = cols  # Nastaví počet stĺpcov na doske.
        width = cols * self.CELL_SIZE  # Šírka obrazovky (šírka všetkých stĺpcov).
        height = (rows + 1) * self.CELL_SIZE  # Výška obrazovky (výška všetkých riadkov + jeden riadok na názov).

        self.screen = pygame.display.set_mode((width, height))  # Nastaví veľkosť okna na obrazovke.
        pygame.display.set_caption("Connect 4")  # Nastaví názov okna na "Connect 4".
        self.board = [[0 for _ in range(self.cols)] for _ in
                      range(self.rows)]  # Inicializuje prázdnu dosku (všetky hodnoty 0).
        self.running = True  # Premenná, ktorá kontroluje, či hra stále beží.

        self.WIDTH, self.HEIGHT = 950, 700
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Connect 4")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.running = True
        self.background_gradient = self.create_vertical_gradient_surface(self.WIDTH, self.HEIGHT,(30, 30, 255), (130, 130, 255),0.95)

        self.empty_text = ''

        self.notifications = []

    def draw_text_centered(self, text, y, size=40):
        font = pygame.font.SysFont("Arial", size, bold=True)
        txt = font.render(text, True, (0, 0, 0))
        text_rect = txt.get_rect(center=(self.WIDTH // 2, y))

        # Nastav veľkosť okolo textu
        padding = 35
        button_rect = pygame.Rect(
            text_rect.left - padding // 2,
            text_rect.top - padding // 2,
            text_rect.width + padding,
            text_rect.height + padding
        )

        # Kresli červený okraj (vonkajší obdĺžnik)
        pygame.draw.rect(self.screen, (255, 0, 0), button_rect)

        # Kresli žltý vnútorný obdĺžnik (výplň tlačidla)
        inner_padding = 9  # hrúbka červeného okraja
        inner_rect = button_rect.inflate(-2 * inner_padding, -2 * inner_padding)
        pygame.draw.rect(self.screen, (255, 255, 0), inner_rect)

        # Vykresli text
        self.screen.blit(txt, text_rect)

        return button_rect  # môžeš použiť na detekciu kliknutia

    def draw_board(self, vyhry_zlty, vyhry_cerveny, skore_zlty, skore_cerveny, skore,current_player):
        self.screen.blit(self.create_vertical_gradient_surface(self.WIDTH, self.HEIGHT,(30, 30, 255),
                                                               (130, 130, 255),0.8), (0, 0))

        # Najprv zobraz skóre
        self.zobraz_skore(vyhry_zlty, vyhry_cerveny, skore_zlty, skore_cerveny, skore)

        # Potom nakresli hraciu plochu
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.EMPTY_COLOR if self.board[row][col] == 0 else self.PLAYER_COLORS[self.board[row][col] - 1]
                pygame.draw.circle(self.screen, color, (
                    col * self.CELL_SIZE + self.CELL_SIZE // 2 + 250,
                    (row + 1) * self.CELL_SIZE + self.CELL_SIZE // 2),
                                   self.RADIUS)

        # Potom nakresli názov
        self.draw_title(self.screen)
        self.current_player(current_player)




        self.leave_button()


    def leave_button(self):
        leave_button = pygame.Rect(50, 610, 80, 80)
        pygame.draw.rect(self.screen, (255, 255, 0), leave_button, border_radius=40)
        pygame.draw.rect(self.screen, (255, 0, 0), leave_button, border_radius=40, width=10)


        # Vycentrovaný text v tlačidle
        leave_txt = self.not_font.render("Menu", True, (0, 0, 0))
        text_rect = leave_txt.get_rect(center=leave_button.center)
        self.screen.blit(leave_txt, text_rect)

        return leave_button






    def clear_board(self, vyhry_zlty, vyhry_cerveny, skore_zlty, skore_cerveny, skore, current_player):
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        self.draw_board(vyhry_zlty, vyhry_cerveny, skore_zlty, skore_cerveny, skore, current_player)

    def animate_fall(self, col, row, current_player, vyhry_zlty, vyhry_cerveny, skore_zlty, skore_cerveny, skore):
        # X pozícia, kde bude žetón spadávať (stĺpec * veľkosť bunky + polovičná veľkosť).
        x = col * self.CELL_SIZE + self.CELL_SIZE // 2 + 250
        # Počiatočná Y pozícia (na začiatku nad doskou).
        y_start = self.CELL_SIZE // 2
        y_end = (row + 1) * self.CELL_SIZE + self.CELL_SIZE // 2

        # Animácia pádu (posúvanie žetónu po Y osi).
        for y in range(y_start, y_end, 10):  # Posúvanie žetónu o 10 px.
            self.draw_board(vyhry_zlty,vyhry_cerveny,skore_zlty,skore_cerveny,skore, current_player)
            pygame.draw.circle(self.screen, self.PLAYER_COLORS[current_player - 1], (x, y), self.RADIUS)  # Vykreslí žetón na novej pozícii.

            self.draw_notifications(self.screen)
            pygame.display.flip()
            pygame.time.delay(3)  # Zastaví na 10 ms pre efekt pádu.

        # Po dokončení animácie nastaví žetón na správnu pozíciu na doske.
        self.board[row][col] = current_player
        self.draw_board(vyhry_zlty, vyhry_cerveny, skore_zlty, skore_cerveny, skore,current_player)  # Vykreslí dosku po páde žetónu.


    def current_player(self,player):
        x = 90  # left + half width
        y = 90
        pygame.draw.circle(self.screen, self.PLAYER_COLORS[player - 1], (x, y), self.RADIUS)





    def winAnimation(self, vyherca):
        confetti_list = []
        for _ in range(100):
            confetti = {
                "x": random.randint(0, self.WIDTH),
                "y": random.randint(-100, -10),
                "size": random.randint(4, 8),
                "color": random.choice(
                    [(255, 0, 0), (0, 255, 0), (0, 100, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]),
                "speed": random.uniform(2, 5),
                "angle": random.uniform(-0.1, 0.1)
            }
            confetti_list.append(confetti)

        running = True
        while running:
            self.clock.tick(60)
            self.screen.fill((30, 30, 30))
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            for c in confetti_list:
                c["y"] += c["speed"]
                c["x"] += c["angle"]
                pygame.draw.rect(self.screen, c["color"], (c["x"], c["y"], c["size"], c["size"]))

            if vyherca.lower() == "cervena":
                text = self.font.render("Vyhral červený!", True, (255, 255, 255))
            else:
                text = self.font.render("Vyhral žltý!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(text, text_rect)

            pygame.display.flip()

    def draw_animation(self):

        running = True
        while running:
            self.clock.tick(60)
            self.draw_animated_background()
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            text = self.font.render("Remíza!", True, (32, 32, 32))
            text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(text, text_rect)

            pygame.display.flip()

    def show_main_menu(self):

        self.draw_animated_background()
        play_rect = self.draw_text_centered("Play", 200)
        about_rect = self.draw_text_centered("About", 300)
        exit_rect = self.draw_text_centered("Exit", 400)
        self.draw_title(self.screen)
        return play_rect, about_rect, exit_rect

    def show_play_menu(self):
        self.draw_animated_background()
        local_rect = self.draw_text_centered("On this device", 250)
        online_rect = self.draw_text_centered("Online (Coming Soon)", 350)
        self.draw_title(self.screen)
        self.leave_button()

        return local_rect, online_rect
    def show_network(self, players):
        self.draw_animated_background()

        font_main = pygame.font.SysFont("Arial", 20)
        font_small = pygame.font.SysFont("Arial", 14)

        block_width = 500
        block_height = 60
        margin = 20
        start_y = 100  # Leave space for header

        screen_width, _ = self.screen.get_size()
        block_x = (screen_width - block_width) // 2  # Center horizontally

        self.leave_button()

        if len(players) > 0:
            nicks = []
            uuids = []
            lastOnlines = []

            invite_rect = []

            empty_text = 'Vyhľadávam hráčov...'

            for player in players:
                nicks.append(player[0])
                uuids.append(player[1])
                lastOnlines.append(player[2])

            for i in range(len(uuids)):
                nick = nicks[i] if i < len(nicks) else ""
                uuid = uuids[i]
                last = lastOnlines[i] + "s ago"

                y = start_y + i * (block_height + margin)

                # Draw outer block
                pygame.draw.rect(self.screen, (50, 50, 50), (block_x, y, block_width, block_height), border_radius=6)

                # Draw "Nick", UUID, Last Online
                nick_text = font_main.render(nick, True, (255, 255, 255))
                uuid_text = font_small.render(uuid, True, (200, 200, 200))
                last_text = font_main.render(last, True, (180, 180, 180))

                self.screen.blit(nick_text, (block_x + 10, y + 5))
                self.screen.blit(uuid_text, (block_x + 10, y + 30))
                self.screen.blit(last_text, (block_x + block_width - last_text.get_width() - 10, y + 5))

                # Draw "Invite" button
                invite_rect.append([pygame.Rect(block_x + block_width // 2 - 40, y + 10, 80, 35), uuids[i]])
                pygame.draw.rect(self.screen, (100, 150, 250), invite_rect[i][0], border_radius=5)
                invite_text = font_main.render("Invite", True, (0, 0, 0))
                self.screen.blit(invite_text, (invite_rect[i][0].x + 10, invite_rect[i][0].y + 5))

            pygame.display.update()
            return  invite_rect
        else:
            self.draw_text_centered('Vyhľadávam hráčov...', 50)
            self.leave_button()


    def show_about(self):
        self.draw_animated_background()
        lines = [
            "Hra Connect 4 je pre dvoch hráčov.",
            "Hráči striedavo vhadzujú žetóny do stĺpcov.",
            "Cieľom je mať 4 rovnaké žetóny v rade:",
            "horizontálne, vertikálne alebo diagonálne.",
            "Hráč, ktorý to dosiahne ako prvý, vyhráva.",
            "Ak je mriežka plná a nikto nevyhral, je to remíza.",
        ]
        y = 170
        for line in lines:
            text_surface = self.font.render(line, True, (0,0,0))
            text_rect = text_surface.get_rect(center=(self.WIDTH // 2, y))
            self.screen.blit(text_surface, text_rect)
            y += 50


        self.leave_button()

        self.draw_title(self.screen)

    def zobraz_skore(self, vyhry_zlty, vyhry_cerveny, skore_zlty, skore_cerveny, skore_max):
        # Vymaže ľavú stranu (kde je skóre)
        self.screen.blit(self.create_vertical_gradient_surface(self.WIDTH, self.HEIGHT, (30, 30, 255),
                                                               (130, 130, 255), 0.7), (0, 0))

        # Pozície pre text naľavo
        x_pos = 20
        y_pos_max = 140

        max_skore_text = self.small_font.render(f"Max skóre:", True, (255, 255, 255))
        max_skore = self.small_font.render(f"{skore_max}", True, (255, 255, 255))
        cerveny_text = self.small_font.render(f"Červený: {vyhry_cerveny}", True, (255, 0, 0))
        cerveny_skore = self.small_font.render(f"Skóre: {skore_cerveny}", True, (255, 0, 0))

        zlty_text = self.small_font.render(f"Žltá: {vyhry_zlty}", True, (255, 255, 0))
        zlty_skore = self.small_font.render(f"Skóre: {skore_zlty}", True, (255, 255, 0))

        self.screen.blit(max_skore_text, (x_pos, y_pos_max))

        self.screen.blit(max_skore, (x_pos, y_pos_max+50))
        self.screen.blit(cerveny_text, (x_pos, y_pos_max+120))
        self.screen.blit(cerveny_skore, (x_pos, y_pos_max+170))
        self.screen.blit(zlty_text, (x_pos, y_pos_max+240))
        self.screen.blit(zlty_skore, (x_pos, y_pos_max+290))

    def player_list_update(self, devices):
        pass

    def draw_title(self, surface):
        font = pygame.font.SysFont("arialblack", 70, bold=True)
        text = "CONNECT 4"
        spacing = 7  # bežné medzery medzi písmenami
        reduced_spacing = 4  # menšia medzera medzi 'T' a '4'

        # Predbežný výpočet šírky textu s rôznymi medzerami
        total_width = 0
        for i in range(len(text)):
            total_width += font.size(text[i])[0]
            if i < len(text) - 1:
                total_width += reduced_spacing if text[i] == "T" and text[i + 1] == " " else spacing

        x_start = (surface.get_width() - total_width) // 2
        y_pos = 0
        x_pos = x_start

        for i in range(len(text)):
            char = text[i]

            # Tieň
            shadow = font.render(char, True, (0, 0, 0))
            surface.blit(shadow, (x_pos + 3, y_pos + 3))

            # Zlatý text
            letter = font.render(char, True, (255, 215, 0))
            surface.blit(letter, (x_pos, y_pos))

            # Posun pozície pre ďalšie písmeno
            x_pos += font.size(char)[0]
            if i < len(text) - 1:
                if char == "T" and text[i + 1] == " ":
                    x_pos += reduced_spacing
                else:
                    x_pos += spacing

    def show_notification(self, message, typ='info', uuid=None):
        self.notifications.append({"text": message, "start_time": pygame.time.get_ticks(), "type": typ, "uuid": uuid})

    def draw_notifications(self, surface, typ='info', uuid=None):
        now = pygame.time.get_ticks()
        for i, notif in enumerate(self.notifications[:]):
            elapsed = now - notif["start_time"]
            if elapsed > self.NOTIF_DURATION and notif['type'] == 'info':
                self.notifications.remove(notif)
                continue
            if elapsed > self.NOTIF_DURATION * 10 and notif['type'] == 'invite':
                self.notifications.remove(notif)
                continue

            # Position (bottom right corner)
            x = surface.get_width() - self.NOTIF_WIDTH - self.MARGIN
            y = surface.get_height() - (self.NOTIF_HEIGHT + self.MARGIN) * (i + 1)

            height = self.NOTIF_HEIGHT
            color = self.NOTIF_COLOR_INFO
            if notif['type'] == 'invite':
                height = self.NOTIF_HEIGHT * 2
                color = self.NOTIF_COLOR_INV

            # Draw background
            notif_rect = pygame.Rect(x, y, self.NOTIF_WIDTH, height)
            pygame.draw.rect(surface, color, notif_rect, border_radius=8)
            pygame.draw.rect(surface, (200, 200, 200), notif_rect, 2, border_radius=8)

            # Render text
            text_surf = self.not_font.render(notif["text"], True, (255, 255, 255))
            surface.blit(text_surf, (x + 10, y + 10))


            if notif['type'] == 'invite':
                accept_rect = pygame.Rect(x + 10, y + height - 40, self.NOTIF_WIDTH // 2 - 15, 30)
                pygame.draw.rect(surface, (50, 150, 50), accept_rect, border_radius=5)
                accept_text = self.not_font.render("Prijať", True, (255, 255, 255))
                surface.blit(accept_text, (accept_rect.x + 10, accept_rect.y + 5))

                reject_rect = pygame.Rect(x + self.NOTIF_WIDTH // 2 + 5, y + height - 40, self.NOTIF_WIDTH //2 - 15, 30)
                pygame.draw.rect(surface, (150, 50, 50), reject_rect, border_radius=5)
                surface.blit(reject_rect, (reject_rect.x + 10, reject_rect.y + 5))
                notif["accept_rect"] = accept_rect
                notif["reject_rect"] = reject_rect

    def handle_notif_clicks(self, pos):
        for notif in self.notifications[:]:
            if notif['type'] == 'invite' and "accept_rect" in notif:
                if notif["accept_rect"].collidepoint(pos):
                    self.accept_invite(notif["uuid"])
                    self.notifications.remove(notif)
                    return True
                if notif["reject_rect"].collidepoint(pos):
                    self.reject_invite(notif["uuid"])
                    self.notifications.remove(notif)
                    return True
        return False

    def receive_invite(self, nick, uuid):
        message = f"Pozvánka od hráča: {nick}"
        self.show_notification(message, typ='invite', uuid=uuid)

    def draw_animated_background(self):
        # Inicializácia stavových premenných pri prvom použití
        if not hasattr(self, "animated_tokens"):
            self.animated_tokens = []
            self.last_token_time = pygame.time.get_ticks()
            self.spawn_delay = 2000  # milisekundy

        # 1. Gradient pozadie
        self.screen.blit(self.background_gradient, (0, 0))

        # 2. Spawn nového tokenu
        current_time = pygame.time.get_ticks()
        if current_time - self.last_token_time > self.spawn_delay:
            token = {
                "x": random.randint(50, self.WIDTH - 50),
                "y": -40,
                "speed": random.uniform(2, 4),
                "color": random.choice(["red", "yellow"]),
                "radius": 20
            }
            self.animated_tokens.append(token)
            self.last_token_time = current_time

        # 3. Aktualizácia a vykreslenie tokenov
        for token in self.animated_tokens[:]:
            token["y"] += token["speed"]
            color = (255, 0, 0) if token["color"] == "red" else (255, 255, 0)
            pygame.draw.circle(self.screen, color, (int(token["x"]), int(token["y"])), self.RADIUS)

            if token["y"] > self.HEIGHT + 40:
                self.animated_tokens.remove(token)


    def create_vertical_gradient_surface(self, width, height, top_color, bottom_color, darkness_factor=0.7):
        surface = pygame.Surface((width, height))
        for y in range(height):
            ratio = y / height
            r = int((top_color[0] + (bottom_color[0] - top_color[0]) * ratio) * darkness_factor)
            g = int((top_color[1] + (bottom_color[1] - top_color[1]) * ratio) * darkness_factor)
            b = int((top_color[2] + (bottom_color[2] - top_color[2]) * ratio) * darkness_factor)

        # Zaisti, že farby nebudú menšie než 0
            r = max(0, r)
            g = max(0, g)
            b = max(0, b)

            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        return surface

