import pygame
from game.config import Config

class MenuState:
    def __init__(self, game):
        self.game = game
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.selected_option = 0
        self.options = ["Start Game", "Options", "Quit"]
        
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.handle_selection()
    
    def handle_selection(self):
        if self.selected_option == 0:
            # Switch to game state
            self.game.current_state = 'game'
            print("Switching to game state...")
        elif self.selected_option == 1:
            print("Options selected")
        elif self.selected_option == 2:
            pygame.quit()
            exit()
    
    def update(self, dt):
        pass
    
    def render(self, surface):
        surface.fill((40, 44, 52))
        
        # Title
        title = self.font_large.render("Village Adventure", True, (255, 203, 107))
        surface.blit(title, (Config.SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Menu options
        for i, option in enumerate(self.options):
            color = (255, 203, 107) if i == self.selected_option else (220, 220, 220)
            text = self.font_small.render(option, True, color)
            surface.blit(text, (Config.SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 50))
        
        # Instructions
        instructions = self.font_small.render("Use ↑↓ arrows to navigate, ENTER to select", True, (180, 180, 180))
        surface.blit(instructions, (Config.SCREEN_WIDTH // 2 - instructions.get_width() // 2, 400))