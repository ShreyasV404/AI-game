import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Four-Direction Sprite Animation Visualizer")

# Colors
BACKGROUND = (25, 25, 35)
PANEL_BG = (40, 40, 50)
TEXT_COLOR = (220, 220, 230)
HIGHLIGHT = (80, 180, 255)
SHADOW = (20, 20, 30)
DIRECTION_COLORS = {
    "DOWN": (100, 200, 100),
    "UP": (200, 100, 100),
    "LEFT": (200, 200, 100),
    "RIGHT": (100, 150, 200)
}

# Fonts
font_large = pygame.font.SysFont("Arial", 32, bold=True)
font_medium = pygame.font.SysFont("Arial", 24)
font_small = pygame.font.SysFont("Arial", 18)

class SpriteSheet:
    def __init__(self, filename, rows=4, cols=4, scale=3):
        self.filename = filename
        self.rows = rows
        self.cols = cols
        self.scale = scale
        
        # Load image
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            print(f"Error: {e}")
            # Create a placeholder image if file not found
            self.sheet = self._create_placeholder()
        
        # Calculate frame dimensions
        self.frame_width = self.sheet.get_width() // cols
        self.frame_height = self.sheet.get_height() // rows
        
        # Create scaled frames for each direction
        self.directions = ["DOWN", "LEFT", "RIGHT", "UP"]  # Common order in sprite sheets
        self.frames = {}
        
        for row, direction in enumerate(self.directions):
            direction_frames = []
            for col in range(cols):
                frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
                frame.blit(self.sheet, (0, 0), 
                          (col * self.frame_width, row * self.frame_height, 
                           self.frame_width, self.frame_height))
                scaled_frame = pygame.transform.scale(frame, 
                                                    (self.frame_width * scale, 
                                                     self.frame_height * scale))
                direction_frames.append(scaled_frame)
            self.frames[direction] = direction_frames
        
        # Calculate scaled dimensions
        self.scaled_width = self.frame_width * scale
        self.scaled_height = self.frame_height * scale
    
    def _create_placeholder(self):
        """Create a placeholder sprite sheet with four directions"""
        placeholder = pygame.Surface((self.cols * 64, self.rows * 64), pygame.SRCALPHA)
        
        # Draw a simple character in four directions
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * 64 + 32
                y = row * 64 + 32
                
                # Body
                pygame.draw.circle(placeholder, (150, 150, 150), (x, y), 20)
                
                # Direction indicator
                if row == 0:  # DOWN
                    pygame.draw.rect(placeholder, (100, 200, 100), (x-15, y+10, 30, 15))
                elif row == 1:  # LEFT
                    pygame.draw.rect(placeholder, (200, 200, 100), (x-25, y-5, 15, 30))
                elif row == 2:  # RIGHT
                    pygame.draw.rect(placeholder, (100, 150, 200), (x+10, y-5, 15, 30))
                elif row == 3:  # UP
                    pygame.draw.rect(placeholder, (200, 100, 100), (x-15, y-25, 30, 15))
                
                # Frame number
                text = font_small.render(str(col+1), True, (200, 200, 200))
                placeholder.blit(text, (col * 64 + 5, row * 64 + 5))
        
        return placeholder

class Animation:
    def __init__(self, sprite_sheet, direction="DOWN", fps=10):
        self.sprite_sheet = sprite_sheet
        self.direction = direction
        self.fps = fps
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 1000 // fps
        self.playing = True
        
    def update(self):
        if self.playing:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update >= self.animation_cooldown:
                self.current_frame = (self.current_frame + 1) % len(self.sprite_sheet.frames[self.direction])
                self.last_update = current_time
                
    def draw(self, x, y):
        screen.blit(self.sprite_sheet.frames[self.direction][self.current_frame], (x, y))
        
    def reset(self):
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        
    def set_direction(self, direction):
        if direction != self.direction:
            self.direction = direction
            self.reset()

# Create sprite sheets (assuming 4 rows for directions, 4-6 columns for frames)
idle_sheet = SpriteSheet("Sword_Idle_with_shadow.png", rows=4, cols=4, scale=3)
walk_sheet = SpriteSheet("Sword_Walk_with_shadow.png", rows=4, cols=6, scale=3)

# Create animations
idle_animation = Animation(idle_sheet, direction="DOWN", fps=8)
walk_animation = Animation(walk_sheet, direction="DOWN", fps=12)

