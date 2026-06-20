import pygame
from Utils.settings import *
from Utils.support import *
from Utils.timer import Timer
from math import sin



class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, building_layer, chicken_layer, cow_layer, npc_layer, create_attack, destroy_attack, toggle_shop):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.z = LAYERS['main']

        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 500
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.hitbox = self.rect.copy().inflate((-110, -40))
        self.collision_sprites  = collision_sprites

        self.health = 1000
        self.max_health = 1000
        self.experience = 0
        self.max_experience = 50
        self.level = 1

        self.health_bar_color = (255, 0, 0)
        self.experience_bar_color = (0, 0, 255)
        self.max_health_bar_width = 100
        self.experience_bar_width = 100
        self.font_size = 30
        self.font = pygame.font.Font('../font/Soda.ttf', self.font_size)

        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch' : Timer(200),
            'seed use': Timer(300, self.use_seed),
            'seed switch' : Timer(150),
            'animal add': Timer(300, self.add_animal),
            'animal switch' : Timer(150),
            'animal feed': Timer(300, self.feed_animal),
            'building switch': Timer(200)
        }

        self.tasks_by_level = {
            1: [
                {'description': 'Collect 201 wood', 'completed': False, 'reward': 50, 'experience': 5, 'requirement': {'item': 'wood', 'quantity': 201}},
                {'description': 'Plant 5 corn seeds', 'completed': False, 'reward': 30, 'experience': 5, 'requirement': {'seed': 'corn', 'quantity': 5}},
                {'description': 'Build chickenhouse', 'completed': False, 'reward': 20, 'experience': 5, 'requirement': {'building': 'chickenhouse', 'quantity': 1}}
            ],
            2: [
                {'description': 'Collect 500 wood', 'completed': False, 'reward': 100, 'experience': 10, 'requirement': {'item': 'wood', 'quantity': 500}},
                {'description': 'Plant 10 tomato seeds', 'completed': False, 'reward': 60, 'experience': 9, 'requirement': {'seed': 'tomato', 'quantity': 10}},
                {'description': 'Build cowhouse', 'completed': False, 'reward': 40, 'experience': 10, 'requirement': {'building': 'cowhouse', 'quantity': 1}}
            ]
        }

        self.tasks = {f'task{i+1}': task for i, task in enumerate(self.tasks_by_level[1])}
        self.show_tasks = False
        self.all_tasks_completed = False

        self.tools = ['hoe', 'axe', 'water', 'hammer']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]


        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        self.seeds_planted = {
            'corn': 0,
            'tomato': 0
        }

        self.animals = ['chicken', 'cow']
        self.animal_index = 0
        self.selected_animal = self.animals[self.animal_index]

        self.item_inventory = {

            'wood' :   200,
            'apple':   5,
            'corn' :   5,
            'tomato' : 5,
            'egg' : 0,

        }

        self.seed_inventory = {
            'corn': 10,
            'tomato': 10
        }

        self.initial_corn_seeds = self.seed_inventory['corn']

        self.animals_inventory = {

            'chicken': 5,
            'cow' : 5
        }

        self.money = 100

        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer
        self.building_layer = building_layer
        self.chicken_layer = chicken_layer
        self.cow_layer = cow_layer
        self.npc_layer = npc_layer
        self.toggle_shop = toggle_shop
        self.chicken_house_count = 0
        self.cow_house_count = 0
        self.attack_range = 5 
        self.damage = 10
        self.additional_offset = Vector2(20, 20)
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.show_completion_window = False
        self.completion_window_rect = pygame.Rect(self.screen_width // 4, self.screen_height // 4, self.screen_width // 2, self.screen_height // 2)
        self.continue_button_rect = pygame.Rect(self.completion_window_rect.centerx - 50, self.completion_window_rect.bottom - 60, 100, 40)
        self.show_dialogue_window = False
        self.dialogue_window_rect = pygame.Rect(self.screen_width // 4, self.screen_height // 4, self.screen_width // 2, self.screen_height // 2)
       
        button_width = 100
        button_height = 40
        button_margin = 10

        self.agree_button_rect = pygame.Rect(
            self.dialogue_window_rect.centerx - button_width - button_margin / 2, 
            self.dialogue_window_rect.bottom - button_height - 20, 
            button_width, 
            button_height
        )
        self.disagree_button_rect = pygame.Rect(
            self.dialogue_window_rect.centerx + button_margin / 2, 
            self.dialogue_window_rect.bottom - button_height - 20, 
            button_width, 
            button_height
        )

        self.cursor_image = pygame.image.load('../graphics/cursor/cursor.png')

        self.watering = pygame.mixer.Sound('../audio/water.mp3')
        self.success = pygame.mixer.Sound('../audio/success.wav')
        self.success.set_volume(0.4)

    def take_damage(self, damage):
        self.health -= damage
        self.health = max(self.health, 0)
        self.draw_health_bar(self.screen)
    
    def draw_health_bar(self, screen):
        health_percentage = (self.health / self.max_health) * 100
        health_bar_width = int((health_percentage / 100) * self.max_health_bar_width)

        health_bar_rect = pygame.Rect(10, 10, health_bar_width, 10)
        pygame.draw.rect(screen, self.health_bar_color, health_bar_rect)

        health_text = f'Health: {self.health}'
        text_surface = self.font.render(health_text, True, (255, 255, 255))
        screen.blit(text_surface, (health_bar_rect.right + 10, health_bar_rect.top))

    def gain_experience(self, experience_points):
        self.experience += experience_points
        if self.experience >= self.max_experience:
            self.level += 1
            self.experience -= self.max_experience
            self.max_experience += 10
            self.experience_bar_width = self.max_experience

            if self.all_tasks_completed:
                print('All tasks completed, assigning new tasks.')
                self.assign_new_tasks()

    def assign_new_tasks(self):
        if self.level in self.tasks_by_level:
            self.tasks = {f'task{i+1}': task for i, task in enumerate(self.tasks_by_level[self.level])}
            self.show_completion_window = False
            self.show_tasks = True
            self.all_tasks_completed = False
            print(f'New tasks assigned for level {self.level}.')
 
    def draw_experience_bar(self, screen):
        experience_ratio = self.experience / self.max_experience
        experience_bar_width = int(self.experience_bar_width * 2 * experience_ratio)
        experience_bar_rect = pygame.Rect(10, 50, experience_bar_width, 10)
        experience_color = (0, 0, 255)
        pygame.draw.rect(screen, experience_color, experience_bar_rect)

        level_text = f'Level: {self.level}'
        text_surface = self.font.render(level_text, True, (255, 255, 255))
        screen.blit(text_surface, (experience_bar_rect.right + 10, experience_bar_rect.top))

        remaining_experience = self.max_experience - self.experience
        remaining_text = f'Next Level: {remaining_experience} XP'
        remaining_surface = self.font.render(remaining_text, True, (255, 255, 255))
        screen.blit(remaining_surface, (SCREEN_WIDTH - remaining_surface.get_width() - 30, 30))

    def draw_text(self, text, font, color, rect):
        lines = []
        words = text.split()
        width, height = rect.size
        space_width, _ = font.size(' ')
        
        current_line = []
        current_width = 0
        for word in words:
            word_width, _ = font.size(word)
            if current_width + word_width + space_width > width:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width + space_width
        
        lines.append(' '.join(current_line)) 

        total_text_height = len(lines) * font.get_height()
        start_y = rect.top + (rect.height - total_text_height) // 2

        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect()
            line_rect.midtop = (rect.centerx, start_y + i * font.get_height())
            self.screen.blit(line_surface, line_rect)

    def draw_completion_window(self):
        pygame.draw.rect(self.screen, (0, 0, 0), self.completion_window_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.completion_window_rect, 5)

        completion_text = "You get stronger, but can you overcome all the challenges along the way..."
        self.draw_text(completion_text, self.font, (255, 255, 255), self.completion_window_rect)

        mouse_pos = pygame.mouse.get_pos()

        if self.continue_button_rect.collidepoint(mouse_pos):
            button_color = (0, 200, 0)
            if pygame.mouse.get_pressed()[0]:
                self.show_completion_window = False
                pygame.mouse.set_visible(False)
        else:
            button_color = (0, 255, 0)

        pygame.draw.rect(self.screen, button_color, self.continue_button_rect)
        button_text = "Continue"
        button_surface = self.font.render(button_text, True, (0, 0, 0))
        button_rect = button_surface.get_rect(center=self.continue_button_rect.center)
        self.screen.blit(button_surface, button_rect)

    def draw_dialogue_window(self):
        pygame.draw.rect(self.screen, (0, 0, 0), self.dialogue_window_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.dialogue_window_rect, 5)

        dialogue_text = "Will you help a poor old man with materials to build a new house....(Will you give up 100 units of wood?)"
        self.draw_text(dialogue_text, self.font, (255, 255, 255), self.dialogue_window_rect)

        mouse_pos = pygame.mouse.get_pos()

        if self.agree_button_rect.collidepoint(mouse_pos):
            agree_button_color = (0, 200, 0)
            if pygame.mouse.get_pressed()[0]:
                self.item_inventory['wood'] -= 100
                self.npc_layer.kill()
                self.show_dialogue_window = False
                pygame.mouse.set_visible(False)
        else:
            agree_button_color = (0, 255, 0)

        pygame.draw.rect(self.screen, agree_button_color, self.agree_button_rect)
        agree_button_text = "Agree"
        agree_button_surface = self.font.render(agree_button_text, True, (0, 0, 0))
        agree_button_rect = agree_button_surface.get_rect(center=self.agree_button_rect.center)
        self.screen.blit(agree_button_surface, agree_button_rect)

        if self.disagree_button_rect.collidepoint(mouse_pos):
            disagree_button_color = (200, 0, 0)
            if pygame.mouse.get_pressed()[0]:
                self.npc_layer.kill()
                self.health -= int(0.99 * self.health)
                self.show_dialogue_window = False
                pygame.mouse.set_visible(False)
        else:
            disagree_button_color = (255, 0, 0)

        pygame.draw.rect(self.screen, disagree_button_color, self.disagree_button_rect)
        disagree_button_text = "Disagree"
        disagree_button_surface = self.font.render(disagree_button_text, True, (0, 0, 0))
        disagree_button_rect = disagree_button_surface.get_rect(center=self.disagree_button_rect.center)
        self.screen.blit(disagree_button_surface, disagree_button_rect)


    def check_tasks_completion(self):
     if not self.tasks:
        return
     tasks_to_remove = []

     for task_name, task_data in self.tasks.items():
        if not task_data['completed']:
            requirement = task_data['requirement']
            if 'item' in requirement:
                if self.item_inventory.get(requirement['item'], 0) >= requirement['quantity']:
                    task_data['completed'] = True
                    self.money += task_data['reward']
                    self.gain_experience(task_data['experience'])
                    self.success.play()
                    print(f'Completed task: {task_data["description"]}. Reward: {task_data["reward"]} coins.')
                    tasks_to_remove.append(task_name)

            if 'seed' in requirement:
                if self.seeds_planted.get(requirement['seed'], 0) >= requirement['quantity']:
                    task_data['completed'] = True
                    self.money += task_data['reward']
                    self.gain_experience(task_data['experience'])
                    self.success.play()
                    print(f'Completed task: {task_data["description"]}. Reward: {task_data["reward"]} coins.')
                    tasks_to_remove.append(task_name)

            if 'building' in requirement:
                if requirement['building'] == 'chickenhouse' and self.chicken_house_count >= requirement['quantity']:
                    task_data['completed'] = True
                    self.money += task_data['reward']
                    self.gain_experience(task_data['experience'])
                    self.success.play()
                    print(f'Completed task: {task_data["description"]}. Reward: {task_data["reward"]} coins.')
                    tasks_to_remove.append(task_name)
                elif requirement['building'] == 'cowhouse' and self.cow_house_count >= requirement['quantity']:
                    task_data['completed'] = True
                    self.money += task_data['reward']
                    self.gain_experience(task_data['experience'])
                    self.success.play()
                    print(f'Completed task: {task_data["description"]}. Reward: {task_data["reward"]} coins.')
                    tasks_to_remove.append(task_name)

     for task_name in tasks_to_remove:
        del self.tasks[task_name]

     if not self.tasks:
        self.show_tasks = False
        self.all_tasks_completed = True
        self.show_completion_window = True

    def display_tasks(self, screen):
        if self.show_tasks:
            task_font = pygame.font.Font('../font/Soda.ttf', self.font_size)
            task_margin = 10
            y_offset = 10
            screen_center = (screen.get_width() // 2, screen.get_height() // 2)

            tasks_to_remove = []

            for task_name, task_data in self.tasks.items():
                task_text = f'{task_data["description"]} - Reward: {task_data["reward"]} coins'
                task_surface = task_font.render(task_text, True, (255, 255, 255))
                task_rect = task_surface.get_rect(center=(screen_center[0], y_offset))
                screen.blit(task_surface, task_rect)
                y_offset += task_surface.get_height() + task_margin

                if task_data['completed']:
                    tasks_to_remove.append(task_name)

            for task_name in tasks_to_remove:
                del self.tasks[task_name]

            if not self.tasks:
                self.show_tasks = False
    
    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)

        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()

        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
            self.watering.play()
            self.watering.set_volume(0.2)

        if self.selected_tool == 'hammer':
            selected_building = self.building_layer.available_buildings[self.building_layer.selected_building_index]
            if self.item_inventory['wood'] > COAST['chickenhouse']:
                if selected_building == 'chickenhouse':
                    self.building_layer.chicken_house(self.target_pos + self.additional_offset)
                    self.success.play()
                    self.gain_experience(15)
                    self.chicken_house_count += 1 
                    self.item_inventory['wood'] -= 15
                elif selected_building == 'cowhouse':
                    self.item_inventory['wood'] > COAST['cowhouse']
                    self.building_layer.cow_house(self.target_pos + self.additional_offset)
                    self.success.play()
                    self.gain_experience(25)
                    self.cow_house_count += 1 
                    self.item_inventory['wood'] -= 25

    def draw_selected_building(self, screen):
        if self.selected_tool == 'hammer':
            selected_building = self.building_layer.available_buildings[self.building_layer.selected_building_index]
            building_image = self.building_layer.building_images[selected_building]
            image_rect = building_image.get_rect(center=(self.screen_width // 2, 90))
            screen.blit(building_image, image_rect)

    def get_target_pos(self):

        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]


    def use_seed(self):
        if self.seed_inventory[self.selected_seed] > 0:
           self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
           self.seed_inventory[self.selected_seed] -= 1
           self.seeds_planted[self.selected_seed] += 1

    def add_animal(self):
        if self.selected_animal == 'chicken':
            if self.animals_inventory['chicken'] >= 1:
               self.chicken_layer.create_chicken(self.rect, self.target_pos)
               self.animals_inventory['chicken'] -= 1
               self.gain_experience(10)
            else:
                print('Error')
        elif self.selected_animal == 'cow':
             if self.animals_inventory['cow'] >= 1:
                self.cow_layer.create_cow(self.rect, self.target_pos)
                self.animals_inventory['cow'] -= 1
                self.gain_experience(20)
             else:
                print('Error')

    def feed_animal(self):
        if self.seed_inventory[self.selected_seed] > 0 and self.selected_seed == 'corn':
           self.chicken_layer.feed_chicken(self.selected_seed, self.rect)
           self.seed_inventory['corn'] -= 1
        elif self.seed_inventory[self.selected_seed] > 0 and self.selected_seed == 'tomato':
           self.cow_layer.feed_cow(self.selected_seed, self.rect)
           self.seed_inventory['tomato'] -= 2
                

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': [],
                           'right_hammer': [], 'left_hammer': [], 'up_hammer': [], 'down_hammer': [],
                           'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[],
                           'right_chicken': [], 'left_chicken': [], 'up_chicken': [], 'down_chicken': [],
                           'right_cow': [], 'left_cow': [], 'up_cow': [], 'down_cow': [],}
        
        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
       self.frame_index += 4* dt
       if self.frame_index >= len(self.animations[self.status]):
           self.frame_index = 0

       self.image = self.animations[self.status][int(self.frame_index)]
       self.rect = self.image.get_rect(center = self.hitbox.center)
		# flicker 
       if not self.vulnerable:
          alpha = self.wave_value()
          self.image.set_alpha(alpha)
       else:
          self.image.set_alpha(255)

        
    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['tool use'].active and not self.sleep: 
			
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            if keys[pygame.K_q] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                self.tool_index = self.tool_index if self.tool_index < len(self.tools) else 0
                self.selected_tool = self.tools[self.tool_index]

            if keys[pygame.K_LCTRL]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            if keys[pygame.K_e] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                self.seed_index += 1
                self.seed_index = self.seed_index if self.seed_index < len(self.seeds) else 0
                self.selected_seed = self.seeds[self.seed_index]

            if keys[pygame.K_r]:
                self.timers['animal add'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            if keys[pygame.K_t]:
                self.timers['animal feed'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0

            if keys[pygame.K_f] and not self.timers['animal switch'].active:
                self.timers['animal switch'].activate()
                self.animal_index += 1
                self.animal_index = self.animal_index if self.animal_index < len(self.animals) else 0
                self.selected_animal = self.animals[self.animal_index]

            if keys[pygame.K_b] and not self.timers['building switch'].active:
                self.timers['building switch'].activate()
                self.building_layer.selected_building_index += 1
                if self.building_layer.selected_building_index >= len(self.building_layer.available_buildings):
                    self.building_layer.selected_building_index = 0

            if keys[pygame.K_x] and not self.attacking:
               self.attacking = True
               self.attack_time = pygame.time.get_ticks()
               self.create_attack()

            if keys[pygame.K_y] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
				
                if self.weapon_index < len(list(weapon_data.keys())) - 1:
                    self.weapon_index += 1
                else:
                   self.weapon_index = 0
					
                self.weapon = list(weapon_data.keys())[self.weapon_index]
            
            if keys[pygame.K_l]:
                if self.npc_layer and self.target_pos:
                    self.show_dialogue_window = True
                else:
                    self.status = 'left_idle'
                    self.sleep = True

            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'Trader':
                        self.toggle_shop()
                    else:
                        self.status = 'left_idle'
                        self.sleep = True
    
    def get_status(self):
        if self.direction.magnitude() == 0:
           if not 'idle' in self.status and not 'attack' in self.status:
              self.status = self.status.split('_')[0] + '_idle'

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
               if 'idle' in self.status:
                     self.status = self.status.replace('_idle','_attack')
               else:
                     self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                 self.status = self.status.replace('_attack','')
        
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

        if self.timers['animal add'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_animal

    def cooldowns(self):
         current_time = pygame.time.get_ticks()

         if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()

         if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

         if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
               self.vulnerable = True

    def get_full_weapon_damage(self):
        weapon_damage = weapon_data[self.weapon]['damage']
        return weapon_damage

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

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

        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

        self.rect.center = self.hitbox.center

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0: 
           return 255
        else: 
           return 0


    def update(self, dt):
        if self.show_completion_window:
            pygame.mouse.set_visible(True)
            cursor = pygame.cursors.Cursor((0, 0), self.cursor_image)
            pygame.mouse.set_cursor(cursor)
            self.draw_completion_window()
        elif self.show_dialogue_window:
            pygame.mouse.set_visible(True)
            cursor = pygame.cursors.Cursor((0, 0), self.cursor_image)
            pygame.mouse.set_cursor(cursor)
            self.draw_dialogue_window()
        else:
            self.input()
            self.get_status()
            self.update_timers()
            self.get_target_pos()
            self.move(dt)
            self.animate(dt)
            self.cooldowns()
            self.draw_selected_building(self.screen)
            self.draw_health_bar(self.screen)
            self.draw_experience_bar(self.screen)
            self.check_tasks_completion()
            self.display_tasks(self.screen)
            self.npc_layer.spawn(self.level)


