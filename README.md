# Indie-Game

![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)
![Language](https://img.shields.io/badge/language-Python%203.9-3776AB?logo=python&logoColor=white)
![Engine](https://img.shields.io/badge/engine-Pygame-00457C)
![Architecture](https://img.shields.io/badge/architecture-Monolithic-lightgrey)

A story-driven 2D indie game built in Python, blending farming, building, and survival mechanics with combat, trading, and a day/night cycle — inspired by titles like *Stardew Valley*, *Terraria*, and *Staxel*.

---

## Overview

Indie-Game is a single-player 2D adventure where the player grows crops, raises animals, fights enemies, builds and modifies their surroundings, trades resources, and completes story objectives, all while progress is automatically tracked and can be saved or loaded between sessions. The game runs fully offline, requires no network connection, and stores all data locally on the player's machine.

## Main Features

- Player movement and interaction with in-game objects
- Animals and plants with unique behaviors and growth/care cycles
- Farming: planting, growing, and harvesting crops
- Combat with enemies and reward collection
- Resource and finance management, including a trading system
- Building and environment customization
- Story-driven objectives and quests with progress tracking
- Dynamic day/night cycle affecting gameplay
- Save and load progress via local file storage
- Dynamic scenes with smooth transitions between menus and gameplay
- Configurable settings (resolution, volume) stored in data files
- Expandable, modular architecture for adding new features

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9 |
| Game engine | Pygame (graphics, sound, input, timing) |
| Map loading | PyTmx (Tiled Map Editor integration) |
| Persistence | Pickle (serialization/deserialization to local `.txt` save files) |
| IDE | Visual Studio Code |
| Version control | Git / GitHub |
| Architecture style | Monolithic — all game logic, state, and rendering run in a single application |

## Design Patterns

The codebase applies several classic design patterns to keep the architecture maintainable and extensible:

- **Game Loop** — drives the core update/render cycle, processing input and refreshing game state every frame
- **State** — governs how entities (player, animals, enemies) change behavior during execution
- **Composite** — lets the game treat individual objects and groups of objects (e.g. a tree and the fruit it yields) uniformly
- **Decorator** — adds new functionality to existing objects (e.g. assigning animals to buildings) without altering their structure

## Project Structure

The project is organized into five main packages, each responsible for a distinct part of the game:

- **Entities**: Game objects such as the player, animals, plants, NPCs, and enemies, along with their individual behaviors and logic.
- **Graphics**: Graphical assets and rendering logic, including animations triggered by object interaction or destruction.
- **Interface**: Menus, heads-up display (HUD), and UI components such as tool and seed selection.
- **Scene**: Game scenes, level/map loading and collision handling, and scene transitions.
- **Utils**: Helper functions, timers, and shared utilities used across the game.
- **main.py**: Entry point of the game.

### Key Classes

- `Level` — manages everything placed on the map (objects, layers, collisions) via PyTmx; handles setup, level reset, and shop interaction
- `Player` — handles movement, tool/seed use, animations, collisions, and interaction with animals, enemies, NPCs, and buildings
- `Overlay` — renders the in-game tool/seed HUD
- `Menu` — handles the trading/shop interface
- `Transition` — manages visual transitions between scenes
- `Rain` / `DayChange` — handle weather and the day/night cycle

## Requirements

**Functional** (selected highlights — see full specification in project documentation)
- Start a new game with selectable difficulty
- Save progress to a local `.txt` file (serialized with Pickle) and load it later
- Navigate a main menu (new game, load, settings, exit)
- Grow and harvest crops
- Raise and care for animals
- Manage resources and finances, including trading
- Complete quests/objectives and receive rewards
- Modify and extend game content (developer-facing)

**Non-functional**
- Runs as a standalone desktop application
- Targets Windows 10
- Fully offline — no internet connection required
- Simple, intuitive interface usable without prior instructions

## Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/AndreyMaksimenko/Indie-Game.git
cd Indie-Game
pip install pygame pytmx
```

### Running the game

```bash
python main.py
```

## Testing

The game was validated against its functional requirements using a dedicated set of 27 test cases covering new game creation, save/load, menu navigation, farming, harvesting, animal care, resource/trading management, quest completion, and content updates. All 27 test cases passed.

## Developed by

**Maksymenko Andrii**
