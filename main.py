import pygame
import sys
import os

# Add the game directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'game'))

from config import Config
from states.menu_state import MenuState
from states.game_state import GameState

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption("Top-Down Village Adventure")
        self.clock = pygame.time.Clock()
        
        # Initialize all states
        self.states = {
            'menu': MenuState(self),
            'game': GameState(self)
        }
        self.current_state = 'menu'
        
        print("Game initialized - Use arrow keys and ENTER in menu")
    
    def run(self):
        while True:
            dt = self.clock.tick(Config.FPS) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Pass event to current state
                self.states[self.current_state].handle_events(event)
            
            # Update current state
            self.states[self.current_state].update(dt)
            
            # Render current state
            self.states[self.current_state].render(self.screen)
            pygame.display.flip()
            
            pygame.display.set_caption(f"Top-Down Village Adventure - FPS: {self.clock.get_fps():.2f}")
            
            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()