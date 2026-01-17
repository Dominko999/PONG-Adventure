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
from save_manager import SaveManager


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
        self.exp_gain = None
        self.player = None

        self.save_manager = SaveManager()

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
        self.screen = pygame.display.get_surface()

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
        self.player_health = self.game_manager.player.stats['health']
        self.enemy_health = getattr(self.game_manager.active_enemy, 'health')
        self.enemy_name = getattr(self.game_manager.active_enemy, 'name')

        # creating sprite instances
        self.ball = BattleBall(self.all_sprites, self.paddle_sprites, self.update_UI)
        self.player_paddle = PlayerPaddle((self.all_sprites, self.paddle_sprites), self.game_manager.player)
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

    def battle_won(self):
        self.game_manager.exp_gain = self.game_manager.active_enemy.exp_gain
        self.game_manager.save_manager.game_state['defeated_enemies'][self.game_manager.active_enemy.id] = True
        self.game_manager.active_enemy.kill()
        self.game_manager.active_enemy = None
        self.game_manager.change_scene('STATS', new_instance = True)

    def battle_lost(self):
        self.game_manager.change_scene('GAME_OVER', True)

    def run(self, dt):
        super().run(dt)

        # update
        self.all_sprites.update(dt)

        # check if the battle is over
        if self.player_health <= 0:
            self.battle_lost()
        elif self.enemy_health <= 0:
            self.battle_won()

        # pauses the game if escape is pressed
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
        self.item_sprites = pygame.sprite.Group()

        if self.game_manager.player is None:
            self.player = Player(self.overworld_sprites, self.tilemap.collision_group, self.game_manager.save_manager.game_state['player_position'], self.tilemap.world_size, self.game_manager.save_manager.game_state['stats']) #475, 6100
        else:
            self.player = self.game_manager.player
            self.overworld_sprites.add(self.player)

        # enemies and blocked doors
        self.classes_of_instances_to_spawn = {
            'FlyEnemy' : FlyEnemy,
            'SpiderlikeEnemy' : SpiderlikeEnemy,
            'BeetleEnemy' : BeetleEnemy,
            'BlockedDoor' : BlockedDoor
        }

        self.enemies_to_spawn = [ #(name,x,y,{optionally}: 'BlockedDoor',x,y)
            ('FlyEnemy', 1710, 5125),
            ('FlyEnemy', 2020, 5140),
            ('FlyEnemy', 2270, 5100),
            ('SpiderlikeEnemy', 2460, 4350),
            ('SpiderlikeEnemy', 3760, 2780),
            ('SpiderlikeEnemy', 3760, 2780),
            ('BeetleEnemy', 3760, 2780, 'BlockedDoor', 1710, 5125) #4096, 2480
        ]
        self.spawn_enemies()
        # NPCs
        self.npc1 = OldCreatureNPC((self.overworld_sprites, self.npc_sprites), (2250,5910))
        self.npc2 = OldBeetleNPC((self.overworld_sprites, self.npc_sprites), (2425,2800))

        # items
        self.old_scripture = OldScripture((self.overworld_sprites, self.item_sprites), (4155,1737))
        self.lightbulb1 = LightBulb((self.overworld_sprites, self.item_sprites), (2594, 3533))

        self.camera = Camera(self.player, self.tilemap.world_size)
        self.camera_group = CameraGroup(self.camera)
        self.camera_group.add(self.tilemap.background_group,self.overworld_sprites, self.tilemap.collision_group)

        self.text_box = TextBox(self.dialogue_sprites, 'none')

        self.end_game = False

    def spawn_enemies(self):
        for index, line in enumerate(self.enemies_to_spawn):
            class_name = line[0]
            pos = (line[1], line[2])
            id = str(index)
            #check if enemy is not cleared
            if not self.game_manager.save_manager.is_instance_already_cleared(id):
                enemy_instance = self.classes_of_instances_to_spawn[class_name]((self.overworld_sprites, self.enemy_sprites), self.tilemap.collision_group, self.tilemap.world_size, pos, id)
                if len(line) == 7:
                    blocked_door = line[4]
                    door_pos = (line[5], line[6])
                    self.classes_of_instances_to_spawn[blocked_door]((self.overworld_sprites, self.tilemap.collision_group), door_pos, enemy_instance)



    def handle_collision_with_enemies(self):
        for enemy in self.enemy_sprites:
            if enemy.rect.colliderect(self.player.rect):
                self.game_manager.active_enemy = enemy
                self.game_manager.player = self.player
                self.game_manager.change_scene('BATTLE', True, True)


    def handle_collision_with_npc(self):
        for npc in self.npc_sprites:
            if npc.rect.colliderect(self.player.rect):
                self.scene_state = 'Dialogue'
                self.text_box = TextBox(self.dialogue_sprites, npc.dialogue, npc.name, 'dialogue')
                npc.advance_dialogue()

    def handle_collision_with_items(self):
        for item in self.item_sprites:
            if item.rect.colliderect(self.player.rect):
                if isinstance(item, LightBulb):
                    self.game_manager.save_manager.save_game(self.player.rect.center, self.player.stats, item.checkpoint_name)
                    self.scene_state = 'Dialogue'
                    self.text_box = TextBox(self.dialogue_sprites, item.text, mode='text')
                elif isinstance(item, OldScripture):
                    self.scene_state = 'Dialogue'
                    self.end_game = True
                    self.text_box = TextBox(self.dialogue_sprites, item.text, mode='text')


    def run(self, dt):
        super().run(dt)

        if self.pressed_keys[pygame.K_ESCAPE]:
            self.game_manager.change_scene('PAUSE_MENU', True)

        # update default
        if self.scene_state == 'Default':
            self.overworld_sprites.update(dt)
            self.handle_collision_with_enemies()
            self.camera.update()
            print(self.player.rect.center)
            if self.just_pressed_keys[pygame.K_e]:
                self.handle_collision_with_npc()
                self.handle_collision_with_items()


        # update dialogue
        elif self.scene_state == 'Dialogue':
            self.dialogue_sprites.update(dt)
            if self.text_box.active:
                if self.just_pressed_keys[pygame.K_e]:
                    self.text_box.next_line()
            else:
                # dialogue finished
                if self.end_game:
                    self.game_manager.change_scene('MENU', False)
                self.scene_state = 'Default'

        # draw
        self.screen.fill(COLORS['bg'])
        self.camera_group.draw(self.screen)

        if self.scene_state == 'Dialogue' and self.text_box != None:
            self.dialogue_sprites.draw(self.screen)

        pygame.display.update()

