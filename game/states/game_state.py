import pygame
from game.config import Config
from game.player import Player
from game.tilemap import TileMap
from game.camera import Camera

class GameState:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 24)
        
        # Create world
        self.tilemap = TileMap()
        world_width = self.tilemap.width * Config.TILE_SIZE
        world_height = self.tilemap.height * Config.TILE_SIZE
        
        # Find a safe starting position for the player (on a path)
        start_x, start_y = self.find_safe_start_position()
        
        # Create player at safe position
        self.player = Player(start_x, start_y, self)
        
        # Create camera
        self.camera = Camera(self.player, world_width, world_height)
        
        # Debug settings
        self.show_collision_boxes = False  # Set to False to hide collision boxes
        self.show_player_collision = True
        
        print("Game world created!")
        print(f"World size: {world_width}x{world_height}")
        print(f"Player starting at: {start_x}, {start_y}")
    
    def find_safe_start_position(self):
        """Find a position on a path (not colliding with objects)"""
        # Try multiple positions to find a safe spot
        safe_positions = []
        
        # First, look for path tiles in the ground layer
        for y, row in enumerate(self.tilemap.layers[0]):
            for x, char in enumerate(row):
                if char == 'p':  # Path tile
                    # Check if this position is collision-free
                    test_x = x * Config.TILE_SIZE + Config.TILE_SIZE // 2
                    test_y = y * Config.TILE_SIZE + Config.TILE_SIZE // 2
                    
                    # Create a temporary player rect to check collisions
                    temp_rect = pygame.Rect(0, 0, 40, 50)  # Match player collision size
                    temp_rect.center = (test_x, test_y)
                    
                    if not self.tilemap.check_collision(temp_rect):
                        safe_positions.append((test_x, test_y))
        
        # If we found safe path positions, return the first one
        if safe_positions:
            return safe_positions[0]
        
        # If no path found, look for any grass tile without collision
        for y, row in enumerate(self.tilemap.layers[0]):
            for x, char in enumerate(row):
                if char == 'g':  # Grass tile
                    test_x = x * Config.TILE_SIZE + Config.TILE_SIZE // 2
                    test_y = y * Config.TILE_SIZE + Config.TILE_SIZE // 2
                    
                    temp_rect = pygame.Rect(0, 0, 40, 50)
                    temp_rect.center = (test_x, test_y)
                    
                    if not self.tilemap.check_collision(temp_rect):
                        safe_positions.append((test_x, test_y))
        
        # If we found safe grass positions, return the first one
        if safe_positions:
            return safe_positions[0]
        
        # If still no safe position found, try center of map
        center_x = self.tilemap.width * Config.TILE_SIZE // 2
        center_y = self.tilemap.height * Config.TILE_SIZE // 2
        
        temp_rect = pygame.Rect(0, 0, 40, 50)
        temp_rect.center = (center_x, center_y)
        
        if not self.tilemap.check_collision(temp_rect):
            return center_x, center_y
        
        # Last resort: try multiple positions around the center
        for offset_x in range(0, self.tilemap.width // 2, 2):
            for offset_y in range(0, self.tilemap.height // 2, 2):
                test_x = center_x + offset_x * Config.TILE_SIZE
                test_y = center_y + offset_y * Config.TILE_SIZE
                
                # Make sure position is within map bounds
                test_x = max(Config.TILE_SIZE, min(test_x, (self.tilemap.width - 1) * Config.TILE_SIZE))
                test_y = max(Config.TILE_SIZE, min(test_y, (self.tilemap.height - 1) * Config.TILE_SIZE))
                
                temp_rect.center = (test_x, test_y)
                
                if not self.tilemap.check_collision(temp_rect):
                    return test_x, test_y
        
        # Ultimate fallback: top-left corner (should be safe)
        return Config.TILE_SIZE, Config.TILE_SIZE
    
    def draw_collision_debug(self, surface, offset):
        """Draw collision boxes for debugging"""
        if not self.show_collision_boxes:
            return
            
        # Draw tilemap collision boxes
        for collision_rect in self.tilemap.collision_rects:
            # Adjust for camera offset
            debug_rect = pygame.Rect(
                collision_rect.x - offset.x,
                collision_rect.y - offset.y,
                collision_rect.width,
                collision_rect.height
            )
            # Draw semi-transparent red box for collisions
            s = pygame.Surface((debug_rect.width, debug_rect.height), pygame.SRCALPHA)
            s.fill((255, 0, 0, 64))  # Red with transparency
            surface.blit(s, debug_rect)
            # Draw outline
            pygame.draw.rect(surface, (255, 0, 0), debug_rect, 2)
        
        # Draw player collision box
        if self.show_player_collision:
            player_collision_rect = pygame.Rect(
                self.player.collision_rect.x - offset.x,
                self.player.collision_rect.y - offset.y,
                self.player.collision_rect.width,
                self.player.collision_rect.height
            )
            # Draw semi-transparent blue box for player collision
            s = pygame.Surface((player_collision_rect.width, player_collision_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 255, 64))  # Blue with transparency
            surface.blit(s, player_collision_rect)
            # Draw outline
            pygame.draw.rect(surface, (0, 0, 255), player_collision_rect, 2)
            
            # Draw player center point
            center_x = self.player.position.x - offset.x
            center_y = self.player.position.y - offset.y
            pygame.draw.circle(surface, (0, 255, 0), (int(center_x), int(center_y)), 3)
    
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to menu
                self.game.current_state = 'menu'
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                # Zoom in
                self.camera.zoom_in()
            elif event.key == pygame.K_MINUS:
                # Zoom out
                self.camera.zoom_out()
            elif event.key == pygame.K_0:
                # Reset zoom
                self.camera.reset_zoom()
            elif event.key == pygame.K_F1:
                # Toggle collision debug
                self.show_collision_boxes = not self.show_collision_boxes
                print(f"Collision debug: {self.show_collision_boxes}")
    
    def update(self, dt):
        self.player.update(dt)
        self.camera.update()
    
    def render(self, surface):
        # Clear screen
        surface.fill((0, 0, 0))
        
        # If zoom is normal (1.0), use standard rendering for better performance
        if self.camera.zoom_level == 1.0:
            self.tilemap.draw(surface, self.camera.offset)
            self.player.draw(surface, self.camera.offset)
            # Draw collision debug on top
            self.draw_collision_debug(surface, self.camera.offset)
        else:
            # Create a surface to render the game world at 1:1 scale
            world_surface = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
            world_surface.fill((0, 0, 0))
            
            # Draw world and player at normal scale
            self.tilemap.draw(world_surface, self.camera.offset)
            self.player.draw(world_surface, self.camera.offset)
            # Draw collision debug on the world surface
            self.draw_collision_debug(world_surface, self.camera.offset)
            
            # Scale the world surface to apply zoom
            scaled_width = int(Config.SCREEN_WIDTH * self.camera.zoom_level)
            scaled_height = int(Config.SCREEN_HEIGHT * self.camera.zoom_level)
            scaled_surface = pygame.transform.scale(world_surface, (scaled_width, scaled_height))
            
            # Calculate position to center the scaled surface
            x_offset = (Config.SCREEN_WIDTH - scaled_width) // 2
            y_offset = (Config.SCREEN_HEIGHT - scaled_height) // 2
            
            # Draw the scaled surface centered on screen
            surface.blit(scaled_surface, (x_offset, y_offset))
        
        # Draw UI (always on top, not affected by zoom)
        self.draw_ui(surface)
    
    def draw_ui(self, surface):
        # Player info
        weapon = "Sword" if self.player.armed else "Unarmed"
        state_text = self.font.render(f"State: {self.player.state} | Direction: {self.player.direction} | Weapon: {weapon}", 
                                    True, (255, 255, 255))
        surface.blit(state_text, (10, 10))
        
        # Position info
        pos_text = self.font.render(f"Position: {int(self.player.position.x)}, {int(self.player.position.y)}", 
                                  True, (255, 255, 255))
        surface.blit(pos_text, (10, 40))
        
        # Zoom info
        zoom_text = self.font.render(f"Zoom: {self.camera.zoom_level:.1f}x", 
                                   True, (255, 255, 255))
        surface.blit(zoom_text, (10, 70))
        
        # Collision debug info
        collision_status = "ON" if self.show_collision_boxes else "OFF"
        collision_text = self.font.render(f"Collision Debug: {collision_status} (F1 to toggle)", 
                                        True, (255, 255, 255))
        surface.blit(collision_text, (10, 100))
        
        # Controls help
        controls = [
            "WASD/Arrows: Move",
            "Shift: Run", 
            "Space: Attack",
            "Q: Toggle Weapon",
            "+/-: Zoom In/Out",
            "0: Reset Zoom",
            "F1: Toggle Collision Boxes",
            "ESC: Menu"
        ]
        
        for i, control in enumerate(controls):
            text = self.font.render(control, True, (200, 200, 200))
            surface.blit(text, (Config.SCREEN_WIDTH - text.get_width() - 10, 10 + i * 25))