import os
import math
import random
import pygame
from settings import settings

GROUND_COLOR = (100, 70, 50)
GROUND_SHADOW = (60, 40, 30)
SKY_COLOR = (120, 180, 255)
PLATFORM_COLOR = (140, 100, 70)
PLATFORM_TOP = (180, 140, 100)
PLATFORM_SHADOW = (80, 60, 40)

COIN_GOLD = (245, 198, 48)
COIN_HIGHLIGHT = (255, 240, 170)
COIN_SHADOW = (180, 120, 20)


def load_any_image(*names):
    for name in names:
        path = settings.paths.image(name)
        if os.path.exists(path):
            try:
                return pygame.image.load(path).convert()
            except Exception:
                pass
    return None


class World:
    def __init__(self, player):
        self.player = player

        self.width = settings.world.width
        self.height = settings.core.height
        self.ground_y = settings.world.ground_y(self.height)

        self.background = load_any_image("background.png", "bg.png")
        if self.background:
            self.background = pygame.transform.scale(
                self.background,
                (settings.core.width, settings.core.height)
            )

        self.platforms = []
        self.platform_cache = []
        self.landing_tolerance = 10

        self.coins = []
        self.coin_frames = self._build_coin_frames(size=26, frame_count=12)
        self.coin_sound = self._load_sound("coin.wav")
        self.coin_count = 0
        self.total_coin_count = 0

        self.particles = []
        self.time = 0.0

        if not hasattr(self.player, "coins"):
            self.player.coins = 0

    # ================= SOUND =================
    def _load_sound(self, name):
        try:
            path = settings.paths.sound(name)
            if os.path.exists(path):
                return pygame.mixer.Sound(path)
        except Exception:
            pass
        return None

    # ================= COIN SPRITES =================
    def _build_coin_frames(self, size=26, frame_count=12):
        frames = []
        for i in range(frame_count):
            surf = pygame.Surface((size, size), pygame.SRCALPHA)

            t = i / frame_count
            squash = 0.18 + 0.82 * abs(math.cos(t * math.pi * 2))
            coin_w = max(4, int(size * squash))
            x = (size - coin_w) // 2

            rect = pygame.Rect(x, 0, coin_w, size)

            pygame.draw.ellipse(surf, COIN_GOLD, rect)
            shine_w = max(2, coin_w // 3)
            pygame.draw.ellipse(
                surf,
                COIN_HIGHLIGHT,
                (x + 3, 4, shine_w, size - 8)
            )
            pygame.draw.ellipse(surf, COIN_SHADOW, rect, 2)

            frames.append(surf)

        return frames

    # ================= RESIZE =================
    def on_resize(self):
        self.height = settings.core.height
        self.ground_y = settings.world.ground_y(self.height)

        if self.background:
            self.background = pygame.transform.scale(
                self.background,
                (settings.core.width, settings.core.height)
            )

    # ================= LOAD LEVEL =================
    def load_level(self, data):
        self.platforms.clear()
        self.platform_cache.clear()
        self.coins.clear()
        self.particles.clear()

        self.coin_count = 0
        self.total_coin_count = 0
        self.time = 0.0

        self.width = data.get("world_width", self.width)

        # ===== المنصات =====
        for p in data.get("platforms", []):
            x, y, w, h = p[:4]
            p_type = p[4] if len(p) > 4 else "static"
            options = p[5] if len(p) > 5 and isinstance(p[5], dict) else {}

            top_y = self.ground_y + y
            rect = pygame.Rect(x, top_y, w, h)

            self.platforms.append({
                "rect": rect,
                "type": p_type,
                "start_x": float(x),
                "start_y": float(top_y),
                "range": float(options.get("range", 0)),
                "speed": float(options.get("speed", 0)),
                "axis": options.get("axis", "x"),
                "dir": 1,
                "dx": 0.0,
                "dy": 0.0,
                "min_x": float(x) - float(options.get("range", 0)),
                "max_x": float(x) + float(options.get("range", 0)),
                "min_y": float(top_y) - float(options.get("range", 0)),
                "max_y": float(top_y) + float(options.get("range", 0)),
            })

            surf = pygame.Surface((w, h))
            surf.fill(PLATFORM_COLOR)
            top_h = max(2, h // 5)
            pygame.draw.rect(surf, PLATFORM_TOP, (0, 0, w, top_h))
            pygame.draw.rect(surf, PLATFORM_SHADOW, (0, h - top_h, w, top_h))
            self.platform_cache.append(surf)

        # ===== الكوينز =====
        for c in data.get("coins", []):
            if isinstance(c, dict):
                x = float(c.get("x", 0))
                y = float(c.get("y", 0))
                value = int(c.get("value", 1))
            else:
                x = float(c[0])
                y = float(c[1])
                value = int(c[2]) if len(c) > 2 else 1

            base_y = self.ground_y + y

            self.coins.append({
                "x": x,
                "base_y": base_y,
                "y": base_y,
                "phase": (x * 0.017 + base_y * 0.031) % (math.pi * 2),
                "radius": 11,
                "value": value,
            })

        self.total_coin_count = len(self.coins)

    # ================= EFFECTS =================
    def _spawn_coin_effect(self, x, y):
        # Glow
        self.particles.append({
            "type": "glow",
            "x": x,
            "y": y,
            "radius": 10,
            "life": 0.35
        })

        # Sparks
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(80, 200)

            self.particles.append({
                "type": "spark",
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.uniform(0.25, 0.55),
                "size": random.randint(2, 4)
            })

        if self.coin_sound:
            try:
                self.coin_sound.play()
            except Exception:
                pass

    # ================= UPDATE =================
    def update(self, dt):
        self.time += dt
        p = self.player

        # =========================================================
        # 1) تحديث المنصات أولاً
        # =========================================================
        for plat in self.platforms:
            plat["dx"] = 0.0
            plat["dy"] = 0.0

            if plat["type"] != "moving":
                continue

            step = plat["speed"] * dt * plat["dir"]
            rect = plat["rect"]

            if plat["axis"] == "x":
                old_x = rect.x
                rect.x += step

                if rect.x <= plat["min_x"]:
                    rect.x = plat["min_x"]
                    plat["dir"] = 1
                elif rect.x >= plat["max_x"]:
                    rect.x = plat["max_x"]
                    plat["dir"] = -1

                plat["dx"] = rect.x - old_x

            else:
                old_y = rect.y
                rect.y += step

                if rect.y <= plat["min_y"]:
                    rect.y = plat["min_y"]
                    plat["dir"] = 1
                elif rect.y >= plat["max_y"]:
                    rect.y = plat["max_y"]
                    plat["dir"] = -1

                plat["dy"] = rect.y - old_y

        # =========================================================
        # 2) حمل اللاعب مع المنصة التي كان واقفًا عليها سابقًا
        # =========================================================
        prev_platform_index = getattr(p, "current_platform", None)
        if prev_platform_index is not None and 0 <= prev_platform_index < len(self.platforms):
            prev_plat = self.platforms[prev_platform_index]
            p.pos.x += prev_plat["dx"]
            p.pos.y += prev_plat["dy"]

        # =========================================================
        # 3) حفظ الحالة السابقة
        # =========================================================
        prev_x = p.pos.x
        prev_y = p.pos.y
        prev_bottom = prev_y + p.h
        prev_top = prev_y

        # =========================================================
        # 4) حركة اللاعب أفقياً + تصادم الجوانب
        # =========================================================
        p.pos.x += p.vel.x * dt

        if p.pos.x < 0:
            p.pos.x = 0
            p.vel.x = 0

        if p.pos.x > self.width - p.w:
            p.pos.x = self.width - p.w
            p.vel.x = 0

        for plat in self.platforms:
            rect = plat["rect"]

            if p.pos.y + p.h > rect.top and p.pos.y < rect.bottom:
                if p.vel.x > 0 and prev_x + p.w <= rect.left and p.pos.x + p.w > rect.left:
                    p.pos.x = rect.left - p.w
                    p.vel.x = 0
                elif p.vel.x < 0 and prev_x >= rect.right and p.pos.x < rect.right:
                    p.pos.x = rect.right
                    p.vel.x = 0

        # =========================================================
        # 5) حركة اللاعب عموديًا + تصادم السقف/الأرض
        # =========================================================
        p.pos.y += p.vel.y * dt

        on_ground = False
        p.current_platform = None

        ground_top = self.ground_y - p.h
        if p.pos.y >= ground_top:
            p.pos.y = ground_top
            p.vel.y = 0
            on_ground = True

        for i, plat in enumerate(self.platforms):
            rect = plat["rect"]

            if p.pos.x + p.w > rect.left and p.pos.x < rect.right:

                # هبوط من الأعلى
                if (
                    p.vel.y >= 0 and
                    prev_bottom <= rect.top + self.landing_tolerance and
                    p.pos.y + p.h >= rect.top
                ):
                    p.pos.y = rect.top - p.h
                    p.vel.y = 0
                    on_ground = True
                    p.current_platform = i
                    break

                # ضرب السقف من الأسفل
                elif (
                    p.vel.y < 0 and
                    prev_top >= rect.bottom - self.landing_tolerance and
                    p.pos.y <= rect.bottom
                ):
                    p.pos.y = rect.bottom
                    p.vel.y = 0

        p.on_ground = on_ground

        # =========================================================
        # 6) جمع الكوينز
        # =========================================================
        if self.coins:
            player_rect = p.rect()
            kept_coins = []

            for coin in self.coins:
                r = coin["radius"]
                coin_rect = pygame.Rect(
                    int(coin["x"] - r),
                    int(coin["y"] - r),
                    r * 2,
                    r * 2
                )

                if player_rect.colliderect(coin_rect):
                    self.player.coins = getattr(self.player, "coins", 0) + coin["value"]
                    self.coin_count += coin["value"]
                    self._spawn_coin_effect(coin["x"], coin["y"])
                else:
                    coin["y"] = coin["base_y"] + math.sin(self.time * 5.0 + coin["phase"]) * 6.0
                    kept_coins.append(coin)

            self.coins = kept_coins

        # =========================================================
        # 7) تحديث الـ particles
        # =========================================================
        new_particles = []

        for part in self.particles:
            part["life"] -= dt
            if part["life"] <= 0:
                continue

            if part["type"] == "spark":
                part["x"] += part["vx"] * dt
                part["y"] += part["vy"] * dt
                part["vy"] += 300 * dt

            elif part["type"] == "glow":
                part["radius"] += 80 * dt

            new_particles.append(part)

        self.particles = new_particles

    # ================= DRAW =================
    def draw(self, screen, camera_x):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(SKY_COLOR)

        screen_width = screen.get_width()

        # ===== الأرض =====
        pygame.draw.rect(
            screen,
            GROUND_COLOR,
            (0, self.ground_y, screen_width, self.height - self.ground_y)
        )
        pygame.draw.rect(
            screen,
            GROUND_SHADOW,
            (0, self.ground_y, screen_width, 6)
        )

        # ===== المنصات =====
        for i, plat in enumerate(self.platforms):
            rect = plat["rect"]
            draw_x = int(rect.x - camera_x)

            if draw_x + rect.w < 0 or draw_x > screen_width:
                continue

            screen.blit(self.platform_cache[i], (draw_x, rect.y))

        # ===== الكوينز =====
        for coin in self.coins:
            draw_x = int(coin["x"] - camera_x)
            draw_y = int(coin["y"])

            if draw_x < -30 or draw_x > screen_width + 30:
                continue

            frame_count = len(self.coin_frames)
            frame_index = int((self.time * 10.0 + coin["phase"]) % frame_count)
            img = self.coin_frames[frame_index]

            screen.blit(
                img,
                (draw_x - img.get_width() // 2, draw_y - img.get_height() // 2)
            )

        # ===== particles =====
        for part in self.particles:
            x = int(part["x"] - camera_x)
            y = int(part["y"])

            if part["type"] == "spark":
                pygame.draw.circle(screen, (255, 230, 120), (x, y), part["size"])

            elif part["type"] == "glow":
                alpha = max(0, min(255, int(255 * part["life"] * 2)))
                surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                pygame.draw.circle(
                    surf,
                    (255, 220, 100, alpha),
                    (50, 50),
                    int(part["radius"])
                )
                screen.blit(surf, (x - 50, y - 50))