from settings import *
from pathlib import Path
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, image_name,image_number, scale, speed):
        super().__init__()
        self.frames = []
        for i in range(image_number):
            self.frames.append(pygame.image.load(Path(__file__).resolve().parent.parent / 'data' / str(image_name + str(i + 1) + '.png')).convert_alpha())
            self.frames[i] = pygame.transform.scale(self.frames[i], scale)
        self.image = self.frames[0]
        self.rect = self.image.get_frect()
        self.index = 0
        self.speed = speed

    def update(self, dt):
        if self.speed == 0:
            return
        self.index += dt * self.speed
        self.image = self.frames[int(self.index) % len(self.frames)]