# Set active animation
active_animation = idle_animation
active_sheet = idle_sheet

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                active_animation = idle_animation
                active_sheet = idle_sheet
                active_animation.reset()
            elif event.key == pygame.K_2:
                active_animation = walk_animation
                active_sheet = walk_sheet
                active_animation.reset()
            elif event.key == pygame.K_SPACE:
                active_animation.playing = not active_animation.playing
            elif event.key == pygame.K_r:
                active_animation.reset()
            elif event.key == pygame.K_ESCAPE:
                running = False
            # Direction controls
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                active_animation.set_direction("DOWN")
            elif event.key in (pygame.K_UP, pygame.K_w):
                active_animation.set_direction("UP")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                active_animation.set_direction("LEFT")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                active_animation.set_direction("RIGHT")
    
    # Update animation
    active_animation.update()
    
    # Draw background
    screen.fill(BACKGROUND)
    
    # Draw title
    title_text = font_large.render("Four-Direction Sprite Animation Visualizer", True, TEXT_COLOR)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))
    
    # Draw animation panel
    panel_rect = pygame.Rect(50, 80, WIDTH - 100, HEIGHT - 200)
    pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=12)
    pygame.draw.rect(screen, HIGHLIGHT, panel_rect, 3, border_radius=12)
    
    # Draw sprite
    sprite_x = WIDTH // 2 - active_sheet.scaled_width // 2
    sprite_y = HEIGHT // 2 - active_sheet.scaled_height // 2
    active_animation.draw(sprite_x, sprite_y)
    
    # Draw frame info
    frame_count = len(active_sheet.frames[active_animation.direction])
    frame_text = font_medium.render(f"Frame: {active_animation.current_frame + 1}/{frame_count}", 
                                    True, TEXT_COLOR)
    screen.blit(frame_text, (WIDTH // 2 - frame_text.get_width() // 2, HEIGHT - 160))
    
    # Draw direction info with color coding
    direction_text = font_medium.render(f"Direction: {active_animation.direction}", 
                                       True, DIRECTION_COLORS[active_animation.direction])
    screen.blit(direction_text, (WIDTH // 2 - direction_text.get_width() // 2, HEIGHT - 130))
    
    # Draw controls panel
    controls_y = HEIGHT - 100
    controls_rect = pygame.Rect(WIDTH // 2 - 300, controls_y, 600, 80)
    pygame.draw.rect(screen, SHADOW, controls_rect, border_radius=10)
    pygame.draw.rect(screen, (60, 60, 70), controls_rect, 2, border_radius=10)
    
    # Draw controls text
    controls_text1 = font_small.render("Animation: 1-Idle  2-Walk  Space-Play/Pause  R-Reset", True, TEXT_COLOR)
    controls_text2 = font_small.render("Direction: Arrow Keys or WASD  Esc-Exit", True, TEXT_COLOR)
    
    screen.blit(controls_text1, (WIDTH // 2 - controls_text1.get_width() // 2, controls_y + 15))
    screen.blit(controls_text2, (WIDTH // 2 - controls_text2.get_width() // 2, controls_y + 45))
    
    # Draw animation status
    status = "Playing" if active_animation.playing else "Paused"
    status_text = font_medium.render(f"Status: {status}", True, TEXT_COLOR)
    screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, 100))
    
    # Draw animation name
    anim_name = "Idle Animation" if active_animation == idle_animation else "Walk Animation"
    name_text = font_medium.render(anim_name, True, HIGHLIGHT)
    screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, 130))
    
    # Draw direction key hints
    key_size = 40
    key_spacing = 60
    center_x = WIDTH // 2
    
    # UP
    up_key_rect = pygame.Rect(center_x - key_size//2, sprite_y + active_sheet.scaled_height + 30, key_size, key_size)
    up_color = DIRECTION_COLORS["UP"] if active_animation.direction == "UP" else (70, 70, 80)
    pygame.draw.rect(screen, up_color, up_key_rect, border_radius=5)
    pygame.draw.rect(screen, HIGHLIGHT if active_animation.direction == "UP" else (100, 100, 110), 
                    up_key_rect, 2, border_radius=5)
    up_text = font_small.render("↑", True, TEXT_COLOR)
    screen.blit(up_text, (up_key_rect.centerx - up_text.get_width()//2, 
                         up_key_rect.centery - up_text.get_height()//2))
    
    # LEFT/RIGHT/DOWN
    left_key_rect = pygame.Rect(center_x - key_spacing - key_size//2, up_key_rect.y + key_spacing, key_size, key_size)
    down_key_rect = pygame.Rect(center_x - key_size//2, up_key_rect.y + key_spacing, key_size, key_size)
    right_key_rect = pygame.Rect(center_x + key_spacing - key_size//2, up_key_rect.y + key_spacing, key_size, key_size)
    
    for rect, direction, symbol in [(left_key_rect, "LEFT", "←"), 
                                   (down_key_rect, "DOWN", "↓"), 
                                   (right_key_rect, "RIGHT", "→")]:
        color = DIRECTION_COLORS[direction] if active_animation.direction == direction else (70, 70, 80)
        pygame.draw.rect(screen, color, rect, border_radius=5)
        pygame.draw.rect(screen, HIGHLIGHT if active_animation.direction == direction else (100, 100, 110), 
                        rect, 2, border_radius=5)
        dir_text = font_small.render(symbol, True, TEXT_COLOR)
        screen.blit(dir_text, (rect.centerx - dir_text.get_width()//2, 
                              rect.centery - dir_text.get_height()//2))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()


# Sword_Death_with_shadow.png
# Sword_Hurt_with_shadow.png
# Sword_Idle_with_shadow.png
# Sword_Run_Attack_with_shadow.png
# Sword_Run_with_shadow.png
# Sword_Walk_Attack_with_shadow.png
# Sword_Walk_with_shadow.png