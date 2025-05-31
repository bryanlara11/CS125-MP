"""
Menu System Module

This module implements the game's menu system and user interface.
It provides:
- Main menu interface
- Song selection
- Difficulty settings
- Game options
- Visual feedback and transitions
- User input handling for menu navigation

The module creates an interactive menu system that allows players
to navigate through different game options and start gameplay.

Menu Structure:
1. Main Menu
   - Song Selection
   - Coming Soon Features
   - Quit Game

2. Song Selection
   - List of available songs
   - Song details (title, artist)
   - Difficulty selection

3. Difficulty Selection
   - Easy (120 BPM)
   - Medium (140 BPM)
   - Hard (160 BPM)

4. Game Modes
   - Normal Mode (song-based)
"""

import pygame
import sys
import os
from Utility.font_manager import font_manager
from game.game import Game
from assets import outlines, arrows

# Screen configuration
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# UI color scheme for consistent visual design
COLORS = {
    "GOLD": "#b68f40",      # Accent color for important elements
    "GREEN": "#d7fcd4",     # Primary text color
    "WHITE": "White",       # Secondary text color
    "BLACK": "black",       # Background elements
    "HOVER_GREEN": "#a0f5b0", # Interactive element hover state
    "RED": "red"            # Warning/error states
}

# Song database containing all available songs and their properties
SONGS = {
    "song1": {
        "title": "Realize (Re:Zero Opening 2)",
        "artist": "Konomi Suzuki",
        "music_file": "assets/songs/Song 1/audio/song1.mp3",
        "key_log_file": "assets/songs/Song 1/key_log.csv",
        "difficulty": {
            "easy": {"bpm": 120},    # Slower tempo for beginners
            "medium": {"bpm": 140},  # Moderate challenge
            "hard": {"bpm": 160}     # Fast-paced gameplay
        }
    },
    "song2": {
        "title": "Zenzenzense (Your Name)",
        "artist": "RADWIMPS",
        "music_file": "assets/songs/Song 2/audio/song2.mp3",
        "key_log_file": "assets/songs/Song 2/key_log2.csv",
        "difficulty": {
            "easy": {"bpm": 120},
            "medium": {"bpm": 140},
            "hard": {"bpm": 160}
        }
    },
    "song3": {
        "title": "Silhouette (Naruto Opening 16)",
        "artist": "KANA-BOON",
        "music_file": "assets/songs/Song 3/audio/song3.mp3",
        "key_log_file": "assets/songs/Song 3/key_log.csv",
        "difficulty": {
            "easy": {"bpm": 120},
            "medium": {"bpm": 140},
            "hard": {"bpm": 160}
        },
        "volume": 1.0,  # Custom volume setting for this song
        "VIDEO_START_DELAY" : 5.0 #Custom video start delay for this song
    }
}

