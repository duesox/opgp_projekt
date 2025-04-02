# !!! importujte si pyGame pred spustenim !!!
import pygame  # Importuje pygame knižnicu, ktorá sa používa na vytváranie hier a grafických aplikácií.
import sys  # Importuje knižnicu sys na manipuláciu so systémovými operáciami, ako je ukončenie programu.

class Graphics:

    # Konštanty pre hru
    CELL_SIZE = 100  # Veľkosť jednej bunky na mriežke (100x100 px)
    RADIUS = CELL_SIZE // 2 - 5  # Polomer pre vykreslenie žetónov (rádovo o 5 px menší než polomer bunky)

    BG_COLOR = (0, 0, 139)  # Tmavo modrá farba pozadia
    EMPTY_COLOR = (220, 220, 220)  # Svetlo šedá farba pre prázdne polia
    PLAYER_COLORS = [(0, 0, 255), (255, 0, 0)]  # Farby hráčov: Modrá a Červená (RGB)

    def __init__(self, rows, cols, player):
        pygame.init()  # Inicializuje Pygame knižnicu.

        self.rows = rows  # Nastaví počet riadkov na doske.
        self.cols = cols  # Nastaví počet stĺpcov na doske.
        width = cols * self.CELL_SIZE  # Šírka obrazovky (šírka všetkých stĺpcov).
        height = (rows + 1) * self.CELL_SIZE  # Výška obrazovky (výška všetkých riadkov + jeden riadok na názov).

        self.screen = pygame.display.set_mode((width, height))  # Nastaví veľkosť okna na obrazovke.
        pygame.display.set_caption("Connect 4")  # Nastaví názov okna na "Connect 4".
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]  # Inicializuje prázdnu dosku (všetky hodnoty 0).
        self.current_player = player  # Určuje, ktorý hráč je na rade (1 -> Modrá, 2 -> Červená).
        self.running = True  # Premenná, ktorá kontroluje, či hra stále beží.

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

    def get_available_row(self, col):
        """Vráti prvý voľný riadok v danom stĺpci, alebo None ak je plný."""
        # Prechádza všetky riadky v danom stĺpci (odspodu).
        for row in reversed(range(self.rows)):
            if self.board[row][col] == 0:  # Ak je pole prázdne (0), vracia tento riadok.
                return row
        return None  # Ak nie je voľný riadok, vracia None.

    def animate_fall(self, col, row):
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
            pygame.draw.circle(self.screen, self.PLAYER_COLORS[self.current_player - 1], (x, y), self.RADIUS)  # Vykreslí žetón na novej pozícii.
            pygame.display.update()  # Aktualizuje obrazovku.
            pygame.time.delay(10)  # Zastaví na 10 ms pre efekt pádu.

        # Po dokončení animácie nastaví žetón na správnu pozíciu na doske.
        self.board[row][col] = self.current_player
        self.draw_board()  # Vykreslí dosku po páde žetónu.

    def handle_click(self, x_pos):
        """Spracuje kliknutie hráča a spustí animáciu pádu žetónu."""
        col = x_pos // self.CELL_SIZE  # Určí stĺpec, na ktorý bolo kliknuté (podľa X pozície kliknutia).
        available_row = self.get_available_row(col)  # Získa prvý voľný riadok v tomto stĺpci.
        if available_row is not None:  # Ak je voľný riadok.
            self.animate_fall(col, available_row)  # Spustí animáciu pádu žetónu.
            # Prepne na druhého hráča (1 -> 2, 2 -> 1).
            self.current_player = 3 - self.current_player

    def run(self):
        """Spustí hlavný cyklus hry."""
        self.draw_board()  # Na začiatku vykreslí dosku.
        while self.running:  # Kým hra beží.
            for event in pygame.event.get():  # Pre každý event (akcia) v Pygame.
                if event.type == pygame.QUIT:  # Ak je event "Quit" (zatvorenie okna).
                    self.running = False  # Zastaví hru.
                elif event.type == pygame.MOUSEBUTTONDOWN:  # Ak je kliknutie myšou.
                    self.handle_click(event.pos[0])  # Spracuje kliknutie na danú X pozíciu.
        pygame.quit()  # Ukončí Pygame knižnicu po skončení hry.
        sys.exit()  # Ukončí program.

if __name__ == "__main__":  # Ak sa súbor spustí priamo.
    game = Graphics(6, 7, 1)  # Vytvorí nový objekt triedy Graphics (6 riadkov, 7 stĺpcov, začína hráč 1).
    game.run()  # Spustí hru.
