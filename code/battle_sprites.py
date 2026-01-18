from timer import Timer
from pygame import sprite
from settings import *

class Paddle(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.Surface(SIZE['paddle'])
        self.rect = self.image.get_frect()
        self.speed = SPEED['paddle']

        #timers
        self.action_cooldown_timer = Timer(COOLDOWN['paddle'])

        self.attack_forward_timer = Timer(DURATIONS['paddle_attack'], func=self.activate_attack_back_timer)
        self.attack_back_timer = Timer(DURATIONS['paddle_attack'])

        self.slide_timer = Timer(DURATIONS['paddle_slide'])

        self.slide_direction = 1
        self.old_rect = self.rect.copy()

    def update(self, dt):
        #updating timers
        self.action_cooldown_timer.update()
        self.attack_back_timer.update()
        self.attack_forward_timer.update()
        self.slide_timer.update()

        self.keys = pygame.key.get_pressed()
        self.old_rect = self.rect.copy()

        #prevents movement and consecutive actions while in action
        if not self.attack_forward_timer and not self.attack_back_timer and not self.slide_timer:
            self.move(dt)
            self.try_to_act()
        self.update_color()
        self.attack(dt)
        self.slide(dt)

    def update_color(self):
        if self.slide_timer:
            self.image.fill(COLORS['paddle_slide'])
        elif self.action_cooldown_timer:
            self.image.fill(COLORS['paddle_cooldown'])
        else:
            self.image.fill(COLORS['paddle_active'])

    def attack(self, dt):
        if self.attack_forward_timer:
            self.rect.centerx += self.speed * dt * self.direction * SPEED_BOOST['attack']
        elif self.attack_back_timer:
            self.rect.centerx -= self.speed * dt * self.direction * SPEED_BOOST['attack']

    def slide(self, dt):
        if self.slide_timer:
            if self.rect.top > 0 and self.rect.bottom < WINDOW_HEIGHT:
                self.rect.centery += self.speed * dt * self.slide_direction * SPEED_BOOST['slide']

    def activate_attack_back_timer(self):
        self.attack_back_timer.activate()

    def reset(self):
        self.speed = SPEED['paddle']
        self.rect = self.image.get_frect(center=(POS[self.paddle_side]))
        self.action_cooldown_timer.deactivate()

class LeftPaddle(Paddle):
    def __init__(self, groups):
        super().__init__(groups)
        self.base_x = POS['left_paddle'][0]
        self.rect = self.image.get_frect(center=(POS['left_paddle']))
        self.direction = 1

    def move(self, dt):
        if self.keys[pygame.K_w]:
            if self.rect.top > BATTLE_AREA_TOP:
                self.rect.centery -= self.speed * dt
                self.slide_direction = -1
        if self.keys[pygame.K_s]:
            if self.rect.bottom < BATTLE_AREA_BOTTOM:
                self.rect.centery += self.speed * dt
                self.slide_direction = 1

    def try_to_act(self):
        if self.keys[pygame.K_d] and not self.action_cooldown_timer:
            self.action_cooldown_timer.activate()
            self.attack_forward_timer.activate()
        if self.keys[pygame.K_q] and not self.action_cooldown_timer:
            self.action_cooldown_timer.activate()
            self.slide_timer.activate()

class PlayerPaddle(LeftPaddle):
    def __init__(self, groups, player):
        super().__init__(groups)
        self.sync_stats(player)
        self.rect = self.image.get_frect(center=(POS['player_paddle']))
        self.base_x = POS['player_paddle'][0]

    def sync_stats(self, player):
        self.image = pygame.Surface((SIZE['paddle'][0], SIZE['paddle'][1] + (player.stats['size'] * 25)))
        self.speed = SPEED['paddle'] + (player.stats['agility'] * 100)

    def slide(self, dt):
        if self.slide_timer:
            if self.rect.top > BATTLE_AREA_TOP and self.rect.bottom < BATTLE_AREA_BOTTOM:
                self.rect.centery += self.speed * dt * self.slide_direction * SPEED_BOOST['slide']

class RightPaddle(Paddle):
    def __init__(self, groups):
        super().__init__(groups)
        self.base_x = POS['right_paddle'][0]
        self.rect = self.image.get_frect(center=(POS['right_paddle']))
        self.direction = -1

    def move(self, dt):
        if self.keys[pygame.K_UP]:
            if self.rect.top > 0:
                self.rect.centery -= self.speed * dt
                self.slide_direction = -1
        if self.keys[pygame.K_DOWN]:
            if self.rect.bottom < WINDOW_HEIGHT:
                self.rect.centery += self.speed * dt
                self.slide_direction = 1

    def try_to_act(self):
        if self.keys[pygame.K_LEFT] and not self.action_cooldown_timer:
            self.action_cooldown_timer.activate()
            self.attack_forward_timer.activate()
        if self.keys[pygame.K_RIGHT] and not self.action_cooldown_timer:
            self.slide_timer.activate()

class AiRightPaddle(RightPaddle):
    def __init__(self,groups,ball, enemy_name):
        super().__init__(groups)
        self.enemy_stats = BATTLE_STATS.get(enemy_name, 'Default')
        self.image = pygame.Surface(self.enemy_stats['paddle_size'])
        self.rect = self.image.get_frect()
        self.old_rect = self.rect.copy()
        self.ball = ball
        self.speed = SPEED['ai_paddle']
        self.error_rate = ERROR_RATE['big']
        self.decision_timer = Timer(COOLDOWN['ai_paddle_decision'])

    def calculate_move(self, value):
        number = random.randrange(0,10)
        if number < self.error_rate * 10:
            return value * -1
        else:
            return value

    def direction_to_ball(self,ball):
        if self.rect.centery - ball.centery > 0:
            return -1
        elif self.rect.centery - ball.centery < 0:
            return 1
        else:
            return 0

    def direction_changed(self):
        if self.direction_to_ball(self.ball.rect) != self.direction_to_ball(self.ball.old_rect):
            return True
        else: return False

    def distance_to_ball(self):
        return self.rect.centery - self.ball.rect.centery

    def speed_modifier_based_on_distance_to_ball(self):
        return abs(self.distance_to_ball()) / (WINDOW_HEIGHT / 4) * (
                    self.ball.vector.x / (SPEED_LIMIT['ball'].x / 2))

    def dampen_value(self, value):
        if value < 0.1:
            return value * self.enemy_stats['low_speed_multiplier']
        elif value < 0.5:
            return value * self.enemy_stats['medium_speed_multiplier']
        else:
            return value * self.enemy_stats['high_speed_multiplier']

    def update(self,dt):
        super().update(dt)
        self.decision_timer.update()

    def cap_speed(self, value, dt):
        if value > (self.enemy_stats['speed'] * dt):
            return float(self.enemy_stats['speed'] * dt)
        else: return value

    def move(self,dt):
        if not self.decision_timer or self.direction_changed():
            self.movement_direction = self.calculate_move(self.direction_to_ball(self.ball.rect))
            self.decision_timer.activate()
        if self.movement_direction == 1 and self.rect.bottom < WINDOW_HEIGHT:
            self.slide_direction = 1
            self.rect.centery += self.cap_speed(self.speed * dt * self.dampen_value(self.speed_modifier_based_on_distance_to_ball()),dt)
        elif self.movement_direction == -1 and self.rect.top > 0:
            self.slide_direction = -1
            self.rect.centery -= self.cap_speed(self.speed * dt * self.dampen_value(self.speed_modifier_based_on_distance_to_ball()),dt)

    def choose_action(self):
        x = random.randrange(0,self.enemy_stats['nothing'])
        if x in range(0,self.enemy_stats['attack']):
            self.action_cooldown_timer.activate()
            self.attack_forward_timer.activate()
        elif x in range(self.enemy_stats['attack'],self.enemy_stats['slide']):
            self.action_cooldown_timer.activate()
            self.slide_timer.activate()
        else:
            self.action_cooldown_timer.activate()

    def try_to_act(self):
        if self.ball.rect.right > self.rect.centerx - 100 and not self.action_cooldown_timer:
            if abs(self.distance_to_ball()) > self.rect.height / 2:
                self.choose_action()
            else:
                self.choose_action()

class EnemyPaddle(AiRightPaddle):
    def __init__(self,groups,ball,enemy_name):
        super().__init__(groups, ball, enemy_name)
        self.base_x = POS['enemy_paddle'][0]
        self.rect = self.image.get_frect(center=(POS['enemy_paddle']))


    def move(self,dt):
        if not self.decision_timer or self.direction_changed():
            self.movement_direction = self.calculate_move(self.direction_to_ball(self.ball.rect))
            self.decision_timer.activate()
        if self.movement_direction == 1 and self.rect.bottom < BATTLE_AREA_BOTTOM:
            self.slide_direction = 1
            self.rect.centery += self.cap_speed(self.speed * dt * self.dampen_value(self.speed_modifier_based_on_distance_to_ball()),dt)
        elif self.movement_direction == -1 and self.rect.top > BATTLE_AREA_TOP:
            self.slide_direction = -1
            self.rect.centery -= self.cap_speed(self.speed * dt * self.dampen_value(self.speed_modifier_based_on_distance_to_ball()),dt)

    def slide(self, dt):
        if self.slide_timer:
            if self.rect.top > 0 and self.rect.bottom < WINDOW_HEIGHT:
                self.rect.centery += self.speed * dt * self.slide_direction * SPEED_BOOST['slide']

class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, paddle_sprites, update_stats, music_manager):
        super().__init__(groups)
        self.paddle_sprites = paddle_sprites
        self.update_stats = update_stats
        self.music_manager = music_manager

        self.image = pygame.Surface(SIZE['ball'], pygame.SRCALPHA)
        self.rect = self.image.get_frect(center=(POS['ball']))
        self.color = COLORS['ball']

        self.direction = random.choice([1, -1])
        self.base_speed = SPEED['ball']
        self.vector = pygame.Vector2(self.base_speed, 0)
        self.curve_amount = 0
        self.speed_limit = SPEED_LIMIT['ball']
        self.old_rect = self.rect.copy()

    def calculate_color(self,ball_color, value, index):
        if type(index) == int:
            color = ball_color[index] + value
            if color < 0:
                color = 0
            elif color > 255:
                color = 255
            ball_color[index] = color
            return ball_color
        for i in index:
            color = ball_color[i] + value
            if color < 0:
                color = 0
            elif color > 255:
                color = 255
            ball_color[i] = color
        return ball_color

    def calculate_point_of_contact(self, paddle):
        point_of_contact = paddle.rect.centery - self.rect.centery
        if point_of_contact < -80:
            point_of_contact = -80
        if point_of_contact > 80:
            point_of_contact = 80
        return point_of_contact * -1

    def speed_check(self):
        if self.vector.y > self.speed_limit.y:
            self.vector.y = self.speed_limit.y
        elif self.vector.y < -self.speed_limit.y:
            self.vector.y = -self.speed_limit.y
        if self.vector.x > self.speed_limit.x:
            self.vector.x = self.speed_limit.x

    def change_color(self):
        for i in range(0,3):
            if self.color[i] != 255:
                self.color[i] += 1

    def bounce_and_score(self):
        if self.rect.top < 0 and self.vector.y < 0:
            self.vector.y *= -1
        elif self.rect.bottom > WINDOW_HEIGHT and self.vector.y > 0:
            self.vector.y *= -1

        if self.rect.left < 0:
            self.update_stats('left')
            self.reset()
        elif self.rect.right > WINDOW_WIDTH:
            self.update_stats('right')
            self.reset()

    def move(self,dt):
        self.rect.centerx += self.vector.x * dt * self.direction
        self.collision('horizontal')
        self.rect.centery += self.vector.y * dt
        self.collision('vertical')

    def apply_curve_amount(self,dt):
        self.vector.y += self.curve_amount * dt * 5
        if self.curve_amount > 0:
            self.curve_amount -= dt * 40
        elif self.curve_amount < 0:
            self.curve_amount += dt * 40

    def update(self, dt):
        self.old_rect = self.rect.copy()

        self.apply_curve_amount(dt)
        self.move(dt)
        self.bounce_and_score()
        self.speed_check()

        self.draw_circle()

        if self.color != [0,0,0]:
            self.change_color()

    def strong_bounce(self, paddle):
        self.calculate_color(self.color, -220, (1, 2))
        self.direction *= -1
        self.vector.x += 150
        self.vector.y += self.calculate_point_of_contact(paddle) * 5

    def weak_bounce(self, paddle):
        self.calculate_color(self.color, -80, (1, 2))
        self.direction *= -1
        self.vector.x -= 100
        self.vector.y += self.calculate_point_of_contact(paddle) * 5

    def curve_bounce(self, paddle):
        self.calculate_color(self.color, -220, (2))
        self.direction *= -1
        self.vector.x += 100
        self.vector.y += self.calculate_point_of_contact(paddle) * 2
        if paddle.slide_direction == 1:
            self.curve_amount = random.randint(200,300)
        else:
            self.curve_amount = -random.randint(200,300)

    def chose_bounce(self,sprite):
        if sprite in self.paddle_sprites:
            if sprite.attack_forward_timer:
                self.strong_bounce(sprite)
            elif sprite.slide_timer:
                self.curve_bounce(sprite)
            else:
                self.weak_bounce(sprite)
        else:
            self.weak_bounce(sprite)

    def collision(self, direction):
        for sprite in self.paddle_sprites:
            if sprite.rect.colliderect(self.rect):
                self.music_manager.play_sound('ball_hit')
                if direction == "horizontal":
                    if self.rect.right > sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                        self.chose_bounce(sprite)
                    else:
                        self.rect.left = sprite.rect.right
                        self.chose_bounce(sprite)
                elif direction == "vertical":
                    if self.rect.top > sprite.rect.bottom and self.old_rect.top <= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        self.vector.y *= -1
                    else:
                        self.rect.bottom = sprite.rect.top
                        self.vector.y *= -1

    def draw_circle(self):
        pygame.draw.circle(self.image, self.color, (SIZE['ball'][0] / 2, SIZE['ball'][1] / 2), SIZE['ball'][0] / 2)

    def reset(self):
        self.music_manager.play_sound('health_lost')
        self.rect = self.image.get_frect(center = (POS['ball']))
        self.direction = random.choice([1, -1])

        self.vector = pygame.Vector2(self.base_speed, 0)
        self.curve_amount = 0
        self.direction = random.choice([1, -1])
        self.color = COLORS['ball']

class BattleBall(Ball):
    def __init__(self, groups, paddle_sprites, update_stats, music_manager):
        super().__init__(groups, paddle_sprites, update_stats, music_manager)

    def bounce_and_score(self):
        if self.rect.top < BATTLE_AREA_TOP and self.vector.y < 0:
            self.vector.y *= -1
        elif self.rect.bottom > BATTLE_AREA_BOTTOM and self.vector.y > 0:
            self.vector.y *= -1

        if self.rect.left < BATTLE_AREA_LEFT:
            self.update_stats('left')
            self.reset()
        elif self.rect.right > BATTLE_AREA_RIGHT:
            self.update_stats('right')
            self.reset()
