import pygame
import sys
import importlib
import random
import math
import os
import re
import json
import hashlib
import zipfile
import time
from enum import Enum
from collections import defaultdict


pygame.init()


# =====================================
# VERSION SYSTEM FIX
# =====================================
GAME_VERSION = "1.9.0"
TOTAL_LEVELS = 20

SCREEN_WIDTH = 1924
SCREEN_HEIGHT = 1080
FPS = 60
FONT_LARGE = pygame.font.Font(None, 80)
FONT_MEDIUM = pygame.font.Font(None, 50)
FONT_SMALL = pygame.font.Font(None, 32)
FONT_TINY = pygame.font.Font(None, 24)


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
DARK_BLUE = (25, 25, 112)


class SoundFX:
    """Simple procedural SFX generator shared across whole game."""
    def __init__(self):
        self.enabled = True
        self.cache = {}
        self.master_volume = 0.70
        self.sample_rate = 44100
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
        except Exception:
            self.enabled = False

    def set_master_volume(self, value):
        self.master_volume = max(0.0, min(1.0, value))

    def play(self, name):
        if not self.enabled:
            return
        try:
            if name not in self.cache:
                self.cache[name] = self._create(name)
            snd = self.cache.get(name)
            if snd is not None:
                snd.set_volume(self.master_volume)
                snd.play()
        except Exception:
            pass

    def _wave(self, phase, wave):
        if wave == "square":
            return 1.0 if math.sin(phase) >= 0 else -1.0
        if wave == "triangle":
            return (2.0 / math.pi) * math.asin(math.sin(phase))
        if wave == "soft_square":
            s = math.sin(phase)
            return math.tanh(3.0 * s)
        return math.sin(phase)

    def _build_tone(self, cfg):
        duration_ms = cfg.get("duration_ms", 80)
        sample_count = max(1, int(self.sample_rate * duration_ms / 1000.0))
        base_freq = float(cfg.get("freq", 440.0))
        volume = max(0.0, min(1.0, float(cfg.get("volume", 0.12))))
        layers = cfg.get("layers", [(1.0, 1.0, "sine", 0.0)])
        attack_ms = max(0.5, float(cfg.get("attack_ms", 2.5)))
        release_ms = max(2.0, float(cfg.get("release_ms", 20.0)))
        decay_pow = max(0.2, float(cfg.get("decay_pow", 1.4)))
        slide = float(cfg.get("slide", 0.0))
        noise = max(0.0, min(0.25, float(cfg.get("noise", 0.0))))
        echo_ms = float(cfg.get("echo_ms", 0.0))
        echo_decay = max(0.0, min(0.8, float(cfg.get("echo_decay", 0.0))))

        attack_len = max(1, int(self.sample_rate * attack_ms / 1000.0))
        release_len = max(1, int(self.sample_rate * release_ms / 1000.0))

        data = [0.0] * sample_count
        phase_steps = []
        phase_vals = []
        for ratio, amp, wave, detune in layers:
            phase_steps.append((float(ratio), float(amp), wave, float(detune)))
            phase_vals.append(random.uniform(0.0, math.pi * 2.0))

        denom = max(1, sample_count - 1)
        for i in range(sample_count):
            t_norm = i / denom
            freq_mul = 1.0 + (slide * t_norm)
            if freq_mul < 0.2:
                freq_mul = 0.2

            mixed = 0.0
            for idx, (ratio, amp, wave, detune) in enumerate(phase_steps):
                freq = (base_freq * ratio * freq_mul) + detune
                phase_vals[idx] += (2.0 * math.pi * freq) / self.sample_rate
                mixed += self._wave(phase_vals[idx], wave) * amp

            if noise > 0.0:
                mixed += random.uniform(-1.0, 1.0) * noise

            attack_env = min(1.0, i / attack_len)
            decay_env = (1.0 - t_norm) ** decay_pow
            env = attack_env * decay_env
            if i >= sample_count - release_len:
                env *= max(0.0, (sample_count - i) / release_len)

            data[i] = mixed * env

        if echo_ms > 0.0 and echo_decay > 0.0:
            delay = int(self.sample_rate * echo_ms / 1000.0)
            if delay > 0:
                for i in range(delay, sample_count):
                    data[i] += data[i - delay] * echo_decay

        peak = max(0.001, max(abs(v) for v in data))
        target = volume * 32767.0
        scale = target / peak

        buf = bytearray(sample_count * 2)
        for i, v in enumerate(data):
            val = int(max(-32767, min(32767, v * scale)))
            buf[2 * i] = val & 0xFF
            buf[2 * i + 1] = (val >> 8) & 0xFF

        return pygame.mixer.Sound(buffer=bytes(buf))

    def _create(self, name):
        presets = {
            "level_start": {
                "freq": 520, "duration_ms": 105, "volume": 0.16,
                "layers": [(1.0, 0.9, "soft_square", 0.0), (2.0, 0.22, "sine", 3.0)],
                "attack_ms": 2.0, "release_ms": 34.0, "decay_pow": 1.15,
                "slide": 0.20, "noise": 0.01, "echo_ms": 32, "echo_decay": 0.10,
            },
            "level_action": {
                "freq": 270, "duration_ms": 24, "volume": 0.055,
                "layers": [(1.0, 1.0, "triangle", 0.0), (1.98, 0.16, "sine", 0.0)],
                "attack_ms": 1.2, "release_ms": 16.0, "decay_pow": 1.6,
                "slide": -0.10,
            },
            "level_success": {
                "freq": 840, "duration_ms": 170, "volume": 0.17,
                "layers": [(1.0, 0.80, "sine", 0.0), (1.50, 0.30, "triangle", 2.0), (2.0, 0.14, "sine", -3.0)],
                "attack_ms": 3.0, "release_ms": 60.0, "decay_pow": 0.95,
                "slide": 0.12, "echo_ms": 58, "echo_decay": 0.16,
            },
            "level_fail": {
                "freq": 205, "duration_ms": 210, "volume": 0.16,
                "layers": [(1.0, 0.82, "soft_square", 0.0), (0.5, 0.28, "sine", 0.0)],
                "attack_ms": 1.0, "release_ms": 70.0, "decay_pow": 1.1,
                "slide": -0.40, "noise": 0.02,
            },
            "level_complete": {
                "freq": 960, "duration_ms": 230, "volume": 0.19,
                "layers": [(1.0, 0.78, "sine", 0.0), (1.25, 0.30, "triangle", 0.0), (2.0, 0.18, "sine", 4.0)],
                "attack_ms": 3.0, "release_ms": 88.0, "decay_pow": 0.85,
                "slide": 0.22, "echo_ms": 72, "echo_decay": 0.19,
            },
            "pause_toggle": {
                "freq": 330, "duration_ms": 58, "volume": 0.10,
                "layers": [(1.0, 0.95, "triangle", 0.0), (2.0, 0.20, "sine", 0.0)],
                "attack_ms": 1.5, "release_ms": 26.0, "decay_pow": 1.2,
                "slide": -0.08,
            },
            "menu_click": {
                "freq": 365, "duration_ms": 52, "volume": 0.085,
                "layers": [(1.0, 0.9, "triangle", 0.0), (2.0, 0.22, "sine", 0.0)],
                "attack_ms": 1.6, "release_ms": 24.0, "decay_pow": 1.45,
                "slide": 0.05,
            },
            "simon_flash": {
                "freq": 710, "duration_ms": 82, "volume": 0.10,
                "layers": [(1.0, 0.86, "sine", 0.0), (2.0, 0.20, "triangle", 1.0)],
                "attack_ms": 2.0, "release_ms": 36.0, "decay_pow": 1.1,
                "slide": 0.08,
            },
        }
        return self._build_tone(presets.get(name, presets["menu_click"]))

class GameState(Enum):
    LOGIN = 0
    MENU = 1
    PLAYING = 2
    PATCH_NOTES = 3
    SETTINGS = 4
    GAME = 5
    LEVEL_COMPLETE = 6
    GAME_OVER = 7
    ACHIEVEMENTS = 8
    THEMES = 9

