Whispers of The Undead - Game Mechanics Overview
Based on the code, "Whispers of The Undead" is a 2D vampire-themed action game with roguelike elements. Here's a comprehensive breakdown of the game mechanics:
Core Gameplay
Top-down perspective where you control a vampire character navigating through an ancient castle
Mouse-based aiming - your character rotates to face your mouse cursor
WASD movement for navigating around the castle rooms
Wave-based combat against progressively harder enemies
Room exploration system with different connected areas in the castle
Player Abilities
Basic Abilities
Vampire Attack - Left mouse button fires a projectile in the direction you're facing
Attack has a cooldown period before you can use it again
Unlockable Abilities
You gain these every 3 waves by selecting from random upgrade options:
Dash Ability (Space key) - Quick burst of speed in your movement direction (costs 15 Blood Essence)
Mist Form (Q key) - Temporary invincibility (costs 20 Blood Essence)
Bat Transform (E key) - Increased movement speed for 3 seconds (costs 30 Blood Essence)
Resource Systems
Health System
Heart-based health (starts with 3 hearts)
Taking damage from enemies reduces hearts
Temporary invincibility after being hit
Game over when health reaches zero
Blood Essence
Resource for using special vampire abilities
Maximum of 100 (can be upgraded)
Collected by defeating enemies (they drop blood pickups)
Different enemies yield different amounts of Blood Essence
Enemy Types
Bats


Basic enemies with low health (2 HP)
Slow movement speed
Drop 10 Blood Essence
Vampires


Medium health (3 HP)
Faster than Bats
Special ability: can teleport behind the player
Drop 20 Blood Essence
Werewolves


High health (4 HP)
Fastest enemy type
Special ability: becomes enraged at low health (faster and larger)
Drop 30 Blood Essence
Enemy Behavior
Enemies use A* pathfinding to navigate to the player
They have a state machine with different behaviors:
Hunt: Normal pursuit of player
Dodge: Move away from player after being damaged
Recover: Stand still temporarily after taking damage
Wave System & Progression
Game progresses through numbered waves
Each wave spawns more enemies than the last
Enemy types become more diverse in later waves
Every 3 waves, you get to choose an upgrade
Story events trigger at specific wave numbers
Upgrades System
When offered, you can choose from:
Special abilities (Dash, Mist Form, Bat Transform)
Increased Blood Essence capacity
Additional health hearts
Castle Environment
Multiple interconnected rooms:
Castle Entrance
Connecting Hallway
Grand Hall
Rooms have different layouts
Navigation is restricted to defined playable areas
Minimap available (toggle with M key)
UI Features
Health display (hearts)
Blood Essence meter
Current wave counter
Current room indicator
Optional minimap (M key)
Visible enemy health bars
Story Elements
Text-based story progression as you advance through waves
Area descriptions when discovering new rooms
Narrative about seeking a "blood relic" and confronting the castle's master
This vampire-themed action game combines resource management, ability usage, and wave survival with exploration elements to create an engaging gameplay experience.