class Button:
    """
    Interactive button class for menu navigation.
    
    Features:
    - Dynamic sizing based on content
    - Hover effects
    - Multi-line text support
    - Custom styling
    - Click detection
    
    The button system provides:
    - Visual feedback on interaction
    - Consistent styling across menus
    - Flexible layout options
    - Accessible user interface
    """
    
    def __init__(self, image, pos, text_input, font_size, base_color, hovering_color, width=None, height=None):
        """
        Initialize a button with specified properties.
        
        Args:
            image: Optional background image
            pos: (x, y) position on screen
            text_input: Button text (supports multiple lines with \n)
            font_size: Text size
            base_color: Normal state color
            hovering_color: Hover state color
            width: Optional fixed width
            height: Optional fixed height
        """
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font_manager.get_font(font_size)
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.is_hovering = False
        self.width = width
        self.height = height

        # Standard button dimensions for consistency
        standard_width = 350
        standard_height = 90

        # Calculate button dimensions based on content or use standard size
        if self.width is not None and self.height is not None:
            button_width = self.width
            button_height = self.height
        elif image is None:
            button_width = standard_width
            button_height = standard_height
        else:
            # Calculate size based on text content
            padding_x = 30
            padding_y = 20
            lines = self.text_input.split('\n')
            max_width = 0
            total_height = 0
            for line in lines:
                line_surface = self.font.render(line, True, self.base_color)
                max_width = max(max_width, line_surface.get_width())
                total_height += line_surface.get_height()

            button_width = max_width + 2 * padding_x
            button_height = total_height + 2 * padding_y
            
        # Create button surface if no image provided
        if self.image is None:
            self.image = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            
            # Draw button with modern styling
            button_color = (50, 50, 50, 180)  # Semi-transparent dark gray
            border_color = (200, 200, 200)    # Light gray border
            border_width = 3
            border_radius = 10
            
            # Draw button background and border
            pygame.draw.rect(self.image, button_color, (0, 0, button_width, button_height), border_radius=border_radius)
            pygame.draw.rect(self.image, border_color, (0, 0, button_width, button_height), border_width, border_radius=border_radius)

            # Render text with proper centering
            lines = self.text_input.split('\n')
            current_y = (button_height - sum(self.font.render(line, True, self.base_color).get_height() for line in lines)) // 2
            for line in lines:
                line_surface = self.font.render(line, True, self.base_color)
                line_rect = line_surface.get_rect(center=(button_width // 2, current_y + line_surface.get_height() // 2))
                self.image.blit(line_surface, line_rect)
                current_y += line_surface.get_height()

        # Set button position
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        """
        Draw the button on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        screen.blit(self.image, self.rect)

    def checkForInput(self, position):
        """
        Check if a position is within the button's bounds.
        
        Args:
            position: (x, y) coordinates to check
            
        Returns:
            bool: True if position is within button bounds
        """
        return (position[0] in range(self.rect.left, self.rect.right) and
                position[1] in range(self.rect.top, self.rect.bottom))

    def changeColor(self, position):
        """
        Update button appearance based on hover state.
        
        This method:
        1. Checks if mouse is over button
        2. Updates visual state
        3. Redraws button with appropriate colors
        
        Args:
            position: Current mouse position
        """
        is_now_hovering = self.checkForInput(position)

        if is_now_hovering != self.is_hovering:
            self.is_hovering = is_now_hovering
            # Re-render the button image with the appropriate text color
            text_color = self.hovering_color if self.is_hovering else self.base_color

            # Redraw button with updated colors
            button_width, button_height = self.image.get_size()
            self.image = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            
            button_color = (50, 50, 50, 180)
            border_color = (255, 0, 0) if self.is_hovering else (200, 200, 200)
            border_width = 3
            border_radius = 10

            # Draw updated button
            pygame.draw.rect(self.image, button_color, (0, 0, button_width, button_height), border_radius=border_radius)
            pygame.draw.rect(self.image, border_color, (0, 0, button_width, button_height), border_width, border_radius=border_radius)

            # Update text with new color
            lines = self.text_input.split('\n')
            current_y = (button_height - sum(self.font.render(line, True, self.base_color).get_height() for line in lines)) // 2
            for line in lines:
                line_surface = self.font.render(line, True, text_color)
                line_rect = line_surface.get_rect(center=(button_width // 2, current_y + line_surface.get_height() // 2))
                self.image.blit(line_surface, line_rect)
                current_y += line_surface.get_height()

def start_game(song_key, difficulty):
    """
    Initialize and start the rhythm game.
    
    This function:
    1. Sets up the game environment
    2. Initializes audio
    3. Creates game instance
    4. Handles game flow
    5. Manages navigation after game ends
    
    Args:
        song_key: Key of selected song
        difficulty: Game difficulty level
    """
    # Initialize audio system
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        
    # Create and run game instance
    game = Game(outlines, arrows, SONGS, song_key, difficulty)
    next_action = game.run()
    
    # Clean up game resources
    game.cleanup()
    
    # Handle post-game navigation
    if next_action == 'restart':
        pygame.time.wait(100)  # Brief delay for cleanup
        start_game(song_key, difficulty)
    elif next_action == 'difficulty_select':
        pattern_selection(song_key) # Go back to difficulty selection for the same song
    elif next_action == 'difficulty_select_current_song':
        pattern_selection(song_key) # Go back to difficulty selection for the song that just finished
    else: # Covers 'quit' or None (window close)
        main_menu() # Go back to the main menu

def song_selection_menu():
    """
    Display the song selection screen.
    
    This screen:
    1. Lists available songs
    2. Shows song details
    3. Handles song selection
    4. Provides navigation options
    """
    pygame.display.set_caption("Select Song")

    # Create list of available songs
    songs_list = [
        {"key": key, "title": song_info["title"], "artist": song_info.get("artist", "Unknown Artist")}
        for key, song_info in SONGS.items()
        if "title" in song_info
    ]

    # Check if there are any songs available
    if not songs_list:
        print("[ERROR] No songs found in SONGS dictionary.")
        # Optionally, return to main menu or display an error message
        main_menu()
        return

    # Scrolling state variable
    current_song_index = 0
    
    # Get the initial song info for the button
    initial_song = songs_list[current_song_index]

    # Define button dimensions and gap
    song_button_width = 900 # Much wider button for song title
    song_button_height = 200 # Adjusted height
    arrow_button_width = 80
    arrow_button_height = 50
    horizontal_gap = 50 # Gap between song button and arrow buttons

    # Create the single song button
    song_button = Button(
        image=None,
        pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2), # Centered vertically and horizontally
        text_input=f"{initial_song['title'].upper()}\n{initial_song['artist'].upper()}", # Combined title and artist
        font_size=40, # Adjusted font size for larger button
        base_color=COLORS["WHITE"],
        hovering_color=COLORS["RED"],
        width=song_button_width,
        height=song_button_height
    )

    # Create scroll buttons positioned to the sides of the large song button
    up_arrow_button = Button(
        image=None,
        pos=(SCREEN_WIDTH//2 - song_button_width // 2 - horizontal_gap - arrow_button_width // 2, SCREEN_HEIGHT//2 - arrow_button_height // 2), # Position to the left, vertically centered
        text_input="UP", # Could use an image later
        font_size=50,
        base_color=COLORS["WHITE"],
        hovering_color=COLORS["RED"],
        width=arrow_button_width,
        height=arrow_button_height
    )

    down_arrow_button = Button(
        image=None,
        pos=(SCREEN_WIDTH//2 + song_button_width // 2 + horizontal_gap + arrow_button_width // 2, SCREEN_HEIGHT//2 - arrow_button_height // 2), # Position to the right, vertically centered
        text_input="DOWN", # Could use an image later
        font_size=50,
        base_color=COLORS["WHITE"],
        hovering_color=COLORS["RED"],
        width=arrow_button_width,
        height=arrow_button_height
    )
    
    # Back button remains at the bottom
    back_button = Button(
        image=None,
        pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100), # Position near the bottom
        text_input="BACK",
        font_size=75,
        base_color=COLORS["WHITE"],
        hovering_color=COLORS["RED"],
        width=300, # Slightly smaller back button
        height=80
    )

    while True:
        mouse_pos = pygame.mouse.get_pos()
        SCREEN.fill(COLORS["BLACK"])

        # Get the current song info
        current_song = songs_list[current_song_index]

        # Display the consistent menu title
        title_text = font_manager.get_font(100).render("SELECT SONG", True, COLORS["GOLD"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        SCREEN.blit(title_text, title_rect)

        # Update the text of the single song button
        song_button.text_input = f"{current_song['title'].upper()}\n{current_song.get('artist', 'Unknown Artist').upper()}"
        # Re-render the song button to update its text and appearance
        song_button.changeColor(mouse_pos) # This also handles hover color change
        song_button.update(SCREEN)

        # Update and draw scroll buttons conditionally
        if current_song_index > 0:
            up_arrow_button.changeColor(mouse_pos)
            up_arrow_button.update(SCREEN)

        if current_song_index < len(songs_list) - 1:
            down_arrow_button.changeColor(mouse_pos)
            down_arrow_button.update(SCREEN)

        # Update and draw back button
        back_button.changeColor(mouse_pos)
        back_button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check scroll button input only if visible
                if current_song_index > 0 and up_arrow_button.checkForInput(mouse_pos):
                    current_song_index -= 1
                    # Force re-render of the song button with new text (combined title and artist)
                    current_song = songs_list[current_song_index]
                    song_button = Button(
                        image=None,
                        pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2), # Maintain centered position
                        text_input=f"{current_song['title'].upper()}\n{current_song.get('artist', 'Unknown Artist').upper()}",
                        font_size=40, # Adjusted font size
                        base_color=COLORS["WHITE"],
                        hovering_color=COLORS["RED"],
                        width=song_button_width,
                        height=song_button_height
                    )
                
                if current_song_index < len(songs_list) - 1 and down_arrow_button.checkForInput(mouse_pos):
                    current_song_index += 1
                    # Force re-render of the song button with new text (combined title and artist)
                    current_song = songs_list[current_song_index]
                    song_button = Button(
                        image=None,
                        pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2), # Maintain centered position
                        text_input=f"{current_song['title'].upper()}\n{current_song.get('artist', 'Unknown Artist').upper()}",
                        font_size=40, # Adjusted font size
                        base_color=COLORS["WHITE"],
                        hovering_color=COLORS["RED"],
                        width=song_button_width,
                        height=song_button_height
                    )

                # Check the single song button input
                if song_button.checkForInput(mouse_pos):
                    selected_song_key = songs_list[current_song_index]["key"]
                    pattern_selection(selected_song_key)
                    return

                # Check back button input
                if back_button.checkForInput(mouse_pos):
                    main_menu()
                    return

        pygame.display.update()

def pattern_selection(selected_song):
    """Difficulty selection screen."""
    pygame.display.set_caption("Difficulty")

    # Define fixed button height and gap
    button_height = 90
    button_gap = 30
    button_y_start = 350 # Starting position adjusted for fixed height

    # Create difficulty buttons
    difficulty_buttons = [
        Button(
            image=None,
            pos=(SCREEN_WIDTH//2, button_y_start),
            text_input="EASY",
            font_size=75,
            base_color=COLORS["WHITE"],
            hovering_color=COLORS["RED"],
            width=350, # Fixed width
            height=button_height # Fixed height
        ),
        Button(
            image=None,
            pos=(SCREEN_WIDTH//2, button_y_start + button_height + button_gap),
            text_input="MEDIUM",
            font_size=75,
            base_color=COLORS["WHITE"],
            hovering_color=COLORS["RED"],
            width=350, # Fixed width
            height=button_height # Fixed height
        ),
        Button(
            image=None,
            pos=(SCREEN_WIDTH//2, button_y_start + 2 * (button_height + button_gap)),
            text_input="HARD",
            font_size=75,
            base_color=COLORS["WHITE"],
            hovering_color=COLORS["RED"],
            width=350, # Fixed width
            height=button_height # Fixed height
        )
    ]

    # Back button
    back_button = Button(
        image=None,
        pos=(SCREEN_WIDTH//2, button_y_start + 3 * (button_height + button_gap) + 50), # Position after difficulty buttons with extra space
        text_input="BACK",
        font_size=75,
        base_color=COLORS["WHITE"],
        hovering_color=COLORS["RED"],
        width=350, # Fixed width
        height=button_height # Fixed height
    )

    while True:
        mouse_pos = pygame.mouse.get_pos()
        SCREEN.fill(COLORS["BLACK"])

        # Get song information
        song = SONGS.get(selected_song, {"title": "Unknown Song", "artist": "Unknown Artist"})

        # Draw song title (Header - h1)
        song_title_text = font_manager.get_font(70).render(song['title'].upper(), True, COLORS["GOLD"])
        song_title_rect = song_title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        SCREEN.blit(song_title_text, song_title_rect)

        # Draw difficulty selection text (Subheading - h2)
        difficulty_text = font_manager.get_font(50).render("SELECT DIFFICULTY", True, COLORS["WHITE"])
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        SCREEN.blit(difficulty_text, difficulty_rect)

        # Update and draw difficulty buttons
        for button in difficulty_buttons:
            button.changeColor(mouse_pos)
            button.update(SCREEN)

        # Update and draw back button
        back_button.changeColor(mouse_pos)
        back_button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if difficulty_buttons[0].checkForInput(mouse_pos):
                    start_game(selected_song, "easy")
                    return
                if difficulty_buttons[1].checkForInput(mouse_pos):
                    start_game(selected_song, "medium")
                    return
                if difficulty_buttons[2].checkForInput(mouse_pos):
                    start_game(selected_song, "hard")
                    return
                if back_button.checkForInput(mouse_pos):
                    song_selection_menu()
                    return

        pygame.display.update()

def main_menu():
    """Main menu screen."""
    pygame.display.set_caption("Main Menu")

    # Define fixed button height and gap
    button_height = 90
    button_gap = 40
    button_y_start = 420 # Adjusted starting position for fixed height

    # Load the background image
    background_image_path = os.path.join('graphics', 'BACKGROUND PICTURE FOR MP.png')
    try:
        background_image = pygame.image.load(background_image_path)
        # Scale the image to fit the screen size
        background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Warning: Could not load background image {background_image_path}: {e}")
        background_image = None # Fallback to black background if image not loaded

    # State variable to show 'Coming Soon' message
    show_coming_soon = False

    while True:
        mouse_pos = pygame.mouse.get_pos()
        # Draw the background image or fill with black if image not loaded
        if background_image:
            SCREEN.blit(background_image, (0, 0))
        else:
            SCREEN.fill(COLORS["BLACK"])

        # Menu title
        menu_text = font_manager.get_font(100).render("RHYTHM GAME", True, COLORS["GOLD"])
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, 200))

        # Add a semi-transparent black box behind the title
        box_padding = 20 # Add some padding around the text
        box_width = menu_rect.width + 2 * box_padding
        box_height = menu_rect.height + 2 * box_padding
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surface.fill((0, 0, 0, 180)) # Black with 180/255 alpha (around 70% opaque)
        box_rect = box_surface.get_rect(center=menu_rect.center)
        SCREEN.blit(box_surface, box_rect)

        SCREEN.blit(menu_text, menu_rect)

        # Create buttons with fixed size and adjusted positions
        play_button = Button(
            image=None,
            pos=(SCREEN_WIDTH//2, button_y_start),
            text_input="PLAY",
            font_size=75,
            base_color=COLORS["WHITE"],
            hovering_color=COLORS["RED"],
            width=400,
            height=95
        )
        endless_button = Button(
            image=None,
            pos=(SCREEN_WIDTH//2, button_y_start + button_height + button_gap),
            text_input="ENDLESS",
            font_size=75,
            base_color=COLORS["WHITE"],
            hovering_color=COLORS["RED"],
            width=400,
            height=95
        )
        quit_button = Button(
            image=None,
            pos=(SCREEN_WIDTH//2, button_y_start + 2 * (button_height + button_gap)),
            text_input="QUIT",
            font_size=75,
            base_color=COLORS["WHITE"],
            hovering_color=COLORS["RED"],
            width=400,
            height=95
        )

        # Update and draw buttons
        for button in [play_button, endless_button, quit_button]:
            button.changeColor(mouse_pos)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(mouse_pos):
                    song_selection_menu()
                    return
                if endless_button.checkForInput(mouse_pos):
                    coming_soon_panel() # Call the new coming soon panel function
                if quit_button.checkForInput(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def coming_soon_panel():
    """Displays a 'Coming Soon' panel."""
    pygame.display.set_caption("Coming Soon")

    # Create a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    # Create the 'Coming Soon' text
    coming_soon_text = font_manager.get_font(75).render("Coming Soon!", True, COLORS["WHITE"])
    coming_soon_rect = coming_soon_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

    # Create a 'Back' button
    back_button = Button(
        image=None,
        pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100), # Position near the bottom
        text_input="BACK",
        font_size=75,
        base_color=COLORS["WHITE"],
        hovering_color=COLORS["RED"],
        width=300,
        height=80
    )

    while True:
        mouse_pos = pygame.mouse.get_pos()

        # Draw the previous screen's content (optional, for transition effect)
        # Or just draw the overlay on a black screen
        SCREEN.fill(COLORS["BLACK"])
        SCREEN.blit(overlay, (0, 0))

        # Draw 'Coming Soon' text
        SCREEN.blit(coming_soon_text, coming_soon_rect)

        # Update and draw back button
        back_button.changeColor(mouse_pos)
        back_button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.checkForInput(mouse_pos):
                    main_menu() # Go back to the main menu
                    return # Exit this panel's loop

        pygame.display.update()