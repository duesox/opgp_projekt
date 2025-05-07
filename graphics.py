import pygame
import random
import sys

class Graphics:
    CELL_SIZE = 100
    RADIUS = CELL_SIZE // 2 - 5
    BG_COLOR = (0, 0, 139)
    EMPTY_COLOR = (220, 220, 220)
    PLAYER_COLORS = [(0, 0, 255), (255, 0, 0)]

    def __init__(self, rows, cols):
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.WIDTH, self.HEIGHT = 700, 700
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Connect 4")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.running = True

    def draw_text_centered(self, text, y, size=40):
        font = pygame.font.SysFont("Arial", size)
        txt = font.render(text, True, (255, 255, 255))
        rect = txt.get_rect(center=(self.WIDTH // 2, y))
        self.screen.blit(txt, rect)
        return rect

    def draw_board(self):
        self.screen.fill(self.BG_COLOR)
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.EMPTY_COLOR if self.board[row][col] == 0 else self.PLAYER_COLORS[self.board[row][col] - 1]
                pygame.draw.circle(self.screen, color, (
                    col * self.CELL_SIZE + self.CELL_SIZE // 2,
                    (row + 1) * self.CELL_SIZE + self.CELL_SIZE // 2),
                    self.RADIUS)
        leave_button = pygame.Rect(10, 10, 120, 50)
        pygame.draw.rect(self.screen, (255, 0, 0), leave_button)
        leave_txt = self.font.render("Leave", True, (255, 255, 255))
        self.screen.blit(leave_txt, (20, 15))
        pygame.display.update()
        return leave_button

    def clear_board(self):
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    def animate_fall(self, col, row, current_player):
        x = col * self.CELL_SIZE + self.CELL_SIZE // 2
        y_start = self.CELL_SIZE // 2
        y_end = (row + 1) * self.CELL_SIZE + self.CELL_SIZE // 2
        for y in range(y_start, y_end, 10):
            self.draw_board()
            pygame.draw.circle(self.screen, self.PLAYER_COLORS[current_player - 1], (x, y), self.RADIUS)
            pygame.display.update()
            pygame.time.delay(10)
        self.board[row][col] = current_player
        self.draw_board()

    def winAnimation(self, vyherca):
        confetti_list = []
        for _ in range(100):
            confetti = {
                "x": random.randint(0, self.WIDTH),
                "y": random.randint(-100, -10),
                "size": random.randint(4, 8),
                "color": random.choice([(255, 0, 0), (0, 255, 0), (0, 100, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]),
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
            text = self.big_font.render(vyherca + " Vyhral!", True, (255, 255, 255))
            rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(text, rect)
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
        online_rect = self.draw_text_centered("Online (Coming Soon)", 350)
        pygame.display.update()
        return local_rect, online_rect

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


