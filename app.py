# commit 1: player_movement.py
import pygame
import math
import sys

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

COLOR_GRASS_BG   = (48, 148, 58)
COLOR_GRASS_DARK = (38, 126, 48)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4.8
        self.facing_angle = 0

    def move(self, dx, dy):
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.facing_angle = math.atan2(dy, dx)
        self.x = max(40, min(SCREEN_WIDTH - 40, self.x))
        self.y = max(90, min(SCREEN_HEIGHT - 40, self.y))

    def draw(self, surf):
        pygame.draw.ellipse(surf, (30, 80, 35), (self.x - 18, self.y + 10, 36, 14))
        pygame.draw.circle(surf, (226, 178, 92), (int(self.x), int(self.y)), 19)
        pygame.draw.circle(surf, (244, 200, 115), (int(self.x), int(self.y)), 13)
        pygame.draw.circle(surf, (200, 40, 40), (int(self.x), int(self.y)), 14, 2)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

while True:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
    dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
    player.move(dx, dy)

    screen.fill(COLOR_GRASS_BG)
    for tx in range(0, SCREEN_WIDTH, 64):
        for ty in range(60, SCREEN_HEIGHT, 64):
            if (tx // 64 + ty // 64) % 2 == 0:
                pygame.draw.rect(screen, COLOR_GRASS_DARK, (tx, ty, 64, 64))

    player.draw(screen)
    pygame.display.flip()