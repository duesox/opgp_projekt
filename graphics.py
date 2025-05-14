import pygame
import random
import sys


class Graphics:
    CELL_SIZE = 100
    RADIUS = CELL_SIZE // 2 - 5
    BG_COLOR = (0, 0, 139)
    EMPTY_COLOR = (220, 220, 220)
    PLAYER_COLORS = [(0, 0, 255), (255, 0, 0)]

    def set_empty_text(self, text):
        self.empty_text = text

    def __init__(self, rows, cols):
        pygame.init()  # Inicializuje Pygame knižnicu.

        self.font = pygame.font.SysFont("Arial", 80, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 50, bold=True)
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

        self.empty_text = ''

    def draw_text_centered(self, text, y, size=40):
        font = pygame.font.SysFont("Arial", size)
        txt = font.render(text, True, (255, 255, 255))
        rect = txt.get_rect(center=(self.WIDTH // 2, y))
        self.screen.blit(txt, rect)
        return rect

    def draw_board(self, vyhry_modry, vyhry_cerveny, skore_modry, skore_cerveny, skore):
        self.screen.fill(self.BG_COLOR)
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.EMPTY_COLOR if self.board[row][col] == 0 else self.PLAYER_COLORS[self.board[row][col] - 1]
                pygame.draw.circle(self.screen, color, (
                    col * self.CELL_SIZE + self.CELL_SIZE // 2 + 250,
                    (row + 1) * self.CELL_SIZE + self.CELL_SIZE // 2),
                                   self.RADIUS)
        leave_button = pygame.Rect(10, 10, 120, 50)
        pygame.draw.rect(self.screen, (255, 0, 0), leave_button)
        leave_txt = self.font.render("Leave", True, (255, 255, 255))
        self.screen.blit(leave_txt, (20, 15))

        self.zobraz_skore(vyhry_modry, vyhry_cerveny, skore_modry, skore_cerveny, skore)
        self.draw_title(self.screen)
        pygame.display.update()
        return leave_button

    def draw_board_no_update(self):
        pygame.draw.rect(self.screen, self.BG_COLOR, (250, 0, self.cols * self.CELL_SIZE, self.CELL_SIZE))
        self.draw_title(self.screen)

        for row in range(self.rows):
            for col in range(self.cols):
                # Súradnice stredu bunky
                x = col * self.CELL_SIZE + self.CELL_SIZE // 2 + 250
                y = (row + 1) * self.CELL_SIZE + self.CELL_SIZE // 2

                # Súradnice obdĺžnika pozadia bunky
                rect_x = col * self.CELL_SIZE + 250
                rect_y = (row + 1) * self.CELL_SIZE

                # Modré pozadie bunky
                pygame.draw.rect(self.screen, self.BG_COLOR, (rect_x, rect_y, self.CELL_SIZE, self.CELL_SIZE))

                # Zistenie farby žetónu
                color = self.EMPTY_COLOR if self.board[row][col] == 0 else self.PLAYER_COLORS[self.board[row][col] - 1]

                # Vykreslenie žetónu
                pygame.draw.circle(self.screen, color, (x, y), self.RADIUS)

    def clear_board(self, vyhry_modry, vyhry_cerveny, skore_modry, skore_cerveny, skore):
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        self.draw_board(vyhry_modry, vyhry_cerveny, skore_modry, skore_cerveny, skore)

    def animate_fall(self, col, row, current_player, vyhry_modry, vyhry_cerveny, skore_modry, skore_cerveny, skore):
        # X pozícia, kde bude žetón spadávať (stĺpec * veľkosť bunky + polovičná veľkosť).
        x = col * self.CELL_SIZE + self.CELL_SIZE // 2 + 250
        # Počiatočná Y pozícia (na začiatku nad doskou).
        y_start = self.CELL_SIZE // 2
        y_end = (row + 1) * self.CELL_SIZE + self.CELL_SIZE // 2

        # Animácia pádu (posúvanie žetónu po Y osi).
        for y in range(y_start, y_end, 10):  # Posúvanie žetónu o 10 px.
            self.draw_board_no_update()
            pygame.draw.circle(self.screen, self.PLAYER_COLORS[current_player - 1], (x, y),
                               self.RADIUS)  # Vykreslí žetón na novej pozícii.

            pygame.display.update()  # Aktualizuje obrazovku.
            pygame.time.delay(10)  # Zastaví na 10 ms pre efekt pádu.

        # Po dokončení animácie nastaví žetón na správnu pozíciu na doske.
        self.board[row][col] = current_player
        self.draw_board(vyhry_modry, vyhry_cerveny, skore_modry, skore_cerveny, skore)  # Vykreslí dosku po páde žetónu.

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
                text = self.font.render("Vyhral modrý!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(text, text_rect)

            pygame.display.flip()

    def show_main_menu(self):
        self.screen.fill((30, 30, 30))
        play_rect = self.draw_text_centered("Play", 200)
        about_rect = self.draw_text_centered("About", 300)
        exit_rect = self.draw_text_centered("Exit", 400)
        pygame.display.update()
        return play_rect, about_rect, exit_rect

    def show_play_menu(self):
        self.screen.fill((30, 30, 30))
        local_rect = self.draw_text_centered("On this device", 250)
        online_rect = self.draw_text_centered("Online (WIP)", 350)
        pygame.display.update()
        return local_rect, online_rect

    def show_network(self, players):
        self.screen.fill((30, 30, 30))

        font_main = pygame.font.SysFont("Arial", 20)
        font_small = pygame.font.SysFont("Arial", 14)

        block_width = 500
        block_height = 60
        margin = 20
        start_y = 100  # Leave space for header

        screen_width, _ = self.screen.get_size()
        block_x = (screen_width - block_width) // 2  # Center horizontally

        # --- Draw "Leave" Button (top-left) ---
        leave_rect = pygame.Rect(20, 20, 80, 35)
        pygame.draw.rect(self.screen, (200, 70, 70), leave_rect, border_radius=5)
        leave_text = font_main.render("Leave", True, (255, 255, 255))
        self.screen.blit(leave_text, (leave_rect.x + 10, leave_rect.y + 5))

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
            return leave_rect, invite_rect
        else:
            self.draw_text_centered('Vyhľadávam hráčov...', 20)
            return leave_rect

    def show_about(self):
        self.screen.fill((30, 30, 30))
        lines = [
            "Hra Connect 4 je pre dvoch hráčov.",
            "Hráči striedavo vhadzujú žetóny do stĺpcov.",
            "Cieľom je mať 4 rovnaké žetóny v rade - horizontálne, vertikálne alebo diagonálne.",
            "Hráč, ktorý to dosiahne ako prvý, vyhráva.",
            "Ak je mriežka plná a nikto nevyhral, je to remíza.",
            "Klikni hocikde pre návrat do menu."
        ]
        y = 150
        for line in lines:
            self.draw_text_centered(line, y, 30)
            y += 50
        pygame.display.update()

    def zobraz_skore(self, vyhry_modry, vyhry_cerveny, skore_modry, skore_cerveny, skore_max):
        # Vymaže ľavú stranu (kde je skóre)
        pygame.draw.rect(self.screen, self.BG_COLOR, (0, 0, 200, self.HEIGHT))

        # Pozície pre text naľavo
        x_pos = 20
        y_pos_max = self.CELL_SIZE

        max_skore_text = self.small_font.render(f"Max skóre:", True, (255, 255, 255))
        max_skore = self.small_font.render(f"{skore_max}", True, (255, 255, 255))
        cerveny_text = self.small_font.render(f"Červený: {vyhry_cerveny}", True, (255, 0, 0))
        cerveny_skore = self.small_font.render(f"Skóre: {skore_cerveny}", True, (255, 0, 0))

        modry_text = self.small_font.render(f"Modrý: {vyhry_modry}", True, (0, 0, 255))
        modry_skore = self.small_font.render(f"Skóre: {skore_modry}", True, (0, 0, 255))

        self.screen.blit(max_skore_text, (x_pos, y_pos_max))
        self.screen.blit(max_skore, (x_pos, y_pos_max + 50))
        self.screen.blit(cerveny_text, (x_pos, y_pos_max + 100))
        self.screen.blit(cerveny_skore, (x_pos, y_pos_max + 150))
        self.screen.blit(modry_text, (x_pos, y_pos_max + 200))
        self.screen.blit(modry_skore, (x_pos, y_pos_max + 250))
        pygame.display.update()

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
