import pygame
import random
from game.config import Config
from game.asset_loader import asset_loader

# Expanded village layout based on your pattern
# g = grass, p = path, h = house plot, t = tree plot
# Scaled up to create a proper village with connected paths and neighborhoods
VILLAGE_LAYOUT = [
    "tttttttttttttttttttttttttttttttttttttttttttttttttt",
    "tggggggggggggggggggggggggggggggggggggggggggggggggt",
    "tggggggggggggggggggggggggggggggggggggggggggggggggt",
    "tggghgggtggghgggtggghgggtggghgggtggghgggtggghggggt",
    "tggg   gggg   gggg   gggg   gggg   gggg   gggggggt",
    "tggg   gggg   gggg   gggg   gggg   gggg   gggggggt",
    "tggghgggtggghgggtggghgggtggghgggtggghgggtggghggggt",
    "tggggggggggggggggggggggggggggggggggggggggggggggggt",
    "tgggpppppppppppppppppppppppppppppppppppppppppgggt",
    "tgggpgggggggggggggggggggggggggggggggggggggggpgggt",
    "tgggpggghgggtgggppppppppppppppppppgggtggghggpgggt",
    "tgggpggg   ggggpggggggggggggggggggpgggg   gggpgggt",
    "tgggpggg   ggggpggghgggtggghgggtgggpgggg   gggpgggt",
    "tgggpggghgggtggpggg   gggg   gggg   pgggtggghggggt",
    "tgggpggggggggggpggg   gggg   gggg   pggggggggggggt",
    "tgggppppppppppppppp   gggg   gggg   pppppppppppggt",
    "tgggggggggggggggggp   gggg   gggg   pggggggggggggt",
    "tggghgggtggghgggtgp   gggg   gggg   pgtggghgggtggt",
    "tggg   gggg   ggggg   gggg   gggg   ggggg   gggggt",
    "tggg   gggg   ggggg   gggg   gggg   ggggg   gggggt",
    "tggghgggtggghgggtgp   gggg   gggg   pgtggghgggtggt",
    "tgggggggggggggggggp   gggg   gggg   pggggggggggggt",
    "tgggppppppppppppppp   gggg   gggg   pppppppppppggt",
    "tgggpggggggggggpggg   gggg   gggg   pggggggggggggt",
    "tgggpggghgggtggpggg   gggg   gggg   pgggtggghggggt",
    "tgggpggg   ggggpggghgggtggghgggtgggpgggg   gggpgggt",
    "tgggpggg   ggggpgggggggggggggggggggpgggg   gggpgggt",
    "tgggpggghgggtgggppppppppppppppppppgggtggghggpgggt",
    "tgggpgggggggggggggggggggggggggggggggggggggggpgggt",
    "tgggpppppppppppppppppppppppppppppppppppppppppgggt",
    "tgggggggggggggggggggggggggggggggggggggggggggggggt",
    "tggghgggtggghgggtggghgggtggghgggtggghgggtggghggggt",
    "tggg   gggg   gggg   gggg   gggg   gggg   gggggggt",
    "tggg   gggg   gggg   gggg   gggg   gggg   gggggggt",
    "tggghgggtggghgggtggghgggtggghgggtggghgggtggghggggt",
    "tggggggggggggggggggggggggggggggggggggggggggggggggt",
    "ttttttttttttttttttttttttttttttttttttttttttttttttt",
]


