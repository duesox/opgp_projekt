# !!! importujte si pyGame pred spustenim !!!
import pygame  # Importuje pygame knižnicu, ktorá sa používa na vytváranie hier a grafických aplikácií.
import random
import sys  # Importuje knižnicu sys na manipuláciu so systémovými operáciami, ako je ukončenie programu.

class Graphics:

    # Konštanty pre hru
    CELL_SIZE = 100  # Veľkosť jednej bunky na mriežke (100x100 px)
    RADIUS = CELL_SIZE // 2 - 5  # Polomer pre vykreslenie žetónov (rádovo o 5 px menší než polomer bunky)

    BG_COLOR = (0, 0, 139)  # Tmavo modrá farba pozadia
    EMPTY_COLOR = (220, 220, 220)  # Svetlo šedá farba pre prázdne polia
    PLAYER_COLORS = [(0, 0, 255), (255, 0, 0)]  # Farby hráčov: Modrá a Červená (RGB)

    def __init__(self, rows, cols):
        pygame.init()  # Inicializuje Pygame knižnicu.

        self.rows = rows  # Nastaví počet riadkov na doske.
        self.cols = cols  # Nastaví počet stĺpcov na doske.
        width = cols * self.CELL_SIZE  # Šírka obrazovky (šírka všetkých stĺpcov).
        height = (rows + 1) * self.CELL_SIZE  # Výška obrazovky (výška všetkých riadkov + jeden riadok na názov).

        self.screen = pygame.display.set_mode((width, height))  # Nastaví veľkosť okna na obrazovke.
        pygame.display.set_caption("Connect 4")  # Nastaví názov okna na "Connect 4".
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]  # Inicializuje prázdnu dosku (všetky hodnoty 0).
        self.running = True  # Premenná, ktorá kontroluje, či hra stále beží.

        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 80, bold=True)

    def draw_board(self):
        """Vykreslí hraciu plochu."""
        self.screen.fill(self.BG_COLOR)  # Vyplní obrazovku tmavo modrou farbou (pozadie).
        for row in range(self.rows):  # Pre každý riadok na doske.
            for col in range(self.cols):  # Pre každý stĺpec na doske.
                # Ak je pole prázdne (0), použije sa farba EMPTY_COLOR, inak sa použije farba hráča.
                color = self.EMPTY_COLOR if self.board[row][col] == 0 else self.PLAYER_COLORS[self.board[row][col] - 1]
                # Vykreslí žetón (kruh) na danú pozíciu (row, col) s vybranou farbou.
                pygame.draw.circle(self.screen, color, (
                    col * self.CELL_SIZE + self.CELL_SIZE // 2,  # X pozícia (stĺpec * veľkosť bunky + polovičná veľkosť).
                    (row + 1) * self.CELL_SIZE + self.CELL_SIZE // 2),  # Y pozícia (riadok * veľkosť bunky + polovičná veľkosť).
                    self.RADIUS)  # Polomer pre vykreslenie žetónu.
        pygame.display.update()  # Aktualizuje obrazovku, aby sa vykreslili všetky zmeny.

    def animate_fall(self, col, row, current_player):
        """Animuje pád žetónu do daného stĺpca a riadku."""
        # X pozícia, kde bude žetón spadávať (stĺpec * veľkosť bunky + polovičná veľkosť).
        x = col * self.CELL_SIZE + self.CELL_SIZE // 2
        # Počiatočná Y pozícia (na začiatku nad doskou).
        y_start = self.CELL_SIZE // 2
        # Konečná Y pozícia (na riadku, kam žetón spadne).
        y_end = (row + 1) * self.CELL_SIZE + self.CELL_SIZE // 2

        # Animácia pádu (posúvanie žetónu po Y osi).
        for y in range(y_start, y_end, 10):  # Posúvanie žetónu o 10 px.
            self.draw_board()  # Vykreslí dosku, aby sa žetóny zobrazovali.
            pygame.draw.circle(self.screen, self.PLAYER_COLORS[current_player - 1], (x, y), self.RADIUS)  # Vykreslí žetón na novej pozícii.
            pygame.display.update()  # Aktualizuje obrazovku.
            pygame.time.delay(10)  # Zastaví na 10 ms pre efekt pádu.

        # Po dokončení animácie nastaví žetón na správnu pozíciu na doske.
        self.board[row][col] = current_player
        self.draw_board()  # Vykreslí dosku po páde žetónu.

    def winAnimation(self):
        # Create confetti particles as dictionaries
        confetti_list = []
        for _ in range(100):
            confetti = {
                "x": random.randint(0, self.WIDTH),
                "y": random.randint(-100, -10),
                "size": random.randint(4, 8),
                "color": random.choice([
                    (255, 0, 0), (0, 255, 0), (0, 100, 255),
                    (255, 255, 0), (255, 0, 255), (0, 255, 255)
                ]),
                "speed": random.uniform(2, 5),
                "angle": random.uniform(-0.1, 0.1)
            }
            confetti_list.append(confetti)

        running = True
        while running:
            self.clock.tick(60)
            self.screen.fill((30, 30, 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            # Update & draw each confetti particle
            for c in confetti_list:
                c["y"] += c["speed"]
                c["x"] += c["angle"]
                pygame.draw.rect(self.screen, c["color"], (c["x"], c["y"], c["size"], c["size"]))

            # Draw "You Won" text
            text = self.font.render("You Won!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(text, text_rect)

            pygame.display.flip()

if __name__ == "__main__":  # Ak sa súbor spustí priamo.
    game = Graphics(6, 7)  # Vytvorí nový objekt triedy Graphics (6 riadkov, 7 stĺpcov, začína hráč 1).
    game.winAnimation()
