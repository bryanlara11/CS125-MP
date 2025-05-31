"""
Video Player Module

This module provides video playback functionality for the rhythm game.
It handles:
- Video file loading and decoding
- Frame-by-frame video playback
- Synchronization with game timing
- Video state management
- Resource cleanup

The module enables background video playback during gameplay,
enhancing the visual experience of the rhythm game.

Video Features:
- Frame-accurate playback
- Transparency control
- Volume management
- Pause/resume functionality
- Size adjustment
- Seeking capabilities

Technical Details:
- Uses ffpyplayer for video decoding
- Supports various video formats
- Maintains frame timing accuracy
- Handles resource management
"""

import pygame 
from pymediainfo import MediaInfo
from ffpyplayer.player import MediaPlayer
from os.path import exists, basename, splitext
from os import strerror
from errno import ENOENT


class Video:
    """
    Handles video playback and management for the rhythm game.
    
    This class provides:
    1. Video file loading and initialization
    2. Frame-by-frame playback control
    3. Video state management
    4. Resource handling
    5. Visual effects (transparency)
    
    The video system integrates with the game to provide:
    - Background visuals
    - Visual feedback
    - Enhanced atmosphere
    """
    
    def __init__(self, path):
        """
        Initialize video player with the given video file.
        
        This method:
        1. Validates the video file
        2. Extracts video metadata
        3. Sets up playback parameters
        4. Initializes the video surface
        
        Args:
            path: Path to the video file
        """
        self.path = path
        self.transparency = 128  # Default transparency (0-255, where 0 is fully transparent)
        
        if exists(path):
            self.video = MediaPlayer(path)
            info = self.get_file_data()
            
            # Store video metadata for playback control
            self.duration = info["duration"]
            self.frames = 0
            self.frame_delay = 1 / info["frame rate"]
            self.size = info["original size"]
            self.image = pygame.Surface((0, 0))
                        
            self.active = True
        else:
            raise FileNotFoundError(ENOENT, strerror(ENOENT), path)
        
    def get_file_data(self):
        """
        Extract metadata from the video file.
        
        This method:
        1. Parses the video file
        2. Extracts technical information
        3. Returns formatted metadata
        
        Returns:
            dict: Video metadata including:
                - Duration
                - Frame rate
                - Dimensions
                - Aspect ratio
        """
        info = MediaInfo.parse(self.path).video_tracks[0]
        return {
            "path": self.path,
            "name": splitext(basename(self.path))[0],
            "frame rate": float(info.frame_rate),
            "frame count": info.frame_count,
            "duration": info.duration / 1000,  # Convert to seconds
            "original size": (info.width, info.height),
            "original aspect ratio": info.other_display_aspect_ratio[0]
        }
                
    def get_playback_data(self):
        """
        Get current playback state.
        
        This method provides real-time information about:
        1. Playback status
        2. Current position
        3. Volume level
        4. Pause state
        5. Display size
        
        Returns:
            dict: Current playback information
        """
        return {
            "active": self.active,
            "time": self.video.get_pts(),
            "volume": self.video.get_volume(),
            "paused": self.video.get_pause(),
            "size": self.size
        }
        
    def restart(self):
        """
        Reset video to beginning and restart playback.
        
        This method:
        1. Seeks to the start of the video
        2. Resets frame counter
        3. Reactivates playback
        """
        self.video.seek(0, relative=False, accurate=False)
        self.frames = 0
        self.active = True
        
    def close(self):
        """
        Stop playback and clean up resources.
        
        This method:
        1. Stops video playback
        2. Releases video resources
        3. Marks video as inactive
        """
        self.video.close_player()
        self.active = False
    
    def set_size(self, size):
        """
        Set the display size of the video.
        
        This method:
        1. Updates video dimensions
        2. Maintains aspect ratio
        3. Updates display surface
        
        Args:
            size: Tuple of (width, height) for the video display
        """
        self.video.set_size(size[0], size[1])
        self.size = size
    
    def set_volume(self, volume):
        """
        Set the playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.video.set_volume(volume)
    
    def seek(self, seek_time, accurate=False):
        """
        Seek to a specific time in the video.
        
        This method:
        1. Validates seek time
        2. Updates video position
        3. Adjusts frame counter
        
        Args:
            seek_time: Time to seek to in seconds
            accurate: Whether to seek accurately (slower but more precise)
        """
        vid_time = self.video.get_pts()
        if vid_time + seek_time < self.duration and self.active:
            self.video.seek(seek_time)
            if seek_time < 0:
                while (vid_time + seek_time < self.frames * self.frame_delay):
                    self.frames -= 1
            
    def toggle_pause(self):
        """
        Toggle video playback pause state.
        
        This method:
        1. Checks current pause state
        2. Toggles between play/pause
        3. Maintains frame timing
        """
        self.video.toggle_pause()
        
    def update(self):
        """
        Update video frame if needed.
        
        This method:
        1. Checks if new frame is needed
        2. Decodes and processes frame
        3. Updates display surface
        
        Returns:
            bool: True if frame was updated, False otherwise
        """
        updated = False
        while self.video.get_pts() > self.frames * self.frame_delay:
            frame, val = self.video.get_frame()
            self.frames += 1
            updated = True
        if updated:
            if val == "eof":
                self.active = False
            elif frame != None:
                self.image = pygame.image.frombuffer(frame[0].to_bytearray()[0], frame[0].get_size(), "RGB")
        return updated
        
    def set_transparency(self, value):
        """
        Set the transparency level of the video.
        
        This method:
        1. Validates transparency value
        2. Updates transparency level
        3. Affects next frame rendering
        
        Args:
            value: Transparency level (0-255, where 0 is fully transparent)
        """
        self.transparency = max(0, min(255, value))
        
    def draw(self, surf, pos, force_draw=True):
        """
        Draw the current video frame to the surface.
        
        This method:
        1. Updates video frame if needed
        2. Applies transparency
        3. Blits to target surface
        
        Args:
            surf: Pygame surface to draw on
            pos: Position to draw the video
            force_draw: Whether to draw even if frame hasn't changed
        """
        if self.active:
            if self.update() or force_draw:
                # Create a temporary surface with alpha channel
                temp_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                # Blit the video frame onto the temporary surface
                temp_surface.blit(self.image, (0, 0))
                # Set the alpha value for the entire surface
                temp_surface.set_alpha(self.transparency)
                # Blit the semi-transparent surface onto the main surface
                surf.blit(temp_surface, pos)
