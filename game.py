import json
import sys
import pygame
import pygame.time

from game_objects import *
from menus import *
from network import *
from init_settings import *
from graphics import Graphics
from debug import Debug

class Game(object):
    def __init__(self, cfg):
        # Pygame setup
        self.graphics = Graphics()
        self.clock = pygame.time.Clock()
        # pygame.init()
        # self.width, self.height = 400, 800
        # self.screen = pygame.display.set_mode((self.width, self.height))
        # # info = pygame.display.Info()  # You have to call this before pygame.display.set_mode()
        # # self.width, self.height = info.current_w, info.current_h
        # # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # self.clock = pygame.time.Clock()
        # self.font_name = pygame.font.get_default_font()
        # Gameplay variables
        self.user = User()
        self.gameinfo = GameInfo()
        self.cfg = cfg
        # self.user, self.gameinfo = load_cfg(self.cfg)
        self.user = load_cfg(self.cfg)
        self.players = []
        self.followers = []
        self.obstacle_group = pygame.sprite.Group()
        # menus
        self.main_menu = MainMenu(self)
        self.sp_menu = SinglePlayer(self)
        self.mp_menu = MultiPlayer(self)
        self.mp_server_menu = MultiPlayerServer(self)
        self.mp_client_menu = MultiPlayerClient(self)
        self.mp_client_waiting_menu = MpClientWaiting(self)
        self.mp_server_waiting_menu = MpServerWaiting(self)
        self.sp_set_players_menu = SpSetPlayers(self)
        self.points_menu = Points(self)
        self.curr_menu = self.main_menu
        # Inputs
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY, self.SPACE_KEY = False, False, False,\
                                                                                                  False, False, False
        self.keys = pygame.key.get_pressed()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_moved = False
        self.text_input = ""
        self.text_typing = False
        # Network
        self.network = None
        self.client = False
        self.client_controls = [False, False, False, 0]

        self.gap_test = False
        # debug
        # self.debug = Debug(self.graphics)

    def init_game(self):
        try:
            for i in range(self.gameinfo.players_num):
                player = pygame.sprite.GroupSingle(Player(i, self))
                follower = pygame.sprite.GroupSingle(Follower(i))
                self.players.append(player)
                self.followers.append(follower)
        except Exception as e:
            print(f"Function: init_game Error-message: {e}")

    def init_client(self, server):
        self.network = Client(self, server)

    def init_server(self):
        self.network = Server(self)

    def all_ready(self):
        all_ready = True
        for i in range(self.gameinfo.players_num):
            # print(f"{i}: {self.players[i].sprite.ready}")
            if not self.players[i].sprite.ready:
                all_ready = False
                # break
        return all_ready

    def all_visible(self, visible):
        try:
            for i in range(self.gameinfo.players_num):
                self.players[i].sprite.visible = not visible
        except:
            pass

    def all_received(self):
        all_received = True
        for i in range(self.gameinfo.bot_num+1, self.gameinfo.players_num, 1):
            if self.gameinfo.timestamp != self.players[i].sprite.timestamp:
                all_received = False
                break
        return all_received

    def end_game(self):
        self.save_points()
        for item in self.players:
            item.empty()
        self.players.clear()
        for item in self.followers:
            item.empty()
        self.followers.clear()
        self.obstacle_group.empty()
        if not self.client:
            self.gameinfo.end = True

    def draw_all(self):
        try:
            for i in range(self.gameinfo.players_num):
                if self.players[i].sprite.visible:
                    self.obstacle_group.add(Obstacle(self.players[i].sprite.f2_x, self.players[i].sprite.f2_y, i))
                self.followers[i].update(self.players[i].sprite.f1_x, self.players[i].sprite.f1_y)

            self.obstacle_group.draw(self.graphics.screen)
            for i in range(self.gameinfo.players_num):
                if self.players[i].sprite.alive:
                    if self.client:
                        self.players[i].update(move=False)
                    else:
                        self.players[i].update()

            for i in range(self.gameinfo.players_num):
                if not self.gameinfo.gap:
                    self.followers[i].draw(self.graphics.screen)
                self.players[i].draw(self.graphics.screen)
                # self.players[i].sprite.radar.draw(self.screen)

        except Exception as e:
            print(f"Function: draw_all Error-message: {e}")

    def handle_collosion(self):
        try:
            for i in range(self.gameinfo.players_num):
                if self.players[i].sprite.alive:
                    if pygame.sprite.spritecollide(self.players[i].sprite, self.obstacle_group, False):
                        # self.players[i].sprite.alive = True
                        self.players[i].sprite.alive = False
                    else:
                        for j in range(self.gameinfo.players_num):
                            if j != i:
                                if pygame.sprite.spritecollide(self.players[i].sprite, self.players[j], False):
                                    self.players[i].sprite.alive = False
                                if pygame.sprite.spritecollide(self.players[i].sprite, self.followers[j], False):
                                    self.players[i].sprite.alive = False
        except Exception as e:
            print(f"Function: handle_collision Error-message: {e}")

    def is_finished(self):
        try:
            players_alive = 0
            last_alive = 0
            for i in range(self.gameinfo.players_num):
                if self.players[i].sprite.alive:
                    players_alive += 1
                    last_alive = i
            if players_alive == 1:
                self.gameinfo.round = False
                self.players[last_alive].sprite.score += 1
                if self.players[last_alive].sprite.score < self.gameinfo.max_score:
                    # print(f"{self.players[last_alive].sprite.name} won the round! Score:"
                    #       f" {self.players[last_alive].sprite.score} Max score: {self.gameinfo.max_score}")
                    self.print_scores()
                    # print(f"playing {self.playing}, round: {self.round}, end: {self.end}, running: {self.running},
                    # menu: {self.main_menu.run_display}")
                else:
                    # print(f"{self.players[last_alive].sprite.name} won the game!")
                    self.print_scores()
                    self.print_winner(last_alive)
                    self.gameinfo.end = True
                    # self.end_game()
            if players_alive == 0:
                self.gameinfo.round = False
                self.print_scores()
        except Exception as e:
            print(f"Function: is_finished Error-message: {e}")

    def client_finished_round(self):
        try:
            players_alive = 0
            last_alive = 0
            for i in range(self.gameinfo.players_num):
                if self.players[i].sprite.alive:
                    players_alive += 1
                    last_alive = i
            if players_alive == 1:
                # self.round = False
                # self.players[last_alive].sprite.score += 1

                if self.players[last_alive].sprite.score < self.gameinfo.max_score:
                    # print(f"{self.players[last_alive].sprite.name} won the round! Score: "
                    #       f"{self.players[last_alive].sprite.score} Max score: {self.gameinfo.max_score}")
                    self.print_scores()
                    # print(f"playing {self.playing}, round: {self.round}, end: {self.end}, running: {self.running},
                    # menu: {self.main_menu.run_display}")
                else:
                    # print(f"{self.players[last_alive].sprite.name} won the game!")
                    self.print_scores()
                    self.print_winner(last_alive)
                    # self.end_game()
            if players_alive == 0:
                # self.round = False
                self.print_scores()
        except Exception as e:
            print(f"Function: client_finished_round Error-message: {e}")

    def next_round(self):
        self.obstacle_group.empty()
        self.obstacle_group.draw(self.graphics.screen)
        for i in range(self.gameinfo.players_num):
            self.players[i].sprite.alive = True
            self.players[i].sprite.x = randint(0, self.graphics.width)
            self.players[i].sprite.y = randint(0, self.graphics.height)
            self.players[i].sprite.real_x = self.players[i].sprite.x
            self.players[i].sprite.real_y = self.players[i].sprite.y
            self.players[i].sprite.f1_x = 2000
            self.players[i].sprite.f1_y = 2000
            self.players[i].sprite.f2_x = 3000
            self.players[i].sprite.f2_y = 3000
            self.players[i].update()
            self.followers[i].update(self.players[i].sprite.x, self.players[i].sprite.y)
        if not self.client:
            self.gameinfo.round = True

    def client_next_round(self):
        self.obstacle_group.empty()
        self.obstacle_group.draw(self.graphics.screen)
        for i in range(self.gameinfo.players_num):
            self.players[i].sprite.alive = True
            self.players[i].sprite.x = 4000
            self.players[i].sprite.y = 4000
            self.players[i].sprite.real_x = self.players[i].sprite.x
            self.players[i].sprite.real_y = self.players[i].sprite.y
            self.players[i].sprite.f1_x = 2000
            self.players[i].sprite.f1_y = 2000
            self.players[i].sprite.f2_x = 3000
            self.players[i].sprite.f2_y = 3000
            self.players[i].update()
            self.followers[i].update(self.players[i].sprite.x, self.players[i].sprite.y)
        if not self.client:
            self.gameinfo.round = True

    def print_scores(self):
        font = pygame.font.SysFont('arial', 30, True)
        pos = 0
        for i in range(self.gameinfo.players_num):
            text = font.render(f"{self.players[i].sprite.name} score:   {self.players[i].sprite.score}", 1, COLORS[i])
            pos += 30
            self.graphics.screen.blit(text, ((self.graphics.width / 2) - 100, pos))

    def print_winner(self, winner):
        font = pygame.font.SysFont('arial', 50, True)
        text_surface = font.render(f"{self.players[winner].sprite.name} won the game!", 1, COLORS[winner])
        pos = 500
        text_rect = text_surface.get_rect()
        text_rect.center = (self.graphics.width/2, pos)
        self.graphics.screen.blit(text_surface, text_rect)

    def save_points(self):
        with open("points.json", "r") as f:
            data = json.load(f)
        f.close()
        for i in range(self.gameinfo.players_num):
            found = False
            for player in data['players']:
                if self.players[i].sprite.name in player['name']:
                    found = True
                    player['points'] += self.players[i].sprite.score
                    player['last_points'] = self.players[i].sprite.score
            if not found:
                new_player = {
                    "name": self.players[i].sprite.name,
                    "points": self.players[i].sprite.score,
                    "last_points": self.players[i].sprite.score
                }
                data['players'].append(new_player)
        # print(data)
        data['players'].sort(key=lambda d: d['points'], reverse=True)
        print(data['players'])
        with open("points.json", "w") as f:
            json.dump(data, f, indent=4)
        f.close()

    def event_handler(self):
        self.reset_keys()
        self.mouse_moved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == self.gameinfo.gap_timer:
                self.gameinfo.gap = not self.gameinfo.gap
                self.all_visible(self.gameinfo.gap)
                if self.gameinfo.playing:
                    if self.gameinfo.gap_size > 0 and self.gameinfo.gap_delay > 0:
                        speed_rate = int((1 - (self.gameinfo.speed/100)) * 100)
                        if self.gameinfo.gap:
                            pygame.time.set_timer(self.gameinfo.gap_timer, (self.gameinfo.gap_size * speed_rate)+40)
                        else:
                            pygame.time.set_timer(self.gameinfo.gap_timer, self.gameinfo.gap_delay * speed_rate * 10)

            if event.type == pygame.KEYDOWN:
                if self.text_typing:
                    if event.key == pygame.K_BACKSPACE:
                        self.text_input = self.text_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.text_typing = False
                    else:
                        self.text_input += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.ESC_KEY = True
                    if event.key == pygame.K_RETURN:
                        self.START_KEY = True
                    if event.key == pygame.K_BACKSPACE:
                        self.BACK_KEY = True
                    if event.key == pygame.K_DOWN:
                        self.DOWN_KEY = True
                    if event.key == pygame.K_UP:
                        self.UP_KEY = True
                    if event.key == pygame.K_SPACE:
                        self.SPACE_KEY = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = event.pos
                self.mouse_buttons = pygame.mouse.get_pressed()

            if pygame.MOUSEMOTION:
                self.mouse_moved = True
        self.keys = pygame.key.get_pressed()

    def client_event_handler(self):
        self.reset_keys()
        self.mouse_moved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if event.type == self.gameinfo.gap_timer:
            #     self.gap_test = not self.gap_test
            #     if self.gameinfo.playing:
            #         if self.gameinfo.gap_size > 0 and self.gameinfo.gap_delay > 0:
            #             speed_rate = int((1 - (self.gameinfo.speed/100)) * 100)
            #             if self.gap_test:
            #                 pygame.time.set_timer(self.gameinfo.gap_timer, (self.gameinfo.gap_size * speed_rate)+40)
            #             else:
            #                 pygame.time.set_timer(self.gameinfo.gap_timer, self.gameinfo.gap_delay * speed_rate * 10)

            if event.type == pygame.KEYDOWN:
                if self.text_typing:
                    if event.key == pygame.K_BACKSPACE:
                        self.text_input = self.text_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.text_typing = False
                    else:
                        self.text_input += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE:
                        self.ESC_KEY = True
                    if event.key == pygame.K_RETURN:
                        self.START_KEY = True
                    if event.key == pygame.K_BACKSPACE:
                        self.BACK_KEY = True
                    if event.key == pygame.K_DOWN:
                        self.DOWN_KEY = True
                    if event.key == pygame.K_UP:
                        self.UP_KEY = True
                    if event.key == pygame.K_SPACE:
                        self.SPACE_KEY = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pos = event.pos
                self.mouse_buttons = pygame.mouse.get_pressed()

            if pygame.MOUSEMOTION:
                self.mouse_moved = True
        self.keys = pygame.key.get_pressed()

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY, self.SPACE_KEY = False, False, False,\
                                                                                                  False, False, False
        self.mouse_pos = tuple()
        self.mouse_buttons = tuple()

    def unload_gameinfo(self):
        try:
            for i, player in enumerate(self.players):
                player.sprite.x = self.gameinfo.mp_players[i].x
                player.sprite.y = self.gameinfo.mp_players[i].y
                player.sprite.score = self.gameinfo.mp_players[i].score
                player.sprite.name = self.gameinfo.mp_players[i].name
                player.sprite.ready = self.gameinfo.mp_players[i].ready
                player.sprite.alive = self.gameinfo.mp_players[i].alive
                player.sprite.visible = self.gameinfo.mp_players[i].visible
                player.sprite.timestamp = self.gameinfo.mp_players[i].timestamp
                # player.update()
                self.followers[i].update(player.sprite.f1_x, player.sprite.f1_y)

        except Exception as e:
            print(f"Function: unload_gameinfo Error-message: {e}")

    def client_input(self):
        self.client_controls[0] = False
        self.client_controls[1] = False
        self.client_controls[2] = False
        self.client_controls[3] = self.gameinfo.timestamp
        if self.SPACE_KEY:
            self.client_controls[2] = True
        if self.keys[KEYS[0][0]]:
            self.client_controls[0] = True
            self.client_controls[1] = False
        if self.keys[KEYS[0][1]]:
            self.client_controls[0] = False
            self.client_controls[1] = True

    def sp_game_loop(self):
        self.gameinfo.playing = True
        self.gameinfo.round = True
        self.gameinfo.end = False
        self.clock.tick(self.gameinfo.speed)

        pygame.time.set_timer(self.gameinfo.gap_timer, self.gameinfo.gap_delay)
        while self.gameinfo.playing:  # game is on
            self.clock.tick(self.gameinfo.speed)
            self.graphics.debug.debug('asd', 2)
            self.graphics.debug.debug(f'round: {self.gameinfo.round}, playing: {self.gameinfo.playing}, end: {self.gameinfo.end}', 1)

            self.event_handler()
            if not self.gameinfo.end:
                if self.gameinfo.round:
                    self.graphics.screen.fill('black')
                    self.draw_all()
                    self.handle_collosion()
                    self.is_finished()
                    if self.ESC_KEY or self.BACK_KEY:
                        self.end_game()
                else:
                    if self.ESC_KEY or self.BACK_KEY:
                        self.end_game()
                    if self.SPACE_KEY:
                        self.next_round()
            else:
                if self.ESC_KEY or self.BACK_KEY or self.SPACE_KEY:
                    self.end_game()
                    self.gameinfo.playing = False
                    self.curr_menu.menu_loop()
            self.graphics.update()

    def mp_server_game_loop(self): # working game loop
        pygame.time.delay(1000)
        self.gameinfo.playing = True
        self.gameinfo.round = True
        self.gameinfo.end = False
        self.clock.tick(self.gameinfo.speed)
        for i in range(self.gameinfo.bot_num, self.gameinfo.players_num, 1):
            self.players[i].sprite.ready = False
        pygame.time.set_timer(self.gameinfo.gap_timer, self.gameinfo.gap_delay)
        while self.gameinfo.playing:  # game is on
            self.clock.tick(self.gameinfo.speed)
            self.event_handler()
            if not self.gameinfo.end:
                if self.gameinfo.round:
                    self.graphics.screen.fill('black')
                    self.draw_all()
                    self.handle_collosion()
                    self.is_finished()

                    for i in range(self.gameinfo.bot_num, self.gameinfo.players_num, 1):
                        self.graphics.debug.debug(self.players[i].sprite.client_move, i)
                        # print(f"{i}: {self.players[i].sprite.ready}")
                        self.players[i].sprite.ready = False
                    if self.ESC_KEY or self.BACK_KEY:
                        self.end_game()
                else:
                    if self.ESC_KEY or self.BACK_KEY:
                        self.end_game()
                    if self.SPACE_KEY:
                        self.players[self.gameinfo.bot_num].sprite.ready = True
                    if self.all_ready():
                        for i in range(self.gameinfo.bot_num, self.gameinfo.players_num, 1):
                            self.players[i].sprite.ready = False
                        self.next_round()

            else:
                if self.ESC_KEY or self.BACK_KEY or self.SPACE_KEY:
                    self.end_game()
                    self.gameinfo.playing = False
                    self.curr_menu.menu_loop()
            self.graphics.update()

    def mp_client_game_loop(self):
        # pygame.time.set_timer(self.gameinfo.gap_timer, self.gameinfo.gap_delay)
        self.client = True
        self.clock.tick(self.gameinfo.speed)
        self.client_controls[2] = False

        while True:  # game is on
            self.clock.tick(self.gameinfo.speed)
            self.client_event_handler()
            self.client_input()
            self.graphics.debug.debug(self.client_controls, 1)
            if not self.gameinfo.end:
                if self.gameinfo.round:
                    self.graphics.screen.fill('black')
                    # self.client_draw_all()
                    self.draw_all()

                    if self.ESC_KEY or self.BACK_KEY:
                        self.end_game()
                        # self.n.disconnect_server()
                else:
                    if self.ESC_KEY or self.BACK_KEY:
                        self.end_game()
                        # self.n.disconnect_server()
                    self.client_finished_round()
                    self.client_next_round()
                    # self.print_scores()
            else:
                self.client_finished_round()
                if self.ESC_KEY or self.BACK_KEY or self.SPACE_KEY:
                    self.end_game()
                    # self.n.disconnect_server()
                    self.curr_menu.menu_loop()
                    break
            self.graphics.update()

