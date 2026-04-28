import os
import pygame
import traceback
from settings import settings
from levels import levels
from mobile_controls import MobileControls


# ================= IMAGE CACHE =================
_IMAGE_CACHE = {}
_SCALED_CACHE = {}


def load_any_image(*names):
    for name in names:
        if name in _IMAGE_CACHE:
            return _IMAGE_CACHE[name]

        path = settings.paths.image(name)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                _IMAGE_CACHE[name] = img
                return img
            except Exception as e:
                print("❌ image error:", e)
    return None


def get_scaled(img, size):
    key = (id(img), size)
    if key in _SCALED_CACHE:
        return _SCALED_CACHE[key]

    scaled = pygame.transform.smoothscale(img, size)
    _SCALED_CACHE[key] = scaled
    return scaled


# ================= SCENE BASE =================
class Scene:
    def enter(self, game): pass
    def handle(self, game, events): pass
    def update(self, game, dt): pass
    def draw(self, game): pass
    def on_resize(self, game): pass


# ================= SCENE MANAGER =================
class SceneManager:
    def __init__(self):
        self.current = None

    def set(self, scene, game):
        try:
            self.current = scene
            scene.enter(game)
        except Exception:
            print("🔥 Scene load crash:")
            print(traceback.format_exc())

    def handle(self, game, events):
        if self.current:
            self.current.handle(game, events)

    def update(self, game, dt):
        if self.current:
            self.current.update(game, dt)

    def draw(self, game):
        if self.current:
            self.current.draw(game)

    def on_resize(self, game):
        if self.current:
            self.current.on_resize(game)


# ================= MENU =================
class MenuScene(Scene):
    def enter(self, game):
        self.raw_bg = load_any_image("menu_bg.png", "background.png")
        self.bg = None
        self._resize_bg()

    def _resize_bg(self):
        if self.raw_bg:
            self.bg = get_scaled(
                self.raw_bg,
                (settings.core.width, settings.core.height)
            )

    def handle(self, game, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                try:
                    game.scenes.set(PlayScene(), game)
                except Exception:
                    print("🔥 Start crash:")
                    print(traceback.format_exc())

    def on_resize(self, game):
        self._resize_bg()

    def draw(self, game):
        if self.bg:
            game.screen.blit(self.bg, (0, 0))
        else:
            game.screen.fill((30, 30, 30))

        txt = game.font.render("START (TOUCH)", True, (255, 255, 255))
        game.screen.blit(txt, (50, 50))


# ================= PLAY =================
class PlayScene(Scene):
    def enter(self, game):
        try:
            from player import Player
            from camera import Camera
            from world import World

            self.player = Player()
            self.world = World(self.player)
            self.camera = Camera()

            self.level_index = 1
            self.level_index = max(0, min(self.level_index, len(levels) - 1))

            self._load_level()

            self.camera.set_targets([self.player])
            self.camera.set_world(self.world)

            self.mobile = MobileControls(
                settings.core.width,
                settings.core.height
            )

            self.ui_font = pygame.font.SysFont("arial", 26, bold=True)
            self.small_font = pygame.font.SysFont("arial", 18, bold=True)

        except Exception:
            print("🔥 PlayScene crash:")
            print(traceback.format_exc())

    def _load_level(self):
        try:
            self.level = levels[self.level_index]
            self.world.width = self.level.get("world_width", settings.world.width)
            self.world.load_level(self.level)

            spawn = self.level.get("spawn", (100, 0))
            self.player.reset(spawn=spawn, ground_y=self.world.ground_y)

            self.camera.pos.x = 0

            print(f"✅ Loaded: {self.level.get('name', 'Level')}")

        except Exception:
            print("🔥 Level load crash:")
            print(traceback.format_exc())

    def on_resize(self, game):
        if hasattr(self.mobile, "on_resize"):
            self.mobile.on_resize(settings.core.width, settings.core.height)

        if hasattr(self.world, "on_resize"):
            self.world.on_resize()

    def handle(self, game, events):
        self.mobile.handle(events)

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    self._load_level()

    def update(self, game, dt):
        try:
            keys = pygame.key.get_pressed()
            mobile = self.mobile.get_input()

            self.player.update(dt, keys, mobile)
            self.world.update(dt)
            self.camera.update(dt)

        except Exception:
            print("🔥 Update crash:")
            print(traceback.format_exc())

    def draw(self, game):
        self.world.draw(game.screen, self.camera.pos.x)
        self.player.draw(game.screen, self.camera)
        self.mobile.draw(game.screen)


# ================= GAME =================
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", settings.ui.font_size)

        self.scenes = SceneManager()
        self.scenes.set(MenuScene(), self)

    def handle(self, events):
        self.scenes.handle(self, events)

    def update(self, dt):
        self.scenes.update(self, dt)

    def draw(self):
        self.scenes.draw(self)

    def on_resize(self):
        self.scenes.on_resize(self)