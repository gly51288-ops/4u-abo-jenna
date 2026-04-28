import pygame
from dataclasses import dataclass, field, asdict
from typing import Tuple, Dict
import json
import os


# ================= PATH MANAGER =================
class PathManager:
    def __init__(self):
        self.base = os.path.dirname(os.path.abspath(__file__))

    def get(self, *paths):
        return os.path.join(self.base, *paths)

    def exists(self, *paths):
        return os.path.exists(self.get(*paths))


paths_manager = PathManager()


# ================= PROFILES =================
PROFILES = {
    "LOW": {"FPS": 60, "VSYNC": False, "CAMERA_SMOOTHNESS": 4},
    "MEDIUM": {"FPS": 60, "VSYNC": True, "CAMERA_SMOOTHNESS": 5},
    "HIGH": {"FPS": 120, "VSYNC": True, "CAMERA_SMOOTHNESS": 6},
}


# ================= CORE =================
@dataclass
class Core:
    width: int = 900
    height: int = 500
    fps: int = 60
    title: str = "Ninja Game"
    fullscreen: bool = False
    vsync: bool = True


# ================= COLORS =================
@dataclass
class Colors:
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    BLACK: Tuple[int, int, int] = (0, 0, 0)
    GREEN: Tuple[int, int, int] = (0, 200, 0)
    BLUE: Tuple[int, int, int] = (0, 200, 255)
    GRAY: Tuple[int, int, int] = (120, 120, 120)
    RED: Tuple[int, int, int] = (220, 60, 60)


# ================= WORLD =================
@dataclass
class WorldConfig:
    width: int = 9000
    ground_offset: int = 80

    def ground_y(self, screen_height):
        return screen_height - self.ground_offset


# ================= PLAYER =================
@dataclass
class PlayerConfig:
    width: int = 60
    height: int = 70

    max_speed: float = 300
    acceleration: float = 1800
    friction: float = 1500

    gravity: float = 2000
    jump_force: float = -700


# ================= CAMERA =================
@dataclass
class CameraConfig:
    smoothness: float = 5.0
    deadzone_x: int = 100


# ================= UI =================
@dataclass
class UI:
    button_w: int = 240
    button_h: int = 70
    font_name: str = "arial"
    font_size: int = 30


# ================= INPUT =================
@dataclass
class InputConfig:
    keys: Dict[str, int] = field(default_factory=lambda: {
        "LEFT": pygame.K_LEFT,
        "RIGHT": pygame.K_RIGHT,
        "JUMP": pygame.K_SPACE,
    })


# ================= PATHS =================
@dataclass
class Paths:
    save: str = "save.json"

    # ===== IMAGES =====
    def image(self, name):
        possible_paths = [
            paths_manager.get("assets", "images", name),
            paths_manager.get("images", name),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        print(f"⚠️ Missing image: {name}")
        return None  # 🔥 مهم

    # ===== SOUND (احترافي) =====
    def sound(self, name):
        possible_paths = [
            paths_manager.get("audio", name),           # ⭐ الأساسي
            paths_manager.get("assets", "audio", name),
            paths_manager.get("sounds", name),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"🔊 Found sound: {path}")
                return path

        print(f"❌ Sound NOT FOUND: {name}")
        return None  # 🔥 لا ترجع مسار وهمي

    def save_path(self):
        return paths_manager.get(self.save)


# ================= DEBUG =================
@dataclass
class Debug:
    enabled: bool = False
    show_fps: bool = True
    show_hitbox: bool = False


# ================= SETTINGS =================
class Settings:
    def __init__(self):
        self.core = Core()
        self.colors = Colors()
        self.world = WorldConfig()
        self.player = PlayerConfig()
        self.camera = CameraConfig()
        self.ui = UI()
        self.input = InputConfig()
        self.paths = Paths()
        self.debug = Debug()

        self._print_info()
        self.load()

    def _print_info(self):
        print("📁 Project Path:", paths_manager.base)
        print("🎮 FPS:", self.core.fps)

    def apply_profile(self, name="MEDIUM"):
        p = PROFILES.get(name.upper(), PROFILES["MEDIUM"])
        self.core.fps = p["FPS"]
        self.core.vsync = p["VSYNC"]
        self.camera.smoothness = p["CAMERA_SMOOTHNESS"]

    def save(self):
        try:
            data = {
                "core": asdict(self.core),
                "player": asdict(self.player)
            }

            with open(self.paths.save_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print("💾 Settings saved")

        except Exception as e:
            print("❌ Save error:", e)

    def load(self):
        try:
            path = self.paths.save_path()

            if not os.path.exists(path):
                print("ℹ️ No save file found")
                return

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for k, v in data.get("core", {}).items():
                setattr(self.core, k, v)

            for k, v in data.get("player", {}).items():
                setattr(self.player, k, v)

            print("✅ Settings loaded")

        except Exception as e:
            print("❌ Load error:", e)


# ================= GLOBAL =================
settings = Settings()