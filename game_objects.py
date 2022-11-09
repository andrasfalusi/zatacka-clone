import pygame
import math
from random import randint
import time

COLORS = 'white', 'green', 'yellow', 'purple', 'red', 'blue'
KEYS = (pygame.K_LEFT, pygame.K_RIGHT), (pygame.K_a, pygame.K_s), (pygame.K_n, pygame.K_m), (pygame.K_F1, pygame.K_F2),\
       (pygame.K_KP_PLUS, pygame.K_KP_MINUS), (pygame.K_KP_2, pygame.K_KP_3)


class User(object):
    def __init__(self):
        self.name = "Username"

    def __str__(self):
        print(self.name)


class PlayerInfo(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.name = ""
        self.score = 0
        self.ready = False
        self.alive = True
        self.visible = False
        self.timestamp = 0

    def __str__(self):
        print(f"    +PlayerInfo")
        print(f"        name: {self.name}")
        print(f"        x: {self.x}")
        print(f"        y: {self.y}")
        print(f"        score: {self.score}")
        print(f"        ready: {self.ready}")
        print(f"        alive: {self.alive}")
        print(f"        visible: {self.visible}")
        print(f"        timestamp: {self.timestamp}")
        return ""

    def update(self, x, y, name, score, ready, alive, visible, timestamp):
        self.x = x
        self.y = y
        self.name = name
        self.score = score
        self.ready = ready
        self.alive = alive
        self.visible = visible
        self.timestamp = timestamp


class GameInfo(object):
    def __init__(self):
        # self.username = "Username"
        self.user_num = -1
        self.players_num = 2
        self.max_player = 6
        self.max_score = 2
        self.speed = 40
        self.gap_size = 3
        self.gap_delay = 7
        self.gap_timer = pygame.USEREVENT + 1
        self.gap = False
        self.bot_num = 0
        # Game status infos
        self.playing = False
        self.end = False
        self.round = False
        self.timestamp = 0
        self.mp_players = []
        for i in range(6):
            self.mp_players.append(PlayerInfo())

    def __str__(self):
        print(f"+GameInfo")
        print(f"    user_num: {self.user_num}")
        print(f"    players_num: {self.players_num}")
        print(f"    max_player: {self.max_player}")
        print(f"    max_score: {self.max_score}")
        print(f"    speed: {self.speed}")
        print(f"    gap_size: {self.gap_size}")
        print(f"    gap_delay{self.gap_delay}")
        print(f"    gap_timer: {self.gap_timer}")
        print(f"    gap: {self.gap}")
        print(f"    bot_num: {self.bot_num}")
        print(f"    playing: {self.playing}")
        print(f"    end: {self.end}")
        print(f"    round: {self.round}")
        print(f"    timestamp: {self.timestamp}\n")
        for idx, player in enumerate(self.mp_players):
            print(f"    {idx}. ")
            print(player)
        return ""

    def update(self, user_num, players):
        self.user_num = user_num
        for idx, player in enumerate(players):
            self.mp_players[idx].update(player.sprite.x, player.sprite.y, player.sprite.name, player.sprite.score,
                                        player.sprite.ready, player.sprite.alive, player.sprite.visible, player.sprite.timestamp)


    def clear_game_status(self):
        self.playing = False
        self.end = False
        self.round = False


class Radar(pygame.sprite.Sprite):
    def __init__(self, s):
        super().__init__()
        self.image = pygame.Surface((s, s), pygame.SRCALPHA)
        # self.image = pygame.Surface((140, 140))
        self.image.fill('white')
        self.x = 0
        self.y = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.rect.center = (self.x, self.y)

class Player(pygame.sprite.Sprite):
    def __init__(self, player_num, game):
        super().__init__()
        self.game = game
        self.name = f"Player {player_num+1}"
        self.player_num = player_num
        if self.player_num+1 <= self.game.gameinfo.bot_num:
            self.name = f"Bot {self.player_num+1}"
            self.bot = True
            self.radar_far = pygame.sprite.GroupSingle(Radar(140))
            self.radar_near = pygame.sprite.GroupSingle(Radar(50))
            self.ready = True
        else:
            self.bot = False
            self.ready = False
        self.alive = True
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        self.speed = 2
        self.rotation_speed = 6
        self.angle = randint(0, 360)
        self.direction = False
        self.former_warning = False
        self.x = randint(0, self.game.graphics.width)
        self.y = randint(0, self.game.graphics.height)
        self.visible = False
        self.real_x = self.x
        self.real_y = self.y
        self.f1_x, self.f1_y = 0, 0
        self.f2_x, self.f2_y = 0, 0
        self.score = 0
        self.color = COLORS[player_num]
        pygame.draw.circle(self.image, self.color, (2, 2), 2)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
        self.timestamp = 0
        self.client_move = [False, False]

    # def set_pos(self, x, y):
    #     self.x = x
    #     self.y = y

    def update(self, move=True):
        if self.bot:
            # print("update bot")
            self.bot_avoid_collision()
            self.radar_near.update(self.x, self.y)
            self.radar_far.update(self.x, self.y)
        else:
            # print("update player")
            self.player_input()
        self.f2_x = self.f1_x
        self.f2_y = self.f1_y
        self.f1_x = self.x
        self.f1_y = self.y
        if move:
            self.move()
        # self.rect.center = (int(self.x), int(self.y))
        self.rect.center = (self.x, self.y)

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.speed
        horizontal = math.sin(radians) * self.speed
        self.real_y -= vertical
        self.real_x -= horizontal

        if self.real_x < 0:
            self.real_x = self.game.graphics.width
        elif self.real_x > self.game.graphics.width:
            self.real_x = 0
        if self.real_y < 0:
            self.real_y = self.game.graphics.height
        elif self.real_y > self.game.graphics.height:
            self.real_y = 0
        self.x = round(self.real_x)
        self.y = round(self.real_y)

    def player_input(self):
        if not self.game.client:
            if self.game.keys[KEYS[self.player_num][0]]:
                self.rotate(True, False)
            if self.game.keys[KEYS[self.player_num][1]]:
                self.rotate(False, True)
            if self.client_move[0]:
                self.rotate(True, False)
            if self.client_move[1]:
                self.rotate(False, True)

    def bot_avoid_collision(self):
        # print("avoid")
        self.predict_path()

    def predict_path(self):
        warning = False
        self.direction = 0
        vision_range = 70
        vision_angle_wide = 55
        vision_angle_narrow = 15

        try:
            detected = pygame.sprite.spritecollide(self.radar_far.sprite, self.game.obstacle_group, False)
            # print(f"{self.player_num} detected {len(detected)}")
            if len(detected) >= 100:
                detected = pygame.sprite.spritecollide(self.radar_near.sprite, self.game.obstacle_group, False)
                # print(f"{self.player_num} detected near {len(detected)}")
            radians_mid = math.radians(self.angle)
            radians_right_wide = math.radians(self.angle + vision_angle_wide)
            radians_right_narrow = math.radians(self.angle + vision_angle_narrow)
            radians_left_wide = math.radians(self.angle - vision_angle_wide)
            radians_left_narrow = math.radians(self.angle - vision_angle_narrow)
            for i in range(vision_range, 1, -2):
                vertical_right_wide = math.cos(radians_right_wide) * i
                horizontal_right_wide = math.sin(radians_right_wide) * i
                pred_y_right_wide = self.y - vertical_right_wide
                pred_x_right_wide = self.x - horizontal_right_wide

                vertical_left_wide = math.cos(radians_left_wide) * i
                horizontal_left_wide = math.sin(radians_left_wide) * i
                pred_y_left_wide = self.y - vertical_left_wide
                pred_x_left_wide = self.x - horizontal_left_wide

                vertical_right_narrow = math.cos(radians_right_narrow) * i
                horizontal_right_narrow = math.sin(radians_right_narrow) * i
                pred_y_right_narrow = self.y - vertical_right_narrow
                pred_x_right_narrow = self.x - horizontal_right_narrow

                vertical_left_narrow = math.cos(radians_left_narrow) * i
                horizontal_left_narrow = math.sin(radians_left_narrow) * i
                pred_y_left_narrow = self.y - vertical_left_narrow
                pred_x_left_narrow = self.x - horizontal_left_narrow

                vertical_mid = math.cos(radians_mid) * i
                horizontal_mid = math.sin(radians_mid) * i
                pred_y_mid = self.y - vertical_mid
                pred_x_mid = self.x - horizontal_mid

                for obstacle in detected:
                    if (pred_y_right_narrow > obstacle.sprite.y - 2) and (pred_y_right_narrow < obstacle.y + 2) and (
                            pred_x_right_narrow > obstacle.x - 2) and (pred_x_right_narrow < obstacle.x + 2):
                        print(f"{self.player_num}  turn right {i}")
                        self.direction = 1
                        warning = True
                        break
                    print(f"obstacle {obstacle.y}")
                    if (pred_y_left_narrow > obstacle.y - 2) and (pred_y_left_narrow < obstacle.y + 2) and (
                            pred_x_left_narrow > obstacle.x - 2) and (pred_x_left_narrow < obstacle.x + 2):
                        print(f"{self.player_num}  turn left {i}")
                        self.direction = 2
                        warning = True
                        break

                    if (pred_y_right_wide > obstacle.y-2) and (pred_y_right_wide < obstacle.y+2) and \
                            (pred_x_right_wide > obstacle.x-2) and (pred_x_right_wide < obstacle.x+2):
                        print(f"{self.player_num}  turn right {i}")
                        self.direction = 1
                        warning = True
                        break

                    if (pred_y_left_wide > obstacle.y-2) and (pred_y_left_wide < obstacle.y+2) and \
                            (pred_x_left_wide > obstacle.x-2) and (pred_x_left_wide < obstacle.x+2):
                        print(f"{self.player_num}  turn left {i}")
                        self.direction = 2
                        warning = True
                        break

                if warning:
                    if not((pred_y_mid > obstacle.y-2) and (pred_y_mid < obstacle.y+2) and
                           (pred_x_mid > obstacle.x-2) and (pred_x_mid < obstacle.x+2)):
                        self.direction = 3
                    break
        except:
            print("detection error")

        # self.direction = randint(0,1)
        if self.direction == 1:
            # print(f"{self.player_num}  turn right {i}")
            self.rotate(False, True)
        if self.direction == 2:
            # print(f"{self.player_num}  turn left {i}")
            self.rotate(True, False)

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_speed
        elif right:
            self.angle -= self.rotation_speed


class Follower(pygame.sprite.Sprite):
    def __init__(self, player_num):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        # self.image.fill(COLORS[player_num])
        self.x = 0
        self.y = 0
        self.color = COLORS[player_num]
        pygame.draw.circle(self.image, self.color, (2, 2), 2)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, x, y):
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, player_num):
        super().__init__()
        self.color = COLORS[player_num]
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        # self.image = pygame.Surface((4, 4))
        # self.image.fill(self.color)
        self.x = x
        self.y = y

        pygame.draw.circle(self.image, self.color, (2, 2), 2)
        self.rect = self.image.get_rect(center=(self.x, self.y))