class Menu(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)

        self.title_text = FONTS['menu_title'].render('PONG + Adventure', True, COLORS['bg_detail'])
        self.title_rect = self.title_text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 200))
        self.buttons_group = pygame.sprite.Group()
        self.start_button = Button(self.buttons_group, 'Start', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                                   300, 90, lambda : self.game_manager.change_scene('SAVE_FILES'), self.screen)
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

        self.overworld_instructions_text = ['Use WASD to move',
                                    'Press E key to advance dialogue and interact with NPCs and items',
                                    'Press Esc key to pause the game']
        self.battle_instructions_text = ['Use W and S keys to move the paddle up and down',
                                    'Use D key to bounce the ball with more power',
                                    'Use Q key to make the paddle slide and curve the ball']

        self.buttons_group = pygame.sprite.Group()
        self.start_button = Button(self.buttons_group, 'OK', 'menu_buttons', 'bg', WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 250,
                                   300, 90, lambda : self.game_manager.change_scene('INTRO'), self.screen)

    def run(self, dt):
        super().run(dt)

        #update
        self.buttons_group.update(dt)

        #draw
        self.screen.fill(COLORS['bg'])

        write_text('Overworld controls:', FONTS['menu_buttons'], COLORS['bg_detail'], WINDOW_WIDTH / 2, 100, screen=self.screen)
        write_text(self.overworld_instructions_text, FONTS['instructions_text'], COLORS['bg_detail'], WINDOW_WIDTH / 2, 150, 50, screen=self.screen)

        write_text('Battle controls:', FONTS['menu_buttons'], COLORS['bg_detail'], WINDOW_WIDTH / 2, 350,
                   screen=self.screen)
        write_text(self.battle_instructions_text, FONTS['instructions_text'], COLORS['bg_detail'], WINDOW_WIDTH / 2,
                   400, 50, screen=self.screen)

        self.buttons_group.draw(self.screen)

        pygame.display.update()

