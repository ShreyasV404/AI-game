import pygame
import os
from game.config import Config

class AssetLoader:
    def __init__(self):
        self.assets = {}
        self.loaded = False
        self.base_path = "assets"  # Base path for all assets
        
        # Direction mapping - we'll adjust this based on testing
        # Current mapping that's wrong: up->left, left->right, right->up
        # Let's try to find the correct mapping
        self.direction_map = {
            'front': 0,   # Try different values
            'back': 3,    # Try different values  
            'side_left': 1,  # Try different values
            'side_right': 2  # Try different values
        }
        
    def load_all_assets(self):
        """Load all game assets"""
        if self.loaded:
            return
            
        print("Loading game assets...")
        
        # Load tileset first (background)
        self.load_tileset_assets()
        
        # Load character animations
        self.load_character_assets()
        
        # Load objects (houses, etc.)
        self.load_object_assets()
        
        self.loaded = True
        print("Assets loaded successfully!")
        
    
    def load_image(self, path, convert_alpha=True):
        """Load an image with error handling"""
        try:
            full_path = os.path.join(self.base_path, path)
            if convert_alpha:
                return pygame.image.load(full_path).convert_alpha()
            else:
                return pygame.image.load(full_path).convert()
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            # Return a placeholder
            surface = pygame.Surface((64, 64))
            surface.fill((255, 0, 255))  # Magenta for missing texture
            return surface
    
    def split_sprite_sheet(self, sprite_sheet, frame_width, frame_height):
        """Split a sprite sheet into individual frames by rows and columns"""
        frames = []
        sheet_width, sheet_height = sprite_sheet.get_size()
        
        # Calculate rows and columns based on sheet dimensions
        cols = sheet_width // frame_width
        rows = sheet_height // frame_height
        
        print(f"Splitting sprite sheet: {sheet_width}x{sheet_height} into {cols}x{rows} frames of {frame_width}x{frame_height}")
        
        for row in range(rows):
            row_frames = []
            for col in range(cols):
                # Calculate the position of the frame
                x = col * frame_width
                y = row * frame_height
                
                # Extract the frame
                frame = sprite_sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                row_frames.append(frame)
            frames.append(row_frames)
        
        return frames, rows, cols
    
    def load_character_assets(self):
        """Load actual character sprite sheets"""
        self.assets['character'] = {
            'sword': {},
            'unarmed': {}
        }
        
        # Load sword character sprite sheets
        sword_animations = {
            'idle': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Idle_with_shadow.png',
                'frame_width': 64,
                'frame_height': 64,
            },
            'walk': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Walk_with_shadow.png',
                'frame_width': 64,
                'frame_height': 64,
            },
            'run': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Run_with_shadow.png',
                'frame_width': 64,
                'frame_height': 64,
            },
            'attack': {
                'file': 'character/PNG/Sword/With_shadow/Sword_attack_with_shadow.png',
                'frame_width': 64,
                'frame_height': 64,
            },
            'death': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Death_with_shadow.png',
                'frame_width': 64,
                'frame_height': 64,
            },
            'hurt': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Hurt_with_shadow.png',
                'frame_width': 64,
                'frame_height': 64,
            }
        }
        
        # Load each sword animation
        for state, config in sword_animations.items():
            sprite_sheet = self.load_image(config['file'])
            if sprite_sheet and sprite_sheet.get_size() != (1, 1):  # Check if not placeholder
                frames_by_row, rows, cols = self.split_sprite_sheet(
                    sprite_sheet, 
                    config['frame_width'], 
                    config['frame_height']
                )
                
                print(f"  {state} sprite sheet has {rows} rows and {cols} columns")
                
                # Use our direction mapping to assign rows to directions
                for direction, row_index in self.direction_map.items():
                    if row_index < len(frames_by_row):
                        key = f"{state}_{direction}"
                        self.assets['character']['sword'][key] = frames_by_row[row_index]
                        print(f"    - Row {row_index} -> {direction}: {len(frames_by_row[row_index])} frames")
                    else:
                        print(f"    - ERROR: Row {row_index} not available for {direction}")
                
            else:
                print(f"Failed to load {state} sprite sheet, using placeholder")
                # Create placeholder as fallback
                self.create_placeholder_animations('sword', state)
        
        # For unarmed, we'll use sword animations as fallback for now
        self.assets['character']['unarmed'] = self.assets['character']['sword'].copy()
        
        print(f"Loaded character: {len(self.assets['character']['sword'])} sword animations")
    
    def create_placeholder_animations(self, weapon_type, state):
        """Create placeholder animations if sprite sheets fail to load"""
        frames = 4  # Default number of frames
        
        if state == 'walk':
            frames = 6
        elif state == 'run':
            frames = 8
        elif state == 'attack':
            frames = 6
        elif state == 'death':
            frames = 7
        elif state == 'hurt':
            frames = 3
        
        directions = ['front', 'back', 'side_left', 'side_right']
        for direction in directions:
            key = f"{state}_{direction}"
            animation_frames = []
            for i in range(frames):
                frame = self.create_character_frame(weapon_type, direction, i, frames)
                animation_frames.append(frame)
            self.assets['character'][weapon_type][key] = animation_frames
    
    def create_character_frame(self, weapon_type, direction, frame_index, total_frames):
        """Create a simple placeholder character frame (fallback)"""
        width, height = 64, 64
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Simple character representation
        color = (255, 100, 100) if weapon_type == 'sword' else (100, 100, 255)
        
        # Body
        pygame.draw.rect(surface, color, (16, 20, 32, 30))
        
        # Head
        pygame.draw.circle(surface, (255, 220, 180), (32, 12), 10)
        
        # Simple animation for walk/run
        leg_offset = int(4 * (1 if (frame_index % total_frames) < total_frames/2 else -1))
        
        # Legs
        leg_color = (50, 50, 50)
        if direction in ['front', 'back']:
            pygame.draw.rect(surface, leg_color, (20, 48, 8, 12))
            pygame.draw.rect(surface, leg_color, (44, 48, 8, 12))
        elif direction == 'side_left':
            pygame.draw.rect(surface, leg_color, (32 + leg_offset, 48, 8, 12))
            pygame.draw.rect(surface, leg_color, (48, 48, 8, 12))
        elif direction == 'side_right':
            pygame.draw.rect(surface, leg_color, (24 - leg_offset, 48, 8, 12))
            pygame.draw.rect(surface, leg_color, (8, 48, 8, 12))
        
        # Add border to indicate placeholder
        pygame.draw.rect(surface, (255, 255, 0), (0, 0, width, height), 2)
        
        return surface
    
    def load_tileset_assets(self):
        """Load the main tileset background and individual tiles"""
        self.assets['tileset'] = {}
        
        # Load the main FieldsTileset as background
        fields_tileset = self.load_image("tileset/1 Tiles/FieldsTileset.png", convert_alpha=False)
        
        # Load specific grass tile (FieldsTile_38)
        grass_tile = self.load_image("tileset/1 Tiles/FieldsTile_38.png", convert_alpha=False)
        
        # Store the background and grass tile
        self.assets['tileset']['background'] = fields_tileset
        self.assets['tileset']['grass'] = grass_tile
        
        print(f"Loaded background: {fields_tileset.get_size()}")
        print(f"Loaded grass tile: {grass_tile.get_size()}")
    
    def load_object_assets(self):
        """Load object assets like houses"""
        self.assets['objects'] = {}
        
        # Load houses
        house_files = ["1.png", "2.png", "3.png", "4.png"]
        self.assets['objects']['houses'] = []
        
        for house_file in house_files:
            house_path = f"tileset/2 Objects/7 House/{house_file}"
            house_image = self.load_image(house_path)
            self.assets['objects']['houses'].append(house_image)
            print(f"Loaded house: {house_file} - Size: {house_image.get_size()}")
        
        print(f"Loaded {len(self.assets['objects']['houses'])} house variants")
    
    def get_background(self):
        """Get the background image"""
        return self.assets['tileset'].get('background')
    
    def get_grass_tile(self):
        """Get the grass tile"""
        return self.assets['tileset'].get('grass')
    
    def get_house(self, variant=0):
        """Get house object by variant"""
        if 'houses' in self.assets['objects'] and variant < len(self.assets['objects']['houses']):
            return self.assets['objects']['houses'][variant]
        return None
    
    def get_character_animation(self, weapon, state, direction):
        """Get animation frames for character"""
        key = f"{state}_{direction}"
        if weapon in self.assets['character'] and key in self.assets['character'][weapon]:
            return self.assets['character'][weapon][key]
        
        # Fallback if animation not found
        print(f"Animation not found: {key}, using idle_front as fallback")
        return self.assets['character'][weapon].get('idle_front', [])

# Global asset loader instance
asset_loader = AssetLoader()