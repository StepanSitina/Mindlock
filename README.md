# MindLock! - Puzzle Hra

Pythonová puzzle hra s 11 jedinečnými mini-hrami s postupující obtížností. Vyzkoušej svou paměť, logiku a schopnost řešit problémy!

## Vlastnosti

### 11 Unikátních Her
- **Simon Says** - Zapamatuj si a opakuj posloupnosti barev (5 kol k výhře)
- **Bludiště** - Projdi komplexním bludištěm a dosáhni cíle
- **Hledač Tlačítka** - Najdi správné tlačítko z 9 možností
- **Tetris Lite** - Vymaž 3 řady v zjednodušené verzi Tetrisu
- **2048** - Kombinuj dlaždice a vytvoř dlaždici 2048
- **Vážka** - Rozděl předměty stejně na obě strany
- **Hádanka** - Řeš české hádanky pro postup
- **Sudoku Lite** - Vyplň 4x4 Sudoku
- **Caesarova Šifra** - Dešifruj zprávy pomocí posunů
- **Přepínače** - Aktivuj všechny přepínače s řetězovými reakcemi
- **Unscrambler Slov** - Uspořádej písmena do slov

## Ovládání

### Během Hry
- **H** - Zobraz popup nápovědu (kontextně závislá pomoc)
- **ESC** - Otevři menu pauzy
  - Pokračovat - Vrátit se do hry
  - Restart - Restartovat level a odemknout level 2
  - Výstup - Vrátit se na výběr levelů
- **WSAD / Šipky** - Pohyb (v hrách vyžadujících pohyb)
- **Myš/Klik** - Interakce s tlačítky a UI

### Tajné Funkce
- **O** - Odemkni všech 20 levelů (admin mód - skrytá funkce!)

## Hrání

- 20 postupně obtížnějších levelů
- Odemykej levely splněním předchozích
- Systém nápověd pro pomoc když se zaseknete
- Funkce pauzy pro všechny hry
- Popup menu pro výhru/prohru

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

### Verze 1.2.0
- Hezčí a moderní menu
- Opravena logika 2048
- Přidán delay v Simon Says
- Patch notes nyní v Pop-up okně

### Verze 1.1.0
- Opravena mechanika levelů
- Přidány nápovědy

### Verze 1.0.0
- Počáteční verze hry
- 11 různých herních módů

## Instalace

### Požadavky
- Python 3.10+
- pygame-ce (Community Edition)

### Nastavení
```bash
pip install pygame-ce
git clone https://github.com/StepanSitina/Mindlock.git
cd Mindlock
python game.py
```

## Herní Nastavení

Přístup k nastavením z hlavního menu:
- **Nastavení Grafiky** - Úprava FPS (10-240)
- **Info Vývojáře** - Zobrazení verze a statistik hry

## Autor
Vytvořil: Stepan Sitina

## Licence
Soukromý projekt

## Užij si to!
Vyzkoušej si MindLock! a podívej se, jak daleko můžeš dojít!
