import pygame.event

from settings import *
from battle_sprites import *
from overworld_sprites import *
from tilemap import *
from button import Button
from text_box import TextBox
from camera import *
from progress_bar import ProgressBar
from global_functions import *

class GameManager():
    def __init__(self, scene):
        self.current_scene = scene or 'GAME'
        self.paused_scene = None
        self.right_player = 'AI'
        self.right_player_list = ['HUMAN', 'AI']
        self.new_instance_request = None

        # battle-related variables
        self.battle_result = None
        self.active_enemy = None

    def change_scene(self, scene, pause_previous = False, new_instance = False): #Changes the scene to one passed in the scene variable, if pause previous is true, then the previous scene is stored so that you can resume it
        if pause_previous:
            self.paused_scene = self.current_scene
        self.current_scene = scene
        if new_instance:
            self.new_instance_request = scene

    def unpause_scene(self):
        if self.paused_scene is not None:
            self.current_scene = self.paused_scene
            self.paused_scene = None

    def toggle_player(self, side, toggle_direction):
        if side == 'right':
            right_player_index = self.right_player_list.index(self.right_player)
            if toggle_direction == 'next':
                self.right_player = self.right_player_list[(right_player_index + 1) % len(self.right_player_list)]
            elif toggle_direction == 'previous':
                self.right_player = self.right_player_list[abs((right_player_index - 1)) % len(self.right_player_list)]
        #add left player toggle if needed

    def get_scene(self):
        return self.current_scene

    def quit_game(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

class Scene():
    def __init__(self, game_manager : GameManager):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.game_manager = game_manager

        self.scene_state = 'Default'

    def run(self, dt):
        self.pressed_keys = pygame.key.get_pressed()
        self.just_pressed_keys = pygame.key.get_just_pressed()

class Battle(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)

        self.enemy_ref = getattr(self.game_manager, 'active_enemy', None)

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.paddle_sprites = pygame.sprite.Group()
        self.ui_sprites = pygame.sprite.Group()

        # getting player and enemy variables
        self.player_health = 5
        self.enemy_health = getattr(self.game_manager.active_enemy, 'health')
        self.enemy_name = getattr(self.game_manager.active_enemy, 'name')

        # creating sprite instances
        self.ball = BattleBall(self.all_sprites, self.paddle_sprites, self.update_UI)
        self.player_paddle = PlayerPaddle((self.all_sprites, self.paddle_sprites))
        self.right_paddle = EnemyPaddle((self.all_sprites, self.paddle_sprites), self.ball, self.enemy_name)

        self.player_health_bar = ProgressBar(self.ui_sprites, self.player_health,20,COLORS['health'],BATTLE_AREA_LEFT + 20,BATTLE_AREA_BOTTOM + 70, 'left')
        self.enemy_health_bar = ProgressBar(self.ui_sprites, self.enemy_health,20,COLORS['health'],BATTLE_AREA_RIGHT - 20,BATTLE_AREA_BOTTOM + 70, 'right')

    def draw_UI(self):
        # player
        write_text('Player', FONTS['instructions_text'], COLORS['bg_detail'], BATTLE_AREA_LEFT + 20, BATTLE_AREA_BOTTOM + 30, screen=self.screen, anchor='midleft')
        self.player_health_bar.update_progress_bar(self.player_health)

        # enemy
        write_text(self.enemy_name, FONTS['instructions_text'], COLORS['bg_detail'], BATTLE_AREA_RIGHT - 20, BATTLE_AREA_BOTTOM + 30, screen=self.screen, anchor ='midright')
        self.enemy_health_bar.update_progress_bar(self.enemy_health)

        # lines forming the battle area
        pygame.draw.line(self.screen, COLORS['bg_detail'], (WINDOW_WIDTH / 2, BATTLE_AREA_TOP), (WINDOW_WIDTH / 2, BATTLE_AREA_BOTTOM),2)
        pygame.draw.line(self.screen, COLORS['bg_detail'], (BATTLE_AREA_LEFT, BATTLE_AREA_TOP), (BATTLE_AREA_LEFT, BATTLE_AREA_BOTTOM), 2)
        pygame.draw.line(self.screen, COLORS['bg_detail'], (BATTLE_AREA_RIGHT, BATTLE_AREA_TOP),(BATTLE_AREA_RIGHT, BATTLE_AREA_BOTTOM), 2)
        pygame.draw.line(self.screen, COLORS['bg_detail'], (BATTLE_AREA_LEFT, BATTLE_AREA_TOP), (BATTLE_AREA_RIGHT, BATTLE_AREA_TOP), 2)
        pygame.draw.line(self.screen, COLORS['bg_detail'], (BATTLE_AREA_LEFT, BATTLE_AREA_BOTTOM),(BATTLE_AREA_RIGHT, BATTLE_AREA_BOTTOM), 2)

    def update_UI(self, side):
        if side == 'left':
            self.player_health -= 1
        else:
            self.enemy_health -= 1

    def run(self, dt):
        super().run(dt)

        # update
        self.all_sprites.update(dt)

        if self.player_health <= 0:
            self.game_manager.change_scene('GAME_OVER', True)
        elif self.enemy_health <= 0:
            self.game_manager.active_enemy.kill()
            self.game_manager.active_enemy = None
            self.game_manager.unpause_scene()

        if self.pressed_keys[pygame.K_ESCAPE]:
            self.game_manager.change_scene('PAUSE_MENU', True)

        # draw
        self.screen.fill(COLORS['bg'])
        self.draw_UI()
        self.all_sprites.draw(self.screen)
        self.ui_sprites.draw(self.screen)

        pygame.display.update()

class Overworld(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)
        self.tilemap = Tilemap()
        self.overworld_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.npc_sprites = pygame.sprite.Group()
        self.dialogue_sprites = pygame.sprite.Group()
        self.player = Player(self.overworld_sprites, self.tilemap.collision_group, (475, 6100), self.tilemap.world_size)

        self.enemy = FlyEnemy((self.overworld_sprites, self.enemy_sprites), self.tilemap.collision_group, (1710, 5125), self.tilemap.world_size)
        self.enemy2 = FlyEnemy((self.overworld_sprites, self.enemy_sprites), self.tilemap.collision_group, (2020, 5140), self.tilemap.world_size)
        self.enemy3 = FlyEnemy((self.overworld_sprites, self.enemy_sprites), self.tilemap.collision_group, (2270, 5100), self.tilemap.world_size)
        self.enemy4 = SpiderlikeEnemy((self.overworld_sprites, self.enemy_sprites), self.tilemap.collision_group, (2460, 4350), self.tilemap.world_size)
        self.enemy3 = SpiderlikeEnemy((self.overworld_sprites, self.enemy_sprites), self.tilemap.collision_group, (3760, 2780), self.tilemap.world_size)
        self.enemy4 = SpiderlikeEnemy((self.overworld_sprites, self.enemy_sprites), self.tilemap.collision_group,
                                      (3760, 2780), self.tilemap.world_size)
        self.enemy5 = BeetleEnemy((self.overworld_sprites, self.enemy_sprites), self.tilemap.collision_group,(3760, 2780), self.tilemap.world_size)

        self.npc1 = OldCreatureNPC((self.overworld_sprites, self.npc_sprites), (2250,5910))
        self.npc2 = OldBeetleNPC((self.overworld_sprites, self.npc_sprites), (2425,2800))

        self.camera = Camera(self.player, self.tilemap.world_size)
        self.camera_group = CameraGroup(self.camera)
        self.camera_group.add(self.tilemap.background_group,self.overworld_sprites, self.tilemap.collision_group)

        self.dialogue_index = 0
        self.dialogue_box = TextBox(self.dialogue_sprites, 'none')

    def initialize_battle(self):
        for enemy in self.enemy_sprites:
            if enemy.rect.colliderect(self.player.rect):
                self.game_manager.active_enemy = enemy
                self.game_manager.change_scene('BATTLE', True, True)


    def run(self, dt):
        super().run(dt)

        if self.pressed_keys[pygame.K_ESCAPE]:
            self.game_manager.change_scene('PAUSE_MENU', True)

        # update default
        if self.scene_state == 'Default':
            self.overworld_sprites.update(dt)
            self.initialize_battle()
            self.camera.update()
            print(self.player.rect.center)
            if self.just_pressed_keys[pygame.K_e]:
                for npc in self.npc_sprites:
                    if npc.rect.colliderect(self.player.rect):
                        self.scene_state = 'Dialogue'
                        self.dialogue_box = TextBox(self.dialogue_sprites, npc.dialogue)


        # update dialogue
        elif self.scene_state == 'Dialogue':
            if self.dialogue_box.active:
                if self.just_pressed_keys[pygame.K_e]:
                    self.dialogue_box.next_line()
            else:
                # dialogue finished
                self.scene_state = 'Default'

        # draw
        self.screen.fill(COLORS['bg'])
        self.camera_group.draw(self.screen)

        if self.scene_state == 'Dialogue' and self.dialogue_box != None:
            self.dialogue_sprites.draw(self.screen)
            print('dziala')

        pygame.display.update()

class Menu(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)

        self.title_text = FONTS['menu_title'].render('PONG + Adventure', True, COLORS['bg_detail'])
        self.title_rect = self.title_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 200))
        self.buttons_group = pygame.sprite.Group()
        self.start_button = Button(self.buttons_group, 'Start', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                                   300, 90, lambda : self.game_manager.change_scene('INSTRUCTIONS'), self.screen)
        self.quit_button = Button(self.buttons_group, 'Quit', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 200,
                                  300, 90, lambda: self.game_manager.quit_game(), self.screen)
    def run(self, dt):
        super().run(dt)
        self.screen.fill(COLORS['bg'])
        self.screen.blit(self.title_text, self.title_rect)
        self.buttons_group.draw(self.screen)
        self.buttons_group.update(dt)

        pygame.display.update()

