import pygame
from settings import settings


class Camera:
    def __init__(self):
        self.pos = pygame.Vector2(0, 0)
        self.target = None
        self.world = None  # 🔥 ربط العالم

        # ===== إعدادات =====
        self.smoothness = settings.camera.smoothness
        self.deadzone = settings.camera.deadzone_x

        # 🔥 تقديم اللاعب (مثل ماريو)
        self.look_ahead_ratio = 0.4

    # ================= TARGET =================
    def set_targets(self, targets):
        if targets:
            self.target = targets[0]

    # ================= WORLD =================
    def set_world(self, world):
        self.world = world

    # ================= UPDATE =================
    def update(self, dt):
        if not self.target:
            return

        # ===== مركز اللاعب =====
        player_center = self.target.pos.x + self.target.w / 2

        # ===== مركز الشاشة =====
        screen_center = settings.core.width * self.look_ahead_ratio

        # ===== الهدف =====
        target_x = player_center - screen_center

        # ===== الفرق =====
        diff = target_x - self.pos.x

        # ===== DEADZONE =====
        if abs(diff) > self.deadzone:
            factor = min(1, self.smoothness * dt)
            self.pos.x += diff * factor

        # ===== حدود العالم (🔥 الإصلاح الحقيقي) =====
        if self.world:
            max_x = self.world.width - settings.core.width
        else:
            max_x = 0

        if max_x < 0:
            max_x = 0

        self.pos.x = max(0, min(self.pos.x, max_x))

    # ================= APPLY =================
    def apply(self, rect):
        return pygame.Rect(
            int(rect.x - self.pos.x),
            int(rect.y),
            rect.w,
            rect.h
        )