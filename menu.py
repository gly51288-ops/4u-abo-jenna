# menu.py

import pygame
from settings import settings   # ✔ الصحيح


class MenuScreen:
    def __init__(self, screen):
        self.screen = screen

        self.font_big = pygame.font.Font(None, 70)
        self.font_small = pygame.font.Font(None, 36)

        # استخدم الإعدادات الصحيحة
        self.button = pygame.Rect(
            settings.core.width // 2 - 120,
            settings.core.height // 2,
            240,
            70
        )

        self.color = settings.colors.GRAY

    # ================= EVENTS =================
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button.collidepoint(event.pos):
                return True
        return False

    # ================= UPDATE =================
    def update(self):
        if self.button.collidepoint(pygame.mouse.get_pos()):
            self.color = (90, 90, 90)
        else:
            self.color = settings.colors.GRAY

    # ================= DRAW =================
    def draw(self):
        self.screen.fill((30, 30, 30))

        title = self.font_big.render(
            "GAME", True, settings.colors.WHITE
        )

        self.screen.blit(
            title,
            (
                settings.core.width // 2 - title.get_width() // 2,
                120
            )
        )

        pygame.draw.rect(
            self.screen,
            self.color,
            self.button,
            border_radius=12
        )

        text = self.font_small.render(
            "START GAME", True, settings.colors.WHITE
        )

        self.screen.blit(
            text,
            (
                self.button.centerx - text.get_width() // 2,
                self.button.centery - text.get_height() // 2
            )
        )