import pygame


class MobileControls:
    def __init__(self, screen_w, screen_h):
        self._build_layout(screen_w, screen_h)

        # حالة الأزرار
        self.pressed = {k: False for k in self.buttons}

        # تتبع الأصابع
        self.fingers = {}

        # ===== الخط =====
        self.font = pygame.font.SysFont("arial", int(self.size * 0.4))

        self.icons = {
            "left": "◀",
            "right": "▶",
            "jump": "⭡",
            "dash": "⚡"
        }

        # 🔥 كاش للنصوص
        self.icon_cache = {
            name: self.font.render(icon, True, (255, 255, 255))
            for name, icon in self.icons.items()
        }

        # 🔥 كاش للرسم
        self.button_surfaces = {}
        self._build_surfaces()

    # ================= BUILD LAYOUT =================
    def _build_layout(self, screen_w, screen_h):
        self.size = int(screen_h * 0.12)
        margin = int(screen_h * 0.05)

        self.buttons = {
            "left": pygame.Rect(margin, screen_h - self.size - margin, self.size, self.size),
            "right": pygame.Rect(margin + self.size + 20, screen_h - self.size - margin, self.size, self.size),

            "jump": pygame.Rect(screen_w - self.size - margin, screen_h - self.size - margin, self.size, self.size),
            "dash": pygame.Rect(screen_w - self.size - margin, screen_h - self.size*2 - 20, self.size, self.size),
        }

    # ================= BUILD SURFACES =================
    def _build_surfaces(self):
        self.button_surfaces.clear()

        for name, rect in self.buttons.items():

            # 🔘 زر عادي
            normal = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(normal, (255, 255, 255, 50), (0, 0, rect.w, rect.h), border_radius=30)
            pygame.draw.rect(normal, (255, 255, 255, 120), (0, 0, rect.w, rect.h), 3, border_radius=30)

            # 🔘 زر مضغوط
            pressed = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(pressed, (0, 200, 255, 180), (0, 0, rect.w, rect.h), border_radius=30)
            pygame.draw.rect(pressed, (0, 255, 255, 230), (0, 0, rect.w, rect.h), 3, border_radius=30)

            # 🔥 Glow
            glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 200, 255, 40), (0, 0, rect.w, rect.h), border_radius=30)

            self.button_surfaces[name] = {
                "normal": normal,
                "pressed": pressed,
                "glow": glow
            }

    # ================= RESIZE =================
    def on_resize(self, screen_w, screen_h):
        self._build_layout(screen_w, screen_h)
        self._build_surfaces()

    # ================= INPUT =================
    def handle(self, events):
        screen = pygame.display.get_surface()
        sw, sh = screen.get_width(), screen.get_height()

        for e in events:

            # ===== TOUCH DOWN =====
            if e.type == pygame.FINGERDOWN:
                x = int(e.x * sw)
                y = int(e.y * sh)

                for name, rect in self.buttons.items():
                    if rect.collidepoint((x, y)):
                        self.pressed[name] = True
                        self.fingers[e.finger_id] = name
                        break

            # ===== TOUCH UP =====
            elif e.type == pygame.FINGERUP:
                if e.finger_id in self.fingers:
                    btn = self.fingers[e.finger_id]
                    self.pressed[btn] = False
                    del self.fingers[e.finger_id]

            # 🔥 حذفنا FINGERMOTION (كان يسبب تقطيع)

            # ===== MOUSE =====
            elif e.type == pygame.MOUSEBUTTONDOWN:
                for name, rect in self.buttons.items():
                    if rect.collidepoint(e.pos):
                        self.pressed[name] = True

            elif e.type == pygame.MOUSEBUTTONUP:
                for name in self.pressed:
                    self.pressed[name] = False

    # ================= INPUT STATE =================
    def get_input(self):
        return self.pressed

    # ================= DRAW =================
    def draw(self, screen):
        for name, rect in self.buttons.items():

            data = self.button_surfaces[name]

            # Glow
            screen.blit(data["glow"], rect.topleft)

            # Button
            if self.pressed[name]:
                surf = data["pressed"]
            else:
                surf = data["normal"]

            screen.blit(surf, rect.topleft)

            # Icon (🔥 من الكاش)
            txt = self.icon_cache[name]
            screen.blit(
                txt,
                (
                    rect.centerx - txt.get_width() // 2,
                    rect.centery - txt.get_height() // 2
                )
            )