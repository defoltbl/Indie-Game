import pygame
from Utils.settings import *
from pytmx.util_pygame import load_pygame
from Utils.support import *
from random import choice
import uuid
import time

class ChickenTile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, name, chicken_id, building_id, fed, feed_interval, last_fed_time, objects = []):
        super().__init__(groups)

        self.import_assets()

        self.status = 'down_idle'
        self.frame_index = 0

        self.image  = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.z = LAYERS['main']

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 10

         # зіткнення
        self.hitbox = self.rect.copy()
        self.collision_sprites = pygame.sprite.Group()

        self.direction_movement = None
        self.direction_timer = 3000
        self.current_timer = 0

        self.name = name

        self.chicken_id= chicken_id
        self.building_id = building_id
        self.fed = fed
        self.feed_interval = feed_interval
        self.last_fed_time = last_fed_time

        self.objects = objects

        self.tmx_data = load_pygame('../data/map.tmx')

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': []}
        
        for animation in self.animations.keys():
            full_path = '../graphics/animals/chicken/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
       self.frame_index += 4* dt
       if self.frame_index >= len(self.animations[self.status]):
           self.frame_index = 0

       self.image = self.animations[self.status][int(self.frame_index)]

    
    def change(self, dt):
        self.current_timer += dt * 1000 
        if self.current_timer >= self.direction_timer:
            self.current_timer = 0
            self.direction_movement = choice([DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT])

        self.input(dt)
    
    def input(self, dt):
            if self.direction_movement == 'up':
                self.direction.y -= self.speed * dt
                self.status = 'up'
            elif self.direction_movement == 'down':
                self.direction.y += self.speed * dt
                self.status = 'down'
            else:
                self.direction.y = 0

            if self.direction.y < 0:
               self.status = 'up'
            elif self.direction.y > 0:
                 self.status = 'down'

            if self.direction_movement == 'right':
                self.direction.x += self.speed * dt
                self.status = 'right'
            elif self.direction_movement == 'left':
                self.direction.x -= self.speed * dt
                self.status = 'left'
            else:
                self.direction.x = 0

            if self.direction.x > 0:
               self.status = 'right'
            elif self.direction.y < 0:
                 self.status = 'left'
                
    def get_status(self):
        if self.direction.magnitude() == 0:
           self.status = self.status.split('_')[0] + '_idle'
    
    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0 :
                           self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0 :
                           self.hitbox.left = sprite.hitbox.right 
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                        
                    if direction == 'vertical': 
                        if self.direction.y > 0 :
                           self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0 :
                           self.hitbox.top = sprite.hitbox.bottom 
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
                                   
    def move(self, dt):
        if self.direction.magnitude() > 0:
           self.direction = self.direction.normalize()
            
        previous_pos = self.pos.copy()

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        if pygame.sprite.spritecollideany(self, self.collision_sprites):
           self.pos = previous_pos
           self.hitbox.centerx = round(self.pos.x)
           self.rect.centerx = self.hitbox.centerx
           self.direction.x *= -1

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

        if pygame.sprite.spritecollideany(self, self.collision_sprites):
           self.pos = previous_pos
           self.hitbox.centery = round(self.pos.y)
           self.rect.centery = self.hitbox.centery
           self.direction.y *= -1

        collision_tiles = self.tmx_data.get_layer_by_name('Collision').tiles()
        for tile in collision_tiles:
            tile_rect = pygame.Rect(tile[0] * TILE_SIZE, tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if self.hitbox.colliderect(tile_rect):
              self.pos = previous_pos
              self.hitbox.centerx = round(self.pos.x)
              self.rect.centerx = self.hitbox.centerx
              self.hitbox.centery = round(self.pos.y)
              self.rect.centery = self.hitbox.centery
              break

        tree_tiles = self.tmx_data.get_layer_by_name('Trees')
        for tile in tree_tiles:
            tile_rect = pygame.Rect(tile.x, tile.y, tile.width, tile.height)
            if self.hitbox.colliderect(tile_rect):
               self.pos = previous_pos
               self.hitbox.centerx = round(self.pos.x)
               self.rect.centerx = self.hitbox.centerx
               self.hitbox.centery = round(self.pos.y)
               self.rect.centery = self.hitbox.centery
               break 

        decoration_tiles = self.tmx_data.get_layer_by_name('Decoration')
        for tile in decoration_tiles:
            tile_rect = pygame.Rect(tile.x, tile.y, tile.width, tile.height)
            if self.hitbox.colliderect(tile_rect):
               self.pos = previous_pos
               self.hitbox.centerx = round(self.pos.x)
               self.rect.centerx = self.hitbox.centerx
               self.hitbox.centery = round(self.pos.y)
               self.rect.centery = self.hitbox.centery
               break 

        for obj in self.objects:
            if obj != self and hasattr(obj, 'hitbox') and self.hitbox.colliderect(obj.hitbox):
               self.pos = previous_pos
               self.hitbox.centerx = round(self.pos.x)
               self.rect.centerx = self.hitbox.centerx
               self.hitbox.centery = round(self.pos.y)
               self.rect.centery = self.hitbox.centery
               break 

    def get_state(self):
        return {
            'pos': self.rect.topleft,
            'name': self.name,
            'chicken_id': self.chicken_id,
            'building_id': self.building_id,
            'fed': self.fed,
            'feed_interval': self.feed_interval,
            'last_fed_time': self.last_fed_time
        }

    @classmethod
    def from_state(cls, state):
        pos = state['pos']
        name = state['name']
        chicken_id = state['chicken_id']
        building_id = state['building_id']
        fed = state['fed']
        feed_interval = state['feed_interval']
        last_fed_time = state['last_fed_time']
        return cls(
            pos=pos,
            groups=[],
            name=name,
            chicken_id=chicken_id,
            building_id=building_id,
            fed=fed,
            feed_interval=feed_interval,
            last_fed_time=last_fed_time,
            objects=[]
        )
    
    def update(self, dt):
        self.change(dt)
        self.get_status()
        self.move(dt)
        self.animate(dt)

class Egg(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/products/egg.png')
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['main']


class CowTile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, name, cow_id, building_id, fed, feed_interval, last_fed_time, objects = []):
        super().__init__(groups)

        self.import_assets()

        self.status = 'down_idle'
        self.frame_index = 0

        self.image  = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.z = LAYERS['main']

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 50

        self.hitbox = self.rect.copy()
        self.collision_sprites = pygame.sprite.Group()

        self.direction_movement = None
        self.direction_timer = 4000
        self.current_timer = 0

        self.name = name

        self.cow_id= cow_id
        self.building_id = building_id
        self.fed = fed
        self.feed_interval = feed_interval
        self.last_fed_time = last_fed_time

        self.objects = objects

        self.tmx_data = load_pygame('../data/map.tmx')

    def import_assets(self):
        self.animations = { 'left': [], 'right': [], 'right_idle': [], 'left_idle': [],  'down_idle': []}
        
        for animation in self.animations.keys():
            full_path = '../graphics/animals/cow/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
       self.frame_index += 4* dt
       if self.frame_index >= len(self.animations[self.status]):
           self.frame_index = 0

       self.image = self.animations[self.status][int(self.frame_index)]

    
    def change(self, dt):
        self.current_timer += dt * 1000 
        if self.current_timer >= self.direction_timer:
            self.current_timer = 0
            self.direction_movement = choice([DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT])

        self.input(dt)
    
    def input(self, dt):
            if self.direction_movement == 'right':
                self.direction.x += self.speed * dt
                self.status = 'right'
            elif self.direction_movement == 'left':
                self.direction.x -= self.speed * dt
                self.status = 'left'
            else:
                self.direction.x = 0

            if self.direction.x > 0:
               self.status = 'right'
            elif self.direction.y < 0:
                 self.status = 'left'
                
    def get_status(self):
        if self.direction.magnitude() == 0:
           self.status = self.status.split('_')[0] + '_idle'
    
    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0 :
                           self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0 :
                           self.hitbox.left = sprite.hitbox.right 
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                        
                    if direction == 'vertical': 
                        if self.direction.y > 0 : 
                           self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0 :
                           self.hitbox.top = sprite.hitbox.bottom 
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
                                   
    def move(self, dt):
        if self.direction.magnitude() > 0:
           self.direction = self.direction.normalize()
            
        previous_pos = self.pos.copy()

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        if pygame.sprite.spritecollideany(self, self.collision_sprites):
           self.pos = previous_pos
           self.hitbox.centerx = round(self.pos.x)
           self.rect.centerx = self.hitbox.centerx
           self.direction.x *= -1
            
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

        if pygame.sprite.spritecollideany(self, self.collision_sprites):
           self.pos = previous_pos
           self.hitbox.centery = round(self.pos.y)
           self.rect.centery = self.hitbox.centery
           self.direction.y *= -1

        collision_tiles = self.tmx_data.get_layer_by_name('Collision').tiles()
        for tile in collision_tiles:
            tile_rect = pygame.Rect(tile[0] * TILE_SIZE, tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if self.hitbox.colliderect(tile_rect):
              self.pos = previous_pos
              self.hitbox.centerx = round(self.pos.x)
              self.rect.centerx = self.hitbox.centerx
              self.hitbox.centery = round(self.pos.y)
              self.rect.centery = self.hitbox.centery
              break  

        tree_tiles = self.tmx_data.get_layer_by_name('Trees')
        for tile in tree_tiles:
            tile_rect = pygame.Rect(tile.x, tile.y, tile.width, tile.height)
            if self.hitbox.colliderect(tile_rect):
               self.pos = previous_pos
               self.hitbox.centerx = round(self.pos.x)
               self.rect.centerx = self.hitbox.centerx
               self.hitbox.centery = round(self.pos.y)
               self.rect.centery = self.hitbox.centery
               break 

        decoration_tiles = self.tmx_data.get_layer_by_name('Decoration')
        for tile in decoration_tiles:
            tile_rect = pygame.Rect(tile.x, tile.y, tile.width, tile.height)
            if self.hitbox.colliderect(tile_rect):
               self.pos = previous_pos
               self.hitbox.centerx = round(self.pos.x)
               self.rect.centerx = self.hitbox.centerx
               self.hitbox.centery = round(self.pos.y)
               self.rect.centery = self.hitbox.centery
               break  

        for obj in self.objects:
            if obj != self and hasattr(obj, 'hitbox') and self.hitbox.colliderect(obj.hitbox):
               self.pos = previous_pos
               self.hitbox.centerx = round(self.pos.x)
               self.rect.centerx = self.hitbox.centerx
               self.hitbox.centery = round(self.pos.y)
               self.rect.centery = self.hitbox.centery
               break 

    def get_state(self):
        return {
            'pos': self.rect.topleft,
            'name': self.name,
            'cow_id': self.cow_id,
            'building_id': self.building_id,
            'fed': self.fed,
            'feed_interval': self.feed_interval,
            'last_fed_time': self.last_fed_time
        }

    @classmethod
    def from_state(cls, state):
        pos = state['pos']
        name = state['name']
        cow_id = state['cow_id']
        building_id = state['building_id']
        fed = state['fed']
        feed_interval = state['feed_interval']
        last_fed_time = state['last_fed_time']
        return cls(
            pos=pos,
            groups=[],
            name=name,
            cow_id=cow_id,
            building_id=building_id,
            fed=fed,
            feed_interval=feed_interval,
            last_fed_time=last_fed_time,
            objects=[]
        )
    
    def update(self, dt):
        self.change(dt)
        self.get_status()
        self.move(dt)
        self.animate(dt)

class Milk(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/products/milk.png')
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['main']

class AnimalLayer:
    def __init__(self, all_sprites, collision_sprites, building_layer):
        
        # sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.egg_sprites = pygame.sprite.Group()
        self.milk_sprites = pygame.sprite.Group()

        self.building_layer = building_layer

        self.building_sprites = self.building_layer.building_sprites.sprites()
        self.chicken_sprites = self.building_layer.chicken_sprites.sprites()
        self.cow_sprites = self.building_layer.cow_sprites.sprites()
        self.chicken_relations = self.building_layer.chicken_relations
        self.cow_relations = self.building_layer.cow_relations
        self.chicken_houses = self.building_layer.chicken_houses
        self.cow_houses = self.building_layer.cow_houses

        self.create_soil_grid()
        self.create_hit_rects()

        self.max_chickens = 3
        self.max_cows = 2
        self.chicken_counts = {}
        self.cow_counts = {}

        self.chicken_house_found = False
        self.cow_house_found = False

        self.chicken_created = False
        self.cow_created = False

        self.last_fed_time = time.time()

        self.initialize_relations()

    def initialize_relations(self):
        for building in self.building_layer.chicken_houses:
            if building.id not in self.chicken_relations:
                self.chicken_relations[building.id] = []
        for building in self.building_layer.cow_houses:
            if building.id not in self.cow_relations:
                self.cow_relations[building.id] = []

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
                    
    def create_chicken(self, player_rect, point):
        print("Checking for ChickenHouse...")
        chicken_spawn_offset = 75
        self.chicken_house_found = False
        for obj in self.building_layer.chicken_houses:
         if obj.name == 'ChickenHouse' and obj.hitbox.colliderect(player_rect):
            building_id = obj.id
            self.chicken_house_found = True
            chicken_id = str(uuid.uuid4())
            print(f"Found ChickenHouse with ID {building_id}")
            if self.chicken_counts.get(building_id , 0) < self.max_chickens:
                for rect in self.hit_rects:
                    if rect.collidepoint(point):
                        x = rect.x // TILE_SIZE
                        y = rect.y // TILE_SIZE
                        if self.grid[y][x].count('A') < 10:
                            self.grid[y][x].append('A')
                            self.chicken_relations[building_id].append(chicken_id)
                            print("Chicken can be created")
                            print("Creating chicken...")
                            chicken = ChickenTile(
                               pos=((x * TILE_SIZE) + chicken_spawn_offset, (y * TILE_SIZE) + chicken_spawn_offset),
                                groups=[self.all_sprites, self.chicken_sprites, self.collision_sprites],
                                name='Chicken',
                                chicken_id = chicken_id,
                                building_id = building_id,
                                fed = False,
                                feed_interval = 1,
                                last_fed_time = self.last_fed_time,
                                objects = self.building_layer.chicken_houses
                            )
                            self.building_layer.chicken_houses.append(chicken)
                            print("Chicken created successfully.")
                            self.building_layer.save_objects_chicken()
                            print("saved ch")
                            return
        if not self.chicken_house_found:
         print("No ChickenHouse found in the loaded objects.")
        print("Finished checking.")


    def create_cow(self, player_rect, point):
        print("Checking for CowHouse...")
        cow_spawn_offset = 75
        self.cow_house_found = False
        for obj in self.cow_houses:
         if obj.name == 'CowHouse' and obj.hitbox.colliderect(player_rect):
            building_id = obj.id
            self.cow_house_found = True
            cow_id = str(uuid.uuid4())
            print(f"Found CowHouse with ID {building_id}")
            if self.cow_counts.get(building_id , 0) < self.max_cows:
                for rect in self.hit_rects:
                    if rect.collidepoint(point):
                        x = rect.x // TILE_SIZE
                        y = rect.y // TILE_SIZE
                        if self.grid[y][x].count('B') < 5:
                            self.grid[y][x].append('B')
                            self.cow_relations[building_id].append(cow_id)
                            print("Cow can be created")
                            print("Creating cow...")
                            cow = CowTile(
                                pos=((x * TILE_SIZE) + cow_spawn_offset, (y * TILE_SIZE) + cow_spawn_offset),
                                groups=[self.all_sprites, self.cow_sprites, self.collision_sprites],
                                name='Cow',
                                cow_id = cow_id,
                                building_id = building_id,
                                fed = False,
                                feed_interval = 1,
                                last_fed_time = self.last_fed_time,
                                objects = self.cow_houses
                            )
                            self.cow_houses.append(cow)
                            print("Cow created successfully.")
                            self.building_layer.save_objects_cow()
                            print("saved cw")
                            return
        if not self.cow_house_found:
         print("No CowHouse found in the loaded objects.")
        print("Finished checking.")
                    
    def feed_chicken(self, plant_type, player_rect):
        print("Checking for Feed...")
        for obj in self.chicken_houses:
         if obj.name == 'Chicken' and obj.hitbox.colliderect(player_rect):
             if not obj.fed and plant_type == 'corn' and obj.chicken_id:
                obj.fed = True
                obj.last_fed_time = time.time()
                print(f"Last fed time for Chicken ID {obj.chicken_id}: {obj.last_fed_time}")
                obj.plant_type = plant_type
                print(f"Chicken with ID {obj.chicken_id} fed successfully.")
                break
             elif obj.fed:
                print(f"Chicken with ID {obj.chicken_id} has already been fed.")
             else:
                print(f"Chicken with ID {obj.chicken_id} cannot be fed with {plant_type}.")
        else:
           print("No chicken found to feed.")

    def update_chicken(self, dt):
        current_time = time.time()
        print(f"Current time: {current_time}")
        for obj in self.chicken_houses:
            if obj.name == 'Chicken':
               obj.update(dt)

               if obj.chicken_id and obj.feed_interval:
                   if current_time - obj.last_fed_time >= obj.feed_interval:
                       self.spawn_egg(obj)
                       obj.fed = False

    def spawn_egg(self, chicken):
        if chicken.fed:
           print(f"Checking if chicken is fed: {chicken.fed}")
           egg = Egg(pos=(chicken.rect.x, chicken.rect.y), 
                  groups=[self.all_sprites, self.collision_sprites, self.egg_sprites])
           self.egg_sprites.add(egg)
           print(f"Egg laid by Chicken with ID {chicken.chicken_id}.")
        else:
           print(f"Chicken with ID {chicken.chicken_id} needs to be fed before laying eggs.")

    def feed_cow(self, plant_type, player_rect):
        print("Checking for Feed...")
        for obj in self.cow_houses:
         if obj.name == 'Cow' and obj.hitbox.colliderect(player_rect):
             if not obj.fed and plant_type == 'tomato' and obj.cow_id:
                obj.fed = True
                obj.last_fed_time = time.time()
                print(f"Last fed time for Cow ID {obj.cow_id}: {obj.last_fed_time}")
                obj.plant_type = plant_type
                print(f"Cow with ID {obj.cow_id} fed successfully.")
                break
             elif obj.fed:
                print(f"Cow with ID {obj.cow_id} has already been fed.")
             else:
                print(f"Cow with ID {obj.cow_id} cannot be fed with {plant_type}.")
        else:
           print("No Cow found to feed.")

    def update_cow(self, dt):
        current_time = time.time()
        print(f"Current time: {current_time}")
        for obj in self.cow_houses:
            if obj.name == 'Cow':
               obj.update(dt)

               if obj.cow_id and obj.feed_interval:
                   if current_time - obj.last_fed_time >= obj.feed_interval:
                       self.spawn_milk(obj)
                       obj.fed = False

    def spawn_milk(self, cow):
        if cow.fed:
           print(f"Checking if cow is fed: {cow.fed}")
           milk = Milk(pos=(cow.rect.x, cow.rect.y), 
                  groups=[self.all_sprites, self.collision_sprites, self.milk_sprites])
           self.milk_sprites.add(milk)
           print(f"Milk laid by Cow with ID {cow.cow_id}.")
        else:
           print(f"Cow with ID {cow.cow_id} needs to be fed before laying milk.")



                    
                    
                    
                    

                    

            

    


    

                    
                    


