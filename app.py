import random
import pygame
import math
import sys

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

COLOR_GRASS_BG   = (48, 148, 58)
COLOR_GRASS_DARK = (38, 126, 48)
COLOR_DIRT        = (112, 72, 36)
COLOR_CANE_STEM   = (170, 204, 76)
COLOR_CANE_NODE   = (108, 148, 42)
COLOR_CANE_LEAF   = (96, 178, 58)
COLOR_GOLD_STEM   = (255, 215, 0)
COLOR_GOLD_LEAF   = (255, 238, 88)
COLOR_WHITE       = (255, 255, 255)

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

class SugarCane:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.stage = 0
        self.grow_timer = random.randint(30, 90)
        self.mature_time = 140
        self.is_golden = random.random() < 0.12
        self.sway_offset = random.uniform(0, 100)
        self.hitbox_radius = 28

    def update(self, ticks):
        if self.stage < 2:
            self.grow_timer += 1
            if self.grow_timer > self.mature_time:
                self.stage += 1
                self.grow_timer = 0
                if self.stage == 2 and self.is_golden:
                    self.stage = 3

    def draw(self, surf, ticks):
        pygame.draw.ellipse(surf, COLOR_DIRT, (self.x - 18, self.y - 7, 36, 14))
        sway = math.sin((ticks * 0.05) + self.sway_offset) * 4

        stem_col = COLOR_GOLD_STEM if self.stage == 3 else COLOR_CANE_STEM
        node_col = COLOR_WHITE if self.stage == 3 else COLOR_CANE_NODE
        leaf_col = COLOR_GOLD_LEAF if self.stage == 3 else COLOR_CANE_LEAF

        if self.stage == 0:
            pygame.draw.line(surf, stem_col, (self.x, self.y), (self.x + sway * 0.5, self.y - 14), 4)
        elif self.stage == 1:
            pygame.draw.line(surf, stem_col, (self.x, self.y), (self.x + sway * 0.7, self.y - 32), 6)
            pygame.draw.line(surf, node_col, (self.x - 4, self.y - 16), (self.x + 4, self.y - 16), 2)
        else:
            tip_x, tip_y = self.x + sway, self.y - 56
            pygame.draw.line(surf, stem_col, (self.x, self.y), (tip_x, tip_y), 8)
            for frac in (0.28, 0.56, 0.82):
                nx = self.x + (tip_x - self.x) * frac
                ny = self.y + (tip_y - self.y) * frac
                pygame.draw.line(surf, node_col, (nx - 5, ny), (nx + 5, ny), 3)
            pygame.draw.line(surf, leaf_col, (tip_x, tip_y), (tip_x - 20, tip_y - 12), 4)
            pygame.draw.line(surf, leaf_col, (tip_x, tip_y), (tip_x + 20, tip_y - 12), 4)

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

