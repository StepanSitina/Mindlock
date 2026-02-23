# MindLock! - Puzzle Game

A Python-based puzzle game featuring 11 unique mini-games with progressive difficulty. Challenge your memory, logic, and problem-solving skills!

## Features

### 11 Unique Game Modes
- **Simon Says** - Remember and replay color sequences (5 rounds to win)
- **Maze** - Navigate through a complex labyrinth to reach the goal
- **Button Finder** - Identify the correct button among 9 options
- **Tetris Lite** - Clear 3 lines in this simplified Tetris version
- **2048** - Combine tiles to create the 2048 tile
- **Balance Game** - Distribute items equally on both sides
- **Riddle Game** - Solve Czech riddles to progress
- **Sudoku Lite** - Complete 4x4 Sudoku puzzles
- **Caesar Cipher** - Decrypt messages using shift ciphers
- **Switch Game** - Activate all switches with chain reactions
- **Word Unscrambler** - Rearrange letters to form words

## Controls

### In-Game
- **H** - Display hint popup (with context-specific help)
- **ESC** - Open pause menu
  - Continue - Resume game
  - Restart - Restart level and unlock level 2
  - Exit - Return to level selection
- **WSAD / Arrow Keys** - Move (in games that require movement)
- **Mouse/Click** - Interact with buttons and UI elements

### Secret Features
- **O** - Unlock all 20 levels (admin mode - hidden feature!)

## GamePlay

- 20 progressively difficult levels
- Unlock levels by completing previous ones
- Hint system to help when stuck
- Pause functionality for all games
- Win/loss conditions with popup menus

## Patch Notes

### Version 1.5.0 (Current)
- Bludiště má nyní mnohem více zdí (164 přesně)
- Přidán tajný admin mode - stiskni O pro odemknutí všech levelů
- Vylepšená herní vyvážená obtížnost
- Patch notes aktualizovány po každé změně

### Version 1.4.0
- Nápověda jako popup okno (stiskni H)
- Pause menu s ESC klávesou
- Tlačítka: Continue, Restart (odemyka level 2), Exit
- Simon Says nyní vyžaduje 5 kol místo 7

### Version 1.3.0
- Opravena chyba SimonSays s nekonečnou smyčkou
- Opravena inicializace TetrisLite
- Odstraněny všechny komentáře ze kódu
- Opraveny chyby v souboru

### Version 1.2.0
- Hezčí a moderní menu
- Opravena logika 2048
- Přidán delay v Simon Says
- Patch notes nyní v Pop-up okně

### Version 1.1.0
- Opravena mechanika levelů
- Přidány nápovědy

### Version 1.0.0
- Počáteční verze hry
- 11 různých herních módů

## Installation

### Requirements
- Python 3.10+
- pygame-ce (Community Edition)

### Setup
```bash
pip install pygame-ce
git clone https://github.com/StepanSitina/Mindlock.git
cd Mindlock
python game.py
```

## Game Settings

Access settings from the main menu:
- **Graphics Settings** - Adjust FPS (10-240)
- **Developer Info** - View version and game statistics

## Author
Created by Stepan Sitina

## License
Private project

## Enjoy!
Challenge your brain with MindLock! and see how far you can progress!
