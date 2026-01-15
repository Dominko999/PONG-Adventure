from timer import Timer
from pygame import sprite
from random import randint
from settings import *
from pathlib import Path
from camera import CameraGroup
from animation import AnimatedSprite

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, collision_group, position, world_size, stats):
        super().__init__(groups)

        # stats
        self.stats = stats

        self.exp_cap = self.stats['level'] * 2 + 4
        self.health = 3
        self.agility = 5
        self.size = 4

        self.position = position
        self.change_sprite()
        self.facing_right = True
        self.movement_speed = SPEED['player']
        self.collision_group = collision_group
        self.world_size = world_size

    def add_exp(self, exp):
        self.stats['exp'] += exp

    def level_up(self):
        self.stats['level'] += 1
        self.stats['exp'] -= self.exp_cap
        self.exp_cap += 2
        self.change_sprite()

    def change_sprite(self):
        if self.stats['level'] == 1 or self.stats['level'] == 2:
            self.animated_sprite = AnimatedSprite('fli', 4, (56, 40), 8)
            self.image = self.animated_sprite.image
            self.rect = self.animated_sprite.rect
        elif self.stats['level'] == 3 or self.stats['level'] == 4:
            self.animated_sprite = AnimatedSprite('medium_fli', 4, (60, 56), 8)
            self.image = self.animated_sprite.image
            self.rect = self.animated_sprite.rect
        elif self.stats['level'] >= 5:
            self.animated_sprite = AnimatedSprite('large_fli', 4, (84, 76), 8)
            self.image = self.animated_sprite.image
            self.rect = self.animated_sprite.rect
        self.rect.center = self.position


    def move(self, dt):
        if self.keys[pygame.K_w]:
            if self.rect.top > 0:
                self.rect.centery -= self.movement_speed * dt
                self.collision("vertical")
        if self.keys[pygame.K_s]:
            if self.rect.bottom < self.world_size.y:
                self.rect.centery += self.movement_speed * dt
                self.collision("vertical")
        if self.keys[pygame.K_a]:
            self.facing_right = False
            if self.rect.left > 0:
                self.rect.centerx -= self.movement_speed * dt
                self.collision("horizontal")
        if self.keys[pygame.K_d]:
            self.facing_right = True
            if self.rect.right < self.world_size.x:
                self.rect.centerx += self.movement_speed * dt
                self.collision("horizontal")
        self.position = self.rect.center

    def collision(self, direction):
        for sprite in self.collision_group:
            if sprite.rect.colliderect(self.rect):
                if direction == "horizontal":
                    if self.rect.right > sprite.rect.left and self.old_rect.right <= sprite.rect.left:
                        self.rect.right = sprite.rect.left
                    else:
                        self.rect.left = sprite.rect.right
                elif direction == "vertical":
                    if self.rect.top < sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom:
                        self.rect.top = sprite.rect.bottom
                    else:
                        self.rect.bottom = sprite.rect.top

    def update(self, dt):
        self.image = self.animated_sprite.image
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.animated_sprite.update(dt)

        self.keys = pygame.key.get_pressed()
        self.old_rect = self.rect.copy()
        self.move(dt)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, collision_group, world_size, id):
        super().__init__(groups)

        #self.bounding_box = pygame.Rect(0, 0, self.rect.width * 5, self.rect.height * 5)
        #self.bounding_box.center = (self.rect.centerx, self.rect.centery)

        self.world_size = world_size
        self.collision_group = collision_group

        self.change_direction_timer = Timer(1,self.change_direction, True)
        self.change_direction_timer.activate()
        self.id = id

    def update(self, dt):
        self.change_direction_timer.update()
        self.old_rect = self.rect.copy()
        self.move(dt)

    def change_direction(self):
        print("change direction")
        self.multiplier_x = randint(-1, 1)
        self.multiplier_y = randint(-1, 1)

    def move(self, dt):
        self.rect.centerx += self.speed * dt * self.multiplier_x
        self.collision("horizontal")
        self.rect.centery += self.speed * dt * self.multiplier_y
        self.collision("vertical")

    def collision(self, direction):
        for sprite in self.collision_group:
            if sprite.rect.colliderect(self.rect):
                if direction == "horizontal":
                    if self.rect.right > sprite.rect.left and self.old_rect.right <= sprite.rect.left:
                        self.rect.right = sprite.rect.left
                    else:
                        self.rect.left = sprite.rect.right
                elif direction == "vertical":
                    if self.rect.top < sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom:
                        self.rect.top = sprite.rect.bottom
                    else:
                        self.rect.bottom = sprite.rect.top

        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.world_size[0])
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.world_size[1])

class FlyEnemy(Enemy):
    def __init__(self, groups, collision_group, world_size, position, id):
        super().__init__(groups, collision_group, world_size, id)
        self.name = "Evil fly"
        self.health = 1
        self.exp_gain = 10
        self.animated_sprite = AnimatedSprite('fly', 4, (120, 76), 8)
        self.image = self.animated_sprite.image
        self.rect = self.animated_sprite.rect
        self.rect.center = position
        self.speed = SPEED['fly']
        self.old_rect = self.rect
        self.multiplier_x = 0
        self.multiplier_y = 0

    def update(self, dt):
        super().update(dt)
        self.image = self.animated_sprite.image
        self.animated_sprite.update(dt)

