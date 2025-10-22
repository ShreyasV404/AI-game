import pygame
from game.config import Config
from game.asset_loader import asset_loader

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, game_state):
        super().__init__()
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = Config.PLAYER_SPEED
        self.game_state = game_state  # Reference to game state for collision checking
        
        # Animation states
        self.state = "idle"
        self.direction = "front"  # Default direction
        self.armed = True  # Start with sword
        
        # Make sure assets are loaded
        asset_loader.load_all_assets()
        
        # Set initial animation
        self.current_animation = asset_loader.get_character_animation(
            "sword" if self.armed else "unarmed", 
            self.state, 
            self.direction
        )
        self.animation_index = 0
        self.animation_time = 0
        
        if self.current_animation and len(self.current_animation) > 0:
            self.image = self.current_animation[self.animation_index]
            # Use original 64x64 size - NO SCALING
        else:
            # Fallback if animation not found
            self.image = pygame.Surface((64, 64), pygame.SRCALPHA)
            self.image.fill((255, 0, 255))  # Magenta for missing texture
            
        self.rect = self.image.get_rect(center=self.position)
        
        # Create collision rectangle for 64x64 sprite
        self.collision_rect = pygame.Rect(0, 0, 20, 20)  # Slightly smaller than sprite
        self.collision_rect.center = self.position
        
        # Movement flags
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        
        # Attack cooldown
        self.attack_cooldown = 0
        
        # Debug
        self.last_direction = ""
        self.key_debug = ""
        
    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        
        # Update movement flags
        self.moving_up = keys[pygame.K_w] or keys[pygame.K_UP]
        self.moving_down = keys[pygame.K_s] or keys[pygame.K_DOWN]
        self.moving_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        self.moving_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        
        # Calculate velocity
        self.velocity = pygame.Vector2(0, 0)
        
        # Store old direction for debug
        old_direction = self.direction
        
        # Clear key debug
        self.key_debug = ""
        
       # Reset velocity first
        self.velocity.x = 0
        self.velocity.y = 0

        # Set direction based on input - prioritize the last pressed direction
        if self.moving_up:
            self.velocity.y = -1
            self.direction = "back"
            self.key_debug += "UP->back "
        if self.moving_down:
            self.velocity.y = 1
            self.direction = "front"
            self.key_debug += "DOWN->front "
        if self.moving_left:
            self.velocity.x = -1
            self.direction = "side_left"
            self.key_debug += "LEFT->side_left "
        if self.moving_right:
            self.velocity.x = 1
            self.direction = "side_right"
            self.key_debug += "RIGHT->side_right "

        # For diagonal movement, set direction based on dominant axis
        if self.velocity.x != 0 and self.velocity.y != 0:
            # For diagonal movement, prioritize horizontal direction for animation
            if abs(self.velocity.x) > abs(self.velocity.y):
                if self.velocity.x > 0:
                    self.direction = "side_right"
                else:
                    self.direction = "side_left"
            else:
                if self.velocity.y > 0:
                    self.direction = "front"
                else:
                    self.direction = "back"
        
        # Normalize diagonal movement
        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize()
            
        
            
        # State changes
        if keys[pygame.K_SPACE] and self.attack_cooldown <= 0:
            self.state = "attack"
            self.attack_cooldown = 0.5  # 0.5 second cooldown
            self.animation_index = 0  # Reset animation for attack
        elif self.attack_cooldown > 0:
            # Continue attack animation
            pass
        elif self.velocity.length() > 0:
            if keys[pygame.K_LSHIFT]:
                self.state = "run"
                self.speed = Config.PLAYER_SPEED * 1.8
            else:
                self.state = "walk"
                self.speed = Config.PLAYER_SPEED
        else:
            self.state = "idle"
        
        # Toggle weapon
        if keys[pygame.K_q]:
            self.armed = not self.armed
            # Reset animation when weapon changes
            self.animation_index = 0
    
    def update(self, dt):
        self.handle_input(dt)
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                # Attack finished, return to previous state
                if self.velocity.length() > 0:
                    self.state = "walk"
                else:
                    self.state = "idle"
        
        # Store old position for collision checking
        old_position = self.position.copy()
        
        # Update position
        self.position += self.velocity * self.speed * dt
        
        # Keep player within world bounds - adjusted for 64x64 sprite
        world_width = self.game_state.tilemap.width * Config.TILE_SIZE
        world_height = self.game_state.tilemap.height * Config.TILE_SIZE
        self.position.x = max(32, min(self.position.x, world_width - 32))
        self.position.y = max(32, min(self.position.y, world_height - 32))
        
        # Update rects
        self.rect.center = self.position
        self.collision_rect.center = self.position
        
        # Check collision with houses
        if self.game_state.tilemap.check_collision(self.collision_rect):
            # Collision detected, revert to old position
            self.position = old_position
            self.rect.center = self.position
            self.collision_rect.center = self.position
        
        # Update animation
        weapon = "sword" if self.armed else "unarmed"
        new_animation = asset_loader.get_character_animation(weapon, self.state, self.direction)
        
        if new_animation and new_animation != self.current_animation:
            self.current_animation = new_animation
            self.animation_index = 0  # Reset animation when it changes
        
        if self.current_animation and len(self.current_animation) > 0:
            self.animation_time += dt
            frame_duration = Config.PLAYER_ANIMATION_SPEED
            
            # Adjust animation speed based on state
            if self.state == "run":
                frame_duration *= 0.6
            elif self.state == "attack":
                frame_duration *= 0.8
                
            if self.animation_time >= frame_duration:
                self.animation_time = 0
                self.animation_index = (self.animation_index + 1) % len(self.current_animation)
                self.image = self.current_animation[self.animation_index]
                # NO SCALING - use original 64x64 size
    
    def draw(self, surface, offset):
        pos = self.rect.topleft - offset
        surface.blit(self.image, pos)
        
        # Draw debug text
        # font = pygame.font.Font(None, 24)
        # debug_text = f"Dir: {self.direction} State: {self.state}"
        # text_surface = font.render(debug_text, True, (255, 255, 255))
        # surface.blit(text_surface, (self.rect.x - offset.x, self.rect.y - offset.y - 20))