class Intro(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)
        self.intro_sprites = pygame.sprite.Group()
        self.buttons_group = pygame.sprite.Group()

        self.animated_image = AnimatedSprite('intro', 3,(450,450),0)
        self.animated_image.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 115)
        self.intro_sprites.add(self.animated_image)

        self.first_image_text = [
            'Many years ago a great scripture was written',
            'Inside it were many wise words',
            'VERY WISE WORDS',
            'Many battles were fought to obtain it',
            'Finally the scripture was lost',
            'Many expeditions were made in order to find it',
            'Every single one of them failed',
            'Until only a legend remained of the greatness of the scripture',
            'But one day a very small fly embarked on a journey',
            'A VERY EPIC one',
            'To find the scripture and save the world from the evil spirits'
        ]

        self.text_box = TextBox(self.intro_sprites, self.first_image_text, mode='text')

        self.skip_button = Button(self.buttons_group, 'Skip', 'menu_buttons', 'bg', WINDOW_WIDTH / 10, WINDOW_HEIGHT / 8,
                                   150, 50, lambda : self.game_manager.change_scene('OVERWORLD', new_instance = True), self.screen)


    def run(self, dt):
        super().run(dt)

        # update
        self.buttons_group.update(dt)
        self.intro_sprites.update(dt)
        if self.text_box.active:
            if self.just_pressed_keys[pygame.K_e]:
                self.text_box.next_line()
            if self.text_box.line == 4:
                self.animated_image.image = self.animated_image.frames[1]
            if self.text_box.line == 8:
                self.animated_image.image = self.animated_image.frames[2]
        else:
            # dialogue finished
            self.game_manager.change_scene('OVERWORLD', new_instance = True)

        #draw
        self.screen.fill(COLORS['bg'])
        self.buttons_group.draw(self.screen)
        self.intro_sprites.draw(self.screen)

        pygame.display.update()

class SaveFiles(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)

        self.buttons_group = pygame.sprite.Group()
        self.create_buttons()

    def load_save_file(self, file_number):
        self.game_manager.save_manager.load_save(file_number)
        if self.game_manager.save_manager.new_game:
            self.game_manager.change_scene('INSTRUCTIONS', new_instance=True)
        else:
            self.game_manager.change_scene('OVERWORLD', new_instance=True)

    def delete_save_file(self, file_number):
        self.game_manager.save_manager.delete_save_file(file_number)
        self.buttons_group.empty()
        self.create_buttons()


    def create_buttons(self):
        self.file_1_button = Button(self.buttons_group, self.game_manager.save_manager.return_save_name('save1'),
                                    'menu_buttons', 'bg', WINDOW_WIDTH / 24 * 11, 250,
                                    1000, 140, lambda: self.load_save_file('save1'), self.screen)
        self.file_2_button = Button(self.buttons_group, self.game_manager.save_manager.return_save_name('save2'),
                                    'menu_buttons', 'bg', WINDOW_WIDTH / 24 * 11, 420,
                                    1000, 140, lambda: self.load_save_file('save2'), self.screen)
        self.file_3_button = Button(self.buttons_group, self.game_manager.save_manager.return_save_name('save3'),
                                    'menu_buttons', 'bg', WINDOW_WIDTH / 24 * 11, 590,
                                    1000, 140, lambda: self.load_save_file('save3'), self.screen)
        self.delete_file_1_button = Button(self.buttons_group, 'Delete',
                                           'instructions_text', 'bg', WINDOW_WIDTH / 24 * 22, 250,
                                           150, 60, lambda: self.delete_save_file('save1'), self.screen)
        self.delete_file_2_button = Button(self.buttons_group, 'Delete',
                                           'instructions_text', 'bg', WINDOW_WIDTH / 24 * 22, 420,
                                           150, 60, lambda: self.delete_save_file('save2'), self.screen)
        self.delete_file_3_button = Button(self.buttons_group, 'Delete',
                                           'instructions_text', 'bg', WINDOW_WIDTH / 24 * 22, 590,
                                           150, 60, lambda: self.delete_save_file('save3'), self.screen)

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
        self.continue_from_last_save_button = Button(self.buttons_group, 'Retry from last save', 'menu_buttons', 'bg', WINDOW_WIDTH / 2,
                                                     WINDOW_HEIGHT / 2,
                                                     500, 90, lambda: self.retry_from_last_save(), self.screen)
        self.return_to_menu_button = Button(self.buttons_group, 'Menu', 'menu_buttons', 'bg', WINDOW_WIDTH / 2,
                                            WINDOW_HEIGHT / 2 + 100,
                                            300, 90, lambda: self.game_manager.change_scene('MENU'), self.screen)
        self.quit_button = Button(self.buttons_group, 'Quit', 'menu_buttons', 'bg', WINDOW_WIDTH / 2,
                                  WINDOW_HEIGHT / 2 + 200,
                                  300, 90, lambda: self.game_manager.quit_game(), self.screen)

    def retry_from_last_save(self):
        self.game_manager.save_manager.load_save()
        self.game_manager.player = None
        self.game_manager.change_scene('OVERWORLD', False, True)

    def run(self, dt):
        super().run(dt)

        # update
        self.buttons_group.update(dt)

        # draw
        self.screen.fill(COLORS['bg'])
        write_text('GAME OVER', FONTS['menu_title'], COLORS['bg_detail'], WINDOW_WIDTH / 2, 200, screen=self.screen)
        self.buttons_group.draw(self.screen)

        pygame.display.update()

