
# Whispers of The Undead

**Whispers of The Undead** is a 2D vampire-themed action roguelike game built using **Python** and **Pygame**. Players control a vampire navigating an ancient castle, facing wave-based enemy combat, unlocking abilities, and uncovering a dark story.

---

## 🎮 Gameplay Overview

* **Top-down perspective** with WASD movement and mouse-based aiming
* **Wave-based combat** with scaling difficulty and diverse enemy types
* **Room exploration system** with multiple connected castle areas
* **Unlockable vampire powers** and resource-based ability management
* **Text-driven story** revealing secrets of the cursed castle

---

## 🕹️ Player Controls

| Action         | Key / Input              |
| -------------- | ------------------------ |
| Move           | W / A / S / D            |
| Aim & Attack   | Mouse (Left Click)       |
| Dash           | Space (15 Blood Essence) |
| Mist Form      | Q (20 Blood Essence)     |
| Bat Transform  | E (30 Blood Essence)     |
| Toggle Minimap | M                        |

---

## ⚔️ Player Abilities

* **Basic Attack**: Fires a projectile toward the cursor; has a cooldown
* **Dash**: Quick movement burst
* **Mist Form**: Temporary invincibility
* **Bat Transform**: Increases movement speed for 3 seconds

*Abilities are unlocked every wave from randomized options.*

---

## ❤️ Resource Systems

### Health System

* Heart-based system (starts with 3 hearts)
* Temporary invincibility after taking damage
* Game over when health reaches 0

### Blood Essence

* Used to activate special abilities
* Max capacity of 100 (upgradable)
* Earned by defeating enemies (different enemies drop different amounts)

---

## 👹 Enemy Types

| Enemy      | HP | Traits                                                                                     |
| ---------- | -- | ------------------------------------------------------------------------------------------ |
| Bats       | 2  | Basic, slow enemies; drop 10 Blood Essence                                                 |
| Vampires   | 3  | Faster enemies; can teleport behind the player; drop 20 Blood Essence                      |
| Werewolves | 4  | Fastest enemies; become enraged at low health (increase size/speed); drop 30 Blood Essence |

---

## 🧠 Enemy AI

* **A\*** Pathfinding for navigation
* **State Machine Behavior**:

  * **Hunt**: Pursue the player
  * **Dodge**: Evade after being hit
  * **Recover**: Brief pause after damage

---

## 🌊 Wave & Upgrade System

* Game progresses through **numbered waves**
* Every wave increases in difficulty and enemy count
* Every **3 waves**, choose one of:

  * Unlock new ability
  * Increase max Blood Essence
  * Gain an extra health heart
* Story elements and environmental changes triggered at specific waves

---

## 🏰 Environment

* Castle includes:

  * Castle Entrance
  * Connecting Hallway
  * Grand Hall
* Each room has unique layouts and is restricted to defined playable zones
* **Minimap available** (press `M`)

---

## 🧾 UI Features

* Heart-based **Health Display**
* **Blood Essence Meter**
* **Wave Counter**
* **Current Room Indicator**
* Optional **Minimap**
* **Enemy Health Bars** during combat

---

## 📖 Story Elements

* Text-based story snippets revealed as you progress
* Narrative centers on the search for a powerful **Blood Relic**
* Face the **Castle Master** in a final confrontation

---

## 🛠️ Built With

* **Python 3.x**
* **Pygame**
* Object-Oriented Programming principles
* A\* Algorithm for AI pathfinding
* Finite State Machines for enemy behavior

---

## 📸 Screenshots / Demo

*To be added*

---

## 📂 Project Structure

```
/assets       # Sprites, audio, and other media
/game         # Core game modules (player, enemies, levels, UI)
main.py       # Entry point
README.md     # You're here
```

---

## 🚀 Getting Started

1. Clone the repo

   ```bash
   git clone https://github.com/yourusername/whispers-of-the-undead.git
   cd whispers-of-the-undead
   ```

2. Install dependencies

   ```bash
   pip install pygame
   ```

3. Run the game

   ```bash
   python main.py
   ```

---

