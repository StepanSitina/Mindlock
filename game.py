import pygame
import sys
import random
import math
from enum import Enum
from collections import defaultdict, deque


pygame.init()


# =====================================
# VERSION SYSTEM FIX
# =====================================
GAME_VERSION = "1.8.0"

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

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PATCH_NOTES = 3
    SETTINGS = 4
    GAME = 5
    LEVEL_COMPLETE = 6
    GAME_OVER = 7

class Button:
    def __init__(self, x, y, width, height, text, font=FONT_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False
        self.color = BLUE
        self.hover_color = CYAN
        
    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 3)
        text_surface = self.font.render(self.text, True, BLACK)
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
        self.state = GameState.MENU
        self.fps = 60
        self.current_level = 1
        self.unlocked_levels = 1
        self.level_completed = False
        self.game_won = False
        self.admin_mode = False
        self.show_hint = False
        self.hint_timer = 0
        self.pause_menu_open = False
        self.show_hint_popup = False
        self.hint_popup_timer = 0
        self.completed_levels = set()
        self.space_pressed = False
        self.space_press_count = 0
        self.space_press_timer = 0
        self.current_game = None
        
        self.version = GAME_VERSION
        
        self.menu_buttons = {
            "play": Button(self.screen_width//2 - 140, 250, 280, 60, "PLAY"),
            "patch": Button(self.screen_width//2 - 140, 350, 280, 60, "PATCH NOTES"),
            "settings": Button(self.screen_width//2 - 140, 450, 280, 60, "SETTINGS"),
            "exit": Button(self.screen_width//2 - 140, 550, 280, 60, "EXIT")
        }
        
        self.patch_notes = [
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
        self.settings_tab = "graphics"  # "graphics" or "developer"
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
        """Toggle real fullscreen / windowed mode"""
        self.graphics_settings["fullscreen"] = not self.graphics_settings["fullscreen"]
        if self.graphics_settings["fullscreen"]:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height))
    
    def initialize_ui_elements(self):
        """Reinitialize all UI elements for current resolution"""
        sw, sh = self.screen_width, self.screen_height
        s = min(sw / 1920, sh / 1080)  # global scale factor
        bw, bh = int(280 * s), int(60 * s)
        self.menu_buttons = {
            "play":     Button(sw//2 - bw//2, int(250*s), bw, bh, "PLAY"),
            "patch":    Button(sw//2 - bw//2, int(350*s), bw, bh, "PATCH NOTES"),
            "settings": Button(sw//2 - bw//2, int(450*s), bw, bh, "SETTINGS"),
            "exit":     Button(sw//2 - bw//2, int(550*s), bw, bh, "EXIT")
        }
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
        self.create_level_buttons()
        
    def create_level_buttons(self):
        """Vytvoří tlačítka pro všech 20 levelů"""
        for i in range(1, 21):
            col = (i - 1) % 5
            row = (i - 1) // 5
            x = 150 + col * 180
            y = 150 + row * 120
            self.level_buttons[i] = Button(x, y, 160, 100, f"LEVEL {i}", FONT_SMALL)
    
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
        """Kreslí hlavní menu"""
        self.screen.fill((20, 40, 80))
        
  
        title = FONT_LARGE.render("MindLock!", True, CYAN)
        title_rect = title.get_rect(center=(self.screen_width//2, 90))
       
        shadow = FONT_LARGE.render("MindLock!", True, (0, 50, 80))
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
      
        pygame.draw.line(self.screen, CYAN, (self.screen_width//2 - 300, 160), (self.screen_width//2 - 100, 160), 2)
        pygame.draw.line(self.screen, CYAN, (self.screen_width//2 + 100, 160), (self.screen_width//2 + 300, 160), 2)
        

        subtitle = FONT_SMALL.render("Puzzle Game", True, (200, 200, 255))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width//2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
  
        for button in self.menu_buttons.values():
            button.draw(self.screen)
    
    def draw_patch_notes(self):
        """Kreslí patch notes"""
        self.screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("PATCH NOTES", True, CYAN)
        title_rect = title.get_rect(center=(self.screen_width//2, 40))
        self.screen.blit(title, title_rect)
        

        box_rect = pygame.Rect(150, 120, self.screen_width - 300, 500)
        pygame.draw.rect(self.screen, DARK_GRAY, box_rect)
        pygame.draw.rect(self.screen, CYAN, box_rect, 3)
        
     
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
        """Resolution-adaptive settings screen with tabs."""
        sw, sh = self.screen_width, self.screen_height
        s = min(sw / 1920, sh / 1080)
        self.screen.fill((0, 0, 51))  # dark navy
        rects = {}  # collect clickable rects this frame

        # Scaled fonts
        f_title = pygame.font.Font(None, max(20, int(72 * s)))
        f_btn   = pygame.font.Font(None, max(14, int(36 * s)))
        f_val   = pygame.font.Font(None, max(14, int(40 * s)))
        f_small = pygame.font.Font(None, max(12, int(28 * s)))

        # --- Title ---
        title_surf = f_title.render("SETTINGS", True, CYAN)
        self.screen.blit(title_surf, title_surf.get_rect(center=(sw//2, int(50*s))))

        # --- Tabs ---
        tab_w, tab_h = int(200*s), int(50*s)
        tab_gap = int(20*s)
        tabs_total = tab_w * 2 + tab_gap
        tx = sw//2 - tabs_total//2
        ty = int(110*s)
        for i, (tab_id, tab_label) in enumerate([("graphics", "Graphics"), ("developer", "Developer")]):
            r = pygame.Rect(tx + i*(tab_w + tab_gap), ty, tab_w, tab_h)
            active = self.settings_tab == tab_id
            col = (0, 102, 255) if active else (40, 40, 80)
            pygame.draw.rect(self.screen, col, r)
            pygame.draw.rect(self.screen, (100, 180, 255) if active else (80, 80, 120), r, 2)
            lbl = f_btn.render(tab_label, True, WHITE)
            self.screen.blit(lbl, lbl.get_rect(center=r.center))
            rects[f"tab_{tab_id}"] = r

        # --- Content area ---
        cy = ty + tab_h + int(40*s)  # current Y cursor
        row_h = int(55*s)
        btn_w = int(50*s)
        btn_h = int(44*s)
        toggle_w = int(300*s)
        cx = sw // 2  # center X

        def _draw_btn(rect, text, font=f_btn):
            pygame.draw.rect(self.screen, (0, 102, 255), rect)
            pygame.draw.rect(self.screen, (100, 180, 255), rect, 2)
            t = font.render(text, True, WHITE)
            self.screen.blit(t, t.get_rect(center=rect.center))

        if self.settings_tab == "graphics":
            # Row: FPS
            lbl = f_btn.render("FPS:", True, WHITE)
            lbl_x = cx - int(180*s)
            self.screen.blit(lbl, (lbl_x, cy + (row_h - lbl.get_height())//2))
            minus_r = pygame.Rect(cx - int(20*s) - btn_w, cy + (row_h-btn_h)//2, btn_w, btn_h)
            plus_r  = pygame.Rect(cx + int(20*s),         cy + (row_h-btn_h)//2, btn_w, btn_h)
            _draw_btn(minus_r, "-")
            _draw_btn(plus_r, "+")
            val = f_val.render(str(self.fps), True, YELLOW)
            self.screen.blit(val, val.get_rect(center=(cx, cy + row_h//2)))
            rects["fps_down"] = minus_r
            rects["fps_up"] = plus_r
            cy += row_h

            # Row: Resolution
            lbl = f_btn.render("Resolution:", True, WHITE)
            self.screen.blit(lbl, (lbl_x, cy + (row_h - lbl.get_height())//2))
            res_val = f_val.render(self.graphics_settings["resolution"], True, YELLOW)
            self.screen.blit(res_val, res_val.get_rect(center=(cx, cy + row_h//2)))
            arr_r = pygame.Rect(cx + int(90*s), cy + (row_h-btn_h)//2, btn_w, btn_h)
            _draw_btn(arr_r, ">")
            rects["resolution_next"] = arr_r
            cy += row_h

            # Row: Fullscreen
            fs_text = "Fullscreen: ON" if self.graphics_settings["fullscreen"] else "Fullscreen: OFF"
            fs_r = pygame.Rect(cx - toggle_w//2, cy + (row_h-btn_h)//2, toggle_w, btn_h)
            _draw_btn(fs_r, fs_text)
            rects["fullscreen"] = fs_r
            cy += row_h

            # Row: VSync
            vs_text = "VSync: ON" if self.graphics_settings["vsync"] else "VSync: OFF"
            vs_r = pygame.Rect(cx - toggle_w//2, cy + (row_h-btn_h)//2, toggle_w, btn_h)
            _draw_btn(vs_r, vs_text)
            rects["vsync"] = vs_r
            cy += row_h

            # Row: UI Scale
            lbl = f_btn.render("UI Scale:", True, WHITE)
            self.screen.blit(lbl, (lbl_x, cy + (row_h - lbl.get_height())//2))
            minus_r2 = pygame.Rect(cx - int(20*s) - btn_w, cy + (row_h-btn_h)//2, btn_w, btn_h)
            plus_r2  = pygame.Rect(cx + int(20*s),         cy + (row_h-btn_h)//2, btn_w, btn_h)
            _draw_btn(minus_r2, "-")
            _draw_btn(plus_r2, "+")
            val2 = f_val.render(f"{self.graphics_settings['ui_scale']}%", True, YELLOW)
            self.screen.blit(val2, val2.get_rect(center=(cx, cy + row_h//2)))
            rects["scale_down"] = minus_r2
            rects["scale_up"] = plus_r2
            cy += row_h

        else:  # developer tab
            info_lines = [
                f"Developer: Stepan Sitina",
                f"Version: {self.version}",
                f"Levels: 20",
                f"Game modes: 20",
            ]
            for line in info_lines:
                t = f_btn.render(line, True, WHITE)
                self.screen.blit(t, t.get_rect(center=(cx, cy + row_h//2)))
                cy += row_h

        # --- BACK button (bottom center) ---
        back_w, back_h = int(220*s), int(60*s)
        back_r = pygame.Rect(cx - back_w//2, sh - int(90*s), back_w, back_h)
        _draw_btn(back_r, "BACK")
        rects["back"] = back_r

        self._settings_rects = rects
    
    def draw_play_menu(self):
        """Kreslí menu pro výběr levelů"""
        self.screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("VYBRAT LEVEL", True, CYAN)
        title_rect = title.get_rect(center=(self.screen_width//2, 30))
        self.screen.blit(title, title_rect)
        
        for level_num, button in self.level_buttons.items():
            if level_num <= self.unlocked_levels:
                if level_num in self.completed_levels:
                    pygame.draw.rect(self.screen, GREEN, button.rect)
                    pygame.draw.rect(self.screen, YELLOW, button.rect, 3)
                    done_text = FONT_SMALL.render(f"LEVEL {level_num}*", True, BLACK)
                    done_rect = done_text.get_rect(center=button.rect.center)
                    self.screen.blit(done_text, done_rect)
                else:
                    button.draw(self.screen)
            else:
                # No special display for levels beyond 19
                pygame.draw.rect(self.screen, DARK_GRAY, button.rect)
                pygame.draw.rect(self.screen, GRAY, button.rect, 3)
                lock_text = FONT_SMALL.render("LOCKED", True, RED)
                lock_rect = lock_text.get_rect(center=button.rect.center)
                self.screen.blit(lock_text, lock_rect)
        
        self.play_buttons["back"].draw(self.screen)
    
    def draw_popup_menu(self):
        """Kreslí popup menu po skončení levelu"""

        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.game_won:
            title = FONT_LARGE.render("YOU WON!", True, GREEN)
        else:
            title = FONT_LARGE.render("YOU LOST!", True, RED)
        
        title_rect = title.get_rect(center=(self.screen_width//2, 250))
        self.screen.blit(title, title_rect)
        
        # Zobraz čas pro ReactionTime
        if hasattr(self.current_game, 'reaction_time_ms') and self.current_game.reaction_time_ms > 0:
            time_text = FONT_MEDIUM.render(f"Cas: {self.current_game.reaction_time_ms} ms", True, YELLOW)
            self.screen.blit(time_text, (self.screen_width//2 - 180, 350))
        
        self.popup_buttons["menu"].draw(self.screen)
        self.popup_buttons["restart"].draw(self.screen)
        
        if self.game_won and self.current_level < 20:
            self.popup_buttons["next"].draw(self.screen)
    
    def draw_pause_menu(self):
        """Kreslí pause menu"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = FONT_LARGE.render("PAUSE", True, YELLOW)
        title_rect = title.get_rect(center=(self.screen_width//2, 200))
        self.screen.blit(title, title_rect)
        
        self.pause_buttons["continue"].draw(self.screen)
        self.pause_buttons["restart"].draw(self.screen)
        self.pause_buttons["exit"].draw(self.screen)
    
    def draw_hint_popup(self):
        """Kreslí hint popup s word-wrapem"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        hint_title = FONT_LARGE.render("NAPOVEDA", True, YELLOW)
        hint_title_rect = hint_title.get_rect(center=(self.screen_width//2, 280))
        self.screen.blit(hint_title, hint_title_rect)
        
        hint = self.current_game.get_hint()
        # Word-wrap the hint into lines that fit on screen
        max_chars = 55
        words = hint.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 <= max_chars:
                cur = cur + " " + w if cur else w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        
        # Calculate box size
        line_h = 42
        total_h = len(lines) * line_h + 40
        box_w = 900
        box_y = 370
        box_rect = pygame.Rect(self.screen_width//2 - box_w//2, box_y, box_w, total_h)
        pygame.draw.rect(self.screen, BLUE, box_rect)
        pygame.draw.rect(self.screen, CYAN, box_rect, 3)
        
        for i, line in enumerate(lines):
            hint_text = FONT_MEDIUM.render(line, True, GREEN)
            hint_rect = hint_text.get_rect(center=(self.screen_width//2, box_y + 20 + i * line_h + line_h//2))
            self.screen.blit(hint_text, hint_rect)
        
        close_text = FONT_SMALL.render("Klikni kdekoliv pro zavreni", True, WHITE)
        close_rect = close_text.get_rect(center=(self.screen_width//2, box_y + total_h + 40))
        self.screen.blit(close_text, close_rect)
    
    def handle_menu_click(self, pos):
        """Zpracuje klik v menu"""
        if self.menu_buttons["play"].is_clicked(pos):
            self.state = GameState.PLAYING
        elif self.menu_buttons["patch"].is_clicked(pos):
            self.state = GameState.PATCH_NOTES
        elif self.menu_buttons["settings"].is_clicked(pos):
            self.state = GameState.SETTINGS
        elif self.menu_buttons["exit"].is_clicked(pos):
            self.running = False
    
    def handle_patch_click(self, pos):
        """Zpracuje klik v patch notes"""
        if self.patch_buttons["back"].is_clicked(pos):
            self.state = GameState.MENU
    
    def handle_settings_click(self, pos):
        """Handle clicks on the dynamically-built settings UI."""
        R = self._settings_rects
        # Tabs
        if R.get("tab_graphics") and R["tab_graphics"].collidepoint(pos):
            self.settings_tab = "graphics"
        elif R.get("tab_developer") and R["tab_developer"].collidepoint(pos):
            self.settings_tab = "developer"
        # Graphics controls
        elif R.get("fps_down") and R["fps_down"].collidepoint(pos):
            self.fps = max(10, self.fps - 10)
        elif R.get("fps_up") and R["fps_up"].collidepoint(pos):
            self.fps = min(240, self.fps + 10)
        elif R.get("resolution_next") and R["resolution_next"].collidepoint(pos):
            cur = self.graphics_settings["resolution"]
            if cur in self.available_resolutions:
                idx = (self.available_resolutions.index(cur) + 1) % len(self.available_resolutions)
            else:
                idx = 0
            self.change_resolution(self.available_resolutions[idx])
        elif R.get("fullscreen") and R["fullscreen"].collidepoint(pos):
            self._toggle_fullscreen()
        elif R.get("vsync") and R["vsync"].collidepoint(pos):
            self.graphics_settings["vsync"] = not self.graphics_settings["vsync"]
        elif R.get("scale_down") and R["scale_down"].collidepoint(pos):
            idx = self.available_ui_scales.index(self.graphics_settings["ui_scale"])
            self.graphics_settings["ui_scale"] = self.available_ui_scales[(idx - 1) % len(self.available_ui_scales)]
            self.apply_ui_scale()
        elif R.get("scale_up") and R["scale_up"].collidepoint(pos):
            idx = self.available_ui_scales.index(self.graphics_settings["ui_scale"])
            self.graphics_settings["ui_scale"] = self.available_ui_scales[(idx + 1) % len(self.available_ui_scales)]
            self.apply_ui_scale()
        # Back
        if R.get("back") and R["back"].collidepoint(pos):
            self.state = GameState.MENU
    
    def handle_play_click(self, pos):
        """Zpracuje klik v play menu"""
        # Zkontroluj odemčené levely (1-19)
        for level_num, button in self.level_buttons.items():
            if button.is_clicked(pos):
                if level_num <= self.unlocked_levels:
                    try:
                        self.current_level = level_num
                        self.game_won = False
                        self.level_completed = False
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
            self.state = GameState.MENU
    
    def handle_popup_click(self, pos):
        """Zpracuje klik v popup menu"""
        if self.game_won:
            self.completed_levels.add(self.current_level)
        
        if self.popup_buttons["menu"].is_clicked(pos):
            self.state = GameState.PLAYING
        elif self.popup_buttons["restart"].is_clicked(pos):
            try:
                self.current_game = self.create_game_level(self.current_level)
                self.level_completed = False
                self.game_won = False
            except Exception as e:
                print(f"Chyba při restartování levelu: {e}")
                self.state = GameState.PLAYING
        elif self.game_won and self.current_level < 20 and self.popup_buttons["next"].is_clicked(pos):
            if self.current_level < 20:
                self.current_level += 1
                try:
                    self.current_game = self.create_game_level(self.current_level)
                    self.level_completed = False
                    self.game_won = False
                except Exception as e:
                    print(f"Chyba při zavádění dalšího levelu: {e}")
                    self.state = GameState.PLAYING
    
    def handle_pause_click(self, pos):
        """Zpracuje klik v pause menu"""
        if self.pause_buttons["continue"].is_clicked(pos):
            self.pause_menu_open = False
        elif self.pause_buttons["restart"].is_clicked(pos):
            try:
                self.current_game = self.create_game_level(self.current_level)
                self.level_completed = False
                self.game_won = False
                self.pause_menu_open = False
            except Exception as e:
                print(f"Chyba při restartů ze pauzy: {e}")
                self.state = GameState.PLAYING
                self.pause_menu_open = False
        elif self.pause_buttons["exit"].is_clicked(pos):
            self.state = GameState.PLAYING
            self.pause_menu_open = False
    
    def create_game_level(self, level_num):
        """Vytvoří hru pro daný level s detailním error handlingem"""
        if level_num < 1 or level_num > 20:
            print(f"❌ [ERROR] Level {level_num} neexistuje! Dostupné: 1-20")
            return None
        
        game_creators = [
            # --- EASY (levels 1-5): simple mechanics, instant feedback ---
            ("SpeedClick", lambda: SpeedClick()),          #  1 - just click fast
            ("ReactionTime", lambda: ReactionTime()),      #  2 - wait & click
            ("ColorMatch", lambda: ColorMatch()),           #  3 - match colors
            ("ColorBlind", lambda: ColorBlind()),           #  4 - spot the odd color
            ("NumberSort", lambda: NumberSort()),           #  5 - sort numbers in order
            # --- MEDIUM (levels 6-10): memory & word knowledge ---
            ("SimonSays", lambda: SimonSays()),             #  6 - remember sequences
            ("MemoryCards", lambda: MemoryCards()),         #  7 - flip & match pairs
            ("TimeBomb", lambda: TimeBomb()),               #  8 - defuse under pressure
            ("Hangman", lambda: Hangman()),                 #  9 - guess word from riddles
            ("WordUnscrambler", lambda: WordUnscrambler()), # 10 - unscramble letters
            # --- HARD (levels 11-14): spatial & logic puzzles ---
            ("Maze", lambda: Maze()),                       # 11 - navigate a maze
            ("RotatingImage", lambda: RotatingImage()),     # 12 - rotate tiles
            ("RiddleGame", lambda: RiddleGame()),           # 13 - solve riddles
            ("TetrisLite", lambda: TetrisLite()),           # 14 - tetris gameplay
            # --- VERY HARD (levels 15-20): multi-step reasoning ---
            ("QuantumSwitches", lambda: QuantumSwitches()), # 15 - linked toggle switches
            ("CipherBreaker", lambda: CipherBreaker()),     # 16 - Caesar cipher decode
            ("PipeRotate", lambda: PipeRotate()),           # 17 - rotate pipes to connect
            ("CableConnect", lambda: CableConnect()),       # 18 - cables with locks & decoys
            ("LaserMirrors", lambda: LaserMirrors()),        # 19 - laser w/ portals & 8 mirrors
            ("RollingBalls", lambda: RollingBalls()),       # 20 - tilt board, slide ball to goal
        ]
        
        try:
            game_name, game_creator = game_creators[level_num - 1]
            print(f"🎮 [INFO] Inicializuji level {level_num}: {game_name}...")
            
            game_instance = game_creator()
            
            if game_instance is None:
                print(f"❌ [ERROR] Level {level_num} ({game_name}) vrátil None!")
                return None
            
            print(f"✅ [SUCCESS] Level {level_num} ({game_name}) úspěšně načten!")
            return game_instance
            
        except IndexError:
            print(f"❌ [ERROR] IndexError - Level {level_num} není v seznamu!")
            return None
        except TypeError as e:
            print(f"❌ [ERROR] TypeError v konstruktoru levelu {level_num}: {e}")
            import traceback
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"❌ [CRASH] Neznámá chyba při vytváření levelu {level_num}: {e}")
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
                for button in self.menu_buttons.values():
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
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.MENU:
                    self.handle_menu_click(mouse_pos)
                elif self.state == GameState.PATCH_NOTES:
                    self.handle_patch_click(mouse_pos)
                elif self.state == GameState.SETTINGS:
                    self.handle_settings_click(mouse_pos)
                elif self.state == GameState.PLAYING:
                    self.handle_play_click(mouse_pos)
                elif self.state == GameState.GAME:
                    if self.show_hint_popup:
                        self.show_hint_popup = False
                    elif self.pause_menu_open:
                        self.handle_pause_click(mouse_pos)
                    elif self.level_completed:
                        self.handle_popup_click(mouse_pos)
                    elif self.current_game:
                        self.current_game.handle_event(event)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    self.admin_mode = not self.admin_mode
                    if self.admin_mode:
                        self.unlocked_levels = 20
                    else:
                        self.unlocked_levels = 1
                if self.state == GameState.GAME:
                    if event.key == pygame.K_ESCAPE:
                        if not self.level_completed:
                            self.pause_menu_open = not self.pause_menu_open
                    elif event.key == pygame.K_SPACE:
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
        if self.state == GameState.GAME and not self.level_completed and self.current_game and not self.pause_menu_open:
            self.current_game.update()
            if self.current_game.is_won():
                self.level_completed = True
                self.game_won = True
                if self.current_level == self.unlocked_levels and self.unlocked_levels < 23:
                    self.unlocked_levels += 1
            elif self.current_game.is_lost():
                self.level_completed = True
                self.game_won = False
        
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
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PATCH_NOTES:
            self.draw_patch_notes()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.PLAYING:
            self.draw_play_menu()
        elif self.state == GameState.GAME:
            if self.current_game:
                self.current_game.draw(self.screen)
                
                level_text = FONT_SMALL.render(f"Level: {self.current_level}/20", True, WHITE)
                self.screen.blit(level_text, (self.screen_width - 200, 10))
                
                hint_text = FONT_TINY.render("Napoveda: 2x SPACE | ESC: Menu", True, YELLOW)
                self.screen.blit(hint_text, (10, 10))
                
                if self.show_hint_popup:
                    self.draw_hint_popup()
                
                if self.pause_menu_open:
                    self.draw_pause_menu()
                
                if self.level_completed:
                    self.draw_popup_menu()
        
        pygame.display.flip()
    
    def run(self):
        """Hlavní herní smyčka"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()


class BaseGame:
    """Základní třída pro všechny hry"""
    def __init__(self):
        self.won = False
        self.lost = False
        self.score = 0
    
    def handle_event(self, event):
        pass
    
    def update(self):
        pass
    
    def draw(self, screen):
        pass
    
    def is_won(self):
        return self.won
    
    def is_lost(self):
        return self.lost
    
    def get_hint(self):
        return "Zkus tlačítko!"

class Maze(BaseGame):
    """Grid-based maze - hráč se pohybuje po mřížce, 21x25 (lichá čísla pro DFS)"""
    def __init__(self):
        super().__init__()
        self.CELL_SIZE = 32
        self.COLS = 25
        self.ROWS = 21

        # Start and goal on odd-indexed DFS cells (guaranteed connected)
        self.player_row = 1
        self.player_col = 1
        self.goal_row = self.ROWS - 2   # 19
        self.goal_col = self.COLS - 2   # 23

        # Generate a guaranteed-solvable maze
        self.grid = self._generate_solvable_maze()

    # ------------------------------------------------------------------
    #  PUBLIC ENTRY POINT – regenerates until BFS confirms solvability
    # ------------------------------------------------------------------
    def _generate_solvable_maze(self):
        """
        Generates mazes until one passes the BFS reachability check.
        With a correct DFS carve this always succeeds on the first try,
        but the loop acts as a safety net.
        """
        for _ in range(100):
            maze = self._generate_maze_dfs()
            if self._bfs_path_exists(maze, self.player_row, self.player_col,
                                     self.goal_row, self.goal_col):
                return maze
        # Absolute fallback: open a straight corridor so the game is playable
        return self._fallback_maze()

    # ------------------------------------------------------------------
    #  ITERATIVE DFS  (Recursive-Backtracking, stack-based)
    # ------------------------------------------------------------------
    def _generate_maze_dfs(self):
        """
        Iterative DFS (recursive backtracking) maze generation.
        Works on odd-indexed cells (rooms).  Even-indexed cells between
        two rooms are carved to form passages.

        1 = path (walkable)   0 = wall
        """
        rows = self.ROWS
        cols = self.COLS

        # Start with every cell as a wall
        maze = [[0] * cols for _ in range(rows)]

        # Begin carving from the top-left room (1, 1)
        start_r, start_c = 1, 1
        maze[start_r][start_c] = 1
        stack = [(start_r, start_c)]

        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        while stack:
            r, c = stack[-1]

            # Collect unvisited neighbours (2 cells away, odd→odd)
            neighbours = []
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and maze[nr][nc] == 0:
                    neighbours.append((nr, nc, dr, dc))

            if neighbours:
                nr, nc, dr, dc = random.choice(neighbours)
                # Carve the wall cell between current room and neighbour room
                maze[r + dr // 2][c + dc // 2] = 1
                maze[nr][nc] = 1
                stack.append((nr, nc))
            else:
                stack.pop()

        return maze

    # ------------------------------------------------------------------
    #  BFS VERIFICATION
    # ------------------------------------------------------------------
    def _bfs_path_exists(self, maze, sr, sc, gr, gc):
        """Return True if a walkable path exists from (sr,sc) to (gr,gc)."""
        if maze[sr][sc] != 1 or maze[gr][gc] != 1:
            return False

        visited = set()
        queue = deque([(sr, sc)])
        visited.add((sr, sc))

        while queue:
            r, c = queue.popleft()
            if r == gr and c == gc:
                return True
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < self.ROWS and 0 <= nc < self.COLS
                        and (nr, nc) not in visited and maze[nr][nc] == 1):
                    visited.add((nr, nc))
                    queue.append((nr, nc))

        return False

    # ------------------------------------------------------------------
    #  FALLBACK – trivial solvable maze (should never be needed)
    # ------------------------------------------------------------------
    def _fallback_maze(self):
        """Create a simple maze with a guaranteed open corridor."""
        maze = [[0] * self.COLS for _ in range(self.ROWS)]
        # Open row 1 across the top, then column 23 down the right side
        for c in range(1, self.COLS - 1):
            maze[1][c] = 1
        for r in range(1, self.ROWS - 1):
            maze[r][self.COLS - 2] = 1
        return maze
    

    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            new_r, new_c = self.player_row, self.player_col

            if event.key in (pygame.K_UP, pygame.K_w):
                new_r -= 1
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                new_r += 1
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                new_c -= 1
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                new_c += 1

            # Move only if the target cell is inside the grid AND walkable
            if (0 <= new_r < self.ROWS and 0 <= new_c < self.COLS
                    and self.grid[new_r][new_c] == 1):
                self.player_row = new_r
                self.player_col = new_c

            # Win condition
            if self.player_row == self.goal_row and self.player_col == self.goal_col:
                self.won = True

    def draw(self, screen):
        screen.fill(DARK_BLUE)

        # Centre the grid on a 1920x1080 screen
        offset_x = (1920 - self.COLS * self.CELL_SIZE) // 2
        offset_y = (1080 - self.ROWS * self.CELL_SIZE) // 2

        # Draw grid
        for row in range(self.ROWS):
            for col in range(self.COLS):
                x = offset_x + col * self.CELL_SIZE
                y = offset_y + row * self.CELL_SIZE
                
                if self.grid[row][col] == 0:
                    # Wall – brown
                    pygame.draw.rect(screen, (139, 69, 19),
                                     pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE))
                else:
                    # Cesta - tmavě modrá
                    pygame.draw.rect(screen, (40, 40, 60), pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE))
                    pygame.draw.rect(screen, (60, 60, 90), pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE), 1)
        
        # Cíl - zelený
        goal_x = offset_x + self.goal_col * self.CELL_SIZE + 4
        goal_y = offset_y + self.goal_row * self.CELL_SIZE + 4
        pygame.draw.rect(screen, GREEN, pygame.Rect(goal_x, goal_y, self.CELL_SIZE - 8, self.CELL_SIZE - 8))
        
        # Start pozice - modrý čtverec v poli
        start_x = offset_x + 0 * self.CELL_SIZE + 4
        start_y = offset_y + 0 * self.CELL_SIZE + 4
        pygame.draw.rect(screen, BLUE, pygame.Rect(start_x, start_y, self.CELL_SIZE - 8, self.CELL_SIZE - 8))
        
        # Hráč - tyrkysový čtverec
        player_x = offset_x + self.player_col * self.CELL_SIZE + 4
        player_y = offset_y + self.player_row * self.CELL_SIZE + 4
        pygame.draw.rect(screen, CYAN, pygame.Rect(player_x, player_y, self.CELL_SIZE - 8, self.CELL_SIZE - 8))
        
        # Instrukce
        title = FONT_MEDIUM.render("BLUDIŠTĚ", True, YELLOW)
        screen.blit(title, (50, screen.get_height() - 150))
        
        instr = FONT_SMALL.render("ŠIPKY/WSAD = Pohyb | Dorazit na ZELENÝ CÍL", True, WHITE)
        screen.blit(instr, (50, screen.get_height() - 100))
    
    def get_hint(self):
        return "Hledej cestu na zelený čtverec vpravo dole!"

class SimonSays(BaseGame):
    def __init__(self):
        super().__init__()
        self.colors = [RED, YELLOW, GREEN, BLUE]
        self.sequence = [0]
        self.player_sequence = []
        self.current_step = 0
        self.waiting_for_input = False
        self.lights_on = [False] * 4
        self.light_timer = 0
        self.round = 1
        self.round_delay = 0
        self.sequence_delay = 0
        self.circle_radius = 75
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.waiting_for_input:
            pos = event.pos
            screen_w = SCREEN_WIDTH
            screen_h = SCREEN_HEIGHT
            circle_positions = [
                (screen_w//2 - 100, screen_h//2 - 100),
                (screen_w//2 + 100, screen_h//2 - 100),
                (screen_w//2 - 100, screen_h//2 + 100),
                (screen_w//2 + 100, screen_h//2 + 100),
            ]
            for i, (cx, cy) in enumerate(circle_positions):
                dist = ((pos[0] - cx)**2 + (pos[1] - cy)**2)**0.5
                if dist <= self.circle_radius:
                    self.player_sequence.append(i)
                    self.lights_on[i] = True
                    self.light_timer = 15
                    self.check_sequence()
                    break
    
    def update(self):
        self.light_timer = max(0, self.light_timer - 1)
        if self.light_timer == 0:
            self.lights_on = [False] * 4
        
        if self.round_delay > 0:
            self.round_delay -= 1
        elif self.sequence_delay > 0:
            self.sequence_delay -= 1
        elif not self.waiting_for_input and not self.won:
            self.play_sequence()
    
    def play_sequence(self):
        if self.current_step < len(self.sequence):
            self.lights_on[self.sequence[self.current_step]] = True
            # Zrychluj i délku osvětlení
            self.light_timer = max(15, 30 - (len(self.sequence) // 2))
            self.current_step += 1
            # Zrychluj delay mezi prvky - čím více prvků, tím rychlejší
            self.sequence_delay = max(10, 35 - (len(self.sequence) * 2))
        else:
            self.waiting_for_input = True
            self.player_sequence = []
    
    def check_sequence(self):
        # Porovnej poslední vstup hráče se sekvencí
        current_index = len(self.player_sequence) - 1
        
        # Pokud je vstup špatný, prohra
        if self.player_sequence[current_index] != self.sequence[current_index]:
            self.lost = True
            return
        
        # Pokud hráč dokončil sekvenci úspěšně
        if len(self.player_sequence) == len(self.sequence):
            if len(self.sequence) == 8:
                # Výhra - dosáhli jsme 8 kol
                self.won = True
            else:
                # Přidej další prvek sekvence a pokračuj
                self.sequence.append(random.randint(0, 3))
                self.waiting_for_input = False
                self.current_step = 0
                self.round += 1
                # Zrychluj sekvenci - čím vyšší kolo, tím rychlejší
                base_delay = max(15, 120 - (len(self.sequence) * 5))
                self.round_delay = base_delay
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        # Získej aktuální rozlišení
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        
        title = FONT_LARGE.render("SIMON SAYS", True, CYAN)
        screen.blit(title, (screen_w//2 - 150, 30))
        
        # Pozice koleček (dynamicky podle rozlišení)
        circle_positions = [
            (screen_w//2 - 100, screen_h//2 - 100),  # Levé horní
            (screen_w//2 + 100, screen_h//2 - 100),  # Pravé horní
            (screen_w//2 - 100, screen_h//2 + 100),  # Levé dolní
            (screen_w//2 + 100, screen_h//2 + 100),  # Pravé dolní
        ]
        
        # Nakresli 4 barevná kolečka
        for i in range(4):
            cx, cy = circle_positions[i]
            color = self.colors[i] if not self.lights_on[i] else (255, 255, 255)
            pygame.draw.circle(screen, color, (cx, cy), self.circle_radius)
            # Přidej outline pro lepší viditelnost
            pygame.draw.circle(screen, WHITE, (cx, cy), self.circle_radius, 3)
        
        # Info s pokrokem
        info = FONT_MEDIUM.render(f"Kolo: {self.round}/8 | Délka: {len(self.sequence)}", True, YELLOW)
        screen.blit(info, (screen_w//2 - 250, 550))
        
        # Zobraz pokrok v sekvenci
        progress = FONT_SMALL.render(f"Tvá řada: {len(self.player_sequence)}/{len(self.sequence)}", True, CYAN)
        screen.blit(progress, (screen_w//2 - 200, 600))
        
        if self.waiting_for_input:
            instr = FONT_SMALL.render("Tvůj tah! Klikej na světla", True, GREEN)
        else:
            instr = FONT_SMALL.render("Sleduj sekvenci...", True, WHITE)
        screen.blit(instr, (screen_w//2 - 200, 650))
        
        if self.lost:
            lose = FONT_LARGE.render("ŠPATNĚ!", True, RED)
            screen.blit(lose, (screen_w//2 - 150, 700))
    
    def get_hint(self):
        return "Zapamatuj si pořadí barev!"

class ClickMaster(BaseGame):
    """Klikej na pohybující se cíl - reflex a přesnost"""
    def __init__(self):
        super().__init__()
        self.target_x = SCREEN_WIDTH // 2
        self.target_y = SCREEN_HEIGHT // 2
        self.target_radius = 30
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(-3, 3)
        self.clicks = 0
        self.timer = 0
        self.max_time = 600  # 10 sekund
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            dist = ((pos[0] - self.target_x) ** 2 + (pos[1] - self.target_y) ** 2) ** 0.5
            if dist <= self.target_radius:
                self.clicks += 1
                if self.clicks >= 10:
                    self.won = True
    
    def update(self):
        self.timer += 1
        
        # Pohyb cíle
        self.target_x += self.vel_x
        self.target_y += self.vel_y
        
        # Odskoky od stěn
        if self.target_x - self.target_radius < 0 or self.target_x + self.target_radius > SCREEN_WIDTH:
            self.vel_x *= -1
            self.target_x = max(self.target_radius, min(SCREEN_WIDTH - self.target_radius, self.target_x))
        if self.target_y - self.target_radius < 0 or self.target_y + self.target_radius > SCREEN_HEIGHT - 100:
            self.vel_y *= -1
            self.target_y = max(self.target_radius, min(SCREEN_HEIGHT - 100 - self.target_radius, self.target_y))
        
        # Čas vypršel
        if self.timer >= self.max_time:
            if self.clicks >= 10:
                self.won = True
            else:
                self.lost = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("KLIKEJ NA CÍL", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH // 2 - 200, 30))
        
        # Cíl - červený kruh
        pygame.draw.circle(screen, RED, (int(self.target_x), int(self.target_y)), self.target_radius)
        pygame.draw.circle(screen, YELLOW, (int(self.target_x), int(self.target_y)), self.target_radius, 3)
        
        # Počítadlo
        counter = FONT_MEDIUM.render(f"Kliknutí: {self.clicks}/10", True, YELLOW)
        screen.blit(counter, (SCREEN_WIDTH // 2 - 150, 750))
        
        # Čas
        time_left = max(0, (self.max_time - self.timer) // 60)
        time_text = FONT_SMALL.render(f"Čas: {time_left}s", True, GREEN)
        screen.blit(time_text, (SCREEN_WIDTH // 2 - 50, 820))
        
        instr = FONT_TINY.render("Klikej na pohybující se terč - musíš 10x!", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH // 2 - 200, 650))
    
    def get_hint(self):
        return "Klikej přesně na červený kruh!"

class TetrisLite(BaseGame):
    """Lehký Tetris s rotací"""
    
    COLS = 10
    ROWS = 20
    CELL = 30
    FALL_INTERVAL = 30
    LOCK_DELAY = 30
    LINES_TO_WIN = 3
    
    SHAPES = {
        "I": [
            [(0, 0), (1, 0), (2, 0), (3, 0)],
            [(0, 0), (0, 1), (0, 2), (0, 3)],
        ],
        "O": [
            [(0, 0), (1, 0), (0, 1), (1, 1)],
        ],
        "T": [
            [(0, 0), (1, 0), (2, 0), (1, 1)],
            [(0, 0), (0, 1), (0, 2), (1, 1)],
            [(1, 0), (0, 1), (1, 1), (2, 1)],
            [(1, 0), (1, 1), (1, 2), (0, 1)],
        ],
        "S": [
            [(1, 0), (2, 0), (0, 1), (1, 1)],
            [(0, 0), (0, 1), (1, 1), (1, 2)],
        ],
        "Z": [
            [(0, 0), (1, 0), (1, 1), (2, 1)],
            [(1, 0), (0, 1), (1, 1), (0, 2)],
        ],
        "L": [
            [(0, 0), (0, 1), (0, 2), (1, 2)],
            [(0, 0), (1, 0), (2, 0), (0, 1)],
            [(0, 0), (1, 0), (1, 1), (1, 2)],
            [(2, 0), (0, 1), (1, 1), (2, 1)],
        ],
        "J": [
            [(1, 0), (1, 1), (0, 2), (1, 2)],
            [(0, 0), (0, 1), (1, 1), (2, 1)],
            [(0, 0), (1, 0), (0, 1), (0, 2)],
            [(0, 0), (1, 0), (2, 0), (2, 1)],
        ],
    }
    
    SHAPE_COLORS = {
        "I": (0, 255, 255),
        "O": (255, 255, 0),
        "T": (128, 0, 128),
        "S": (0, 255, 0),
        "Z": (255, 0, 0),
        "L": (255, 165, 0),
        "J": (0, 0, 255),
    }
    
    class _Piece:
        def __init__(self, name, shapes):
            self.name = name
            self.shapes = shapes
            self.rot = 0
            self.x = 3
            self.y = 0
        
        @property
        def cells(self):
            return list(self.shapes[self.name][self.rot])
        
        def rotated_cells(self, direction=1):
            new_rot = (self.rot + direction) % len(self.shapes[self.name])
            return list(self.shapes[self.name][new_rot]), new_rot
    
    def __init__(self):
        super().__init__()
        # Grid: 0 = empty, else colour tuple
        self.grid = [[0] * self.COLS for _ in range(self.ROWS)]
        self.bag = []
        self.piece = self._spawn_piece()
        self.next_piece_name = self._next_from_bag()
        self.hold_name = None
        self.hold_used = False          # only one hold per piece drop
        self.lines_cleared = 0
        self.score = 0
        self.fall_timer = 0
        self.lock_timer = 0
        self.paused = False
        self.started = False            # press-any-key gate
        self.game_over = False

    # ---- bag randomiser ---------------------------------------------------
    def _next_from_bag(self):
        if not self.bag:
            self.bag = list(self.SHAPES.keys())
            random.shuffle(self.bag)
        return self.bag.pop()

    def _spawn_piece(self):
        name = self._next_from_bag()
        return self._Piece(name, self.SHAPES)

    # ---- collision / placement --------------------------------------------
    def _valid(self, cells, ox, oy):
        for cx, cy in cells:
            gx, gy = ox + cx, oy + cy
            if gx < 0 or gx >= self.COLS or gy >= self.ROWS:
                return False
            if gy >= 0 and self.grid[gy][gx]:
                return False
        return True

    def _lock_piece(self):
        color = self.SHAPE_COLORS[self.piece.name]
        for cx, cy in self.piece.cells:
            gx, gy = self.piece.x + cx, self.piece.y + cy
            if 0 <= gy < self.ROWS and 0 <= gx < self.COLS:
                self.grid[gy][gx] = color
        self._clear_lines()
        self._next_turn()

    def _next_turn(self):
        self.piece = self._Piece(self.next_piece_name, self.SHAPES)
        self.next_piece_name = self._next_from_bag()
        self.hold_used = False
        self.lock_timer = 0
        self.fall_timer = 0
        if not self._valid(self.piece.cells, self.piece.x, self.piece.y):
            self.game_over = True
            self.lost = True

    def _clear_lines(self):
        new_grid = []
        cleared = 0
        for row in self.grid:
            if all(cell != 0 for cell in row):
                cleared += 1
            else:
                new_grid.append(row)
        for _ in range(cleared):
            new_grid.insert(0, [0] * self.COLS)
        self.grid = new_grid
        self.lines_cleared += cleared
        self.score += [0, 100, 300, 500, 800][min(cleared, 4)]
        if self.lines_cleared >= self.LINES_TO_WIN:
            self.won = True

    # ---- movement helpers -------------------------------------------------
    def _move(self, dx, dy):
        if self._valid(self.piece.cells, self.piece.x + dx, self.piece.y + dy):
            self.piece.x += dx
            self.piece.y += dy
            if dy == 0:
                self.lock_timer = 0      # reset lock timer on horizontal move
            return True
        return False

    def _rotate(self, direction=1):
        new_cells, new_rot = self.piece.rotated_cells(direction)
        # Try basic rotation then simple wall kicks
        kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1), (0, -2)]
        for kx, ky in kicks:
            if self._valid(new_cells, self.piece.x + kx, self.piece.y + ky):
                self.piece.x += kx
                self.piece.y += ky
                self.piece.rot = new_rot
                self.lock_timer = 0
                return True
        return False

    def _hold(self):
        if self.hold_used:
            return
        self.hold_used = True
        if self.hold_name is None:
            self.hold_name = self.piece.name
            self.piece = self._Piece(self.next_piece_name, self.SHAPES)
            self.next_piece_name = self._next_from_bag()
        else:
            old_hold = self.hold_name
            self.hold_name = self.piece.name
            self.piece = self._Piece(old_hold, self.SHAPES)
        self.lock_timer = 0
        self.fall_timer = 0

    def _ghost_y(self):
        gy = self.piece.y
        while self._valid(self.piece.cells, self.piece.x, gy + 1):
            gy += 1
        return gy

    # ---- event handling ---------------------------------------------------
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # Start gate
        if not self.started:
            self.started = True
            return

        if self.won or self.game_over:
            return

        # Pause toggle
        if event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
            return

        if self.paused:
            return

        # Movement (Arrow keys AND WASD)
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self._move(-1, 0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self._move(1, 0)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            if self._move(0, 1):
                self.fall_timer = 0
        # Rotation on R only
        elif event.key == pygame.K_r:
            self._rotate()
        # Hold
        elif event.key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT):
            self._hold()

    # ---- update (auto-fall) -----------------------------------------------
    def update(self):
        if not self.started or self.paused or self.won or self.game_over:
            return

        self.fall_timer += 1
        if self.fall_timer >= self.FALL_INTERVAL:
            self.fall_timer = 0
            if not self._move(0, 1):
                self.lock_timer += 1
                if self.lock_timer >= self.LOCK_DELAY:
                    self._lock_piece()
            else:
                self.lock_timer = 0
        else:
            # Check if piece is resting on something and count lock delay
            if not self._valid(self.piece.cells, self.piece.x, self.piece.y + 1):
                self.lock_timer += 1
                if self.lock_timer >= self.LOCK_DELAY:
                    self._lock_piece()

    # ---- drawing ----------------------------------------------------------
    def _draw_block(self, screen, x, y, color, size=None):
        s = size or self.CELL
        rect = pygame.Rect(x, y, s, s)
        pygame.draw.rect(screen, color, rect)
        # highlight
        pygame.draw.line(screen, tuple(min(c + 40, 255) for c in color), (x, y), (x + s - 1, y))
        pygame.draw.line(screen, tuple(min(c + 40, 255) for c in color), (x, y), (x, y + s - 1))
        # shadow
        pygame.draw.line(screen, tuple(max(c - 60, 0) for c in color), (x, y + s - 1), (x + s - 1, y + s - 1))
        pygame.draw.line(screen, tuple(max(c - 60, 0) for c in color), (x + s - 1, y), (x + s - 1, y + s - 1))

    def _draw_mini_piece(self, screen, name, cx, cy, cell=20):
        if name is None:
            return
        color = self.SHAPE_COLORS[name]
        cells = self.SHAPES[name][0]
        for bx, by in cells:
            self._draw_block(screen, cx + bx * cell, cy + by * cell, color, cell)

    def draw(self, screen):
        screen.fill((15, 15, 30))

        # ---- start screen ----
        if not self.started:
            t = FONT_LARGE.render("TETRIS", True, CYAN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 300))
            p = FONT_MEDIUM.render("Press any key to start", True, WHITE)
            screen.blit(p, (SCREEN_WIDTH // 2 - p.get_width() // 2, 450))
            return

        # Layout constants
        grid_w = self.COLS * self.CELL
        grid_h = self.ROWS * self.CELL
        ox = (SCREEN_WIDTH - grid_w) // 2
        oy = (SCREEN_HEIGHT - grid_h) // 2

        # ---- grid background ----
        pygame.draw.rect(screen, (30, 30, 50), (ox - 2, oy - 2, grid_w + 4, grid_h + 4))
        for r in range(self.ROWS):
            for c in range(self.COLS):
                rect = pygame.Rect(ox + c * self.CELL, oy + r * self.CELL, self.CELL, self.CELL)
                if self.grid[r][c]:
                    self._draw_block(screen, rect.x, rect.y, self.grid[r][c])
                else:
                    pygame.draw.rect(screen, (40, 40, 60), rect)
                    pygame.draw.rect(screen, (55, 55, 75), rect, 1)

        # ---- ghost piece ----
        if not self.won and not self.game_over:
            gy = self._ghost_y()
            ghost_color = tuple(c // 3 for c in self.SHAPE_COLORS[self.piece.name])
            for cx, cy in self.piece.cells:
                gx_p = ox + (self.piece.x + cx) * self.CELL
                gy_p = oy + (gy + cy) * self.CELL
                pygame.draw.rect(screen, ghost_color, (gx_p, gy_p, self.CELL, self.CELL))
                pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in ghost_color),
                                 (gx_p, gy_p, self.CELL, self.CELL), 1)

        # ---- current piece ----
        if not self.won and not self.game_over:
            pc = self.SHAPE_COLORS[self.piece.name]
            for cx, cy in self.piece.cells:
                px = ox + (self.piece.x + cx) * self.CELL
                py = oy + (self.piece.y + cy) * self.CELL
                if py >= oy:
                    self._draw_block(screen, px, py, pc)

        # ---- grid border ----
        pygame.draw.rect(screen, CYAN, (ox - 2, oy - 2, grid_w + 4, grid_h + 4), 2)

        # ---- right panel: Next / Hold / Score / Lines ----
        panel_x = ox + grid_w + 30

        # Next piece
        lbl = FONT_SMALL.render("NEXT", True, CYAN)
        screen.blit(lbl, (panel_x, oy))
        pygame.draw.rect(screen, (40, 40, 60), (panel_x, oy + 30, 100, 80))
        pygame.draw.rect(screen, CYAN, (panel_x, oy + 30, 100, 80), 1)
        self._draw_mini_piece(screen, self.next_piece_name, panel_x + 10, oy + 40)

        # Hold piece
        lbl = FONT_SMALL.render("HOLD", True, CYAN)
        screen.blit(lbl, (panel_x, oy + 130))
        pygame.draw.rect(screen, (40, 40, 60), (panel_x, oy + 160, 100, 80))
        pygame.draw.rect(screen, CYAN, (panel_x, oy + 160, 100, 80), 1)
        self._draw_mini_piece(screen, self.hold_name, panel_x + 10, oy + 170)

        # Score
        lbl = FONT_SMALL.render("SCORE", True, CYAN)
        screen.blit(lbl, (panel_x, oy + 270))
        val = FONT_MEDIUM.render(str(self.score), True, YELLOW)
        screen.blit(val, (panel_x, oy + 300))

        # Lines progress
        lbl = FONT_SMALL.render("LINES", True, CYAN)
        screen.blit(lbl, (panel_x, oy + 370))
        val = FONT_MEDIUM.render(f"{self.lines_cleared} / {self.LINES_TO_WIN}", True, YELLOW)
        screen.blit(val, (panel_x, oy + 400))

        # ---- left panel: Controls ----
        ctrl_x = ox - 260
        ctrl_y = oy
        lbl = FONT_SMALL.render("CONTROLS", True, CYAN)
        screen.blit(lbl, (ctrl_x, ctrl_y))
        controls = [
            "A / Left  = Move Left",
            "D / Right = Move Right",
            "S / Down  = Soft Drop",
            "R         = Rotate",
            "C / Shift = Hold",
            "ESC       = Pause",
        ]
        for i, line in enumerate(controls):
            t = FONT_TINY.render(line, True, LIGHT_GRAY)
            screen.blit(t, (ctrl_x, ctrl_y + 35 + i * 28))

        # ---- overlays ----
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            t = FONT_LARGE.render("PAUSED", True, YELLOW)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            s = FONT_SMALL.render("Press ESC to resume", True, WHITE)
            screen.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        if self.won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            t = FONT_LARGE.render("YOU WIN!", True, GREEN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            s = FONT_SMALL.render(f"Lines: {self.lines_cleared}  Score: {self.score}", True, WHITE)
            screen.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        if self.game_over and not self.won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            t = FONT_LARGE.render("GAME OVER", True, RED)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            s = FONT_SMALL.render(f"Lines: {self.lines_cleared}  Score: {self.score}", True, WHITE)
            screen.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

    def get_hint(self):
        return "Vymaž 3 řady! Použij R pro rotaci, C/Shift pro hold."

class Game2048(BaseGame):
    """Pong – 1 hráč vs AI, first to 3 goals wins."""

    # --- constants (relative to the play area) ---
    AREA_W = 700
    AREA_H = 500
    PADDLE_W = 12
    PADDLE_H = 90
    PADDLE_SPD = 6
    AI_SPD = 3.5            # slightly slower than ball – beatable but not free
    BALL_SZ = 12
    BALL_DX = 5
    BALL_DY = 4
    GOALS_TO_WIN = 1

    def __init__(self):
        super().__init__()
        self.started = False
        self.paused = False
        # 3-second countdown (180 frames at 60 FPS)
        self.countdown = 180
        self.countdown_active = False
        # origin of play area (centred on 1920x1080)
        self.ox = (SCREEN_WIDTH - self.AREA_W) // 2
        self.oy = (SCREEN_HEIGHT - self.AREA_H) // 2
        self.player_score = 0
        self.ai_score = 0
        self._reset_paddles()
        self._reset_ball()

    def _reset_paddles(self):
        self.player_pad = pygame.Rect(
            self.ox + 20,
            self.oy + self.AREA_H // 2 - self.PADDLE_H // 2,
            self.PADDLE_W, self.PADDLE_H)
        self.ai_pad = pygame.Rect(
            self.ox + self.AREA_W - 20 - self.PADDLE_W,
            self.oy + self.AREA_H // 2 - self.PADDLE_H // 2,
            self.PADDLE_W, self.PADDLE_H)

    def _reset_ball(self):
        dx = random.choice([-1, 1])
        dy = random.choice([-1, 1])
        self.ball = pygame.Rect(
            self.ox + self.AREA_W // 2 - self.BALL_SZ // 2,
            self.oy + self.AREA_H // 2 - self.BALL_SZ // 2,
            self.BALL_SZ, self.BALL_SZ)
        self.bdx = self.BALL_DX * dx
        self.bdy = self.BALL_DY * dy
        self.goal_pause = 0          # frames to freeze after a goal

    # ----- event handling --------------------------------------------------
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if not self.started:
            self.started = True
            self.countdown_active = True
            return
        if self.countdown_active:
            return  # ignore input during countdown
        if event.key == pygame.K_ESCAPE:
            self.paused = not self.paused

    # ----- update (called every frame) -------------------------------------
    def update(self):
        if not self.started or self.paused or self.won or self.lost:
            return

        # --- 3-second countdown ---
        if self.countdown_active:
            self.countdown -= 1
            if self.countdown <= 0:
                self.countdown_active = False
            return

        # goal-pause countdown
        if self.goal_pause > 0:
            self.goal_pause -= 1
            return

        # --- player paddle (continuous key reading) ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player_pad.y -= self.PADDLE_SPD
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player_pad.y += self.PADDLE_SPD
        self.player_pad.clamp_ip(pygame.Rect(self.ox, self.oy, self.AREA_W, self.AREA_H))

        # --- AI paddle (beatable but not trivial) ---
        diff = self.ball.centery - self.ai_pad.centery
        # 12% chance AI freezes this frame
        if random.random() < 0.12:
            pass
        elif abs(diff) > 18:
            self.ai_pad.y += self.AI_SPD if diff > 0 else -self.AI_SPD
        self.ai_pad.clamp_ip(pygame.Rect(self.ox, self.oy, self.AREA_W, self.AREA_H))

        # --- move ball ---
        self.ball.x += self.bdx
        self.ball.y += self.bdy

        # bounce top/bottom
        if self.ball.top <= self.oy:
            self.ball.top = self.oy
            self.bdy = abs(self.bdy)
        elif self.ball.bottom >= self.oy + self.AREA_H:
            self.ball.bottom = self.oy + self.AREA_H
            self.bdy = -abs(self.bdy)

        # bounce off paddles
        if self.ball.colliderect(self.player_pad) and self.bdx < 0:
            self.bdx = abs(self.bdx)
            self.bdy += random.uniform(-1.5, 1.5)
            self.ball.left = self.player_pad.right
        elif self.ball.colliderect(self.ai_pad) and self.bdx > 0:
            self.bdx = -abs(self.bdx)
            self.bdy += random.uniform(-1.5, 1.5)
            self.ball.right = self.ai_pad.left

        # --- scoring ---
        if self.ball.right <= self.ox:
            self.ai_score += 1
            self._reset_ball()
            self.goal_pause = 40
        elif self.ball.left >= self.ox + self.AREA_W:
            self.player_score += 1
            self._reset_ball()
            self.goal_pause = 40

        # win / lose
        if self.player_score >= self.GOALS_TO_WIN:
            self.won = True
        elif self.ai_score >= self.GOALS_TO_WIN:
            self.lost = True

    # ----- drawing ---------------------------------------------------------
    def draw(self, screen):
        screen.fill((15, 15, 30))

        ox, oy, aw, ah = self.ox, self.oy, self.AREA_W, self.AREA_H

        # --- start screen ---
        if not self.started:
            t = FONT_LARGE.render("PONG", True, CYAN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 350))
            s = FONT_SMALL.render("W/S nebo šipky = pohyb | Stiskni cokoliv", True, WHITE)
            screen.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, 460))
            return

        # --- countdown overlay ---
        if self.countdown_active:
            # draw the field behind the countdown
            pygame.draw.rect(screen, (25, 25, 45), (ox, oy, aw, ah))
            pygame.draw.rect(screen, CYAN, (ox, oy, aw, ah), 2)
            secs = self.countdown // 60 + 1   # 3, 2, 1
            num = FONT_LARGE.render(str(min(secs, 3)), True, YELLOW)
            screen.blit(num, (SCREEN_WIDTH // 2 - num.get_width() // 2,
                              SCREEN_HEIGHT // 2 - num.get_height() // 2))
            return

        # area background + border
        pygame.draw.rect(screen, (25, 25, 45), (ox, oy, aw, ah))
        pygame.draw.rect(screen, CYAN, (ox, oy, aw, ah), 2)

        # centre dashed line
        for y in range(oy, oy + ah, 20):
            pygame.draw.rect(screen, GRAY, (ox + aw // 2 - 1, y, 2, 10))

        # paddles
        pygame.draw.rect(screen, CYAN, self.player_pad)
        pygame.draw.rect(screen, YELLOW, self.ai_pad)

        # ball
        pygame.draw.ellipse(screen, WHITE, self.ball)

        # scores
        pt = FONT_LARGE.render(str(self.player_score), True, CYAN)
        at = FONT_LARGE.render(str(self.ai_score), True, YELLOW)
        screen.blit(pt, (ox + aw // 4 - pt.get_width() // 2, oy - 70))
        screen.blit(at, (ox + 3 * aw // 4 - at.get_width() // 2, oy - 70))

        # labels
        pl = FONT_TINY.render("TY", True, CYAN)
        al = FONT_TINY.render("AI", True, YELLOW)
        screen.blit(pl, (ox + aw // 4 - pl.get_width() // 2, oy - 90))
        screen.blit(al, (ox + 3 * aw // 4 - al.get_width() // 2, oy - 90))

        # info line
        info = FONT_TINY.render(f"Kdo dá {self.GOALS_TO_WIN} góly, vyhrává!", True, LIGHT_GRAY)
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, oy + ah + 15))

        # overlays
        if self.paused:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render("PAUZA", True, YELLOW)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))

        if self.won:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render("VYHRÁL JSI!", True, GREEN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))

        if self.lost:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render("AI VYHRÁLA!", True, RED)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))

    def get_hint(self):
        return "W/S nebo šipky nahoru/dolů – odráží míček!"

class BalanceGame(BaseGame):
    """Hra s váhou - vyvážit předměty"""
    def __init__(self):
        super().__init__()
        self.items = [
            {"name": "ZLATÁ MISKA", "weight": 3},
            {"name": "STŘÍBRNÁ MISKA", "weight": 2},
            {"name": "STEN", "weight": 5},
            {"name": "CIHLA", "weight": 4},
            {"name": "KLÍČ", "weight": 1}
        ]
        self.left_side = []
        self.right_side = []
        self.total_weight = sum(item["weight"] for item in self.items)
        self.target_weight = self.total_weight // 2
        self.available_items = self.items.copy()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1 and self.available_items:
                self.left_side.append(self.available_items.pop(0))
            elif event.key == pygame.K_2 and self.available_items:
                self.right_side.append(self.available_items.pop(0))
            
            left_weight = sum(item["weight"] for item in self.left_side)
            right_weight = sum(item["weight"] for item in self.right_side)
            
            if left_weight == right_weight and left_weight == self.target_weight:
                self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("VYVAŽOVACÍ HRA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 180, 30))
        
        pygame.draw.circle(screen, YELLOW, (SCREEN_WIDTH//2, 250), 30)
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH//2 - 250, 250), (SCREEN_WIDTH//2 + 250, 250), 3)
        pygame.draw.rect(screen, BLUE, pygame.Rect(SCREEN_WIDTH//2 - 250, 200, 200, 80))
        pygame.draw.rect(screen, BLUE, pygame.Rect(SCREEN_WIDTH//2 + 50, 200, 200, 80))
        
        left_weight = sum(item["weight"] for item in self.left_side)
        right_weight = sum(item["weight"] for item in self.right_side)
        
        left_text = FONT_MEDIUM.render(f"VLEVO: {left_weight}", True, WHITE)
        right_text = FONT_MEDIUM.render(f"VPRAVO: {right_weight}", True, WHITE)
        screen.blit(left_text, (SCREEN_WIDTH//2 - 240, 210))
        screen.blit(right_text, (SCREEN_WIDTH//2 + 60, 210))
        
        y = 350
        avail_text = FONT_SMALL.render("DOSTUPNÉ PŘEDMĚTY:", True, CYAN)
        screen.blit(avail_text, (50, y))
        y += 50
        
        for i, item in enumerate(self.available_items):
            text = FONT_SMALL.render(f"{i+1}: {item['name']} ({item['weight']}kg)", True, WHITE)
            screen.blit(text, (70, y))
            y += 40
        
        instr = FONT_SMALL.render("Stiskem 1 nebo 2 přidej předmět", True, YELLOW)
        screen.blit(instr, (SCREEN_WIDTH//2 - 180, 700))
    
    def get_hint(self):
        target = self.total_weight // 2
        return f"Vyváž obě strany na {target}kg"

class RiddleGame(BaseGame):
    """Lehké hádanky"""
    def __init__(self):
        super().__init__()
        self.riddles = [
            {"q": "Co má ruku, ale nemůže psát?", "a": "HODINY"},
            {"q": "Čím více vezmeš, tím víc ti zbyde. Co to je?", "a": "STOPY"},
            {"q": "Co jde, ale nikdy nechodí?", "a": "VODA"},
        ]
        self.current_riddle = random.choice(self.riddles)
        self.answer = ""
        self.input_active = True
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.answer = self.answer[:-1]
            elif event.key == pygame.K_RETURN:
                if self.answer.upper() == self.current_riddle["a"]:
                    self.won = True
                else:
                    self.lost = True
            elif event.unicode.isalpha():
                self.answer += event.unicode.upper()
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("HÁDANKA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 130, 50))
        
        question = FONT_MEDIUM.render(self.current_riddle["q"], True, YELLOW)
        question_rect = question.get_rect(center=(SCREEN_WIDTH//2, 200))
        screen.blit(question, question_rect)
        
        answer_text = FONT_MEDIUM.render(self.answer + "_", True, WHITE)
        answer_rect = answer_text.get_rect(center=(SCREEN_WIDTH//2, 400))
        pygame.draw.rect(screen, BLUE, pygame.Rect(answer_rect.x - 20, answer_rect.y - 20, answer_rect.width + 40, answer_rect.height + 40))
        screen.blit(answer_text, answer_rect)
        
        instr = FONT_SMALL.render("Napiš odpověď a zmáčkni ENTER", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 220, 600))
    
    def get_hint(self):
        return f"Nápověda: {self.current_riddle['a'][0]}..."

class SudokuLite(BaseGame):
    """Lehké sudoku 4x4"""
    def __init__(self):
        super().__init__()
        self.grid = [
            [0, 0, 1, 2],
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 1, 0, 0]
        ]
        self.solution = [
            [3, 4, 1, 2],
            [1, 2, 4, 3],
            [2, 3, 4, 1],
            [4, 1, 3, 2]
        ]
        self.player_grid = [row.copy() for row in self.grid]
        self.selected = None
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i in range(4):
                for j in range(4):
                    x = 300 + j * 100
                    y = 200 + i * 100
                    if pygame.Rect(x, y, 100, 100).collidepoint(pos):
                        if self.grid[i][j] == 0:
                            self.selected = (i, j)
        
        elif event.type == pygame.KEYDOWN and self.selected:
            i, j = self.selected
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                value = int(event.unicode)
                if self.is_valid_move(i, j, value):
                    self.player_grid[i][j] = value
                    if self.check_win():
                        self.won = True
            elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                self.player_grid[i][j] = 0
    
    def check_win(self):
        return self.player_grid == self.solution
    
    def is_valid_move(self, row, col, value):
        """Kontrola Sudoku pravidel: řádek, sloupec, blok"""
        # Kontrola řádku
        if value in self.player_grid[row]:
            return False
        
        # Kontrola sloupce
        for i in range(4):
            if self.player_grid[i][col] == value:
                return False
        
        # Kontrola bloku 2x2
        block_row = (row // 2) * 2
        block_col = (col // 2) * 2
        for i in range(block_row, block_row + 2):
            for j in range(block_col, block_col + 2):
                if self.player_grid[i][j] == value:
                    return False
        
        return True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("SUDOKU 4x4", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 130, 30))
        
        for i in range(4):
            for j in range(4):
                x = 300 + j * 100
                y = 200 + i * 100
                color = GRAY if self.grid[i][j] == 0 else DARK_GRAY
                pygame.draw.rect(screen, color, pygame.Rect(x, y, 100, 100))
                pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 100, 100), 2)
                
                if self.selected == (i, j):
                    pygame.draw.rect(screen, YELLOW, pygame.Rect(x, y, 100, 100), 5)
                
                value = self.player_grid[i][j]
                if value > 0:
                    value_text = FONT_LARGE.render(str(value), True, CYAN if self.grid[i][j] == 0 else WHITE)
                    value_rect = value_text.get_rect(center=(x + 50, y + 50))
                    screen.blit(value_text, value_rect)
        
        instr = FONT_SMALL.render("Klikni na pole a napiš čísla 1-4", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 220, 650))
    
    def get_hint(self):
        return "Každé číslo se smí vyskytovat jen jednou! Vyplň všechna prázdná pole."
    
    def update(self):
        pass

class CaesarCipher(BaseGame):
    """Rychlá matematika - soutěž s časem"""
    def __init__(self):
        super().__init__()
        self.operations = ["+", "-", "*"]
        self.correct_answers = 0
        self.total_problems = 5
        self.current_problem = self.generate_problem()
        self.answer = ""
        self.time_limit = 120
        self.start_time = pygame.time.get_ticks() // 1000
    
    def generate_problem(self):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(self.operations)
        
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        else:
            result = a * b
        
        return {"a": a, "b": b, "op": op, "result": result, "display": f"{a} {op} {b}"}
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.answer = self.answer[:-1]
            elif event.key == pygame.K_RETURN:
                try:
                    if int(self.answer) == self.current_problem["result"]:
                        self.correct_answers += 1
                        if self.correct_answers >= self.total_problems:
                            self.won = True
                        else:
                            self.current_problem = self.generate_problem()
                            self.answer = ""
                except:
                    pass
                self.answer = ""
            elif event.unicode.isdigit() or (event.unicode == "-" and len(self.answer) == 0):
                self.answer += event.unicode
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("RYCHLÁ MATEMATIKA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 240, 30))
        
        progress = FONT_MEDIUM.render(f"SPRÁVNĚ: {self.correct_answers}/{self.total_problems}", True, YELLOW)
        screen.blit(progress, (SCREEN_WIDTH//2 - 180, 120))
        
        problem = FONT_LARGE.render(self.current_problem["display"], True, WHITE)
        problem_rect = problem.get_rect(center=(SCREEN_WIDTH//2, 250))
        screen.blit(problem, problem_rect)
        
        answer_text = FONT_LARGE.render(self.answer + "_", True, CYAN)
        answer_rect = answer_text.get_rect(center=(SCREEN_WIDTH//2, 400))
        pygame.draw.rect(screen, BLUE, pygame.Rect(answer_rect.x - 50, answer_rect.y - 30, answer_rect.width + 100, answer_rect.height + 60))
        pygame.draw.rect(screen, CYAN, pygame.Rect(answer_rect.x - 50, answer_rect.y - 30, answer_rect.width + 100, answer_rect.height + 60), 3)
        screen.blit(answer_text, answer_rect)
        
        instr = FONT_SMALL.render("Napiš výsledek a stiskni ENTER", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 250, 600))
    
    def get_hint(self):
        return f"Odpověď: {self.current_problem['result']}"

class SwitchGame(BaseGame):
    """Logická hra s přepínači"""
    def __init__(self):
        super().__init__()
        self.num_switches = random.randint(3, 5)
        self.state = [False] * self.num_switches
        self.goal = [True] * self.num_switches
        
        # Generuj náhodnou počáteční konfiguraci
        for _ in range(random.randint(1, 3)):
            switch_to_press = random.randint(0, self.num_switches - 1)
            self.press_switch(switch_to_press)
    
    def press_switch(self, index):
        """Změní stav přepínačů"""
        for i in range(self.num_switches):
            if i == index or abs(i - index) == 1:
                self.state[i] = not self.state[i]
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i in range(self.num_switches):
                x = 300 + i * 150
                y = 350
                if pygame.Rect(x - 40, y - 40, 80, 80).collidepoint(pos):
                    self.press_switch(i)
                    if self.state == self.goal:
                        self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("PŘEPÍNAČE", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 120, 50))
        
        # Cíl
        goal_text = FONT_SMALL.render("CÍL: Rozsvítit všechna světla", True, GREEN)
        screen.blit(goal_text, (SCREEN_WIDTH//2 - 180, 150))
        
        # Přepínače
        for i in range(self.num_switches):
            x = 300 + i * 150
            y = 350
            color = GREEN if self.state[i] else RED
            pygame.draw.circle(screen, color, (x, y), 40)
            pygame.draw.circle(screen, WHITE, (x, y), 40, 3)
        
        instr = FONT_SMALL.render("Klikni na přepínač - změní stav jeho sousedů!", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 280, 600))
    
    def get_hint(self):
        return "Každé kliknutí změní stav sousedů!"

class WordUnscrambler(BaseGame):
    """Zamíchané slovo - psaní textu + klikání na písmena"""
    def __init__(self):
        super().__init__()
        self.word_pairs = [
            ("AHOJ", "HOJA"),
            ("HLAVA", "VAHLA"),
            ("PSANÍ", "NASÍP"),
            ("OKNO", "ONKO"),
            ("STŮL", "LŮST"),
            ("KNIHA", "NHKIA"),
            ("BARVA", "VARBA"),
            ("LÉTO", "TOLE"),
            ("TRÁVA", "VAART"),
            ("CHLEB", "LHCBE"),
            ("VODA", "ADOV"),
            ("VÍTR", "RÍTV"),
            ("SLOVO", "VOSLO"),
            ("MRAKY", "YAMRK"),
            ("SLANÝ", "NASŁY"),
        ]
        
        self.current_pair = random.choice(self.word_pairs)
        self.original = self.current_pair[0]
        self.scrambled = list(self.current_pair[1])
        self.answer = ""  # String místo seznamu
        self.used = [False] * len(self.scrambled)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # BACKSPACE = smazat poslední písmeno a vrátit do dostupných
            if event.key == pygame.K_BACKSPACE:
                if len(self.answer) > 0:
                    # Najdi poslední písmeno v self.answer
                    last_char = self.answer[-1]
                    # Vrat ho do dostupných - označ jako nepoužité
                    for i in range(len(self.scrambled) - 1, -1, -1):
                        if self.scrambled[i] == last_char and self.used[i]:
                            self.used[i] = False
                            break
                    # Odeber z odpovědi
                    self.answer = self.answer[:-1]
            # ENTER = ověřit odpověď
            elif event.key == pygame.K_RETURN:
                if self.answer.upper() == self.original:
                    self.won = True
                else:
                    self.answer = ""
                    self.used = [False] * len(self.scrambled)
            # Psaní textu - přidej písmeno
            elif event.unicode.isalpha():
                char = event.unicode.upper()
                # Zkontroluj, zda je písmeno ze scrambled a není ještě použito
                if char in self.scrambled and len(self.answer) < len(self.original):
                    # Najdi první nepoužívané výskyt písmena
                    char_index = -1
                    for i, letter in enumerate(self.scrambled):
                        if letter == char and not self.used[i]:
                            char_index = i
                            break
                    
                    if char_index != -1:
                        self.answer += char
                        self.used[char_index] = True
                        # Okamžitá kontrola výhry
                        if self.answer == self.original:
                            self.won = True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # Klikání na písmena
            for i in range(len(self.scrambled)):
                if self.used[i]:
                    continue
                x = 100 + i * 90
                y = 420
                if pygame.Rect(x, y, 70, 70).collidepoint(pos):
                    if len(self.answer) < len(self.original):
                        self.answer += self.scrambled[i]
                        self.used[i] = True
                        if self.answer == self.original:
                            self.won = True
                    return
            
            # Tlačítko SMAZAT
            if pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 120, 200, 80).collidepoint(pos):
                self.answer = ""
                self.used = [False] * len(self.scrambled)
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("SEŘAĎ SLOVO", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 140, 30))
        
        instr1 = FONT_SMALL.render("Psej nebo klikej na písmena v správném pořadí", True, YELLOW)
        screen.blit(instr1, (SCREEN_WIDTH//2 - 300, 120))
        
        # Input box
        answer_box_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, 180, 500, 80)
        pygame.draw.rect(screen, BLUE, answer_box_rect)
        pygame.draw.rect(screen, CYAN, answer_box_rect, 3)
        
        # Vyplněná pole
        for i in range(len(self.original)):
            x = SCREEN_WIDTH//2 - 240 + i * 95
            y = 195
            
            if i < len(self.answer):
                pygame.draw.rect(screen, GREEN, pygame.Rect(x, y, 70, 70))
                letter_text = FONT_MEDIUM.render(self.answer[i], True, BLACK)
            else:
                pygame.draw.rect(screen, (40, 40, 100), pygame.Rect(x, y, 70, 70))
                letter_text = FONT_MEDIUM.render("_", True, WHITE)
            
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 70, 70), 2)
            letter_rect = letter_text.get_rect(center=(x + 35, y + 35))
            screen.blit(letter_text, letter_rect)
        
        # Dostupná písmena
        avail_text = FONT_SMALL.render("DOSTUPNÁ PÍSMENA:", True, CYAN)
        screen.blit(avail_text, (100, 350))
        
        for i, char in enumerate(self.scrambled):
            if self.used[i]:
                continue
            x = 100 + i * 90
            y = 420
            pygame.draw.rect(screen, BLUE, pygame.Rect(x, y, 70, 70))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 70, 70), 2)
            
            char_text = FONT_MEDIUM.render(char, True, WHITE)
            char_rect = char_text.get_rect(center=(x + 35, y + 35))
            screen.blit(char_text, char_rect)
        
        # Tlačítko SMAZAT
        clear_btn_rect = pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 120, 200, 80)
        pygame.draw.rect(screen, RED, clear_btn_rect)
        pygame.draw.rect(screen, WHITE, clear_btn_rect, 2)
        clear_text = FONT_SMALL.render("SMAZAT", True, BLACK)
        clear_rect = clear_text.get_rect(center=clear_btn_rect.center)
        screen.blit(clear_text, clear_rect)
        
        # Instrukce
        instr2 = FONT_SMALL.render("ENTER: Ověř | BACKSPACE: Smazat poslední | KLIK na písmena", True, WHITE)
        screen.blit(instr2, (SCREEN_WIDTH//2 - 350, 700))
    
    def get_hint(self):
        return f"Správné slovo: {self.original}"


class MemoryCards(BaseGame):
    """Hra na paměť - otočit karty a najít páry - maximálně 2 karty současně"""
    def __init__(self):
        super().__init__()
        self.symbols = ['A', 'B', 'C', 'D'] 
        self.cards = self.symbols + self.symbols
        random.shuffle(self.cards)
        self.revealed = [False] * 8
        self.matched = [False] * 8
        self.selected = []
        self.matches = 0
        self.animation_timer = 0
        self.card_size = 100
        self.card_spacing = 50
        self.start_x = SCREEN_WIDTH // 2 - 2 * (self.card_size) - self.card_spacing
        self.start_y = SCREEN_HEIGHT // 2 - self.card_size
    
    def handle_event(self, event):
        # Pouze je-li není aktivní animace zpět (flip animation)
        if event.type == pygame.MOUSEBUTTONDOWN and len(self.selected) < 2 and self.animation_timer == 0:
            pos = event.pos
            for i in range(8):
                x = self.start_x + (i % 4) * (self.card_size + self.card_spacing)
                y = self.start_y + (i // 4) * (self.card_size + self.card_spacing)
                if pygame.Rect(x, y, self.card_size, self.card_size).collidepoint(pos):
                    # Neklikat na už matchnuté karty nebo už vybrané
                    if not self.matched[i] and i not in self.selected:
                        self.selected.append(i)
                        self.revealed[i] = True
                        
                        # Když jsou 2 karty vybrány
                        if len(self.selected) == 2:
                            if self.cards[self.selected[0]] == self.cards[self.selected[1]]:
                                # Úspěšný match
                                self.matched[self.selected[0]] = True
                                self.matched[self.selected[1]] = True
                                self.matches += 1
                                self.selected = []
                                if self.matches == 4:
                                    self.won = True
                            else:
                                # Nesprávný match - start animace
                                self.animation_timer = 60  # 1 sekunda
                        break
    
    def update(self):
        # Animace: po 1 sekundě se karty zpět skryjou
        if self.animation_timer > 0:
            self.animation_timer -= 1
            if self.animation_timer == 0:
                # Skryj karty
                for idx in self.selected:
                    self.revealed[idx] = False
                self.selected = []
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("MEMORY KARTY", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 50))
        
        for i in range(8):
            x = self.start_x + (i % 4) * (self.card_size + self.card_spacing)
            y = self.start_y + (i // 4) * (self.card_size + self.card_spacing)
            color = GREEN if self.matched[i] else BLUE
            pygame.draw.rect(screen, color, pygame.Rect(x, y, self.card_size, self.card_size))
            if self.revealed[i]:
                text = FONT_LARGE.render(self.cards[i], True, YELLOW)
                text_rect = text.get_rect(center=(x + self.card_size // 2, y + self.card_size // 2))
                screen.blit(text, text_rect)
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, self.card_size, self.card_size), 3)
        
        info = FONT_SMALL.render(f"Páry: {self.matches}/4", True, WHITE)
        screen.blit(info, (SCREEN_WIDTH//2 - 100, 700))
        
        hint_text = FONT_TINY.render("Maximálně 2 karty současně!", True, YELLOW)
        screen.blit(hint_text, (SCREEN_WIDTH//2 - 150, 750))
    
    def get_hint(self):
        return "Zapamatuj si pozice karet! Maximálně 2 současně."


class FindShape(BaseGame):
    """Najdi správný tvar - jednoduchý a stabilní level"""
    def __init__(self):
        super().__init__()
        self.target_shape = random.choice(["kruh", "ctverce", "trojuhelnik"])
        self.shapes = []
        self.create_shapes()
        self.clicked_correct = False
    
    def create_shapes(self):
        """Vytvoří náhodné tvary"""
        positions = [
            (300, 300), (800, 300), (1300, 300),
            (300, 600), (800, 600), (1300, 600)
        ]
        shapes = ["kruh", "ctverce", "trojuhelnik"] * 2
        random.shuffle(shapes)
        
        target_pos = random.choice(positions)
        positions.remove(target_pos)
        
        for shape, pos in zip(shapes, positions):
            self.shapes.append({"type": shape, "pos": pos, "radius": 50})
        
        # Vlož cíl do náhodné pozice
        self.shapes.append({"type": self.target_shape, "pos": target_pos, "radius": 50})
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for shape in self.shapes:
                x, y = shape["pos"]
                dist = ((pos[0] - x)**2 + (pos[1] - y)**2)**0.5
                if dist < shape["radius"]:
                    if shape["type"] == self.target_shape:
                        self.won = True
                    else:
                        self.lost = True
                    break
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render(f"NAJDI: {self.target_shape.upper()}", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 250, 30))
        
        for shape in self.shapes:
            x, y = shape["pos"]
            shape_type = shape["type"]
            r = shape["radius"]
            
            if shape_type == "kruh":
                pygame.draw.circle(screen, RED, (x, y), r)
            elif shape_type == "ctverce":
                pygame.draw.rect(screen, BLUE, pygame.Rect(x - r, y - r, 2*r, 2*r))
            elif shape_type == "trojuhelnik":
                pygame.draw.polygon(screen, GREEN, [(x, y-r), (x-r, y+r), (x+r, y+r)])
            
            pygame.draw.circle(screen, WHITE, (x, y), r, 2)
        
        instr = FONT_SMALL.render("Klikni na cílový tvar!", True, YELLOW)
        screen.blit(instr, (SCREEN_WIDTH//2 - 150, 700))
    
    def get_hint(self):
        return f"Hledej: {self.target_shape}"


class SpeedClick(BaseGame):
    """Klikej rychle na bílé čtverce - timer začíná až po prvním kliknutí"""
    def __init__(self):
        super().__init__()
        self.targets = []
        self.clicked = 0
        self.timer = 0
        self.timer_started = False
        self.time_limit = 420  # 7 sekund (420 framů)
        self.generate_targets()
    
    def generate_targets(self):
        self.targets = []
        for _ in range(10):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(200, SCREEN_HEIGHT - 200)
            self.targets.append(pygame.Rect(x, y, 60, 60))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.timer_started:
                self.timer_started = True
            
            pos = event.pos
            for i, target in enumerate(self.targets):
                if target.collidepoint(pos):
                    self.targets.pop(i)
                    self.clicked += 1
                    if self.clicked == 10:
                        self.won = True
                    break
    
    def update(self):
        if self.timer_started:
            self.timer += 1
            if self.timer > self.time_limit:
                if self.clicked >= 10:
                    self.won = True
                else:
                    self.lost = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("RYCHLE KLIKEJ!", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 180, 30))
        
        for target in self.targets:
            pygame.draw.rect(screen, WHITE, target)
            pygame.draw.rect(screen, CYAN, target, 3)
        
        info = FONT_MEDIUM.render(f"Kliknutí: {self.clicked}/10", True, YELLOW)
        screen.blit(info, (SCREEN_WIDTH//2 - 150, 700))
        
        if self.timer_started:
            time_left = max(0, (self.time_limit - self.timer) // 60)
            time_text = FONT_SMALL.render(f"Čas: {time_left}s", True, GREEN if time_left > 2 else RED)
            screen.blit(time_text, (SCREEN_WIDTH//2 - 60, 750))
        else:
            start_text = FONT_SMALL.render("Klikni kdekoli pro start!", True, YELLOW)
            screen.blit(start_text, (SCREEN_WIDTH//2 - 150, 600))
    
    def get_hint(self):
        return "Klikej na všechny čtverce!"


class PatternFollow(BaseGame):
    """Sleduj a opakuj barvu vzoru"""
    def __init__(self):
        super().__init__()
        self.pattern = [random.randint(0, 3) for _ in range(5)]
        self.player_pattern = []
        self.showing = False
        self.show_timer = 0
        self.colors = [RED, YELLOW, GREEN, BLUE]
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.showing:
            pos = event.pos
            for i in range(4):
                x = 300 + (i % 2) * 250
                y = 300 + (i // 2) * 250
                if pygame.Rect(x, y, 200, 200).collidepoint(pos):
                    self.player_pattern.append(i)
                    self.show_timer = 30
                    self.check()
                    break
    
    def check(self):
        if self.player_pattern[-1] != self.pattern[len(self.player_pattern) - 1]:
            self.lost = True
        elif len(self.player_pattern) == len(self.pattern):
            self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("NÁSLEDUJ BARVY", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        for i in range(4):
            x = 300 + (i % 2) * 250
            y = 300 + (i // 2) * 250
            pygame.draw.rect(screen, self.colors[i], pygame.Rect(x, y, 200, 200))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 200, 200), 3)
        
        info = FONT_SMALL.render(f"Krok {len(self.player_pattern)}/{len(self.pattern)}", True, WHITE)
        screen.blit(info, (SCREEN_WIDTH//2 - 150, 700))
    
    def get_hint(self):
        return f"Pamatuj: {len(self.pattern)} barev"


class NumberSort(BaseGame):
    """Seřaď čísla od nejmenšího k největšímu"""
    def __init__(self):
        super().__init__()
        self.numbers = random.sample(range(1, 101), 5)
        self.player_order = []
        self.sorted_correct = sorted(self.numbers)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i, num in enumerate(self.numbers):
                x = 250 + i * 250
                y = 400
                if pygame.Rect(x, y, 150, 100).collidepoint(pos):
                    if num not in self.player_order:
                        self.player_order.append(num)
                        if self.player_order == self.sorted_correct:
                            self.won = True
                    break
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("SEŘAĎ ČÍSLA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        for i, num in enumerate(self.numbers):
            x = 250 + i * 250
            y = 400
            pygame.draw.rect(screen, BLUE, pygame.Rect(x, y, 150, 100))
            text = FONT_LARGE.render(str(num), True, WHITE)
            screen.blit(text, (x + 40, y + 20))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 150, 100), 3)
        
        result = " < ".join(str(n) for n in self.player_order) if self.player_order else "?"
        result_text = FONT_SMALL.render(f"Tvůj výběr: {result}", True, YELLOW)
        screen.blit(result_text, (SCREEN_WIDTH//2 - 300, 650))
    
    def get_hint(self):
        return f"Správné pořadí: {' < '.join(str(n) for n in self.sorted_correct)}"


class ReactionTime(BaseGame):
    """Test reflexu - červená = prohra, zelená = měření"""
    def __init__(self):
        super().__init__()
        self.state = "red"  # "red" nebo "green"
        self.timer = 0
        self.reaction_time_ms = 0
        self.target_time = 300  # Nadprůměrný čas v ms
        self.change_timer = random.randint(120, 300)
        self.clicked = False
        self.start_frame = 0
    
    def update(self):
        self.timer += 1
        if self.timer == self.change_timer and self.state == "red":
            self.state = "green"
            self.start_frame = self.timer
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:
            self.clicked = True
            if self.state == "red":
                # Klik během červené = okamžitá prohra
                self.lost = True
            elif self.state == "green":
                # Měření času
                frames_passed = self.timer - self.start_frame
                self.reaction_time_ms = int(frames_passed * (1000 / 60))
                if self.reaction_time_ms < self.target_time:
                    self.won = True
                else:
                    self.lost = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("REFLEX TEST", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 200, 30))
        
        info = FONT_SMALL.render(f"Červená = prohra | Zelená = měření | Cíl: pod {self.target_time}ms", True, YELLOW)
        screen.blit(info, (SCREEN_WIDTH//2 - 400, 120))
        
        if self.state == "red":
            # Červená obrazovka - čekání
            pygame.draw.rect(screen, RED, pygame.Rect(400, 250, 1000, 500))
            text = FONT_LARGE.render("CEKEJ... NEKLIKEJ!", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - 350, 450))
        elif self.state == "green":
            if not self.clicked:
                # Zelená - klikni!
                pygame.draw.rect(screen, GREEN, pygame.Rect(400, 250, 1000, 500))
                text = FONT_LARGE.render("KLIKNI TEĎ!", True, BLACK)
                screen.blit(text, (SCREEN_WIDTH//2 - 280, 450))
            else:
                # Zobraz čas a výsledek
                time_text = FONT_LARGE.render(f"{self.reaction_time_ms} ms", True, YELLOW)
                screen.blit(time_text, (SCREEN_WIDTH//2 - 150, 280))
                
                if self.reaction_time_ms < self.target_time:
                    result = FONT_MEDIUM.render("VYHRAL! ✓", True, GREEN)
                    diff = FONT_SMALL.render(f"{self.target_time - self.reaction_time_ms}ms lepší", True, GREEN)
                else:
                    result = FONT_MEDIUM.render("PROHRA! ✗", True, RED)
                    diff = FONT_SMALL.render(f"{self.reaction_time_ms - self.target_time}ms horší", True, RED)
                
                screen.blit(result, (SCREEN_WIDTH//2 - 120, 450))
                screen.blit(diff, (SCREEN_WIDTH//2 - 120, 500))
    
    def get_hint(self):
        return f"Čekej na zelený čtverec a klikni rychleji než {self.target_time}ms!"


class Hangman(BaseGame):
    """Guess word - Hangman with categories and riddle hints - NOW IN ENGLISH"""
    def __init__(self):
        super().__init__()
        self.categories = {
            "ANIMALS": ["DOG", "CAT", "BIRD", "HORSE", "ELEPHANT"],
            "FOOD": ["PIZZA", "BREAD", "CHEESE", "APPLE", "CHICKEN"],
            "COUNTRIES": ["FRANCE", "GERMANY", "JAPAN", "BRAZIL", "CANADA"],
            "SPORTS": ["TENNIS", "HOCKEY", "SOCCER", "BOXING", "SWIMMING"]
        }
        self.riddles = {
            "DOG": "Domesticated 15,000 years ago from wolves, this loyal companion can learn hundreds of words and sniff out diseases.",
            "CAT": "Worshipped as gods in ancient Egypt, these silent hunters spend 70% of their lives sleeping.",
            "BIRD": "The only living descendants of dinosaurs, some species can fly backwards while others swim but never take flight.",
            "HORSE": "Alexander the Great's Bucephalus was one; they sleep standing up and can run within hours of birth.",
            "ELEPHANT": "Earth's largest land mammal, it mourns its dead, fears bees, and its tusks are actually overgrown teeth.",
            "PIZZA": "A dish that traveled from Naples to conquer the world, the Margherita variety was named after an Italian queen in 1889.",
            "BREAD": "One of humanity's oldest prepared foods dating back 14,000 years, ancient Egyptians used it as currency.",
            "CHEESE": "Accidentally discovered when milk was stored in animal stomachs, some aged varieties are legally alive with mites.",
            "APPLE": "Newton allegedly discovered gravity thanks to one; its seeds contain a compound that converts to cyanide.",
            "CHICKEN": "Descended from the jungle fowl of Southeast Asia, it outnumbers humans 3 to 1 on Earth.",
            "FRANCE": "Home to a tower once hated by locals, a louvre that was a fortress, and the world's most visited country.",
            "GERMANY": "A European nation central to both World Wars, famous for engineering, autobahns with no speed limit, and Oktoberfest.",
            "JAPAN": "An island nation with more vending machines per capita than any other, where trains apologize for being seconds late.",
            "BRAZIL": "Named after a tree, it hosts the world's largest carnival and contains 60% of the Amazon rainforest.",
            "CANADA": "The world's second-largest country by area, it has more lakes than the rest of the world combined.",
            "TENNIS": "A sport where 'love' means zero, originally played with bare hands in French monasteries.",
            "HOCKEY": "A sport played on frozen water where a vulcanized rubber disc can travel over 170 km/h.",
            "SOCCER": "The world's most popular sport; its biggest tournament was once decided by a 'Hand of God' goal.",
            "BOXING": "Known as 'the sweet science', ancient Greeks wrapped their fists in leather strips to compete at Olympia.",
            "SWIMMING": "Benjamin Franklin invented flippers for it; humans are the only primates that naturally enjoy doing it."
        }
        self.category = random.choice(list(self.categories.keys()))
        self.word = random.choice(self.categories[self.category])
        self.riddle = self.riddles.get(self.word, "")
        self.guessed = set()
        self.wrong = 0
        self.max_wrong = 6
        self.hint_visible = False
        self.hint_space_count = 0
        self.hint_space_timer = 0
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Double-SPACE detection for hint toggle
            if event.key == pygame.K_SPACE:
                self.hint_space_count += 1
                self.hint_space_timer = 25  # ~400ms at 60fps
                if self.hint_space_count >= 2:
                    self.hint_visible = not self.hint_visible
                    self.hint_space_count = 0
                return
            if event.unicode.isalpha():
                letter = event.unicode.upper()
                if letter not in self.guessed:
                    self.guessed.add(letter)
                    if letter not in self.word:
                        self.wrong += 1
                    
                    if all(l in self.guessed for l in self.word):
                        self.won = True
                    if self.wrong >= self.max_wrong:
                        self.lost = True
    
    def update(self):
        if self.hint_space_timer > 0:
            self.hint_space_timer -= 1
        else:
            self.hint_space_count = 0
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("HANGMAN", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        cat_text = FONT_SMALL.render(f"Category: {self.category}", True, CYAN)
        screen.blit(cat_text, (SCREEN_WIDTH//2 - 150, 80))

        # Riddle hint (only visible after double-SPACE)
        if self.riddle and self.hint_visible:
            max_w = 80
            words = self.riddle.split()
            lines = []
            cur = ""
            for w in words:
                if len(cur) + len(w) + 1 <= max_w:
                    cur = cur + " " + w if cur else w
                else:
                    lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
            for li, line in enumerate(lines):
                rt = FONT_TINY.render(line, True, (200, 200, 255))
                screen.blit(rt, (SCREEN_WIDTH//2 - rt.get_width()//2, 120 + li * 22))
        elif not self.hint_visible:
            ht = FONT_TINY.render("Napoveda: 2x SPACE", True, (120, 120, 150))
            screen.blit(ht, (SCREEN_WIDTH//2 - ht.get_width()//2, 120))

        word_display = " ".join(l if l in self.guessed else "_" for l in self.word)
        word_text = FONT_LARGE.render(word_display, True, YELLOW)
        screen.blit(word_text, (SCREEN_WIDTH//2 - 200, 230))
        
        guessed_text = FONT_SMALL.render(f"Hádaná písmena: {' '.join(sorted(self.guessed))}", True, WHITE)
        screen.blit(guessed_text, (SCREEN_WIDTH//2 - 300, 380))
        
        wrong_text = FONT_MEDIUM.render(f"Chyby: {self.wrong}/{self.max_wrong}", True, RED)
        screen.blit(wrong_text, (SCREEN_WIDTH//2 - 150, 500))
        
        # OPRAVA: Zobraz slovo když prohraješ
        if self.lost:
            lost_text = FONT_LARGE.render(f"PROHRAUL! Slovo: {self.word}", True, RED)
            screen.blit(lost_text, (SCREEN_WIDTH//2 - 300, 650))
    
    def get_hint(self):
        return f"Slovo: {self.word}"


class ColorBlind(BaseGame):
    """Najdi jinou barvu - stejná barva, jen jiný odstín - VÍCE RUNDY A BAREV"""
    def __init__(self):
        super().__init__()
        self.total_rounds = 5  # Více rundy
        self.current_round = 0
        self.rounds_completed = 0
        self.available_colors = [RED, BLUE, YELLOW, GREEN, CYAN]
        self.generate_new_round()
    
    def generate_new_round(self):
        """Generuj nové kolo s jinou barvou"""
        self.base_color = random.choice(self.available_colors)
        
        # Vytvoř podobný odstín - stejná barva, ale o něco světlejší/tmavší
        color_map = {
            RED: (200, 50, 50),
            BLUE: (50, 100, 200),
            YELLOW: (200, 200, 100),
            GREEN: (100, 180, 100),
            CYAN: (50, 220, 220)
        }
        self.different_color = color_map[self.base_color]
        self.positions = list(range(16))
        self.different_pos = random.randint(0, 15)
        random.shuffle(self.positions)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i in range(16):
                x = 300 + (i % 4) * 200
                y = 250 + (i // 4) * 200
                if pygame.Rect(x, y, 150, 150).collidepoint(pos):
                    if self.positions[i] == self.different_pos:
                        self.rounds_completed += 1
                        if self.rounds_completed >= self.total_rounds:
                            self.won = True
                        else:
                            # Další kolo
                            self.current_round += 1
                            self.generate_new_round()
                    else:
                        self.lost = True
                    break
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("NAJDI ROZDÍL", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        # Počet rundy
        round_text = FONT_MEDIUM.render(f"Kolo {self.rounds_completed + 1}/{self.total_rounds}", True, YELLOW)
        screen.blit(round_text, (SCREEN_WIDTH//2 - 150, 100))
        
        for i in range(16):
            x = 300 + (i % 4) * 200
            y = 250 + (i // 4) * 200
            color = self.different_color if self.positions[i] == self.different_pos else self.base_color
            pygame.draw.rect(screen, color, pygame.Rect(x, y, 150, 150))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 150, 150), 2)
    
    def get_hint(self):
        return f"Najdi jinou barvu! Kolo {self.rounds_completed + 1}/{self.total_rounds}"


class MasterChallenge(BaseGame):
    """Finální výzva - kombinace všeho"""
    def __init__(self):
        super().__init__()
        self.challenges = [
            {"type": "math", "data": {"num1": 25, "num2": 7, "op": "*", "ans": 175}},
            {"type": "memory", "data": {"sequence": [1, 3, 0, 2, 1]}},
            {"type": "speed", "data": {}},
        ]
        self.current = 0
        self.completed = 0
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.current == 0:
                if event.unicode.isdigit():
                    self.completed += 1
                    if self.completed >= 3:
                        self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("FINÁLNÍ VÝZVA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 180, 50))
        
        challenge_text = FONT_MEDIUM.render(f"Vyzva {self.current + 1}/3", True, YELLOW)
        screen.blit(challenge_text, (SCREEN_WIDTH//2 - 150, 250))
        
        instruction = FONT_SMALL.render("Dokončil(a) jsi základní úkoly!", True, GREEN if self.completed > 0 else WHITE)
        screen.blit(instruction, (SCREEN_WIDTH//2 - 250, 450))
    
    def get_hint(self):
        return "Dej to všechno dohromady!"


class PipeConnect(BaseGame):
    """Otočení trubek - propoj zdroj s cílem"""
    def __init__(self):
        super().__init__()
        self.grid_size = 4
        self.cell_size = 100
        self.start_pos = (0, 1)
        self.end_pos = (3, 2)
        self.pipes = self.create_grid()
        self.water_timer = 0
    
    def create_grid(self):
        pipes = []
        for row in range(self.grid_size):
            pipe_row = []
            for col in range(self.grid_size):
                rotation = random.randint(0, 3)
                pipe_type = random.choice(["straight", "corner"])
                pipe_row.append({"type": pipe_type, "rotation": rotation})
            pipes.append(pipe_row)
        pipes[self.start_pos[0]][self.start_pos[1]] = {"type": "start", "rotation": 0}
        pipes[self.end_pos[0]][self.end_pos[1]] = {"type": "end", "rotation": 0}
        return pipes
    
    def is_connected(self):
        """Kontrola zda jsou trubky správně připojeny"""
        visited = set()
        queue = [self.start_pos]
        
        while queue:
            pos = queue.pop(0)
            if pos in visited:
                continue
            visited.add(pos)
            
            if pos == self.end_pos:
                return True
            
            row, col = pos
            pipe = self.pipes[row][col]
            rotation = pipe["rotation"]
            
            connections = self.get_connections(pipe["type"], rotation)
            for direction in connections:
                next_pos = self.move_in_direction(pos, direction)
                if next_pos and next_pos not in visited:
                    next_pipe = self.pipes[next_pos[0]][next_pos[1]]
                    opposite = self.opposite_direction(direction)
                    next_connections = self.get_connections(next_pipe["type"], next_pipe["rotation"])
                    if opposite in next_connections:
                        queue.append(next_pos)
        
        return False
    
    def get_connections(self, pipe_type, rotation):
        """Vrací spojení trubky v daném otočení"""
        if pipe_type == "straight":
            if rotation in [0, 2]:
                return ["up", "down"]
            else:
                return ["left", "right"]
        elif pipe_type == "corner":
            corners = [
                ["up", "right"],
                ["right", "down"],
                ["down", "left"],
                ["left", "up"]
            ]
            return corners[rotation]
        elif pipe_type in ["start", "end"]:
            return ["down"] if pipe_type == "start" else ["up"]
        return []
    
    def move_in_direction(self, pos, direction):
        row, col = pos
        if direction == "up" and row > 0:
            return (row - 1, col)
        elif direction == "down" and row < self.grid_size - 1:
            return (row + 1, col)
        elif direction == "left" and col > 0:
            return (row, col - 1)
        elif direction == "right" and col < self.grid_size - 1:
            return (row, col + 1)
        return None
    
    def opposite_direction(self, direction):
        opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
        return opposites[direction]
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    x = 400 + col * self.cell_size
                    y = 250 + row * self.cell_size
                    rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                    if rect.collidepoint(pos):
                        if self.pipes[row][col]["type"] not in ["start", "end"]:
                            self.pipes[row][col]["rotation"] = (self.pipes[row][col]["rotation"] + 1) % 4
                        if self.is_connected():
                            self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("OTOČENÍ TRUBEK", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 180, 30))
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = 400 + col * self.cell_size
                y = 250 + row * self.cell_size
                pipe = self.pipes[row][col]
                
                color = GREEN if (row, col) == self.start_pos else RED if (row, col) == self.end_pos else BLUE
                pygame.draw.rect(screen, color, pygame.Rect(x, y, self.cell_size, self.cell_size))
                pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, self.cell_size, self.cell_size), 2)
                
                if pipe["type"] == "straight":
                    angle = pipe["rotation"] * 90
                    if angle % 180 == 0:
                        pygame.draw.line(screen, YELLOW, (x + 50, y + 20), (x + 50, y + 80), 3)
                    else:
                        pygame.draw.line(screen, YELLOW, (x + 20, y + 50), (x + 80, y + 50), 3)
                elif pipe["type"] == "corner":
                    rotation = pipe["rotation"]
                    points = [
                        [(x + 50, y + 20), (x + 50, y + 50), (x + 80, y + 50)],
                        [(x + 20, y + 50), (x + 50, y + 50), (x + 50, y + 80)],
                        [(x + 50, y + 80), (x + 50, y + 50), (x + 20, y + 50)],
                        [(x + 80, y + 50), (x + 50, y + 50), (x + 50, y + 20)]
                    ]
                    pygame.draw.lines(screen, YELLOW, False, points[rotation], 3)
        
        instr = FONT_SMALL.render("Klikni na trubku pro otočení - propoj zdroj s cílem", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 310, 700))
    
    def get_hint(self):
        return "Otáčej trubky, aby se zdroj (zelený) připojil k cíli (červený)"


class TimeBomb(BaseGame):
    """Časová bomba - přeřízni správný kabel pro deaktivaci"""
    def __init__(self):
        super().__init__()
        self.cables = [
            {"color": RED, "correct": False},
            {"color": GREEN, "correct": True},
            {"color": BLUE, "correct": False},
            {"color": YELLOW, "correct": False}
        ]
        random.shuffle(self.cables)
        self.timer = 600  # 10 sekund
        self.cut = False
        self.message = "Vyberte správný kabel!"
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.cut:
            pos = event.pos
            for i, cable in enumerate(self.cables):
                x = 300 + i * 150
                y = 400
                if pygame.Rect(x - 30, y - 50, 60, 100).collidepoint(pos):
                    self.cut = True
                    if cable["correct"]:
                        self.won = True
                        self.message = "Bomba deaktivována! ✓"
                    else:
                        self.lost = True
                        self.message = "VÝBUCH! Špatný kabel! ✗"
                    break
    
    def update(self):
        if not self.cut:
            self.timer -= 1
            if self.timer <= 0:
                self.lost = True
                self.message = "Čas vypršel! Výbuch! ✗"
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        # Bomba s časovačem
        title = FONT_LARGE.render("⏱ ČASOVÁ BOMBA ⏱", True, RED if self.timer < 180 else YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - 250, 30))
        
        # Časovač
        seconds = max(0, self.timer // 60)
        timer_text = FONT_LARGE.render(f"{seconds}s", True, RED if seconds < 3 else YELLOW)
        screen.blit(timer_text, (SCREEN_WIDTH//2 - 80, 150))
        
        # Kabely
        for i, cable in enumerate(self.cables):
            x = 300 + i * 150
            y = 400
            
            # Kreslení kabelu jako svislé čáry
            pygame.draw.line(screen, cable["color"], (x, y - 50), (x, y + 50), 8)
            
            # Kreslení řezu
            if self.cut:
                pygame.draw.line(screen, WHITE, (x - 30, y), (x + 30, y), 3)
            
            pygame.draw.rect(screen, cable["color"], pygame.Rect(x - 20, y - 40, 40, 30))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x - 20, y - 40, 40, 30), 2)
        
        # Zpráva
        msg_color = GREEN if self.won else RED
        message = FONT_MEDIUM.render(self.message, True, msg_color)
        screen.blit(message, (SCREEN_WIDTH//2 - 200, 550))
        
        # Instrukce
        if not self.cut:
            instr = FONT_SMALL.render("KLIKNI NA SPRÁVNÝ KABEL - váš život závisí na tom!", True, WHITE)
            screen.blit(instr, (SCREEN_WIDTH//2 - 300, 650))
    
    def get_hint(self):
        correct_idx = next(i for i, c in enumerate(self.cables) if c["correct"])
        return f"Správný kabel je na {correct_idx + 1}. místě!"


class RotatingImage(BaseGame):
    """
    Rozpoznej Tvar – Level 11 HARD Edition.
    3 brutally deceptive rounds.  Pick the ONE exact match among 12 shapes.
    Round 1: Pentagon 30° rotation (purple)
    Round 2: Scalene Triangle 60° rotation (orange)
    Round 3: Isosceles Trapezoid 25° rotation (cyan)
    Pass: 2/3 correct.  Perfect: 3/3.
    """

    TOTAL_ROUNDS = 3
    # time limits per round in frames (60 fps)
    ROUND_FRAMES = [45 * 60, 50 * 60, 60 * 60]

    # colours
    C_PURPLE = (123, 44, 191)
    C_ORANGE = (255, 107, 53)
    C_CYAN   = (0, 217, 255)
    C_CORRECT_BG = (30, 120, 30)
    C_WRONG_BG   = (140, 20, 20)
    C_CELL_BG    = (35, 38, 60)
    C_CELL_HL    = (55, 58, 85)

    # grid: 4 cols × 3 rows = 12 slots
    GRID_COLS = 4
    GRID_ROWS = 3
    CELL_W    = 200
    CELL_H    = 180

    def __init__(self):
        super().__init__()
        self.current_round = 0
        self.correct_count = 0
        self.frame_timer   = 0
        self.feedback_timer = 0   # >0 while showing correct/wrong flash
        self.last_correct   = None
        self.hover_idx      = -1

        # Build all 3 rounds
        self.rounds = [
            self._build_round_1(),
            self._build_round_2(),
            self._build_round_3(),
        ]
        self._prepare_round()

    # ------------------------------------------------------------------
    # POLYGON HELPERS
    # ------------------------------------------------------------------
    @staticmethod
    def _regular_polygon(cx, cy, r, n, rot_deg=0):
        """Return list of (x,y) for a regular n-gon centred at (cx,cy)."""
        pts = []
        for i in range(n):
            a = math.radians(rot_deg + 360 * i / n - 90)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts

    @staticmethod
    def _rotate_pts(pts, cx, cy, deg):
        """Rotate a list of points around (cx,cy) by deg degrees."""
        a = math.radians(deg)
        cos_a, sin_a = math.cos(a), math.sin(a)
        out = []
        for x, y in pts:
            dx, dy = x - cx, y - cy
            out.append((cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a))
        return out

    @staticmethod
    def _scale_pts(pts, cx, cy, s):
        """Scale points relative to centre."""
        return [(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in pts]

    @staticmethod
    def _stretch_pts(pts, cx, cy, sx, sy):
        """Non-uniform scale."""
        return [(cx + (x - cx) * sx, cy + (y - cy) * sy) for x, y in pts]

    @staticmethod
    def _move_vertex(pts, idx, dx, dy):
        """Return copy with one vertex shifted."""
        out = list(pts)
        x, y = out[idx]
        out[idx] = (x + dx, y + dy)
        return out

    # ------------------------------------------------------------------
    # SHAPE DRAW  (all shapes are drawn as filled+outlined polygons)
    # ------------------------------------------------------------------
    def _draw_poly(self, surf, pts, fill, outline=(0, 0, 0), ow=3):
        if len(pts) < 3:
            return
        pygame.draw.polygon(surf, fill, pts)
        pygame.draw.polygon(surf, outline, pts, ow)

    # ------------------------------------------------------------------
    # BUILD ROUNDS
    # ------------------------------------------------------------------
    def _build_round_1(self):
        """Pentagon recognition – 12 options, 1 correct."""
        colour = self.C_PURPLE
        cx, cy = 0, 0  # placeholder; will be offset at draw time
        r = 50          # drawing radius for grid cells

        def target(cx, cy):
            return self._rotate_pts(self._regular_polygon(cx, cy, r, 5), cx, cy, 30)

        def make(cx, cy):
            """All 12 option generators. Index 0 = correct."""
            return [
                # 0 correct: pentagon 30°
                target(cx, cy),
                # 1 pentagon -20°
                self._rotate_pts(self._regular_polygon(cx, cy, r, 5), cx, cy, -20),
                # 2 pentagon 45°
                self._rotate_pts(self._regular_polygon(cx, cy, r, 5), cx, cy, 45),
                # 3 pentagon -60°
                self._rotate_pts(self._regular_polygon(cx, cy, r, 5), cx, cy, -60),
                # 4 hexagon 30°
                self._rotate_pts(self._regular_polygon(cx, cy, r, 6), cx, cy, 30),
                # 5 heptagon 30°
                self._rotate_pts(self._regular_polygon(cx, cy, r, 7), cx, cy, 30),
                # 6 star 5-pointed
                self._star(cx, cy, r, r * 0.45, 5, 0),
                # 7 pentagon stretched horiz
                self._stretch_pts(self._rotate_pts(self._regular_polygon(cx, cy, r, 5), cx, cy, 30), cx, cy, 1.35, 0.85),
                # 8 pentagon small
                self._scale_pts(self._rotate_pts(self._regular_polygon(cx, cy, r, 5), cx, cy, 30), cx, cy, 0.6),
                # 9 pentagon large
                self._scale_pts(self._rotate_pts(self._regular_polygon(cx, cy, r, 5), cx, cy, 30), cx, cy, 1.45),
                # 10 pentagon with shifted vertex
                self._move_vertex(self._rotate_pts(self._regular_polygon(cx, cy, r, 5), cx, cy, 30), 2, 12, -10),
                # 11 diamond (4 sides)
                self._rotate_pts(self._regular_polygon(cx, cy, r, 4), cx, cy, 30),
            ]

        return {
            "title": "KOLO 1/3 – ROTAČNÍ BLUDIŠTĚ",
            "subtitle": "Najdi přesný pětiúhelník otočený o 30°",
            "colour": colour,
            "correct_idx": 0,
            "make_fn": make,
            "target_fn": target,
        }

    def _star(self, cx, cy, r_out, r_in, n, rot_deg):
        pts = []
        for i in range(n * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.radians(rot_deg + 360 * i / (n * 2) - 90)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts

    def _build_round_2(self):
        """Scalene triangle 60° rotation."""
        colour = self.C_ORANGE

        # Scalene base: sides ~40, 50, 60 (half-sizes for grid-cell rendering)
        def scalene(cx, cy):
            return [(cx - 30, cy + 25), (cx + 40, cy + 25), (cx + 5, cy - 35)]

        def target(cx, cy):
            return self._rotate_pts(scalene(cx, cy), cx, cy, 60)

        def isosceles(cx, cy):
            return [(cx - 30, cy + 25), (cx + 30, cy + 25), (cx, cy - 35)]

        def equilateral(cx, cy):
            return self._regular_polygon(cx, cy, 42, 3)

        def right_tri(cx, cy):
            return [(cx - 30, cy + 30), (cx + 35, cy + 30), (cx - 30, cy - 30)]

        def make(cx, cy):
            return [
                # 0 correct: scalene 60°
                target(cx, cy),
                # 1 isosceles 60°
                self._rotate_pts(isosceles(cx, cy), cx, cy, 60),
                # 2 equilateral 60°
                self._rotate_pts(equilateral(cx, cy), cx, cy, 60),
                # 3 scalene -60°
                self._rotate_pts(scalene(cx, cy), cx, cy, -60),
                # 4 scalene 0°
                scalene(cx, cy),
                # 5 scalene 90°
                self._rotate_pts(scalene(cx, cy), cx, cy, 90),
                # 6 scalene 0.7x
                self._scale_pts(self._rotate_pts(scalene(cx, cy), cx, cy, 60), cx, cy, 0.7),
                # 7 scalene 1.5x
                self._scale_pts(self._rotate_pts(scalene(cx, cy), cx, cy, 60), cx, cy, 1.4),
                # 8 scalene stretched
                self._stretch_pts(self._rotate_pts(scalene(cx, cy), cx, cy, 60), cx, cy, 1.3, 0.8),
                # 9 right triangle 60°
                self._rotate_pts(right_tri(cx, cy), cx, cy, 60),
                # 10 diamond
                self._rotate_pts(self._regular_polygon(cx, cy, 40, 4), cx, cy, 60),
                # 11 trapezoid
                self._rotate_pts([(cx - 35, cy + 25), (cx + 35, cy + 25), (cx + 20, cy - 25), (cx - 20, cy - 25)], cx, cy, 60),
            ]

        return {
            "title": "KOLO 2/3 – MĚŘÍTKOVÝ KLAM",
            "subtitle": "Najdi přesný nerovnostranný trojúhelník otočený o 60°",
            "colour": colour,
            "correct_idx": 0,
            "make_fn": make,
            "target_fn": target,
        }

    def _build_round_3(self):
        """Isosceles trapezoid 25° rotation."""
        colour = self.C_CYAN

        def iso_trap(cx, cy):
            # top=30 half-width, bottom=70 half-width, height=45
            return [(cx - 30, cy - 22), (cx + 30, cy - 22),
                    (cx + 55, cy + 23), (cx - 55, cy + 23)]

        def target(cx, cy):
            return self._rotate_pts(iso_trap(cx, cy), cx, cy, 25)

        def right_trap(cx, cy):
            return [(cx - 30, cy - 25), (cx + 30, cy - 25),
                    (cx + 55, cy + 25), (cx - 30, cy + 25)]

        def parallelogram(cx, cy):
            return [(cx - 35, cy + 20), (cx + 15, cy - 20),
                    (cx + 50, cy - 20), (cx, cy + 20)]

        def rectangle(cx, cy):
            return [(cx - 40, cy - 22), (cx + 40, cy - 22),
                    (cx + 40, cy + 22), (cx - 40, cy + 22)]

        def make(cx, cy):
            return [
                # 0 correct: iso trapezoid 25°
                target(cx, cy),
                # 1 iso trap -25°
                self._rotate_pts(iso_trap(cx, cy), cx, cy, -25),
                # 2 iso trap 0°
                iso_trap(cx, cy),
                # 3 iso trap 45°
                self._rotate_pts(iso_trap(cx, cy), cx, cy, 45),
                # 4 iso trap 90°
                self._rotate_pts(iso_trap(cx, cy), cx, cy, 90),
                # 5 right trapezoid 25°
                self._rotate_pts(right_trap(cx, cy), cx, cy, 25),
                # 6 iso trap 0.8x
                self._scale_pts(self._rotate_pts(iso_trap(cx, cy), cx, cy, 25), cx, cy, 0.8),
                # 7 iso trap 1.3x
                self._scale_pts(self._rotate_pts(iso_trap(cx, cy), cx, cy, 25), cx, cy, 1.3),
                # 8 iso trap skewed
                self._stretch_pts(self._rotate_pts(iso_trap(cx, cy), cx, cy, 25), cx, cy, 0.85, 1.2),
                # 9 parallelogram 25°
                self._rotate_pts(parallelogram(cx, cy), cx, cy, 25),
                # 10 rectangle 25°
                self._rotate_pts(rectangle(cx, cy), cx, cy, 25),
                # 11 irregular quad
                self._rotate_pts([(cx - 40, cy - 15), (cx + 25, cy - 30),
                                  (cx + 45, cy + 10), (cx - 20, cy + 30)], cx, cy, 25),
            ]

        return {
            "title": "KOLO 3/3 – EXTRÉMNÍ VÝZVA",
            "subtitle": "Najdi přesný rovnoramenný lichoběžník otočený o 25°",
            "colour": colour,
            "correct_idx": 0,
            "make_fn": make,
            "target_fn": target,
        }

    # ------------------------------------------------------------------
    # ROUND MANAGEMENT
    # ------------------------------------------------------------------
    def _prepare_round(self):
        """Shuffle option order for current round and reset timer."""
        rd = self.rounds[self.current_round]
        # Build index map: positions 0-11, then shuffle, record where correct ended up
        order = list(range(12))
        random.shuffle(order)
        rd["order"] = order
        # correct answer grid index
        rd["answer_pos"] = order.index(rd["correct_idx"])
        self.frame_timer = 0
        self.feedback_timer = 0

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if self.won or self.lost:
            return
        if self.feedback_timer > 0:
            return  # ignore clicks during flash

        if event.type == pygame.MOUSEMOTION:
            self.hover_idx = self._cell_at(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = self._cell_at(event.pos)
            if idx < 0:
                return
            rd = self.rounds[self.current_round]
            picked_shape_idx = rd["order"][idx]
            if picked_shape_idx == rd["correct_idx"]:
                self.correct_count += 1
                self.last_correct = True
            else:
                self.last_correct = False
            self.feedback_timer = 60  # 1 second flash

    def _cell_at(self, pos):
        """Return 0-11 grid index or -1."""
        mx, my = pos
        ox = (SCREEN_WIDTH - self.GRID_COLS * self.CELL_W) // 2
        oy = 480
        col = (mx - ox) // self.CELL_W
        row = (my - oy) // self.CELL_H
        if 0 <= col < self.GRID_COLS and 0 <= row < self.GRID_ROWS:
            return row * self.GRID_COLS + col
        return -1

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update(self):
        if self.won or self.lost:
            return

        # feedback flash countdown
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer == 0:
                self._advance_round()
            return

        self.frame_timer += 1
        limit = self.ROUND_FRAMES[self.current_round]
        if self.frame_timer >= limit:
            # time ran out – counts as wrong
            self.last_correct = False
            self.feedback_timer = 60

    def _advance_round(self):
        self.current_round += 1
        if self.current_round >= self.TOTAL_ROUNDS:
            if self.correct_count >= 2:
                self.won = True
            else:
                self.lost = True
        else:
            self._prepare_round()

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------
    def draw(self, screen):
        screen.fill((10, 12, 28))

        if self.won or self.lost:
            self._draw_end_screen(screen)
            return

        rd = self.rounds[self.current_round]
        colour = rd["colour"]

        # --- header ---
        t = FONT_MEDIUM.render("ROZPOZNEJ TVAR – HARD", True, CYAN)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 10))

        rt = FONT_SMALL.render(rd["title"], True, YELLOW)
        screen.blit(rt, (SCREEN_WIDTH // 2 - rt.get_width() // 2, 65))

        sub = FONT_TINY.render(rd["subtitle"], True, LIGHT_GRAY)
        screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 100))

        # score + timer
        secs_left = max(0, (self.ROUND_FRAMES[self.current_round] - self.frame_timer) // 60)
        info = FONT_SMALL.render(
            f"Skóre: {self.correct_count}/{self.current_round}  |  ⏱ 0:{secs_left:02d}", True, WHITE)
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 130))

        # --- target shape (large, centred) ---
        target_cx = SCREEN_WIDTH // 2
        target_cy = 280
        target_pts = rd["target_fn"](target_cx, target_cy)
        # scale up target for visibility
        target_pts = self._scale_pts(target_pts, target_cx, target_cy, 1.6)
        self._draw_poly(screen, target_pts, colour)
        # label
        lbl = FONT_TINY.render("▶ CÍLOVÝ TVAR ◀", True, WHITE)
        screen.blit(lbl, (SCREEN_WIDTH // 2 - lbl.get_width() // 2, 355))

        # --- border around target area ---
        pygame.draw.rect(screen, colour,
                         (SCREEN_WIDTH // 2 - 160, 195, 320, 175), 2)

        # --- option grid ---
        ox = (SCREEN_WIDTH - self.GRID_COLS * self.CELL_W) // 2
        oy = 480

        for i in range(12):
            col = i % self.GRID_COLS
            row = i // self.GRID_COLS
            rx = ox + col * self.CELL_W
            ry = oy + row * self.CELL_H
            rect = pygame.Rect(rx, ry, self.CELL_W - 6, self.CELL_H - 6)

            # bg
            bg = self.C_CELL_HL if i == self.hover_idx else self.C_CELL_BG
            # feedback overlay
            if self.feedback_timer > 0:
                shape_idx = rd["order"][i]
                if shape_idx == rd["correct_idx"]:
                    bg = self.C_CORRECT_BG
                elif i == self.hover_idx and not self.last_correct:
                    bg = self.C_WRONG_BG

            pygame.draw.rect(screen, bg, rect, border_radius=6)
            pygame.draw.rect(screen, (80, 85, 110), rect, 2, border_radius=6)

            # draw shape
            ccx = rx + self.CELL_W // 2 - 3
            ccy = ry + self.CELL_H // 2 - 3
            shape_idx = rd["order"][i]
            pts = rd["make_fn"](ccx, ccy)[shape_idx]
            self._draw_poly(screen, pts, colour)

            # number label
            num = FONT_TINY.render(str(i + 1), True, GRAY)
            screen.blit(num, (rx + 6, ry + 4))

        # --- instructions ---
        ins = FONT_TINY.render("Klikni na tvar, který přesně odpovídá cílovému tvaru nahoře!", True, LIGHT_GRAY)
        screen.blit(ins, (SCREEN_WIDTH // 2 - ins.get_width() // 2, SCREEN_HEIGHT - 30))

    def _draw_end_screen(self, screen):
        if self.won:
            t = FONT_LARGE.render("LEVEL COMPLETE!", True, GREEN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        else:
            t = FONT_LARGE.render("GAME OVER", True, RED)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 80))

        sc = FONT_MEDIUM.render(f"Správně: {self.correct_count} / {self.TOTAL_ROUNDS}", True, WHITE)
        screen.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        if self.won:
            msg = FONT_SMALL.render("Výborně! Tvůj zrak je ostrý.", True, YELLOW)
        else:
            msg = FONT_SMALL.render("Potřebuješ alespoň 2 ze 3 správně.", True, LIGHT_GRAY)
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

    def get_hint(self):
        if self.current_round == 0:
            return "Hledej pětiúhelník otočený přesně o 30° – pozor na šestiúhelníky a hvězdy!"
        elif self.current_round == 1:
            return "Nerovnostranný trojúhelník má 3 různé strany. Otočení 60° – ne -60°!"
        else:
            return "Lichoběžník: 2 rovnoběžné strany, rovnoramenný, otočený 25°. Pozor na rovnoběžníky!"


class LaserMirrors(BaseGame):
    """Laser Reflection Puzzle – nasměruj laser na cíl otáčením zrcadel na mřížce.
    Advanced version with portals, 14 mirrors, and a winding 10-bounce solution."""

    # Grid dimensions and cell size
    G_COLS = 12
    G_ROWS = 10
    CELL = 56

    # Directions: RIGHT, DOWN, LEFT, UP  (dx, dy)
    DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def __init__(self):
        super().__init__()

        # Cursor position (grid coords)
        self.cx = 6
        self.cy = 5

        # ====== PUZZLE LAYOUT (12 cols × 10 rows) ======
        #
        #      0  1  2  3  4  5  6  7  8  9  10 11
        #  0   .  .  B  .  .  .  B  .  .  B  .  .
        #  1  L→ .  .  .  M1 .  .  M4 .  .  M5 .
        #  2   .  .  B  .  .  .  B  .  D2 .  .  .
        #  3   .  .  D1 B  .  .  B  .  .  B  .  D5
        #  4   .  B  .  .  M2 .  .  M3 .  .  P→ .
        #  5   .  .  .  B  .  .  .  .  B  .  .  .
        #  6   B  .  .  D4 .  M8 .  .  .  .  .  T
        #  7   .  P← .  B  .  .  B  B  .  D3 .  .
        #  8   B  .  .  B  .  .  D6 .  B  .  .  .
        #  9   .  M6 .  .  .  M7 .  .  .  B  .  B
        #
        # L = Laser emitter (RIGHT)   T = Target
        # Mx = Solution mirror (8)     Dx = Decoy mirror (6)
        # B = Wall    P = Portal pair (beam teleports, same direction)
        #
        # SOLUTION (rotate ALL 8 solution mirrors):
        #   (0,1)→→→(4,1)[M1\]↓↓(4,4)[M2\]→→(7,4)[M3/]
        #   ↑↑(7,1)[M4/]→→(10,1)[M5\]↓↓(10,4)[Portal]
        #   ~~>(1,7)[Portal]↓(1,9)[M6\]→→→(5,9)[M7/]
        #   ↑↑(5,6)[M8/]→→→→→(11,6) TARGET!

        # Laser emitter: left edge, row 1, shoots RIGHT
        self.emitter = (0, 1)
        self.emit_dir = 0                # index into DIRS → RIGHT

        # Target: right edge, row 6
        self.target = (11, 6)

        # Grid: None = empty, "block" = wall, dict = mirror/portal
        self.grid = [[None] * self.G_COLS for _ in range(self.G_ROWS)]

        # --- Fixed walls / obstacles (20 blocks) ---
        walls = [
            (2, 0), (6, 0), (9, 0),
            (2, 2), (6, 2),
            (3, 3), (6, 3), (9, 3),
            (1, 4),
            (3, 5), (8, 5),
            (0, 6),
            (3, 7), (6, 7), (7, 7),
            (0, 8), (3, 8), (8, 8),
            (9, 9), (11, 9),
        ]
        for wx, wy in walls:
            self.grid[wy][wx] = "block"

        # --- Portal pair (beam enters one, exits the other, same direction) ---
        self.grid[4][10] = {"type": "portal", "pair": (1, 7), "id": "A"}
        self.grid[7][1]  = {"type": "portal", "pair": (10, 4), "id": "A"}

        # --- Solution mirrors (ALL start in the WRONG orientation) ---
        solution_mirrors = [
            (4,  1, "/"),     # M1 – needs "\"   (RIGHT→DOWN)
            (4,  4, "/"),     # M2 – needs "\"   (DOWN→RIGHT)
            (7,  4, "\\"),    # M3 – needs "/"   (RIGHT→UP)
            (7,  1, "\\"),    # M4 – needs "/"   (UP→RIGHT)
            (10, 1, "/"),     # M5 – needs "\"   (RIGHT→DOWN)
            (1,  9, "/"),     # M6 – needs "\"   (DOWN→RIGHT)
            (5,  9, "\\"),    # M7 – needs "/"   (RIGHT→UP)
            (5,  6, "\\"),    # M8 – needs "/"   (UP→RIGHT)
        ]
        # --- Decoy mirrors (red herrings – off the solution path) ---
        decoy_mirrors = [
            (2,  3, "/"),     # D1
            (8,  2, "\\"),    # D2
            (9,  7, "/"),     # D3
            (3,  6, "\\"),    # D4
            (11, 3, "/"),     # D5
            (6,  8, "\\"),    # D6
        ]
        for mx, my, angle in solution_mirrors + decoy_mirrors:
            self.grid[my][mx] = {"type": "mirror", "angle": angle}

        # Precompute laser path
        self.laser_path = []
        self.hit_target = False
        self._trace_laser()

    # ------------------------------------------------------------------
    #  LASER TRACING
    # ------------------------------------------------------------------
    def _reflect(self, dir_idx, angle):
        """Return new direction index after hitting a mirror of given angle."""
        if angle == "/":
            #  RIGHT(0)→UP(3), DOWN(1)→LEFT(2), LEFT(2)→DOWN(1), UP(3)→RIGHT(0)
            return [3, 2, 1, 0][dir_idx]
        else:  # "\\"
            #  RIGHT(0)→DOWN(1), DOWN(1)→RIGHT(0), LEFT(2)→UP(3), UP(3)→LEFT(2)
            return [1, 0, 3, 2][dir_idx]

    def _trace_laser(self):
        """Trace the laser beam from the emitter through the grid."""
        self.laser_path = []
        self.hit_target = False

        x, y = self.emitter
        d = self.emit_dir
        visited = set()

        for _ in range(300):  # safety limit
            state = (x, y, d)
            if state in visited:
                break  # infinite loop detected
            visited.add(state)

            self.laser_path.append((x, y))

            # Check if we reached the target
            if (x, y) == self.target:
                self.hit_target = True
                break

            # Check what's in this cell
            cell = self.grid[y][x]
            if cell == "block":
                break  # absorbed by wall

            if isinstance(cell, dict):
                if cell["type"] == "mirror":
                    d = self._reflect(d, cell["angle"])
                elif cell["type"] == "portal":
                    # Teleport to paired portal, keep same direction
                    px, py = cell["pair"]
                    self.laser_path.append((px, py))
                    x, y = px, py
                    dx, dy = self.DIRS[d]
                    nx, ny = x + dx, y + dy
                    if nx < 0 or nx >= self.G_COLS or ny < 0 or ny >= self.G_ROWS:
                        break
                    x, y = nx, ny
                    continue

            # Move to next cell
            dx, dy = self.DIRS[d]
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= self.G_COLS or ny < 0 or ny >= self.G_ROWS:
                break  # left the grid
            x, y = nx, ny

        if self.hit_target:
            self.won = True

    # ------------------------------------------------------------------
    #  INPUT
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.won:
            return

        # Cursor movement
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.cx = max(0, self.cx - 1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.cx = min(self.G_COLS - 1, self.cx + 1)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.cy = max(0, self.cy - 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.cy = min(self.G_ROWS - 1, self.cy + 1)

        # Rotate mirror under cursor (R only)
        elif event.key == pygame.K_r:
            cell = self.grid[self.cy][self.cx]
            if isinstance(cell, dict) and cell["type"] == "mirror":
                cell["angle"] = "\\" if cell["angle"] == "/" else "/"
                self._trace_laser()

    # ------------------------------------------------------------------
    #  DRAWING
    # ------------------------------------------------------------------
    def draw(self, screen):
        screen.fill((10, 10, 25))

        # Origin so the grid is centred
        ox = (SCREEN_WIDTH - self.G_COLS * self.CELL) // 2
        oy = (SCREEN_HEIGHT - self.G_ROWS * self.CELL) // 2

        # --- draw grid cells ---
        for gy in range(self.G_ROWS):
            for gx in range(self.G_COLS):
                rx = ox + gx * self.CELL
                ry = oy + gy * self.CELL
                rect = pygame.Rect(rx, ry, self.CELL, self.CELL)

                cell = self.grid[gy][gx]

                if cell == "block":
                    pygame.draw.rect(screen, (80, 80, 100), rect)
                    pygame.draw.rect(screen, (120, 120, 140), rect, 2)
                else:
                    pygame.draw.rect(screen, (25, 25, 45), rect)
                    pygame.draw.rect(screen, (45, 45, 65), rect, 1)

                # Mirror
                if isinstance(cell, dict) and cell["type"] == "mirror":
                    pad = 8
                    if cell["angle"] == "/":
                        pygame.draw.line(screen, YELLOW,
                                         (rx + pad, ry + self.CELL - pad),
                                         (rx + self.CELL - pad, ry + pad), 4)
                    else:
                        pygame.draw.line(screen, YELLOW,
                                         (rx + pad, ry + pad),
                                         (rx + self.CELL - pad, ry + self.CELL - pad), 4)

                # Portal
                if isinstance(cell, dict) and cell["type"] == "portal":
                    cx_p = rx + self.CELL // 2
                    cy_p = ry + self.CELL // 2
                    pygame.draw.circle(screen, (180, 0, 255), (cx_p, cy_p),
                                       self.CELL // 3, 3)
                    pygame.draw.circle(screen, (220, 100, 255), (cx_p, cy_p),
                                       self.CELL // 5)
                    lbl = FONT_TINY.render("P", True, WHITE)
                    screen.blit(lbl, (cx_p - lbl.get_width() // 2,
                                      cy_p - lbl.get_height() // 2))

        # --- emitter ---
        ex = ox + self.emitter[0] * self.CELL + self.CELL // 2
        ey = oy + self.emitter[1] * self.CELL + self.CELL // 2
        pygame.draw.circle(screen, GREEN, (ex, ey), 14)
        lbl = FONT_TINY.render("L", True, BLACK)
        screen.blit(lbl, (ex - lbl.get_width() // 2, ey - lbl.get_height() // 2))

        # --- target ---
        tx = ox + self.target[0] * self.CELL + self.CELL // 2
        ty = oy + self.target[1] * self.CELL + self.CELL // 2
        pygame.draw.circle(screen, RED, (tx, ty), 14)
        lbl = FONT_TINY.render("T", True, WHITE)
        screen.blit(lbl, (tx - lbl.get_width() // 2, ty - lbl.get_height() // 2))

        # --- laser beam ---
        beam_color = (0, 255, 100) if self.hit_target else (0, 200, 255)
        glow_color = (100, 255, 180) if self.hit_target else (120, 230, 255)
        for i in range(len(self.laser_path) - 1):
            ax, ay = self.laser_path[i]
            bx, by = self.laser_path[i + 1]
            # Skip drawing across portal jumps (non-adjacent cells)
            if abs(ax - bx) + abs(ay - by) > 1:
                continue
            p1 = (ox + ax * self.CELL + self.CELL // 2,
                  oy + ay * self.CELL + self.CELL // 2)
            p2 = (ox + bx * self.CELL + self.CELL // 2,
                  oy + by * self.CELL + self.CELL // 2)
            pygame.draw.line(screen, beam_color, p1, p2, 4)
            pygame.draw.line(screen, glow_color, p1, p2, 2)

        # --- cursor highlight ---
        cur_rect = pygame.Rect(ox + self.cx * self.CELL, oy + self.cy * self.CELL,
                               self.CELL, self.CELL)
        pygame.draw.rect(screen, WHITE, cur_rect, 3)

        # --- title ---
        title = FONT_MEDIUM.render("LASER REFLECTION", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        # --- info bar ---
        mirror_count = sum(1 for row in self.grid for c in row
                           if isinstance(c, dict) and c.get("type") == "mirror")
        info = FONT_TINY.render(
            f"ZRCADEL: {mirror_count}  |  PORTÁLY: 1 pár", True, (180, 180, 200))
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 60))

        # --- instructions ---
        instr = FONT_TINY.render(
            "ŠIPKY/WASD = pohyb  |  R = otočit zrcadlo  |  "
            "Nasměruj laser přes portály na cíl!", True, LIGHT_GRAY)
        screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, SCREEN_HEIGHT - 40))

        # --- win overlay ---
        if self.won:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render("LASER NA CÍLI!", True, GREEN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))

    def get_hint(self):
        return "Otoč SPRÁVNÁ zrcadla a nasměruj laser přes portály na cíl. Pozor – některá zrcadla jsou návnady!"


class FindDifferences(BaseGame):
    """Najdi rozdíly - klikej na rozdíly mezi dvěma obrázky"""
    def __init__(self):
        super().__init__()
        self.differences = [
            {"pos": (400, 300), "radius": 20},
            {"pos": (800, 450), "radius": 15},
            {"pos": (650, 250), "radius": 18},
            {"pos": (550, 500), "radius": 12},
            {"pos": (900, 200), "radius": 16}
        ]
        self.found = [False] * len(self.differences)
        self.total_differences = len(self.differences)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i, diff in enumerate(self.differences):
                if self.distance(pos, diff["pos"]) < diff["radius"] + 10:
                    self.found[i] = True
            
            if all(self.found):
                self.won = True
    
    def distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("NAJDI ROZDÍLY", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 20))
        
        progress = FONT_MEDIUM.render(f"NALEZENO: {sum(self.found)}/{self.total_differences}", True, YELLOW)
        screen.blit(progress, (SCREEN_WIDTH//2 - 150, 100))
        
        left_text = FONT_SMALL.render("VLEVO", True, WHITE)
        right_text = FONT_SMALL.render("VPRAVO", True, WHITE)
        screen.blit(left_text, (300, 180))
        screen.blit(right_text, (1300, 180))
        
        pygame.draw.rect(screen, BLUE, pygame.Rect(150, 220, 350, 500))
        pygame.draw.rect(screen, BLUE, pygame.Rect(1420, 220, 350, 500))
        
        for i, diff in enumerate(self.differences):
            if not self.found[i]:
                pygame.draw.circle(screen, RED, diff["pos"], diff["radius"])
                pygame.draw.circle(screen, RED, (diff["pos"][0] + 1220, diff["pos"][1]), diff["radius"])
            else:
                pygame.draw.circle(screen, GREEN, diff["pos"], diff["radius"])
                pygame.draw.circle(screen, GREEN, (diff["pos"][0] + 1220, diff["pos"][1]), diff["radius"])
        
        instr = FONT_SMALL.render("Klikni na všechny rozdíly v obrázku vpravo", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 300, 800))
    
    def get_hint(self):
        found_count = sum(self.found)
        remaining = self.total_differences - found_count
        return f"Zbývá najít {remaining} rozdílů"


class ColorMatch(BaseGame):
    """Click the correct color - can spawn multiple circles, difficulty increases"""
    def __init__(self):
        super().__init__()
        self.colors = [RED, GREEN, BLUE, YELLOW, CYAN]
        self.color_names = {RED: "RED", GREEN: "GREEN", BLUE: "BLUE", YELLOW: "YELLOW", CYAN: "CYAN"}
        self.target_color = random.choice(self.colors)
        self.target_name = self.color_names[self.target_color]
        self.objects = []
        self.score = 0
        self.lives = 3
        self.timer = 0
        self.spawn_timer = 0
        self.spawn_rate = 20  # Faster spawning
        self.round_timer = 0
        self.round_time = 1800  # 30 seconds
        self.generate_objects()
    
    def generate_objects(self):
        """Generate random colored objects moving in all directions - difficulty increases over time"""
        # Increase difficulty as time goes on
        difficulty_multiplier = 1 + (self.round_timer / self.round_time) * 0.5
        current_spawn_rate = int(self.spawn_rate / difficulty_multiplier)
        
        if self.spawn_timer <= 0:
            color = random.choice(self.colors)
            x = random.randint(200, SCREEN_WIDTH - 200)
            y = random.randint(250, SCREEN_HEIGHT - 150)
            size = random.randint(40, 80)
            lifetime = 120
            # Random direction and angle (0-360°)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 4.0) * difficulty_multiplier
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            self.objects.append({"x": x, "y": y, "size": size, "color": color, "lifetime": lifetime, "vx": vx, "vy": vy})
            self.spawn_timer = current_spawn_rate
        self.spawn_timer -= 1
        
        # Move objects and bounce off walls
        for obj in self.objects:
            obj["x"] += obj["vx"]
            obj["y"] += obj["vy"]
            # Bounce off walls
            if obj["x"] - obj["size"] < 0 or obj["x"] + obj["size"] > SCREEN_WIDTH:
                obj["vx"] *= -1
                obj["x"] = max(obj["size"], min(SCREEN_WIDTH - obj["size"], obj["x"]))
            if obj["y"] - obj["size"] < 100 or obj["y"] + obj["size"] > SCREEN_HEIGHT - 150:
                obj["vy"] *= -1
                obj["y"] = max(100 + obj["size"], min(SCREEN_HEIGHT - 150 - obj["size"], obj["y"]))
        
        # Remove "dead" objects
        self.objects = [o for o in self.objects if o["lifetime"] > 0]
        for obj in self.objects:
            obj["lifetime"] -= 1
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            clicked = False
            for obj in self.objects[:]:
                dist = math.sqrt((obj["x"] - pos[0])**2 + (obj["y"] - pos[1])**2)
                if dist < obj["size"]:
                    clicked = True
                    if obj["color"] == self.target_color:
                        self.score += 1
                    else:
                        self.lives -= 1
                    self.objects.remove(obj)
                    break
            
            if self.lives <= 0:
                self.lost = True
    
    def update(self):
        self.generate_objects()
        self.timer += 1
        self.round_timer += 1
        
        if self.round_timer > self.round_time:
            if self.score > 5:
                self.won = True
            else:
                self.lost = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("COLOR MATCH", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 180, 20))
        
        target_text = FONT_LARGE.render(f"CLICK {self.target_name}", True, self.target_color)
        screen.blit(target_text, (SCREEN_WIDTH//2 - 280, 100))
        
        # Objects - filled circles
        for obj in self.objects:
            pygame.draw.circle(screen, obj["color"], (int(obj["x"]), int(obj["y"])), obj["size"])
            pygame.draw.circle(screen, WHITE, (int(obj["x"]), int(obj["y"])), obj["size"], 3)
        
        # Score and lives
        score_text = FONT_MEDIUM.render(f"Score: {self.score}", True, GREEN)
        lives_text = FONT_MEDIUM.render(f"Lives: {self.lives}", True, RED)
        screen.blit(score_text, (50, 50))
        screen.blit(lives_text, (SCREEN_WIDTH - 250, 50))
        
        time_left = max(0, (self.round_time - self.round_timer) // 60)
        time_text = FONT_SMALL.render(f"Time: {time_left}s", True, YELLOW)
        screen.blit(time_text, (SCREEN_WIDTH//2 - 80, 150))
    
    def get_hint(self):
        return f"Click on {self.target_name} circles - avoid others! Get 6+ points to win!"


class PipeRotate(BaseGame):
    """
    Pipe Puzzle – 8×8 grid.  Rotate pipes so a continuous path connects
    the green START node to the red END node.
    Left-click = rotate clockwise 90°.  Right-click = rotate counter-clockwise.
    Locked pipes (shown with a padlock dot) cannot be rotated.
    """

    # Each pipe type lists its base openings as a frozenset of sides.
    # Sides: 0=RIGHT  1=DOWN  2=LEFT  3=UP
    PIPE_DEFS = {
        "straight": frozenset([0, 2]),       # ─  horizontal
        "curve":    frozenset([0, 1]),        # ╮  L-shape (right+down)
        "t_junc":   frozenset([0, 1, 2]),    # ┬  T-shape
        "cross":    frozenset([0, 1, 2, 3]), # ┼  4-way
        "dead":     frozenset([0]),           # ╶  dead-end (one opening)
    }

    OPPOSITE = {0: 2, 1: 3, 2: 0, 3: 1}
    DIR_DELTA = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}  # (dx, dy)

    GRID_COLS = 8
    GRID_ROWS = 8
    CELL = 80

    def __init__(self):
        super().__init__()
        self.moves = 0
        self.start = (0, 0)       # (col, row)
        self.end   = (7, 7)

        # Build a guaranteed-solvable puzzle
        self.grid = [[None] * self.GRID_COLS for _ in range(self.GRID_ROWS)]
        self._build_puzzle()

    # ------------------------------------------------------------------
    #  PUZZLE BUILDER – lay out a solution path, fill extras, scramble
    # ------------------------------------------------------------------
    def _build_puzzle(self):
        """
        1. Carve a random path from START to END (DFS on the grid).
        2. Assign pipe types that match the path's shape.
        3. Fill remaining empty cells with random pipes.
        4. Lock a few pipes on the solution path as hints.
        5. Scramble every unlocked pipe rotation so the player has work to do.
        """
        path = self._random_path(self.start, self.end)

        # --- assign pipe types & correct rotations along the path ---
        for idx, (cx, cy) in enumerate(path):
            needed = set()                       # sides that must be open
            if idx > 0:
                px, py = path[idx - 1]
                needed.add(self._side_towards(cx, cy, px, py))
            if idx < len(path) - 1:
                nx, ny = path[idx + 1]
                needed.add(self._side_towards(cx, cy, nx, ny))

            pipe_type, rotation = self._best_pipe(needed)
            self.grid[cy][cx] = {
                "type": pipe_type,
                "rot": rotation,
                "locked": False,
            }

        # --- fill remaining cells with random pipes ---
        types_pool = ["straight", "curve", "t_junc", "dead"]
        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_COLS):
                if self.grid[r][c] is None:
                    self.grid[r][c] = {
                        "type": random.choice(types_pool),
                        "rot": random.randint(0, 3),
                        "locked": False,
                    }

        # --- lock 5 pipes on the path as hints (always lock start & end) ---
        lock_indices = {0, len(path) - 1}
        mid_indices = list(range(1, len(path) - 1))
        random.shuffle(mid_indices)
        for li in mid_indices[:3]:
            lock_indices.add(li)
        for li in lock_indices:
            cx, cy = path[li]
            self.grid[cy][cx]["locked"] = True

        # --- scramble unlocked pipes ---
        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_COLS):
                cell = self.grid[r][c]
                if not cell["locked"]:
                    cell["rot"] = random.randint(0, 3)

    # ---- path utilities ---------------------------------------------------
    def _random_path(self, start, end):
        """DFS-based random walk from start to end, visiting cells at most once."""
        sx, sy = start
        ex, ey = end
        visited = set()
        visited.add((sx, sy))
        path = [(sx, sy)]

        def dfs(x, y):
            if (x, y) == (ex, ey):
                return True
            neighbours = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            random.shuffle(neighbours)
            for nx, ny in neighbours:
                if 0 <= nx < self.GRID_COLS and 0 <= ny < self.GRID_ROWS and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    path.append((nx, ny))
                    if dfs(nx, ny):
                        return True
                    path.pop()
                    visited.discard((nx, ny))
            return False

        dfs(sx, sy)
        return path

    @staticmethod
    def _side_towards(cx, cy, tx, ty):
        """Return the side index of (cx,cy) that faces (tx,ty)."""
        dx, dy = tx - cx, ty - cy
        if dx == 1:  return 0   # RIGHT
        if dy == 1:  return 1   # DOWN
        if dx == -1: return 2   # LEFT
        return 3                # UP

    def _best_pipe(self, needed_sides):
        """
        Choose the simplest pipe type whose base openings can be rotated
        to cover *exactly* the needed_sides set.  Returns (type, rotation).
        """
        # Try types from simplest to most complex
        preference = ["dead", "straight", "curve", "t_junc", "cross"]
        for ptype in preference:
            base = self.PIPE_DEFS[ptype]
            for rot in range(4):
                rotated = frozenset((s + rot) % 4 for s in base)
                if needed_sides <= rotated and len(rotated) - len(needed_sides) <= 1:
                    return ptype, rot
        # fallback: cross always works
        return "cross", 0

    # ------------------------------------------------------------------
    #  OPENINGS HELPER
    # ------------------------------------------------------------------
    def _openings(self, cell):
        """Return set of open sides for a cell dict."""
        base = self.PIPE_DEFS.get(cell["type"], frozenset())
        return frozenset((s + cell["rot"]) % 4 for s in base)

    # ------------------------------------------------------------------
    #  PATH VALIDATION (BFS)
    # ------------------------------------------------------------------
    def _find_connected_path(self):
        """BFS from START.  Returns the set of connected cells and whether END is reached."""
        sx, sy = self.start
        visited = set()
        queue = deque([(sx, sy)])
        visited.add((sx, sy))

        while queue:
            x, y = queue.popleft()
            cell = self.grid[y][x]
            for side in self._openings(cell):
                dx, dy = self.DIR_DELTA[side]
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.GRID_COLS and 0 <= ny < self.GRID_ROWS and (nx, ny) not in visited:
                    neighbour = self.grid[ny][nx]
                    if self.OPPOSITE[side] in self._openings(neighbour):
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        return visited, self.end in visited

    # ------------------------------------------------------------------
    #  INPUT
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if self.won:
            return
        if event.type not in (pygame.MOUSEBUTTONDOWN,):
            return

        mx, my = event.pos
        ox = (SCREEN_WIDTH - self.GRID_COLS * self.CELL) // 2
        oy = (SCREEN_HEIGHT - self.GRID_ROWS * self.CELL) // 2

        col = (mx - ox) // self.CELL
        row = (my - oy) // self.CELL
        if not (0 <= col < self.GRID_COLS and 0 <= row < self.GRID_ROWS):
            return

        cell = self.grid[row][col]
        if cell["locked"]:
            return

        # Left-click → clockwise, Right-click → counter-clockwise
        if event.button == 1:
            cell["rot"] = (cell["rot"] + 1) % 4
        elif event.button == 3:
            cell["rot"] = (cell["rot"] - 1) % 4
        else:
            return

        self.moves += 1

        # Check win
        _, reached = self._find_connected_path()
        if reached:
            self.won = True

    # ------------------------------------------------------------------
    #  DRAWING HELPERS
    # ------------------------------------------------------------------
    def _draw_pipe(self, screen, rx, ry, cell, color):
        """Draw the pipe shape inside the cell rect (rx, ry)."""
        cx = rx + self.CELL // 2
        cy = ry + self.CELL // 2
        half = self.CELL // 2 - 6
        thick = 10

        openings = self._openings(cell)
        # Draw a line from centre to each open side
        ends = {
            0: (cx + half, cy),
            1: (cx, cy + half),
            2: (cx - half, cy),
            3: (cx, cy - half),
        }
        for side in openings:
            ex, ey = ends[side]
            pygame.draw.line(screen, color, (cx, cy), (ex, ey), thick)

        # Draw a circle at centre junction
        pygame.draw.circle(screen, color, (cx, cy), thick // 2 + 2)

    # ------------------------------------------------------------------
    #  DRAW
    # ------------------------------------------------------------------
    def draw(self, screen):
        screen.fill((10, 12, 28))

        ox = (SCREEN_WIDTH - self.GRID_COLS * self.CELL) // 2
        oy = (SCREEN_HEIGHT - self.GRID_ROWS * self.CELL) // 2

        # Validation data
        connected, goal_reached = self._find_connected_path()

        # --- grid cells ---
        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_COLS):
                rx = ox + c * self.CELL
                ry = oy + r * self.CELL
                rect = pygame.Rect(rx, ry, self.CELL, self.CELL)
                cell = self.grid[r][c]

                # BG
                bg = (30, 32, 50) if not cell["locked"] else (45, 40, 55)
                pygame.draw.rect(screen, bg, rect)
                pygame.draw.rect(screen, (55, 58, 80), rect, 1)

                # Pipe colour: green if connected, yellow otherwise
                pipe_col = (0, 220, 100) if (c, r) in connected else (200, 200, 60)
                self._draw_pipe(screen, rx, ry, cell, pipe_col)

                # Lock indicator (small white dot)
                if cell["locked"]:
                    pygame.draw.circle(screen, WHITE, (rx + self.CELL - 12, ry + 12), 5)

        # --- start & end markers ---
        sx = ox + self.start[0] * self.CELL + self.CELL // 2
        sy = oy + self.start[1] * self.CELL + self.CELL // 2
        pygame.draw.circle(screen, GREEN, (sx, sy), 14)
        lbl = FONT_TINY.render("S", True, BLACK)
        screen.blit(lbl, (sx - lbl.get_width() // 2, sy - lbl.get_height() // 2))

        ex_px = ox + self.end[0] * self.CELL + self.CELL // 2
        ey_px = oy + self.end[1] * self.CELL + self.CELL // 2
        pygame.draw.circle(screen, RED, (ex_px, ey_px), 14)
        lbl = FONT_TINY.render("E", True, WHITE)
        screen.blit(lbl, (ex_px - lbl.get_width() // 2, ey_px - lbl.get_height() // 2))

        # --- grid border ---
        pygame.draw.rect(screen, CYAN, (ox - 2, oy - 2,
                                        self.GRID_COLS * self.CELL + 4,
                                        self.GRID_ROWS * self.CELL + 4), 2)

        # --- title ---
        t = FONT_MEDIUM.render("PIPE PUZZLE", True, CYAN)
        screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 15))

        # --- HUD: moves ---
        mv = FONT_SMALL.render(f"Tahy: {self.moves}", True, YELLOW)
        screen.blit(mv, (ox, oy - 40))

        # --- status ---
        if goal_reached:
            st = FONT_SMALL.render("SPOJENO!", True, GREEN)
        else:
            st = FONT_SMALL.render(f"Propojeno: {len(connected)} políček", True, LIGHT_GRAY)
        screen.blit(st, (ox + self.GRID_COLS * self.CELL - st.get_width(), oy - 40))

        # --- instructions ---
        instr = FONT_TINY.render("Levé kliknutí = otočit CW | Pravé kliknutí = otočit CCW | "
                                 "Bílá tečka = zamčené", True, LIGHT_GRAY)
        screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, SCREEN_HEIGHT - 35))

        # --- win overlay ---
        if self.won:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            w = FONT_LARGE.render("LEVEL COMPLETE!", True, GREEN)
            screen.blit(w, (SCREEN_WIDTH // 2 - w.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            m = FONT_SMALL.render(f"Tahy: {self.moves}", True, WHITE)
            screen.blit(m, (SCREEN_WIDTH // 2 - m.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def get_hint(self):
        return "Otáčej potrubí kliknutím – spoj zelenou S a červenou E! Zamčené trubky jsou nápověda."


class CableConnect(BaseGame):
    """Spoj barevné kabely – HARD: 6 párů, 2 návnady, zámky, 3 pokusy."""

    # 6 real colors + 2 decoy colors
    ALL_COLORS = [
        (255, 0, 0),      # 0 RED
        (0, 200, 0),      # 1 GREEN
        (0, 100, 255),    # 2 BLUE
        (255, 255, 0),    # 3 YELLOW
        (0, 255, 255),    # 4 CYAN
        (255, 0, 255),    # 5 MAGENTA
        (255, 140, 0),    # 6 ORANGE  (decoy)
        (160, 0, 255),    # 7 PURPLE  (decoy)
    ]
    ALL_NAMES = ["CERV", "ZEL", "MODR", "ZLUT", "CYAN", "MAG", "ORAN", "FIAL"]

    NUM_PAIRS = 6     # real cable pairs
    NUM_RIGHT = 8     # 6 real + 2 decoys on the right side

    def __init__(self):
        super().__init__()

        # Left side: one node per real color (indices 0-5)
        self.left_cables = list(range(self.NUM_PAIRS))

        # Right side: all 8 colours, shuffled
        self.right_cables = list(range(self.NUM_RIGHT))
        random.shuffle(self.right_cables)

        self.connections = {}   # {left_index: right_index}
        self.used_right = set()
        self.selected = None

        # Strikes
        self.max_wrong = 3
        self.wrong_count = 0

        # Lock rules: right-side colour 4 (CYAN) unlocks after colour 0 (RED) is connected,
        #             right-side colour 5 (MAG)  unlocks after colour 2 (BLUE) is connected.
        self.lock_prereqs = {4: 0, 5: 2}

        # Flash feedback
        self.flash_timer = 0
        self.flash_color = (255, 255, 255)
        self.flash_msg = ""

    # ---- helpers --------------------------------------------------------
    def _is_locked(self, right_color_id):
        if right_color_id not in self.lock_prereqs:
            return False
        prereq = self.lock_prereqs[right_color_id]
        for li in self.connections:
            if self.left_cables[li] == prereq:
                return False
        return True

    def _flash(self, msg, color, duration=60):
        self.flash_msg = msg
        self.flash_color = color
        self.flash_timer = duration

    def _strike(self, msg):
        self.wrong_count += 1
        self._flash(msg, (255, 50, 50), 70)
        if self.wrong_count >= self.max_wrong:
            self.lost = True

    # ---- connection attempt ---------------------------------------------
    def _try_connect(self, left_i, right_i):
        if left_i in self.connections or right_i in self.used_right:
            self._flash("UZ SPOJENO!", (255, 160, 0))
            return

        rc = self.right_cables[right_i]

        if self._is_locked(rc):
            self._strike("ZAMCENO! Spoj nejdriv prerequisitu.")
            return

        lc = self.left_cables[left_i]
        if lc != rc:
            self._strike("SPATNA BARVA!")
            return

        # success
        self.connections[left_i] = right_i
        self.used_right.add(right_i)
        self._flash("SPOJENO!", (0, 255, 80), 40)

        if len(self.connections) == self.NUM_PAIRS:
            self.won = True

    # ---- events ---------------------------------------------------------
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.won or self.lost:
            return

        pos = event.pos

        # Left nodes
        for i in range(self.NUM_PAIRS):
            x, y = 350, 190 + i * 100
            if pygame.Rect(x - 35, y - 35, 70, 70).collidepoint(pos):
                if i in self.connections:
                    break
                if self.selected and self.selected[0] == "right":
                    self._try_connect(i, self.selected[1])
                    self.selected = None
                else:
                    self.selected = ("left", i)
                return

        # Right nodes
        for i in range(self.NUM_RIGHT):
            x, y = SCREEN_WIDTH - 350, 155 + i * 88
            if pygame.Rect(x - 35, y - 35, 70, 70).collidepoint(pos):
                if i in self.used_right:
                    break
                if self.selected and self.selected[0] == "left":
                    self._try_connect(self.selected[1], i)
                    self.selected = None
                else:
                    self.selected = ("right", i)
                return

    def update(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1

    # ---- drawing --------------------------------------------------------
    def _node_pos_left(self, i):
        return 350, 190 + i * 100

    def _node_pos_right(self, i):
        return SCREEN_WIDTH - 350, 155 + i * 88

    def draw(self, screen):
        screen.fill(DARK_BLUE)

        title = FONT_LARGE.render("KABELY", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 15))

        # Strikes bar
        strikes = "X " * self.wrong_count + "O " * (self.max_wrong - self.wrong_count)
        sc = RED if self.wrong_count >= 2 else WHITE
        st = FONT_SMALL.render(f"Pokusy: {strikes.strip()}", True, sc)
        screen.blit(st, (SCREEN_WIDTH // 2 - st.get_width() // 2, 70))

        # -- left nodes --
        for i in range(self.NUM_PAIRS):
            x, y = self._node_pos_left(i)
            ci = self.left_cables[i]
            color = self.ALL_COLORS[ci]
            done = i in self.connections
            sel = self.selected == ("left", i)

            if done:
                dim = (color[0] // 3, color[1] // 3, color[2] // 3)
                pygame.draw.circle(screen, dim, (x, y), 28)
                pygame.draw.circle(screen, (100, 100, 100), (x, y), 28, 2)
            else:
                pygame.draw.circle(screen, color, (x, y), 28)
                bc = YELLOW if sel else WHITE
                pygame.draw.circle(screen, bc, (x, y), 28, 5 if sel else 3)

            lbl = FONT_TINY.render(self.ALL_NAMES[ci], True, BLACK if not done else GRAY)
            screen.blit(lbl, lbl.get_rect(center=(x, y)))

        # -- right nodes --
        for i in range(self.NUM_RIGHT):
            x, y = self._node_pos_right(i)
            ci = self.right_cables[i]
            color = self.ALL_COLORS[ci]
            done = i in self.used_right
            sel = self.selected == ("right", i)
            locked = self._is_locked(ci)

            if done:
                dim = (color[0] // 3, color[1] // 3, color[2] // 3)
                pygame.draw.circle(screen, dim, (x, y), 28)
                pygame.draw.circle(screen, (100, 100, 100), (x, y), 28, 2)
            elif locked:
                pygame.draw.circle(screen, (50, 50, 60), (x, y), 28)
                pygame.draw.circle(screen, (90, 90, 100), (x, y), 28, 3)
                lt = FONT_TINY.render("LOCK", True, (140, 140, 160))
                screen.blit(lt, lt.get_rect(center=(x, y)))
            else:
                pygame.draw.circle(screen, color, (x, y), 28)
                bc = YELLOW if sel else WHITE
                pygame.draw.circle(screen, bc, (x, y), 28, 5 if sel else 3)
                lbl = FONT_TINY.render(self.ALL_NAMES[ci], True, BLACK)
                screen.blit(lbl, lbl.get_rect(center=(x, y)))

        # -- connection lines --
        for li, ri in self.connections.items():
            x1, y1 = self._node_pos_left(li)
            x2, y2 = self._node_pos_right(ri)
            lc = self.ALL_COLORS[self.left_cables[li]]
            pygame.draw.line(screen, lc, (x1, y1), (x2, y2), 5)

        # -- flash message --
        if self.flash_timer > 0 and self.flash_msg:
            ft = FONT_MEDIUM.render(self.flash_msg, True, self.flash_color)
            screen.blit(ft, (SCREEN_WIDTH // 2 - ft.get_width() // 2,
                             SCREEN_HEIGHT // 2 + 220))

        # -- on-screen rules panel (right edge) --
        rules = [
            "PRAVIDLA:",
            "1. Spoj stejne barvy",
            "2. ORAN + FIAL = navnady!",
            "3. CYAN: odemkni CERV",
            "4. MAG: odemkni MODR",
            f"5. Max {self.max_wrong} chyby",
        ]
        ry_start = 190
        for ri, rule in enumerate(rules):
            rc = YELLOW if ri == 0 else (180, 180, 200)
            rt = FONT_TINY.render(rule, True, rc)
            screen.blit(rt, (SCREEN_WIDTH - 230, ry_start + ri * 24))

        # -- counter --
        ct = FONT_SMALL.render(
            f"Pripojeno: {len(self.connections)}/{self.NUM_PAIRS}", True, YELLOW)
        screen.blit(ct, (SCREEN_WIDTH // 2 - ct.get_width() // 2, SCREEN_HEIGHT - 80))

        instr = FONT_TINY.render(
            "KLIKNI VLEVO -> PAK VPRAVO  |  "
            "Pozor na navnady a zamky!", True, LIGHT_GRAY)
        screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2,
                            SCREEN_HEIGHT - 40))

        # -- overlays --
        if self.won:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render("KABELY SPOJENY!", True, GREEN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2,
                            SCREEN_HEIGHT // 2 - 40))

        if self.lost:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render("PRILIS MNOHO CHYB!", True, RED)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2,
                            SCREEN_HEIGHT // 2 - 40))

    def get_hint(self):
        return "ORAN a FIAL jsou navnady! Spoj CERV pred CYAN, MODR pred MAG."


# =====================================================================
#  LEVEL 15 — QUANTUM SWITCHES
# =====================================================================
class QuantumSwitches(BaseGame):
    """Quantum Switches – activate switches in the right sequence.
    Each switch toggles itself AND specific linked switches."""

    NUM_SW = 7
    # Link map: pressing switch i also toggles switches in LINKS[i]
    LINKS = {
        0: [2, 5],
        1: [3],
        2: [0, 4],
        3: [1, 6],
        4: [2, 5],
        5: [0, 4, 6],
        6: [3, 5],
    }
    # Goal: all ON
    # Known solution order: 1, 4, 0, 6 (verified)

    def __init__(self):
        super().__init__()
        self.switches = [False] * self.NUM_SW
        self.press_count = 0
        self.max_presses = 12  # par = 4, generous limit = 12
        self.flash_msg = ""
        self.flash_timer = 0

    def _toggle(self, idx):
        self.switches[idx] = not self.switches[idx]
        for linked in self.LINKS.get(idx, []):
            self.switches[linked] = not self.switches[linked]

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or self.won or self.lost:
            return
        pos = event.pos
        ox = (SCREEN_WIDTH - self.NUM_SW * 120) // 2
        for i in range(self.NUM_SW):
            cx = ox + i * 120 + 50
            cy = SCREEN_HEIGHT // 2
            if (pos[0] - cx) ** 2 + (pos[1] - cy) ** 2 <= 45 ** 2:
                self._toggle(i)
                self.press_count += 1
                if all(self.switches):
                    self.won = True
                    return
                if self.press_count >= self.max_presses:
                    self.lost = True
                    self.flash_msg = "PRILIS MNOHO TAHU!"
                    self.flash_timer = 120
                return

    def update(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1

    def draw(self, screen):
        screen.fill((12, 12, 30))

        title = FONT_LARGE.render("QUANTUM SWITCHES", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        goal = FONT_SMALL.render("CIL: Rozsviť všechny přepínače!", True, YELLOW)
        screen.blit(goal, (SCREEN_WIDTH // 2 - goal.get_width() // 2, 100))

        ox = (SCREEN_WIDTH - self.NUM_SW * 120) // 2

        # Draw link lines first (behind circles)
        for i, linked in self.LINKS.items():
            cx1 = ox + i * 120 + 50
            cy1 = SCREEN_HEIGHT // 2
            for j in linked:
                if j > i:  # draw each link once
                    cx2 = ox + j * 120 + 50
                    cy2 = SCREEN_HEIGHT // 2
                    pygame.draw.line(screen, (50, 50, 80), (cx1, cy1), (cx2, cy2), 2)

        # Draw switches
        for i in range(self.NUM_SW):
            cx = ox + i * 120 + 50
            cy = SCREEN_HEIGHT // 2
            color = (0, 220, 80) if self.switches[i] else (180, 30, 30)
            pygame.draw.circle(screen, color, (cx, cy), 42)
            pygame.draw.circle(screen, WHITE, (cx, cy), 42, 3)
            lbl = FONT_MEDIUM.render(str(i + 1), True, BLACK if self.switches[i] else WHITE)
            screen.blit(lbl, lbl.get_rect(center=(cx, cy)))
            st = FONT_TINY.render("ON" if self.switches[i] else "OFF", True, WHITE)
            screen.blit(st, st.get_rect(center=(cx, cy + 58)))

        # Press counter
        ct = FONT_SMALL.render(
            f"Tahy: {self.press_count}/{self.max_presses}", True,
            RED if self.press_count >= self.max_presses - 2 else WHITE)
        screen.blit(ct, (SCREEN_WIDTH // 2 - ct.get_width() // 2, SCREEN_HEIGHT - 120))

        # Link legend
        legend = FONT_TINY.render(
            "Kazdy prepinac meni i propojene sousedy (cary)!", True, LIGHT_GRAY)
        screen.blit(legend, (SCREEN_WIDTH // 2 - legend.get_width() // 2, SCREEN_HEIGHT - 50))

        # Flash
        if self.flash_timer > 0 and self.flash_msg:
            ft = FONT_MEDIUM.render(self.flash_msg, True, RED)
            screen.blit(ft, (SCREEN_WIDTH // 2 - ft.get_width() // 2, SCREEN_HEIGHT // 2 + 140))

        # Overlays
        if self.won:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render("VSECHNY ROZSVICENY!", True, GREEN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        if self.lost:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render("PRILIS MNOHO TAHU!", True, RED)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))

    def get_hint(self):
        return "Kazdy prepinac meni i propojene. Zkus stisknout 2, 5, 1, 7."


# =====================================================================
#  LEVEL 16 — CIPHER BREAKER  (Caesar cipher puzzle)
# =====================================================================
class CipherBreaker(BaseGame):
    """Cipher Breaker – decrypt a Caesar-shifted word using given shift table."""

    SHIFT_TABLE = {
        "A": "D", "B": "E", "C": "F", "D": "G", "E": "H",
        "F": "I", "G": "J", "H": "K", "I": "L", "J": "M",
        "K": "N", "L": "O", "M": "P", "N": "Q", "O": "R",
        "P": "S", "Q": "T", "R": "U", "S": "V", "T": "W",
        "U": "X", "V": "Y", "W": "Z", "X": "A", "Y": "B",
        "Z": "C",
    }
    # Reverse table for decryption
    REVERSE = {}

    WORDS = [
        "PUZZLE", "MIRROR", "CIPHER", "QUANTUM", "SWITCH",
        "BRAIN", "LOGIC", "PORTAL", "ENIGMA", "NEBULA",
    ]

    def __init__(self):
        super().__init__()
        # Build reverse lookup
        for k, v in self.SHIFT_TABLE.items():
            self.REVERSE[v] = k

        self.plain = random.choice(self.WORDS)
        self.encrypted = "".join(self.SHIFT_TABLE.get(c, c) for c in self.plain)
        self.answer = ""
        self.wrong_attempts = 0
        self.max_attempts = 4
        self.feedback = ""
        self.feedback_timer = 0
        self.show_table = True

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or self.won or self.lost:
            return
        if event.key == pygame.K_TAB:
            self.show_table = not self.show_table
            return
        if event.key == pygame.K_BACKSPACE:
            self.answer = self.answer[:-1]
            return
        if event.key == pygame.K_RETURN:
            if self.answer.upper() == self.plain:
                self.won = True
            else:
                self.wrong_attempts += 1
                self.feedback = f"SPATNE! ({self.max_attempts - self.wrong_attempts} zbyvaji)"
                self.feedback_timer = 90
                self.answer = ""
                if self.wrong_attempts >= self.max_attempts:
                    self.lost = True
            return
        if event.unicode.isalpha() and len(self.answer) < len(self.plain) + 2:
            self.answer += event.unicode.upper()

    def update(self):
        if self.feedback_timer > 0:
            self.feedback_timer -= 1

    def draw(self, screen):
        screen.fill((15, 10, 30))

        title = FONT_LARGE.render("CIPHER BREAKER", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        inst = FONT_SMALL.render("Desifruj slovo pomoci tabulky (posun +3). Napís a stiskni ENTER.", True, WHITE)
        screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 85))

        # Encrypted word
        enc_label = FONT_SMALL.render("Zasifrovane:", True, YELLOW)
        screen.blit(enc_label, (SCREEN_WIDTH // 2 - 350, 150))
        enc_text = FONT_LARGE.render(self.encrypted, True, (255, 100, 100))
        screen.blit(enc_text, (SCREEN_WIDTH // 2 - 100, 140))

        # Answer field
        ans_label = FONT_SMALL.render("Tvoje odpoved:", True, YELLOW)
        screen.blit(ans_label, (SCREEN_WIDTH // 2 - 350, 230))
        ans_box = pygame.Rect(SCREEN_WIDTH // 2 - 100, 225, 400, 55)
        pygame.draw.rect(screen, (30, 30, 60), ans_box)
        pygame.draw.rect(screen, CYAN, ans_box, 2)
        ans_text = FONT_LARGE.render(self.answer + "_", True, GREEN)
        screen.blit(ans_text, (ans_box.x + 10, ans_box.y + 5))

        # Attempts
        att = FONT_SMALL.render(
            f"Pokusy: {self.wrong_attempts}/{self.max_attempts}", True,
            RED if self.wrong_attempts >= 3 else WHITE)
        screen.blit(att, (SCREEN_WIDTH // 2 - att.get_width() // 2, 300))

        # Shift table
        if self.show_table:
            tbl_y = 370
            tbl_label = FONT_SMALL.render("SIFROVACI TABULKA (posun +3):", True, YELLOW)
            screen.blit(tbl_label, (SCREEN_WIDTH // 2 - tbl_label.get_width() // 2, tbl_y - 30))
            letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            row1 = "  ".join(letters)
            row2 = "  ".join(self.SHIFT_TABLE[c] for c in letters)
            r1 = FONT_TINY.render("PLAIN:    " + row1, True, (180, 180, 220))
            r2 = FONT_TINY.render("CIPHER:  " + row2, True, (255, 140, 140))
            screen.blit(r1, (SCREEN_WIDTH // 2 - r1.get_width() // 2, tbl_y))
            screen.blit(r2, (SCREEN_WIDTH // 2 - r2.get_width() // 2, tbl_y + 28))
            tip = FONT_TINY.render("Kazde pismeno v CIPHER odpovida pismenu v PLAIN (napr. D->A, H->E)", True, LIGHT_GRAY)
            screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, tbl_y + 62))

        tab_hint = FONT_TINY.render("TAB = zobrazit/skrýt tabulku", True, (100, 100, 130))
        screen.blit(tab_hint, (SCREEN_WIDTH // 2 - tab_hint.get_width() // 2, SCREEN_HEIGHT - 40))

        # Feedback
        if self.feedback_timer > 0 and self.feedback:
            ft = FONT_MEDIUM.render(self.feedback, True, RED)
            screen.blit(ft, (SCREEN_WIDTH // 2 - ft.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

        # Overlays
        if self.won:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render(f"SPRAVNE! Slovo: {self.plain}", True, GREEN)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
        if self.lost:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            t = FONT_LARGE.render(f"KONEC! Slovo bylo: {self.plain}", True, RED)
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, SCREEN_HEIGHT // 2 - 40))

    def get_hint(self):
        return f"Posun je +3. Prvni pismeno desifrovane: {self.plain[0]}"


# =====================================================================
#  LEVEL 20 — ROLLING BALLS
# =====================================================================
class RollingBalls(BaseGame):
    """Rolling Balls – 5 sub-levels, resolution-adaptive grid puzzle.
    Ball slides until hitting a wall. Holes kill, switches open gates."""

    # 0=empty, 1=wall, 2=hole, 3=switch(off), 4=gate(closed), 5=gate(open), 6=switch(on)
    LEVELS = [
        {   # Level 1 – intro: no hazards, just reach the goal
            "grid": [
                [1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,1,0,0,0,0,1],
                [1,0,1,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,1,0,0,1],
                [1,0,0,1,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,1,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1],
            ],
            "switch_gate": {},
            "ball": (1, 1), "goal": (8, 6), "max_moves": 30,
        },
        {   # Level 2 – walls only
            "grid": [
                [1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,1,0,0,0,0,1],
                [1,0,1,0,0,0,1,0,0,1],
                [1,0,0,0,1,0,0,0,0,1],
                [1,1,0,0,0,0,0,0,1,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,1,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1],
            ],
            "switch_gate": {},
            "ball": (1, 1), "goal": (8, 6), "max_moves": 35,
        },
        {   # Level 3 – switch & gate (solvable)
            "grid": [
                [1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,1,0,0,0,0,1],
                [1,0,1,0,0,0,0,0,0,1],
                [1,0,0,0,0,3,0,1,0,1],
                [1,0,0,1,1,1,4,0,0,1],
                [1,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,1,0,1,0,0,1],
                [1,1,1,1,1,1,1,1,1,1],
            ],
            "switch_gate": {(5, 3): (6, 4)},
            "ball": (1, 1), "goal": (8, 5), "max_moves": 40,
        },
        {   # Level 4 – two switches, tight corridors
            "grid": [
                [1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,1,0,0,0,0,0,0,1],
                [1,0,1,0,0,0,1,0,0,0,0,1],
                [1,0,0,3,1,0,0,0,0,1,0,1],
                [1,1,0,1,1,4,0,0,1,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,1,3,1,0,4,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1],
            ],
            "switch_gate": {(3, 3): (5, 4), (5, 6): (8, 6)},
            "ball": (1, 1), "goal": (10, 7), "max_moves": 45,
        },
        {   # Level 5 – maze-like, multiple gates
            "grid": [
                [1,1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,1,0,0,0,0,0,1],
                [1,0,1,0,0,0,0,1,0,1,0,1],
                [1,0,0,0,1,3,0,0,0,0,0,1],
                [1,1,0,1,1,1,4,0,1,0,1,1],
                [1,0,0,0,0,0,0,0,0,3,0,1],
                [1,0,1,0,1,0,1,0,4,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,1,0,0,1,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1,1],
            ],
            "switch_gate": {(5, 3): (6, 4), (9, 5): (8, 6)},
            "ball": (1, 1), "goal": (10, 8), "max_moves": 50,
        },
    ]

    def __init__(self):
        super().__init__()
        self.sub_level = 0
        self._load_sub_level(0)

    def _load_sub_level(self, idx):
        """Load sub-level by index, deep-copy grid so restarts work."""
        data = self.LEVELS[idx]
        self.sub_level = idx
        self.ROWS = len(data["grid"])
        self.COLS = len(data["grid"][0])
        self.grid = [row[:] for row in data["grid"]]
        self.switch_gate = dict(data["switch_gate"])
        self.ball_x, self.ball_y = data["ball"]
        self.goal_x, self.goal_y = data["goal"]
        self.max_moves = data["max_moves"]
        self.moves = 0
        self.won = False
        self.lost = False

    # ---------- sliding mechanics ----------
    def _slide(self, dx, dy):
        if self.won or self.lost:
            return
        moved = False
        while True:
            nx = self.ball_x + dx
            ny = self.ball_y + dy
            if nx < 0 or nx >= self.COLS or ny < 0 or ny >= self.ROWS:
                break
            cell = self.grid[ny][nx]
            if cell == 1 or cell == 4:
                break
            self.ball_x = nx
            self.ball_y = ny
            moved = True
            if cell == 2:
                self.lost = True
                return
            if cell in (3, 6):
                if (nx, ny) in self.switch_gate:
                    gx, gy = self.switch_gate[(nx, ny)]
                    if self.grid[gy][gx] == 4:
                        self.grid[gy][gx] = 5
                        self.grid[ny][nx] = 6
                    else:
                        self.grid[gy][gx] = 4
                        self.grid[ny][nx] = 3
            if self.ball_x == self.goal_x and self.ball_y == self.goal_y:
                self.won = True
                return
        if moved:
            self.moves += 1
            if self.moves >= self.max_moves:
                self.lost = True

    # ---------- events ----------
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        # R = restart current sub-level
        if event.key == pygame.K_r:
            self._load_sub_level(self.sub_level)
            return
        # After winning, ENTER = next sub-level
        if self.won:
            if event.key == pygame.K_RETURN:
                if self.sub_level + 1 < len(self.LEVELS):
                    self._load_sub_level(self.sub_level + 1)
                else:
                    pass  # all sub-levels beaten – MindLock popup handles it
            return
        if self.lost:
            if event.key == pygame.K_RETURN:
                self._load_sub_level(self.sub_level)
            return
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self._slide(-1, 0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self._slide(1, 0)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self._slide(0, -1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._slide(0, 1)

    def is_won(self):
        return self.won and self.sub_level == len(self.LEVELS) - 1

    # ---------- resolution-adaptive drawing ----------
    def draw(self, screen):
        sw, sh = screen.get_size()
        scale = min(sw / 900, sh / 700)   # reference 900x700 design
        screen.fill((10, 15, 30))

        # Scaled fonts
        f_large = pygame.font.Font(None, max(16, int(64 * scale)))
        f_med   = pygame.font.Font(None, max(14, int(40 * scale)))
        f_small = pygame.font.Font(None, max(12, int(28 * scale)))
        f_tiny  = pygame.font.Font(None, max(10, int(20 * scale)))

        # Title
        title = f_large.render("ROLLING BALLS", True, CYAN)
        title_y = int(12 * scale)
        screen.blit(title, (sw // 2 - title.get_width() // 2, title_y))

        # Sub-level / moves info
        info = f_small.render(
            f"Level: {self.sub_level + 1}/{len(self.LEVELS)}   Tahy: {self.moves}/{self.max_moves}",
            True, RED if self.moves >= self.max_moves - 3 else WHITE)
        info_y = title_y + title.get_height() + int(6 * scale)
        screen.blit(info, (sw // 2 - info.get_width() // 2, info_y))

        # Compute cell size to fit grid centered between header and footer
        header_h = info_y + info.get_height() + int(10 * scale)
        footer_h = int(50 * scale)
        avail_w = sw - int(40 * scale)
        avail_h = sh - header_h - footer_h
        cell = min(avail_w // self.COLS, avail_h // self.ROWS, int(60 * scale))
        cell = max(cell, 16)

        ox = (sw - self.COLS * cell) // 2
        oy = header_h + (avail_h - self.ROWS * cell) // 2

        colors = {
            0: (30, 30, 55), 1: (80, 80, 100), 2: (20, 20, 20),
            3: (200, 200, 0), 4: (140, 50, 50), 5: (50, 140, 50),
            6: (100, 255, 100),
        }
        r_hole = max(4, int(cell * 0.28))
        r_goal = max(4, int(cell * 0.28))
        r_ball = max(5, int(cell * 0.31))

        for gy in range(self.ROWS):
            for gx in range(self.COLS):
                rx = ox + gx * cell
                ry = oy + gy * cell
                c = self.grid[gy][gx]
                rect = pygame.Rect(rx, ry, cell, cell)
                pygame.draw.rect(screen, colors.get(c, (30, 30, 55)), rect)
                pygame.draw.rect(screen, (50, 50, 70), rect, 1)
                cx, cy = rx + cell // 2, ry + cell // 2
                if c == 2:
                    pygame.draw.circle(screen, (40, 0, 0), (cx, cy), r_hole)
                elif c in (3, 6):
                    lbl = f_tiny.render("SW", True, BLACK)
                    screen.blit(lbl, lbl.get_rect(center=(cx, cy)))
                elif c == 4:
                    lbl = f_tiny.render("GATE", True, WHITE)
                    screen.blit(lbl, lbl.get_rect(center=(cx, cy)))
                elif c == 5:
                    lbl = f_tiny.render("OPEN", True, BLACK)
                    screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

        # Goal
        gcx = ox + self.goal_x * cell + cell // 2
        gcy = oy + self.goal_y * cell + cell // 2
        pygame.draw.circle(screen, (255, 215, 0), (gcx, gcy), r_goal)
        gl = f_tiny.render("CIL", True, BLACK)
        screen.blit(gl, gl.get_rect(center=(gcx, gcy)))

        # Ball
        bx = ox + self.ball_x * cell + cell // 2
        by = oy + self.ball_y * cell + cell // 2
        pygame.draw.circle(screen, (0, 180, 255), (bx, by), r_ball)
        pygame.draw.circle(screen, WHITE, (bx, by), r_ball, 2)

        # Footer instructions
        instr = f_tiny.render(
            "SIPKY/WASD = pohyb  |  R = restart  |  Vyhni se diram!", True, LIGHT_GRAY)
        screen.blit(instr, (sw // 2 - instr.get_width() // 2, sh - int(38 * scale)))

        # Win / Lose overlays
        if self.won or self.lost:
            ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 150))
            screen.blit(ov, (0, 0))
            if self.won:
                if self.sub_level + 1 < len(self.LEVELS):
                    msg = f"LEVEL {self.sub_level + 1} HOTOVO!"
                    sub = "ENTER = dalsi level"
                else:
                    msg = "MICEK V CILI!"
                    sub = "Vsechny levely hotovy!"
                t = f_large.render(msg, True, GREEN)
            else:
                reason = "SPADL DO DIRY!" if self.grid[self.ball_y][self.ball_x] == 2 else "PRILIS MNOHO TAHU!"
                t = f_large.render(reason, True, RED)
                sub = "ENTER = restart"
            screen.blit(t, (sw // 2 - t.get_width() // 2, sh // 2 - int(40 * scale)))
            s = f_small.render(sub, True, YELLOW)
            screen.blit(s, (sw // 2 - s.get_width() // 2, sh // 2 + int(30 * scale)))

    def get_hint(self):
        return "Micek se klouze az narazi na zed. Aktivuj prepinac a vyhni se diram!"


class ComingSoonGame(BaseGame):
    """Prázdný level - Coming Soon"""
    def __init__(self):
        super().__init__()
        self.timer = 0
    
    def handle_event(self, event):
        """Kliknutí je disabled"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Nic se nestane
            pass
    
    def update(self):
        self.timer += 1
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("COMING SOON", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - 280, 250))
        
        message = FONT_MEDIUM.render("Tento level je připraven na zpracování", True, CYAN)
        screen.blit(message, (SCREEN_WIDTH//2 - 350, 400))
        
        submsg = FONT_SMALL.render("Později bude k dispozici!", True, WHITE)
        screen.blit(submsg, (SCREEN_WIDTH//2 - 150, 500))
        
        locked = FONT_SMALL.render("Tento level je nehratelný", True, RED)
        screen.blit(locked, (SCREEN_WIDTH//2 - 150, 650))
    
    def get_hint(self):
        return "Tento level zatím není dostupný - Coming Soon!"


class BlankGame(BaseGame):
    """
    Prázdný level bez zprávy.
    
    DISABLE COMING SOON FOR LEVEL 20:
    Tato třída se používá pro level 20.
    Na rozdíl od ComingSoonGame() nezobrazuje žádnou zprávu.
    Kliknutím na level 20 se nic nestane (tiché selhání).
    """
    def __init__(self):
        super().__init__()
        self.timer = 0
    
    def handle_event(self, event):
        """Všechny eventy jsou ignorovány"""
        pass
    
    def update(self):
        self.timer += 1
    
    def draw(self, screen):
        """Zobrazuje Coming soon zprávu"""
        screen.fill(DARK_BLUE)
        
        # Nadpis
        title = FONT_LARGE.render("🚀 COMING SOON 🚀", True, CYAN)
        title_rect = title.get_rect(center=(screen.get_width()//2, 200))
        screen.blit(title, title_rect)
        
        # Hlavní zpráva
        msg = FONT_MEDIUM.render("Level 20 bude přidán v příští verzi!", True, WHITE)
        msg_rect = msg.get_rect(center=(screen.get_width()//2, 400))
        screen.blit(msg, msg_rect)
        
        # Verze info
        version_text = FONT_SMALL.render(f"MindLock! {GAME_VERSION}", True, GRAY)
        version_rect = version_text.get_rect(center=(screen.get_width()//2, 600))
        screen.blit(version_text, version_rect)
    
    def get_hint(self):
        return "Level bude k dispozici v příští verzi"


if __name__ == "__main__":
    game = Game()
    game.run()

