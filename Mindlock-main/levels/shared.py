import pygame
import random
import math
import os
import re
import json
import hashlib
import zipfile
import time
from enum import Enum
from collections import defaultdict, deque

if not pygame.get_init():
    pygame.init()

GAME_VERSION = "1.9.0"

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
