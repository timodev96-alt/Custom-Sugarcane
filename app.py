import pygame
import math
import random
import sys
import struct

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

COLOR_GRASS_BG    = (48, 148, 58)
COLOR_GRASS_DARK  = (38, 126, 48)
COLOR_DIRT        = (112, 72, 36)
COLOR_CANE_STEM   = (170, 204, 76)
COLOR_CANE_NODE   = (108, 148, 42)
COLOR_CANE_LEAF   = (96, 178, 58)
COLOR_GOLD_STEM   = (255, 215, 0)
COLOR_GOLD_LEAF   = (255, 238, 88)
COLOR_WHITE       = (255, 255, 255)
COLOR_GOLD        = (255, 205, 40)
COLOR_RUSH_PINK   = (255, 75, 140)

def create_sound(freq_start, freq_end, duration, wave_type="sine", vol=0.25):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    phase = 0.0

    for i in range(n_samples):
        progress = i / max(1, n_samples)
        freq = freq_start + (freq_end - freq_start) * progress
        phase += 2.0 * math.pi * freq / sample_rate

        if wave_type == "sine":
            val = math.sin(phase)
        elif wave_type == "square":
            val = 1.0 if math.sin(phase) > 0 else -1.0
        elif wave_type == "triangle":
            val = (2.0 / math.pi) * math.asin(math.sin(phase))
        else:
            val = random.uniform(-1.0, 1.0)

        env = (1.0 - progress) ** 1.5
        sample = int(val * env * vol * 32767)
        buf.extend(struct.pack("<h", max(-32768, min(32767, sample))))

    try:
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception:
        return None
    
class Particle:
    def __init__(self, x, y, vx, vy, color, radius, life=30, shape="circle"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.max_life = life
        self.life = life
        self.shape = shape
        self.rot = random.uniform(0, 360)
        self.rot_speed = random.uniform(-10, 10)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.vy += 0.12
        self.life -= 1
        self.rot += self.rot_speed

    def draw(self, surf):
        alpha_ratio = max(0, self.life / self.max_life)
        cur_rad = max(1, int(self.radius * alpha_ratio))
        if self.shape == "circle":
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), cur_rad)
        elif self.shape == "spark":
            length = cur_rad * 2.2
            dx = math.cos(math.radians(self.rot)) * length
            dy = math.sin(math.radians(self.rot)) * length
            pygame.draw.line(surf, self.color, (self.x - dx, self.y - dy), (self.x + dx, self.y + dy), 2)

class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255), size=22):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 45
        self.max_life = 45
        self.vy = -1.8
        self.font = pygame.font.SysFont("arialblack", size)

    def update(self):
        self.y += self.vy
        self.vy *= 0.96
        self.life -= 1

    def draw(self, surf):
        txt_surf = self.font.render(self.text, True, self.color)
        alpha = int(255 * (self.life / self.max_life))
        txt_surf.set_alpha(alpha)
        surf.blit(txt_surf, txt_surf.get_rect(center=(int(self.x), int(self.y))))

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

    def update(self, time_ticks):
        if self.stage < 2:
            self.grow_timer += 1
            if self.grow_timer > self.mature_time:
                self.stage += 1
                self.grow_timer = 0
                if self.stage == 2 and self.is_golden:
                    self.stage = 3

    def draw(self, surf, time_ticks):
        pygame.draw.ellipse(surf, COLOR_DIRT, (self.x - 18, self.y - 7, 36, 14))
        sway = math.sin((time_ticks * 0.05) + self.sway_offset) * 4

        stem_color = COLOR_GOLD_STEM if self.stage == 3 else COLOR_CANE_STEM
        node_color = COLOR_WHITE if self.stage == 3 else COLOR_CANE_NODE
        leaf_color = COLOR_GOLD_LEAF if self.stage == 3 else COLOR_CANE_LEAF

        if self.stage == 0:
            pygame.draw.line(surf, stem_color, (self.x, self.y), (self.x + sway * 0.5, self.y - 14), 4)
            pygame.draw.circle(surf, leaf_color, (int(self.x + sway * 0.5), int(self.y - 15)), 4)
        elif self.stage == 1:
            pygame.draw.line(surf, stem_color, (self.x, self.y), (self.x + sway * 0.7, self.y - 32), 6)
            pygame.draw.line(surf, node_color, (self.x - 4, self.y - 16), (self.x + 4, self.y - 16), 2)
            tip_x, tip_y = self.x + sway * 0.7, self.y - 32
            pygame.draw.line(surf, leaf_color, (tip_x, tip_y), (tip_x - 12, tip_y - 8), 3)
            pygame.draw.line(surf, leaf_color, (tip_x, tip_y), (tip_x + 12, tip_y - 8), 3)
        else:
            tip_x = self.x + sway
            tip_y = self.y - 56
            pygame.draw.line(surf, stem_color, (self.x, self.y), (tip_x, tip_y), 8)

            for fraction in (0.28, 0.56, 0.82):
                nx = self.x + (tip_x - self.x) * fraction
                ny = self.y + (tip_y - self.y) * fraction
                pygame.draw.line(surf, node_color, (nx - 5, ny), (nx + 5, ny), 3)

            pygame.draw.line(surf, leaf_color, (tip_x, tip_y), (tip_x - 20, tip_y - 12), 4)
            pygame.draw.line(surf, leaf_color, (tip_x, tip_y), (tip_x + 20, tip_y - 12), 4)
            pygame.draw.line(surf, leaf_color, (tip_x, tip_y), (tip_x - 14, tip_y - 24), 3)
            pygame.draw.line(surf, leaf_color, (tip_x, tip_y), (tip_x + 14, tip_y - 24), 3)

            if self.stage == 3 and random.random() < 0.2:
                sx = tip_x + random.randint(-16, 16)
                sy = tip_y + random.randint(-16, 20)
                pygame.draw.circle(surf, COLOR_WHITE, (int(sx), int(sy)), random.randint(1, 3))

