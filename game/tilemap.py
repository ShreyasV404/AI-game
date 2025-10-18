import pygame
import random
from game.config import Config
from game.asset_loader import asset_loader

class TileMap:
    def __init__(self):
        self.tile_size = Config.TILE_SIZE
        self.tiles = {}
        self.tile_images = {}
        self.objects = []  # List for houses and other objects
        self.collision_rects = []  # List for collision rectangles
        self.load_tileset()
        self.create_map()
        self.place_houses()
        
    def load_tileset(self):
        """Load tileset using asset loader"""
        asset_loader.load_all_assets()
        
        # Get the background and grass tile
        self.background = asset_loader.get_background()
        self.grass_tile = asset_loader.get_grass_tile()
        
        print("Tileset loaded")
        if self.background:
            print(f"Background size: {self.background.get_size()}")
        if self.grass_tile:
            print(f"Grass tile size: {self.grass_tile.get_size()}")
    
    def create_map(self):
        """Create a village map using the actual tileset as background and grass tiles on top"""
        self.width = 50
        self.height = 50
        self.data = []
        
        # Initialize with all grass
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(1)  # 1 means grass, 0 means path (no grass)
            self.data.append(row)
        
        # Create main roads (set to 0 for no grass - showing the background)
        road_width = 3
        for i in range(10, 40):
            for w in range(road_width):
                # Horizontal road
                if 0 <= 20 + w < self.height and 0 <= i < self.width:
                    self.data[20 + w][i] = 0  # No grass - path
                # Vertical road  
                if 0 <= i < self.height and 0 <= 20 + w < self.width:
                    self.data[i][20 + w] = 0  # No grass - path
        
        # Create village center (no grass - path area)
        center_size = 8
        center_x, center_y = 20, 20
        for y in range(center_y - center_size//2, center_y + center_size//2):
            for x in range(center_x - center_size//2, center_x + center_size//2):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.data[y][x] = 0  # No grass - path
        
        # Add some grass patches with variations
        grass_patches = [(5, 5, 8, 8), (35, 5, 8, 8), (5, 35, 8, 8), (35, 35, 8, 8)]
        for fx, fy, fw, fh in grass_patches:
            for y in range(fy, fy + fh):
                for x in range(fx, fx + fw):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.data[y][x] = 1  # Grass
    
    def place_houses(self):
        """Place houses in the village with collision rectangles"""
        # Place houses away from the center where player starts
        house_locations = [
            (12, 12, 0),  # (x, y, house_variant) - moved away from center
            (28, 12, 1),
            (12, 28, 2), 
            (28, 28, 3)
        ]
        
        for x, y, variant in house_locations:
            house_image = asset_loader.get_house(variant)
            if house_image:
                # Convert tile position to pixel position
                pixel_x = x * self.tile_size
                pixel_y = y * self.tile_size
                
                # Adjust position based on house size (centered)
                house_width, house_height = house_image.get_size()
                pixel_x -= (house_width - self.tile_size) // 2
                pixel_y -= (house_height - self.tile_size)
                
                # Add house to objects list
                self.objects.append({
                    'image': house_image,
                    'position': (pixel_x, pixel_y),
                    'type': 'house'
                })
                
                # Create collision rectangle for the house
                # Make the collision area slightly smaller than the visual house for better gameplay
                collision_margin = 10  # Pixels to shrink the collision box
                collision_rect = pygame.Rect(
                    pixel_x + collision_margin,
                    pixel_y + collision_margin,
                    house_width - collision_margin * 2,
                    house_height - collision_margin
                )
                self.collision_rects.append(collision_rect)
        
        print(f"Placed {len(self.objects)} houses with collision in the village")
    
    def check_collision(self, rect):
        """Check if a rectangle collides with any object"""
        for collision_rect in self.collision_rects:
            if rect.colliderect(collision_rect):
                return True
        return False
    
    def draw(self, surface, camera_offset):
        """Draw the visible portion of the tilemap and objects"""
        # Draw the background (tiled)
        if self.background:
            bg_width, bg_height = self.background.get_size()
            for y in range(0, self.height * self.tile_size, bg_height):
                for x in range(0, self.width * self.tile_size, bg_width):
                    surface.blit(self.background, (x - camera_offset.x, y - camera_offset.y))
        
        # Draw grass tiles on top of background where needed
        start_x = max(0, int(camera_offset.x // self.tile_size))
        end_x = min(self.width, int((camera_offset.x + Config.SCREEN_WIDTH) // self.tile_size) + 2)
        start_y = max(0, int(camera_offset.y // self.tile_size))
        end_y = min(self.height, int((camera_offset.y + Config.SCREEN_HEIGHT) // self.tile_size) + 2)
        
        if self.grass_tile:
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    if self.data[y][x] == 1:  # Draw grass tile
                        pos = (x * self.tile_size - camera_offset.x, 
                              y * self.tile_size - camera_offset.y)
                        surface.blit(self.grass_tile, pos)
        
        # Draw objects (houses)
        for obj in self.objects:
            obj_x, obj_y = obj['position']
            # Check if object is visible
            if (obj_x - camera_offset.x < Config.SCREEN_WIDTH and 
                obj_x + obj['image'].get_width() - camera_offset.x > 0 and
                obj_y - camera_offset.y < Config.SCREEN_HEIGHT and
                obj_y + obj['image'].get_height() - camera_offset.y > 0):
                
                surface.blit(obj['image'], (obj_x - camera_offset.x, obj_y - camera_offset.y))
        
        # Debug: Draw collision rectangles (uncomment to see collision areas)
        # for collision_rect in self.collision_rects:
        #     pygame.draw.rect(surface, (255, 0, 0), 
        #                    (collision_rect.x - camera_offset.x, collision_rect.y - camera_offset.y,
        #                     collision_rect.width, collision_rect.height), 1)