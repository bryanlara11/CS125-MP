"""
Arrow Spawner Module

This module handles the spawning and management of arrows in the rhythm game.
It provides:
- Arrow creation and initialization
- Arrow movement and positioning
- Arrow state management
- Integration with pattern manager
- Arrow cleanup and removal

The module is responsible for creating and managing the visual arrows
that players need to hit in time with the music.

Game Mechanics:
- Arrows spawn based on song timing
- Arrows move at constant speed
- Arrows can be in normal or gravity mode
- Arrows are synchronized with music
- Arrows are removed after being hit or missed

Technical Features:
- Pattern-based arrow generation
- Timing synchronization
- State management
- Resource optimization
- Collision detection preparation
"""

import queue
import pandas as pd
from game.constants import SPAWN_WINDOW, WINDOW_WIDTH, WINDOW_HEIGHT, ARROW_SPACING, NORMAL_HIT_ZONE_Y, GRAVITY_HIT_ZONE_Y
from Sprites.tiles import Tiles, spawn_positions
from game.pattern_manager import PatternManager
import os
import pygame
import random
import time
from game.constants import (
    BASE_ARROW_SPEED, DIFFICULTY_SPEEDS,
    MUSIC_START_DELAY
)

class ArrowSpawner:
    """
    Manages the creation and movement of arrows in the rhythm game.
    
    This class is responsible for:
    1. Reading arrow patterns from song data
    2. Spawning arrows at the correct times
    3. Managing arrow movement and positioning
    4. Handling arrow state transitions
    5. Coordinating with the pattern manager
    
    The spawner ensures:
    - Accurate timing with music
    - Smooth arrow movement
    - Proper arrow cleanup
    - Resource efficiency
    """
    
    def __init__(self, arrows, songs_data):
        self.spawn_queue = queue.Queue()
        self.timestamp_key_dict = {}
        self.arrows = arrows
        self.key_to_arrow = {
            'd': 'left_arrow',
            'f': 'down_arrow',
            'j': 'up_arrow',
            'k': 'right_arrow'
        }
        self.pattern_manager = PatternManager()
        self.use_patterns = False  # Flag to determine if we're using patterns or CSV
        self.difficulty = 'easy'  # Default, will be set in pattern mode
        self.spawning_allowed = True # Flag to control spawning
        self.songs_data = songs_data # Store the songs data
        self.last_spawn_time = 0
        self.spawn_delay = 1.0  # Base delay between spawns
        self.pattern_mode = False
        self.pattern_index = 0
        self.pattern = []
        self.timestamps = []
        self.arrow_group = pygame.sprite.Group()
        self.spawn_timer = 0
        self.is_spawning = False
        
        # Get arrow speed based on difficulty
        self.arrow_speed = DIFFICULTY_SPEEDS.get(self.difficulty, BASE_ARROW_SPEED)
        
        # Initialize spawn timing
        self.spawn_delay = SPAWN_WINDOW
        self.music_start_delay = MUSIC_START_DELAY

    def get_sprite(self, key):
        """Get the sprite for a given key."""
        arrow_key = self.key_to_arrow.get(key)
        if arrow_key:
            return self.arrows.get(arrow_key)
        return None

    def spawn_arrow(self, current_time, arrow_group, gravity_mode=False):
        """Spawn a new arrow based on the current game mode and time."""
        if not self.spawning_allowed:
            return

        if self.use_patterns:
            # Use key log timestamps for timing, but select pattern for each
            if not self.spawn_queue.empty():
                item = self.spawn_queue.queue[0]
                if 0 <= item - current_time <= SPAWN_WINDOW:
                    timestamp = round(self.spawn_queue.get(), 3)
                    # Instead of using the original key, select a pattern
                    pattern_keys = self.pattern_manager.get_weighted_pattern(self.difficulty)
                    for key in pattern_keys:
                        tile_img = self.get_sprite(key)
                        if tile_img is None:
                            print(f"[ERROR] No sprite found for key: '{key}'")
                            continue
                        tile = Tiles(tile_img, spawn_positions[key], key)
                        if gravity_mode:
                            # In gravity mode, spawn at the bottom of the screen
                            tile.rect.bottom = WINDOW_HEIGHT + 100
                        else:
                            # In normal mode, spawn at the top of the screen
                            tile.rect.top = -100
                        arrow_group.add(tile)
            return

        # Normal mode (using CSV timestamps)
        if not self.spawn_queue.empty():
            item = self.spawn_queue.queue[0]
            if 0 <= item - current_time <= SPAWN_WINDOW:
                timestamp = round(self.spawn_queue.get(), 3)
                keys = self.timestamp_key_dict.get(timestamp, [])
                
                # Handle both single key and list of keys
                if isinstance(keys, str):
                    keys = [keys]
                
                for key in keys:
                    if not key:
                        continue
                        
                    tile_img = self.get_sprite(key)
                    if tile_img is None:
                        print(f"[ERROR] No sprite found for key: '{key}'")
                        continue
                        
                    tile = Tiles(tile_img, spawn_positions[key], key)
                    if gravity_mode:
                        # In gravity mode, spawn at the bottom of the screen
                        tile.rect.bottom = WINDOW_HEIGHT + 100
                    else:
                        # In normal mode, spawn at the top of the screen
                        tile.rect.top = -100
                    arrow_group.add(tile)

    def add_timestamps(self, song_key):
        """Add timestamps from the song's CSV file."""
        song_info = self.songs_data.get(song_key)
        if not song_info:
            print(f"[ERROR] No song info found for key: {song_key}")
            return

        # Clear existing timestamps
        self.spawn_queue = queue.Queue()
        self.timestamp_key_dict = {}

        # Get the key log file path
        key_log_file = song_info.get("key_log_file")
        if not key_log_file:
            print(f"[ERROR] No key log file specified for song: {song_key}")
            return

        try:
            # Read the CSV file
            df = pd.read_csv(key_log_file)
            
            # In hard mode, shuffle the keys while keeping timestamps
            if self.difficulty == 'hard':
                # Get all keys and shuffle them
                all_keys = df['key'].tolist()
                random.shuffle(all_keys)
                # Replace the original keys with shuffled ones
                df['key'] = all_keys
            
            # Process each row
            for _, row in df.iterrows():
                timestamp = round(float(row['timestamp']), 3)
                keys = str(row['key']).strip()  # Convert to string and remove whitespace
                
                # Split keys if multiple are present (comma-separated)
                if ',' in keys:
                    keys = [k.strip() for k in keys.split(',')]
                else:
                    keys = [keys]
                
                # Validate all keys
                valid_keys = []
                for key in keys:
                    if key in self.key_to_arrow:
                        valid_keys.append(key)
                    else:
                        print(f"[WARNING] Invalid key '{key}' found in CSV, skipping")
                
                if valid_keys:
                    # Add to queues
                    self.spawn_queue.put(timestamp)
                    self.timestamp_key_dict[timestamp] = valid_keys
            
            print(f"[DEBUG] Loaded {len(df)} timestamps from {key_log_file}")
            
        except FileNotFoundError:
            print(f"[ERROR] Key log file not found: {key_log_file}")
        except Exception as e:
            print(f"[ERROR] Failed to load CSV file: {e}")

    def start_pattern_mode(self, difficulty):
        """Start pattern mode with the given difficulty."""
        self.use_patterns = True
        self.difficulty = difficulty
        self.pattern_mode = True
        self.pattern_index = 0
        self.pattern = []
        self.spawn_queue = queue.Queue()
        self.timestamp_key_dict = {}
        
        # Generate initial timestamps for pattern mode
        current_time = 0
        while current_time < 300:  # 5 minutes of patterns
            self.spawn_queue.put(current_time)
            current_time += random.uniform(0.5, 1.5)  # Random interval between patterns

    def start_spawning(self):
        """
        Begin the arrow spawning process.
        
        This method:
        1. Resets spawn timers
        2. Activates spawning
        3. Prepares for first arrow
        """
        self.spawn_timer = time.time()
        self.last_spawn_time = self.spawn_timer
        self.is_spawning = True

    def stop_spawning(self):
        """
        Stop the arrow spawning process.
        
        This method:
        1. Deactivates spawning
        2. Clears spawn timers
        3. Prepares for cleanup
        """
        self.is_spawning = False
        self.spawn_timer = 0
        self.last_spawn_time = 0

    def update(self, gravity_mode=False):
        """
        Update arrow positions and spawn new arrows.
        
        This method:
        1. Updates existing arrow positions
        2. Spawns new arrows based on timing
        3. Removes arrows that are off-screen
        4. Handles gravity mode transitions
        
        Args:
            gravity_mode: Whether the game is in gravity mode
        """
        current_time = time.time()
        
        # Spawn new arrows if enough time has passed
        if self.is_spawning and (current_time - self.last_spawn_time) >= self.spawn_delay:
            self._spawn_arrow(gravity_mode)
            self.last_spawn_time = current_time
        
        # Update existing arrows
        for arrow in self.arrow_group:
            # Move arrow based on gravity mode
            if gravity_mode:
                arrow.rect.y -= self.arrow_speed  # Move upward in gravity mode
            else:
                arrow.rect.y += self.arrow_speed  # Move downward in normal mode
            
            # Remove arrows that are off-screen
            if (gravity_mode and arrow.rect.bottom < 0) or \
               (not gravity_mode and arrow.rect.top > WINDOW_HEIGHT):
                self.arrow_group.remove(arrow)

    def _spawn_arrow(self, gravity_mode):
        """
        Spawn a new arrow based on the current pattern.
        
        This method:
        1. Gets the next pattern from the pattern manager
        2. Creates arrow sprites
        3. Positions them correctly
        4. Adds them to the arrow group
        
        Args:
            gravity_mode: Whether the game is in gravity mode
        """
        pattern = self.pattern_manager.get_next_pattern()
        if pattern:
            for key in pattern.keys:
                # Create arrow sprite
                arrow = Arrow(self.arrows[key], key)
                
                # Position arrow based on gravity mode
                if gravity_mode:
                    # Start from bottom in gravity mode
                    arrow.rect.bottom = WINDOW_HEIGHT
                else:
                    # Start from top in normal mode
                    arrow.rect.top = 0
                
                # Set horizontal position
                arrow.rect.centerx = WINDOW_WIDTH // 2 + (ord(key) - ord('f')) * 100
                
                self.arrow_group.add(arrow)

    def cleanup(self):
        """
        Clean up arrow resources.
        
        This method:
        1. Stops spawning
        2. Removes all arrows
        3. Resets state
        """
        self.stop_spawning()
        self.arrow_group.empty()

class Arrow(pygame.sprite.Sprite):
    """
    Represents a single arrow in the game.
    
    This class:
    1. Manages arrow appearance
    2. Tracks arrow position
    3. Handles arrow state
    4. Provides hit detection data
    
    Each arrow:
    - Moves at constant speed
    - Has a hitbox for collision detection
    - Links to a specific key
    """
    
    def __init__(self, image, key):
        """
        Initialize an arrow sprite.
        
        Args:
            image: The arrow image to use
            key: The keyboard key this arrow corresponds to
        """
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.key = key
        self.hitbox = self.rect.copy()  # Create hitbox for collision detection 