import pygame
import json
from game.config import Config

class TileMap:
    def __init__(self):
        self.tile_size = Config.TILE_SIZE
        self.tiles = {}
        self.load_tiles()
        
    def load_tiles(self):
        # Load your tileset images here
        # This would map tile IDs to actual surfaces
        self.tile_images = {
            0: self.create_placeholder_tile((100, 200, 100)),  # Grass
            1: self.create_placeholder_tile((150, 150, 150)),  # Path
            2: self.create_placeholder_tile((200, 200, 100)),  # Field
        }
        
        # Create a sample map
        self.width = 50
        self.height = 50
        self.data = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Add some paths and fields
        for i in range(10, 40):
            self.data[25][i] = 1  # Horizontal path
            self.data[i][25] = 1  # Vertical path
            
        for y in range(5, 15):
            for x in range(5, 15):
                self.data[y][x] = 2  # Field area
    
    def create_placeholder_tile(self, color):
        surface = pygame.Surface((self.tile_size, self.tile_size))
        surface.fill(color)
        pygame.draw.rect(surface, (50, 50, 50), (0, 0, self.tile_size, self.tile_size), 1)
        return surface
    
    def draw(self, surface, camera_offset):
        start_x = max(0, int(camera_offset.x // self.tile_size))
        end_x = min(self.width, int((camera_offset.x + Config.SCREEN_WIDTH) // self.tile_size) + 1)
        start_y = max(0, int(camera_offset.y // self.tile_size))
        end_y = min(self.height, int((camera_offset.y + Config.SCREEN_HEIGHT) // self.tile_size) + 1)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.data[y][x]
                if tile_type in self.tile_images:
                    pos = (x * self.tile_size - camera_offset.x, 
                          y * self.tile_size - camera_offset.y)
                    surface.blit(self.tile_images[tile_type], pos)

class World:
    def __init__(self):
        self.tilemap = TileMap()
        self.objects = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        
    def update(self, dt):
        self.objects.update(dt)
        self.npcs.update(dt)
        
    def draw(self, surface, camera_offset):
        self.tilemap.draw(surface, camera_offset)
        self.objects.draw(surface)
        self.npcs.draw(surface)