"""
Hit Detection Module

This module handles the detection and scoring of player hits in the rhythm game.
It provides:
- Arrow hit detection logic
- Timing window calculations
- Score computation
- Hit feedback processing
- Accuracy tracking

The module is crucial for determining the accuracy of player inputs
and providing appropriate scoring and feedback based on timing precision.

Game Mechanics:
- Perfect hits: Within 20ms of the target time (green)
- Good hits: Within 65ms of the target time (yellow)
- Late hits: Within 100ms of the target time (red)
- Misses: Outside timing window or wrong key (gray)

Scoring System:
- Perfect: 100 points × combo multiplier
- Good: 50 points × combo multiplier
- Late: 25 points × combo multiplier
- Miss: 0 points and combo reset

Combo System:
- 1-99 hits: 1x multiplier
- 100-199 hits: 2x multiplier
- 200-299 hits: 3x multiplier
- 300+ hits: 4x multiplier
"""

from game.constants import (
    HIT_MARGIN_PERFECT,  # Perfect hit timing window (20ms)
    HIT_MARGIN_GOOD,     # Good hit timing window (65ms)
    HIT_MARGIN_LATE,     # Late hit timing window (100ms)
    SCORE_PERFECT,       # Points for perfect hits (100)
    SCORE_GOOD,          # Points for good hits (50)
    SCORE_LATE,          # Points for late hits (25)
    SCORE_MISS           # Points for misses (0)
)
import pygame
from Utility.audio_manager import audio_manager
import time

