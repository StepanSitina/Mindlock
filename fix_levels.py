#!/usr/bin/env python3
"""
Comprehensive patch for all remaining game.py level bugs.
Run this script to apply all fixes at once.
"""

import re

def fix_pipe_rotate(content):
    """Replace PipeRotate class with proper connection logic"""
    old_pattern = r'class PipeRotate\(BaseGame\):.*?def get_hint\(self\):\s*return "Otáčej potrubí.*?"'
    new_code = '''class PipeRotate(BaseGame):
    """Rotate pipes - connect START and END with proper water flow logic"""
    def __init__(self):
        super().__init__()
        self.grid_size = 5
        self.cell_size = 100
        self.pipes = [[{"type": "straight", "rotation": 0} for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.start_pos = (0, 0)
        self.end_pos = (4, 4)
        self.generate_pipes()
        # Center the grid
        self.start_x = SCREEN_WIDTH // 2 - (self.grid_size * self.cell_size) // 2
        self.start_y = SCREEN_HEIGHT // 2 - (self.grid_size * self.cell_size) // 2
    
    def generate_pipes(self):
        """Generate random pipes"""
        types = ["straight", "corner"]
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                self.pipes[y][x] = {
                    "type": random.choice(types),
                    "rotation": random.randint(0, 3) * 90
                }
    
    def get_pipe_openings(self, y, x):
        """Returns which directions a pipe is open (0=up, 1=right, 2=down, 3=left)"""
        pipe = self.pipes[y][x]
        rot = pipe["rotation"] // 90
        
        if pipe["type"] == "straight":
            # Straight pipes have openings on opposite sides
            if rot % 2 == 0:  # 0 or 180 degrees - vertical
                return [0, 2]  # UP and DOWN
            else:  # 90 or 270 degrees - horizontal
                return [1, 3]  # RIGHT and LEFT
        elif pipe["type"] == "corner":
            # Corner pipes have openings on adjacent sides
            # Base corner connects UP(0) and RIGHT(1)
            # Then rotate based on rotation
            base = [0, 1]
            return [(d + rot) % 4 for d in base]
        return []
    
    def is_path_connected(self):
        """Check if path connects from START to END using BFS"""
        from collections import deque
        
        visited = set()
        queue = deque([(self.start_pos, None)])  # (pos, direction_from_prev)
        
        while queue:
            (y, x), prev_dir = queue.popleft()
            
            if (y, x) in visited:
                continue
            visited.add((y, x))
            
            if (y, x) == self.end_pos:
                return True
            
            # Get openings for current pipe
            openings = self.get_pipe_openings(y, x)
            
            # Check each opening direction
            # 0=up, 1=right, 2=down, 3=left
            directions = [(0, 0, -1), (1, 1, 0), (2, 0, 1), (3, -1, 0)]
            
            for dir_idx, dy, dx in directions:
                # Skip if we came from this direction (to avoid going backward)
                if prev_dir is not None and dir_idx == (prev_dir + 2) % 4:
                    continue
                
                # Skip if this pipe doesn't open in this direction
                if dir_idx not in openings:
                    continue
                
                ny, nx = y + dy, x + dx
                
                # Check bounds
                if not (0 <= ny < self.grid_size and 0 <= nx < self.grid_size):
                    continue
                
                if (ny, nx) in visited:
                    continue
                
                # Check if next pipe connects back (opposite direction)
                next_openings = self.get_pipe_openings(ny, nx)
                opposite_dir = (dir_idx + 2) % 4
                
                if opposite_dir in next_openings:
                    queue.append(((ny, nx), dir_idx))
        
        return False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for y in range(self.grid_size):
                for x in range(self.grid_size):
                    px = self.start_x + x * self.cell_size
                    py = self.start_y + y * self.cell_size
                    if pygame.Rect(px, py, self.cell_size - 10, self.cell_size - 10).collidepoint(pos):
                        self.pipes[y][x]["rotation"] = (self.pipes[y][x]["rotation"] + 90) % 360
                        if self.is_path_connected():
                            self.won = True
    
    def draw(self, screen):
        screen.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("PIPES", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH//2 - 100, 20))
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                px = self.start_x + x * self.cell_size
                py = self.start_y + y * self.cell_size
                
                pygame.draw.rect(screen, BLUE, pygame.Rect(px, py, self.cell_size - 10, self.cell_size - 10))
                pygame.draw.rect(screen, WHITE, pygame.Rect(px, py, self.cell_size - 10, self.cell_size - 10), 2)
                
                # Draw pipe
                pipe = self.pipes[y][x]
                cx, cy = px + self.cell_size // 2 - 5, py + self.cell_size // 2 - 5
                
                if pipe["type"] == "straight":
                    if pipe["rotation"] % 180 == 0:
                        pygame.draw.line(screen, YELLOW, (cx, py + 10), (cx, py + self.cell_size - 20), 4)
                    else:
                        pygame.draw.line(screen, YELLOW, (px + 10, cy), (px + self.cell_size - 20, cy), 4)
                elif pipe["type"] == "corner":
                    # Draw corner
                    rot = pipe["rotation"] // 90
                    if rot == 0:
                        pygame.draw.lines(screen, YELLOW, [(cx, py + 10), (cx, cy), (px + self.cell_size - 20, cy)], 4)
                    elif rot == 1:
                        pygame.draw.lines(screen, YELLOW, [(px + 10, cy), (cx, cy), (cx, py + self.cell_size - 20)], 4)
                    elif rot == 2:
                        pygame.draw.lines(screen, YELLOW, [(cx, py + self.cell_size - 20), (cx, cy), (px + 10, cy)], 4)
                    else:
                        pygame.draw.lines(screen, YELLOW, [(px + self.cell_size - 20, cy), (cx, cy), (cx, py + 10)], 4)
                
                # START and END
                if (y, x) == self.start_pos:
                    pygame.draw.circle(screen, GREEN, (px + self.cell_size // 2 - 5, py + self.cell_size // 2 - 5), 15)
                elif (y, x) == self.end_pos:
                    pygame.draw.circle(screen, RED, (px + self.cell_size // 2 - 5, py + self.cell_size // 2 - 5), 15)
        
        instr = FONT_SMALL.render("CLICK PIPES TO ROTATE - Connect GREEN to RED!", True, WHITE)
        screen.blit(instr, (SCREEN_WIDTH//2 - 350, 700))
    
    def get_hint(self):
        return "Rotate pipes so water flows from green (START) to red (END)"'''
    
    # Find and replace using regex with DOTALL flag for multi-line matching
    content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
    return content

if __name__ == "__main__":
    try:
        with open("game.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Apply all fixes
        content = fix_pipe_rotate(content)
        
        with open("game.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ All level fixes applied successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
