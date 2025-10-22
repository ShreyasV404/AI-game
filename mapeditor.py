import pygame
import sys
import os
import json
from pygame.locals import *

# Add the game directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))

from config import Config
from asset_loader import asset_loader

class MapEditor:
    def __init__(self):
        pygame.init()
        
        # Reduced window size to fit most screens
        self.screen_width = 1000
        self.screen_height = 700
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Village Adventure - Map Editor")
        self.clock = pygame.time.Clock()
        
        # Load assets
        asset_loader.load_all_assets()
        
        # Editor state
        self.current_layer = 0  # 0: Ground, 1: Objects, 2: Decor
        self.selected_tile = None
        self.dragging = False
        self.offset_x, self.offset_y = 0, 0
        self.camera_x, self.camera_y = 0, 0
        self.grid_size = Config.TILE_SIZE
        self.show_grid = True
        
        # Selection tool state
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
        self.selected_blocks = set()  # Store selected block coordinates
        
        # Reduced map size to fit better in smaller window
        self.map_width = 30
        self.map_height = 25
        
        # Map data with layers
        self.layers = {
            0: [[' ' for _ in range(self.map_width)] for _ in range(self.map_height)],  # Ground layer
            1: [[' ' for _ in range(self.map_width)] for _ in range(self.map_height)],  # Object layer
            2: [[' ' for _ in range(self.map_width)] for _ in range(self.map_height)]   # Decor layer
        }
        
        # Available tiles by layer - with proper size information
        self.tile_palette = {
            0: [  # Ground layer (32x32)
                ('grass', 'g', asset_loader.get_tile('grass'), 32, 32),
                ('path', 'p', asset_loader.get_tile('path'), 32, 32)
            ],
            1: [  # Object layer  
                ('house_2', 'h', asset_loader.get_object('house_2'), 96, 96),
                ('house_4', 'H', asset_loader.get_object('house_4'), 96, 96),
                ('tree', 't', asset_loader.get_object('tree'), 64, 64)
            ],
            2: []  # Decor layer (empty for now)
        }
        
        # UI dimensions
        self.palette_width = 180  # Slightly reduced
        self.layer_height = 35    # Slightly reduced
        
        self.font = pygame.font.Font(None, 22)  # Slightly smaller font
        self.small_font = pygame.font.Font(None, 16)  # Smaller font
        
        # Tools
        self.tools = ['brush', 'select']
        self.current_tool = 'brush'
        
        print("Map Editor initialized!")
        print("Layers: 0=Ground, 1=Objects, 2=Decor")
        print("Tools: Brush (B), Select (S)")
        print("Use mouse wheel to zoom, middle click to pan")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                # Check palette click
                if mouse_x < self.palette_width:
                    if mouse_y < self.layer_height:
                        # Layer selection
                        layer_width = self.palette_width // 3
                        self.current_layer = mouse_x // layer_width
                    else:
                        # Tile selection
                        palette_y = mouse_y - self.layer_height
                        tile_index = palette_y // 50  # Reduced from 60
                        if (self.current_layer in self.tile_palette and 
                            tile_index < len(self.tile_palette[self.current_layer])):
                            tile_data = self.tile_palette[self.current_layer][tile_index]
                            self.selected_tile = tile_data
                
                # Map editing
                elif event.button == 1:  # Left click
                    if self.current_tool == 'brush':
                        self.place_tile(mouse_x, mouse_y)
                        self.dragging = True
                    elif self.current_tool == 'select':
                        self.start_selection(mouse_x, mouse_y)
                
                elif event.button == 3:  # Right click - erase tile
                    if self.current_tool == 'brush':
                        self.erase_tile(mouse_x, mouse_y)
                        self.dragging = True
                    elif self.current_tool == 'select':
                        self.clear_selection()
                
                elif event.button == 2:  # Middle click - start pan
                    self.offset_x, self.offset_y = mouse_x, mouse_y
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Left button up
                    if self.current_tool == 'brush':
                        self.dragging = False
                    elif self.current_tool == 'select':
                        self.finalize_selection()
            
            elif event.type == MOUSEMOTION:
                if event.buttons[2]:  # Middle button drag - pan
                    self.camera_x += (event.pos[0] - self.offset_x) * 0.5
                    self.camera_y += (event.pos[1] - self.offset_y) * 0.5
                    self.offset_x, self.offset_y = event.pos
                
                elif self.dragging and event.buttons[0] and self.current_tool == 'brush':  # Left drag - place tiles
                    self.place_tile(*event.pos)
                
                elif self.dragging and event.buttons[2] and self.current_tool == 'brush':  # Right drag - erase tiles
                    self.erase_tile(*event.pos)
                
                elif self.selecting and event.buttons[0] and self.current_tool == 'select':  # Selection drag
                    self.update_selection(*event.pos)
            
            elif event.type == KEYDOWN:
                if event.key == K_g:
                    self.show_grid = not self.show_grid
                elif event.key == K_s and pygame.key.get_mods() & KMOD_CTRL:
                    self.save_map()
                elif event.key == K_l and pygame.key.get_mods() & KMOD_CTRL:
                    self.load_map()
                elif event.key == K_c and pygame.key.get_mods() & KMOD_CTRL:
                    self.clear_layer()
                elif event.key == K_1:
                    self.current_layer = 0
                elif event.key == K_2:
                    self.current_layer = 1
                elif event.key == K_3:
                    self.current_layer = 2
                elif event.key == K_EQUALS or event.key == K_PLUS:
                    self.grid_size = min(64, self.grid_size + 4)
                elif event.key == K_MINUS:
                    self.grid_size = max(16, self.grid_size - 4)
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_b:
                    self.current_tool = 'brush'
                    self.clear_selection()
                elif event.key == K_s and not pygame.key.get_mods() & KMOD_CTRL:
                    self.current_tool = 'select'
                elif event.key == K_a and pygame.key.get_mods() & KMOD_CTRL:
                    self.select_all()
                elif event.key == K_BACKSPACE and self.selected_blocks:
                    self.delete_selected()
                elif event.key == K_d and pygame.key.get_mods() & KMOD_CTRL and self.selected_tile and self.selected_blocks:
                    self.fill_selected()
    
    def start_selection(self, mouse_x, mouse_y):
        """Start a new selection box"""
        self.selecting = True
        map_x, map_y = self.screen_to_map(mouse_x, mouse_y)
        self.selection_start = (map_x, map_y)
        self.selection_end = (map_x, map_y)
    
    def update_selection(self, mouse_x, mouse_y):
        """Update the selection box while dragging"""
        if self.selecting and self.selection_start:
            map_x, map_y = self.screen_to_map(mouse_x, mouse_y)
            self.selection_end = (map_x, map_y)
    
    def finalize_selection(self):
        """Finalize the selection when mouse is released"""
        if self.selecting and self.selection_start and self.selection_end:
            self.calculate_selected_blocks()
            self.selecting = False
    
    def calculate_selected_blocks(self):
        """Calculate which blocks are inside the selection rectangle"""
        if not self.selection_start or not self.selection_end:
            return
        
        start_x, start_y = self.selection_start
        end_x, end_y = self.selection_end
        
        # Normalize coordinates
        min_x = min(start_x, end_x)
        max_x = max(start_x, end_x)
        min_y = min(start_y, end_y)
        max_y = max(start_y, end_y)
        
        # Clamp to map bounds
        min_x = max(0, min_x)
        max_x = min(self.map_width - 1, max_x)
        min_y = max(0, min_y)
        max_y = min(self.map_height - 1, max_y)
        
        # Add all blocks in the rectangle to selection
        self.selected_blocks.clear()
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                self.selected_blocks.add((x, y))
    
    def clear_selection(self):
        """Clear the current selection"""
        self.selected_blocks.clear()
        self.selecting = False
        self.selection_start = None
        self.selection_end = None
    
    def select_all(self):
        """Select all blocks on the current layer"""
        self.selected_blocks.clear()
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.selected_blocks.add((x, y))
    
    def delete_selected(self):
        """Delete all selected blocks"""
        for x, y in self.selected_blocks:
            if 0 <= x < self.map_width and 0 <= y < self.map_height:
                self.layers[self.current_layer][y][x] = ' '
    
    def fill_selected(self):
        """Fill all selected blocks with the currently selected tile"""
        if not self.selected_tile:
            return
            
        for x, y in self.selected_blocks:
            if 0 <= x < self.map_width and 0 <= y < self.map_height:
                self.layers[self.current_layer][y][x] = self.selected_tile[1]
    
    def screen_to_map(self, mouse_x, mouse_y):
        """Convert screen coordinates to map coordinates"""
        map_x = int((mouse_x - self.palette_width + self.camera_x) // self.grid_size)
        map_y = int((mouse_y + self.camera_y) // self.grid_size)
        return map_x, map_y
    
    def place_tile(self, mouse_x, mouse_y):
        if not self.selected_tile:
            return
        
        map_x, map_y = self.screen_to_map(mouse_x, mouse_y)
        
        # Check bounds - for large objects, check if they fit
        if (0 <= map_x < self.map_width and 0 <= map_y < self.map_height):
            # For large objects, make sure they don't extend beyond map boundaries
            if self.current_layer == 1:  # Object layer
                tile_width_in_tiles = self.selected_tile[3] // 32
                tile_height_in_tiles = self.selected_tile[4] // 32
                
                if (map_x + tile_width_in_tiles <= self.map_width and 
                    map_y + tile_height_in_tiles <= self.map_height):
                    self.layers[self.current_layer][map_y][map_x] = self.selected_tile[1]
            else:
                self.layers[self.current_layer][map_y][map_x] = self.selected_tile[1]
    
    def erase_tile(self, mouse_x, mouse_y):
        map_x, map_y = self.screen_to_map(mouse_x, mouse_y)
        
        # Check bounds
        if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
            self.layers[self.current_layer][map_y][map_x] = ' '
    
    def clear_layer(self):
        for y in range(self.map_height):
            for x in range(self.map_width):
                self.layers[self.current_layer][y][x] = ' '
        self.clear_selection()
    
    def save_map(self):
        map_data = {
            'width': self.map_width,
            'height': self.map_height,
            'layers': self.layers
        }
        
        with open('custom_map.json', 'w') as f:
            json.dump(map_data, f, indent=2)
        
        print("Map saved as 'custom_map.json'")
    
    def load_map(self):
        try:
            with open('custom_map.json', 'r') as f:
                map_data = json.load(f)
            
            self.map_width = map_data['width']
            self.map_height = map_data['height']
            self.layers = map_data['layers']
            
            # Convert string keys back to integers
            self.layers = {int(k): v for k, v in self.layers.items()}
            
            print("Map loaded from 'custom_map.json'")
        except FileNotFoundError:
            print("No saved map found!")
    
    def draw_palette(self):
        # Draw background
        pygame.draw.rect(self.screen, (50, 50, 60), (0, 0, self.palette_width, self.screen_height))
        
        # Draw layer selector
        layer_width = self.palette_width // 3
        layers = ['GROUND', 'OBJECTS', 'DECOR']
        
        for i in range(3):
            color = (100, 150, 200) if i == self.current_layer else (70, 70, 80)
            pygame.draw.rect(self.screen, color, (i * layer_width, 0, layer_width, self.layer_height))
            text = self.font.render(layers[i], True, (255, 255, 255))
            self.screen.blit(text, (i * layer_width + 5, 8))  # Adjusted position
        
        # Draw tool selector
        tool_y = self.layer_height + 5
        tool_width = self.palette_width // 2
        tools = ['BRUSH', 'SELECT']
        
        for i, tool in enumerate(tools):
            color = (120, 180, 120) if self.tools[i] == self.current_tool else (70, 70, 80)
            pygame.draw.rect(self.screen, color, (i * tool_width, tool_y, tool_width, 25))
            text = self.small_font.render(tool, True, (255, 255, 255))
            self.screen.blit(text, (i * tool_width + 10, tool_y + 5))
        
        # Draw tile palette
        y_offset = self.layer_height + 35
        
        if self.current_layer in self.tile_palette:
            for i, (name, char, image, width, height) in enumerate(self.tile_palette[self.current_layer]):
                # Draw tile background
                rect = pygame.Rect(10, y_offset + i * 50, 160, 40)  # Reduced size
                color = (80, 80, 90) if self.selected_tile and self.selected_tile[1] == char else (60, 60, 70)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (100, 100, 110), rect, 2)
                
                # Draw tile image with proper scaling for preview
                if image:
                    # Calculate scale to fit in preview
                    preview_size = 30
                    scale_x = preview_size / width
                    scale_y = preview_size / height
                    scale = min(scale_x, scale_y)
                    
                    scaled_width = int(width * scale)
                    scaled_height = int(height * scale)
                    
                    scaled_img = pygame.transform.scale(image, (scaled_width, scaled_height))
                    x_pos = 15 + (preview_size - scaled_width) // 2
                    y_pos = y_offset + i * 50 + 5 + (preview_size - scaled_height) // 2
                    self.screen.blit(scaled_img, (x_pos, y_pos))
                
                # Draw tile name and size
                name_text = self.small_font.render(name, True, (255, 255, 255))
                self.screen.blit(name_text, (50, y_offset + i * 50 + 5))
                
                size_text = self.small_font.render(f"{width}x{height}", True, (200, 200, 200))
                self.screen.blit(size_text, (50, y_offset + i * 50 + 22))
        
        # Draw instructions
        instructions = [
            "CONTROLS:",
            "B: Brush tool",
            "S: Select tool",
            "LMB: Place/Select",
            "RMB: Erase/Clear Sel",
            "MMB: Pan camera",
            "G: Toggle grid",
            "1/2/3: Change layer",
            "+/-: Zoom in/out",
            "Ctrl+A: Select all",
            "Ctrl+D: Fill selection",
            "Del: Delete selected",
            "Ctrl+S: Save map",
            "Ctrl+L: Load map",
            "Ctrl+C: Clear layer",
            "ESC: Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, (180, 180, 180))
            self.screen.blit(text, (10, 450 + i * 18))  # Adjusted position
    
    def draw_selection(self):
        """Draw the selection box and highlighted blocks"""
        # Draw selection box during selection
        if self.selecting and self.selection_start and self.selection_end:
            start_x, start_y = self.selection_start
            end_x, end_y = self.selection_end
            
            # Convert to screen coordinates
            screen_start_x = self.palette_width + start_x * self.grid_size - self.camera_x
            screen_start_y = start_y * self.grid_size - self.camera_y
            screen_end_x = self.palette_width + end_x * self.grid_size - self.camera_x
            screen_end_y = end_y * self.grid_size - self.camera_y
            
            # Calculate rectangle
            rect_x = min(screen_start_x, screen_end_x)
            rect_y = min(screen_start_y, screen_end_y)
            rect_width = abs(screen_end_x - screen_start_x) + self.grid_size
            rect_height = abs(screen_end_y - screen_start_y) + self.grid_size
            
            # Draw semi-transparent blue selection box
            selection_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
            selection_surface.fill((0, 100, 255, 50))  # Semi-transparent blue
            pygame.draw.rect(selection_surface, (0, 150, 255), (0, 0, rect_width, rect_height), 2)
            self.screen.blit(selection_surface, (rect_x, rect_y))
        
        # Draw highlighted selected blocks
        for x, y in self.selected_blocks:
            screen_x = self.palette_width + x * self.grid_size - self.camera_x
            screen_y = y * self.grid_size - self.camera_y
            
            # Only draw if visible
            if (screen_x > -self.grid_size and screen_x < self.screen_width and
                screen_y > -self.grid_size and screen_y < self.screen_height):
                
                # Draw semi-transparent highlight
                highlight_surface = pygame.Surface((self.grid_size, self.grid_size), pygame.SRCALPHA)
                highlight_surface.fill((0, 200, 255, 80))  # Semi-transparent blue
                self.screen.blit(highlight_surface, (screen_x, screen_y))
                
                # Draw border
                pygame.draw.rect(self.screen, (0, 150, 255), 
                               (screen_x, screen_y, self.grid_size, self.grid_size), 2)
    
    def draw_map(self):
        """Draw the map with proper object sizing"""
        # Draw map background
        map_area_width = self.screen_width - self.palette_width
        pygame.draw.rect(self.screen, (40, 40, 50), 
                        (self.palette_width, 0, 
                         map_area_width, self.screen_height))
        
        # Draw ground layer first (layer 0)
        for y in range(self.map_height):
            for x in range(self.map_width):
                char = self.layers[0][y][x]
                if char == ' ':
                    continue
                
                # Find the tile data
                tile_data = None
                for tile in self.tile_palette[0]:
                    if tile[1] == char:
                        tile_data = tile
                        break
                
                if tile_data and tile_data[2]:
                    screen_x = self.palette_width + x * self.grid_size - self.camera_x
                    screen_y = y * self.grid_size - self.camera_y
                    
                    # Only draw if visible
                    if (screen_x > -self.grid_size and screen_x < self.screen_width and
                        screen_y > -self.grid_size and screen_y < self.screen_height):
                        
                        # Scale ground tiles to grid size (32x32)
                        scaled_img = pygame.transform.scale(tile_data[2], (self.grid_size, self.grid_size))
                        self.screen.blit(scaled_img, (screen_x, screen_y))
        
        # Draw object layer (layer 1) with proper sizing
        for y in range(self.map_height):
            for x in range(self.map_width):
                char = self.layers[1][y][x]
                if char == ' ':
                    continue
                
                # Find the object data
                obj_data = None
                for obj in self.tile_palette[1]:
                    if obj[1] == char:
                        obj_data = obj
                        break
                
                if obj_data and obj_data[2]:
                    # Calculate the base position (top-left of the grid cell)
                    base_x = self.palette_width + x * self.grid_size - self.camera_x
                    base_y = y * self.grid_size - self.camera_y
                    
                    # Get object dimensions
                    obj_width, obj_height = obj_data[3], obj_data[4]
                    
                    # Calculate scale factor to convert from pixels to grid units
                    scale_factor = self.grid_size / 32.0
                    
                    # Calculate scaled dimensions
                    scaled_width = int(obj_width * scale_factor)
                    scaled_height = int(obj_height * scale_factor)
                    
                    # Center the object horizontally and align to bottom of cell
                    obj_x = base_x - (scaled_width - self.grid_size) // 2
                    obj_y = base_y - (scaled_height - self.grid_size)
                    
                    # Only draw if visible
                    if (obj_x < self.screen_width and obj_x + scaled_width > self.palette_width and
                        obj_y < self.screen_height and obj_y + scaled_height > 0):
                        
                        # Scale object to proper size
                        scaled_obj = pygame.transform.scale(obj_data[2], (scaled_width, scaled_height))
                        self.screen.blit(scaled_obj, (obj_x, obj_y))
        
        # Draw grid
        if self.show_grid:
            for x in range(0, self.map_width):
                for y in range(0, self.map_height):
                    screen_x = self.palette_width + x * self.grid_size - self.camera_x
                    screen_y = y * self.grid_size - self.camera_y
                    
                    # Check if visible in current viewport
                    if (screen_x > -self.grid_size and screen_x < self.screen_width and
                        screen_y > -self.grid_size and screen_y < self.screen_height):
                        
                        pygame.draw.rect(self.screen, (80, 80, 80), 
                                       (screen_x, screen_y, self.grid_size, self.grid_size), 1)
    
    def draw_ui(self):
        # Current layer info
        layer_names = {0: "GROUND", 1: "OBJECTS", 2: "DECOR"}
        layer_text = self.font.render(f"Layer: {layer_names[self.current_layer]}", True, (255, 255, 255))
        self.screen.blit(layer_text, (self.palette_width + 10, 10))
        
        # Current tool info
        tool_text = self.font.render(f"Tool: {self.current_tool.upper()}", True, (255, 255, 255))
        self.screen.blit(tool_text, (self.palette_width + 10, 35))
        
        # Selected tile info with size
        if self.selected_tile:
            size_info = f" ({self.selected_tile[3]}x{self.selected_tile[4]})" if len(self.selected_tile) > 3 else ""
            tile_text = self.small_font.render(f"Selected: {self.selected_tile[0]}{size_info}", 
                                       True, (255, 255, 255))
            self.screen.blit(tile_text, (self.palette_width + 10, 60))
        
        # Selection info
        if self.selected_blocks:
            sel_text = self.small_font.render(f"Selected: {len(self.selected_blocks)} blocks", True, (0, 200, 255))
            self.screen.blit(sel_text, (self.palette_width + 10, 85))
        
        # Grid info
        grid_text = self.small_font.render(f"Grid: {self.grid_size}px", True, (255, 255, 255))
        self.screen.blit(grid_text, (self.palette_width + 10, 110))
        
        # Camera info
        cam_text = self.small_font.render(f"Camera: ({int(self.camera_x)}, {int(self.camera_y)})", True, (255, 255, 255))
        self.screen.blit(cam_text, (self.palette_width + 10, 135))
        
        # Map info
        map_text = self.small_font.render(f"Map: {self.map_width}x{self.map_height}", True, (255, 255, 255))
        self.screen.blit(map_text, (self.screen_width - 120, 10))
        
        # Help text
        help_text = self.small_font.render("Press B/S to switch tools, ESC to exit", True, (200, 200, 200))
        self.screen.blit(help_text, (self.screen_width - 280, self.screen_height - 20))
    
    def run(self):
        while True:
            self.handle_events()
            
            # Clear screen
            self.screen.fill((30, 30, 40))
            
            # Draw everything
            self.draw_palette()
            self.draw_map()
            self.draw_selection()  # Draw selection on top of map
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    editor = MapEditor()
    editor.run()