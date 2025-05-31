"""
Outline Manager Module

This module manages the visual outlines and effects in the rhythm game.
It provides:
- Arrow outline rendering
- Visual feedback effects
- Animation states
- Outline synchronization with arrows
- Visual style management

The module ensures consistent and appealing visual feedback
for player interactions and game events.

Game Layout:
- Four lanes (D, F, J, K keys)
- Outlines mark the hit zones
- Outlines can be at top or bottom based on gravity mode
- Each outline has a unique visual style

Visual Feedback:
- Outlines provide visual targets for arrows
- Position changes based on gravity mode
- Helps players track timing and accuracy
"""

import pygame
from Sprites.outlines import Outline, outline_positions
from game.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, OUTLINE_SPACING,
    NORMAL_HIT_ZONE_Y, GRAVITY_HIT_ZONE_Y, HIT_ZONE_EDGE_DISTANCE
)

class OutlineManager:
    """
    Manages the visual outlines that serve as hit zones in the game.
    
    This class is responsible for:
    1. Creating and positioning outlines
    2. Managing outline states
    3. Handling gravity mode transitions
    4. Maintaining visual consistency
    
    The outline system provides:
    - Visual targets for players
    - Hit zone indicators
    - Game mode feedback
    """
    
    def __init__(self, outlines):
        """
        Initialize the outline manager.
        
        Args:
            outlines: Dictionary containing outline images for each key
        """
        self.outlines = outlines
        self.outline_positions = {}  # Store original positions for reference
        
        # Map keyboard keys to their corresponding outline types
        # This mapping ensures correct visual feedback for each key
        self.key_to_outline_key = {
            'd': 'left_outline',    # Left arrow outline (D key)
            'f': 'down_outline',    # Down arrow outline (F key)
            'j': 'up_outline',      # Up arrow outline (J key)
            'k': 'right_outline'    # Right arrow outline (K key)
        }

    def add_outlines(self, outline_group, gravity_mode=False):
        """
        Add outlines to the group with appropriate positioning.
        
        This method:
        1. Clears existing outlines
        2. Creates new outlines for each key
        3. Positions them based on gravity mode
        4. Stores their positions for reference
        
        Args:
            outline_group: Pygame sprite group to add outlines to
            gravity_mode: Whether the game is in gravity mode (arrows fall up)
        """
        outline_group.empty()  # Clear existing outlines
        
        # Create and position outlines for each key
        for key in ['d', 'f', 'j', 'k']:
            # Get the appropriate outline image for this key
            outline_key = self.key_to_outline_key[key]
            image = self.outlines[outline_key]
            pos = outline_positions[key]  # Get predefined position for this key
            outline = Outline(image, pos[0], key)  # Create outline sprite
            
            # Position outline based on gravity mode
            if gravity_mode:
                # In gravity mode, place outline at top of screen
                # This creates the effect of arrows falling upward
                outline.rect.y = HIT_ZONE_EDGE_DISTANCE - outline.rect.height
            else:
                # In normal mode, place outline at bottom of screen
                # This creates the standard falling arrows effect
                outline.rect.y = WINDOW_HEIGHT - HIT_ZONE_EDGE_DISTANCE
                
            outline_group.add(outline)
            
            # Store original position for reference
            # This helps with position restoration and transitions
            self.outline_positions[key] = {
                'x': outline.rect.x,
                'y': outline.rect.y
            }

    def update_outline_positions(self, outline_group, gravity_mode):
        """
        Update outline positions based on gravity mode.
        
        This method:
        1. Iterates through all outlines
        2. Updates their positions based on gravity mode
        3. Maintains visual consistency during mode changes
        
        Args:
            outline_group: Group containing outline sprites
            gravity_mode: Whether the game is in gravity mode
        """
        for outline in outline_group:
            if gravity_mode:
                # Move outlines to top in gravity mode
                # Creates the upward-falling arrows effect
                outline.rect.y = HIT_ZONE_EDGE_DISTANCE - outline.rect.height
            else:
                # Move outlines to bottom in normal mode
                # Creates the standard falling arrows effect
                outline.rect.y = WINDOW_HEIGHT - HIT_ZONE_EDGE_DISTANCE

class Outline(pygame.sprite.Sprite):
    """
    Represents a single outline sprite in the game.
    
    This class:
    1. Manages individual outline appearance
    2. Tracks outline position
    3. Links outlines to keyboard keys
    
    Each outline serves as:
    - A visual target for arrows
    - A hit zone indicator
    - A key mapping reference
    """
    
    def __init__(self, image, x_pos, key):
        """
        Initialize an outline sprite.
        
        Args:
            image: The outline image to use
            x_pos: Horizontal position of the outline
            key: The keyboard key this outline corresponds to
        """
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.key = key 