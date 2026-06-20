from Utils.settings import *
from Utils.weapon import Weapon
from Utils.particles import AnimationPlayer
from Entities.player import Player
from Entities.enemies import Enemy
from Entities.npc import NpcLayer
from Interface.overlay import Overlay
from Graphics.sprites import Generic, Water, Flower, Tree, Interaction, Particle
from pytmx.util_pygame import load_pygame
from Utils.support import *
from Utils.transition import Transition
from Scene.soil import SoilLayer
from Entities.animals import AnimalLayer
from Scene.buildings import BuildingLayer
from Graphics.sky import Rain, DayChange
from Interface.menu import Menu
import random
from random import randint


class Level:
    def __init__(self, screen_width, screen_height, volume, difficulty):
        
        self.initialized = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.volume = volume
        self.difficulty = difficulty

        self.display_surface = pygame.display.get_surface()

        self.all_sprites = Camera()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.building_layer = BuildingLayer(self.all_sprites, self.collision_sprites)
        self.chicken_layer = AnimalLayer(self.all_sprites, self.collision_sprites, self.building_layer)
        self.cow_layer = AnimalLayer(self.all_sprites, self.collision_sprites, self.building_layer)
        self.npc_layer = NpcLayer(self.all_sprites, self.collision_sprites)
        self.animation_player = AnimationPlayer()
        self.enemies_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.current_attack = None
        self.enemies = []
        self.enemy_spawned = False

        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 6
        self.soil_layer.raining = self.raining
        self.sky = DayChange()

        self.menu = Menu(self.player, self.toggle_shop)
        self.shop_active = False

        self.success = pygame.mixer.Sound('../audio/success.wav')
        self.success.set_volume(0.4)

        self.create_soil_grid()
        self.create_hit_rects()

        self.adjust_monster_parameters()


    def adjust_monster_parameters(self):
        multiplier = {
            'Easy': 0.75,
            'Medium': 1.5,
            'Hard': 2
        }[self.difficulty]

        for monster in monster_data.values():
            monster['health'] = int(monster['health'] * multiplier)
            monster['damage'] = int(monster['damage'] * multiplier)

    def setup(self):
        tmx_data = load_pygame('../data/map.tmx')

        for layer in ['HouseFloor','HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls','HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)

        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

        water_frames = import_folder('../graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        for obj in tmx_data.get_layer_by_name('Trees'):
             self.tree =  Tree(
                pos = (obj.x, obj.y), 
                surf = obj.image, 
                groups = [self.all_sprites, self.collision_sprites, self.tree_sprites], 
                name = obj.name,
                player_add = self.player_add)
             self.tree_sprites.add(self.tree)

        for obj in tmx_data.get_layer_by_name('Decoration'):
            Flower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos = (obj.x, obj.y), 
                    group = self.all_sprites, 
                    collision_sprites = self.collision_sprites,
                    tree_sprites = self.tree_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer,
                    building_layer = self.building_layer,
                    chicken_layer = self.chicken_layer,
                    cow_layer = self.cow_layer,
                    npc_layer = self.npc_layer,
                    create_attack = self.create_attack,
                    destroy_attack = self.destroy_attack,
                    toggle_shop = self.toggle_shop)
                  
            
            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
            
            if obj.name == 'Trader':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

        Generic(pos = (0,0), 
                surf = pygame.image.load('../graphics/world/ground.png').convert_alpha(), 
                groups = self.all_sprites,
                z = LAYERS['ground'])
        
    def spawn(self, player_level):
        if player_level % 2 == 0 and not self.enemy_spawned:
            self.enemy_()
            self.enemy_spawned = True
            print('Evil')
        elif player_level % 2 != 0:
            self.enemy_spawned = False


    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE

        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles) ]
        for x, y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y , TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def enemy_(self):
        possible_positions = [(rect.x // TILE_SIZE, rect.y // TILE_SIZE) for rect in self.hit_rects if 'E' and 'N' and 'C' and 'M' and 'A' and 'B' not in self.grid[rect.y // TILE_SIZE][rect.x // TILE_SIZE]]
        if possible_positions:
            x, y = random.choice(possible_positions)
            self.grid[y][x].append('E')
            self.create_enemy(x, y)

    def create_enemy(self, x, y):
        monster_name = random.choice(list(monster_data.keys()))
        enemy = Enemy(
            pos=(x * TILE_SIZE, y * TILE_SIZE), 
            groups=[self.all_sprites, self.attackable_sprites, self.enemies_sprites],
            collision_sprites = self.collision_sprites,
            monster_name=monster_name,
			damage_player = self.damage_player,
			trigger_death_particles = self.trigger_death_particles,
        )
        self.enemies.append(enemy)

    def damage_player(self,amount,attack_type, attack_sound):
          if self.player.vulnerable:
             self.player.health -= amount
             self.player.vulnerable = False
             self.player.hurt_time = pygame.time.get_ticks()
             self.attack_sound = attack_sound
             self.animation_player.create_particles(attack_type,self.player.rect.center,[self.all_sprites])
             self.player.take_damage(amount)

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, self.all_sprites)


    def create_attack(self):

        self.current_attack = Weapon(self.player,[self.all_sprites, self.attack_sprites])
        print(f"Player position: {self.player.rect.center}, Weapon position: {self.current_attack.rect.center}")
        print(f"Current attack created: {self.current_attack}")

    def destroy_attack(self):
        if self.current_attack:
             self.current_attack.kill()
             self.all_sprites.remove(self.current_attack)
             print(f"Current attack destroyed: {self.current_attack}")
        self.current_attack = None
        print(f"Current attack after destruction: {self.current_attack}")


    def player_attack_logic(self):
     if self.attack_sprites:
        for attack_sprite in self.attack_sprites:
            collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, True)
            if collision_sprites:
                for target_sprite in collision_sprites:
                    target_sprite.get_damage(self.player,attack_sprite.sprite_type)


    def reset(self, dt):
        
        self.soil_layer.update_plants()
        
        self.soil_layer.remove_water()

        self.chicken_layer.update_chicken(dt)
        self.cow_layer.update_cow(dt)

        self.raining = randint(0,10) > 6
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        for tree in self.tree_sprites.sprites():
            if isinstance(tree, Tree):
               for apple in tree.apple_sprites.sprites():
                   apple.kill()
               tree.create_fruit()
        
        self.sky.start_color = [255, 255, 255]

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites,
                             z = LAYERS['main'])
                    self.soil_layer.grid[plant.rect.centery // TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')

    def egg_collect(self):
        if self.chicken_layer.egg_sprites:
           for egg in self.chicken_layer.egg_sprites.sprites():
               if egg.rect.colliderect(self.player.hitbox):
                  self.player_add('egg')
                  egg.kill()
                  Particle(egg.rect.topleft, egg.image, self.all_sprites, z=LAYERS['main'])
                  self.player.gain_experience(5)

    def milk_collect(self):
        if self.cow_layer.milk_sprites:
           for milk in self.cow_layer.milk_sprites.sprites():
               if milk.rect.colliderect(self.player.hitbox):
                  self.player_add('egg')
                  milk.kill()
                  Particle(milk.rect.topleft, milk.image, self.all_sprites, z=LAYERS['main'])
                  self.player.gain_experience(5)

    def player_add(self, item, amount = 1):

        self.player.item_inventory[item] += amount
        self.success.play()

    def toggle_shop(self):

        self.shop_active = not self.shop_active

    def run(self, dt):

        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        
        if self.shop_active:
            self.menu.update()
        else:
            self.all_sprites.update(dt)
            self.plant_collision()
            self.egg_collect()
            self.milk_collect()
            self.all_sprites.enemy_update(self.player)
            self.spawn(self.player.level)
            self.player_attack_logic()

        
        for self.tree in self.tree_sprites.sprites():
            self.tree.update(dt)
            self.all_sprites.add(self.tree)

        self.overlay.display(self.player)
        if self.raining and not self.shop_active:
            self.rain.update()
        self.sky.display(dt)

        if self.player.sleep:
            self.transition.play(dt)

    def update_settings(self, screen_width, screen_height, volume):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.volume = volume
        pygame.display.set_mode((screen_width, screen_height))

    def music_sound(self, music, volume):
        self.music = music
        self.volume = volume
        self.music.play(loops=-1)


    def save_player_state(self, filename):
        player_state = {
            'item_inventory': self.player.item_inventory,
            'seed_inventory': self.player.seed_inventory,
            'animals_inventory': self.player.animals_inventory,
            'money': self.player.money,
            'selected_tool' : self.player.selected_tool,
            'pos' : self.player.pos,
            'selected_seed': self.player.selected_seed,
            'selected_animal': self.player.selected_animal,
            'tool_index': self.player.tool_index,
            'seed_index': self.player.seed_index,
            'animal_index': self.player.animal_index,
            'health': self.player.health,
            'experience': self.player.experience,
            'max_experience': self.player.max_experience,
            'level': self.player.level,
            'tasks': self.player.tasks,
            'weapon_index': self.player.weapon_index,
        }

        with open(filename, 'wb') as f:
            pickle.dump(player_state, f)

    def load_player_state(self, filename):
        try:
            with open(filename, 'rb') as file:
                player_state = pickle.load(file)
                self.player.item_inventory = player_state['item_inventory']
                self.player.seed_inventory = player_state['seed_inventory']
                self.player.animals_inventory = player_state['animals_inventory']
                self.player.money = player_state['money']
                self.player.selected_tool = player_state['selected_tool']
                self.player.pos = player_state['pos']
                self.player.selected_seed = player_state['selected_seed']
                self.player.selected_animal = player_state['selected_animal']
                self.player.tool_index = player_state['tool_index']
                self.player.seed_index = player_state['seed_index']
                self.player.animal_index = player_state['animal_index']
                self.player.health = player_state['health']
                self.player.experience = player_state['experience']
                self.player.max_experience = player_state['max_experience']
                self.player.level = player_state['level']
                self.player.tasks = player_state['tasks']
                self.player.weapon_index = player_state['weapon_index']
        except FileNotFoundError:
            print(f"File {filename} not found.")
        except Exception as e:
            print(f"Error loading player state: {e}")


class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():  
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)

    def update_screen_size(self, screen_width, screen_height):
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = screen_width, screen_height
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)



