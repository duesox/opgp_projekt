# Najprv nainstalujte pygame:
# pip install pygame

import pygame
import sys

# Konštanty
ROWS = 6
COLS = 7
CELL_SIZE = 100
WIDTH = COLS * CELL_SIZE
HEIGHT = (ROWS + 1) * CELL_SIZE  # Extra riadok pre nazov hry + extra text
RADIUS = CELL_SIZE // 2 - 5
BG_COLOR = (0, 0, 139)  # Tmavo modra
EMPTY_COLOR = (220, 220, 220)  # Svetlo siva

# inicializacia pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect 4")

# Vykreslenie hracej plochy
def draw_board():
    screen.fill(BG_COLOR)
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.circle(
                screen, EMPTY_COLOR, (col * CELL_SIZE + CELL_SIZE // 2, (row + 1) * CELL_SIZE + CELL_SIZE // 2), RADIUS
            )
    pygame.display.update()

# Main loop
running = True
draw_board()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
sys.exit()
