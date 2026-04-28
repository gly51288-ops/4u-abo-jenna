import os
import pygame
from settings import settings


# ================= LOAD IMAGE =================
def load_any_image(*names):
    for name in names:
        path = settings.paths.image(name)
        if os.path.exists(path):
            try:
                return pygame.image.load(path).convert_alpha()
            except Exception:
                pass
    return None


# ================= PLAYER =================
class Player:
    def __init__(self):
        # ===== الحجم =====
        self.w = settings.player.width
        self.h = settings.player.height

        # ===== الموقع والحركة =====
        self.pos = pygame.Vector2(100, 0)
        self.vel = pygame.Vector2()

        # ===== فيزياء =====
        self.max_speed = settings.player.max_speed
        self.acc = settings.player.acceleration
        self.friction = settings.player.friction
        self.gravity = settings.player.gravity

        # 🔥 قفز أعلى من السابق
        self.jump_force = min(settings.player.jump_force, -900)
        self.air_control = 0.6

        # ===== تحسين القفز =====
        self.jump_cut_multiplier = 0.45   # عند ترك زر القفز مبكراً
        self.max_fall_speed = 1800

        # ===== حالة =====
        self.facing_right = True
        self.on_ground = False
        self.current_platform = None

        # ===== أنظمة احترافية =====
        self.coyote_time_max = 0.10
        self.jump_buffer_max = 0.10
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0

        # ===== صوت =====
        self.jump_sound_cooldown = 0.12
        self.jump_sound_timer = 0.0

        # ===== صورة =====
        self.sprite = load_any_image("ninja.png", "player.png", "hero.png")
        self.sprite_flipped = None

        if self.sprite:
            self.sprite = pygame.transform.smoothscale(self.sprite, (self.w, self.h))
            self.sprite_flipped = pygame.transform.flip(self.sprite, True, False)

        self.prev_jump = False
        self.reset()

    # ================= RESET =================
    def reset(self, spawn=None, ground_y=None):
        if ground_y is None:
            ground_y = settings.world.ground_y(settings.core.height)

        if spawn:
            self.pos.x = float(spawn[0])
            self.pos.y = float(ground_y - self.h - spawn[1])
        else:
            self.pos.x = 100.0
            self.pos.y = float(ground_y - self.h)

        self.vel.update(0, 0)
        self.on_ground = False
        self.current_platform = None

        self.prev_jump = False
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.jump_sound_timer = 0.0

    # ================= RECT =================
    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.w, self.h)

    # ================= INPUT =================
    def _read_input(self, keys, mobile=None):
        move = 0
        jump = False

        if keys[pygame.K_RIGHT]:
            move = 1
        elif keys[pygame.K_LEFT]:
            move = -1

        if keys[pygame.K_SPACE]:
            jump = True

        if mobile:
            if mobile.get("right"):
                move = 1
            elif mobile.get("left"):
                move = -1

            if mobile.get("jump"):
                jump = True

        return move, jump

    # ================= UPDATE =================
    def update(self, dt, keys, mobile=None):
        if self.jump_sound_timer > 0:
            self.jump_sound_timer -= dt

        move, jump_pressed = self._read_input(keys, mobile)

        # ===== Jump Buffer =====
        if jump_pressed:
            self.jump_buffer_timer = self.jump_buffer_max
        else:
            self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)

        # ===== Coyote Time =====
        if self.on_ground:
            self.coyote_timer = self.coyote_time_max
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        control = 1.0 if self.on_ground else self.air_control

        # ===== حركة أفقية =====
        if move != 0:
            self.vel.x += move * self.acc * control * dt
            self.facing_right = move > 0
        else:
            if self.vel.x > 0:
                self.vel.x -= self.friction * dt
                if self.vel.x < 0:
                    self.vel.x = 0
            elif self.vel.x < 0:
                self.vel.x += self.friction * dt
                if self.vel.x > 0:
                    self.vel.x = 0

        if abs(self.vel.x) < 1:
            self.vel.x = 0

        self.vel.x = max(-self.max_speed, min(self.max_speed, self.vel.x))

        # ===== القفز =====
        can_jump = self.on_ground or self.coyote_timer > 0.0

        if self.jump_buffer_timer > 0.0 and can_jump and not self.prev_jump:
            self.vel.y = self.jump_force
            self.on_ground = False
            self.current_platform = None

            self.coyote_timer = 0.0
            self.jump_buffer_timer = 0.0

            if self.jump_sound_timer <= 0:
                try:
                    import audio
                    if audio.audio and "jump" in audio.audio.sounds:
                        audio.audio.play("jump")
                except Exception:
                    pass

                self.jump_sound_timer = self.jump_sound_cooldown

        # ===== Jump Cut =====
        # إذا ترك زر القفز مبكراً وهو يصعد، يقل ارتفاع القفزة
        if not jump_pressed and self.vel.y < 0:
            self.vel.y *= self.jump_cut_multiplier

        self.prev_jump = jump_pressed

        # ===== الجاذبية =====
        if not self.on_ground:
            self.vel.y += self.gravity * dt
        else:
            self.vel.y = 0

        if self.vel.y > self.max_fall_speed:
            self.vel.y = self.max_fall_speed

    # ================= DRAW =================
    def draw(self, screen, camera):
        rect = camera.apply(self.rect())

        if self.sprite:
            img = self.sprite if self.facing_right else self.sprite_flipped
            screen.blit(img, rect)
        else:
            pygame.draw.rect(screen, (0, 255, 0), rect)