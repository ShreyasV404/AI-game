import pygame
from game.config import Config

class Camera:
    def __init__(self, target, world_width, world_height):
        self.target = target
        self.offset = pygame.Vector2(0, 0)
        self.world_width = world_width
        self.world_height = world_height
        
    def update(self):
        # Center camera on target
        target_x = self.target.rect.centerx - Config.SCREEN_WIDTH // 2
        target_y = self.target.rect.centery - Config.SCREEN_HEIGHT // 2
        
        # Smooth camera movement (optional - can be adjusted)
        smooth_factor = 0.2  # Instead of 0.1
        self.offset.x += (target_x - self.offset.x) * smooth_factor
        self.offset.y += (target_y - self.offset.y) * smooth_factor
        
        # Clamp to world boundaries
        self.offset.x = max(0, min(self.offset.x, self.world_width - Config.SCREEN_WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.world_height - Config.SCREEN_HEIGHT))
        
        