class HitDetector:
    """
    Handles all hit detection and scoring logic for the rhythm game.
    
    This class is responsible for:
    1. Detecting when arrows are hit
    2. Calculating timing accuracy
    3. Managing the scoring system
    4. Tracking combo multipliers
    5. Providing visual and audio feedback
    
    The hit detection system uses a combination of:
    - Horizontal overlap detection
    - Vertical position comparison
    - Timing window calculations
    """
    
    def __init__(self):
        # Initialize scoring and feedback variables
        self.score = 0                # Total game score
        self.hit_feedback = ""        # Text to display for hit feedback
        self.hit_feedback_timer = 0   # Timer for feedback display
        self.hit_type = ""            # Type of hit (Perfect/Good/Late/Miss)
        self.hit_color = (0, 0, 0)    # Color for feedback text
        
        # Combo tracking
        self.combo = 0                # Current combo count
        self.max_combo = 0            # Highest combo achieved
        self.combo_hits = 0           # Total hits in current combo
        self.combo_score = 0          # Score from current combo
        self.misses = 0               # Total misses in the game
        
        # Key press cooldown system to prevent double-triggering
        self.last_key_press_time = {} # Dictionary to track last press time for each key
        self.key_cooldown = 0.05      # 50ms cooldown between key presses

    def check_hit(self, key, arrow_group, outline_group):
        """
        Process a key press and check for hits.
        
        The hit detection process:
        1. Check for key press cooldown
        2. Find matching arrows for the pressed key
        3. Find the corresponding outline
        4. Calculate timing accuracy
        5. Determine hit type and award points
        
        Args:
            key: The key that was pressed
            arrow_group: Group of active arrow sprites
            outline_group: Group of outline sprites
        """
        current_time = time.time()
        
        # Prevent rapid-fire key presses (anti-spam measure)
        if key in self.last_key_press_time:
            if current_time - self.last_key_press_time[key] < self.key_cooldown:
                return
        
        # Update last key press time for cooldown system
        self.last_key_press_time[key] = current_time
        
        # Find arrows that match the pressed key
        possible_hits = [arrow for arrow in arrow_group if arrow.key == key]
        if not possible_hits:
            self._handle_miss()
            return
        
        # Find the corresponding outline for this key
        outline_sprite = next((o for o in outline_group if o.key == key), None)
        if not outline_sprite:
            self._handle_miss()
            return
        
        # Sort arrows by distance to outline center for accurate hit detection
        # This ensures we check the closest arrow first
        possible_hits.sort(key=lambda a: abs(a.hitbox.centery - outline_sprite.rect.centery))
        closest_arrow = possible_hits[0]
        
        # Check horizontal overlap between arrow and outline
        # This ensures the arrow is aligned with the correct lane
        if not (closest_arrow.hitbox.right >= outline_sprite.rect.left and 
                closest_arrow.hitbox.left <= outline_sprite.rect.right):
            self._handle_miss()
            return
        
        # Calculate vertical overlap for precise hit detection
        # This ensures the arrow is within the hit zone
        vertical_overlap = min(closest_arrow.hitbox.bottom, outline_sprite.rect.bottom) - max(closest_arrow.hitbox.top, outline_sprite.rect.top)
        if vertical_overlap <= 0:
            self._handle_miss()
            return
        
        # Calculate timing accuracy
        # The distance between arrow center and outline center determines timing
        center_dist = abs(closest_arrow.hitbox.centery - outline_sprite.rect.centery)
        is_late = closest_arrow.hitbox.centery > outline_sprite.rect.centery
        
        # Check if arrow is within the valid hit zone
        is_within_outline = (closest_arrow.hitbox.bottom >= outline_sprite.rect.top and 
                           closest_arrow.hitbox.top <= outline_sprite.rect.bottom)
        
        # Determine hit type based on timing windows
        # Each window has a different score and feedback
        if center_dist <= HIT_MARGIN_PERFECT:
            self._handle_hit("Perfect", SCORE_PERFECT, (0, 255, 0), 'perfect', arrow_group, closest_arrow)
        elif center_dist <= HIT_MARGIN_GOOD:
            self._handle_hit("Good", SCORE_GOOD, (255, 255, 0), 'good', arrow_group, closest_arrow)
        elif is_within_outline and center_dist <= HIT_MARGIN_LATE:
            self._handle_hit("Late" if is_late else "Early", SCORE_LATE, (255, 0, 0), 'good', arrow_group, closest_arrow)
        else:
            self._handle_miss()

    def _handle_hit(self, hit_type, base_score, color, sound, arrow_group, arrow):
        """
        Process a successful hit.
        
        This method:
        1. Updates the hit feedback
        2. Calculates and adds the score
        3. Updates the combo counter
        4. Plays the appropriate sound effect
        5. Removes the hit arrow
        
        Args:
            hit_type: Type of hit (Perfect/Good/Late)
            base_score: Base score for this hit type
            color: Color for feedback text
            sound: Sound effect to play
            arrow_group: Group containing the hit arrow
            arrow: The arrow that was hit
        """
        self.hit_type = hit_type
        self.hit_color = color
        self.hit_feedback = hit_type
        self.hit_feedback_timer = pygame.time.get_ticks()
        self.score += self.apply_score(base_score)
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        audio_manager.play_sound(sound)
        if arrow in arrow_group:
            arrow_group.remove(arrow)

    def _handle_miss(self):
        """
        Process a miss.
        
        This method:
        1. Resets the combo counter
        2. Updates the hit feedback
        3. Adds miss to the total count
        4. Plays the miss sound effect
        """
        self.combo = 0
        self.hit_type = "Miss"
        self.hit_color = (128, 128, 128)
        self.hit_feedback = "Miss"
        self.hit_feedback_timer = pygame.time.get_ticks()
        self.score += SCORE_MISS
        self.misses += 1
        audio_manager.play_sound('miss')

    def check_miss(self, arrow):
        """
        Handle a miss when an arrow passes the hit zone without being hit.
        
        This is called when an arrow moves past the hit zone without
        being hit by the player.
        """
        self._handle_miss()

    def cleanup(self):
        """Clean up resources when the game ends."""
        pass  # No cleanup needed anymore

    def get_combo_multiplier(self):
        """
        Calculate the current combo multiplier.
        
        The multiplier increases with longer combos:
        - 1-99 hits: 1x multiplier
        - 100-199 hits: 2x multiplier
        - 200-299 hits: 3x multiplier
        - 300+ hits: 4x multiplier
        
        Returns:
            int: Multiplier based on current combo (1-4x)
        """
        if self.combo >= 300:
            return 4
        elif self.combo >= 200:
            return 3
        elif self.combo >= 100:
            return 2
        return 1

    def apply_score(self, base_score):
        """
        Apply the current combo multiplier to the score.
        
        This method:
        1. Gets the current combo multiplier
        2. Multiplies the base score by the multiplier
        3. Returns the final score
        
        Args:
            base_score: Base score before multiplier
            
        Returns:
            int: Final score after applying multiplier
        """
        multiplier = self.get_combo_multiplier()
        return base_score * multiplier 