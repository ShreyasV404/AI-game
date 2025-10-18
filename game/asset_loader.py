import pygame
import os
from game.config import Config

class AssetLoader:
    def __init__(self):
        self.assets = {
            'character': {},
            'tiles': {},
            'objects': {},
            'decor': {}
        }
        self.loaded = False
        self.base_path = "assets"  # Base path for all assets
        
        # This mapping seems correct for the spritesheets.
        # Row 0: front, Row 1: left, Row 2: right, Row 3: back
        self.direction_map = {
            'front': 0,
            'side_left': 1,
            'side_right': 2,
            'back': 3,
        }
        
    def load_all_assets(self):
        """Load all game assets"""
        if self.loaded:
            return
            
        print("Loading game assets...")
        
        # Load tiles (ground, fences)
        self.load_tileset_assets()
        
        # Load decor (grass tufts)
        self.load_decor_assets()
        
        # Load objects (houses, tents)
        self.load_object_assets()
        
        # Load character animations
        self.load_character_assets()
        
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
            surface = pygame.Surface((32, 32))
            surface.fill((255, 0, 255))  # Magenta for missing texture
            return surface
    
    def load_tileset_assets(self):
        """Load all individual ground and fence tiles"""
        print("Loading tileset...")
        
        # Load specific tiles we need
        self.assets['tiles']['grass'] = self.load_image("tileset/1 Tiles/FieldsTile_38.png", convert_alpha=False)
        self.assets['tiles']['path'] = self.load_image("tileset/1 Tiles/FieldsTile_05.png", convert_alpha=False)
        
        print(f"Loaded {len(self.assets['tiles'])} tiles.")

    def load_object_assets(self):
        """Load object assets like houses and trees"""
        print("Loading objects...")
        
        # Load houses
        self.assets['objects']['house_2'] = self.load_image("tileset/2 Objects/7 House/2.png")
        self.assets['objects']['house_4'] = self.load_image("tileset/2 Objects/7 House/4.png")
        
        # Load tree
        self.assets['objects']['tree'] = self.load_image("tileset/2 Objects/8 Tree/tree.png")
        
        print(f"Loaded {len(self.assets['objects'])} objects.")

    def load_decor_assets(self):
        """Load decor assets"""
        print("Loading decor...")
        # We're not using decor for now, but keeping the structure
        print("No decor items loaded.")
        
    def split_sprite_sheet(self, sprite_sheet, frame_width, frame_height):
        """Split a sprite sheet into individual frames by rows and columns"""
        frames = []
        sheet_width, sheet_height = sprite_sheet.get_size()
        
        cols = sheet_width // frame_width
        rows = sheet_height // frame_height
        
        print(f"Splitting sprite sheet: {sheet_width}x{sheet_height} into {cols}x{rows} frames of {frame_width}x{frame_height}")
        
        for row in range(rows):
            row_frames = []
            for col in range(cols):
                x = col * frame_width
                y = row * frame_height
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
        
        sword_animations = {
            'idle': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Idle_with_shadow.png',
                'frame_width': 64, 'frame_height': 64,
                'expected_frames': 4  # Expected frames per direction
            },
            'walk': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Walk_with_shadow.png',
                'frame_width': 64, 'frame_height': 64,
                'expected_frames': 6
            },
            'run': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Run_with_shadow.png',
                'frame_width': 64, 'frame_height': 64,
                'expected_frames': 8
            },
            'attack': {
                'file': 'character/PNG/Sword/With_shadow/Sword_attack_with_shadow.png',
                'frame_width': 64, 'frame_height': 64,
                'expected_frames': 6
            },
            'death': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Death_with_shadow.png',
                'frame_width': 64, 'frame_height': 64,
                'expected_frames': 7
            },
            'hurt': {
                'file': 'character/PNG/Sword/With_shadow/Sword_Hurt_with_shadow.png',
                'frame_width': 64, 'frame_height': 64,
                'expected_frames': 3
            }
        }
        
        print("Loading character assets...")
        for state, config in sword_animations.items():
            sprite_sheet = self.load_image(config['file'])
            if sprite_sheet and sprite_sheet.get_width() > 64:  # Check if not placeholder
                frames_by_row, rows, cols = self.split_sprite_sheet(
                    sprite_sheet, 
                    config['frame_width'], 
                    config['frame_height']
                )
                
                print(f"  {state} sprite sheet has {rows} rows and {cols} columns")
                
                for direction, row_index in self.direction_map.items():
                    if row_index < len(frames_by_row):
                        key = f"{state}_{direction}"
                        animation_frames = frames_by_row[row_index]
                        
                        # Ensure we have the expected number of frames
                        if len(animation_frames) < config['expected_frames']:
                            print(f"     - WARNING: {direction} has only {len(animation_frames)} frames, expected {config['expected_frames']}")
                            # Duplicate the last frame to fill missing frames
                            last_frame = animation_frames[-1] if animation_frames else self.create_character_frame('sword', direction, 0, 1)
                            while len(animation_frames) < config['expected_frames']:
                                animation_frames.append(last_frame)
                        
                        self.assets['character']['sword'][key] = animation_frames
                        print(f"     - Row {row_index} -> {direction}: {len(animation_frames)} frames")
                    else:
                        print(f"     - ERROR: Row {row_index} not available for {direction}")
                        # Create placeholder animation for missing direction
                        self.create_placeholder_animations('sword', state, direction, config['expected_frames'])
            else:
                print(f"Failed to load {state} sprite sheet, using placeholder")
                for direction in self.direction_map.keys():
                    self.create_placeholder_animations('sword', state, direction, config['expected_frames'])
        
        self.assets['character']['unarmed'] = self.assets['character']['sword'].copy()
        print(f"Loaded character: {len(self.assets['character']['sword'])} sword animations")
    
    def create_placeholder_animations(self, weapon_type, state, direction, frames):
        """Create placeholder animations if sprite sheets fail to load"""
        animation_frames = [self.create_character_frame(weapon_type, direction, i, frames) for i in range(frames)]
        key = f"{state}_{direction}"
        self.assets['character'][weapon_type][key] = animation_frames
    
    def create_character_frame(self, weapon_type, direction, frame_index, total_frames):
        """Create a simple placeholder character frame (fallback)"""
        width, height = 64, 64
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Different colors for different weapons
        if weapon_type == 'sword':
            body_color = (255, 100, 100)  # Reddish
            weapon_color = (200, 200, 200)  # Gray sword
        else:
            body_color = (100, 100, 255)  # Blueish
            weapon_color = (150, 150, 150)  # Dark gray for unarmed
        
        # Body
        pygame.draw.rect(surface, body_color, (16, 20, 32, 30))
        
        # Head
        pygame.draw.circle(surface, (255, 220, 180), (32, 12), 10)
        
        # Legs with walking animation
        leg_offset = int(4 * (frame_index % 2))  # Alternate legs
        leg_color = (50, 50, 50)
        
        if direction == 'front':
            pygame.draw.rect(surface, leg_color, (20, 48, 8, 12))
            pygame.draw.rect(surface, leg_color, (44, 48, 8, 12))
        elif direction == 'back':
            # For back view, make legs more visible
            pygame.draw.rect(surface, leg_color, (22, 48, 6, 12))
            pygame.draw.rect(surface, leg_color, (42, 48, 6, 12))
        elif direction == 'side_left':
            pygame.draw.rect(surface, leg_color, (28 + leg_offset, 48, 8, 12))
            pygame.draw.rect(surface, leg_color, (36 - leg_offset, 48, 8, 12))
        elif direction == 'side_right':
            pygame.draw.rect(surface, leg_color, (28 - leg_offset, 48, 8, 12))
            pygame.draw.rect(surface, leg_color, (36 + leg_offset, 48, 8, 12))
        
        # Add weapon for sword
        if weapon_type == 'sword':
            if direction == 'side_right':
                pygame.draw.rect(surface, weapon_color, (50, 25, 10, 4))  # Sword on right side
            elif direction == 'side_left':
                pygame.draw.rect(surface, weapon_color, (4, 25, 10, 4))   # Sword on left side
            else:
                pygame.draw.rect(surface, weapon_color, (32, 50, 4, 10))  # Sword pointing down
        
        # Border for visibility
        pygame.draw.rect(surface, (255, 255, 0), (0, 0, width, height), 2)
        
        # Add frame number for debugging
        font = pygame.font.Font(None, 20)
        frame_text = font.render(str(frame_index), True, (255, 255, 255))
        surface.blit(frame_text, (5, 5))
        
        return surface
    
    # --- GETTER METHODS ---
    
    def get_tile(self, name):
        """Get a specific tile by name"""
        return self.assets['tiles'].get(name)

    def get_object(self, name):
        """Get a specific object by name"""
        return self.assets['objects'].get(name)

    def get_decor(self, name):
        """Get a specific decor item by name"""
        return self.assets['decor'].get(name)
        
    def get_character_animation(self, weapon, state, direction):
        """Get animation frames for character"""
        key = f"{state}_{direction}"
        if weapon in self.assets['character'] and key in self.assets['character'][weapon]:
            frames = self.assets['character'][weapon][key]
            if frames:  # Check if we have frames
                return frames
        
        # Fallback: try to get any animation for this state
        print(f"Animation not found: {key}, looking for fallback...")
        for fallback_dir in ['front', 'side_right', 'side_left', 'back']:
            fallback_key = f"{state}_{fallback_dir}"
            if weapon in self.assets['character'] and fallback_key in self.assets['character'][weapon]:
                print(f"Using fallback: {fallback_key}")
                return self.assets['character'][weapon][fallback_key]
        
        # Ultimate fallback: idle front
        print(f"No animation found for {key}, using idle_front as ultimate fallback")
        return self.assets['character'][weapon].get('idle_front', [])

# Global asset loader instance
asset_loader = AssetLoader()