class Instructions(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)

        self.left_player_instructions_text = ['Use W and S keys to move the paddle up and down',
                                    'Use D key to bounce the ball with more power',
                                    'Use Q key to make the paddle slide and curve the ball']

        self.right_player_instructions_text = ['Use UP and DOWN arrow keys to move the paddle up and down',
                                              'Use LEFT key to bounce the ball with more power',
                                              'Use RIGHT key to make the paddle slide and curve the ball']


        self.buttons_group = pygame.sprite.Group()
        self.start_button = Button(self.buttons_group, 'OK', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 250,
                                   300, 90, lambda : self.game_manager.change_scene('SAVE_FILES'), self.screen)

    def run(self, dt):
        super().run(dt)

        #update
        self.buttons_group.update(dt)

        #draw
        self.screen.fill(COLORS['bg'])

        write_text('Left player:', FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 4, 150, screen=self.screen)
        write_text(self.left_player_instructions_text, FONTS['instructions_text'], COLORS['bg_detail'], WINDOW_WIDTH / 4, 250, 50, screen=self.screen)

        self.buttons_group.draw(self.screen)

        pygame.display.update()

class SaveFiles(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)

        self.buttons_group = pygame.sprite.Group()
        self.file_1_button = Button(self.buttons_group, 'File 1', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, 250,
                                    1000, 140, lambda : self.game_manager.change_scene('OVERWORLD', new_instance = True), self.screen)
        self.file_2_button = Button(self.buttons_group, 'File 2', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, 420,
                                    1000, 140, lambda: self.game_manager.change_scene('BATTLE', new_instance = True), self.screen)
        self.file_3_button = Button(self.buttons_group, 'File 3', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, 590,
                                    1000, 140, lambda: self.game_manager.change_scene('BATTLE', new_instance = True), self.screen)

    def run(self, dt):
        super().run(dt)

        #update
        self.buttons_group.update(dt)

        #draw
        self.screen.fill(COLORS['bg'])
        write_text('Save Files', FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 4, 100,screen=self.screen)
        self.buttons_group.draw(self.screen)

        pygame.display.update()

