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
        
        # Find a safe starting position for the player (not inside a house)
        start_x, start_y = self.find_safe_start_position()
        
        # Create player at safe position
        self.player = Player(start_x, start_y, self)
        
        # Create camera
        self.camera = Camera(self.player, world_width, world_height)
        
        print("Game world created!")
        print(f"World size: {world_width}x{world_height}")
        print(f"Player starting at: {start_x}, {start_y}")
    
    def find_safe_start_position(self):
        """Find a position that's not inside any house"""
        # Try the center of the map first
        center_x = self.tilemap.width * Config.TILE_SIZE // 2
        center_y = self.tilemap.height * Config.TILE_SIZE // 2
        
        # Create a temporary player rect to check collisions
        temp_rect = pygame.Rect(0, 0, 20, 30)
        temp_rect.center = (center_x, center_y)
        
        # If center is blocked, try positions around it
        if not self.tilemap.check_collision(temp_rect):
            return center_x, center_y
        
        # Try positions in a spiral pattern from center
        for radius in range(1, 10):
            for angle in range(0, 360, 45):
                # Calculate position in a circle around center
                test_x = center_x + int(radius * Config.TILE_SIZE * pygame.math.Vector2(1, 0).rotate(angle).x)
                test_y = center_y + int(radius * Config.TILE_SIZE * pygame.math.Vector2(1, 0).rotate(angle).y)
                
                temp_rect.center = (test_x, test_y)
                if not self.tilemap.check_collision(temp_rect):
                    return test_x, test_y
        
        # If all else fails, return a hardcoded safe position
        return Config.TILE_SIZE * 10, Config.TILE_SIZE * 10
    
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
        else:
            # Create a surface to render the game world at 1:1 scale
            world_surface = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
            world_surface.fill((0, 0, 0))
            
            # Draw world and player at normal scale
            self.tilemap.draw(world_surface, self.camera.offset)
            self.player.draw(world_surface, self.camera.offset)
            
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
        
        # Controls help
        controls = [
            "WASD/Arrows: Move",
            "Shift: Run", 
            "Space: Attack",
            "Q: Toggle Weapon",
            "+/-: Zoom In/Out",
            "0: Reset Zoom",
            "ESC: Menu"
        ]
        
        for i, control in enumerate(controls):
            text = self.font.render(control, True, (200, 200, 200))
            surface.blit(text, (Config.SCREEN_WIDTH - text.get_width() - 10, 10 + i * 25))