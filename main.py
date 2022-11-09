from game import Game
import sys
# Multiplayer

if len(sys.argv) > 1:
    game = Game(sys.argv[1])
else:
    game = Game('cfg.ini')

while True:
    game.curr_menu.menu_loop()


