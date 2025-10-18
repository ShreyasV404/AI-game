# Village Adventure Game

A top-down 2D adventure game built with Pygame featuring exploration, character movement, and a detailed village environment.

## Features

- **Smooth Character Movement**: 8-directional movement with walking and running
- **Character Animations**: Idle, walk, run, attack, hurt, and death animations for all directions
- **Weapon System**: Toggle between sword and unarmed states
- **Zoomable Camera**: Dynamic camera that follows the player with zoom in/out functionality
- **Collision Detection**: Proper collision with environment objects
- **Village Environment**: Detailed map with houses, trees, paths, and grass areas
- **State Management**: Menu and game states with smooth transitions

## Controls

### In-Game Controls
- **WASD / Arrow Keys**: Move character
- **Shift**: Run (while moving)
- **Space**: Attack
- **Q**: Toggle weapon (sword/unarmed)
- **+ / =**: Zoom in
- **-**: Zoom out
- **0**: Reset zoom
- **ESC**: Return to menu

### Menu Controls
- **Up/Down Arrows**: Navigate menu
- **Enter**: Select option

## Requirements

- Python 3.8+
- Pygame 2.6.1+

## Installation

1. Ensure you have Python installed on your system
2. Install Pygame:
   ```bash
   pip install pygame
   ```
3. Download or clone the game files
4. Make sure the asset folder structure is maintained:
   ```
   assets/
   ├── character/
   ├── tileset/
   │   ├── 1 Tiles/
   │   └── 2 Objects/
   └── ...
   ```

## Running the Game

Navigate to the game directory and run:
```bash
python main.py
```

## Project Structure

```
game/
├── main.py                 # Main game loop and entry point
├── config.py              # Game configuration and constants
├── asset_loader.py        # Asset management and loading
├── camera.py              # Camera system with zoom functionality
├── player.py              # Player character with movement and animations
├── tilemap.py             # Map generation and collision detection
└── states/
    ├── game_state.py      # Main gameplay state
    └── menu_state.py      # Menu state
```

## Assets

The game uses custom sprite sheets and tile sets:
- Character animations from RPG character packs
- Tile sets for ground, paths, and environment
- Object sprites for houses, trees, and decorations

## Development

The game is built with a modular architecture making it easy to extend:
- Add new game states by extending the state system
- Expand the map by modifying the layout in `tilemap.py`
- Add new character animations through the asset loader
- Implement new features using the existing component system

## License

This project is for educational and demonstration purposes. Please ensure you have proper licenses for any assets used in commercial projects.