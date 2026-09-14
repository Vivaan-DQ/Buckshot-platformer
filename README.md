# Buckshot Platformer

*This is a simplified version of the popular game known as Buckshot Roulette. I took heavy inspiration from the game and this was used m submission for my very first project for software engineering in school!


## 🎮 About

*Buckshot Platformer* is a high-stakes gambling game where players are placed in a roulette scenario (Russian roulette, hint hint) and make the choices on whether to shoot the enemy, or run this risk (I had to name it run this risk instead of shoot self for obvious reasons, after all it was a school project).

Every design decision, every line of code, every questionable life choice in this project was made by me. However, I am no artist, and my stick figures prove insufficient for such a project, and hence i had to resort to AI use for making sprites (I know its a lame thing to do, but my game had to at least look good otherwise you guys wouldn't have played it 😔)

## Features

- **2D platforming movement** - simple introductory scenes leading up to a boss fight.
- **Turn-based shotgun combat** - You'll have to play the game to know how that works...
- **The Risk Action** — a dangerous move that deliberately *Runs the risk, but grants an extra turn. High risk, high reward and if you're that kind of player, i respect that.
- **In-game rulebook** — Inspitred by the general lease of liablity in the actual game that the player is made to sign.
- **Battle log** — so that even if you're trying to play this in class, at least you don't need the volume lol.
- **Player & enemy health bars** — otherwise you wouldn't really know when someone is about to die, and that would be quite disfuctional to say the least...

## 🕹️ Controls

| Key | Action |
| --- | --- |
| `ENTER` | Start the game |
| `A` | Move left |
| `D` | Move right |
| `E` | Interact with objects, doors, items |
| `F` | Fire your weapon |
| `G` | **Run the Risk** — intentionally harms you, but grants an extra turn. Use at your own risk... obviously |
| `ESC` | Exit the rulebook |

## 🚀 Getting Started

### Prerequisites

- Python 3.x installed on your machine

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/buckshot-platformer.git
cd buckshot-platformer

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# Install the one and only dependency
pip install pygame
```

### Running the Game

```bash
python main.py
```

> ⚠️ Replace `main.py` with the actual entry-point file name of your project.

## 📸 Screenshots

### Title Screen

![Title Screen](screenshots/title-screen.png)

### Platformer Gameplay

![Platformer Gameplay](screenshots/platformer-gameplay.png)

### Combat — Round 1

![Combat Round](screenshots/combat-round.png)

### In-Game Rulebook

![Rulebook](screenshots/rulebook.png)

## 🎨 A Note on the Art (Full Transparency)

**All code, game design, and suffering: 100% human-made (me).**
**Most/all sprites and artwork: AI-generated.**

As mentioned earlier, I am no artist, most of the images were made by AI, except for the rulebook, that was like the only sprite i made one canva and i am quite proud of it.

## 🗂️ Project Structure

```javascript
buckshot-platformer/
├── main.py            # Game entry point
├── ...                # Game modules / assets
├── screenshots/       # Screenshots used in this README
└── README.md
```

## 🛠️ Built With

- **Python** — core game logic
- **Pygame** — rendering, input handling, and all things game-y *(installed via pip)*
- **`os` & `random`** — Python's standard library, for file paths and a healthy dose of chaos (respectively)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork the project and submit a pull request.

## 📜 License

This project is licensed under the MIT License, open source feel free to use it *and run the risk... (no pun intended)

(It was definitely intended)

---

*Made by Techbar Studios (My old minecraft username, this isn't an actual studio lol). A fan-made homage to Buckshot Roulette — not affiliated with the original game.*

TLDR: Buckshot roulette platformer, works on both windows and mac, made in python enjoy 😄