import pygame
from Utils.settings import *
from Utils.timer import Timer

class Menu:
    def __init__(self, player, toggle_menu):
        self.player = player
        self.toggle_menu = toggle_menu
        self.display_surface = pygame.display.get_surface()
        self.font_size = 30
        self.font = pygame.font.Font('../font/Soda.ttf', self.font_size)

        self.width = 400
        self.space = 10
        self.padding = 8

        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys()) + list(self.player.animals_inventory.keys())
        self.sell_border = len(self.player.item_inventory) - 1
        self.setup()

        self.initial_screen_width = SCREEN_WIDTH
        self.initial_screen_height = SCREEN_HEIGHT
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0

        self.index = 0
        self.timer = Timer(200)

    def display_money(self):
        text_surf = self.font.render(f'{self.player.money}$', False, 'Black')
        text_rect = text_surf.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))

        pygame.draw.rect(self.display_surface, 'White', text_rect.inflate(10, 10), 0, 6)
        self.display_surface.blit(text_surf, text_rect)

    def setup(self):
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)

        self.buy_text = self.font.render('Buy', False, 'Black')
        self.sell_text = self.font.render('Sell', False, 'Black')

    def input(self):
        keys = pygame.key.get_pressed()
        self.timer.update()

        if keys[pygame.K_ESCAPE]:
            self.toggle_menu()

        if not self.timer.active:
            if keys[pygame.K_UP]:
                self.index -= 1
                self.timer.activate()

            if keys[pygame.K_DOWN]:
                self.index += 1
                self.timer.activate()

            if keys[pygame.K_SPACE]:
                self.timer.activate()

                current_item = self.options[self.index]

                if self.index <= self.sell_border:
                    if self.player.item_inventory[current_item] > 0:
                        self.player.item_inventory[current_item] -= 1
                        self.player.money += SALE_PRICES[current_item]
                else:
                    if current_item in self.player.seed_inventory:
                        seed_price = PURCHASEE_PRICES[current_item]
                        if self.player.money >= seed_price:
                            self.player.seed_inventory[current_item] += 1
                            self.player.money -= seed_price
                        else:
                            print("Not enough money to purchase seeds.")
                    elif current_item in self.player.animals_inventory:
                        animal_price = PURCHASEE_PRICES[current_item]
                        if self.player.money >= animal_price:
                            self.player.animals_inventory[current_item] += 1
                            self.player.money -= animal_price
                        else:
                            print("Not enough money to purchase animals.")
                    else:
                        print(f"Error: {current_item} not found in inventory.")

        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0

    def update_menu_scale(self, new_width, new_height):
        self.scale_factor_x = new_width / self.initial_screen_width
        self.scale_factor_y = new_height / self.initial_screen_height

        self.width *= self.scale_factor_x
        self.main_rect.width *= self.scale_factor_x
        self.main_rect.height *= self.scale_factor_y
        self.menu_top = new_height / 2 - self.total_height / 2  
        self.total_height = 0  

        scaled_font_size = int(self.font_size * min(self.scale_factor_x, self.scale_factor_y))
        self.font = pygame.font.Font('../font/Soda.ttf', scaled_font_size)

        self.text_surfs.clear()

        for item in self.options:
            text_surf = self.font.render(item, False, 'Black')
            scaled_text_surf = pygame.transform.scale(text_surf, (int(text_surf.get_width() * self.scale_factor_x), int(text_surf.get_height() * self.scale_factor_y)))
            self.text_surfs.append(scaled_text_surf)
            self.total_height += scaled_text_surf.get_height() + (self.padding * 2)

        self.total_height += (len(self.text_surfs) - 1) * self.space

        self.main_rect = pygame.Rect(new_width / 2 - self.width / 2, self.menu_top, self.width, self.total_height)  

        self.buy_text = self.font.render('Buy', False, 'Black')
        self.sell_text = self.font.render('Sell', False, 'Black')
        buy_text_width = self.buy_text.get_width() * self.scale_factor_x
        sell_text_width = self.sell_text.get_width() * self.scale_factor_x
        text_spacing = 20 * self.scale_factor_x  

        self.buy_text_pos = (self.main_rect.left + (self.main_rect.width - buy_text_width) / 2, self.menu_top + (self.index * (self.font_size + self.padding * 2 + self.space)))
        self.sell_text_pos = (self.main_rect.left + (self.main_rect.width - sell_text_width) / 2, self.menu_top + (self.index * (self.font_size + self.padding * 2 + self.space)))

        if self.buy_text_pos[0] < self.main_rect.left:
           self.buy_text_pos = (self.main_rect.left, self.buy_text_pos[1])
        if self.buy_text_pos[0] + buy_text_width > self.main_rect.right:
           self.buy_text_pos = (self.main_rect.right - buy_text_width, self.buy_text_pos[1])

        if self.sell_text_pos[0] < self.main_rect.left:
           self.sell_text_pos = (self.main_rect.left, self.sell_text_pos[1])
        if self.sell_text_pos[0] + sell_text_width > self.main_rect.right:
           self.sell_text_pos = (self.main_rect.right - sell_text_width, self.sell_text_pos[1])



    def show_entry(self, text_surf, amount, top, selected):
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height() + (self.padding * 2))
        pygame.draw.rect(self.display_surface, 'White', bg_rect, 0, 4)

        text_rect = text_surf.get_rect(midleft=(self.main_rect.left + 20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        amount_surf = self.font.render(str(amount), False, 'Black')
        amount_rect = amount_surf.get_rect(midright=(self.main_rect.right - 20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect, 4, 4)
            if self.index <= self.sell_border:
                pos_rect = self.sell_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.sell_text, pos_rect)
            else:
                pos_rect = self.buy_text.get_rect(midleft=(self.main_rect.left + 150, bg_rect.centery))
                self.display_surface.blit(self.buy_text, pos_rect)

    def update(self):
        current_width = pygame.display.get_surface().get_width()
        current_height = pygame.display.get_surface().get_height()

        if current_width != self.initial_screen_width or current_height != self.initial_screen_height:
           self.update_menu_scale(current_width, current_height)
           self.initial_screen_width = current_width
           self.initial_screen_height = current_height

        self.input()
        self.display_money()
        amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values()) + list(self.player.animals_inventory.values())

        for text_index, text_surf in enumerate(self.text_surfs):
            if text_index < len(amount_list): 
               top = self.main_rect.top + text_index * (text_surf.get_height() + (self.padding * 2) + self.space)
               amount = amount_list[text_index]
               self.show_entry(text_surf, amount, top, self.index == text_index)
            else:
               print(f"Warning: text_index {text_index} is out of range for amount_list.")