class Stats(Scene):
    def __init__(self, scene_manager : GameManager):
        super().__init__(scene_manager)

        self.state = 'DEFAULT'

        self.level_up_buttons = pygame.sprite.Group()
        self.default_buttons = pygame.sprite.Group()
        self.ui_sprites = pygame.sprite.Group()

        self.add_exp()

        self.fli_image = AnimatedSprite('fli_stats', 1, (256,256), 0)
        self.match_fli_image()

        self.exp_bar = ProgressBar(self.ui_sprites, self.game_manager.player.exp_cap, 20, COLORS['paddle_slide'],WINDOW_WIDTH / 10,
                                   WINDOW_HEIGHT / 7 * 5.3, anchor='left')

        self.health_icon = AnimatedSprite('health', 2, (64,64), 4)
        self.health_icon.rect.center = (WINDOW_WIDTH / 10 * 5, WINDOW_HEIGHT / 7 * 2)
        self.health_up_button = Button(self.level_up_buttons, '+', 'dialogue', 'paddle_active', WINDOW_WIDTH / 11 * 9.5,
                                       WINDOW_HEIGHT / 7 * 2, 64, 64,
                                       lambda:self.upgrade_stat('health'), self.screen)

        self.agility_icon = AnimatedSprite('agility', 8, (64, 64), 4)
        self.agility_icon.rect.center = (WINDOW_WIDTH / 10 * 5, WINDOW_HEIGHT / 7 * 3)
        self.agility_up_button = Button(self.level_up_buttons, '+', 'dialogue', 'paddle_active', WINDOW_WIDTH / 11 * 9.5,
                                        WINDOW_HEIGHT / 7 * 3, 64, 64,
                                        lambda: self.upgrade_stat('agility'), self.screen)

        self.size_icon = AnimatedSprite('size', 3, (64, 64), 4)
        self.size_icon.rect.center = (WINDOW_WIDTH / 10 * 5, WINDOW_HEIGHT / 7 * 4)
        self.size_up_button = Button(self.level_up_buttons, '+', 'dialogue', 'paddle_active', WINDOW_WIDTH / 11 * 9.5,
                                     WINDOW_HEIGHT / 7 * 4, 64, 64,
                                     lambda: self.upgrade_stat('size'), self.screen)

        self.ui_sprites.add(self.health_icon, self.agility_icon, self.size_icon, self.fli_image)
        self.level_up_buttons.add(self.health_up_button, self.agility_up_button, self.size_up_button)
        self.start_button = Button(self.default_buttons, 'Continue', 'menu_buttons', 'bg', WINDOW_WIDTH / 2,
                                   WINDOW_HEIGHT / 2 + 250,300, 90,
                                   lambda : self.game_manager.unpause_scene(), self.screen)

    def upgrade_stat(self, stat):
        self.game_manager.player.stats[stat] += 1
        self.state = 'DEFAULT'

    def add_exp(self):
        self.game_manager.player.stats['exp'] += self.game_manager.exp_gain

    def match_fli_image(self):
        if self.game_manager.player.stats['level'] == 1 or self.game_manager.player.stats['level'] == 2:
            self.ui_sprites.remove(self.fli_image)
            self.fli_image = AnimatedSprite('fli_stats', 1, (256,256), 0)
            self.ui_sprites.add(self.fli_image)
        elif self.game_manager.player.stats['level'] == 3 or self.game_manager.player.stats['level'] == 4:
            self.ui_sprites.remove(self.fli_image)
            self.fli_image = AnimatedSprite('medium_fli_stats', 1, (256,256), 0)
            self.ui_sprites.add(self.fli_image)
        else:
            self.ui_sprites.remove(self.fli_image)
            self.fli_image = AnimatedSprite('large_fli_stats', 1, (256, 256), 0)
            self.ui_sprites.add(self.fli_image)
        self.fli_image.rect.midleft = (WINDOW_WIDTH / 10, WINDOW_HEIGHT / 7 * 3)

    def check_level_up(self):
        if self.game_manager.player.stats['exp'] >= self.game_manager.player.exp_cap:
            self.game_manager.player.level_up()
            self.state = 'LEVEL_UP'

    def run(self, dt):
        super().run(dt)

        #update
        self.ui_sprites.update(dt)
        self.exp_bar.update_progress_bar(self.game_manager.player.stats['exp'])

        #draw
        self.screen.fill(COLORS['bg'])

        write_text('Stats', FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 2,
                   WINDOW_HEIGHT / 7, anchor='center',screen=self.screen)

        write_text('Level ' + str(self.game_manager.player.stats['level']), FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 10, WINDOW_HEIGHT / 7 * 4.7, anchor='midleft',screen=self.screen)

        # stat names
        write_text('Health', FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 12 * 6.5,
                   WINDOW_HEIGHT / 7 * 2, anchor='midleft', screen=self.screen)
        write_text('Agility', FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 12 * 6.5,
                   WINDOW_HEIGHT / 7 * 3, anchor='midleft',screen=self.screen)
        write_text('Size', FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 12 * 6.5,
                   WINDOW_HEIGHT / 7 * 4, anchor='midleft',screen=self.screen)

        # stat numbers
        write_text(str(self.game_manager.player.stats['health']), FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 12 * 9.5,
                   WINDOW_HEIGHT / 7 * 2, anchor='midleft', screen=self.screen)
        write_text(str(self.game_manager.player.stats['agility']), FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 12 * 9.5,
                   WINDOW_HEIGHT / 7 * 3, anchor='midleft', screen=self.screen)
        write_text(str(self.game_manager.player.stats['size']), FONTS['instructions_player'], COLORS['bg_detail'], WINDOW_WIDTH / 12 * 9.5,
                   WINDOW_HEIGHT / 7 * 4, anchor='midleft', screen=self.screen)

        if self.state == 'DEFAULT':
            self.default_buttons.draw(self.screen)
            self.default_buttons.update(dt)
            self.check_level_up()

        elif self.state == 'LEVEL_UP':
            self.match_fli_image()
            self.level_up_buttons.draw(self.screen)
            self.level_up_buttons.update(dt)
            write_text('Level Up!', FONTS['instructions_text'], COLORS['bg_detail'], WINDOW_WIDTH / 10 + self.exp_bar.rect.width + 25,
                       WINDOW_HEIGHT / 7 * 5.3 + 5, anchor='midleft', screen=self.screen)

        self.ui_sprites.draw(self.screen)

        pygame.display.update()