from timer import Timer
from pygame import sprite
from random import randint
from settings import *
from pathlib import Path
from camera import CameraGroup
from animation import AnimatedSprite

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, collision_group, position, world_size):
        super().__init__(groups)
        self.animated_sprite = AnimatedSprite('fli', 4, (56, 40), 8)
        self.image = self.animated_sprite.image
        self.facing_right = True
        self.rect = self.animated_sprite.rect
        self.rect.center = position
        self.speed = SPEED['player']
        self.collision_group = collision_group
        self.world_size = world_size

    def update(self, dt):
        self.image = self.animated_sprite.image
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.animated_sprite.update(dt)

        self.keys = pygame.key.get_pressed()
        self.old_rect = self.rect.copy()
        self.move(dt)

    def move(self, dt):
        if self.keys[pygame.K_w]:
            if self.rect.top > 0:
                self.rect.centery -= self.speed * dt
                self.collision("vertical")
        if self.keys[pygame.K_s]:
            if self.rect.bottom < self.world_size.y:
                self.rect.centery += self.speed * dt
                self.collision("vertical")
        if self.keys[pygame.K_a]:
            self.facing_right = False
            if self.rect.left > 0:
                self.rect.centerx -= self.speed * dt
                self.collision("horizontal")
        if self.keys[pygame.K_d]:
            self.facing_right = True
            if self.rect.right < self.world_size.x:
                self.rect.centerx += self.speed * dt
                self.collision("horizontal")

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

class Enemy(pygame.sprite.Sprite):
    def __init__(self, groups, collision_group, world_size):
        super().__init__(groups)

        #self.bounding_box = pygame.Rect(0, 0, self.rect.width * 5, self.rect.height * 5)
        #self.bounding_box.center = (self.rect.centerx, self.rect.centery)

        self.world_size = world_size
        self.collision_group = collision_group

        self.change_direction_timer = Timer(1,self.change_direction, True)
        self.change_direction_timer.activate()

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
    def __init__(self, groups, collision_group, world_size, position):
        super().__init__(groups, collision_group, world_size)
        self.name = "Evil fly"
        self.health = 1
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
    def __init__(self, groups, collision_group, world_size, position):
        super().__init__(groups, collision_group, world_size)
        self.name = "Evil spiderlike creature"
        self.health = 6
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
    def __init__(self, groups, collision_group, world_size, position):
        super().__init__(groups, collision_group, world_size)
        self.name = "Evil very big beetle"
        self.health = 14
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

        # self.bounding_box = pygame.Rect(0, 0, self.rect.width * 5, self.rect.height * 5)
        # self.bounding_box.center = (self.rect.centerx, self.rect.centery)

class InteractableObject(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        # self.bounding_box = pygame.Rect(0, 0, self.rect.width * 5, self.rect.height * 5)
        # self.bounding_box.center = (self.rect.centerx, self.rect.centery)

class OldCreatureNPC(NPC):
    def __init__(self, groups, position):
        super().__init__(groups)
        self.animated_sprite = AnimatedSprite('old_creature', 4, (128, 112), 4)
        self.image = self.animated_sprite.image
        self.rect = self.animated_sprite.rect
        self.rect.center = position

        self.dialogue = [
            'Hello there small fly',
            'Do you want to fight me?',
            'Do not worry I was joking',
            'The developer is too stupid to implement such a feature',
            'Thank you for your understanding',
            'Have a nice day'
        ]

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

        self.dialogue = [
            'I am a very old creature',
            'I was created in 2019'
        ]

    def update(self, dt):
        super().update(dt)
        self.image = self.animated_sprite.image
        self.animated_sprite.update(dt)