class TileMap:
    def __init__(self):
        self.tile_size = Config.TILE_SIZE
        self.objects = []  # List for houses, trees, and other large objects
        self.collision_rects = []  # List for *all* collision rectangles
        
        # Dictionaries to hold our loaded assets
        self.tiles = {}
        self.objects_assets = {}
        
        self.load_assets()
        self.build_map()

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
        
        print("All map assets loaded into TileMap.")

    def build_map(self):
        """Create the map surface and objects based on the VILLAGE_LAYOUT."""
        self.map_layout = VILLAGE_LAYOUT
        self.width = len(self.map_layout[0])
        self.height = len(self.map_layout)
        
        # This 2D list will hold the pre-rendered surface for each tile
        self.tile_surfaces = []

        for y, row in enumerate(self.map_layout):
            row_surfaces = []
            for x, char in enumerate(row):
                # Determine base tile
                if char == 'g':
                    base_tile = self.tiles['grass'].copy()
                elif char == 'p':
                    base_tile = self.tiles['path'].copy()
                elif char == 'h':
                    base_tile = self.tiles['grass'].copy()
                elif char == 't':
                    base_tile = self.tiles['grass'].copy()
                else:  # Space character for house interiors
                    base_tile = self.tiles['grass'].copy()

                tile_pos = (x * self.tile_size, y * self.tile_size)

                # Add objects and collision based on character
                if char == 't':
                    # Add tree
                    self._place_object('tree', x, y)
                    # Tree collision (smaller than visual tree)
                    collision_rect = pygame.Rect(
                        tile_pos[0] + 10, 
                        tile_pos[1] + 30, 
                        self.tile_size - 20, 
                        self.tile_size - 30
                    )
                    self.collision_rects.append(collision_rect)
                
                elif char == 'h':
                    # Add house (alternate between two house types)
                    house_type = 'house_2' if (x + y) % 2 == 0 else 'house_4'
                    self._place_object(house_type, x, y)
                    # House collision (covers the entire tile)
                    collision_rect = pygame.Rect(tile_pos, (self.tile_size, self.tile_size))
                    self.collision_rects.append(collision_rect)
                
                row_surfaces.append(base_tile)
            self.tile_surfaces.append(row_surfaces)
        
        print(f"Map built: {self.width}x{self.height} tiles.")
        print(f"Placed {len(self.objects)} large objects.")
        print(f"Created {len(self.collision_rects)} collision rectangles.")

    def _place_object(self, obj_type, tile_x, tile_y):
        """Helper to place an object on the map."""
        image = self.objects_assets.get(obj_type)
        if not image:
            return

        pixel_x = tile_x * self.tile_size
        pixel_y = tile_y * self.tile_size
        
        # Adjust position based on object size
        img_width, img_height = image.get_size()
        
        # Center the object on the tile
        if obj_type == 'tree':
            # Trees are 64x64, so center them on 32x32 tiles
            adj_x = pixel_x - (img_width - self.tile_size) // 2
            adj_y = pixel_y - (img_height - self.tile_size)
        else:
            # Houses are larger, adjust accordingly
            adj_x = pixel_x - (img_width - self.tile_size) // 2
            adj_y = pixel_y - (img_height - self.tile_size)
        
        # Add to object list for drawing
        self.objects.append({
            'image': image,
            'rect': pygame.Rect(adj_x, adj_y, img_width, img_height)
        })

    def check_collision(self, rect):
        """Check if a rectangle collides with any object or wall."""
        for collision_rect in self.collision_rects:
            if rect.colliderect(collision_rect):
                return True
        return False

    def draw(self, surface, camera_offset):
        """Draw the visible portion of the tilemap and objects."""
        
        # Calculate visible tile range
        start_x = max(0, int(camera_offset.x // self.tile_size))
        end_x = min(self.width, int((camera_offset.x + Config.SCREEN_WIDTH) // self.tile_size) + 2)
        start_y = max(0, int(camera_offset.y // self.tile_size))
        end_y = min(self.height, int((camera_offset.y + Config.SCREEN_HEIGHT) // self.tile_size) + 2)
        
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
        
        # Layer 2: Draw large objects (houses, trees)
        visible_objects = []
        for obj in self.objects:
            obj_rect = obj['rect']
            # Check if object is visible on screen
            if (obj_rect.x - camera_offset.x < Config.SCREEN_WIDTH and 
                obj_rect.x + obj_rect.width - camera_offset.x > 0 and
                obj_rect.y - camera_offset.y < Config.SCREEN_HEIGHT and
                obj_rect.y + obj_rect.height - camera_offset.y > 0):
                
                visible_objects.append(obj)
        
        # Sort by the bottom of the rect
        sorted_objects = sorted(visible_objects, key=lambda obj: obj['rect'].bottom)
        
        for obj in sorted_objects:
            surface.blit(obj['image'], (obj['rect'].x - camera_offset.x, 
                                        obj['rect'].y - camera_offset.y))

        # Debug: Draw collision rectangles (uncomment to see collision areas)
        # for collision_rect in self.collision_rects:
        #     debug_rect = collision_rect.move(-camera_offset.x, -camera_offset.y)
        #     pygame.draw.rect(surface, (255, 0, 0), debug_rect, 1)