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
        self.admin_mode = False
        self.show_hint = False
        self.hint_timer = 0
        self.pause_menu_open = False
        self.show_hint_popup = False
        self.hint_popup_timer = 0
        self.completed_levels = set()
        self.show_coming_soon = False
        self.coming_soon_timer = 0
        

        self.patch_notes = [
            {"version": "1.0.0", "notes": ["Počáteční verze hry", "11 různých herních módů"]},
            {"version": "1.1.0", "notes": ["Opravena mechanika levelů", "Přidány nápovědy"]},
            {"version": "1.2.0", "notes": ["Hezčí a moderní menu", "Opravena logika 2048", "Přidán delay v Simon Says", "Patch notes nyní v Pop-up okně"]},
            {"version": "1.3.0", "notes": ["Opravena chyba SimonSays s nekonečnou smyčkou", "Opravena inicializace TetrisLite", "Odstraněny všechny komentáře ze kódu", "Opraveny chyby v souboru"]},
            {"version": "1.4.0", "notes": ["Nápověda jako popup okno (stiskni N)", "Pause menu s ESC klávesou", "Tlačítka: Continue, Restart (odemyka level 2), Exit", "Simon Says nyní vyžaduje 5 kol místo 7"]},
            {"version": "1.5.0", "notes": ["Bludiště má nyní mnohem více zdí", "Přidán tajný admin mode", "Vylepšená herní vyvážená obtížnost", "Patch notes aktualizovány po každé změně"]},
            {"version": "1.6.0", "notes": ["Bludiště s DFS algoritmem - překrásné", "Coming Soon popup pro hotové levely", "Nápověda přesunuta na N klávesu", "Maze hra zcela přepracována"]}
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
                if level_num in self.completed_levels:
                    pygame.draw.rect(self.screen, GREEN, button.rect)
                    pygame.draw.rect(self.screen, YELLOW, button.rect, 3)
                    done_text = FONT_SMALL.render(f"LEVEL {level_num}", True, BLACK)
                else:
                    button.draw(self.screen)
            else:
                pygame.draw.rect(self.screen, DARK_GRAY, button.rect)
                pygame.draw.rect(self.screen, GRAY, button.rect, 3)
                lock_text = FONT_SMALL.render("LOCKED", True, RED)
                lock_rect = lock_text.get_rect(center=button.rect.center)
                self.screen.blit(lock_text, lock_rect)
        
        self.play_buttons["back"].draw(self.screen)
        
        if self.show_coming_soon:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            coming_text = FONT_LARGE.render("COMING SOON", True, YELLOW)
            coming_rect = coming_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(coming_text, coming_rect)
    
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
                if level_num in self.completed_levels:
                    self.show_coming_soon = True
                    self.coming_soon_timer = 180
                else:
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
        if self.game_won:
            self.completed_levels.add(self.current_level)
        
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
            ButtonFinder(),
            Maze(),
            TetrisLite(),
            Game2048(),
            BalanceGame(),
            RiddleGame(),
            SudokuLite(),
            MemoryCards(),
            SwitchGame(),
            MathQuiz(),
            SpeedClick(),
            PatternFollow(),
            NumberSort(),
            ImageMatch(),
            ReactionTime(),
            PipeConnect(),
            LaserMirrors(),
            FindDifferences(),
            MasterChallenge()
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
                    self.admin_mode = not self.admin_mode
                    if self.admin_mode:
                        self.unlocked_levels = 20
                    else:
                        self.unlocked_levels = 1
                if self.state == GameState.GAME:
                    if event.key == pygame.K_ESCAPE:
                        if not self.level_completed:
                            self.pause_menu_open = not self.pause_menu_open
                    elif not self.level_completed and not self.pause_menu_open:
                        self.current_game.handle_event(event)
                        if event.key == pygame.K_n:
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
        
        if self.coming_soon_timer > 0:
            self.coming_soon_timer -= 1
        else:
            self.show_coming_soon = False
    
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
    """Bludiště s lepší strukturou - naviguj k cíli"""
    def __init__(self):
        super().__init__()
        self.player_x = 0
        self.player_y = 0
        self.goal_x = 63
        self.goal_y = 35
        self.CELL_SIZE = 30
        self.COLS = 64
        self.ROWS = 36
        self.grid = self.create_grid()
        self.generate_maze()
        self.speed = 1
        self.keys_pressed = set()
    
    def create_grid(self):
        """Vytvoří mřížku buněk"""
        return [[self.Cell(x, y) for y in range(self.ROWS)] for x in range(self.COLS)]
    
    class Cell:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.walls = [True, True, True, True]
            self.visited = False
    
    def generate_maze(self):
        """Generuje bludiště s DFS algoritmem"""
        stack = []
        current = self.grid[0][0]
        current.visited = True
        
        while True:
            neighbors = self.get_unvisited_neighbors(current)
            if neighbors:
                next_cell, direction = random.choice(neighbors)
                self.remove_walls(current, next_cell, direction)
                stack.append(current)
                current = next_cell
                current.visited = True
            elif stack:
                current = stack.pop()
            else:
                break
    
    def get_unvisited_neighbors(self, cell):
        """Vrací nenavštívené sousedy buňky"""
        neighbors = []
        directions = [(0, -1, 0), (1, 0, 1), (0, 1, 2), (-1, 0, 3)]
        
        for dx, dy, dir_idx in directions:
            nx = cell.x + dx
            ny = cell.y + dy
            if 0 <= nx < self.COLS and 0 <= ny < self.ROWS:
                neighbor = self.grid[nx][ny]
                if not neighbor.visited:
                    neighbors.append((neighbor, dir_idx))
        return neighbors
    
    def remove_walls(self, current, next_cell, direction):
        """Odstraní zdi mezi buňkami"""
        current.walls[direction] = False
        next_cell.walls[(direction + 2) % 4] = False
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
    
    def update(self):
        """Kontinuální pohyb na základě stisknutých kláves"""
        if not self.keys_pressed:
            return
        
        keys = self.keys_pressed
        cell = self.grid[self.player_x][self.player_y]
        new_x, new_y = self.player_x, self.player_y
        
        if (pygame.K_w in keys or pygame.K_UP in keys) and not cell.walls[0]:
            new_y -= self.speed
        if (pygame.K_s in keys or pygame.K_DOWN in keys) and not cell.walls[2]:
            new_y += self.speed
        if (pygame.K_a in keys or pygame.K_LEFT in keys) and not cell.walls[3]:
            new_x -= self.speed
        if (pygame.K_d in keys or pygame.K_RIGHT in keys) and not cell.walls[1]:
            new_x += self.speed
        
        if 0 <= new_x < self.COLS and 0 <= new_y < self.ROWS:
            self.player_x = new_x
            self.player_y = new_y
        
        if self.player_x == self.goal_x and self.player_y == self.goal_y:
            self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        for column in self.grid:
            for cell in column:
                x = cell.x * self.CELL_SIZE
                y = cell.y * self.CELL_SIZE
                
                if cell.walls[0]:
                    pygame.draw.line(screen, GRAY, (x, y), (x + self.CELL_SIZE, y), 2)
                if cell.walls[1]:
                    pygame.draw.line(screen, GRAY, (x + self.CELL_SIZE, y), (x + self.CELL_SIZE, y + self.CELL_SIZE), 2)
                if cell.walls[2]:
                    pygame.draw.line(screen, GRAY, (x + self.CELL_SIZE, y + self.CELL_SIZE), (x, y + self.CELL_SIZE), 2)
                if cell.walls[3]:
                    pygame.draw.line(screen, GRAY, (x, y + self.CELL_SIZE), (x, y), 2)
        
        goal_x = self.goal_x * self.CELL_SIZE + self.CELL_SIZE // 2
        goal_y = self.goal_y * self.CELL_SIZE + self.CELL_SIZE // 2
        pygame.draw.rect(screen, GREEN, pygame.Rect(self.goal_x * self.CELL_SIZE + 5, self.goal_y * self.CELL_SIZE + 5, self.CELL_SIZE - 10, self.CELL_SIZE - 10))
        
        player_x = self.player_x * self.CELL_SIZE + self.CELL_SIZE // 2
        player_y = self.player_y * self.CELL_SIZE + self.CELL_SIZE // 2
        pygame.draw.circle(screen, CYAN, (player_x, player_y), self.CELL_SIZE // 3)
        
        instr = FONT_SMALL.render("DRŽÍ WSAD nebo ŠIPKY - Naviguj k cíli (zelený čtverec)", True, WHITE)
        screen.blit(instr, (20, SCREEN_HEIGHT - 50))
    
    def get_hint(self):
        return "Pohybuj se WSAD/šipkami. Najdi cestu!"

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
    """Najdi tlačítko - logická hra"""
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.target_label = "SPRÁVNÉ"
        self.create_buttons()
    
    def create_buttons(self):
        """Vytvoří tlačítka s popisem"""
        self.buttons = []
        self.target_button = random.randint(0, 8)
        
        labels = [
            "KLIKNI", "FALEŠNÉ", "ŠPATNĚ", 
            "NEEE", "SPRÁVNÉ", "NENE",
            "JE TO", "TAM", "KLIPY"
        ]
        
        for i in range(9):
            x = 150 + (i % 3) * 300
            y = 250 + (i // 3) * 150
            self.buttons.append({"rect": pygame.Rect(x, y, 150, 100), "label": labels[i]})
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i, btn in enumerate(self.buttons):
                if btn["rect"].collidepoint(pos):
                    if btn["label"] == self.target_label:
                        self.won = True
                    else:
                        self.lost = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("NAJDI TLAČÍTKO", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 170, 30))
        
        target = FONT_MEDIUM.render(f"Hledej: {self.target_label}", True, YELLOW)
        screen.blit(target, (SCREEN_WIDTH//2 - 150, 150))
        
        for i, btn in enumerate(self.buttons):
            color = BLUE
            pygame.draw.rect(screen, color, btn["rect"])
            pygame.draw.rect(screen, WHITE, btn["rect"], 3)
            
            text = FONT_SMALL.render(btn["label"], True, BLACK)
            screen.blit(text, (btn["rect"].x + 30, btn["rect"].y + 30))
        
        instr = FONT_SMALL.render("Klikni na tlačítko se správným popisem!", True, GREEN)
        screen.blit(instr, (SCREEN_WIDTH//2 - 250, 700))
    
    def get_hint(self):
        return f"Hledáš tlačítko: {self.target_label}"

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
    """Zamíchané slovo - roztřída písmena správně"""
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
            ("VÝCHOD", "CCHODV"),
            ("SEVER", "REVSÉ"),
            ("SLANÝ", "NÁLSY"),
        ]
        
        self.current_pair = random.choice(self.word_pairs)
        self.original = self.current_pair[0]
        self.scrambled = list(self.current_pair[1])
        self.answer = [""] * len(self.original)
        self.used = [False] * len(self.scrambled)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            for i in range(len(self.scrambled)):
                if self.used[i]:
                    continue
                x = 100 + i * 90
                y = 300
                if pygame.Rect(x, y, 70, 70).collidepoint(pos):
                    for j in range(len(self.answer)):
                        if self.answer[j] == "":
                            self.answer[j] = self.scrambled[i]
                            self.used[i] = True
                            self.check_win()
                            return
    
    def check_win(self):
        current = "".join(self.answer)
        if current == self.original:
            self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("SEŘAĎ SLOVO", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 140, 30))
        
        instr1 = FONT_SMALL.render("Klikejte postupně na písmena v pořadí", True, YELLOW)
        screen.blit(instr1, (SCREEN_WIDTH//2 - 250, 120))
        
        for i in range(len(self.original)):
            x = 100 + i * 90
            y = 200
            color = GREEN if self.answer[i] != "" else BLUE
            pygame.draw.rect(screen, color, pygame.Rect(x, y, 70, 70))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 70, 70), 2)
            
            if self.answer[i]:
                char_text = FONT_MEDIUM.render(self.answer[i], True, BLACK)
                char_rect = char_text.get_rect(center=(x + 35, y + 35))
                screen.blit(char_text, char_rect)
        
        avail_text = FONT_SMALL.render("DOSTUPNÁ PÍSMENA:", True, CYAN)
        screen.blit(avail_text, (100, 350))
        
        for i, char in enumerate(self.scrambled):
            if self.used[i]:
                continue
            x = 100 + i * 90
            y = 420
            pygame.draw.rect(screen, BLUE, pygame.Rect(x, y, 70, 70))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 70, 70), 2)
            
            char_text = FONT_MEDIUM.render(char, True, BLACK)
            char_rect = char_text.get_rect(center=(x + 35, y + 35))
            screen.blit(char_text, char_rect)
        
        instr2 = FONT_SMALL.render("Slovo musí mít {} písmen".format(len(self.original)), True, WHITE)
        screen.blit(instr2, (SCREEN_WIDTH//2 - 200, 700))
    
    def get_hint(self):
        return f"Správné slovo: {self.original}"


class MemoryCards(BaseGame):
    """Hra na paměť - otočit karty a najít páry"""
    def __init__(self):
        super().__init__()
        self.symbols = ['🌟', '🎮', '🎨', '❤️'] 
        self.cards = self.symbols + self.symbols
        random.shuffle(self.cards)
        self.revealed = [False] * 8
        self.matched = [False] * 8
        self.selected = []
        self.matches = 0
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and len(self.selected) < 2:
            pos = event.pos
            for i in range(8):
                x = 300 + (i % 4) * 150
                y = 300 + (i // 4) * 150
                if pygame.Rect(x, y, 120, 120).collidepoint(pos):
                    if not self.matched[i] and i not in self.selected:
                        self.selected.append(i)
                        self.revealed[i] = True
                        if len(self.selected) == 2:
                            if self.cards[self.selected[0]] == self.cards[self.selected[1]]:
                                self.matched[self.selected[0]] = True
                                self.matched[self.selected[1]] = True
                                self.matches += 1
                                self.selected = []
                                if self.matches == 4:
                                    self.won = True
                            else:
                                self.revealed[self.selected[0]] = False
                                self.revealed[self.selected[1]] = False
                                self.selected = []
                        break
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("MEMORY KARTY", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 50))
        
        for i in range(8):
            x = 300 + (i % 4) * 150
            y = 300 + (i // 4) * 150
            color = GREEN if self.matched[i] else BLUE
            pygame.draw.rect(screen, color, pygame.Rect(x, y, 120, 120))
            if self.revealed[i]:
                text = FONT_LARGE.render(self.cards[i], True, YELLOW)
                screen.blit(text, (x + 30, y + 30))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 120, 120), 3)
        
        info = FONT_SMALL.render(f"Páry: {self.matches}/4", True, WHITE)
        screen.blit(info, (SCREEN_WIDTH//2 - 100, 700))
    
    def get_hint(self):
        return "Zapamatuj si pozice karet!"


class MathQuiz(BaseGame):
    """Matematický kvíz"""
    def __init__(self):
        super().__init__()
        self.num1 = random.randint(1, 20)
        self.num2 = random.randint(1, 20)
        self.operation = random.choice(['+', '-', '*'])
        if self.operation == '+':
            self.answer = self.num1 + self.num2
        elif self.operation == '-':
            self.answer = self.num1 - self.num2
        else:
            self.answer = self.num1 * self.num2
        self.options = [self.answer, self.answer + random.randint(-10, 10), self.answer + random.randint(-10, 10)]
        random.shuffle(self.options)
        self.correct_index = self.options.index(self.answer)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i in range(3):
                x = 200 + i * 400
                y = 400
                if pygame.Rect(x, y, 300, 100).collidepoint(pos):
                    if i == self.correct_index:
                        self.won = True
                    else:
                        self.lost = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("MATEMATIKA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 50))
        
        question = FONT_LARGE.render(f"{self.num1} {self.operation} {self.num2} = ?", True, YELLOW)
        screen.blit(question, (SCREEN_WIDTH//2 - 200, 200))
        
        for i in range(3):
            x = 200 + i * 400
            y = 400
            pygame.draw.rect(screen, BLUE, pygame.Rect(x, y, 300, 100))
            text = FONT_MEDIUM.render(str(self.options[i]), True, WHITE)
            screen.blit(text, (x + 100, y + 25))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 300, 100), 3)
    
    def get_hint(self):
        return f"Odpověď: {self.answer}"


class SpeedClick(BaseGame):
    """Klikej rychle na bílé čtverce"""
    def __init__(self):
        super().__init__()
        self.targets = []
        self.clicked = 0
        self.timer = 0
        self.generate_targets()
    
    def generate_targets(self):
        self.targets = []
        for _ in range(10):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(200, SCREEN_HEIGHT - 200)
            self.targets.append(pygame.Rect(x, y, 60, 60))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for i, target in enumerate(self.targets):
                if target.collidepoint(pos):
                    self.targets.pop(i)
                    self.clicked += 1
                    if self.clicked == 10:
                        self.won = True
                    break
    
    def update(self):
        self.timer += 1
        if self.timer > 300:
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


class ImageMatch(BaseGame):
    """Najdi párová slova"""
    def __init__(self):
        super().__init__()
        self.words = ['OHEŇ', 'VODA', 'VZDUCH', 'PŘÍRODA', 'HVĚZDA', 'JEZERO']
        self.pairs = []
        for word in self.words:
            self.pairs.extend([word, word])
        random.shuffle(self.pairs)
        self.matched = [False] * 12
        self.selected = []
        self.matches = 0
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and len(self.selected) < 2:
            pos = event.pos
            for i in range(12):
                x = 200 + (i % 6) * 200
                y = 300 + (i // 6) * 200
                if pygame.Rect(x, y, 150, 150).collidepoint(pos):
                    if not self.matched[i] and i not in self.selected:
                        self.selected.append(i)
                        if len(self.selected) == 2:
                            if self.pairs[self.selected[0]] == self.pairs[self.selected[1]]:
                                self.matched[self.selected[0]] = True
                                self.matched[self.selected[1]] = True
                                self.matches += 1
                                if self.matches == 6:
                                    self.won = True
                            self.selected = []
                        break
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("KOMBINUJ SLOVA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 180, 30))
        
        for i in range(12):
            x = 200 + (i % 6) * 200
            y = 300 + (i // 6) * 200
            color = GREEN if self.matched[i] else BLUE
            pygame.draw.rect(screen, color, pygame.Rect(x, y, 150, 150))
            if self.matched[i]:
                text = FONT_TINY.render(self.pairs[i], True, YELLOW)
                text_rect = text.get_rect(center=(x + 75, y + 75))
                screen.blit(text, text_rect)
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 150, 150), 3)
        
        info = FONT_SMALL.render(f"Páry: {self.matches}/6", True, WHITE)
        screen.blit(info, (SCREEN_WIDTH//2 - 100, 700))
    
    def get_hint(self):
        return "Najdi stejná slova!"


class ReactionTime(BaseGame):
    """Test reflexu - čekej a klikni když změní barvu"""
    def __init__(self):
        super().__init__()
        self.timer = 0
        self.show_target = False
        self.start_time = 0
        self.reaction_time = 0
        self.color_phase = 0
        self.change_timer = random.randint(120, 300)
    
    def update(self):
        self.timer += 1
        if self.timer == self.change_timer:
            self.show_target = True
            self.start_time = self.timer
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.show_target:
            self.reaction_time = self.timer - self.start_time
            if self.reaction_time < 100:
                self.won = True
            else:
                self.lost = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("REFLEX TEST", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 50))
        
        if self.show_target:
            progress = (self.timer - self.start_time) / 20
            size = int(600 + progress * 100)
            box_x = SCREEN_WIDTH//2 - size//2
            box_y = 300 - size//4
            pygame.draw.rect(screen, GREEN, pygame.Rect(box_x, box_y, size, size // 2))
            text = FONT_LARGE.render("KLIKNI!", True, YELLOW)
            screen.blit(text, (SCREEN_WIDTH//2 - 100, 450))
        else:
            pygame.draw.rect(screen, RED, pygame.Rect(600, 300, 600, 400))
            text = FONT_MEDIUM.render("Čekej na změnu barvy...", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - 250, 450))
    
    def get_hint(self):
        return "Čekej na zelenou barvu a klikni!"


class Hangman(BaseGame):
    """Hádat slovo - Oběšenec"""
    def __init__(self):
        super().__init__()
        self.words = ["PYTHON", "PROGRAM", "VIDEHRA", "LOGIKA", "PUZZLE"]
        self.word = random.choice(self.words)
        self.guessed = set()
        self.wrong = 0
        self.max_wrong = 6
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
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
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("OBĚŠENEC", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        word_display = " ".join(l if l in self.guessed else "_" for l in self.word)
        word_text = FONT_LARGE.render(word_display, True, YELLOW)
        screen.blit(word_text, (SCREEN_WIDTH//2 - 200, 200))
        
        guessed_text = FONT_SMALL.render(f"Hádaná písmena: {' '.join(sorted(self.guessed))}", True, WHITE)
        screen.blit(guessed_text, (SCREEN_WIDTH//2 - 300, 350))
        
        wrong_text = FONT_MEDIUM.render(f"Chyby: {self.wrong}/{self.max_wrong}", True, RED)
        screen.blit(wrong_text, (SCREEN_WIDTH//2 - 150, 500))
    
    def get_hint(self):
        return f"Slovo: {self.word}"


class ColorBlind(BaseGame):
    """Najdi jinou barvu"""
    def __init__(self):
        super().__init__()
        self.base_color = random.choice([RED, BLUE, YELLOW, GREEN])
        self.different_color = [RED, BLUE, YELLOW, GREEN]
        self.different_color.remove(self.base_color)
        self.different_color = random.choice(self.different_color)
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
                        self.won = True
                    else:
                        self.lost = True
                    break
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        title = FONT_LARGE.render("NAJDI ROZDÍL", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        for i in range(16):
            x = 300 + (i % 4) * 200
            y = 250 + (i // 4) * 200
            color = self.different_color if self.positions[i] == self.different_pos else self.base_color
            pygame.draw.rect(screen, color, pygame.Rect(x, y, 150, 150))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x, y, 150, 150), 2)
    
    def get_hint(self):
        return "Najdi barvu která se liší!"


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
        self.pipes = self.create_grid()
        self.start_pos = (0, 1)
        self.end_pos = (3, 2)
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
                    pygame.draw.lines(screen, YELLOW, points[rotation], 3)
        
        instr = FONT_SMALL.render("Klikni na trubku pro otočení - propoj zdroj s cílem", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 310, 700))
    
    def get_hint(self):
        return "Otáčej trubky, aby se zdroj (zelený) připojil k cíli (červený)"


class LaserMirrors(BaseGame):
    """Laserová zrcadla - nasměruj laser na cíl"""
    def __init__(self):
        super().__init__()
        self.laser_start = (100, 540)
        self.laser_direction = 0
        self.target = (1800, 540)
        self.mirrors = [
            {"pos": (600, 400), "angle": 45},
            {"pos": (1200, 600), "angle": 45},
            {"pos": (1500, 400), "angle": 45}
        ]
        self.laser_path = []
    
    def trace_laser(self):
        """Vysleduje cestu laseru skrz zrcadla"""
        self.laser_path = [(self.laser_start, self.laser_direction)]
        pos = list(self.laser_start)
        direction = self.laser_direction
        max_steps = 100
        
        for _ in range(max_steps):
            next_pos = (pos[0] + 20 * math.cos(math.radians(direction)), 
                       pos[1] + 20 * math.sin(math.radians(direction)))
            
            for mirror in self.mirrors:
                mx, my = mirror["pos"]
                if abs(next_pos[0] - mx) < 30 and abs(next_pos[1] - my) < 30:
                    direction = (direction + 2 * mirror["angle"]) % 360
                    self.laser_path.append((next_pos, direction))
            
            if self.distance(next_pos, self.target) < 50:
                self.won = True
                return
            
            pos = next_pos
            if pos[0] < 0 or pos[0] > SCREEN_WIDTH or pos[1] < 0 or pos[1] > SCREEN_HEIGHT:
                break
    
    def distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for mirror in self.mirrors:
                mx, my = mirror["pos"]
                if pygame.Rect(mx - 30, my - 30, 60, 60).collidepoint(pos):
                    mirror["angle"] = (mirror["angle"] + 45) % 360
                    self.trace_laser()
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("LASEROVÁ ZRCADLA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 200, 30))
        
        pygame.draw.circle(screen, GREEN, self.laser_start, 15)
        pygame.draw.circle(screen, RED, self.target, 15)
        
        for mirror in self.mirrors:
            mx, my = mirror["pos"]
            pygame.draw.rect(screen, YELLOW, pygame.Rect(mx - 20, my - 20, 40, 40))
            angle = mirror["angle"]
            end_x = mx + 30 * math.cos(math.radians(angle))
            end_y = my + 30 * math.sin(math.radians(angle))
            pygame.draw.line(screen, WHITE, (mx - 30 * math.cos(math.radians(angle)), 
                                             my - 30 * math.sin(math.radians(angle))),
                            (end_x, end_y), 2)
        
        if self.laser_path:
            for i in range(len(self.laser_path) - 1):
                pos, direction = self.laser_path[i]
                next_pos, _ = self.laser_path[i + 1] if i + 1 < len(self.laser_path) else (list(pos), direction)
                pygame.draw.line(screen, CYAN, pos, next_pos, 3)
        
        instr = FONT_SMALL.render("Klikni na zrcadla pro otočení - vede laser k červenému cíli", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 330, 700))
    
    def get_hint(self):
        return "Otáčej zrcadla tak, aby laser (zelená kroužek) dosáhl cíle (červený kroužek)"


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


if __name__ == "__main__":
    game = Game()
    game.run()

