"""
CableConnect Level 18A - FIXED VERSION (Proper Centering)
Replace the entire CableConnect class with this implementation.
This version properly centers cables for 1920x1080 and validates color connections strictly.
"""

class CableConnect(BaseGame):
    """CableConnect - Connect matching colored cables from left to right"""
    
    def __init__(self):
        super().__init__()
        self.colors = [RED, GREEN, BLUE, YELLOW]
        self.color_names = {RED: "RED", GREEN: "GREEN", BLUE: "BLUE", YELLOW: "YELLOW"}
        
        # Proper centering for 1920x1080
        self.left_x = SCREEN_WIDTH // 2 - 250  # Left side cables
        self.right_x = SCREEN_WIDTH // 2 + 250  # Right side cables
        
        # Create left cables (in order)
        self.left_cables = []
        self.right_cables = []
        
        left_colors = self.colors.copy()
        right_colors = self.colors.copy()
        random.shuffle(right_colors)  # Right side is shuffled
        
        # Position cables vertically
        cable_spacing = 150
        start_y = SCREEN_HEIGHT // 2 - 225  # Center vertically for 4 cables
        
        for i, color in enumerate(left_colors):
            self.left_cables.append({
                "color": color,
                "x": self.left_x,
                "y": start_y + i * cable_spacing,
                "radius": 20
            })
        
        for i, color in enumerate(right_colors):
            self.right_cables.append({
                "color": color,
                "x": self.right_x,
                "y": start_y + i * cable_spacing,
                "radius": 20
            })
        
        self.selected = None  # (side, index) - which cable is selected
        self.connections = {}  # Maps left_index -> right_index if colors match
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # Check left cables
            for i, cable in enumerate(self.left_cables):
                if self.get_distance(pos, (cable["x"], cable["y"])) < cable["radius"] + 10:
                    if self.selected == ("left", i):
                        self.selected = None  # Deselect
                    else:
                        if self.selected and self.selected[0] == "left":
                            self.selected = ("left", i)  # Switch selection
                        else:
                            self.selected = ("left", i)
                    break
            
            # Check right cables
            for i, cable in enumerate(self.right_cables):
                if self.get_distance(pos, (cable["x"], cable["y"])) < cable["radius"] + 10:
                    if self.selected == ("right", i):
                        self.selected = None
                    elif self.selected and self.selected[0] == "left":
                        # Try to connect
                        left_idx = self.selected[1]
                        left_color = self.left_cables[left_idx]["color"]
                        right_color = cable["color"]
                        
                        if left_color == right_color:
                            # Valid connection
                            self.connections[left_idx] = i
                            self.selected = None
                            
                            # Check if all connected
                            if len(self.connections) == 4:
                                self.won = True
                        else:
                            # Invalid - wrong colors
                            self.selected = ("right", i)
                    else:
                        self.selected = ("right", i)
                    break
    
    def get_distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("CABLE CONNECT", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 200, 40))
        
        # Draw connection lines
        for left_idx, right_idx in self.connections.items():
            left_cable = self.left_cables[left_idx]
            right_cable = self.right_cables[right_idx]
            
            start_pos = (left_cable["x"] + left_cable["radius"] + 10, left_cable["y"])
            end_pos = (right_cable["x"] - right_cable["radius"] - 10, right_cable["y"])
            pygame.draw.line(screen, left_cable["color"], start_pos, end_pos, 4)
        
        # Draw left cables (labels on right)
        for i, cable in enumerate(self.left_cables):
            color = cable["color"]
            x, y = cable["x"], cable["y"]
            
            # Highlight if selected
            if self.selected == ("left", i):
                pygame.draw.circle(screen, WHITE, (x, y), cable["radius"] + 5, 3)
            
            # Draw cable circle
            pygame.draw.circle(screen, color, (x, y), cable["radius"])
            pygame.draw.circle(screen, BLACK, (x, y), cable["radius"], 2)
            
            # Label with color name
            label = FONT_SMALL.render(self.color_names[color], True, WHITE)
            screen.blit(label, (x + 40, y - 15))
        
        # Draw right cables
        for i, cable in enumerate(self.right_cables):
            color = cable["color"]
            x, y = cable["x"], cable["y"]
            
            # Highlight if selected
            if self.selected == ("right", i):
                pygame.draw.circle(screen, WHITE, (x, y), cable["radius"] + 5, 3)
            
            # Draw cable circle
            pygame.draw.circle(screen, color, (x, y), cable["radius"])
            pygame.draw.circle(screen, BLACK, (x, y), cable["radius"], 2)
        
        # Connection counter
        connected_text = FONT_MEDIUM.render(f"Connected: {len(self.connections)}/4", True, YELLOW)
        screen.blit(connected_text, (SCREEN_WIDTH//2 - 150, 150))
        
        # Instructions
        instr = FONT_SMALL.render("CLICK & DRAG cables - Match colors! (e.g., RED cable to RED)", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 350, 700))
    
    def get_hint(self):
        return "Connect matching colored cables from left to right. Click a cable on the left, then click the matching color on the right."
