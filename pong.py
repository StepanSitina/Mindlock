"""
Pong Game – 1 Player vs AI
==========================
Controls: W / S to move the left paddle.
First to 3 goals wins.
"""

import pygame
import sys
import random

# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────

# Display
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 220, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_BG = (15, 15, 30)

# Paddle settings
PADDLE_WIDTH = 14
PADDLE_HEIGHT = 100
PADDLE_SPEED = 6          # player paddle speed
AI_SPEED = 4              # AI is slightly slower than the ball

# Ball settings
BALL_SIZE = 14
BALL_SPEED_X = 5          # initial horizontal speed
BALL_SPEED_Y = 4          # initial vertical speed

# Scoring
WINNING_SCORE = 3

# Margins
PADDLE_MARGIN = 30        # distance from screen edge to paddle


# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────

def create_ball():
    """Return a dict representing the ball at the center with a random direction."""
    direction_x = random.choice([-1, 1])
    direction_y = random.choice([-1, 1])
    return {
        "rect": pygame.Rect(
            SCREEN_WIDTH // 2 - BALL_SIZE // 2,
            SCREEN_HEIGHT // 2 - BALL_SIZE // 2,
            BALL_SIZE, BALL_SIZE
        ),
        "dx": BALL_SPEED_X * direction_x,
        "dy": BALL_SPEED_Y * direction_y,
    }


def move_ball(ball):
    """Move the ball and bounce off top / bottom walls."""
    ball["rect"].x += ball["dx"]
    ball["rect"].y += ball["dy"]

    # Bounce off ceiling and floor
    if ball["rect"].top <= 0:
        ball["rect"].top = 0
        ball["dy"] = abs(ball["dy"])      # force downward
    elif ball["rect"].bottom >= SCREEN_HEIGHT:
        ball["rect"].bottom = SCREEN_HEIGHT
        ball["dy"] = -abs(ball["dy"])     # force upward


def move_player(paddle, keys):
    """Move the player paddle based on W / S key input."""
    if keys[pygame.K_w] and paddle.top > 0:
        paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and paddle.bottom < SCREEN_HEIGHT:
        paddle.y += PADDLE_SPEED


def move_ai(paddle, ball):
    """
    AI follows the ball's vertical center with a capped speed.
    Because AI_SPEED < ball speed, it will sometimes miss.
    A small 'reaction zone' in the middle prevents jittering.
    """
    paddle_center = paddle.centery
    ball_center = ball["rect"].centery
    dead_zone = 10  # ignore tiny differences to look natural

    if ball_center < paddle_center - dead_zone:
        paddle.y -= AI_SPEED
    elif ball_center > paddle_center + dead_zone:
        paddle.y += AI_SPEED

    # Clamp to screen
    if paddle.top < 0:
        paddle.top = 0
    if paddle.bottom > SCREEN_HEIGHT:
        paddle.bottom = SCREEN_HEIGHT


def check_paddle_collision(ball, player_paddle, ai_paddle):
    """Bounce the ball off paddles, slightly randomising the Y speed."""
    if ball["rect"].colliderect(player_paddle) and ball["dx"] < 0:
        ball["dx"] = abs(ball["dx"])                     # go right
        ball["dy"] += random.uniform(-1.5, 1.5)          # add spin
        ball["rect"].left = player_paddle.right           # push out

    elif ball["rect"].colliderect(ai_paddle) and ball["dx"] > 0:
        ball["dx"] = -abs(ball["dx"])                    # go left
        ball["dy"] += random.uniform(-1.5, 1.5)
        ball["rect"].right = ai_paddle.left


def check_score(ball, scores):
    """
    Detect if the ball left the screen.
    Returns True if a goal was scored (ball is then reset).
    """
    scored = False
    if ball["rect"].right <= 0:
        # AI scored
        scores["ai"] += 1
        scored = True
    elif ball["rect"].left >= SCREEN_WIDTH:
        # Player scored
        scores["player"] += 1
        scored = True
    return scored