class PauseMenu(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)

        self.buttons_group = pygame.sprite.Group()
        self.resume_button = Button(self.buttons_group, 'Resume', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                                    300, 90, lambda : self.game_manager.unpause_scene(), self.screen)
        self.return_to_menu_button = Button(self.buttons_group, 'Menu', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 100,
                                            300, 90, lambda: self.game_manager.change_scene('MENU'), self.screen)
        self.quit_button = Button(self.buttons_group, 'Quit', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 200,
                                  300, 90, lambda: self.game_manager.quit_game(), self.screen)
    def run(self, dt):
        super().run(dt)

        #update
        self.buttons_group.update(dt)

        #draw
        self.screen.fill(COLORS['bg'])
        write_text('PAUSE', FONTS['menu_title'], COLORS['bg_detail'], WINDOW_WIDTH / 2, 200, screen=self.screen)
        self.buttons_group.draw(self.screen)

        pygame.display.update()

class GameOver(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)

        self.buttons_group = pygame.sprite.Group()
        self.continue_from_last_save_button = Button(self.buttons_group, 'Retry', 'menu_buttons', 'bg', WINDOW_WIDTH / 2,
                                                     WINDOW_HEIGHT / 2,
                                                     300, 90, lambda: self.game_manager.change_scene('OVERWORLD', False, True), self.screen)
        self.return_to_menu_button = Button(self.buttons_group, 'Menu', 'menu_buttons', 'bg', WINDOW_WIDTH / 2,
                                            WINDOW_HEIGHT / 2 + 100,
                                            300, 90, lambda: self.game_manager.change_scene('MENU'), self.screen)
        self.quit_button = Button(self.buttons_group, 'Quit', 'menu_buttons', 'bg', WINDOW_WIDTH / 2,
                                  WINDOW_HEIGHT / 2 + 200,
                                  300, 90, lambda: self.game_manager.quit_game(), self.screen)

    def run(self, dt):
        super().run(dt)

        # update
        self.buttons_group.update(dt)

        # draw
        self.screen.fill(COLORS['bg'])
        write_text('GAME OVER', FONTS['menu_title'], COLORS['bg_detail'], WINDOW_WIDTH / 2, 200, screen=self.screen)
        self.buttons_group.draw(self.screen)

        pygame.display.update()