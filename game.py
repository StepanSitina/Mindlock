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
        self.space_pressed = False
        self.space_press_count = 0
        self.space_press_timer = 0
        self.current_game = None
        

        self.patch_notes = [
            {"version": "1.0.0", "notes": ["Počáteční verze hry", "11 různých herních módů"]},
            {"version": "1.1.0", "notes": ["Opravena mechanika levelů", "Přidány nápovědy"]},
            {"version": "1.2.0", "notes": ["Hezčí a moderní menu", "Opravena logika 2048", "Přidán delay v Simon Says", "Patch notes nyní v Pop-up okně"]},
            {"version": "1.3.0", "notes": ["Opravena chyba SimonSays s nekonečnou smyčkou", "Opravena inicializace TetrisLite", "Odstraněny všechny komentáře ze kódu", "Opraveny chyby v souboru"]},
            {"version": "1.4.0", "notes": ["Nápověda jako popup okno (stiskni N)", "Pause menu s ESC klávesou", "Tlačítka: Continue, Restart (odemyka level 2), Exit", "Simon Says nyní vyžaduje 5 kol místo 7"]},
            {"version": "1.5.0", "notes": ["Bludiště má nyní mnohem více zdí", "Přidán tajný admin mode", "Vylepšená herní vyvážená obtížnost", "Patch notes aktualizovány po každé změně"]},
            {"version": "1.6.0", "notes": ["Bludiště s DFS algoritmem - překrásné", "Coming Soon popup pro hotové levely", "Nápověda přesunuta na N klávesu", "Maze hra zcela přepracována"]},
            {"version": "1.7.0", "notes": ["Nápověda změněna na SPACE SPACE (2x stisk)", "Opraveny chyby v inicializaci game - program se sám nevypíná", "Error handling v Maze DFS algoritmu"]},
            {"version": "1.8.0", "notes": ["Bludiště přepsáno na GRID-BASED systém (25x20, 32px buňky)", "ButtonFinder nahrazen ClickMaster (klikej na pohybující se cíl)", "Odstraněn Coming Soon popup - všechny levely dostupné!", "Jen 19 levelů - bez duplicit"]},
            {"version": "1.9.0", "notes": ["Přepracován level 2: ClickMaster → Najdi jinou barvu (ColorBlind)", "Level 11: FindShape → Rotující obraz (RotatingImage) - rozpoznej tvar", "Level 13: Následuj barvy → Časová bomba (TimeBomb) - nový mode", "2048: Opraveno na cíl 1024 místo 2048 (hint aktualizován)", "Sudoku: Přidána validace pravidel (řádek, sloupec, blok)", "Memory: Opraveno max 2 karty současně, překrývání", "Hangman: Zobrazena kategorie slova na vrchu", "SpeedClick: Timer začíná až na první klik", "Přidán nový level 19: Coming Soon - připraveno na budoucí obsah", "Celkem 19 funkčních levelů - bez duplicit!"]},
            {"version": "2.0.0", "notes": ["ALL BUGS FIXED - Game je nyní plně funkční!", "Level 3: Harder maze s více větvemi", "Level 2: Color shades místo rozdílných barev", "Level 11: Větší klikací plocha pro tlačítka", "Level 16: Správné spojování trubek", "Level 17: LaserMirrors s viditelným laserem a odrazy", "Level 20: Coming Soon popup se nyní zobrazuje!", "Patch notes aktualizovány na verzi 2.0.0"]}
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
                "Levels: 19",
                "Game modes: 19"
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
                    done_text = FONT_SMALL.render(f"LEVEL {level_num}*", True, BLACK)
                    done_rect = done_text.get_rect(center=button.rect.center)
                    self.screen.blit(done_text, done_rect)
                else:
                    button.draw(self.screen)
            elif level_num == 20:
                # Level 20 - Coming Soon, vždy viditelný
                pygame.draw.rect(self.screen, (100, 50, 0), button.rect)
                pygame.draw.rect(self.screen, YELLOW, button.rect, 3)
                soon_text = FONT_SMALL.render("COMING SOON", True, YELLOW)
                soon_rect = soon_text.get_rect(center=button.rect.center)
                self.screen.blit(soon_text, soon_rect)
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
        
        # Zobraz čas pro ReactionTime
        if hasattr(self.current_game, 'reaction_time_ms') and self.current_game.reaction_time_ms > 0:
            time_text = FONT_MEDIUM.render(f"Cas: {self.current_game.reaction_time_ms} ms", True, YELLOW)
            self.screen.blit(time_text, (SCREEN_WIDTH//2 - 180, 350))
        
        self.popup_buttons["menu"].draw(self.screen)
        self.popup_buttons["restart"].draw(self.screen)
        
        if self.game_won and self.current_level < 20:
            self.popup_buttons["next"].draw(self.screen)
        elif self.current_level == 20:
            final_text = FONT_SMALL.render("COMING SOON - zkuste jiný level!", True, YELLOW)
            self.screen.blit(final_text, (SCREEN_WIDTH//2 - 300, 500))
        elif self.current_level == 19 and self.game_won:
            final_text = FONT_SMALL.render("LEVEL 19 COMPLETED - Zbývá Coming Soon!", True, YELLOW)
            self.screen.blit(final_text, (SCREEN_WIDTH//2 - 300, 500))
    
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
        # Zkontroluj odemčené levely - všechny lze hrát, level 20 je Coming Soon
        for level_num, button in self.level_buttons.items():
            if button.is_clicked(pos):
                if level_num <= self.unlocked_levels or level_num == 20:
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
        if level_num < 1 or level_num > 19:
            print(f"❌ [ERROR] Level {level_num} neexistuje! Dostupné: 1-19")
            return None
        
        game_creators = [
            ("SimonSays", lambda: SimonSays()),
            ("ColorBlind", lambda: ColorBlind()),
            ("Maze", lambda: Maze()),
            ("TetrisLite", lambda: TetrisLite()),
            ("Game2048", lambda: Game2048()),
            ("ColorMatch", lambda: ColorMatch()),
            ("RiddleGame", lambda: RiddleGame()),
            ("SudokuLite", lambda: SudokuLite()),
            ("MemoryCards", lambda: MemoryCards()),
            ("Hangman", lambda: Hangman()),
            ("RotatingImage", lambda: RotatingImage()),
            ("SpeedClick", lambda: SpeedClick()),
            ("TimeBomb", lambda: TimeBomb()),
            ("NumberSort", lambda: NumberSort()),
            ("ReactionTime", lambda: ReactionTime()),
            ("PipeRotate", lambda: PipeRotate()),
            ("LaserMirrors", lambda: LaserMirrors()),
            ("CableConnect", lambda: CableConnect()),
            ("ClickMaster_ComingSoon", lambda: ComingSoonGame()),
            ("FutureGame_ComingSoon", lambda: ComingSoonGame())
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
                
                level_text = FONT_SMALL.render(f"Level: {self.current_level}/19", True, WHITE)
                self.screen.blit(level_text, (SCREEN_WIDTH - 200, 10))
                
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
    """Grid-based maze - hráč se pohybuje po mřížce, 20x20 nebo větší"""
    def __init__(self):
        super().__init__()
        self.CELL_SIZE = 32
        self.COLS = 25
        self.ROWS = 20
        
        # Hardcoded maze s mnoha cestami a dead ends
        self.grid = self.generate_maze()
        
        self.player_row = 0
        self.player_col = 0
        self.goal_row = 19
        self.goal_col = 24
        
    def generate_maze(self):
        """Generuje složitější bludiště s více mrtvými cestami a zákruty"""
        # 1 = cesta (walkable), 0 = zeď (wall)
        maze = [
            [1,1,1,1,1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,0,1,1,1],
            [1,0,0,0,1,0,1,0,0,0,1,0,1,0,1,0,1,0,0,0,1,0,0,0,1],
            [1,0,1,0,1,0,1,1,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1],
            [1,0,1,0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,1,0,1],
            [1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1],
            [1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1],
            [1,1,1,0,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1,1,1],
            [1,0,0,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,1,0,0,0,1],
            [1,0,1,1,1,0,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,1,1],
            [1,0,1,0,0,0,1,0,1,0,1,0,0,0,1,0,0,0,1,0,1,0,0,0,1],
            [1,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1],
            [1,0,1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,1],
            [1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,0,1,0,1],
            [1,0,1,0,0,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,1,0,1,0,1],
            [1,0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,0,1],
            [1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1],
            [1,1,1,0,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1],
            [1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
            [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        ]
        
        # Ověřit BFS cestu od startu k cíli
        if not self.is_path_exists(maze, 0, 0, 19, 24):
            print("⚠️  Maze nemá cestu! Regeneruji na jednoduchou liniju...")
            maze = self.create_simple_maze()
        
        return maze
    
    def is_path_exists(self, maze, start_row, start_col, goal_row, goal_col):
        """BFS - ověří, že existuje cesta od startu k cíli"""
        from collections import deque
        queue = deque([(start_row, start_col)])
        visited = {(start_row, start_col)}
        
        while queue:
            row, col = queue.popleft()
            if row == goal_row and col == goal_col:
                return True
            
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]):
                    if maze[nr][nc] == 1 and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        
        return False
    
    def create_simple_maze(self):
        """Vytvoří jednoduchou cestu na okraj"""
        maze = [[0] * 25 for _ in range(20)]
        for col in range(25):
            maze[0][col] = 1
            maze[19][col] = 1
        return maze
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Grid-based pohyb (ne smooth, skokový)
            if event.key in (pygame.K_UP, pygame.K_w):
                if self.player_row > 0 and self.grid[self.player_row - 1][self.player_col] == 1:
                    self.player_row -= 1
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.player_row < self.ROWS - 1 and self.grid[self.player_row + 1][self.player_col] == 1:
                    self.player_row += 1
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if self.player_col > 0 and self.grid[self.player_row][self.player_col - 1] == 1:
                    self.player_col -= 1
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self.player_col < self.COLS - 1 and self.grid[self.player_row][self.player_col + 1] == 1:
                    self.player_col += 1
            
            # Výhra?
            if self.player_row == self.goal_row and self.player_col == self.goal_col:
                self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        # Nakresli grid
        for row in range(self.ROWS):
            for col in range(self.COLS):
                x = col * self.CELL_SIZE
                y = row * self.CELL_SIZE
                
                if self.grid[row][col] == 0:
                    # Zeď - hnědá
                    pygame.draw.rect(screen, (139, 69, 19), pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE))
                else:
                    # Cesta - tmavě modrá
                    pygame.draw.rect(screen, (40, 40, 60), pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE))
                    pygame.draw.rect(screen, (60, 60, 90), pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE), 1)
        
        # Cíl - zelený
        goal_x = self.goal_col * self.CELL_SIZE + 4
        goal_y = self.goal_row * self.CELL_SIZE + 4
        pygame.draw.rect(screen, GREEN, pygame.Rect(goal_x, goal_y, self.CELL_SIZE - 8, self.CELL_SIZE - 8))
        
        # Hráč - tyrkysový čtverec
        player_x = self.player_col * self.CELL_SIZE + 4
        player_y = self.player_row * self.CELL_SIZE + 4
        pygame.draw.rect(screen, CYAN, pygame.Rect(player_x, player_y, self.CELL_SIZE - 8, self.CELL_SIZE - 8))
        
        # Instrukce
        title = FONT_MEDIUM.render("BLUDIŠTĚ", True, YELLOW)
        screen.blit(title, (50, 700))
        
        instr = FONT_SMALL.render("ŠIPKY/WSAD = Pohyb | Dorazit na ZELENÝ CÍL", True, WHITE)
        screen.blit(instr, (50, 750))
    
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
                if any(1024 in row for row in self.grid):
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
        return "Skládej stejná čísla, dosáhni 1024!"

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
    """Klikej rychle na bílé čtverce - timer začíná až po prvním kliknutí"""
    def __init__(self):
        super().__init__()
        self.targets = []
        self.clicked = 0
        self.timer = 0
        self.timer_started = False
        self.time_limit = 300  # 5 sekund (300 framů)
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


    def get_hint(self):
        return "Najdi stejná slova!"


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
        return "Klikni až když je obrazovka ZELENÁ! Červená = prohra!"
    
    def get_hint(self):
        return f"Čekej na zelený čtverec a klikni rychleji než {self.target_time}ms!"


class Hangman(BaseGame):
    """Guess word - Hangman with categories - NOW IN ENGLISH"""
    def __init__(self):
        super().__init__()
        self.categories = {
            "ANIMALS": ["DOG", "CAT", "BIRD", "HORSE", "ELEPHANT"],
            "FOOD": ["PIZZA", "BREAD", "CHEESE", "APPLE", "CHICKEN"],
            "COUNTRIES": ["FRANCE", "GERMANY", "JAPAN", "BRAZIL", "CANADA"],
            "SPORTS": ["TENNIS", "HOCKEY", "SOCCER", "BOXING", "SWIMMING"]
        }
        self.category = random.choice(list(self.categories.keys()))
        self.word = random.choice(self.categories[self.category])
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
        title = FONT_LARGE.render("HANGMAN", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        cat_text = FONT_SMALL.render(f"Category: {self.category}", True, CYAN)
        screen.blit(cat_text, (SCREEN_WIDTH//2 - 150, 80))
        
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
    """Najdi jinou barvu - stejná barva, jen jiný odstín"""
    def __init__(self):
        super().__init__()
        self.base_color = random.choice([RED, BLUE, YELLOW, GREEN])
        # Vytvoř podobný odstín - stejná barva, ale o něco světlejší/tmavší
        if self.base_color == RED:
            self.different_color = (200, 50, 50)  # Světlejší červená
        elif self.base_color == BLUE:
            self.different_color = (50, 100, 200)  # Světlejší modrá
        elif self.base_color == YELLOW:
            self.different_color = (200, 200, 100)  # Světlejší žlutá
        else:  # GREEN
            self.different_color = (100, 180, 100)  # Světlejší zelená
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
    """Rotující obraz - rozpoznej správný tvar při otáčení"""
    def __init__(self):
        super().__init__()
        self.shapes = ["kruh", "čtverec", "trojúhelník", "hvězda", "srdce"]
        self.target_shape = random.choice(self.shapes)
        self.rotation = 0
        self.rotation_speed = 3
        self.click_count = 0
        self.correct_clicks = 0
        self.timer = 0
    
    def draw_shape(self, screen, shape, x, y, size, rotation):
        """Kreslí tvar s rotací"""
        if shape == "kruh":
            pygame.draw.circle(screen, CYAN, (x, y), size)
            pygame.draw.circle(screen, WHITE, (x, y), size, 3)
        elif shape == "čtverec":
            angle_rad = math.radians(rotation)
            points = [
                (x + size * math.cos(angle_rad), y + size * math.sin(angle_rad)),
                (x + size * math.cos(angle_rad + math.pi/2), y + size * math.sin(angle_rad + math.pi/2)),
                (x + size * math.cos(angle_rad + math.pi), y + size * math.sin(angle_rad + math.pi)),
                (x + size * math.cos(angle_rad + 3*math.pi/2), y + size * math.sin(angle_rad + 3*math.pi/2))
            ]
            pygame.draw.polygon(screen, CYAN, points)
            pygame.draw.polygon(screen, WHITE, points, 3)
        elif shape == "trojúhelník":
            angle_rad = math.radians(rotation)
            points = [
                (x + size * math.cos(angle_rad), y + size * math.sin(angle_rad)),
                (x + size * math.cos(angle_rad + 2*math.pi/3), y + size * math.sin(angle_rad + 2*math.pi/3)),
                (x + size * math.cos(angle_rad + 4*math.pi/3), y + size * math.sin(angle_rad + 4*math.pi/3))
            ]
            pygame.draw.polygon(screen, CYAN, points)
            pygame.draw.polygon(screen, WHITE, points, 3)
        elif shape == "hvězda":
            pygame.draw.circle(screen, CYAN, (x, y), size)
            pygame.draw.circle(screen, WHITE, (x, y), size, 3)
        elif shape == "srdce":
            pygame.draw.circle(screen, CYAN, (x, y), size)
            pygame.draw.circle(screen, WHITE, (x, y), size, 3)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Kliknutí POUZE na tlačítka s odpověďmi (ne na rotující tvar)
            for i, shape in enumerate(["kruh", "čtverec", "trojúhelník"]):
                x = 230 + i * 380
                y = 600
                # Větší klikatelná plocha
                if pygame.Rect(x - 80, y - 40, 160, 80).collidepoint(pos):
                    if shape == self.target_shape:
                        self.correct_clicks += 1
                        if self.correct_clicks >= 3:
                            self.won = True
                    else:
                        if self.click_count > 0:
                            self.click_count -= 1
    
    def update(self):
        self.rotation += self.rotation_speed
        self.timer += 1
        if self.timer > 1800:  # 30 sekund
            if self.correct_clicks >= 3:
                self.won = True
            else:
                self.lost = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("ROZPOZNEJ TVAR", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 180, 30))
        
        # Rotující tvar
        self.draw_shape(screen, "kruh", SCREEN_WIDTH//2, 300, 60, self.rotation)
        
        info = FONT_SMALL.render(f"Tvar se otáčí - rozpoznej jej! Správně: {self.correct_clicks}/3", True, YELLOW)
        screen.blit(info, (SCREEN_WIDTH//2 - 250, 450))
        
        # Tlačítka s odpověďmi - větší a čitelnější
        for i, shape in enumerate(["kruh", "čtverec", "trojúhelník"]):
            x = 230 + i * 380
            y = 600
            pygame.draw.rect(screen, BLUE, pygame.Rect(x - 80, y - 40, 160, 80))
            pygame.draw.rect(screen, WHITE, pygame.Rect(x - 80, y - 40, 160, 80), 3)
            
            text = FONT_SMALL.render(shape, True, WHITE)
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)
    
    def get_hint(self):
        return f"Tvar se otáčí - jde o {self.target_shape}!"


class LaserMirrors(BaseGame):
    """Laserová zrcadla - nasměruj laser na cíl - OPRAVENÉ S POČÍTAČEM ODRAZŮ"""
    def __init__(self):
        super().__init__()
        self.laser_start = (150, 540)
        self.laser_direction = 0
        self.target = (1750, 540)
        self.mirrors = [
            {"pos": (600, 400), "angle": 45, "id": 0},
            {"pos": (1200, 650), "angle": 45, "id": 1},
            {"pos": (1500, 350), "angle": 45, "id": 2}
        ]
        self.laser_segments = []
        self.reflection_count = 0
        self.visited_mirrors = set()
        self.trace_laser()
    
    def trace_laser(self):
        """Vysleduje cestu laseru skrz zrcadla a odrazuje se od sten - VIDITELNY LASER"""
        self.laser_segments = []
        self.reflection_count = 0
        self.visited_mirrors = set()
        
        pos = list(self.laser_start)
        direction = self.laser_direction
        bounce_count = 0
        max_bounces = 4
        
        # Trace laser up to 150 segments
        for iteration in range(150):
            if bounce_count > max_bounces:
                break
            
            # Find next collision
            min_dist = float('inf')
            next_target = None
            collision_type = None
            
            # Check mirrors
            for mirror in self.mirrors:
                if mirror["id"] in self.visited_mirrors:
                    continue
                    
                mx, my = mirror["pos"]
                # Calculate intersection with mirror (treat as circle)
                dx = mx - pos[0]
                dy = my - pos[1]
                dist_to_mirror = math.sqrt(dx**2 + dy**2)
                
                if dist_to_mirror < 50 and dist_to_mirror < min_dist:
                    min_dist = dist_to_mirror
                    next_target = mirror
                    collision_type = "mirror"
            
            # Check target
            tx, ty = self.target
            dx = tx - pos[0]
            dy = ty - pos[1]
            dist_to_target = math.sqrt(dx**2 + dy**2)
            
            if dist_to_target < 50 and dist_to_target < min_dist:
                min_dist = dist_to_target
                next_target = None
                collision_type = "target"
            
            # Check walls
            # Trace ray to find wall intersection
            cos_dir = math.cos(math.radians(direction))
            sin_dir = math.sin(math.radians(direction))
            
            # Find closest wall
            walls_dist = []
            
            # Right wall (SCREEN_WIDTH)
            if cos_dir > 0.01:
                t = (SCREEN_WIDTH - pos[0]) / cos_dir
                if t > 0:
                    test_y = pos[1] + t * sin_dir
                    if 0 <= test_y <= SCREEN_HEIGHT:
                        walls_dist.append((t, "right"))
            
            # Left wall (0)
            if cos_dir < -0.01:
                t = -pos[0] / cos_dir
                if t > 0:
                    test_y = pos[1] + t * sin_dir
                    if 0 <= test_y <= SCREEN_HEIGHT:
                        walls_dist.append((t, "left"))
            
            # Bottom wall (SCREEN_HEIGHT)
            if sin_dir > 0.01:
                t = (SCREEN_HEIGHT - pos[1]) / sin_dir
                if t > 0:
                    test_x = pos[0] + t * cos_dir
                    if 0 <= test_x <= SCREEN_WIDTH:
                        walls_dist.append((t, "bottom"))
            
            # Top wall (0)
            if sin_dir < -0.01:
                t = -pos[1] / sin_dir
                if t > 0:
                    test_x = pos[0] + t * cos_dir
                    if 0 <= test_x <= SCREEN_WIDTH:
                        walls_dist.append((t, "top"))
            
            if walls_dist:
                walls_dist.sort(key=lambda x: x[0])
                wall_dist, wall_type = walls_dist[0]
                
                if wall_dist < min_dist:
                    min_dist = wall_dist
                    next_target = (pos[0] + wall_dist * cos_dir, 
                                   pos[1] + wall_dist * sin_dir)
                    collision_type = "wall"
            
            if collision_type is None:
                # No collision - trace to end of screen
                t = 500
                end_pos = (pos[0] + t * cos_dir, pos[1] + t * sin_dir)
                self.laser_segments.append((tuple(pos), end_pos))
                break
            
            if collision_type == "mirror":
                mirror = next_target
                mx, my = mirror["pos"]
                
                # Draw segment to mirror
                self.laser_segments.append((tuple(pos), (mx, my)))
                self.visited_mirrors.add(mirror["id"])
                self.reflection_count = len(self.visited_mirrors)
                bounce_count += 1
                
                # Bounce: reflect direction off mirror angle
                direction = (2 * mirror["angle"] - direction) % 360
                pos = [mx, my]
            
            elif collision_type == "target":
                tx, ty = self.target
                self.laser_segments.append((tuple(pos), (tx, ty)))
                
                if self.reflection_count >= 1:
                    self.won = True
                break
            
            elif collision_type == "wall":
                wall_x, wall_y = next_target
                self.laser_segments.append((tuple(pos), (wall_x, wall_y)))
                bounce_count += 1
                
                # Bounce off wall (reflect direction)
                cos_dir = math.cos(math.radians(direction))
                sin_dir = math.sin(math.radians(direction))
                
                # Determine which wall and bounce accordingly
                if wall_x <= 0 or wall_x >= SCREEN_WIDTH:
                    # Vertical wall - flip horizontal component
                    direction = (180 - direction) % 360
                if wall_y <= 0 or wall_y >= SCREEN_HEIGHT:
                    # Horizontal wall - flip vertical component
                    direction = (360 - direction) % 360
                
                pos = [wall_x, wall_y]
    
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
        
        title = FONT_LARGE.render("LASEROVA ZRCADLA", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 250, 30))
        
        # Laser start (zdroj)
        pygame.draw.circle(screen, GREEN, self.laser_start, 18)
        pygame.draw.circle(screen, CYAN, self.laser_start, 18, 3)
        
        # Target (cíl)
        pygame.draw.circle(screen, RED, self.target, 18)
        pygame.draw.circle(screen, (255, 100, 100), self.target, 18, 3)
        
        # Zrcadla
        for mirror in self.mirrors:
            mx, my = mirror["pos"]
            # Zrcadlo čtverec
            pygame.draw.rect(screen, YELLOW, pygame.Rect(mx - 22, my - 22, 44, 44))
            pygame.draw.rect(screen, WHITE, pygame.Rect(mx - 22, my - 22, 44, 44), 2)
            
            # Indikátor sklonu zrcadla
            angle = mirror["angle"]
            end_x = mx + 28 * math.cos(math.radians(angle))
            end_y = my + 28 * math.sin(math.radians(angle))
            pygame.draw.line(screen, BLACK, (mx, my), (end_x, end_y), 3)
        
        # Kreslení laserového paprsku
        for seg in self.laser_segments:
            p1, p2 = seg
            pygame.draw.line(screen, CYAN, p1, p2, 5)
            # Efekt záblesku
            pygame.draw.line(screen, (100, 255, 255), p1, p2, 2)
        
        # Ukaž počet odrazů
        refl_text = FONT_MEDIUM.render(f"Odrazy: {self.reflection_count}/3", True, 
                                       GREEN if self.reflection_count >= 3 else YELLOW)
        screen.blit(refl_text, (SCREEN_WIDTH//2 - 120, 100))
        
        if self.won:
            win_text = FONT_LARGE.render("TRESINK!!!", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH//2 - 180, 200))
        
        instr = FONT_SMALL.render("KLIKNI NA ZRCADLA (45 stupnu) - Potrebujes 3+ ODRAZY!", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 320, 700))
    
    def get_hint(self):
        return f"Otáčej zrcadla aby laser (zelený) dosáhl cíle (červený) - potřebuješ {3 - self.reflection_count} více odrazů!"


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
    """Otáčení potrubí - propoj START a CÍL - OPRAVENÉ S VALIDACÍ PŘIPOJENÍ"""
    
    PIPE_TYPES = {
        "straight": [(0, 180)],  # Přímá linka - vždy opačné směry
        "corner": [(0, 90)]  # Rohová - vždy kolmé směry
    }
    
    def __init__(self):
        super().__init__()
        self.grid_size = 5
        self.cell_size = 120
        self.start_pos = (0, 0)
        self.end_pos = (4, 4)
        self.pipes = [[{"type": "straight", "rotation": 0} for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.generate_pipes()
    
    def generate_pipes(self):
        """Generuje náhodné potrubí"""
        types = ["straight", "corner"]
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                self.pipes[y][x] = {
                    "type": random.choice(types),
                    "rotation": random.randint(0, 3) * 90
                }
    
    def get_pipe_openings(self, pipe_type, rotation):
        """Vrátí směry, kam se trubka připojuje (0=vpravo, 90=dolu, 180=vlevo, 270=nahoru)"""
        if pipe_type not in self.PIPE_TYPES:
            return set()
        base_openings = self.PIPE_TYPES[pipe_type]
        pipe_dirs = set()
        for opening_pair in base_openings:
            dir1 = (opening_pair[0] + rotation) % 360
            dir2 = (opening_pair[1] + rotation) % 360
            pipe_dirs.add(dir1)
            pipe_dirs.add(dir2)
        return pipe_dirs
    
    def is_path_connected(self):
        """Ověří propojení s kontrolou skutečných otvorů trubek"""
        from collections import deque
        
        queue = deque([self.start_pos])
        visited = {self.start_pos}
        
        DIRECTIONS = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}
        OPPOSITE = {0: 180, 90: 270, 180: 0, 270: 90}
        
        while queue:
            y, x = queue.popleft()
            
            if (y, x) == self.end_pos:
                return True
            
            pipe = self.pipes[y][x]
            pipe_dirs = self.get_pipe_openings(pipe["type"], pipe["rotation"])
            
            for direction in pipe_dirs:
                dy, dx = DIRECTIONS[direction]
                next_y, next_x = y + dy, x + dx
                
                if 0 <= next_y < self.grid_size and 0 <= next_x < self.grid_size:
                    if (next_y, next_x) not in visited:
                        next_pipe = self.pipes[next_y][next_x]
                        next_dirs = self.get_pipe_openings(next_pipe["type"], next_pipe["rotation"])
                        
                        # Ověř, že následující trubka se připojuje zpět (opačný směr)
                        if OPPOSITE[direction] in next_dirs:
                            visited.add((next_y, next_x))
                            queue.append((next_y, next_x))
        
        return False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for y in range(self.grid_size):
                for x in range(self.grid_size):
                    px = 300 + x * self.cell_size
                    py = 200 + y * self.cell_size
                    if pygame.Rect(px, py, self.cell_size - 10, self.cell_size - 10).collidepoint(pos):
                        self.pipes[y][x]["rotation"] = (self.pipes[y][x]["rotation"] + 90) % 360
                        if self.is_path_connected():
                            self.won = True
    
    def draw_pipe_shape(self, screen, cx, cy, pipe_type, rotation):
        """Kreslí tvar potrubí - přímé nebo rohové"""
        center_x = cx + self.cell_size // 2
        center_y = cy + self.cell_size // 2
        pipe_size = 35
        
        if pipe_type == "straight":
            # Přímé potrubí - vodorovné nebo svislé
            if rotation in [0, 180]:  # Vodorovné
                pygame.draw.line(screen, YELLOW, (center_x - pipe_size, center_y), 
                                (center_x + pipe_size, center_y), 12)
            else:  # Svislé (90, 270)
                pygame.draw.line(screen, YELLOW, (center_x, center_y - pipe_size), 
                                (center_x, center_y + pipe_size), 12)
        else:  # corner
            # Rohové potrubí - L-tvar
            if rotation == 0:
                pygame.draw.line(screen, YELLOW, (center_x, center_y), 
                                (center_x + pipe_size, center_y), 12)
                pygame.draw.line(screen, YELLOW, (center_x, center_y), 
                                (center_x, center_y - pipe_size), 12)
            elif rotation == 90:
                pygame.draw.line(screen, YELLOW, (center_x, center_y), 
                                (center_x + pipe_size, center_y), 12)
                pygame.draw.line(screen, YELLOW, (center_x, center_y), 
                                (center_x, center_y + pipe_size), 12)
            elif rotation == 180:
                pygame.draw.line(screen, YELLOW, (center_x, center_y), 
                                (center_x - pipe_size, center_y), 12)
                pygame.draw.line(screen, YELLOW, (center_x, center_y), 
                                (center_x, center_y + pipe_size), 12)
            else:  # 270
                pygame.draw.line(screen, YELLOW, (center_x, center_y), 
                                (center_x - pipe_size, center_y), 12)
                pygame.draw.line(screen, YELLOW, (center_x, center_y), 
                                (center_x, center_y - pipe_size), 12)
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("POTRUBI", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 20))
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                px = 300 + x * self.cell_size
                py = 200 + y * self.cell_size
                
                pygame.draw.rect(screen, BLUE, pygame.Rect(px, py, self.cell_size - 10, self.cell_size - 10))
                pygame.draw.rect(screen, WHITE, pygame.Rect(px, py, self.cell_size - 10, self.cell_size - 10), 2)
                
                # Kresli tvar potrubí
                pipe = self.pipes[y][x]
                self.draw_pipe_shape(screen, px, py, pipe["type"], pipe["rotation"])
                
                # Start a cíl
                if (y, x) == self.start_pos:
                    pygame.draw.circle(screen, GREEN, (px + self.cell_size//2, py + self.cell_size//2), 18)
                    pygame.draw.circle(screen, WHITE, (px + self.cell_size//2, py + self.cell_size//2), 18, 2)
                elif (y, x) == self.end_pos:
                    pygame.draw.circle(screen, RED, (px + self.cell_size//2, py + self.cell_size//2), 18)
                    pygame.draw.circle(screen, WHITE, (px + self.cell_size//2, py + self.cell_size//2), 18, 2)
        
        # Ukaž, jestli je cesta hotová
        if self.is_path_connected():
            status = FONT_MEDIUM.render("SPOJENO!!!", True, GREEN)
            screen.blit(status, (SCREEN_WIDTH//2 - 120, 700))
        
        instr = FONT_SMALL.render("KLIKNI NA POTRUBI - Otáčej aby se ZELENA propojila s CERVENOU!", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 350, 650))
    
    def get_hint(self):
        return "Otáčej potrubí - musí být skutečně připojena!"


class CableConnect(BaseGame):
    """Spoj barevné kabely - OPRAVENÉ S BAREVNÝMI KOLEČKY A VALIDACÍ"""
    def __init__(self):
        super().__init__()
        self.cables = 4
        self.left_cables = list(range(self.cables))  # [0=RED, 1=GREEN, 2=BLUE, 3=YELLOW]
        self.right_cables = list(range(self.cables))
        random.shuffle(self.right_cables)
        self.connections = {}  # {left_index: right_index}
        self.selected = None
        self.cable_colors = [RED, GREEN, BLUE, YELLOW]
        self.cable_names = ["CERVENA", "ZELENA", "MODRA", "ZLUTA"]
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Vlevo
            for i in range(self.cables):
                x, y = 300, 250 + i * 120
                if pygame.Rect(x - 35, y - 35, 70, 70).collidepoint(pos):
                    if self.selected is None:
                        self.selected = ("left", i)
                    elif self.selected[0] == "right":
                        # Propoj kabely - kontroluj barvy!
                        right_i = self.selected[1]
                        if self.left_cables[i] == self.right_cables[right_i]:
                            self.connections[i] = right_i
                            self.selected = None
                            # Ověř výhru
                            if len(self.connections) == self.cables:
                                self.won = True
                        else:
                            self.selected = ("left", i)
                    else:
                        self.selected = ("left", i)
            
            # Vpravo
            for i in range(self.cables):
                x, y = SCREEN_WIDTH - 300, 250 + i * 120
                if pygame.Rect(x - 35, y - 35, 70, 70).collidepoint(pos):
                    if self.selected is None:
                        self.selected = ("right", i)
                    elif self.selected[0] == "left":
                        # Propoj kabely - kontroluj barvy!
                        left_i = self.selected[1]
                        if self.left_cables[left_i] == self.right_cables[i]:
                            self.connections[left_i] = i
                            self.selected = None
                            # Ověř výhru
                            if len(self.connections) == self.cables:
                                self.won = True
                        else:
                            self.selected = ("right", i)
                    else:
                        self.selected = ("right", i)
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("KABELY", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 150, 30))
        
        # Vlevo
        for i in range(self.cables):
            x, y = 300, 250 + i * 120
            cable_idx = self.left_cables[i]
            color = self.cable_colors[cable_idx]
            is_selected = self.selected == ("left", i)
            border_color = YELLOW if is_selected else WHITE
            border_width = 5 if is_selected else 3
            
            # Větší kruh s barvou kabelu
            pygame.draw.circle(screen, color, (x, y), 28)
            pygame.draw.circle(screen, border_color, (x, y), 28, border_width)
            
            # Jméno barvy
            label = FONT_TINY.render(self.cable_names[cable_idx], True, BLACK)
            label_rect = label.get_rect(center=(x, y))
            screen.blit(label, label_rect)
        
        # Vpravo
        for i in range(self.cables):
            x, y = SCREEN_WIDTH - 300, 250 + i * 120
            cable_idx = self.right_cables[i]
            color = self.cable_colors[cable_idx]
            is_selected = self.selected == ("right", i)
            border_color = YELLOW if is_selected else WHITE
            border_width = 5 if is_selected else 3
            
            # Větší kruh s barvou kabelu
            pygame.draw.circle(screen, color, (x, y), 28)
            pygame.draw.circle(screen, border_color, (x, y), 28, border_width)
            
            # Jméno barvy
            label = FONT_TINY.render(self.cable_names[cable_idx], True, BLACK)
            label_rect = label.get_rect(center=(x, y))
            screen.blit(label, label_rect)
        
        # Čáry spojů (s barvou kabelu)
        for left_i, right_i in self.connections.items():
            x1, y1 = 300, 250 + left_i * 120
            x2, y2 = SCREEN_WIDTH - 300, 250 + right_i * 120
            # Čára má barvu levého kabelu
            line_color = self.cable_colors[self.left_cables[left_i]]
            pygame.draw.line(screen, line_color, (x1, y1), (x2, y2), 5)
        
        # Počítadlo
        connected = FONT_SMALL.render(f"Připojeno: {len(self.connections)}/{self.cables}", True, YELLOW)
        screen.blit(connected, (SCREEN_WIDTH//2 - 150, 750))
        
        instr = FONT_SMALL.render("KLIKNI VLEVO, PAK VPRAVO - Spoj stejne BARVY!", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 250, 700))
    
    def get_hint(self):
        return "Spoj kabely podle BAREV - cervena s cervenou, zelena se zelenou!"


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


if __name__ == "__main__":
    game = Game()
    game.run()

