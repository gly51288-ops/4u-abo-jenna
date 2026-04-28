import pygame
import os
from settings import settings


# ================= AUDIO MANAGER =================
class AudioManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            print("⚠️ Mixer not initialized, trying to init...")
            try:
                pygame.mixer.init()
            except Exception as e:
                print("❌ Mixer failed:", e)
                return

        self.sounds = {}
        self.channels = {}

        pygame.mixer.set_num_channels(16)
        self._init_channels()

        print("🔊 AudioManager Ready")

    # ================= CHANNELS =================
    def _init_channels(self):
        try:
            self.channels["jump"] = pygame.mixer.Channel(1)
            self.channels["coin"] = pygame.mixer.Channel(2)
            self.channels["ui"] = pygame.mixer.Channel(3)
        except Exception as e:
            print("⚠️ Channel error:", e)

    # ================= LOAD =================
    def load_sound(self, name, file, volume=1.0):
        if name in self.sounds:
            return self.sounds[name]

        path = settings.paths.sound(file)

        if not os.path.exists(path):
            print(f"❌ Missing sound: {file}")
            return None

        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self.sounds[name] = sound
            print(f"✅ Loaded: {name}")
            return sound

        except Exception as e:
            print(f"❌ Load error ({file}):", e)
            return None

    # ================= PLAY =================
    def play(self, name, loops=0):
        sound = self.sounds.get(name)

        if not sound:
            return  # 🔥 بدون ازعاج ولا كراش

        try:
            if name in self.channels:
                ch = self.channels[name]
                ch.stop()
                ch.play(sound, loops=loops)
            else:
                sound.stop()
                sound.play(loops=loops)

        except Exception as e:
            print(f"❌ Play error ({name}):", e)

    # ================= STOP =================
    def stop(self, name):
        try:
            if name in self.channels:
                self.channels[name].stop()
        except:
            pass

    # ================= MUSIC =================
    def play_music(self, file, volume=0.4, loop=True):
        path = settings.paths.sound(file)

        if not os.path.exists(path):
            print(f"❌ Missing music: {file}")
            return

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
            print("🎵 Music started")
        except Exception as e:
            print("❌ Music error:", e)

    def stop_music(self):
        pygame.mixer.music.stop()

    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        pygame.mixer.music.unpause()


# ================= GLOBAL =================
audio = None


# ================= INIT =================
def init_audio():
    global audio

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        audio = AudioManager()

        if audio:
            # 🔥 تحميل الأصوات هنا (آمن)
            audio.load_sound("jump", "jump.wav", 0.6)
            audio.load_sound("coin", "coin.wav", 0.7)

        print("✅ Audio Initialized")

    except Exception as e:
        print("❌ Audio Init Failed:", e)
        audio = None