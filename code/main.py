from settings import *
from battle_sprites import *
from button import *
from scenes import *
from save_manager import SaveManager

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Pong + Adventure')

    clock = pygame.time.Clock()

    manager = GameManager("MENU")
    RUNNING = True

    current_scene_name = None
    current_scene = None

    scenes = {'MENU' : Menu,
              'PAUSE_MENU' : PauseMenu,
              'INSTRUCTIONS' : Instructions,
              'SAVE_FILES' : SaveFiles,
              'INTRO' : Intro,
              'BATTLE': Battle,
              'OVERWORLD' : Overworld,
              'STATS' : Stats,
              'GAME_OVER' : GameOver}

    scene_instances = {}

    while RUNNING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUNNING = False

        dt = clock.tick() / 1000

        new_scene_name = manager.get_scene()

        if new_scene_name != current_scene_name:
            current_scene_name = new_scene_name
            if new_scene_name not in scene_instances or new_scene_name == manager.new_instance_request:
                scene_instances[new_scene_name] = scenes[current_scene_name](manager)
                manager.new_instance_request = None
        current_scene = scene_instances[new_scene_name]

        current_scene.run(dt)