class Beetle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = random.uniform(-1.2, 1.2)
        self.vy = random.uniform(-1.2, 1.2)
        self.radius = 12
        self.timer = random.randint(40, 120)

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.vx, self.vy = random.uniform(-1.6, 1.6), random.uniform(-1.6, 1.6)
            self.timer = random.randint(60, 140)
        self.x = max(50, min(SCREEN_WIDTH - 50, self.x + self.vx))
        self.y = max(80, min(SCREEN_HEIGHT - 50, self.y + self.vy))

    def draw(self, surf):
        pygame.draw.circle(surf, (120, 28, 64), (int(self.x), int(self.y)), self.radius)
        ang = math.atan2(self.vy, self.vx)
        pygame.draw.circle(surf, (40, 10, 20), (int(self.x + math.cos(ang) * 10), int(self.y + math.sin(ang) * 10)), 6)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 4.8
        self.facing_angle = 0
        self.slash_active = False
        self.slash_timer = 0
        self.slash_duration = 12
        self.slash_range = 64
        self.slash_arc_deg = 110

    def move(self, dx, dy, rush_active=False):
        curr_speed = self.speed * (1.5 if rush_active else 1.0)
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * curr_speed
            self.y += (dy / dist) * curr_speed
            self.facing_angle = math.atan2(dy, dx)

        self.x = max(40, min(SCREEN_WIDTH - 40, self.x))
        self.y = max(90, min(SCREEN_HEIGHT - 40, self.y))

    def swing(self):
        if not self.slash_active:
            self.slash_active = True
            self.slash_timer = self.slash_duration
            return True
        return False

    def update(self):
        if self.slash_active:
            self.slash_timer -= 1
            if self.slash_timer <= 0:
                self.slash_active = False

    def draw(self, surf, time_ticks):
        pygame.draw.ellipse(surf, (30, 80, 35), (self.x - 18, self.y + 10, 36, 14))
        walk_bob = math.sin(time_ticks * 0.3) * 2 if self.slash_active else 0
        py = self.y + walk_bob

        pygame.draw.circle(surf, (226, 178, 92), (int(self.x), int(py)), 19)
        pygame.draw.circle(surf, (244, 200, 115), (int(self.x), int(py)), 13)
        pygame.draw.circle(surf, (200, 40, 40), (int(self.x), int(py)), 14, 2)

        if self.slash_active:
            progress = 1.0 - (self.slash_timer / self.slash_duration)
            arc_sweep = math.radians(self.slash_arc_deg)
            start_ang = self.facing_angle - (arc_sweep / 2)
            cur_ang = start_ang + arc_sweep * progress

            blade_len = 46
            bx = self.x + math.cos(cur_ang) * blade_len
            by = py + math.sin(cur_ang) * blade_len

            pygame.draw.line(surf, (230, 240, 255), (self.x, py), (bx, by), 6)
            pygame.draw.line(surf, COLOR_WHITE, (self.x, py), (bx, by), 2)

            swoosh_pts = []
            for a in [cur_ang - 0.35, cur_ang - 0.18, cur_ang]:
                swoosh_pts.append((self.x + math.cos(a) * (blade_len + 8),
                                   py + math.sin(a) * (blade_len + 8)))
            if len(swoosh_pts) > 1:
                pygame.draw.lines(surf, COLOR_WHITE, False, swoosh_pts, 4)

