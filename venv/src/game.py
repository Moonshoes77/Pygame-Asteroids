import pygame
from player import Player

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Fuck you")
        self._window = pygame.display.set_mode((1024, 768))
        self._clock = pygame.time.Clock()
        self._player = Player(self._window)

    
    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        quit()
            
            self._window.fill(0)
            self._player.update()
            self._player.display()
            pygame.display.flip()
            self._clock.tick(60)   
    