"""
RotatingImage Level 11 - FIXED VERSION with 3 Rounds
Replace the entire RotatingImage class with this implementation.
"""

class RotatingImage(BaseGame):
    """RotatingImage - 3 rounds, player memorizes shapes then chooses the correct rotation"""
    
    SHAPES = {
        "CIRCLE": {
            "draw": lambda screen, x, y, size: pygame.draw.circle(screen, BLUE, (x, y), size),
        },
        "SQUARE": {
            "draw": lambda screen, x, y, size: pygame.draw.rect(screen, GREEN, pygame.Rect(x - size, y - size, size * 2, size * 2)),
        },
        "TRIANGLE": {
            "draw": lambda screen, x, y, size: pygame.draw.polygon(screen, RED, [(x, y - size), (x - size, y + size), (x + size, y + size)]),
        }
    }
    
    def __init__(self):
        super().__init__()
        self.round = 1  # 1, 2, 3
        self.round_time = 120  # frames
        self.round_timer = 0
        self.show_duration = 120  # frames to show shape
        
        self.shapes_list = ["CIRCLE", "SQUARE", "TRIANGLE"]
        self.current_shape = None
        self.current_rotation = 0  # 0, 90, 180, 270
        self.showing = True  # Show or hide shape
        self.
        
        self.correct_guesses = 0
        self.guesses_required = 2  # 1st round: 2 guesses, 2nd: 4, 3rd: 6
        self.lives = 3
        
        self.answer_buttons = []
        self.setup_round()
        
    def setup_round(self):
        """Initialize a new round"""
        self.round_timer = 0
        self.showing = True
        self.current_shape = random.choice(self.shapes_list)
        self.current_rotation = random.choice([0, 90, 180, 270])
        self.correct_guesses = 0
        self.guesses_required = (self.round - 1) * 2 + 2  # Round 1: 2, Round 2: 4, Round 3: 6
        
        # Create answer buttons
        self.answer_buttons = []
        button_y = SCREEN_HEIGHT // 2 + 150
        button_spacing = 250
        start_x = SCREEN_WIDTH // 2 - button_spacing
        
        for i, shape in enumerate(self.shapes_list):
            button_x = start_x + i * button_spacing
            self.answer_buttons.append({
                "shape": shape,
                "rect": pygame.Rect(button_x - 50, button_y - 30, 100, 60),
                "label": shape
            })
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            for button in self.answer_buttons:
                if button["rect"].collidepoint(pos):
                    if button["shape"] == self.current_shape:
                        self.correct_guesses += 1
                        if self.correct_guesses >= self.guesses_required:
                            # Round complete
                            if self.round == 3:
                                self.won = True
                            else:
                                self.round += 1
                                self.setup_round()
                        else:
                            # Continue with same shape, new rotation
                            self.showing = True
                            self.round_timer = 0
                            self.current_rotation = random.choice([0, 90, 180, 270])
                    else:
                        # Wrong answer
                        self.lives -= 1
                        if self.lives <= 0:
                            self.lost = True
                        else:
                            # Show the correct answer
                            self.showing = True
                            self.round_timer = 0
                            self.current_rotation = random.choice([0, 90, 180, 270])
    
    def update(self):
        self.round_timer += 1
        
        if self.showing:
            if self.round_timer >= self.show_duration:
                self.showing = False
                self.round_timer = 0
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        # Title
        title = FONT_LARGE.render("ROTATING IMAGE", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 250, 30))
        
        # Round info
        round_text = FONT_MEDIUM.render(f"Round {self.round}/3", True, YELLOW)
        screen.blit(round_text, (SCREEN_WIDTH//2 - 100, 100))
        
        # Progress
        progress = FONT_SMALL.render(f"Correct: {self.correct_guesses}/{self.guesses_required}", True, GREEN)
        screen.blit(progress, (SCREEN_WIDTH//2 - 150, 170))
        
        # Lives
        lives_text = FONT_SMALL.render(f"Lives: {self.lives}", True, RED if self.lives == 1 else WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH//2 - 50, 230))
        
        # Display shape or hint
        if self.showing:
            # Draw the shape
            x, y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100
            size = 80
            
            # Save current transform state
            screen_copy = screen.copy()
            
            # Rotate surface to show rotated shape
            if self.current_shape == "CIRCLE":
                pygame.draw.circle(screen, BLUE, (x, y), size)
            elif self.current_shape == "SQUARE":
                # For square with rotation
                surface = pygame.Surface((size * 3, size * 3))
                surface.fill(DARK_BLUE)
                pygame.draw.rect(surface, GREEN, pygame.Rect(size // 2, size // 2, size * 2, size * 2))
                rotated = pygame.transform.rotate(surface, self.current_rotation)
                screen.blit(rotated, (x - rotated.get_width() // 2, y - rotated.get_height() // 2))
            elif self.current_shape == "TRIANGLE":
                # Triangle with rotation
                surface = pygame.Surface((size * 3, size * 3))
                surface.fill(DARK_BLUE)
                pygame.draw.polygon(surface, RED, [
                    (size * 1.5, size * 0.5),
                    (size * 0.5, size * 2.5),
                    (size * 2.5, size * 2.5)
                ])
                rotated = pygame.transform.rotate(surface, self.current_rotation)
                screen.blit(rotated, (x - rotated.get_width() // 2, y - rotated.get_height() // 2))
            
            # Show timer bar
            bar_width = 400
            bar_height = 20
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = y + 150
            
            # Background bar
            pygame.draw.rect(screen, GRAY, pygame.Rect(bar_x, bar_y, bar_width, bar_height))
            
            # Progress bar
            progress = (self.round_timer / self.show_duration) * bar_width
            pygame.draw.rect(screen, GREEN, pygame.Rect(bar_x, bar_y, progress, bar_height))
            
            info_text = FONT_SMALL.render("Memorizing...", True, YELLOW)
            screen.blit(info_text, (SCREEN_WIDTH//2 - 100, bar_y + 30))
        else:
            prompt_text = FONT_MEDIUM.render("Which shape did you see?", True, YELLOW)
            screen.blit(prompt_text, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT // 2 - 50))
        
        if not self.showing:
            diff_text = FONT_SMALL.render(f"(Difficulty: Round {self.round})", True, CYAN)
            screen.blit(diff_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT // 2 - 20))
        
        # Draw answer buttons
        for button in self.answer_buttons:
            color = CYAN if button["shape"] == self.current_shape and not self.showing else GRAY
            pygame.draw.rect(screen, color, button["rect"])
            pygame.draw.rect(screen, WHITE, button["rect"], 2)
            
            text = FONT_SMALL.render(button["label"], True, BLACK if color == CYAN else WHITE)
            text_rect = text.get_rect(center=button["rect"].center)
            screen.blit(text, text_rect)
    
    def get_hint(self):
        if self.showing:
            return f"Memorize the {self.current_shape}! You need {self.guesses_required} correct answers this round."
        else:
            return f"Which shape was it? Round {self.round}/3 - Need {self.guesses_required} correct to advance"
