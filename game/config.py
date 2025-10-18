class Config:
    # Display - increased for bigger view
    SCREEN_WIDTH = 850  # Increased from 800
    SCREEN_HEIGHT = 650  # Increased from 600
    FPS = 60
    
    # Player - increased speed for larger world
    PLAYER_SPEED = 250  # Increased from 180
    PLAYER_ANIMATION_SPEED = 0.1
    
    # World - tile size matches your new tileset
    TILE_SIZE = 32
    CHUNK_SIZE = 16
    
    # Colors
    BACKGROUND = (40, 44, 52)
    UI_TEXT = (220, 220, 220)
    UI_HIGHLIGHT = (255, 203, 107)