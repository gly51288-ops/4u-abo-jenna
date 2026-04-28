import pygame
import sys
import traceback
from settings import settings
from game import Game
import audio


# ================= AUDIO PRE-INIT =================
pygame.mixer.pre_init(44100, -16, 2, 256)


class App:
    def __init__(self):
        pygame.init()

        self._init_mixer()
        self.audio = self._init_audio_system()

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

        self.screen = pygame.display.set_mode(
            (settings.core.width, settings.core.height),
            pygame.RESIZABLE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption(settings.core.title)

        self.clock = pygame.time.Clock()
        self.running = True
        self.events = []

        self.game = Game(self.screen)
        self.font = pygame.font.SysFont("consolas", 16)

        # 🔥 تحميل الأصوات
        self._init_audio_assets()

    # ================= MIXER =================
    def _init_mixer(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
                print("✅ Mixer initialized")
            except Exception as e:
                print("❌ Mixer init failed:", e)

    # ================= AUDIO SYSTEM =================
    def _init_audio_system(self):
        try:
            audio.init_audio()

            if getattr(audio, "audio", None) is None:
                print("❌ Audio system failed")
                return None

            print("✅ Audio system ready")
            return audio.audio

        except Exception as e:
            print("❌ Audio init error:", e)
            return None

    # ================= AUDIO ASSETS =================
    def _init_audio_assets(self):
        if not self.audio:
            print("⚠️ No audio system")
            return

        try:
            # 🔥 تحميل جميع الأصوات هنا
            self.audio.load_sound("jump", "jump.wav", 0.6)
            self.audio.load_sound("coin", "coin.wav", 0.8)  # ✅ مهم جداً

            # 🎵 موسيقى (اختياري)
            self.audio.play_music("music.mp3", volume=0.3)

            print("✅ Audio assets loaded")

        except Exception as e:
            print("❌ Audio assets error:", e)

    # ================= EVENTS =================
    def _poll_events(self):
        self.events = pygame.event.get()

        for e in self.events:
            if e.type == pygame.QUIT:
                self.running = False

            elif e.type == pygame.VIDEORESIZE:
                self._resize(e.w, e.h)

    # ================= RESIZE =================
    def _resize(self, w, h):
        settings.core.width = w
        settings.core.height = h

        self.screen = pygame.display.set_mode(
            (w, h),
            pygame.RESIZABLE | pygame.DOUBLEBUF
        )

        self.game.screen = self.screen

        if hasattr(self.game, "on_resize"):
            self.game.on_resize()

    # ================= RUN =================
    def run(self):
        try:
            while self.running:
                dt = min(self.clock.tick(settings.core.fps) / 1000.0, 0.05)

                self._poll_events()

                self.game.handle(self.events)
                self.game.update(dt)

                self.screen.fill((20, 20, 20))
                self.game.draw()

                # ===== FPS =====
                fps = int(self.clock.get_fps())
                fps_text = self.font.render(f"FPS: {fps}", True, (255, 255, 0))
                self.screen.blit(fps_text, (10, 10))

                pygame.display.flip()

        except Exception:
            print("🔥 CRASH:")
            print(traceback.format_exc())

        finally:
            pygame.quit()
            sys.exit()


# ================= START =================
if __name__ == "__main__":
    App().run()