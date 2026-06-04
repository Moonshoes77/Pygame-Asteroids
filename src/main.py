from game import Game
import sys

def main():

    game = Game()
    if game.run() == 1:
        return main()
    else:
        sys.exit()
    
main()
     