import pygame
import sys
import traceback
import os
from settings import settings
from game import Game


# ================= TIME =================
class Time:
    def __init__(self):
        self.raw_dt = 0
        self.smooth = 0
        self.scale = 1.0

    def update(self, raw_dt):
        self.raw_dt = raw_dt
        self.smooth = self.smooth * 0.9 + raw_dt * 0.1

    def get(self):
        return self.smooth * self.scale


# ================= APP =================
class App:
    def __init__(self):

        # 🔥 تهيئة الصوت (مهم جداً قبل init)
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        # 🔥 السماح بالأحداث (للجوال)
        pygame.event.set_allowed([
            pygame.QUIT,
            pygame.FINGERDOWN,
            pygame.FINGERUP,
            pygame.FINGERMOTION,
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.KEYDOWN,
            pygame.KEYUP,
            pygame.VIDEORESIZE
        ])

        # ===== الشاشة =====
        self.flags = pygame.RESIZABLE

        self.screen = pygame.display.set_mode(
            (settings.core.width, settings.core.height),
            self.flags
        )

        pygame.display.set_caption(settings.core.title)

        # ===== أنظمة =====
        self.clock = pygame.time.Clock()
        self.running = True

        self.time = Time()
        self.events = []

        # ===== Fixed Update =====
        self.accumulator = 0
        self.fixed_dt = 1 / 60

        # ===== Debug =====
        self.debug = True
        self.font = pygame.font.SysFont("consolas", 16)

        print("🚀 GAME STARTED")

        # ===== الصوت =====
        self._init_audio()

        # ===== اللعبة =====
        self.game = Game(self.screen)

    # ================= AUDIO =================
    def _init_audio(self):
        try:
            pygame.mixer.init()

            music_path = "assets/audio/music.mp3"

            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)  # تكرار
                print("🎵 Music started")
            else:
                print("❌ music.mp3 not found")

        except Exception as e:
            print("❌ Audio error:", e)

    # ================= EVENTS =================
    def _poll_events(self):
        self.events = pygame.event.get()

        for e in self.events:
            if e.type == pygame.QUIT:
                self.running = False

            elif e.type == pygame.VIDEORESIZE:
                self._resize(e.w, e.h)

            # 🔊 كتم الصوت
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                        print("🔇 Muted")
                    else:
                        pygame.mixer.music.unpause()
                        print("🔊 Unmuted")

    # ================= RESIZE =================
    def _resize(self, w, h):
        settings.core.width = w
        settings.core.height = h

        self.screen = pygame.display.set_mode((w, h), self.flags)
        self.game.screen = self.screen

    # ================= UPDATE =================
    def _update(self):
        self.game.handle(self.events)

        self.accumulator += self.time.get()

        while self.accumulator >= self.fixed_dt:
            self.game.update(self.fixed_dt)
            self.accumulator -= self.fixed_dt

    # ================= DRAW =================
    def _draw(self):
        self.screen.fill((20, 20, 20))

        self.game.draw()

        if self.debug:
            self._draw_debug()

        pygame.display.flip()

    # ================= DEBUG =================
    def _draw_debug(self):
        fps = int(self.clock.get_fps())
        txt = self.font.render(f"FPS: {fps}", True, (255, 255, 255))
        self.screen.blit(txt, (10, 10))

    # ================= RUN =================
    def run(self):
        try:
            while self.running:
                raw_dt = self.clock.tick(60) / 1000
                self.time.update(raw_dt)

                self._poll_events()
                self._update()
                self._draw()

        except Exception:
            error = traceback.format_exc()
            print(error)

            self.screen.fill((0, 0, 0))
            y = 20

            for line in error.split("\n"):
                txt = self.font.render(line, True, (255, 0, 0))
                self.screen.blit(txt, (20, y))
                y += 20

            pygame.display.flip()

            # انتظار
            waiting = True
            while waiting:
                for e in pygame.event.get():
                    if e.type in (pygame.QUIT, pygame.KEYDOWN):
                        waiting = False

        finally:
            pygame.quit()
            sys.exit()


# ================= START =================
if __name__ == "__main__":
    App().run()