import pygame
from game.config import Config

class Camera:
    def __init__(self, target, world_width, world_height):
        self.target = target
        self.offset = pygame.Vector2(0, 0)
        self.world_width = world_width
        self.world_height = world_height
        self.zoom_level = 1.0  # Default zoom (normal size)
        self.min_zoom = 0.5    # Minimum zoom (50% of normal)
        self.max_zoom = 2.0    # Maximum zoom (200% of normal)
        
    def update(self):
        # Center camera on target
        target_x = self.target.rect.centerx - Config.SCREEN_WIDTH // 2
        target_y = self.target.rect.centery - Config.SCREEN_HEIGHT // 2
        
        # Smooth camera movement
        smooth_factor = 0.2
        self.offset.x += (target_x - self.offset.x) * smooth_factor
        self.offset.y += (target_y - self.offset.y) * smooth_factor
        
        # Clamp to world boundaries
        self.offset.x = max(0, min(self.offset.x, self.world_width - Config.SCREEN_WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.world_height - Config.SCREEN_HEIGHT))
    
    def zoom_in(self):
        """Zoom in by 0.1 increments"""
        self.zoom_level = min(self.max_zoom, self.zoom_level + 0.1)
        
    
    def zoom_out(self):
        """Zoom out by 0.1 increments"""
        self.zoom_level = max(self.min_zoom, self.zoom_level - 0.1)
        
    
    def reset_zoom(self):
        """Reset to normal zoom"""
        self.zoom_level = 1.0
        
    
    def get_zoomed_rect(self, rect):
        """Apply zoom transformation to a rectangle"""
        # Calculate center position
        center_x = rect.centerx - self.offset.x
        center_y = rect.centery - self.offset.y
        
        # Apply zoom
        zoomed_width = rect.width * self.zoom_level
        zoomed_height = rect.height * self.zoom_level
        zoomed_x = (center_x * self.zoom_level) + (Config.SCREEN_WIDTH - zoomed_width) // 2
        zoomed_y = (center_y * self.zoom_level) + (Config.SCREEN_HEIGHT - zoomed_height) // 2
        
        return pygame.Rect(zoomed_x, zoomed_y, zoomed_width, zoomed_height)
    
    def get_zoomed_position(self, position):
        """Apply zoom transformation to a position"""
        screen_x = position[0] - self.offset.x
        screen_y = position[1] - self.offset.y
        
        # Apply zoom and center on screen
        zoomed_x = (screen_x * self.zoom_level) + (Config.SCREEN_WIDTH * (1 - self.zoom_level)) // 2
        zoomed_y = (screen_y * self.zoom_level) + (Config.SCREEN_HEIGHT * (1 - self.zoom_level)) // 2
        
        return (zoomed_x, zoomed_y)