def draw_objects(screen, player_paddle, ai_paddle, ball, scores, font_score):
    """Render all game objects and the score."""
    screen.fill(DARK_BG)

    # Centre dashed line
    for y in range(0, SCREEN_HEIGHT, 24):
        pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH // 2 - 1, y, 2, 12))

    # Paddles
    pygame.draw.rect(screen, CYAN, player_paddle)
    pygame.draw.rect(screen, YELLOW, ai_paddle)

    # Ball
    pygame.draw.ellipse(screen, WHITE, ball["rect"])

    # Scores
    player_text = font_score.render(str(scores["player"]), True, CYAN)
    ai_text = font_score.render(str(scores["ai"]), True, YELLOW)
    screen.blit(player_text, (SCREEN_WIDTH // 4 - player_text.get_width() // 2, 20))
    screen.blit(ai_text, (3 * SCREEN_WIDTH // 4 - ai_text.get_width() // 2, 20))


def draw_start_screen(screen, font_large, font_small):
    """Show a simple title / start screen."""
    screen.fill(DARK_BG)
    title = font_large.render("PONG", True, CYAN)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 180))

    info = font_small.render("Player (W/S)  vs  AI", True, WHITE)
    screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 300))

    prompt = font_small.render(f"First to {WINNING_SCORE} wins.  Press any key to start.", True, GRAY)
    screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 370))

    pygame.display.flip()


def draw_win_screen(screen, winner, scores, font_large, font_small):
    """Display who won and offer a rematch."""
    screen.fill(DARK_BG)

    if winner == "player":
        msg = "YOU WIN!"
        color = CYAN
    else:
        msg = "AI WINS!"
        color = YELLOW

    title = font_large.render(msg, True, color)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

    score_line = font_small.render(
        f"Player {scores['player']}  –  {scores['ai']} AI", True, WHITE
    )
    screen.blit(score_line, (SCREEN_WIDTH // 2 - score_line.get_width() // 2, 320))

    prompt = font_small.render("Press any key to play again  |  ESC to quit", True, GRAY)
    screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 400))

    pygame.display.flip()


# ──────────────────────────────────────────────
# MAIN GAME LOOP
# ──────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong – Player vs AI")
    clock = pygame.time.Clock()

    font_large = pygame.font.Font(None, 100)
    font_score = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)

    # ── Start screen ──────────────────────────
    draw_start_screen(screen, font_large, font_small)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                waiting = False
        clock.tick(FPS)

    # ── Game variables ────────────────────────
    running = True
    while running:
        # Reset for a new match
        scores = {"player": 0, "ai": 0}
        player_paddle = pygame.Rect(
            PADDLE_MARGIN,
            SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
            PADDLE_WIDTH, PADDLE_HEIGHT
        )
        ai_paddle = pygame.Rect(
            SCREEN_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH,
            SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2,
            PADDLE_WIDTH, PADDLE_HEIGHT
        )
        ball = create_ball()
        match_over = False

        # ── Match loop ────────────────────────
        while not match_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()

            # Update
            move_player(player_paddle, keys)
            move_ai(ai_paddle, ball)
            move_ball(ball)
            check_paddle_collision(ball, player_paddle, ai_paddle)

            if check_score(ball, scores):
                # Brief pause after a goal, then reset ball
                draw_objects(screen, player_paddle, ai_paddle, ball, scores, font_score)
                pygame.display.flip()
                pygame.time.wait(600)
                ball = create_ball()

            # Check for winner
            if scores["player"] >= WINNING_SCORE:
                match_over = True
                winner = "player"
            elif scores["ai"] >= WINNING_SCORE:
                match_over = True
                winner = "ai"

            # Draw
            draw_objects(screen, player_paddle, ai_paddle, ball, scores, font_score)
            pygame.display.flip()
            clock.tick(FPS)

        # ── Win screen ────────────────────────
        draw_win_screen(screen, winner, scores, font_large, font_small)
        waiting_end = True
        while waiting_end:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        waiting_end = False
                    else:
                        waiting_end = False  # any other key → rematch
            clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