class MainGame:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        except Exception:
            pass

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SUGAR RUSH")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arialblack", 20)

        self.sfx_slice  = create_sound(700, 180, 0.14, "sine", 0.35)
        self.sfx_pop    = create_sound(300, 850, 0.08, "triangle", 0.25)
        self.sfx_gold   = create_sound(400, 1200, 0.28, "square", 0.20)
        self.sfx_rush   = create_sound(260, 980, 0.45, "sine", 0.40)
        self.sfx_squish = create_sound(200, 80, 0.15, "noise", 0.35)

        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.canes = []
        self.beetles = []
        self.particles = []
        self.floating_texts = []

        self.sugar_kilos = 0
        self.canes_cut = 0
        self.combo = 0
        self.combo_timer = 0
        self.sugar_meter = 0
        self.rush_active = False
        self.rush_timer = 0

        self.shake_magnitude = 0
        self.ticks = 0

        for _ in range(35):
            self.spawn_cane(random_stage=True)

    def play_sound(self, sound):
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def trigger_screenshake(self, amount):
        self.shake_magnitude = max(self.shake_magnitude, amount)

    def spawn_cane(self, random_stage=False):
        margin = 60
        x = random.randint(margin, SCREEN_WIDTH - margin)
        y = random.randint(margin + 50, SCREEN_HEIGHT - margin)

        for c in self.canes:
            if math.hypot(c.x - x, c.y - y) < 45:
                return

        cane = SugarCane(x, y)
        if random_stage:
            cane.stage = random.choice([0, 1, 2, 2, 3])
        self.canes.append(cane)

    def handle_slash(self):
        if not self.player.swing():
            return

        self.play_sound(self.sfx_slice)
        hit_anything = False

        for cane in list(self.canes):
            if cane.stage in [2, 3]:
                dist = math.hypot(self.player.x - cane.x, self.player.y - cane.y)
                if dist < self.player.slash_range + cane.hitbox_radius:
                    ang = math.atan2(cane.y - self.player.y, cane.x - self.player.x)
                    diff = (ang - self.player.facing_angle + math.pi) % (2 * math.pi) - math.pi

                    if abs(diff) < math.radians(self.player.slash_arc_deg / 2 + 25):
                        self.harvest_cane(cane)
                        hit_anything = True

        for b in list(self.beetles):
            if math.hypot(self.player.x - b.x, self.player.y - b.y) < self.player.slash_range + b.radius:
                self.beetles.remove(b)
                self.play_sound(self.sfx_squish)
                self.trigger_screenshake(6)
                for _ in range(14):
                    self.particles.append(Particle(b.x, b.y, random.uniform(-4, 4), random.uniform(-4, 4), (160, 30, 80), random.randint(3, 5), life=25))
                self.floating_texts.append(FloatingText(b.x, b.y, "PEST BUST!", COLOR_GOLD_LEAF, 20))
                hit_anything = True

        if hit_anything:
            self.combo += 1
            self.combo_timer = 90

    def harvest_cane(self, cane):
        is_gold = (cane.stage == 3)
        self.canes.remove(cane)
        self.canes_cut += 1

        for _ in range(16 if not is_gold else 28):
            color = random.choice([COLOR_CANE_STEM, COLOR_CANE_LEAF, (220, 245, 160)]) if not is_gold else \
                    random.choice([COLOR_GOLD_STEM, COLOR_GOLD_LEAF, COLOR_WHITE])
            self.particles.append(Particle(cane.x, cane.y - 25, random.uniform(-5, 5), random.uniform(-6, 2),
                                           color, random.randint(3, 7), life=35))

        for _ in range(8):
            self.particles.append(Particle(cane.x, cane.y - 30, random.uniform(-3, 3), random.uniform(-4, 1),
                                           COLOR_WHITE, random.randint(2, 4), life=22, shape="spark"))

        mult = 3 if self.rush_active else 1
        gained_kg = (5 if not is_gold else 18) * mult
        self.sugar_kilos += gained_kg

        if not self.rush_active:
            self.sugar_meter += 8 if not is_gold else 20
            if self.sugar_meter >= 100:
                self.rush_active = True
                self.rush_timer = 7 * FPS
                self.play_sound(self.sfx_rush)
                self.trigger_screenshake(12)
                self.floating_texts.append(FloatingText(self.player.x, self.player.y - 50, "★ SUGAR RUSH! ★", COLOR_RUSH_PINK, 28))

        self.trigger_screenshake(5 if not is_gold else 9)

        txt = f"+{gained_kg}kg!" if not is_gold else f"SWEET GOLD! +{gained_kg}kg!"
        col = COLOR_WHITE if not is_gold else COLOR_GOLD
        self.floating_texts.append(FloatingText(cane.x, cane.y - 35, txt, col, 22 if not is_gold else 26))

        if is_gold:
            self.play_sound(self.sfx_gold)
        else:
            self.play_sound(self.sfx_pop)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            self.ticks += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.handle_slash()

            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                self.player.facing_angle = math.atan2(my - self.player.y, mx - self.player.x)
                self.handle_slash()

            keys = pygame.key.get_pressed()
            dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
            dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
            self.player.move(dx, dy, self.rush_active)
            self.player.update()

            for cane in self.canes:
                cane.update(self.ticks)

            if len(self.canes) < 32 and random.random() < 0.08:
                self.spawn_cane()

            if len(self.beetles) < 4 and random.random() < 0.015:
                self.beetles.append(Beetle(random.choice([0, SCREEN_WIDTH]), random.randint(100, SCREEN_HEIGHT - 100)))
            for b in self.beetles:
                b.update()

            if self.combo_timer > 0:
                self.combo_timer -= 1
                if self.combo_timer <= 0:
                    self.combo = 0

            if self.rush_active:
                self.rush_timer -= 1
                self.sugar_meter = (self.rush_timer / (7 * FPS)) * 100
                if self.rush_timer <= 0:
                    self.rush_active = False
                    self.sugar_meter = 0

            for p in list(self.particles):
                p.update()
                if p.life <= 0:
                    self.particles.remove(p)

            for ft in list(self.floating_texts):
                ft.update()
                if ft.life <= 0:
                    self.floating_texts.remove(ft)

            if self.shake_magnitude > 0:
                self.shake_magnitude *= 0.88
                if self.shake_magnitude < 0.5:
                    self.shake_magnitude = 0

            offset_x, offset_y = 0, 0
            if self.shake_magnitude > 0:
                offset_x = random.uniform(-self.shake_magnitude, self.shake_magnitude)
                offset_y = random.uniform(-self.shake_magnitude, self.shake_magnitude)

            view_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            view_surf.fill(COLOR_GRASS_BG)

            for tx in range(0, SCREEN_WIDTH, 64):
                for ty in range(60, SCREEN_HEIGHT, 64):
                    if (tx // 64 + ty // 64) % 2 == 0:
                        pygame.draw.rect(view_surf, COLOR_GRASS_DARK, (tx, ty, 64, 64))

            if self.rush_active:
                pulse = abs(math.sin(self.ticks * 0.15)) * 45
                rush_ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                rush_ov.fill((255, 60, 140, int(25 + pulse)))
                view_surf.blit(rush_ov, (0, 0))

            for cane in sorted(self.canes, key=lambda c: c.y):
                cane.draw(view_surf, self.ticks)

            for b in self.beetles:
                b.draw(view_surf)

            self.player.draw(view_surf, self.ticks)

            for p in self.particles:
                p.draw(view_surf)

            for ft in self.floating_texts:
                ft.draw(view_surf)

            self.screen.blit(view_surf, (offset_x, offset_y))

            pygame.draw.rect(self.screen, (25, 45, 20), (0, 0, SCREEN_WIDTH, 50))
            pygame.draw.line(self.screen, (60, 110, 50), (0, 50), (SCREEN_WIDTH, 50), 2)

            combo_str = f" | {self.combo}x COMBO!" if self.combo > 1 else ""
            hud_text = self.font.render(
                f"Sugar: {self.sugar_kilos} kg  | Canes: {self.canes_cut}{combo_str}",
                True, COLOR_GOLD if self.combo > 1 else COLOR_WHITE
            )
            self.screen.blit(hud_text, (20, 12))
            pygame.draw.rect(self.screen, (40, 40, 40), (740, 14, 180, 22), border_radius=6)
            fill_w = int((self.sugar_meter / 100) * 176)
            if fill_w > 0:
                pygame.draw.rect(self.screen, COLOR_RUSH_PINK if self.rush_active else (255, 170, 40), (742, 16, fill_w, 18), border_radius=4)
            pygame.draw.rect(self.screen, COLOR_WHITE, (740, 14, 180, 22), 2, border_radius=6)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    MainGame().run()