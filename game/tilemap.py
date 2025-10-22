import pygame
import json
import os
from game.config import Config
from game.asset_loader import asset_loader

class EditorTileMap:
    def __init__(self, map_file="custom_map.json"):
        self.tile_size = Config.TILE_SIZE
        self.objects = []
        self.collision_rects = []
        
        self.tiles = {}
        self.objects_assets = {}
        
        self.load_assets()
        self.load_custom_map(map_file)

    def load_assets(self):
        """Load all necessary assets using the asset_loader."""
        asset_loader.load_all_assets()

        # Load tiles
        self.tiles['grass'] = asset_loader.get_tile("grass")
        self.tiles['path'] = asset_loader.get_tile("path")
        
        # Load objects
        self.objects_assets['tree'] = asset_loader.get_object("tree")
        self.objects_assets['house_2'] = asset_loader.get_object("house_2")
        self.objects_assets['house_4'] = asset_loader.get_object("house_4")
        
        print("All map assets loaded into EditorTileMap.")

    def load_custom_map(self, map_file):
        """Load a map created with the map editor"""
        try:
            # Check if file exists
            if not os.path.exists(map_file):
                print(f"Map file '{map_file}' not found, using default village layout")
                self.load_default_map()
                return
                
            with open(map_file, 'r') as f:
                map_data = json.load(f)
            
            # Extract map data
            self.map_width = map_data['width']
            self.map_height = map_data['height']
            self.layers = map_data['layers']
            
            # Convert string keys back to integers if needed
            if isinstance(next(iter(self.layers.keys())), str):
                self.layers = {int(k): v for k, v in self.layers.items()}
            
            # Set the width and height attributes for compatibility
            self.width = self.map_width
            self.height = self.map_height
            
            self.build_map_from_layers()
            print(f"Custom map loaded: {self.map_width}x{self.map_height}")
            
        except Exception as e:
            print(f"Error loading map file: {e}")
            print("Falling back to default village layout")
            self.load_default_map()

    def load_default_map(self):
        """Fallback to original village layout if custom map fails"""
        # Original village layout from your tilemap.py
        VILLAGE_LAYOUT = [
            "tttttttttttttttttttttttttttttttttttttttttttttttttt",
            "gggggggggggggggggggggggggggggggggggggggggggggggggt",
            "tggggggggggggggggggggggggggggggggggggggggggggggggt",
            "gggghgggtggghgggtggghgggtggghgggtggghgggtggghggggt",
            "tggg   gggg   gggg   gggg   gggg   gggg   gggggggt",
            "gggg   gggg   gggg   gggg   gggg   gggg   gggggggt",
            "tggghgggtggghgggtggghgggtggghgggtggghgggtggghggggt",
            "gggggggggggggggggggggggggggggggggggggggggggggggggt",
            "tgggpppppppppppppppppppppppppppppppppppppppppgggt",
            "ggggpgggggggggggggggggggggggggggggggggggggggpgggt",
            "tgggpggghgggtgggppppppppppppppppppgggtggghggpgggt",
            "ggggpggg   ggggpggggggggggggggggggpgggg   gggpgggt",
            "tgggpggg   ggggpggghgggtggghgggtgggpgggg   gggpgggt",
            "ggggpggghgggtggpggg   gggg   gggg   pgggtggghggggt",
            "tgggpggggggggggpggg   gggg   gggg   pggggggggggggt",
            "ggggppppppppppppppp   gggg   gggg   pppppppppppggt",
            "tgggggggggggggggggp   gggg   gggg   pggggggggggggt",
            "gggghgggtggghgggtgp   gggg   gggg   pgtggghgggtggt",
            "tggg   gggg   ggggg   gggg   gggg   ggggg   gggggt",
            "gggg   gggg   ggggg   gggg   gggg   ggggg   gggggt",
            "tggghgggtggghgggtgp   gggg   gggg   pgtggghgggtggt",
            "ggggggggggggggggggp   gggg   gggg   pggggggggggggt",
            "tgggppppppppppppppp   gggg   gggg   pppppppppppggt",
            "ggggpggggggggggpggg   gggg   gggg   pggggggggggggt",
            "tgggpgggggggtggpggg   gggg   gggg   pgggtggghggggt",
            "ggggpggg   ggggpggghgggtggghgggtgggpgggg   gggpgggt",
            "tgggpgggh  ggggpgggggggggggggggggggpgggg   gggpgggt",
            "ggggpgggggggtgggppppppppppppppppppgggtggghggpgggt",
            "tgggpppppppppppppppppppppppppppppppppppppppppgggt",
            "gggggggggggggggggggggggggggggggggggggggggggggggt",
            "tgggggggggggggggggggggggggggggggggggggggggggggggt",
            "ggggggggtgggggggtgggggggtgggggggtgggggggtggggggggt",
            "tggg   gggg   gggg   gggg   gggg   gggg   gggggggt",
            "ggggh  ggggh  ggggh  ggggh  ggggh  ggggh  gggggggt",
            "tgggggggtgggggggtgggggggtgggggggtgggggggtggggggggt",
            "gggggggggggggggggggggggggggggggggggggggggggggggggt",
            "tgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgtgt",
        ]
        
        self.map_width = len(VILLAGE_LAYOUT[0])
        self.map_height = len(VILLAGE_LAYOUT)
        
        # Set the width and height attributes for compatibility
        self.width = self.map_width
        self.height = self.map_height
        
        # Convert original layout to layer format
        self.layers = {
            0: VILLAGE_LAYOUT,  # Ground layer
            1: [' ' * self.map_width for _ in range(self.map_height)],  # Empty object layer
            2: [' ' * self.map_width for _ in range(self.map_height)]   # Empty decor layer
        }
        
        # Manually add objects based on original layout
        for y, row in enumerate(VILLAGE_LAYOUT):
            for x, char in enumerate(row):
                if char == 't':  # Tree in original layout
                    self.layers[1][y] = self.layers[1][y][:x] + 't' + self.layers[1][y][x+1:]
                elif char == 'h':  # House in original layout
                    self.layers[1][y] = self.layers[1][y][:x] + 'h' + self.layers[1][y][x+1:]
        
        self.build_map_from_layers()
        print("Loaded default village layout")

    def build_map_from_layers(self):
        """Build the map from the layered data"""
        self.tile_surfaces = []
        self.objects = []
        self.collision_rects = []

        # Create ground layer surfaces
        for y in range(self.map_height):
            row_surfaces = []
            for x in range(self.map_width):
                # Get character from ground layer (layer 0)
                if y < len(self.layers[0]) and x < len(self.layers[0][y]):
                    char = self.layers[0][y][x]
                else:
                    char = ' '  # Default to empty

                # Determine base tile
                if char == 'g':
                    base_tile = self.tiles['grass'].copy()
                elif char == 'p':
                    base_tile = self.tiles['path'].copy()
                else:
                    base_tile = self.tiles['grass'].copy()  # Default to grass

                row_surfaces.append(base_tile)
            self.tile_surfaces.append(row_surfaces)

        # Create objects from object layer (layer 1)
        for y in range(self.map_height):
            for x in range(self.map_width):
                # Skip if out of bounds
                if y >= len(self.layers[1]) or x >= len(self.layers[1][y]):
                    continue

                char = self.layers[1][y][x]
                if char == ' ':
                    continue
                
                tile_pos = (x * self.tile_size, y * self.tile_size)

                if char == 't':  # Tree
                    self._place_object('tree', x, y)
                    # Tree collision (smaller than visual tree)
                    # Use the same positioning as the visual tree
                    obj_rect = self.objects[-1]['rect']  # Get the rect we just created
                    collision_rect = pygame.Rect(
                        obj_rect.x + 10, 
                        obj_rect.y + 30, 
                        obj_rect.width - 20, 
                        obj_rect.height - 30
                    )
                    self.collision_rects.append(collision_rect)

                elif char == 'h':  # House type 1
                    self._place_object('house_2', x, y)
                    # House collision - use a slightly smaller rect than the visual
                    obj_rect = self.objects[-1]['rect']  # Get the rect we just created
                    # Make collision rect slightly smaller than visual
                    collision_rect = pygame.Rect(
                        obj_rect.x + 10,  # 10px inset from left
                        obj_rect.y + 10,  # 10px inset from top  
                        obj_rect.width - 20,  # 20px smaller width
                        obj_rect.height - 20  # 20px smaller height
                    )
                    self.collision_rects.append(collision_rect)
            
                elif char == 'H':  # House type 2
                    self._place_object('house_4', x, y)
                    # House collision - use a slightly smaller rect than the visual
                    obj_rect = self.objects[-1]['rect']  # Get the rect we just created
                    # Make collision rect slightly smaller than visual
                    collision_rect = pygame.Rect(
                        obj_rect.x + 10,  # 10px inset from left
                        obj_rect.y + 10,  # 10px inset from top  
                        obj_rect.width - 20,  # 20px smaller width
                        obj_rect.height - 20  # 20px smaller height
                    )
                    self.collision_rects.append(collision_rect)

        # COMPATIBILITY: Create map_layout attribute for original code
        self.map_layout = self.layers[0]

        print(f"Map built from layers: {self.map_width}x{self.map_height} tiles")
        print(f"Placed {len(self.objects)} objects")
        print(f"Created {len(self.collision_rects)} collision rectangles")

    def _place_object(self, obj_type, tile_x, tile_y):
        """Place an object on the map with proper positioning for large objects"""
        image = self.objects_assets.get(obj_type)
        if not image:
            print(f"Warning: Object type '{obj_type}' not found")
            return

        pixel_x = tile_x * self.tile_size
        pixel_y = tile_y * self.tile_size
        
        img_width, img_height = image.get_size()
        
        # Adjust position based on object size
        if obj_type == 'tree':
            # Trees are 64x64, center them on 32x32 tiles
            adj_x = pixel_x - (img_width - self.tile_size) // 2
            adj_y = pixel_y - (img_height - self.tile_size)
        else:
            # Houses are 96x96, center them and align to bottom
            adj_x = pixel_x - (img_width - self.tile_size) // 2
            adj_y = pixel_y - (img_height - self.tile_size)
        
        # Add to object list for drawing
        self.objects.append({
            'image': image,
            'rect': pygame.Rect(adj_x, adj_y, img_width, img_height),
            'type': obj_type,
            'base_tile': (tile_x, tile_y)
        })

    def check_collision(self, rect):
        """Check if a rectangle collides with any object or wall."""
        for collision_rect in self.collision_rects:
            if rect.colliderect(collision_rect):
                return True
        return False

    def draw(self, surface, camera_offset):
        """Draw the visible portion of the tilemap and objects with proper layering."""
        
        # Calculate visible tile range
        start_x = max(0, int(camera_offset.x // self.tile_size))
        end_x = min(self.map_width, int((camera_offset.x + Config.SCREEN_WIDTH) // self.tile_size) + 2)
        start_y = max(0, int(camera_offset.y // self.tile_size))
        end_y = min(self.map_height, int((camera_offset.y + Config.SCREEN_HEIGHT) // self.tile_size) + 2)
        
        # Layer 1: Draw the pre-rendered ground tiles
        for y in range(start_y, end_y):
            # Check if y is a valid row index
            if y < len(self.tile_surfaces):
                current_row = self.tile_surfaces[y]
                row_width = len(current_row)
                
                # Calculate the safe end_x for THIS row
                current_end_x = min(end_x, row_width)

                for x in range(start_x, current_end_x):
                    # Now this access is guaranteed to be safe
                    tile_surface = current_row[x] 
                    pos = (x * self.tile_size - camera_offset.x, 
                           y * self.tile_size - camera_offset.y)
                    surface.blit(tile_surface, pos)
        
        # Layer 2: Draw large objects (houses, trees) with depth sorting
        visible_objects = []
        for obj in self.objects:
            obj_rect = obj['rect']
            # Check if object is visible on screen
            if (obj_rect.x - camera_offset.x < Config.SCREEN_WIDTH and 
                obj_rect.x + obj_rect.width - camera_offset.x > 0 and
                obj_rect.y - camera_offset.y < Config.SCREEN_HEIGHT and
                obj_rect.y + obj_rect.height - camera_offset.y > 0):
                
                visible_objects.append(obj)
        
        # Sort by the bottom of the rect for proper layering
        sorted_objects = sorted(visible_objects, key=lambda obj: obj['rect'].bottom)
        
        for obj in sorted_objects:
            surface.blit(obj['image'], (obj['rect'].x - camera_offset.x, 
                                        obj['rect'].y - camera_offset.y))

    def find_safe_start_position(self):
        """Find a position on a path (not colliding with objects)"""
        # Try multiple positions to find a safe spot
        safe_positions = []
        
        # First, look for path tiles
        for y, row in enumerate(self.layers[0]):
            for x, char in enumerate(row):
                if char == 'p':  # Path tile
                    # Check if this position is collision-free
                    test_x = x * self.tile_size + self.tile_size // 2
                    test_y = y * self.tile_size + self.tile_size // 2
                    
                    # Create a temporary player rect to check collisions
                    temp_rect = pygame.Rect(0, 0, 20, 30)
                    temp_rect.center = (test_x, test_y)
                    
                    if not self.check_collision(temp_rect):
                        safe_positions.append((test_x, test_y))
        
        # If we found safe path positions, return the first one
        if safe_positions:
            return safe_positions[0]
        
        # If no path found, look for any grass tile without collision
        for y, row in enumerate(self.layers[0]):
            for x, char in enumerate(row):
                if char == 'g':  # Grass tile
                    test_x = x * self.tile_size + self.tile_size // 2
                    test_y = y * self.tile_size + self.tile_size // 2
                    
                    temp_rect = pygame.Rect(0, 0, 20, 30)
                    temp_rect.center = (test_x, test_y)
                    
                    if not self.check_collision(temp_rect):
                        safe_positions.append((test_x, test_y))
        
        # If we found safe grass positions, return the first one
        if safe_positions:
            return safe_positions[0]
        
        # If still no safe position found, try center of map
        center_x = self.map_width * self.tile_size // 2
        center_y = self.map_height * self.tile_size // 2
        
        temp_rect = pygame.Rect(0, 0, 20, 30)
        temp_rect.center = (center_x, center_y)
        
        if not self.check_collision(temp_rect):
            return center_x, center_y
        
        # Last resort: try multiple positions around the center
        for offset_x in range(0, self.map_width // 2, 2):
            for offset_y in range(0, self.map_height // 2, 2):
                test_x = center_x + offset_x * self.tile_size
                test_y = center_y + offset_y * self.tile_size
                
                # Make sure position is within map bounds
                test_x = max(self.tile_size, min(test_x, (self.map_width - 1) * self.tile_size))
                test_y = max(self.tile_size, min(test_y, (self.map_height - 1) * self.tile_size))
                
                temp_rect.center = (test_x, test_y)
                
                if not self.check_collision(temp_rect):
                    return test_x, test_y
        
        # Ultimate fallback: top-left corner (should be safe)
        return self.tile_size, self.tile_size

# For backward compatibility
TileMap = EditorTileMap