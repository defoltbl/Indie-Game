import pygame
from Utils.settings import *

class Overlay:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player

        self.overlay_height = self.display_surface.get_height() // 10 
        self.element_spacing = self.overlay_height // 5  
        
        overlay_path = '../graphics/overlay/'
        self.tools_surf = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}
        self.animals_surf = {animal: pygame.image.load(f'{overlay_path}{animal}.png').convert_alpha() for animal in player.animals}
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            path = weapon['graphic']
            weapon = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon)

    def display(self, player):
        self.player = player
        tool_x = 10
        seed_x = 10 + self.overlay_height + self.element_spacing
        animal_x = self.display_surface.get_width() - 10

        tool_y = self.display_surface.get_height() - 10
        seed_y = self.display_surface.get_height() - 10
        animal_y = self.display_surface.get_height() - 10

        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(bottomleft=(tool_x, tool_y))
        self.display_surface.blit(tool_surf, tool_rect)

        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(bottomleft=(seed_x, seed_y))
        self.display_surface.blit(seed_surf, seed_rect)

        animal_surf = self.animals_surf[self.player.selected_animal]
        animal_rect = animal_surf.get_rect(bottomright=(animal_x, animal_y))
        self.display_surface.blit(animal_surf, animal_rect)

        self.weapon_overlay(player.weapon_index,not player.can_switch_weapon)


    def selection_box(self,left,top, has_switched):
        bg_rect = pygame.Rect(left,top,ITEM_BOX_SIZE,ITEM_BOX_SIZE)
        pygame.draw.rect(self.display_surface,UI_BG_COLOR,bg_rect)
        if has_switched:
            pygame.draw.rect(self.display_surface,UI_BORDER_COLOR_ACTIVE,bg_rect,3)
        else:
           pygame.draw.rect(self.display_surface,UI_BORDER_COLOR,bg_rect,3)
        return bg_rect

    def weapon_overlay(self, weapon_index, has_switched):
     screen_width, screen_height = self.display_surface.get_size()

     overlay_width = screen_width // 30 
     overlay_height = overlay_width  

     overlay_x = (screen_width - overlay_width) // 6  
     overlay_y = screen_height - overlay_height - 10  

     bg_rect = pygame.Rect(overlay_x, overlay_y, overlay_width, overlay_height)
     pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
     if has_switched:
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
     else:
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

     weapon_surf = self.weapon_graphics[weapon_index]
     weapon_surf = pygame.transform.scale(weapon_surf, (overlay_width, overlay_height))
     weapon_rect = weapon_surf.get_rect(center=bg_rect.center)
     self.display_surface.blit(weapon_surf, weapon_rect)


    def update_overlay_positions(self, screen_width, screen_height):
      for key in OVERLAY_POSITIONS:
        x_ratio, y_ratio = OVERLAY_POSITIONS[key]

        x = int(x_ratio * screen_width)
        y = int(y_ratio * screen_height)

        if key in ['tool', 'seed', 'animal']:
            element_width = int(screen_width * 0.1) 
            element_height = int(screen_height * 0.1) 
        else:
            element_width, element_height = 0, 0

        x -= element_width // 2
        y -= element_height

        OVERLAY_POSITIONS[key] = (x, y)

