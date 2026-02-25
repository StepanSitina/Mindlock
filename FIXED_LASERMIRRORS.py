"""
LaserMirrors Level 18B - FIXED VERSION with Visible Laser Beam + 3+ Bounce Requirement
Replace the entire LaserMirrors class with this implementation.
"""

class LaserMirrors(BaseGame):
    """LaserMirrors - Direct laser beam on target after 3+ reflections"""
    def __init__(self):
        super().__init__()
        self.laser_start = (150, 540)
        self.laser_direction = 0  # degrees, 0=right
        self.target = (1750, 540)
        self.mirrors = [
            {"pos": (600, 400), "angle": 45, "index": 0},
            {"pos": (1000, 650), "angle": 45, "index": 1},
            {"pos": (1400, 350), "angle": 45, "index": 2}
        ]
        self.reflection_count = 0
        self.laser_segments = []
        self.target_hit = False
        self.trace_laser()
    
    def trace_laser(self):
        """Trace laser path with visible beam and reflection counter"""
        self.laser_segments = []
        self.reflection_count = 0
        self.target_hit = False
        
        current_pos = list(self.laser_start)
        current_dir = self.laser_direction
        visited_mirrors = set()
        
        for step in range(200):
            # Move in current direction
            next_x = current_pos[0] + 15 * math.cos(math.radians(current_dir))
            next_y = current_pos[1] + 15 * math.sin(math.radians(current_dir))
            
            # Check if laser hits target
            dist_to_target = math.sqrt((next_x - self.target[0])**2 + (next_y - self.target[1])**2)
            if dist_to_target < 40 and self.reflection_count >= 3:
                self.laser_segments.append(((current_pos[0], current_pos[1]), (self.target[0], self.target[1])))
                self.target_hit = True
                self.won = True
                return
            
            # Check if laser hits a mirror
            hit_mirror = None
            for mirror in self.mirrors:
                mx, my = mirror["pos"]
                dist = math.sqrt((next_x - mx)**2 + (next_y - my)**2)
                if dist < 35 and mirror["index"] not in visited_mirrors:
                    hit_mirror = mirror
                    break
            
            if hit_mirror:
                # Draw segment to mirror
                self.laser_segments.append(((current_pos[0], current_pos[1]), hit_mirror["pos"]))
                
                # Reflect laser angle
                mirror_angle = hit_mirror["angle"]
                current_dir = (2 * mirror_angle - current_dir) % 360
                
                visited_mirrors.add(hit_mirror["index"])
                self.reflection_count = len(visited_mirrors)
                current_pos = list(hit_mirror["pos"])
            else:
                current_pos = [next_x, next_y]
            
            # Out of bounds
            if current_pos[0] < 0 or current_pos[0] > SCREEN_WIDTH or current_pos[1] < 0 or current_pos[1] > SCREEN_HEIGHT:
                self.laser_segments.append(((current_pos[0] - 15 * math.cos(math.radians(current_dir)), current_pos[1] - 15 * math.sin(math.radians(current_dir))), (current_pos[0], current_pos[1])))
                break
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for mirror in self.mirrors:
                mx, my = mirror["pos"]
                if pygame.Rect(mx - 30, my - 30, 60, 60).collidepoint(pos):
                    mirror["angle"] = (mirror["angle"] + 45) % 360
                    self.trace_laser()
                    break
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("LASER MIRRORS", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 200, 30))
        
        # Draw laser source
        pygame.draw.circle(screen, GREEN, self.laser_start, 15)
        pygame.draw.circle(screen, WHITE, self.laser_start, 15, 2)
        
        # Draw target
        pygame.draw.circle(screen, RED, self.target, 15)
        pygame.draw.circle(screen, WHITE, self.target, 15, 2)
        
        # Draw mirrors
        for mirror in self.mirrors:
            mx, my = mirror["pos"]
            pygame.draw.rect(screen, YELLOW, pygame.Rect(mx - 20, my - 20, 40, 40))
            # Draw mirror angle indicator
            angle = mirror["angle"]
            end_x = mx + 25 * math.cos(math.radians(angle))
            end_y = my + 25 * math.sin(math.radians(angle))
            pygame.draw.line(screen, WHITE, (mx, my), (end_x, end_y), 3)
            pygame.draw.rect(screen, WHITE, pygame.Rect(mx - 20, my - 20, 40, 40), 2)
        
        # Draw laser beam with glow
        for segment in self.laser_segments:
            p1, p2 = segment
            pygame.draw.line(screen, CYAN, p1, p2, 4)
            # Glow effect
            if p1[0] != p2[0] or p1[1] != p2[1]:
                pygame.draw.line(screen, (100, 200, 255), p1, p2, 2)
        
        # Draw reflection counter
        reflection_text = FONT_MEDIUM.render(f"Reflections: {self.reflection_count}/3", True, YELLOW if self.reflection_count < 3 else GREEN)
        screen.blit(reflection_text, (SCREEN_WIDTH//2 - 150, 100))
        
        if self.target_hit:
            win_text = FONT_LARGE.render("TARGET HIT!", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH//2 - 200, 200))
        
        # Instructions
        instr = FONT_SMALL.render("CLICK mirrors to rotate (45 degrees) - Need 3+ reflections to reach RED target!", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 400, 700))
    
    def update(self):
        pass
    
    def get_hint(self):
        return f"Rotate mirrors to reflect laser 3+ times to hit the red target. Currently: {self.reflection_count}/3 reflections"