class Button:
    def __init__(self, x, y, width, height, text, font=FONT_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False
        self.color = BLUE
        self.hover_color = CYAN
        self.text_color = BLACK
        
    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 3)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_hovered(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        # Načti počáteční rozlišení
        self.screen_width = 1920
        self.screen_height = 1080
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("MindLock! - Puzzle Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.LOGIN
        self.fps = 60
        self.logic_fps = FPS
        self._logic_dt = 1.0 / float(self.logic_fps)
        self._logic_accumulator = 0.0
        self._max_catchup_steps = 8
        self.current_level = 1
        self.unlocked_levels = 1
        self._unlocked_levels_before_admin = 1
        self.level_completed = False
        self.game_won = False
        self.admin_mode = False
        self.admin_access = False
        self.show_hint = False
        self.hint_timer = 0
        self.pause_menu_open = False
        self.show_hint_popup = False
        self.hint_popup_timer = 0
        self.completed_levels = set()
        self.level_stars = defaultdict(int)
        self.level_best_time = {}
        self.level_best_reaction_ms = {}
        self.level_best_moves = {}
        self.level_attempt_mistakes = defaultdict(int)
        self.player_score = 0
        self.player_inventory = []
        self.current_level_start_ticks = 0
        self.current_level_elapsed_snapshot = None
        self.space_pressed = False
        self.space_press_count = 0
        self.space_press_timer = 0
        self.current_game = None
        self.sfx = SoundFX()
        self.achievement_notifications = []
        self.win_anim_timer = 0
        self.win_anim_particles = []
        self.screen_glow_timer = 0
        self.screen_shake_timer = 0
        self.enable_screen_glow = True
        self.enable_screen_shake = True
        self.windowed_size = (self.screen_width, self.screen_height)

        self.current_nickname = ""
        self.login_nickname_input = ""
        self.login_password_input = ""
        self.login_active_field = "nickname"
        self.current_password_hash = ""
        self.login_nickname_rect = None
        self.login_password_rect = None
        self.login_error = ""
        self.save_status_message = ""
        self.save_status_timer = 0
        self.save_dir = os.path.join(os.path.dirname(__file__), "saves")
        self.exports_dir = os.path.join(self.save_dir, "exports")
        os.makedirs(self.save_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)

        self.theme_presets = {
            "Neon": {
                "bg": (10, 10, 35), "panel": (25, 35, 70), "accent": (0, 255, 255),
                "text": (235, 245, 255), "subtext": (180, 210, 255), "success": (0, 255, 140),
                "danger": (255, 70, 110), "button": (0, 110, 255), "button_hover": (0, 180, 255),
                "text_on_button": (0, 0, 0),
            },
            "Light": {
                "bg": (236, 242, 255), "panel": (218, 228, 245), "accent": (90, 140, 255),
                "text": (30, 40, 70), "subtext": (65, 85, 130), "success": (70, 180, 110),
                "danger": (210, 90, 90), "button": (135, 175, 255), "button_hover": (165, 200, 255),
                "text_on_button": (20, 30, 50),
            },
            "Retro": {
                "bg": (28, 24, 12), "panel": (58, 46, 22), "accent": (255, 190, 90),
                "text": (255, 231, 180), "subtext": (220, 180, 120), "success": (140, 230, 120),
                "danger": (255, 110, 90), "button": (170, 120, 50), "button_hover": (210, 150, 70),
                "text_on_button": (20, 12, 6),
            },
            "Matrix": {
                "bg": (4, 16, 6), "panel": (8, 30, 12), "accent": (0, 255, 90),
                "text": (170, 255, 170), "subtext": (100, 220, 120), "success": (40, 255, 130),
                "danger": (255, 80, 120), "button": (10, 70, 30), "button_hover": (20, 110, 45),
                "text_on_button": (170, 255, 170),
            },
        }
        self.current_theme = "Neon"
        
        self.version = GAME_VERSION
        
        self.menu_buttons = {
            "play": Button(self.screen_width//2 - 140, 250, 280, 60, "PLAY"),
            "patch": Button(self.screen_width//2 - 140, 340, 280, 60, "PATCH NOTES"),
            "settings": Button(self.screen_width//2 - 140, 430, 280, 60, "SETTINGS"),
            "themes": Button(self.screen_width//2 - 140, 520, 280, 60, "THEMES"),
            "sign_out": Button(self.screen_width//2 - 140, 610, 280, 60, "SIGN OUT"),
            "exit": Button(self.screen_width//2 - 140, 700, 280, 60, "SAVE & EXIT")
        }
        self.login_buttons = {
            "login": Button(self.screen_width//2 - 120, self.screen_height//2 + 130, 240, 60, "LOGIN"),
            "exit": Button(self.screen_width//2 - 120, self.screen_height//2 + 210, 240, 60, "EXIT"),
        }
        self.achievements_button = Button(30, self.screen_height - 90, 220, 50, "ACHIEVEMENTS", FONT_SMALL)
        self.achievements_buttons = {
            "back": Button(self.screen_width//2 - 100, self.screen_height - 100, 200, 60, "BACK")
        }
        self.theme_buttons = {}

        self.achievements = {}
        for i in range(1, 21):
            self.achievements[f"level_{i}"] = {
                "title": f"Level {i} Complete",
                "desc": f"Dokonci level {i}",
                "unlocked": False,
            }
        self.achievements["record_l1"] = {
            "title": "Level 1 Record",
            "desc": "Udrzuj nejlepsi cas v levelu 1",
            "unlocked": False,
        }
        self.achievements["speed_l1"] = {
            "title": "Speed Runner I",
            "desc": "Dokonci level 1 se zbytkem alespon 3s",
            "unlocked": False,
        }
        self.achievements["speed_l8"] = {
            "title": "Bomb Specialist",
            "desc": "Dokonci level 8 se zbytkem alespon 3s",
            "unlocked": False,
        }
        self.achievements["all_levels"] = {
            "title": "Mastermind",
            "desc": "Dokonci vsech 20 levelu",
            "unlocked": False,
        }
        
        self.patch_notes = [
            {
                "version": "1.9.0",
                "notes": [
                    "Level 12 redesigned: pick shape by name (no rotations)",
                    "Level 15 simplified: fewer switches and easier logic",
                    "Added Sound tab with master volume slider",
                    "Softer click sounds and less annoying in-game SFX",
                    "Simon Says: beep when color flashes"
                ]
            },
            {
                "version": "1.8.0",
                "notes": [
                    "Added Quantum Switches (Level 15)",
                    "Added Cipher Breaker (Level 16)",
                    "Added Rolling Balls (Level 20)",
                    "Hangman: hint hidden until 2x SPACE",
                    "20 levels total"
                ]
            },
            {
                "version": "1.7.0",
                "notes": [
                    "Added Word Unscrambler",
                    "Reordered levels by difficulty",
                    "Graphics settings expansion",
                    "Bug fixes and improvements"
                ]
            },
            {
                "version": "1.6.0",
                "notes": [
                    "Added Laser Mirrors",
                    "Added Cable Connect",
                    "Added Pipe Rotate",
                    "UI improvements"
                ]
            }
        ]
        
        # =====================================
        # SETTINGS STATE
        # =====================================
        self.graphics_settings = {
            "resolution": f"{self.screen_width}x{self.screen_height}",
            "fullscreen": False,
            "vsync": True,
            "ui_scale": 100,
        }
        self.available_resolutions = [
            "800x600", "1024x768", "1280x720", "1366x768", "1600x900", "1920x1080"
        ]
        self.available_ui_scales = [75, 100, 125, 150]
        self.sound_settings = {
            "master_volume": 70,
        }
        self.sound_slider_dragging = False
        self.sfx.set_master_volume(self.sound_settings["master_volume"] / 100.0)
        self.settings_tab = "graphics"  # "graphics" or "developer" or "sound"
        # Settings buttons are built dynamically in draw_settings / _build_settings_rects
        self._settings_rects = {}  # filled each frame by draw_settings
        

        self.patch_buttons = {
            "back": Button(self.screen_width//2 - 100, 700, 200, 60, "ZPĚT")
        }
        

        self.play_buttons = {
            "back": Button(self.screen_width//2 - 100, 700, 200, 60, "ZPĚT")
        }
        self.level_buttons = {}
        self.create_level_buttons()
        
  
        self.popup_buttons = {
            "menu": Button(self.screen_width//2 - 250, 400, 150, 60, "MENU"),
            "restart": Button(self.screen_width//2 - 50, 400, 150, 60, "RESTART"),
            "next": Button(self.screen_width//2 + 150, 400, 150, 60, "DALŠÍ")
        }
        
        self.pause_buttons = {
            "continue": Button(self.screen_width//2 - 100, 350, 200, 60, "CONTINUE"),
            "restart": Button(self.screen_width//2 - 100, 450, 200, 60, "RESTART"),
            "exit": Button(self.screen_width//2 - 100, 550, 200, 60, "EXIT")
        }
        self._build_theme_buttons()
        self._apply_theme_to_buttons()
    
    def _scale(self):
        """Combined scale factor: resolution * ui_scale"""
        res_s = min(self.screen_width / 1920, self.screen_height / 1080)
        ui_s = self.graphics_settings["ui_scale"] / 100.0
        return res_s * ui_s

    def _tc(self, key):
        return self.theme_presets.get(self.current_theme, self.theme_presets["Neon"]).get(key, WHITE)

    def _apply_theme_to_buttons(self):
        btn_color = self._tc("button")
        hover_color = self._tc("button_hover")
        txt = self._tc("text_on_button")
        groups = [
            self.menu_buttons.values(), self.patch_buttons.values(), self.play_buttons.values(),
            self.popup_buttons.values(), self.pause_buttons.values(), self.achievements_buttons.values(),
            [self.achievements_button], self.theme_buttons.values(), self.login_buttons.values()
        ]
        for group in groups:
            for button in group:
                button.color = btn_color
                button.hover_color = hover_color
                button.text_color = txt

    def _sanitize_nickname(self, nickname):
        nickname = nickname.strip()
        if not nickname:
            return None
        if not re.fullmatch(r"[A-Za-z0-9_\-]{3,20}", nickname):
            return None
        return nickname

    def _save_file_path(self, nickname):
        return os.path.join(self.save_dir, f"{nickname}.json")

    def _is_admin_nickname(self, nickname):
        return str(nickname).strip().lower() == "thugzs"

    def _default_save_data(self, nickname, password_hash=""):
        return {
            "nickname": nickname,
            "password_hash": password_hash,
            "admin_access": self._is_admin_nickname(nickname),
            "current_level": 1,
            "unlocked_levels": 1,
            "player_score": 0,
            "current_theme": "Neon",
            "player_settings": {
                "screen_shake": True,
                "screen_glow": True,
                "master_volume": 70,
            },
            "inventory": [],
            "level_stars": {},
            "level_best_time": {},
            "level_best_reaction_ms": {},
            "level_best_moves": {},
            "completed_levels": [],
            "achievements": {},
            "graphics": {
                "resolution": self.graphics_settings["resolution"],
                "fullscreen": self.graphics_settings["fullscreen"],
                "vsync": self.graphics_settings["vsync"],
                "ui_scale": self.graphics_settings["ui_scale"],
            },
        }

    def _checksum_for_payload(self, payload):
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _collect_save_payload(self):
        return {
            "nickname": self.current_nickname,
            "password_hash": self.current_password_hash,
            "admin_access": bool(self.admin_access and self._is_admin_nickname(self.current_nickname)),
            "current_level": self.current_level,
            "unlocked_levels": self.unlocked_levels,
            "player_score": self.player_score,
            "current_theme": self.current_theme,
            "player_settings": {
                "screen_shake": self.enable_screen_shake,
                "screen_glow": self.enable_screen_glow,
                "master_volume": self.sound_settings.get("master_volume", 70),
            },
            "inventory": list(self.player_inventory),
            "level_stars": {str(k): int(v) for k, v in self.level_stars.items()},
            "level_best_time": {str(k): float(v) for k, v in self.level_best_time.items()},
            "level_best_reaction_ms": {str(k): int(v) for k, v in self.level_best_reaction_ms.items()},
            "level_best_moves": {str(k): int(v) for k, v in self.level_best_moves.items()},
            "completed_levels": sorted(int(x) for x in self.completed_levels),
            "achievements": {k: bool(v.get("unlocked", False)) for k, v in self.achievements.items()},
            "graphics": {
                "resolution": self.graphics_settings["resolution"],
                "fullscreen": self.graphics_settings["fullscreen"],
                "vsync": self.graphics_settings["vsync"],
                "ui_scale": self.graphics_settings["ui_scale"],
            },
        }

    def save_game(self):
        if not self.current_nickname:
            return False
        payload = self._collect_save_payload()
        data = dict(payload)
        data["checksum"] = self._checksum_for_payload(payload)
        path = self._save_file_path(self.current_nickname)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.save_status_message = f"Save error: {e}"
            self.save_status_timer = 180
            return False

    def _apply_loaded_save(self, data):
        self.admin_access = bool(data.get("admin_access", self._is_admin_nickname(self.current_nickname))) and self._is_admin_nickname(self.current_nickname)
        if not self.admin_access:
            self.admin_mode = False
        self.current_level = int(data.get("current_level", 1))
        self.unlocked_levels = int(data.get("unlocked_levels", 1))
        self.player_score = int(data.get("player_score", 0))
        self.current_theme = data.get("current_theme", "Neon") if data.get("current_theme", "Neon") in self.theme_presets else "Neon"
        self.current_password_hash = str(data.get("password_hash", ""))

        ps = data.get("player_settings", {})
        self.enable_screen_shake = bool(ps.get("screen_shake", True))
        self.enable_screen_glow = bool(ps.get("screen_glow", True))
        self.sound_settings["master_volume"] = int(ps.get("master_volume", self.sound_settings.get("master_volume", 70)))
        self.sfx.set_master_volume(self.sound_settings["master_volume"] / 100.0)

        self.player_inventory = list(data.get("inventory", []))
        self.level_stars = defaultdict(int, {int(k): int(v) for k, v in data.get("level_stars", {}).items()})
        self.level_best_time = {int(k): float(v) for k, v in data.get("level_best_time", {}).items()}
        self.level_best_reaction_ms = {int(k): int(v) for k, v in data.get("level_best_reaction_ms", {}).items()}
        self.level_best_moves = {int(k): int(v) for k, v in data.get("level_best_moves", {}).items()}
        self.completed_levels = set(int(x) for x in data.get("completed_levels", []))
        self._reconcile_unlocked_levels()

        if 2 not in self.level_best_reaction_ms and 2 in self.level_best_time:
            self.level_best_reaction_ms[2] = int(self.level_best_time[2] * 1000)
            self.level_best_time.pop(2, None)

        unlocked_map = data.get("achievements", {})
        for k, ach in self.achievements.items():
            ach["unlocked"] = bool(unlocked_map.get(k, ach.get("unlocked", False)))

        graphics = data.get("graphics", {})
        loaded_resolution = graphics.get("resolution", self.graphics_settings["resolution"])
        loaded_vsync = bool(graphics.get("vsync", self.graphics_settings["vsync"]))
        loaded_scale = int(graphics.get("ui_scale", self.graphics_settings["ui_scale"]))
        loaded_scale = min(self.available_ui_scales, key=lambda v: abs(v - loaded_scale))
        loaded_fullscreen = bool(graphics.get("fullscreen", self.graphics_settings["fullscreen"]))

        self.graphics_settings["vsync"] = loaded_vsync
        self.graphics_settings["ui_scale"] = loaded_scale
        self.apply_ui_scale()

        if loaded_resolution in self.available_resolutions:
            self.change_resolution(loaded_resolution)
        self.graphics_settings["fullscreen"] = loaded_fullscreen
        if loaded_fullscreen:
            desktop = pygame.display.get_desktop_sizes()[0]
            self.screen_width, self.screen_height = desktop
            self.screen = pygame.display.set_mode(desktop, pygame.FULLSCREEN)
            self.graphics_settings["resolution"] = f"{self.screen_width}x{self.screen_height}"
        else:
            w, h = map(int, self.graphics_settings["resolution"].split("x"))
            self.screen_width, self.screen_height = w, h
            self.screen = pygame.display.set_mode((w, h))
        self.initialize_ui_elements()

    def _load_save_payload(self, path):
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        checksum = loaded.get("checksum", "")
        payload = dict(loaded)
        payload.pop("checksum", None)
        if checksum and checksum != self._checksum_for_payload(payload):
            raise ValueError("Save ma neplatny checksum (integrita)")
        return payload

    def _reconcile_unlocked_levels(self):
        max_levels = TOTAL_LEVELS
        if self.level_buttons:
            max_levels = len(self.level_buttons)

        try:
            unlocked = int(self.unlocked_levels)
        except Exception:
            unlocked = 1

        unlocked = max(1, min(max_levels, unlocked))

        valid_completed = []
        for lvl in self.completed_levels:
            try:
                lvl_int = int(lvl)
            except Exception:
                continue
            if 1 <= lvl_int <= max_levels:
                valid_completed.append(lvl_int)

        if valid_completed:
            max_completed = max(valid_completed)
            if max_completed >= max_levels:
                derived_unlocked = max_levels
            else:
                derived_unlocked = max_completed + 1
            unlocked = max(unlocked, derived_unlocked)

        self.unlocked_levels = unlocked

    def _hash_login_password(self, nickname, password):
        return hashlib.sha256(f"{nickname}:{password}".encode("utf-8")).hexdigest()

    def login_or_create_save(self, nickname, password):
        sanitized = self._sanitize_nickname(nickname)
        if sanitized is None:
            self.login_error = "Nickname: 3-20 znaku [A-Z a-z 0-9 _ -]"
            return False

        if not (4 <= len(password) <= 32):
            self.login_error = "Heslo: 4-32 znaku"
            return False

        password_hash = self._hash_login_password(sanitized, password)

        self.current_nickname = sanitized
        path = self._save_file_path(sanitized)
        if not os.path.exists(path):
            data = self._default_save_data(sanitized, password_hash=password_hash)
            payload = dict(data)
            data["checksum"] = self._checksum_for_payload(payload)
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.login_error = f"Nelze vytvorit save: {e}"
                return False

        try:
            payload = self._load_save_payload(path)
            stored_password_hash = str(payload.get("password_hash", ""))
            if stored_password_hash:
                if stored_password_hash != password_hash:
                    self.login_error = "Spatne heslo"
                    return False
            else:
                payload["password_hash"] = password_hash
            self._apply_loaded_save(payload)
        except Exception as e:
            self.login_error = f"Nelze nacist save: {e}"
            return False

        self.login_error = ""
        self.login_nickname_input = sanitized
        self.login_password_input = ""
        self.current_password_hash = password_hash
        self.save_game()
        self.state = GameState.MENU
        self.save_status_message = f"Prihlasen: {self.current_nickname}"
        self.save_status_timer = 120
        return True

    def sign_out(self):
        if self.current_nickname:
            self.admin_mode = False
            self.save_game()
        self.current_nickname = ""
        self.current_password_hash = ""
        self.login_nickname_input = ""
        self.login_password_input = ""
        self.login_error = ""
        self.state = GameState.LOGIN

    def export_save_zip(self):
        if not self.current_nickname:
            return False
        if not self.save_game():
            return False
        src = self._save_file_path(self.current_nickname)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        out_zip = os.path.join(self.exports_dir, f"{self.current_nickname}_{stamp}.zip")
        try:
            with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(src, arcname=f"{self.current_nickname}.json")
            self.save_status_message = f"Export OK: {os.path.basename(out_zip)}"
            self.save_status_timer = 180
            return True
        except Exception as e:
            self.save_status_message = f"Export error: {e}"
            self.save_status_timer = 180
            return False

    def import_latest_save_zip(self):
        if not self.current_nickname:
            return False
        prefix = f"{self.current_nickname}_"
        candidates = [f for f in os.listdir(self.exports_dir) if f.startswith(prefix) and f.endswith(".zip")]
        if not candidates:
            self.save_status_message = "Import: zadny export nenalezen"
            self.save_status_timer = 180
            return False
        candidates.sort(reverse=True)
        latest = os.path.join(self.exports_dir, candidates[0])
        try:
            with zipfile.ZipFile(latest, "r") as zf:
                member = f"{self.current_nickname}.json"
                if member not in zf.namelist():
                    self.save_status_message = "Import error: save nenalezen v ZIP"
                    self.save_status_timer = 180
                    return False
                zf.extract(member, self.save_dir)
            extracted = os.path.join(self.save_dir, f"{self.current_nickname}.json")
            with open(extracted, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            checksum = loaded.get("checksum", "")
            payload = dict(loaded)
            payload.pop("checksum", None)
            if checksum and checksum != self._checksum_for_payload(payload):
                self.save_status_message = "Import error: neplatny checksum"
                self.save_status_timer = 180
                return False
            self._apply_loaded_save(payload)
            self.save_status_message = f"Import OK: {os.path.basename(latest)}"
            self.save_status_timer = 180
            self.save_game()
            return True
        except Exception as e:
            self.save_status_message = f"Import error: {e}"
            self.save_status_timer = 180
            return False

    def change_resolution(self, resolution_str):
        """Change resolution, rebuild display and all UI"""
        try:
            width, height = map(int, resolution_str.split("x"))
            self.screen_width = width
            self.screen_height = height
            self.graphics_settings["resolution"] = resolution_str
            if self.graphics_settings["fullscreen"]:
                self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode((width, height))
            self.initialize_ui_elements()
            return True
        except Exception as e:
            print(f"Resolution change error: {e}")
            return False
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen similarly to F11 behavior."""
        self.graphics_settings["fullscreen"] = not self.graphics_settings["fullscreen"]
        if self.graphics_settings["fullscreen"]:
            self.windowed_size = (self.screen_width, self.screen_height)
            desktop = pygame.display.get_desktop_sizes()[0]
            self.screen_width, self.screen_height = desktop
            self.screen = pygame.display.set_mode(desktop, pygame.FULLSCREEN)
        else:
            self.screen_width, self.screen_height = self.windowed_size
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.graphics_settings["resolution"] = f"{self.screen_width}x{self.screen_height}"
        self.initialize_ui_elements()

    def _build_theme_buttons(self):
        self.theme_buttons = {}
        s = self._scale()
        names = ["Neon", "Light", "Retro", "Matrix"]
        bw, bh = int(300 * s), int(64 * s)
        row_gap = int(56 * s)
        start_x = self.screen_width // 2 - bw // 2
        start_y = int(170 * s)
        f = pygame.font.Font(None, max(14, int(34 * s)))
        for idx, name in enumerate(names):
            x = start_x
            y = start_y + idx * (bh + row_gap)
            self.theme_buttons[name] = Button(x, y, bw, bh, name, f)
    
    def initialize_ui_elements(self):
        """Reinitialize all UI elements for current resolution + ui_scale"""
        sw, sh = self.screen_width, self.screen_height
        s = self._scale()
        bw, bh = int(280 * s), int(60 * s)
        self.menu_buttons = {
            "play":     Button(sw//2 - bw//2, int(250*s), bw, bh, "PLAY"),
            "patch":    Button(sw//2 - bw//2, int(340*s), bw, bh, "PATCH NOTES"),
            "settings": Button(sw//2 - bw//2, int(430*s), bw, bh, "SETTINGS"),
            "themes":   Button(sw//2 - bw//2, int(520*s), bw, bh, "THEMES"),
            "sign_out": Button(sw//2 - bw//2, int(610*s), bw, bh, "SIGN OUT"),
            "exit":     Button(sw//2 - bw//2, int(700*s), bw, bh, "SAVE & EXIT")
        }
        self.achievements_button = Button(int(30*s), sh - int(90*s), int(240*s), int(50*s), "ACHIEVEMENTS", pygame.font.Font(None, max(12, int(28*s))))
        self.patch_buttons = {
            "back": Button(sw//2 - int(100*s), sh - int(100*s), int(200*s), int(60*s), "ZPĚT")
        }
        self.play_buttons = {
            "back": Button(sw//2 - int(100*s), sh - int(100*s), int(200*s), int(60*s), "ZPĚT")
        }
        pb = int(150*s)
        self.popup_buttons = {
            "menu":    Button(sw//2 - int(250*s), int(400*s), pb, int(60*s), "MENU"),
            "restart": Button(sw//2 - pb//2,      int(400*s), pb, int(60*s), "RESTART"),
            "next":    Button(sw//2 + int(100*s),  int(400*s), pb, int(60*s), "DALŠÍ")
        }
        self.pause_buttons = {
            "continue": Button(sw//2 - int(100*s), int(350*s), int(200*s), int(60*s), "CONTINUE"),
            "restart":  Button(sw//2 - int(100*s), int(450*s), int(200*s), int(60*s), "RESTART"),
            "exit":     Button(sw//2 - int(100*s), int(550*s), int(200*s), int(60*s), "EXIT")
        }
        self.achievements_buttons = {
            "back": Button(sw//2 - int(100*s), sh - int(100*s), int(200*s), int(60*s), "BACK")
        }
        self.login_buttons = {
            "login": Button(sw//2 - int(120*s), sh//2 + int(130*s), int(240*s), int(60*s), "LOGIN"),
            "exit": Button(sw//2 - int(120*s), sh//2 + int(210*s), int(240*s), int(60*s), "EXIT")
        }
        self._build_theme_buttons()
        self._apply_theme_to_buttons()
        self.create_level_buttons()

    def _unlock_achievement(self, key):
        ach = self.achievements.get(key)
        if not ach or ach["unlocked"]:
            return
        ach["unlocked"] = True
        self.achievement_notifications.append({
            "text": f"Achievement: {ach['title']}",
            "timer": 120,
            "max": 120,
        })
        self.sfx.play("level_success")

    def _get_remaining_seconds(self):
        if not self.current_game:
            return None
        if hasattr(self.current_game, "timer"):
            return max(0.0, self.current_game.timer / float(self.logic_fps))
        if hasattr(self.current_game, "time_left"):
            return max(0.0, float(self.current_game.time_left))
        return None

    def _get_moves_used(self):
        if not self.current_game:
            return None
        for attr in ("moves", "press_count", "move_count"):
            if hasattr(self.current_game, attr):
                try:
                    return int(getattr(self.current_game, attr))
                except Exception:
                    return None
        return None

    def _get_current_elapsed_seconds(self):
        if self.current_level_elapsed_snapshot is not None:
            return self.current_level_elapsed_snapshot
        if self.current_level_start_ticks <= 0:
            return None
        return max(0.0, (pygame.time.get_ticks() - self.current_level_start_ticks) / 1000.0)

    def _calculate_stars(self, mistakes):
        if mistakes <= 0:
            return 3
        if mistakes == 1:
            return 2
        return 1

    def _start_win_animation(self):
        self.win_anim_timer = 90
        self.screen_glow_timer = 24
        self.screen_shake_timer = 18
        self.win_anim_particles = []
        for _ in range(36):
            self.win_anim_particles.append({
                "x": random.randint(200, self.screen_width - 200),
                "y": random.randint(120, self.screen_height - 200),
                "vx": random.uniform(-2.2, 2.2),
                "vy": random.uniform(-4.2, -1.2),
                "size": random.randint(3, 7),
                "col": random.choice([YELLOW, CYAN, GREEN, WHITE]),
            })
        
    def create_level_buttons(self):
        """Create level buttons scaled to current resolution + ui_scale"""
        sw, sh = self.screen_width, self.screen_height
        s = self._scale()
        btn_w = int(160 * s)
        btn_h = int(100 * s)
        gap_x = int(180 * s)
        gap_y = int(120 * s)
        cols = 5
        total_w = cols * gap_x - (gap_x - btn_w)
        start_x = (sw - total_w) // 2
        start_y = int(150 * s)
        f = pygame.font.Font(None, max(12, int(32 * s)))
        for i in range(1, 21):
            col = (i - 1) % cols
            row = (i - 1) // cols
            x = start_x + col * gap_x
            y = start_y + row * gap_y
            self.level_buttons[i] = Button(x, y, btn_w, btn_h, f"LEVEL {i}", f)
    
    def apply_ui_scale(self):
        """Apply UI scale to fonts and reinitialize all UI elements"""
        global FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_TINY
        scale = self.graphics_settings["ui_scale"] / 100.0
        FONT_LARGE = pygame.font.Font(None, int(80 * scale))
        FONT_MEDIUM = pygame.font.Font(None, int(50 * scale))
        FONT_SMALL = pygame.font.Font(None, int(32 * scale))
        FONT_TINY = pygame.font.Font(None, int(24 * scale))
        self.initialize_ui_elements()
    
    def draw_menu(self):
        """Draw main menu – resolution & UI-scale adaptive"""
        sw, sh = self.screen_width, self.screen_height
        s = self._scale()
        self._apply_theme_to_buttons()
        self.screen.fill(self._tc("bg"))

        f_title = pygame.font.Font(None, max(20, int(80 * s)))
        f_sub   = pygame.font.Font(None, max(12, int(32 * s)))

        title = f_title.render("MindLock!", True, self._tc("accent"))
        title_rect = title.get_rect(center=(sw//2, int(90*s)))
        shadow = f_title.render("MindLock!", True, (0, 50, 80))
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)

        line_y = int(160*s)
        pygame.draw.line(self.screen, self._tc("accent"), (sw//2 - int(300*s), line_y), (sw//2 - int(100*s), line_y), 2)
        pygame.draw.line(self.screen, self._tc("accent"), (sw//2 + int(100*s), line_y), (sw//2 + int(300*s), line_y), 2)

        subtitle = f_sub.render("Puzzle Game", True, self._tc("subtext"))
        self.screen.blit(subtitle, subtitle.get_rect(center=(sw//2, int(180*s))))

        for button in self.menu_buttons.values():
            button.draw(self.screen)
        self.achievements_button.draw(self.screen)

        if self.current_nickname:
            who = f_sub.render(f"Player: {self.current_nickname}", True, self._tc("subtext"))
            self.screen.blit(who, (20, 20))
        if self.save_status_timer > 0 and self.save_status_message:
            msg = f_sub.render(self.save_status_message, True, YELLOW)
            self.screen.blit(msg, (20, sh - int(36*s)))

    def draw_login(self):
        sw, sh = self.screen_width, self.screen_height
        s = self._scale()
        self.screen.fill(self._tc("bg"))

        f_title = pygame.font.Font(None, max(20, int(84 * s)))
        f_sub = pygame.font.Font(None, max(14, int(36 * s)))
        f_err = pygame.font.Font(None, max(14, int(30 * s)))

        title = f_title.render("MindLock!", True, self._tc("accent"))
        self.screen.blit(title, title.get_rect(center=(sw//2, int(180*s))))

        prompt = f_sub.render("Zadej nickname a heslo", True, self._tc("text"))
        self.screen.blit(prompt, prompt.get_rect(center=(sw//2, int(290*s))))

        input_w, input_h = int(520*s), int(64*s)
        nick_rect = pygame.Rect(sw//2 - input_w//2, sh//2 - int(132*s), input_w, input_h)
        pass_rect = pygame.Rect(sw//2 - input_w//2, sh//2 - int(28*s), input_w, input_h)
        self.login_nickname_rect = nick_rect
        self.login_password_rect = pass_rect

        nick_label = f_sub.render("Nickname", True, self._tc("subtext"))
        pass_label = f_sub.render("Heslo", True, self._tc("subtext"))
        self.screen.blit(nick_label, (nick_rect.x, nick_rect.y - int(30*s)))
        self.screen.blit(pass_label, (pass_rect.x, pass_rect.y - int(30*s)))

        nick_border = self._tc("accent") if self.login_active_field == "nickname" else self._tc("subtext")
        pass_border = self._tc("accent") if self.login_active_field == "password" else self._tc("subtext")

        pygame.draw.rect(self.screen, self._tc("panel"), nick_rect, border_radius=8)
        pygame.draw.rect(self.screen, nick_border, nick_rect, 2, border_radius=8)
        pygame.draw.rect(self.screen, self._tc("panel"), pass_rect, border_radius=8)
        pygame.draw.rect(self.screen, pass_border, pass_rect, 2, border_radius=8)

        nick_typed = self.login_nickname_input if self.login_nickname_input else "..."
        nick_col = self._tc("text") if self.login_nickname_input else self._tc("subtext")
        nick_surf = f_sub.render(nick_typed, True, nick_col)
        self.screen.blit(nick_surf, (nick_rect.x + int(16*s), nick_rect.y + int(16*s)))

        masked_password = "*" * len(self.login_password_input) if self.login_password_input else "..."
        pass_col = self._tc("text") if self.login_password_input else self._tc("subtext")
        pass_surf = f_sub.render(masked_password, True, pass_col)
        self.screen.blit(pass_surf, (pass_rect.x + int(16*s), pass_rect.y + int(16*s)))

        self.login_buttons["login"].draw(self.screen)
        self.login_buttons["exit"].draw(self.screen)

        if self.login_error:
            err = f_err.render(self.login_error, True, self._tc("danger"))
            self.screen.blit(err, err.get_rect(center=(sw//2, self.login_buttons["login"].rect.bottom + int(46*s))))

    def draw_achievements(self):
        self._apply_theme_to_buttons()
        self.screen.fill(self._tc("bg"))
        title = FONT_LARGE.render("ACHIEVEMENTS", True, self._tc("accent"))
        self.screen.blit(title, title.get_rect(center=(self.screen_width // 2, 60)))

        y = 130
        lh = 32
        unlocked = sum(1 for a in self.achievements.values() if a["unlocked"])
        total = len(self.achievements)
        p = FONT_SMALL.render(f"Unlocked: {unlocked}/{total}", True, self._tc("accent"))
        self.screen.blit(p, (80, 95))

        if 1 in self.level_best_time:
            rec = FONT_SMALL.render(f"Level 1 record: {self.level_best_time[1]:.2f}s", True, GREEN)
            self.screen.blit(rec, (self.screen_width - rec.get_width() - 80, 95))

        for key, ach in self.achievements.items():
            if y > self.screen_height - 140:
                break
            col = GREEN if ach["unlocked"] else GRAY
            mark = "[X]" if ach["unlocked"] else "[ ]"
            line = FONT_TINY.render(f"{mark} {ach['title']} - {ach['desc']}", True, col)
            self.screen.blit(line, (80, y))
            y += lh

        self.achievements_buttons["back"].draw(self.screen)

    def draw_themes(self):
        self._apply_theme_to_buttons()
        self.screen.fill(self._tc("bg"))
        title = FONT_LARGE.render("THEMES", True, self._tc("accent"))
        self.screen.blit(title, title.get_rect(center=(self.screen_width // 2, 60)))

        active = FONT_SMALL.render(f"Aktivni motiv: {self.current_theme}", True, self._tc("text"))
        self.screen.blit(active, active.get_rect(center=(self.screen_width // 2, 120)))

        desc_map = {
            "Neon": "Jasne svitici barvy a elektricky efekt.",
            "Light": "Svetly pastelovy motiv s jemnym glow.",
            "Retro": "Nostalgicka paleta ve stylu klasickych her.",
            "Matrix": "Tmavy motiv se zelenym digitalnim nadychem.",
        }
        for name, button in self.theme_buttons.items():
            button.hovered = (name == self.current_theme)
            button.draw(self.screen)
            d = FONT_TINY.render(desc_map[name], True, self._tc("subtext"))
            self.screen.blit(d, d.get_rect(center=(button.rect.centerx, button.rect.bottom + 18)))

        self.achievements_buttons["back"].draw(self.screen)

    def _draw_progress_bar(self):
        bw, bh = 260, 16
        x = self.screen_width - bw - 20
        y = 40
        pygame.draw.rect(self.screen, (40, 40, 60), (x, y, bw, bh), border_radius=8)
        fill = int(bw * (self.current_level / 20.0))
        pygame.draw.rect(self.screen, (0, 190, 120), (x, y, fill, bh), border_radius=8)
        pygame.draw.rect(self.screen, WHITE, (x, y, bw, bh), 2, border_radius=8)

    def _draw_achievement_notifications(self):
        base_y = 20
        for idx, note in enumerate(self.achievement_notifications[:3]):
            t = note["timer"]
            alpha = 255
            if t < 20:
                alpha = int(255 * (t / 20))
            panel = pygame.Surface((420, 44), pygame.SRCALPHA)
            panel.fill((20, 30, 55, min(220, alpha)))
            pygame.draw.rect(panel, (80, 200, 255, alpha), panel.get_rect(), 2, border_radius=8)
            txt = FONT_TINY.render(note["text"], True, (255, 255, 255))
            panel.blit(txt, (12, 12))
            self.screen.blit(panel, (self.screen_width - 440, base_y + idx * 52))
    
    def draw_patch_notes(self):
        """Kreslí patch notes"""
        self.screen.fill(self._tc("bg"))
        
        title = FONT_LARGE.render("PATCH NOTES", True, self._tc("accent"))
        title_rect = title.get_rect(center=(self.screen_width//2, 40))
        self.screen.blit(title, title_rect)
        

        box_rect = pygame.Rect(150, 120, self.screen_width - 300, 500)
        pygame.draw.rect(self.screen, self._tc("panel"), box_rect)
        pygame.draw.rect(self.screen, self._tc("accent"), box_rect, 3)
        
     
        y = 140
        max_y = 600
        for patch in self.patch_notes:
            if y > max_y:
                break
            version_text = FONT_MEDIUM.render(f"Verze {patch['version']}", True, YELLOW)
            if y + version_text.get_height() < max_y:
                self.screen.blit(version_text, (180, y))
            y += 45
            
            for note in patch['notes']:
                if y > max_y:
                    break
                note_text = FONT_SMALL.render(f"  • {note}", True, WHITE)
                if y + note_text.get_height() < max_y:
                    self.screen.blit(note_text, (200, y))
                y += 32
            y += 15
        
        self.patch_buttons["back"].draw(self.screen)
    
    def draw_settings(self):
        """Resolution & UI-scale adaptive settings with tabs, no overlap."""
        sw, sh = self.screen_width, self.screen_height
        s = self._scale()
        self.screen.fill(self._tc("bg"))
        rects = {}

        # Scaled fonts
        f_title = pygame.font.Font(None, max(20, int(72 * s)))
        f_btn   = pygame.font.Font(None, max(14, int(36 * s)))
        f_val   = pygame.font.Font(None, max(14, int(40 * s)))

        # --- Title ---
        title_surf = f_title.render("SETTINGS", True, self._tc("accent"))
        self.screen.blit(title_surf, title_surf.get_rect(center=(sw//2, int(50*s))))

        # --- Tabs ---
        tab_w, tab_h = int(180*s), int(50*s)
        tab_gap = int(20*s)
        tabs_total = tab_w * 3 + tab_gap * 2
        tx = sw//2 - tabs_total//2
        ty = int(110*s)
        for i, (tab_id, tab_label) in enumerate([("graphics", "Graphics"), ("sound", "Sound"), ("developer", "Developer")]):
            r = pygame.Rect(tx + i*(tab_w + tab_gap), ty, tab_w, tab_h)
            active = self.settings_tab == tab_id
            col = (0, 102, 255) if active else (40, 40, 80)
            pygame.draw.rect(self.screen, col, r)
            pygame.draw.rect(self.screen, (100, 180, 255) if active else (80, 80, 120), r, 2)
            lbl = f_btn.render(tab_label, True, WHITE)
            self.screen.blit(lbl, lbl.get_rect(center=r.center))
            rects[f"tab_{tab_id}"] = r

        # --- Content ---
        cy = ty + tab_h + int(40*s)
        row_h = int(60*s)       # enough vertical space per row
        btn_w = int(50*s)
        btn_h = int(44*s)
        toggle_w = int(300*s)
        cx = sw // 2
        label_x = cx - int(220*s)   # labels left of center
        val_gap = int(70*s)         # gap between value and +/- buttons

        def _draw_btn(rect, text, font=f_btn):
            pygame.draw.rect(self.screen, (0, 102, 255), rect)
            pygame.draw.rect(self.screen, (100, 180, 255), rect, 2)
            t = font.render(text, True, WHITE)
            self.screen.blit(t, t.get_rect(center=rect.center))

        if self.settings_tab == "graphics":
            # FPS
            lbl = f_btn.render("FPS:", True, WHITE)
            self.screen.blit(lbl, (label_x, cy + (row_h - lbl.get_height())//2))
            minus_r = pygame.Rect(cx - val_gap - btn_w, cy + (row_h-btn_h)//2, btn_w, btn_h)
            plus_r  = pygame.Rect(cx + val_gap,         cy + (row_h-btn_h)//2, btn_w, btn_h)
            _draw_btn(minus_r, "-")
            _draw_btn(plus_r, "+")
            val = f_val.render(str(self.fps), True, YELLOW)
            self.screen.blit(val, val.get_rect(center=(cx, cy + row_h//2)))
            rects["fps_down"] = minus_r
            rects["fps_up"] = plus_r
            cy += row_h

            # Resolution
            lbl = f_btn.render("Resolution:", True, WHITE)
            self.screen.blit(lbl, (label_x, cy + (row_h - lbl.get_height())//2))
            res_val = f_val.render(self.graphics_settings["resolution"], True, YELLOW)
            self.screen.blit(res_val, res_val.get_rect(center=(cx, cy + row_h//2)))
            arr_r = pygame.Rect(cx + val_gap, cy + (row_h-btn_h)//2, btn_w, btn_h)
            _draw_btn(arr_r, ">")
            rects["resolution_next"] = arr_r
            cy += row_h

            # Fullscreen
            fs_text = "Fullscreen: ON" if self.graphics_settings["fullscreen"] else "Fullscreen: OFF"
            fs_r = pygame.Rect(cx - toggle_w//2, cy + (row_h-btn_h)//2, toggle_w, btn_h)
            _draw_btn(fs_r, fs_text)
            rects["fullscreen"] = fs_r
            cy += row_h

            # VSync
            vs_text = "VSync: ON" if self.graphics_settings["vsync"] else "VSync: OFF"
            vs_r = pygame.Rect(cx - toggle_w//2, cy + (row_h-btn_h)//2, toggle_w, btn_h)
            _draw_btn(vs_r, vs_text)
            rects["vsync"] = vs_r
            cy += row_h

            # UI Scale
            lbl = f_btn.render("UI Scale:", True, WHITE)
            self.screen.blit(lbl, (label_x, cy + (row_h - lbl.get_height())//2))
            minus_r2 = pygame.Rect(cx - val_gap - btn_w, cy + (row_h-btn_h)//2, btn_w, btn_h)
            plus_r2  = pygame.Rect(cx + val_gap,         cy + (row_h-btn_h)//2, btn_w, btn_h)
            _draw_btn(minus_r2, "-")
            _draw_btn(plus_r2, "+")
            val2 = f_val.render(f"{self.graphics_settings['ui_scale']}%", True, YELLOW)
            self.screen.blit(val2, val2.get_rect(center=(cx, cy + row_h//2)))
            rects["scale_down"] = minus_r2
            rects["scale_up"] = plus_r2
            cy += row_h

        elif self.settings_tab == "sound":
            lbl = f_btn.render("Master Volume", True, WHITE)
            self.screen.blit(lbl, lbl.get_rect(center=(cx, cy + row_h//2 - int(10*s))))

            slider_w = int(420 * s)
            slider_h = max(6, int(10 * s))
            slider_x = cx - slider_w // 2
            slider_y = cy + int(42 * s)
            slider_r = pygame.Rect(slider_x, slider_y, slider_w, slider_h)

            pygame.draw.rect(self.screen, (40, 55, 90), slider_r, border_radius=6)
            fill_w = int(slider_w * (self.sound_settings["master_volume"] / 100.0))
            if fill_w > 0:
                pygame.draw.rect(self.screen, (0, 140, 255), pygame.Rect(slider_x, slider_y, fill_w, slider_h), border_radius=6)

            knob_x = slider_x + fill_w
            knob_x = max(slider_x, min(slider_x + slider_w, knob_x))
            knob_r = max(8, int(12 * s))
            pygame.draw.circle(self.screen, WHITE, (knob_x, slider_y + slider_h // 2), knob_r)
            pygame.draw.circle(self.screen, (0, 140, 255), (knob_x, slider_y + slider_h // 2), knob_r, 2)

            vol_val = f_val.render(f"{self.sound_settings['master_volume']}%", True, YELLOW)
            self.screen.blit(vol_val, vol_val.get_rect(center=(cx, slider_y + int(38 * s))))

            rects["master_volume_slider"] = slider_r
            cy += int(120 * s)

        else:  # developer tab
            info_lines = [
                f"Developer: Stepan Sitina",
                f"Version: {self.version}",
                f"Levels: 20",
                f"Game modes: 20",
                f"Player: {self.current_nickname if self.current_nickname else '-'}",
            ]
            for line in info_lines:
                t = f_btn.render(line, True, WHITE)
                self.screen.blit(t, t.get_rect(center=(cx, cy + row_h//2)))
                cy += row_h

            dev_btn_w = int(320 * s)
            dev_btn_h = int(48 * s)
            gap = int(14 * s)

            def _dev_button(key, text):
                nonlocal cy
                r = pygame.Rect(cx - dev_btn_w // 2, cy, dev_btn_w, dev_btn_h)
                _draw_btn(r, text)
                rects[key] = r
                cy += dev_btn_h + gap

            _dev_button("save_now", "SAVE NOW")
            _dev_button("export_zip", "EXPORT ZIP")
            _dev_button("import_zip", "IMPORT LATEST ZIP")

            if self.save_status_timer > 0 and self.save_status_message:
                status = f_btn.render(self.save_status_message, True, YELLOW)
                self.screen.blit(status, status.get_rect(center=(cx, cy + int(20*s))))

        # BACK button
        back_w, back_h = int(220*s), int(60*s)
        back_r = pygame.Rect(cx - back_w//2, sh - int(90*s), back_w, back_h)
        _draw_btn(back_r, "BACK")
        rects["back"] = back_r

        self._settings_rects = rects

    def _set_master_volume_from_slider_x(self, mouse_x):
        slider = self._settings_rects.get("master_volume_slider")
        if not slider or slider.width <= 0:
            return
        ratio = (mouse_x - slider.x) / slider.width
        ratio = max(0.0, min(1.0, ratio))
        vol = int(round(ratio * 100))
        self.sound_settings["master_volume"] = vol
        self.sfx.set_master_volume(vol / 100.0)
    
    def draw_play_menu(self):
        """Draw level selection – resolution & UI-scale adaptive"""
        sw, sh = self.screen_width, self.screen_height
        s = self._scale()
        self.screen.fill(self._tc("bg"))

        f_title = pygame.font.Font(None, max(20, int(72 * s)))
        f_lbl   = pygame.font.Font(None, max(12, int(32 * s)))

        title = f_title.render("VYBRAT LEVEL", True, self._tc("accent"))
        self.screen.blit(title, title.get_rect(center=(sw//2, int(50*s))))

        for level_num, button in self.level_buttons.items():
            if level_num <= self.unlocked_levels:
                if level_num in self.completed_levels:
                    pygame.draw.rect(self.screen, GREEN, button.rect)
                    pygame.draw.rect(self.screen, YELLOW, button.rect, 3)
                    done_text = f_lbl.render(f"LEVEL {level_num}*", True, BLACK)
                    self.screen.blit(done_text, done_text.get_rect(center=button.rect.center))
                else:
                    button.draw(self.screen)
            else:
                pygame.draw.rect(self.screen, DARK_GRAY, button.rect)
                pygame.draw.rect(self.screen, GRAY, button.rect, 3)
                lock_text = f_lbl.render("LOCKED", True, RED)
                self.screen.blit(lock_text, lock_text.get_rect(center=button.rect.center))

        self.play_buttons["back"].draw(self.screen)
    
    def draw_popup_menu(self):
        """Popup menu after level ends – scaled"""
        sw, sh = self.screen_width, self.screen_height
        s = self._scale()
        overlay = pygame.Surface((sw, sh))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        f_title = pygame.font.Font(None, max(20, int(80 * s)))
        f_info  = pygame.font.Font(None, max(14, int(50 * s)))

        txt = "YOU WON!" if self.game_won else "YOU LOST!"
        col = GREEN if self.game_won else RED
        title = f_title.render(txt, True, col)
        self.screen.blit(title, title.get_rect(center=(sw//2, int(250*s))))

        stars = self.level_stars.get(self.current_level, 0)
        stars_txt = f_info.render(f"Stars: {stars}/3", True, YELLOW)
        self.screen.blit(stars_txt, stars_txt.get_rect(center=(sw//2, int(315*s))))

        if hasattr(self.current_game, 'reaction_time_ms') and self.current_game.reaction_time_ms > 0:
            cur_t = f_info.render(f"Current time: {self.current_game.reaction_time_ms} ms", True, WHITE)
            self.screen.blit(cur_t, cur_t.get_rect(center=(sw//2, int(340*s))))
        elif self.current_level == 2:
            current_elapsed = self._get_current_elapsed_seconds()
            if current_elapsed is not None:
                cur_t = f_info.render(f"Current time: {int(current_elapsed * 1000)} ms", True, WHITE)
                self.screen.blit(cur_t, cur_t.get_rect(center=(sw//2, int(340*s))))
        else:
            current_elapsed = self._get_current_elapsed_seconds()
            if current_elapsed is not None:
                cur_t = f_info.render(f"Current time: {current_elapsed:.2f}s", True, WHITE)
                self.screen.blit(cur_t, cur_t.get_rect(center=(sw//2, int(340*s))))

        if self.current_level in self.level_best_reaction_ms:
            best_t = f_info.render(f"Best time: {self.level_best_reaction_ms[self.current_level]} ms", True, CYAN)
            self.screen.blit(best_t, best_t.get_rect(center=(sw//2, int(370*s))))
        elif self.current_level == 2 and self.current_level in self.level_best_time:
            best_ms = int(self.level_best_time[self.current_level] * 1000)
            best_t = f_info.render(f"Best time: {best_ms} ms", True, CYAN)
            self.screen.blit(best_t, best_t.get_rect(center=(sw//2, int(370*s))))
        elif self.current_level in self.level_best_time:
            best_t = f_info.render(f"Best time: {self.level_best_time[self.current_level]:.2f}s", True, CYAN)
            self.screen.blit(best_t, best_t.get_rect(center=(sw//2, int(370*s))))
        elif self.current_level in self.level_best_moves:
            best_m = f_info.render(f"Best moves: {self.level_best_moves[self.current_level]}", True, CYAN)
            self.screen.blit(best_m, best_m.get_rect(center=(sw//2, int(360*s))))

        if hasattr(self.current_game, 'reaction_time_ms') and self.current_game.reaction_time_ms > 0:
            time_text = f_info.render(f"Cas: {self.current_game.reaction_time_ms} ms", True, YELLOW)
            self.screen.blit(time_text, time_text.get_rect(center=(sw//2, int(400*s))))

        self.popup_buttons["menu"].draw(self.screen)
        self.popup_buttons["restart"].draw(self.screen)
        if self.game_won and self.current_level < 20:
            self.popup_buttons["next"].draw(self.screen)
    
    def draw_pause_menu(self):
        """Pause menu – scaled"""
        sw, sh = self.screen_width, self.screen_height
        s = self._scale()
        overlay = pygame.Surface((sw, sh))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        f_title = pygame.font.Font(None, max(20, int(80 * s)))
        title = f_title.render("PAUSE", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(sw//2, int(200*s))))

        self.pause_buttons["continue"].draw(self.screen)
        self.pause_buttons["restart"].draw(self.screen)
        self.pause_buttons["exit"].draw(self.screen)
    
    def draw_hint_popup(self):
        """Hint popup with word-wrap – scaled"""
        sw, sh = self.screen_width, self.screen_height
        s = self._scale()
        overlay = pygame.Surface((sw, sh))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        f_title = pygame.font.Font(None, max(20, int(80 * s)))
        f_body  = pygame.font.Font(None, max(14, int(50 * s)))
        f_close = pygame.font.Font(None, max(12, int(32 * s)))

        title = f_title.render("NAPOVEDA", True, YELLOW)
        self.screen.blit(title, title.get_rect(center=(sw//2, int(280*s))))

        hint = self.current_game.get_hint()
        max_chars = 55
        words = hint.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= max_chars:
                cur = cur + " " + w if cur else w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        line_h = int(42 * s)
        total_h = len(lines) * line_h + int(40 * s)
        box_w = int(900 * s)
        box_y = int(370 * s)
        box_rect = pygame.Rect(sw//2 - box_w//2, box_y, box_w, total_h)
        pygame.draw.rect(self.screen, BLUE, box_rect)
        pygame.draw.rect(self.screen, CYAN, box_rect, 3)

        for i, line in enumerate(lines):
            ht = f_body.render(line, True, GREEN)
            self.screen.blit(ht, ht.get_rect(center=(sw//2, box_y + int(20*s) + i*line_h + line_h//2)))

        ct = f_close.render("Klikni kdekoliv pro zavreni", True, WHITE)
        self.screen.blit(ct, ct.get_rect(center=(sw//2, box_y + total_h + int(40*s))))
    
    def handle_menu_click(self, pos):
        """Zpracuje klik v menu"""
        if self.menu_buttons["play"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.PLAYING
        elif self.menu_buttons["patch"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.PATCH_NOTES
        elif self.menu_buttons["settings"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.SETTINGS
        elif self.menu_buttons["themes"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.THEMES
        elif self.menu_buttons["sign_out"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.sign_out()
        elif self.menu_buttons["exit"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.save_game()
            self.running = False
        elif self.achievements_button.is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.ACHIEVEMENTS
    
    def handle_patch_click(self, pos):
        """Zpracuje klik v patch notes"""
        if self.patch_buttons["back"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.MENU

    def handle_achievements_click(self, pos):
        if self.achievements_buttons["back"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.MENU

    def handle_themes_click(self, pos):
        for name, button in self.theme_buttons.items():
            if button.is_clicked(pos):
                self.sfx.play("menu_click")
                self.current_theme = name
                self.save_game()
                return
        if self.achievements_buttons["back"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.MENU

    def handle_login_click(self, pos):
        if self.login_nickname_rect and self.login_nickname_rect.collidepoint(pos):
            self.login_active_field = "nickname"
            return
        if self.login_password_rect and self.login_password_rect.collidepoint(pos):
            self.login_active_field = "password"
            return

        if self.login_buttons["login"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.login_or_create_save(self.login_nickname_input, self.login_password_input)
        elif self.login_buttons["exit"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.running = False
    
    def handle_settings_click(self, pos):
        """Handle clicks on the dynamically-built settings UI."""
        R = self._settings_rects
        save_needed = False
        # Tabs
        if R.get("tab_graphics") and R["tab_graphics"].collidepoint(pos):
            self.sfx.play("menu_click")
            self.settings_tab = "graphics"
        elif R.get("tab_sound") and R["tab_sound"].collidepoint(pos):
            self.sfx.play("menu_click")
            self.settings_tab = "sound"
        elif R.get("tab_developer") and R["tab_developer"].collidepoint(pos):
            self.sfx.play("menu_click")
            self.settings_tab = "developer"
        # Graphics controls
        elif R.get("fps_down") and R["fps_down"].collidepoint(pos):
            self.sfx.play("menu_click")
            self.fps = max(10, self.fps - 10)
            save_needed = True
        elif R.get("fps_up") and R["fps_up"].collidepoint(pos):
            self.sfx.play("menu_click")
            self.fps = min(240, self.fps + 10)
            save_needed = True
        elif R.get("resolution_next") and R["resolution_next"].collidepoint(pos):
            self.sfx.play("menu_click")
            cur = self.graphics_settings["resolution"]
            if cur in self.available_resolutions:
                idx = (self.available_resolutions.index(cur) + 1) % len(self.available_resolutions)
            else:
                idx = 0
            self.change_resolution(self.available_resolutions[idx])
            save_needed = True
        elif R.get("fullscreen") and R["fullscreen"].collidepoint(pos):
            self.sfx.play("menu_click")
            self._toggle_fullscreen()
            save_needed = True
        elif R.get("vsync") and R["vsync"].collidepoint(pos):
            self.sfx.play("menu_click")
            self.graphics_settings["vsync"] = not self.graphics_settings["vsync"]
            save_needed = True
        elif R.get("scale_down") and R["scale_down"].collidepoint(pos):
            self.sfx.play("menu_click")
            idx = self.available_ui_scales.index(self.graphics_settings["ui_scale"])
            self.graphics_settings["ui_scale"] = self.available_ui_scales[(idx - 1) % len(self.available_ui_scales)]
            self.apply_ui_scale()
            save_needed = True
        elif R.get("scale_up") and R["scale_up"].collidepoint(pos):
            self.sfx.play("menu_click")
            idx = self.available_ui_scales.index(self.graphics_settings["ui_scale"])
            self.graphics_settings["ui_scale"] = self.available_ui_scales[(idx + 1) % len(self.available_ui_scales)]
            self.apply_ui_scale()
            save_needed = True
        elif R.get("master_volume_slider") and R["master_volume_slider"].collidepoint(pos):
            self.sound_slider_dragging = True
            self._set_master_volume_from_slider_x(pos[0])
            save_needed = True
        elif R.get("save_now") and R["save_now"].collidepoint(pos):
            self.sfx.play("menu_click")
            if self.save_game():
                self.save_status_message = "Save OK"
                self.save_status_timer = 180
        elif R.get("export_zip") and R["export_zip"].collidepoint(pos):
            self.sfx.play("menu_click")
            self.export_save_zip()
        elif R.get("import_zip") and R["import_zip"].collidepoint(pos):
            self.sfx.play("menu_click")
            self.import_latest_save_zip()
        # Back
        if R.get("back") and R["back"].collidepoint(pos):
            self.sfx.play("menu_click")
            self.sound_slider_dragging = False
            self.state = GameState.MENU

        if save_needed and self.current_nickname:
            self.save_game()
    
    def handle_play_click(self, pos):
        """Zpracuje klik v play menu"""
        # Zkontroluj odemčené levely (1-19)
        for level_num, button in self.level_buttons.items():
            if button.is_clicked(pos):
                if level_num <= self.unlocked_levels:
                    try:
                        self.sfx.play("menu_click")
                        self.current_level = level_num
                        self.game_won = False
                        self.level_completed = False
                        self.current_level_elapsed_snapshot = None
                        self.current_level_start_ticks = pygame.time.get_ticks()
                        self.level_attempt_mistakes[level_num] = 0
                        self.current_game = self.create_game_level(level_num)
                        if self.current_game is not None:
                            self.state = GameState.GAME
                        else:
                            print(f"Nelze spustit level {level_num}")
                    except Exception as e:
                        print(f"Chyba při spuštění levelu: {e}")
                        import traceback
                        traceback.print_exc()
                return
        
        if self.play_buttons["back"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.MENU
    
    def handle_popup_click(self, pos):
        """Zpracuje klik v popup menu"""
        if self.game_won:
            self.completed_levels.add(self.current_level)
        
        if self.popup_buttons["menu"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.PLAYING
        elif self.popup_buttons["restart"].is_clicked(pos):
            try:
                self.current_level_elapsed_snapshot = None
                self.current_level_start_ticks = pygame.time.get_ticks()
                self.current_game = self.create_game_level(self.current_level)
                self.level_completed = False
                self.game_won = False
            except Exception as e:
                print(f"Chyba při restartování levelu: {e}")
                self.state = GameState.PLAYING
        elif self.game_won and self.current_level < 20 and self.popup_buttons["next"].is_clicked(pos):
            if self.current_level < 20:
                self.sfx.play("menu_click")
                self.current_level += 1
                try:
                    self.current_level_elapsed_snapshot = None
                    self.current_level_start_ticks = pygame.time.get_ticks()
                    self.level_attempt_mistakes[self.current_level] = 0
                    self.current_game = self.create_game_level(self.current_level)
                    self.level_completed = False
                    self.game_won = False
                except Exception as e:
                    print(f"Chyba při zavádění dalšího levelu: {e}")
                    self.state = GameState.PLAYING
    
    def handle_pause_click(self, pos):
        """Zpracuje klik v pause menu"""
        if self.pause_buttons["continue"].is_clicked(pos):
            self.sfx.play("pause_toggle")
            self.pause_menu_open = False
        elif self.pause_buttons["restart"].is_clicked(pos):
            try:
                self.current_level_elapsed_snapshot = None
                self.current_level_start_ticks = pygame.time.get_ticks()
                self.current_game = self.create_game_level(self.current_level)
                self.level_completed = False
                self.game_won = False
                self.pause_menu_open = False
            except Exception as e:
                print(f"Chyba při restartů ze pauzy: {e}")
                self.state = GameState.PLAYING
                self.pause_menu_open = False
        elif self.pause_buttons["exit"].is_clicked(pos):
            self.sfx.play("menu_click")
            self.state = GameState.PLAYING
            self.pause_menu_open = False
    
    def create_game_level(self, level_num):
        """Vytvoří hru pro daný level s detailním error handlingem"""
        if level_num < 1 or level_num > 20:
            print(f"[ERROR] Level {level_num} neexistuje! Dostupné: 1-20")
            return None

        try:
            module_name = f"levels.level_{level_num:02d}"
            level_module = importlib.import_module(module_name)
            game_cls = level_module.get_level_class()
            game_name = game_cls.__name__
            print(f"[INFO] Inicializuji level {level_num}: {game_name}...")
            game_instance = game_cls()
            
            if game_instance is None:
                print(f"[ERROR] Level {level_num} ({game_name}) vrátil None!")
                return None

            game_instance.sfx = self.sfx
            self.current_level_elapsed_snapshot = None
            self.current_level_start_ticks = pygame.time.get_ticks()
            
            print(f"[SUCCESS] Level {level_num} ({game_name}) úspěšně načten!")
            self.sfx.play("level_start")
            return game_instance
            
        except TypeError as e:
            print(f"[ERROR] TypeError v konstruktoru levelu {level_num}: {e}")
            import traceback
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"[CRASH] Neznámá chyba při vytváření levelu {level_num}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def handle_events(self):
        """Zpracuje všechny eventy"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEMOTION:
                if self.state == GameState.SETTINGS and self.settings_tab == "sound" and self.sound_slider_dragging:
                    self._set_master_volume_from_slider_x(mouse_pos[0])
                for button in self.login_buttons.values():
                    button.is_hovered(mouse_pos)
                for button in self.menu_buttons.values():
                    button.is_hovered(mouse_pos)
                self.achievements_button.is_hovered(mouse_pos)
                for button in self.theme_buttons.values():
                    button.is_hovered(mouse_pos)
                for button in self.patch_buttons.values():
                    button.is_hovered(mouse_pos)
                for button in self.play_buttons.values():
                    button.is_hovered(mouse_pos)
                for button in self.level_buttons.values():
                    button.is_hovered(mouse_pos)
                for button in self.popup_buttons.values():
                    button.is_hovered(mouse_pos)
                for button in self.pause_buttons.values():
                    button.is_hovered(mouse_pos)
                for button in self.achievements_buttons.values():
                    button.is_hovered(mouse_pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.LOGIN:
                    self.handle_login_click(mouse_pos)
                elif self.state == GameState.MENU:
                    self.handle_menu_click(mouse_pos)
                elif self.state == GameState.PATCH_NOTES:
                    self.handle_patch_click(mouse_pos)
                elif self.state == GameState.SETTINGS:
                    self.handle_settings_click(mouse_pos)
                elif self.state == GameState.ACHIEVEMENTS:
                    self.handle_achievements_click(mouse_pos)
                elif self.state == GameState.THEMES:
                    self.handle_themes_click(mouse_pos)
                elif self.state == GameState.PLAYING:
                    self.handle_play_click(mouse_pos)
                elif self.state == GameState.GAME:
                    if self.show_hint_popup:
                        self.sfx.play("menu_click")
                        self.show_hint_popup = False
                    elif self.pause_menu_open:
                        self.handle_pause_click(mouse_pos)
                    elif self.level_completed:
                        self.handle_popup_click(mouse_pos)
                    elif self.current_game:
                        self.current_game.handle_event(event)

            if event.type == pygame.MOUSEBUTTONUP:
                self.sound_slider_dragging = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.LOGIN:
                    if event.key == pygame.K_RETURN:
                        self.login_or_create_save(self.login_nickname_input, self.login_password_input)
                    elif event.key == pygame.K_ESCAPE:
                        self.sfx.play("menu_click")
                        self.running = False
                    elif event.key == pygame.K_TAB:
                        self.login_active_field = "password" if self.login_active_field == "nickname" else "nickname"
                    elif event.key == pygame.K_BACKSPACE:
                        if self.login_active_field == "nickname":
                            self.login_nickname_input = self.login_nickname_input[:-1]
                        else:
                            self.login_password_input = self.login_password_input[:-1]
                    elif event.unicode:
                        if self.login_active_field == "nickname":
                            if len(self.login_nickname_input) < 20 and re.fullmatch(r"[A-Za-z0-9_\-]", event.unicode):
                                self.login_nickname_input += event.unicode
                        else:
                            if len(self.login_password_input) < 32 and event.unicode.isprintable() and not event.unicode.isspace():
                                self.login_password_input += event.unicode
                    continue

                if event.key == pygame.K_o:
                    if self.admin_access and self._is_admin_nickname(self.current_nickname):
                        self.admin_mode = not self.admin_mode
                        if self.admin_mode:
                            self._unlocked_levels_before_admin = self.unlocked_levels
                            self.unlocked_levels = TOTAL_LEVELS
                        else:
                            self._reconcile_unlocked_levels()
                            self.unlocked_levels = max(self.unlocked_levels, min(TOTAL_LEVELS, self._unlocked_levels_before_admin))
                if event.key == pygame.K_ESCAPE:
                    if self.state in (GameState.PATCH_NOTES, GameState.SETTINGS, GameState.PLAYING, GameState.ACHIEVEMENTS, GameState.THEMES):
                        self.sfx.play("menu_click")
                        self.state = GameState.MENU
                    elif self.state == GameState.GAME:
                        if not self.level_completed:
                            self.sfx.play("pause_toggle")
                            self.pause_menu_open = not self.pause_menu_open
                if event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                if self.state == GameState.GAME:
                    if event.key == pygame.K_SPACE:
                        self.space_press_count += 1
                        self.space_press_timer = 15
                        if self.space_press_count >= 2 and not self.level_completed and not self.pause_menu_open:
                            self.show_hint_popup = True
                            self.hint_popup_timer = 400
                            self.space_press_count = 0
                    elif not self.level_completed and not self.pause_menu_open:
                        self.current_game.handle_event(event)
    
    def update(self):
        """Aktualizuje stav hry"""
        if self.win_anim_timer > 0:
            self.win_anim_timer -= 1
            for p in self.win_anim_particles:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.12

        if self.screen_glow_timer > 0:
            self.screen_glow_timer -= 1
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= 1

        for note in self.achievement_notifications:
            note["timer"] -= 1
        self.achievement_notifications = [n for n in self.achievement_notifications if n["timer"] > 0]

        if self.save_status_timer > 0:
            self.save_status_timer -= 1

        if self.state == GameState.GAME and not self.level_completed and self.current_game and not self.pause_menu_open:
            self.current_game.update()
            if self.current_game.is_won():
                self.level_completed = True
                self.game_won = True
                self.sfx.play("level_success")
                self.sfx.play("level_complete")

                elapsed = 0.0
                if self.current_level_start_ticks > 0:
                    elapsed = (pygame.time.get_ticks() - self.current_level_start_ticks) / 1000.0
                if elapsed > 0:
                    self.current_level_elapsed_snapshot = elapsed

                reaction_ms = None
                if hasattr(self.current_game, "reaction_time_ms"):
                    try:
                        reaction_ms = int(self.current_game.reaction_time_ms)
                    except Exception:
                        reaction_ms = None

                if reaction_ms is not None and reaction_ms > 0:
                    best_ms = self.level_best_reaction_ms.get(self.current_level)
                    if best_ms is None or reaction_ms < best_ms:
                        self.level_best_reaction_ms[self.current_level] = reaction_ms
                    self.current_level_elapsed_snapshot = reaction_ms / 1000.0
                elif self.current_level == 2 and elapsed > 0:
                    reaction_ms = int(elapsed * 1000)
                    best_ms = self.level_best_reaction_ms.get(2)
                    if best_ms is None or reaction_ms < best_ms:
                        self.level_best_reaction_ms[2] = reaction_ms
                    self.current_level_elapsed_snapshot = reaction_ms / 1000.0
                elif elapsed > 0:
                    best = self.level_best_time.get(self.current_level)
                    if best is None or elapsed < best:
                        self.level_best_time[self.current_level] = elapsed

                moves = self._get_moves_used()
                if moves is not None:
                    best_moves = self.level_best_moves.get(self.current_level)
                    if best_moves is None or moves < best_moves:
                        self.level_best_moves[self.current_level] = moves

                stars = self._calculate_stars(self.level_attempt_mistakes[self.current_level])
                self.level_stars[self.current_level] = max(self.level_stars[self.current_level], stars)

                self._unlock_achievement(f"level_{self.current_level}")
                if self.current_level == 1:
                    self._unlock_achievement("record_l1")

                remain = self._get_remaining_seconds()
                if remain is not None and remain >= 3:
                    if self.current_level == 1:
                        self._unlock_achievement("speed_l1")
                    if self.current_level == 8:
                        self._unlock_achievement("speed_l8")

                if len(self.completed_levels | {self.current_level}) >= 20:
                    self._unlock_achievement("all_levels")

                self._start_win_animation()
                if self.current_level == self.unlocked_levels and self.unlocked_levels < TOTAL_LEVELS:
                    self.unlocked_levels += 1
                self.save_game()
            elif self.current_game.is_lost():
                self.level_completed = True
                self.game_won = False
                self.sfx.play("level_fail")
                if self.current_level_start_ticks > 0:
                    self.current_level_elapsed_snapshot = (pygame.time.get_ticks() - self.current_level_start_ticks) / 1000.0
                self.level_attempt_mistakes[self.current_level] += 1
                self.save_game()
        
        if self.hint_popup_timer > 0:
            self.hint_popup_timer -= 1
        else:
            self.show_hint_popup = False
        
        if self.space_press_timer > 0:
            self.space_press_timer -= 1
        else:
            self.space_press_count = 0
    
    def draw(self):
        """Kreslí vše na obrazovku"""
        self._apply_theme_to_buttons()
        if self.state == GameState.LOGIN:
            self.draw_login()
        elif self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PATCH_NOTES:
            self.draw_patch_notes()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.ACHIEVEMENTS:
            self.draw_achievements()
        elif self.state == GameState.THEMES:
            self.draw_themes()
        elif self.state == GameState.PLAYING:
            self.draw_play_menu()
        elif self.state == GameState.GAME:
            if self.current_game:
                self.current_game.draw(self.screen)
                s = self._scale()
                f_hud  = pygame.font.Font(None, max(12, int(32 * s)))
                f_hint = pygame.font.Font(None, max(12, int(24 * s)))
                level_text = f_hud.render(f"Level: {self.current_level}/20", True, WHITE)
                self.screen.blit(level_text, (self.screen_width - int(200*s), int(10*s)))
                self._draw_progress_bar()

                stars = self.level_stars.get(self.current_level, 0)
                stars_txt = f_hud.render(f"Stars: {stars}/3", True, YELLOW)
                self.screen.blit(stars_txt, (self.screen_width - int(200*s), int(64*s)))

                if self.current_level in self.level_best_reaction_ms:
                    if hasattr(self.current_game, 'reaction_time_ms') and self.current_game.reaction_time_ms > 0:
                        ct = f_hint.render(f"Current: {self.current_game.reaction_time_ms}ms", True, WHITE)
                        self.screen.blit(ct, (self.screen_width - int(220*s), int(92*s)))
                    elif self.current_level == 2:
                        cur_elapsed = self._get_current_elapsed_seconds()
                        if cur_elapsed is not None:
                            ct = f_hint.render(f"Current: {int(cur_elapsed * 1000)}ms", True, WHITE)
                            self.screen.blit(ct, (self.screen_width - int(220*s), int(92*s)))
                    bt = f_hint.render(f"Best: {self.level_best_reaction_ms[self.current_level]}ms", True, CYAN)
                    self.screen.blit(bt, (self.screen_width - int(220*s), int(114*s)))
                elif self.current_level == 2 and self.current_level in self.level_best_time:
                    cur_elapsed = self._get_current_elapsed_seconds()
                    if cur_elapsed is not None:
                        ct = f_hint.render(f"Current: {int(cur_elapsed * 1000)}ms", True, WHITE)
                        self.screen.blit(ct, (self.screen_width - int(220*s), int(92*s)))
                    bt = f_hint.render(f"Best: {int(self.level_best_time[self.current_level] * 1000)}ms", True, CYAN)
                    self.screen.blit(bt, (self.screen_width - int(220*s), int(114*s)))
                elif self.current_level in self.level_best_time:
                    cur_elapsed = self._get_current_elapsed_seconds()
                    if cur_elapsed is not None:
                        ct = f_hint.render(f"Current: {cur_elapsed:.2f}s", True, WHITE)
                        self.screen.blit(ct, (self.screen_width - int(220*s), int(92*s)))
                    bt = f_hint.render(f"Best: {self.level_best_time[self.current_level]:.2f}s", True, CYAN)
                    self.screen.blit(bt, (self.screen_width - int(220*s), int(114*s)))
                elif self.current_level in self.level_best_moves:
                    bm = f_hint.render(f"Best moves: {self.level_best_moves[self.current_level]}", True, CYAN)
                    self.screen.blit(bm, (self.screen_width - int(220*s), int(92*s)))

                hint_text = f_hint.render("Napoveda: 2x SPACE | ESC: Menu", True, YELLOW)
                self.screen.blit(hint_text, (int(10*s), int(10*s)))
                
                if self.show_hint_popup:
                    self.draw_hint_popup()
                
                if self.pause_menu_open:
                    self.draw_pause_menu()
                
                if self.level_completed:
                    self.draw_popup_menu()

                if self.win_anim_timer > 0 and self.game_won:
                    for p in self.win_anim_particles:
                        pygame.draw.circle(self.screen, p["col"], (int(p["x"]), int(p["y"])), p["size"])

                if self.screen_shake_timer > 0:
                    dx = random.randint(-3, 3)
                    dy = random.randint(-3, 3)
                    shaken = self.screen.copy()
                    self.screen.fill(BLACK)
                    self.screen.blit(shaken, (dx, dy))

                if self.screen_glow_timer > 0:
                    alpha = int(120 * (self.screen_glow_timer / 24.0))
                    glow = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                    ac = self._tc("accent")
                    glow.fill((ac[0], ac[1], ac[2], alpha))
                    self.screen.blit(glow, (0, 0))

        self._draw_achievement_notifications()
        
        pygame.display.flip()
    
    def run(self):
        """Hlavní herní smyčka"""
        while self.running:
            frame_ms = self.clock.tick_busy_loop(max(1, int(self.fps)))
            self._logic_accumulator += frame_ms / 1000.0

            self.handle_events()

            max_acc = self._logic_dt * self._max_catchup_steps
            if self._logic_accumulator > max_acc:
                self._logic_accumulator = max_acc

            while self._logic_accumulator >= self._logic_dt:
                self.update()
                self._logic_accumulator -= self._logic_dt

            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()


