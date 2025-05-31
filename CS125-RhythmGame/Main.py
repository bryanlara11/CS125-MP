"""
Main entry point for the Rhythm Game application.

This module initializes the game environment, sets up the display window,
and launches the main menu. It handles the basic setup of pygame and
configures the working directory for proper asset loading.

The game runs in a 1600x900 window and uses a modular structure with
separate modules for the menu system and game logic.

Dependencies:
    - pygame: For game window and event handling
    - game.menu: Contains the main menu implementation
    - game.game: Contains the main game logic
    - assets: Contains game assets like outlines and arrows
"""

import pygame
import sys
import os

# hello

# Set the working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize pygame and set video mode
pygame.init()
pygame.display.init()
pygame.display.set_mode((1600, 900))  # Set video mode before loading assets

# Now import the menu and assets
from game.menu import main_menu
from game.game import Game
from assets import outlines, arrows

if __name__ == "__main__":
    main_menu()