class SpiderlikeEnemy(Enemy):
    def __init__(self, groups, collision_group, world_size, position, id):
        super().__init__(groups, collision_group, world_size, id)
        self.name = "Evil spiderlike creature"
        self.health = 6
        self.exp_gain = 6
        self.animated_sprite = AnimatedSprite('spider', 4, (104, 76), 8)
        self.image = self.animated_sprite.image
        self.rect = self.animated_sprite.rect
        self.rect.center = position
        self.speed = SPEED['spider']
        self.old_rect = self.rect
        self.multiplier_x = 0
        self.multiplier_y = 0

    def update(self, dt):
        super().update(dt)
        self.image = self.animated_sprite.image
        self.animated_sprite.update(dt)

class BeetleEnemy(Enemy):
    def __init__(self, groups, collision_group, world_size, position, id):
        super().__init__(groups, collision_group, world_size, id)
        self.name = "Evil very big beetle"
        self.health = 14
        self.exp_gain = 12
        self.animated_sprite = AnimatedSprite('beetle', 2, (88, 124), 4)
        self.image = self.animated_sprite.image
        self.rect = self.animated_sprite.rect
        self.rect.center = position
        self.speed = SPEED['beetle']
        self.old_rect = self.rect
        self.multiplier_x = 0
        self.multiplier_y = 0

    def update(self, dt):
        super().update(dt)
        self.image = self.animated_sprite.image
        self.animated_sprite.update(dt)

class NPC(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)


    def advance_dialogue(self):
        self.times_talked += 1
        self.times_talked = min(self.times_talked,len(self.all_dialogue)-1)
        self.dialogue = self.all_dialogue[self.times_talked]

class OldCreatureNPC(NPC):
    def __init__(self, groups, position):
        super().__init__(groups)
        self.animated_sprite = AnimatedSprite('old_creature', 4, (128, 112), 4)
        self.image = self.animated_sprite.image
        self.rect = self.animated_sprite.rect
        self.rect.center = position

        self.name = "Old creature"

        self.times_talked = 0

        self.all_dialogue = [
            ['Hello there small fly',
            'What are you doing here?',
            'You know you are on the verge of world known to bugkind',
            'If you proceed further, you can lose yourself',
            'It is my task to stop you from doing that',
            'So i hope you will listen to me and turn back',
             'Will you?'],
            ['Why are you still here?',
             'Turn back while you still can',
             'Otherwise the VERY BIG BEETLE will eat you up'],
            ['Are you ignoring my advice?',
             'THEN I WILL EAT YOU UP',
             '...',
             'Do not worry, I was just kidding',
             'The developer is too stupid to code something like that']
        ]

        self.dialogue = self.all_dialogue[self.times_talked]

    def update(self, dt):
        super().update(dt)
        self.image = self.animated_sprite.image
        self.animated_sprite.update(dt)

class OldBeetleNPC(NPC):
    def __init__(self, groups, position):
        super().__init__(groups)
        self.animated_sprite = AnimatedSprite('old_beetle', 3, (128, 112), 4)
        self.image = self.animated_sprite.image
        self.rect = self.animated_sprite.rect
        self.rect.center = position

        self.name = "Old beetle"

        self.all_dialogue = [
            ['Hey you!',
            'Can you understand me?',
            'Yes? Then turn back immediately!',
            'In the next room there is a VERY BIG BEETLE',
            'It has like 14 health points',
             'And you can not go further if you do not kill it'],
            ['Hey! Are not going to listen to me?',
             'Are you insane',
             'Turn back right now!'],
            ['...',
             'You know what?',
             'If you are so eager to die, then let me tell a secret',
             '...',
             'The VERY BIG BEETLE is big, but also very slow',
             'Hit the ball with top or bottom edges of your paddle and see what happens',
             'Also try using the D key',
             'Good luck']
        ]

        self.times_talked = 0

        self.dialogue = self.all_dialogue[self.times_talked]

    def update(self, dt):
        super().update(dt)
        self.image = self.animated_sprite.image
        self.animated_sprite.update(dt)


class InteractableObject(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        # self.bounding_box = pygame.Rect(0, 0, self.rect.width * 5, self.rect.height * 5)
        # self.bounding_box.center = (self.rect.centerx, self.rect.centery)

class OldScripture(InteractableObject):
    def __init__(self, groups, position):
        super().__init__(groups)
        self.animated_sprite = AnimatedSprite('old_scripture', 1, (60, 44), 0)
        self.image = self.animated_sprite.image
        self.rect = self.animated_sprite.rect
        self.rect.center = position

        self.text = [
            'You picked up the old scripture',
            'That is it, you finished the game',
            'Thank you for playing',
            'Have a nice day',
            'Goodbye'
        ]

class LightBulb(InteractableObject):

    def __init__(self, groups, position):
        super().__init__(groups)
        self.animated_sprite = AnimatedSprite('lightbulb', 1, (96, 96), 0)
        self.image = self.animated_sprite.image
        self.rect = self.animated_sprite.rect
        self.rect.center = position
        self.checkpoint_name = 'Anicient ruins'

        self.text = [
            'Game saved'
        ]

class BlockedDoor(pygame.sprite.Sprite):
    def __init__(self, groups, position, enemy):
        super().__init__(groups)
        self.animated_sprite = AnimatedSprite('blocked_door', 1, (128, 16), 4)
        self.image = self.animated_sprite.image
        self.rect = self.animated_sprite.rect
        self.rect.midleft = position

        self.enemy = enemy

    def kill_door_if_enemies_are_dead(self):
        if isinstance(self.enemy,list):
            for enemy in self.enemy:
                if enemy.alive():
                    break
            else: # it runs only if the loop finished without breaking
                self.kill()
        else:
            if not self.enemy.alive():
                self.kill()

    def update(self, dt):
        self.kill_door_if_enemies_are_dead()