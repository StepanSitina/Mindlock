import pygame
import sys
import random
import math
from enum import Enum
from collections import defaultdict


pygame.init()


SCREEN_WIDTH = 1920
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
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("MindLock! - Puzzle Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        self.fps = 60
        self.current_level = 1
        self.unlocked_levels = 1
        self.level_completed = False
        self.game_won = False
        self.show_hint = False
        self.hint_timer = 0
        self.pause_menu_open = False
        self.show_hint_popup = False
        self.hint_popup_timer = 0
        

        self.patch_notes = [
            {"version": "1.0.0", "notes": ["Počáteční verze hry", "11 různých herních módů"]},
            {"version": "1.1.0", "notes": ["Opravena mechanika levelů", "Přidány nápovědy"]},
            {"version": "1.2.0", "notes": ["Hezčí a moderní menu", "Opravena logika 2048", "Přidán delay v Simon Says", "Patch notes nyní v Pop-up okně"]},
            {"version": "1.3.0", "notes": ["Opravena chyba SimonSays s nekonečnou smyčkou", "Opravena inicializace TetrisLite", "Odstraněny všechny komentáře ze kódu", "Opraveny chyby v souboru"]},
            {"version": "1.4.0", "notes": ["Nápověda jako popup okno (stiskni H)", "Pause menu s ESC klávesou", "Tlačítka: Continue, Restart (odemyka level 2), Exit", "Simon Says nyní vyžaduje 5 kol místo 7"]},
            {"version": "1.5.0", "notes": ["Bludiště má nyní mnohem více zdí (164 přesně)", "Přidán tajný admin mode - stiskni O pro odemknutí všech levelů", "Vylepšená herní vyvážená obtížnost", "Patch notes aktualizovány po každé změně"]}
        ]
        
        self.version = self.patch_notes[-1]["version"]

        self.menu_buttons = {
            "play": Button(SCREEN_WIDTH//2 - 110, 250, 220, 70, "PLAY"),
            "patch": Button(SCREEN_WIDTH//2 - 120, 350, 240, 70, "PATCH NOTES"),
            "settings": Button(SCREEN_WIDTH//2 - 110, 450, 220, 70, "SETTINGS"),
            "exit": Button(SCREEN_WIDTH//2 - 110, 550, 220, 70, "QUIT")
        }
        

        self.settings_buttons = {
            "fps_down": Button(600, 280, 50, 50, "-", FONT_MEDIUM),
            "fps_up": Button(750, 280, 50, 50, "+", FONT_MEDIUM),
            "graphics": Button(200, 250, 300, 60, "Graphics", FONT_SMALL),
            "developer": Button(200, 350, 300, 60, "Developer", FONT_SMALL),
            "back": Button(SCREEN_WIDTH//2 - 100, 700, 200, 60, "BACK")
        }
        

        self.settings_expanded = {
            "graphics": False,
            "developer": False
        }
        

        self.patch_buttons = {
            "back": Button(SCREEN_WIDTH//2 - 100, 700, 200, 60, "ZPĚT")
        }
        

        self.play_buttons = {
            "back": Button(SCREEN_WIDTH//2 - 100, 700, 200, 60, "ZPĚT")
        }
        self.level_buttons = {}
        self.create_level_buttons()
        
  
        self.popup_buttons = {
            "menu": Button(SCREEN_WIDTH//2 - 250, 400, 150, 60, "MENU"),
            "restart": Button(SCREEN_WIDTH//2 - 50, 400, 150, 60, "RESTART"),
            "next": Button(SCREEN_WIDTH//2 + 150, 400, 150, 60, "DALŠÍ")
        }
        
        self.pause_buttons = {
            "continue": Button(SCREEN_WIDTH//2 - 100, 350, 200, 60, "CONTINUE"),
            "restart": Button(SCREEN_WIDTH//2 - 100, 450, 200, 60, "RESTART"),
            "exit": Button(SCREEN_WIDTH//2 - 100, 550, 200, 60, "EXIT")
        }

        self.current_game = None
        
    def create_level_buttons(self):
        """Vytvoří tlačítka pro všech 20 levelů"""
        for i in range(1, 21):
            col = (i - 1) % 5
            row = (i - 1) // 5
            x = 150 + col * 180
            y = 150 + row * 120
            self.level_buttons[i] = Button(x, y, 160, 100, f"LEVEL {i}", FONT_SMALL)
    
    def draw_menu(self):
        """Kreslí hlavní menu"""
        self.screen.fill((20, 40, 80))
        
  
        title = FONT_LARGE.render("MindLock!", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 90))
       
        shadow = FONT_LARGE.render("MindLock!", True, (0, 50, 80))
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
      
        pygame.draw.line(self.screen, CYAN, (SCREEN_WIDTH//2 - 300, 160), (SCREEN_WIDTH//2 - 100, 160), 2)
        pygame.draw.line(self.screen, CYAN, (SCREEN_WIDTH//2 + 100, 160), (SCREEN_WIDTH//2 + 300, 160), 2)
        

        subtitle = FONT_SMALL.render("Puzzle Game", True, (200, 200, 255))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
  
        for button in self.menu_buttons.values():
            button.draw(self.screen)
    
    def draw_patch_notes(self):
        """Kreslí patch notes"""
        self.screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("PATCH NOTES", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 40))
        self.screen.blit(title, title_rect)
        

        box_rect = pygame.Rect(150, 120, SCREEN_WIDTH - 300, 500)
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
        """Kreslí nastavení"""
        self.screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("SETTINGS", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 40))
        self.screen.blit(title, title_rect)
        
 
        graphics_button = self.settings_buttons["graphics"]
        graphics_button.draw(self.screen)
        
        if self.settings_expanded["graphics"]:
   
            fps_label = FONT_SMALL.render("FPS:", True, WHITE)
            self.screen.blit(fps_label, (250, 320))
            
            fps_value = FONT_MEDIUM.render(str(self.fps), True, YELLOW)
            fps_rect = fps_value.get_rect(center=(650, 310))
            self.screen.blit(fps_value, fps_rect)
            
            self.settings_buttons["fps_down"].draw(self.screen)
            self.settings_buttons["fps_up"].draw(self.screen)
        
 
        developer_button = self.settings_buttons["developer"]
        developer_button.draw(self.screen)
        
        if self.settings_expanded["developer"]:
            developer_info = [
                "Name: Stepan Sitina",
                "Version: " + self.version,
                "Levels: 20",
                "Game modes: 11"
            ]
            
            y_offset = 410
            for info in developer_info:
                info_text = FONT_SMALL.render("- " + info, True, WHITE)
                self.screen.blit(info_text, (250, y_offset))
                y_offset += 35
        
        self.settings_buttons["back"].draw(self.screen)
    
    def draw_play_menu(self):
        """Kreslí menu pro výběr levelů"""
        self.screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("VYBRAT LEVEL", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 30))
        self.screen.blit(title, title_rect)
        
        for level_num, button in self.level_buttons.items():
      
            if level_num <= self.unlocked_levels:
                button.draw(self.screen)
            else:
                pygame.draw.rect(self.screen, DARK_GRAY, button.rect)
                pygame.draw.rect(self.screen, GRAY, button.rect, 3)
                lock_text = FONT_SMALL.render("LOCKED", True, RED)
                lock_rect = lock_text.get_rect(center=button.rect.center)
                self.screen.blit(lock_text, lock_rect)
        
        self.play_buttons["back"].draw(self.screen)
    
    def draw_popup_menu(self):
        """Kreslí popup menu po skončení levelu"""

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.game_won:
            title = FONT_LARGE.render("YOU WON!", True, GREEN)
        else:
            title = FONT_LARGE.render("YOU LOST!", True, RED)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(title, title_rect)
        
        self.popup_buttons["menu"].draw(self.screen)
        self.popup_buttons["restart"].draw(self.screen)
        
        if self.game_won and self.current_level < 20:
            self.popup_buttons["next"].draw(self.screen)
        elif self.current_level == 20 and self.game_won:
            final_text = FONT_SMALL.render("CONGRATULATIONS - WINNER!", True, YELLOW)
            self.screen.blit(final_text, (SCREEN_WIDTH//2 - 200, 500))
    
    def draw_pause_menu(self):
        """Kreslí pause menu"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = FONT_LARGE.render("PAUSE", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(title, title_rect)
        
        self.pause_buttons["continue"].draw(self.screen)
        self.pause_buttons["restart"].draw(self.screen)
        self.pause_buttons["exit"].draw(self.screen)
    
    def draw_hint_popup(self):
        """Kreslí hint popup"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        hint_title = FONT_LARGE.render("NAPOVEDA", True, YELLOW)
        hint_title_rect = hint_title.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(hint_title, hint_title_rect)
        
        hint = self.current_game.get_hint()
        hint_text = FONT_MEDIUM.render(hint, True, GREEN)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH//2, 450))
        
        box_rect = pygame.Rect(hint_rect.x - 40, hint_rect.y - 20, hint_rect.width + 80, hint_rect.height + 40)
        pygame.draw.rect(self.screen, BLUE, box_rect)
        pygame.draw.rect(self.screen, CYAN, box_rect, 3)
        self.screen.blit(hint_text, hint_rect)
        
        close_text = FONT_SMALL.render("Klikni kdekoliv pro zavreni", True, WHITE)
        close_rect = close_text.get_rect(center=(SCREEN_WIDTH//2, 600))
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
        """Zpracuje klik v nastavení"""
        if self.settings_buttons["graphics"].is_clicked(pos):
            self.settings_expanded["graphics"] = not self.settings_expanded["graphics"]
        elif self.settings_buttons["developer"].is_clicked(pos):
            self.settings_expanded["developer"] = not self.settings_expanded["developer"]
        elif self.settings_expanded["graphics"] and self.settings_buttons["fps_down"].is_clicked(pos):
            self.fps = max(10, self.fps - 10)
        elif self.settings_expanded["graphics"] and self.settings_buttons["fps_up"].is_clicked(pos):
            self.fps = min(240, self.fps + 10)
        elif self.settings_buttons["back"].is_clicked(pos):
            self.state = GameState.MENU
    
    def handle_play_click(self, pos):
        """Zpracuje klik v play menu"""
        for level_num, button in self.level_buttons.items():
            if level_num <= self.unlocked_levels and button.is_clicked(pos):
                self.current_level = level_num
                self.state = GameState.GAME
                self.game_won = False
                self.level_completed = False
                self.current_game = self.create_game_level(level_num)
                return
        
        if self.play_buttons["back"].is_clicked(pos):
            self.state = GameState.MENU
    
    def handle_popup_click(self, pos):
        """Zpracuje klik v popup menu"""
        if self.popup_buttons["menu"].is_clicked(pos):
            self.state = GameState.PLAYING
        elif self.popup_buttons["restart"].is_clicked(pos):
            self.current_game = self.create_game_level(self.current_level)
            self.level_completed = False
            self.game_won = False
        elif self.game_won and self.current_level < 20 and self.popup_buttons["next"].is_clicked(pos):
            if self.current_level < 20:
                self.current_level += 1
                self.current_game = self.create_game_level(self.current_level)
                self.level_completed = False
                self.game_won = False
    
    def handle_pause_click(self, pos):
        """Zpracuje klik v pause menu"""
        if self.pause_buttons["continue"].is_clicked(pos):
            self.pause_menu_open = False
        elif self.pause_buttons["restart"].is_clicked(pos):
            self.unlocked_levels = max(self.unlocked_levels, 2)
            self.current_level = 2
            self.current_game = self.create_game_level(2)
            self.level_completed = False
            self.game_won = False
            self.pause_menu_open = False
        elif self.pause_buttons["exit"].is_clicked(pos):
            self.state = GameState.PLAYING
            self.pause_menu_open = False
    
    def create_game_level(self, level_num):
        """Vytvoří hru pro daný level"""
        games = [
            SimonSays(),
            Maze(),
            ButtonFinder(),
            TetrisLite(),
            Game2048(),
            BalanceGame(),
            RiddleGame(),
            SudokuLite(),
            CaesarCipher(),
            SwitchGame(),
            WordUnscrambler(),
            Maze(),
            SimonSays(),
            ButtonFinder(),
            TetrisLite(),
            Game2048(),
            BalanceGame(),
            RiddleGame(),
            SudokuLite(),
            WordUnscrambler()
        ]
        return games[level_num - 1]
    
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
                for button in self.settings_buttons.values():
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
                    self.unlocked_levels = 20
                if self.state == GameState.GAME:
                    if event.key == pygame.K_ESCAPE:
                        if not self.level_completed:
                            self.pause_menu_open = not self.pause_menu_open
                    elif not self.level_completed and not self.pause_menu_open:
                        self.current_game.handle_event(event)
                        if event.key == pygame.K_h:
                            self.show_hint_popup = True
                            self.hint_popup_timer = 400
    
    def update(self):
        """Aktualizuje stav hry"""
        if self.state == GameState.GAME and not self.level_completed and self.current_game and not self.pause_menu_open:
            self.current_game.update()
            if self.current_game.is_won():
                self.level_completed = True
                self.game_won = True
                if self.current_level == self.unlocked_levels and self.unlocked_levels < 20:
                    self.unlocked_levels += 1
            elif self.current_game.is_lost():
                self.level_completed = True
                self.game_won = False
        
        if self.hint_popup_timer > 0:
            self.hint_popup_timer -= 1
        else:
            self.show_hint_popup = False
    
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
                
                hint_text = FONT_TINY.render("Napoveda: Stiskni H | ESC: Menu", True, YELLOW)
                self.screen.blit(hint_text, (10, 10))
                
                level_text = FONT_SMALL.render(f"Level: {self.current_level}/20", True, WHITE)
                self.screen.blit(level_text, (SCREEN_WIDTH - 200, 10))
                
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
    """Bludiště - pohyb WSAD nebo šipkami"""
    def __init__(self):
        super().__init__()
        self.player_x = 100
        self.player_y = 100
        self.goal_x = 1100
        self.goal_y = 700
        self.walls = self.generate_maze()
        self.player_size = 20
        self.speed = 5
    
    def generate_maze(self):
        """Generuje bludiště s více zdmi"""
        walls = []
        for x in range(0, SCREEN_WIDTH, 40):
            walls.append(pygame.Rect(x, 0, 40, 30))
            walls.append(pygame.Rect(x, SCREEN_HEIGHT - 30, 40, 30))
        for y in range(0, SCREEN_HEIGHT, 40):
            walls.append(pygame.Rect(0, y, 30, 40))
            walls.append(pygame.Rect(SCREEN_WIDTH - 30, y, 30, 40))
        
        internal_walls = [
            pygame.Rect(300, 150, 400, 30),
            pygame.Rect(600, 400, 300, 30),
            pygame.Rect(200, 450, 200, 30),
            pygame.Rect(800, 200, 30, 300),
            pygame.Rect(400, 550, 400, 30),
            pygame.Rect(150, 300, 30, 250),
            pygame.Rect(500, 250, 300, 30),
            pygame.Rect(900, 400, 30, 200),
            pygame.Rect(350, 600, 250, 30),
            pygame.Rect(700, 150, 30, 200),
            pygame.Rect(200, 650, 300, 30),
            pygame.Rect(1200, 300, 30, 350),
            pygame.Rect(600, 600, 200, 30),
            pygame.Rect(1000, 650, 200, 30),
        ]
        walls.extend(internal_walls)
        return walls
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.move(event.key)
    
    def move(self, key):
        """Pohyb pomocí kláves"""
        new_x, new_y = self.player_x, self.player_y
        
        if key in [pygame.K_w, pygame.K_UP]:
            new_y -= self.speed
        elif key in [pygame.K_s, pygame.K_DOWN]:
            new_y += self.speed
        elif key in [pygame.K_a, pygame.K_LEFT]:
            new_x -= self.speed
        elif key in [pygame.K_d, pygame.K_RIGHT]:
            new_x += self.speed
        
        # Kontrola kolize se zdí
        player_rect = pygame.Rect(new_x, new_y, self.player_size, self.player_size)
        collision = False
        for wall in self.walls:
            if player_rect.colliderect(wall):
                collision = True
                break
        
        if not collision:
            self.player_x = new_x
            self.player_y = new_y
        
        # Kontrola cíle
        if math.sqrt((self.player_x - self.goal_x)**2 + (self.player_y - self.goal_y)**2) < 30:
            self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        # Kreslení zdí
        for wall in self.walls:
            pygame.draw.rect(screen, GRAY, wall)
        
        # Cíl
        pygame.draw.circle(screen, GREEN, (self.goal_x, self.goal_y), 20)
        goal_text = FONT_SMALL.render("CÍL", True, BLACK)
        goal_rect = goal_text.get_rect(center=(self.goal_x, self.goal_y))
        screen.blit(goal_text, goal_rect)
        
        # Hráč
        pygame.draw.circle(screen, CYAN, (self.player_x, self.player_y), self.player_size)
        
        # Instrukce
        instr = FONT_SMALL.render("WSAD nebo ŠIPKY - Pohyb", True, WHITE)
        screen.blit(instr, (20, SCREEN_HEIGHT - 50))
    
    def get_hint(self):
        return "Vyhni se zdím, dosáhni zeleného cíle!"

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
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.waiting_for_input:
            pos = event.pos
            for i in range(4):
                col = i % 2
                row = i // 2
                x = 300 + col * 200
                y = 250 + row * 200
                if pygame.Rect(x, y, 150, 150).collidepoint(pos):
                    self.player_sequence.append(i)
                    self.lights_on[i] = True
                    self.light_timer = 30
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
            self.light_timer = 30
            self.current_step += 1
            self.sequence_delay = 35
        else:
            self.waiting_for_input = True
            self.player_sequence = []
    
    def check_sequence(self):
        if self.player_sequence[-1] != self.sequence[len(self.player_sequence) - 1]:
            self.lost = True
        elif len(self.player_sequence) == len(self.sequence):
            if len(self.sequence) == 5:
                self.won = True
            else:
                self.sequence.append(random.randint(0, 3))
                self.waiting_for_input = False
                self.current_step = 0
                self.round += 1
                self.round_delay = 120
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("SIMON SAYS", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        # Tlačítka
        for i in range(4):
            col = i % 2
            row = i // 2
            x = 300 + col * 200
            y = 250 + row * 200
            color = self.colors[i] if not self.lights_on[i] else (255, 255, 255)
            pygame.draw.circle(screen, color, (x + 75, y + 75), 75)
        
        # Info
        info = FONT_MEDIUM.render(f"Kolo: {self.round}", True, YELLOW)
        screen.blit(info, (SCREEN_WIDTH//2 - 80, 500))
        
        if self.waiting_for_input:
            instr = FONT_SMALL.render("Tvůj tah! Klikej na světla", True, GREEN)
        else:
            instr = FONT_SMALL.render("Sleduj sekvenci...", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 180, 600))
        
        if self.lost:
            lose = FONT_LARGE.render("ŠPATNĚ!", True, RED)
            screen.blit(lose, (SCREEN_WIDTH//2 - 100, 650))
    
    def get_hint(self):
        return "Zapamatuj si pořadí barev!"

class ButtonFinder(BaseGame):
    """Najdi tlačítko - jednoduché"""
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.target_button = 0
        self.create_buttons()
    
    def create_buttons(self):
        """Vytvoří náhodná tlačítka"""
        self.buttons = []
        self.target_button = random.randint(0, 8)
        
        for i in range(9):
            x = 150 + (i % 3) * 300
            y = 250 + (i // 3) * 150
            self.buttons.append(pygame.Rect(x, y, 150, 100))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i, btn in enumerate(self.buttons):
                if btn.collidepoint(pos):
                    if i == self.target_button:
                        self.won = True
                    else:
                        self.lost = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("NAJDI TLAČÍTKO", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 170, 30))
        
        for i, btn in enumerate(self.buttons):
            if i == self.target_button:
                color = GREEN
            else:
                color = BLUE
            pygame.draw.rect(screen, color, btn)
            pygame.draw.rect(screen, WHITE, btn, 3)
        
        instr = FONT_SMALL.render("Klikni na zelené tlačítko!", True, GREEN)
        screen.blit(instr, (SCREEN_WIDTH//2 - 150, 700))
    
    def get_hint(self):
        return "Zelené tlačítko se skrývá!"

class TetrisLite(BaseGame):
    """Lehký Tetris"""
    def __init__(self):
        super().__init__()
        self.grid = [[0] * 6 for _ in range(10)]
        self.pieces = [
            [[1, 1], [1, 1]],  
            [[1, 1, 1, 1]],    
            [[1, 1, 1], [1, 0, 0]],  
        ]
        self.piece = self.new_piece()
        self.piece_x = 2
        self.piece_y = 0
        self.fall_timer = 0
        self.lines_cleared = 0
    
    def new_piece(self):
        return random.choice(self.pieces)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                self.piece_x = max(0, self.piece_x - 1)
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                self.piece_x = min(6 - len(self.piece[0]), self.piece_x + 1)
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                self.fall()
    
    def fall(self):
        """Padá kus dolů"""
        if self.can_place(self.piece_x, self.piece_y + 1):
            self.piece_y += 1
        else:
            self.place_piece()
            self.clear_lines()
            self.piece = self.new_piece()
            self.piece_x = 2
            self.piece_y = 0
            
            if not self.can_place(self.piece_x, self.piece_y):
                self.lost = True
    
    def can_place(self, x, y):
        """Kontroluje, jestli lze umístit kus"""
        for row in range(len(self.piece)):
            for col in range(len(self.piece[row])):
                if self.piece[row][col]:
                    grid_x = x + col
                    grid_y = y + row
                    if grid_y >= 10 or grid_x >= 6 or grid_x < 0:
                        if grid_y >= 10:
                            return grid_y < 10
                        return False
                    if grid_y >= 0 and self.grid[grid_y][grid_x]:
                        return False
        return True
    
    def place_piece(self):
        """Umístí kus na hrací pole"""
        for row in range(len(self.piece)):
            for col in range(len(self.piece[row])):
                if self.piece[row][col]:
                    self.grid[self.piece_y + row][self.piece_x + col] = 1
    
    def clear_lines(self):
        """Vymazání plných řad"""
        new_grid = []
        for row in self.grid:
            if sum(row) < 6:
                new_grid.append(row)
            else:
                self.lines_cleared += 1
        
        while len(new_grid) < 10:
            new_grid.insert(0, [0] * 6)
        
        self.grid = new_grid
        
        if self.lines_cleared >= 3:
            self.won = True
    
    def update(self):
        self.fall_timer += 1
        if self.fall_timer > 30:
            self.fall()
            self.fall_timer = 0
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("LEHKÝ TETRIS", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        # Hrací pole
        start_x = 300
        start_y = 150
        cell_size = 30
        
        for row in range(10):
            for col in range(6):
                rect = pygame.Rect(start_x + col * cell_size, start_y + row * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, GRAY, rect, 1)
                if self.grid[row][col]:
                    pygame.draw.rect(screen, CYAN, rect)
        
        # Aktuální kus
        for row in range(len(self.piece)):
            for col in range(len(self.piece[row])):
                if self.piece[row][col]:
                    x = start_x + (self.piece_x + col) * cell_size
                    y = start_y + (self.piece_y + row) * cell_size
                    pygame.draw.rect(screen, YELLOW, pygame.Rect(x, y, cell_size, cell_size))
        
        score_text = FONT_SMALL.render(f"Řady: {self.lines_cleared}/3", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - 80, 600))
        
        instr = FONT_TINY.render("A/D nebo ŠIPKY - Pohyb | S/DOWN - Pád", True, WHITE)
        screen.blit(instr, (100, SCREEN_HEIGHT - 50))
    
    def get_hint(self):
        return "Vymaž 3 řady!"

class Game2048(BaseGame):
    """2048 - zjednodušená verze"""
    def __init__(self):
        super().__init__()
        self.grid = [[0] * 4 for _ in range(4)]
        self.add_new_tile()
        self.add_new_tile()
        self.moves = 0
    
    def add_new_tile(self):
        """Přidá nové číslo"""
        empty = [(i, j) for i in range(4) for j in range(4) if self.grid[i][j] == 0]
        if empty:
            i, j = random.choice(empty)
            self.grid[i][j] = random.choice([2, 4])
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            moved = False
            if event.key in [pygame.K_a, pygame.K_LEFT]:
                moved = self.move_left()
            elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                moved = self.move_right()
            elif event.key in [pygame.K_w, pygame.K_UP]:
                moved = self.move_up()
            elif event.key in [pygame.K_s, pygame.K_DOWN]:
                moved = self.move_down()
            
            if moved:
                self.add_new_tile()
                self.moves += 1
                if any(2048 in row for row in self.grid):
                    self.won = True
    
    def move_left(self):
        changed = False
        new_grid = [[0] * 4 for _ in range(4)]
        
        for i in range(4):
            tiles = [self.grid[i][j] for j in range(4) if self.grid[i][j] != 0]
            
            # Sloučit stejná čísla
            merged = []
            j = 0
            while j < len(tiles):
                if j + 1 < len(tiles) and tiles[j] == tiles[j + 1]:
                    merged.append(tiles[j] * 2)
                    j += 2
                else:
                    merged.append(tiles[j])
                    j += 1
            
            # Umístit do nové řady
            for j in range(len(merged)):
                new_grid[i][j] = merged[j]
        
        if new_grid != self.grid:
            changed = True
        self.grid = new_grid
        return changed
    
    def move_right(self):
        self.grid = [row[::-1] for row in self.grid]
        new_grid = [[0] * 4 for _ in range(4)]
        changed = False
        
        for i in range(4):
            tiles = [self.grid[i][j] for j in range(4) if self.grid[i][j] != 0]
            merged = []
            j = 0
            while j < len(tiles):
                if j + 1 < len(tiles) and tiles[j] == tiles[j + 1]:
                    merged.append(tiles[j] * 2)
                    j += 2
                else:
                    merged.append(tiles[j])
                    j += 1
            for j in range(len(merged)):
                new_grid[i][j] = merged[j]
        
        if new_grid != self.grid:
            changed = True
        self.grid = new_grid
        self.grid = [row[::-1] for row in self.grid]
        return changed
    
    def move_up(self):
        # Transponuj mřížku
        self.grid = [list(row) for row in zip(*self.grid)]
        new_grid = [[0] * 4 for _ in range(4)]
        changed = False
        
        for i in range(4):
            tiles = [self.grid[i][j] for j in range(4) if self.grid[i][j] != 0]
            merged = []
            j = 0
            while j < len(tiles):
                if j + 1 < len(tiles) and tiles[j] == tiles[j + 1]:
                    merged.append(tiles[j] * 2)
                    j += 2
                else:
                    merged.append(tiles[j])
                    j += 1
            for j in range(len(merged)):
                new_grid[i][j] = merged[j]
        
        if new_grid != self.grid:
            changed = True
        self.grid = new_grid
        # Vrť transponovanou mřížku
        self.grid = [list(row) for row in zip(*self.grid)]
        return changed
    
    def move_down(self):
        # Transponuj mřížku
        self.grid = [list(row) for row in zip(*self.grid)]
        new_grid = [[0] * 4 for _ in range(4)]
        changed = False
        
        for i in range(4):
            tiles = [self.grid[i][j] for j in range(4) if self.grid[i][j] != 0]
            merged = []
            j = 0
            while j < len(tiles):
                if j + 1 < len(tiles) and tiles[j] == tiles[j + 1]:
                    merged.append(tiles[j] * 2)
                    j += 2
                else:
                    merged.append(tiles[j])
                    j += 1
            for j in range(len(merged)):
                new_grid[i][3 - len(merged) + j] = merged[j]
        
        if new_grid != self.grid:
            changed = True
        self.grid = new_grid
        self.grid = [list(row) for row in zip(*self.grid)]
        return changed
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("2048", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 100, 30))
        
        start_x = 400
        start_y = 200
        cell_size = 80
        
        for i in range(4):
            for j in range(4):
                rect = pygame.Rect(start_x + j * cell_size, start_y + i * cell_size, cell_size, cell_size)
                value = self.grid[i][j]
                
                if value == 0:
                    pygame.draw.rect(screen, GRAY, rect)
                else:
                    pygame.draw.rect(screen, YELLOW, rect)
                    value_text = FONT_MEDIUM.render(str(value), True, BLACK)
                    value_rect = value_text.get_rect(center=rect.center)
                    screen.blit(value_text, value_rect)
                
                pygame.draw.rect(screen, WHITE, rect, 2)
        
        instr = FONT_SMALL.render("WSAD nebo ŠIPKY - Pohybuj čísla", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 200, 650))
    
    def get_hint(self):
        return "Skládej stejná čísla, dosáhni 2048!"

class BalanceGame(BaseGame):
    """Hra s váhou - přesně půlka"""
    def __init__(self):
        super().__init__()
        self.total_weight = random.randint(200, 400)
        self.left_weight = 0
        self.right_weight = 0
        self.items = [
            {"name": "Jablko", "weight": 10},
            {"name": "Kniha", "weight": 15},
            {"name": "Cihla", "weight": 50},
            {"name": "Pero", "weight": 5},
            {"name": "Lyže", "weight": 25},
        ]
        self.available_items = self.items.copy()
        self.instruction = f"Dosáhni váhy {self.total_weight}g na obě strany!"
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i, item in enumerate(self.available_items):
                x = 100 + i * 100
                y = 300
                if pygame.Rect(x, y, 80, 80).collidepoint(pos):
                    if self.left_weight + item["weight"] <= self.total_weight:
                        self.left_weight += item["weight"]
                        self.available_items.remove(item)
                    break
            
            for i, item in enumerate(self.available_items):
                x = 1000 - i * 100
                y = 300
                if pygame.Rect(x, y, 80, 80).collidepoint(pos):
                    if self.right_weight + item["weight"] <= self.total_weight:
                        self.right_weight += item["weight"]
                        self.available_items.remove(item)
                    break
        
        if self.left_weight == self.total_weight and self.right_weight == self.total_weight:
            self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("VÁŽKA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 100, 30))
        
        # Váha
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH//2 - 200, 200), (SCREEN_WIDTH//2 + 200, 200), 5)
        pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH//2, 200), 10)
        
        # Levá strana
        left_text = FONT_MEDIUM.render(f"L: {self.left_weight}g", True, YELLOW if self.left_weight <= self.total_weight else RED)
        screen.blit(left_text, (200, 200))
        pygame.draw.rect(screen, BLUE, pygame.Rect(150, 250, 200, 150))
        
        # Pravá strana
        right_text = FONT_MEDIUM.render(f"P: {self.right_weight}g", True, YELLOW if self.right_weight <= self.total_weight else RED)
        screen.blit(right_text, (SCREEN_WIDTH - 400, 200))
        pygame.draw.rect(screen, BLUE, pygame.Rect(SCREEN_WIDTH - 350, 250, 200, 150))
        
        # Dostupné položky
        for i, item in enumerate(self.available_items):
            x = 100 + i * 100
            y = 450
            pygame.draw.rect(screen, GREEN, pygame.Rect(x, y, 80, 80))
            item_text = FONT_TINY.render(item["name"], True, BLACK)
            weight_text = FONT_TINY.render(f"{item['weight']}g", True, BLACK)
            screen.blit(item_text, (x + 10, y + 15))
            screen.blit(weight_text, (x + 10, y + 45))
        
        instr = FONT_SMALL.render(self.instruction, True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 250, 600))
    
    def get_hint(self):
        return f"Obě strany musí vážit {self.total_weight}g!"

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
                self.player_grid[i][j] = int(event.unicode)
                if self.check_win():
                    self.won = True
            elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                self.player_grid[i][j] = 0
    
    def check_win(self):
        return self.player_grid == self.solution
    
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
        return "Každé číslo se smí vyskytovat jen jednou!"

class CaesarCipher(BaseGame):
    """Caesarova šifra"""
    def __init__(self):
        super().__init__()
        self.words = [
            {"encrypted": "KHOOR", "original": "AHOJ", "shift": 3},
            {"encrypted": "ZRUOG", "original": "WORLD", "shift": 3},
            {"encrypted": "KHOOR", "original": "AHOJ", "shift": 3},
        ]
        self.current = random.choice(self.words)
        self.answer = ""
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.answer = self.answer[:-1]
            elif event.key == pygame.K_RETURN:
                if self.answer.upper() == self.current["original"]:
                    self.won = True
                else:
                    self.lost = True
            elif event.unicode.isalpha():
                self.answer += event.unicode.upper()
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("CAESAROVA ŠIFRA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 200, 30))
        
        encrypted = FONT_LARGE.render(self.current["encrypted"], True, YELLOW)
        encrypted_rect = encrypted.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(encrypted, encrypted_rect)
        
        # Abeceda
        alpha_text = FONT_SMALL.render(self.alphabet, True, WHITE)
        screen.blit(alpha_text, (100, 300))
        
        shifted = ""
        for i in range(26):
            shifted += self.alphabet[(i + self.current["shift"]) % 26]
        shifted_text = FONT_SMALL.render(shifted, True, CYAN)
        screen.blit(shifted_text, (100, 350))
        
        answer_text = FONT_MEDIUM.render(self.answer + "_", True, WHITE)
        answer_rect = answer_text.get_rect(center=(SCREEN_WIDTH//2, 500))
        pygame.draw.rect(screen, BLUE, pygame.Rect(answer_rect.x - 20, answer_rect.y - 20, answer_rect.width + 40, answer_rect.height + 40))
        screen.blit(answer_text, answer_rect)
        
        instr = FONT_SMALL.render(f"Posun: {self.current['shift']} pozic | Napiš původní slovo", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 300, 600))
    
    def get_hint(self):
        return f"Posun je {self.current['shift']}"

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
    """Zamíchané slovo"""
    def __init__(self):
        super().__init__()
        self.word_pairs = [
            ("AHOJ", "HOJA"),
            ("HLAVA", "AALHV"),
            ("PSANÍ", "NASIP"),
            ("OKNO", "ONKO"),
            ("STŮL", "SULT"),
            ("KNIHA", "NHKIA"),
            ("BARVA", "VARBA"),
            ("SŮNCE", "UNCES"),
            ("MĚSTO", "STEMÓ"),
            ("TRÁVA", "VAART"),
            ("CHLEB", "HCBLE"),
            ("VODA", "ADOV"),
            ("MRAKY", "YAMRK"),
            ("KŮRA", "URKA"),
            ("VÍTR", "RIVT"),
            ("OHEŇ", "HENÖ"),
            ("ZÁPAD", "PADÁZ"),
            ("VÝCHOD", "CHYDOV"),
            ("SEVER", "REVSÉ"),
            ("SLANÝ", "NÁLYSA"),
        ]
        
        self.current_pair = random.choice(self.word_pairs)
        self.original = self.current_pair[0]
        self.scrambled = list(self.current_pair[1])
        self.answer_positions = [0] * len(self.scrambled)
        self.selected = None
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Klik na scrambled
            for i in range(len(self.scrambled)):
                x = 200 + i * 80
                y = 300
                if pygame.Rect(x, y, 60, 60).collidepoint(pos):
                    self.selected = i
            
            # Klik na řešení
            for i in range(len(self.original)):
                x = 200 + i * 80
                y = 450
                if pygame.Rect(x, y, 60, 60).collidepoint(pos) and self.selected is not None:
                    self.answer_positions[self.selected] = i
                    self.selected = None
                    
                    # Kontrola výhry
                    current_word = ""
                    for idx in range(len(self.scrambled)):
                        current_word += self.scrambled[idx]
                    
                    if self.check_win():
                        self.won = True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and self.selected is not None:
                self.answer_positions[self.selected] = 0
                self.selected = None
    
    def check_win(self):
        current_word = ""
        for idx, char in enumerate(self.scrambled):
            pos = self.answer_positions[idx]
            current_word += char
        
        # Kontrola zda slovo odpovídá
        current_arrangement = [None] * len(self.original)
        for idx, char in enumerate(self.scrambled):
            pos = self.answer_positions[idx]
            if pos > 0:
                current_arrangement[pos - 1] = char
        
        return ''.join(filter(None, current_arrangement)) == self.original
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("SEŘAĎ SLOVO", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 140, 50))
        
        hint_text = FONT_SMALL.render(f"Slovo má {len(self.original)} písmen", True, YELLOW)
        screen.blit(hint_text, (SCREEN_WIDTH//2 - 150, 150))
        
        # Zamíchané písmena
        for i, char in enumerate(self.scrambled):
            x = 200 + i * 80
            y = 300
            color = CYAN if i == self.selected else BLUE
            pygame.draw.rect(screen, color, pygame.Rect(x, y, 60, 60))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 60, 60), 2)
            
            char_text = FONT_MEDIUM.render(char, True, BLACK)
            char_rect = char_text.get_rect(center=(x + 30, y + 30))
            screen.blit(char_text, char_rect)
        
        # Pole pro odpověď
        for i in range(len(self.original)):
            x = 200 + i * 80
            y = 450
            pygame.draw.rect(screen, GRAY, pygame.Rect(x, y, 60, 60))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 60, 60), 2)
        
        instr = FONT_SMALL.render("Klikni na písmeno a pak na pozici", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 250, 650))
    
    def get_hint(self):
        return f"Správné slovo: {self.original}"


if __name__ == "__main__":
    game = Game()
    game.run()
