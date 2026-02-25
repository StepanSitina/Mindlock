"""
PipeRotate Level 16 - FIXED VERSION
Replace the entire PipeRotate class with this implementation.
"""

class PipeRotate(BaseGame):
    """PipeRotate - Connect pipes from source to target (requires actual connection, not random click)"""
    
    PIPE_TYPES = {
        "straight": [(0, 90), (180, 270)],  # horizontal or vertical
        "corner": [(0, 180), (90, 270)]     # L-shaped corners
    }
    
    def __init__(self):
        super().__init__()
        self.grid_cols = 5
        self.grid_rows = 4
        self.cell_size = 140
        self.start_x = SCREEN_WIDTH // 2 - (self.grid_cols * self.cell_size) // 2
        self.start_y = SCREEN_HEIGHT // 2 - (self.grid_rows * self.cell_size) // 2
        
        self.grid = []
        self.source = (0, 1)  # Left middle
        self.target = (4, 2)  # Right middle
        self.initialize_grid()
        self.selected_pipe = None
        
    def initialize_grid(self):
        """Create a grid with random pipes"""
        self.grid = []
        for row in range(self.grid_rows):
            grid_row = []
            for col in range(self.grid_cols):
                if (col, row) == self.source or (col, row) == self.target:
                    grid_row.append({"type": "corner", "rotation": 0, "connected": False})
                else:
                    pipe_type = random.choice(["straight", "corner"])
                    rotation = random.choice([0, 90, 180, 270])
                    grid_row.append({"type": pipe_type, "rotation": rotation, "connected": False})
            self.grid.append(grid_row)
    
    def get_pipe_openings(self, pipe_type, rotation):
        """Get the directions this pipe connects to (0=right, 90=down, 180=left, 270=up)"""
        base_openings = self.PIPE_TYPES[pipe_type]
        rotated = []
        
        for opening_pair in base_openings:
            dir1 = (opening_pair[0] + rotation) % 360
            dir2 = (opening_pair[1] + rotation) % 360
            rotated.append((min(dir1, dir2), max(dir1, dir2)))
        
        return rotated
    
    def validate_connection(self):
        """Check if there's a valid path from source to target using BFS"""
        from collections import deque
        
        queue = deque([self.source])
        visited = {self.source}
        
        DIRECTIONS = {
            0: (1, 0),    # right
            90: (0, 1),   # down
            180: (-1, 0), # left
            270: (0, -1)  # up
        }
        
        OPPOSITE = {0: 180, 90: 270, 180: 0, 270: 90}
        
        while queue:
            col, row = queue.popleft()
            
            if (col, row) == self.target:
                return True
            
            pipe = self.grid[row][col]
            openings = self.get_pipe_openings(pipe["type"], pipe["rotation"])
            
            # Flatten openings into individual directions
            pipe_dirs = set()
            for opening_pair in openings:
                pipe_dirs.add(opening_pair[0])
                pipe_dirs.add(opening_pair[1])
            
            # Check each direction this pipe opens to
            for direction in pipe_dirs:
                next_col = col + DIRECTIONS[direction][0]
                next_row = row + DIRECTIONS[direction][1]
                
                if 0 <= next_col < self.grid_cols and 0 <= next_row < self.grid_rows:
                    if (next_col, next_row) not in visited:
                        # Check if the next pipe opens back in the opposite direction
                        next_pipe = self.grid[next_row][next_col]
                        next_openings = self.get_pipe_openings(next_pipe["type"], next_pipe["rotation"])
                        next_dirs = set()
                        for opening_pair in next_openings:
                            next_dirs.add(opening_pair[0])
                            next_dirs.add(opening_pair[1])
                        
                        if OPPOSITE[direction] in next_dirs:
                            visited.add((next_col, next_row))
                            queue.append((next_col, next_row))
        
        return False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for row in range(self.grid_rows):
                for col in range(self.grid_cols):
                    cell_x = self.start_x + col * self.cell_size + self.cell_size // 2
                    cell_y = self.start_y + row * self.cell_size + self.cell_size // 2
                    
                    if pygame.Rect(cell_x - 50, cell_y - 50, 100, 100).collidepoint(pos):
                        if (col, row) != self.source and (col, row) != self.target:
                            self.grid[row][col]["rotation"] = (self.grid[row][col]["rotation"] + 90) % 360
                            
                            # Check if we won
                            if self.validate_connection():
                                self.won = True
                        break
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("PIPE ROTATE", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 200, 30))
        
        # Draw grid
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                cell_x = self.start_x + col * self.cell_size + self.cell_size // 2
                cell_y = self.start_y + row * self.cell_size + self.cell_size // 2
                
                pipe = self.grid[row][col]
                
                # Draw cell background
                color = GREEN if (col, row) == self.source else RED if (col, row) == self.target else DARK_BLUE
                pygame.draw.rect(screen, color, pygame.Rect(cell_x - 50, cell_y - 50, 100, 100))
                pygame.draw.rect(screen, WHITE, pygame.Rect(cell_x - 50, cell_y - 50, 100, 100), 2)
                
                # Draw pipe
                if (col, row) != self.source and (col, row) != self.target:
                    self.draw_pipe(screen, cell_x, cell_y, pipe)
        
        instr = FONT_SMALL.render("CLICK pipes to rotate 90° - Connect source (GREEN) to target (RED)", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 450, 700))
        
        # Show if connected
        if self.validate_connection():
            status = FONT_MEDIUM.render("CONNECTED!", True, GREEN)
            screen.blit(status, (SCREEN_WIDTH//2 - 100, 150))
    
    def draw_pipe(self, screen, x, y, pipe):
        """Draw a pipe segment with proper rotation"""
        rotation = pipe["rotation"]
        pipe_type = pipe["type"]
        
        if pipe_type == "straight":
            if rotation in [0, 180]:  # horizontal
                pygame.draw.line(screen, YELLOW, (x - 40, y), (x + 40, y), 8)
            else:  # vertical
                pygame.draw.line(screen, YELLOW, (x, y - 40), (x, y + 40), 8)
        else:  # corner
            points = [
                (x - 40, y),
                (x, y),
                (x, y - 40)
            ]
            # Rotate points based on rotation
            rotated_points = self.rotate_points(points, (x, y), rotation)
            pygame.draw.lines(screen, YELLOW, rotated_points, 8)
    
    def rotate_points(self, points, center, angle):
        """Rotate points around a center by angle (degrees)"""
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        rotated = []
        for px, py in points:
            dx = px - center[0]
            dy = py - center[1]
            new_x = center[0] + dx * cos_a - dy * sin_a
            new_y = center[1] + dx * sin_a + dy * cos_a
            rotated.append((new_x, new_y))
        return rotated
    
    def get_hint(self):
        return "Rotate pipes to create a continuous connection from the GREEN source to the RED target. Click pipes to rotate them 90 degrees."
