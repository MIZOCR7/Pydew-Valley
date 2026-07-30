import pygame 
from scripts.settings import *
from scripts.player import Player
from scripts.overlay import Overlay
from scripts.sprites import Generic, Water, WildFlower, Trees, Interaction, Particle
from pytmx.util_pygame import load_pygame 
from scripts.support import * 
from scripts.transition import Transition
from scripts.soil import SoilLayer 
from scripts.atmosphere import Rain, Sky
from scripts.main_menu import Menu

from random import randint, random, choice

class Level:
  def __init__(self):
    
    self.display_surface = pygame.display.get_surface()
    
    self.all_sprites = Camera() 
    self.collision_sprites = pygame.sprite.Group() 
    self.tree_sprites = pygame.sprite.Group() 
    self.interaction_sprites = pygame.sprite.Group()
    
    self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
    self.setup()
    self.overlay = Overlay(self.player) 
    self.transition = Transition(self.reset, self.player) 
    self.rain = Rain(self.all_sprites)
    self.raining = randint(0,10) > 3
    self.soil_layer.raining = self.raining
    self.sky = Sky()
    self.shop_active = False
    
    self.menu = Menu(self.player, self.toggle_shop) 
     
    
  
  def setup(self):
    tmx_data = load_pygame('assets/data/map.tmx') 
    for layer in ['HouseFloor', 'HouseFurnitureBottom']: 
      for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
        Generic((x*TILE_SIZE,y*TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
    
    for layer in ['HouseWalls', 'HouseFurnitureTop']:
      for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
        Generic((x*TILE_SIZE,y*TILE_SIZE), surf, self.all_sprites)
    
    for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
      Generic((x*TILE_SIZE,y*TILE_SIZE), surf, self.all_sprites) 
    
    water_frames = import_folder('assets/graphics/water') 
    for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
      Water((x*TILE_SIZE, y*TILE_SIZE), water_frames, self.all_sprites) 
    
    
    for obj in tmx_data.get_layer_by_name('Decoration'):
      WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites]) 
    
    
    for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
      Generic((x*TILE_SIZE, y*TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites) 
    
    
    for obj in tmx_data.get_layer_by_name('Player'):
      if obj.name == 'Start':  
        self.player = Player(
          pos=(obj.x, obj.y), 
          group = self.all_sprites, 
          collision_sprites=self.collision_sprites, 
          tree_sprites=self.tree_sprites,
          interaction=self.interaction_sprites,
          soil_layer=self.soil_layer,
          toggle_shop = self.toggle_shop,) 
        
      if obj.name == 'Bed':
        Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name) 
      
      if obj.name == 'Trader':
        Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name) 
      
      
    Generic(pos=(0,0), surf=pygame.image.load('assets/graphics/world/ground.png').convert_alpha(), groups=self.all_sprites , z = LAYERS['ground']) 
    
    
    for obj in tmx_data.get_layer_by_name('Trees'):
      Trees(
        pos=(obj.x, obj.y), 
        surf=obj.image, 
        groups=[self.all_sprites, self.collision_sprites, self.tree_sprites], name=obj.name,
        player_add=self.player_add) 
    
  
  def player_add(self, item):
    self.player.item_inventory[item] += 1 
  
  
  def toggle_shop(self):
    self.shop_active = not self.shop_active 
  
  
  def reset(self):
    
    self.soil_layer.update_plants() 
    
    
    self.soil_layer.remove_water()
    self.raining = randint(0,10) > 3
    self.soil_layer.raining = self.raining
    if self.raining:
      self.soil_layer.water_all()
    
    for tree in self.tree_sprites.sprites():
      if not hasattr(tree, 'apple_sprites'): continue
      for apple in tree.apple_sprites.sprites():
        apple.kill()
      tree.create_fruit() 
    
    self.sky.start_color = [255, 255, 255] 
    
    
  def plant_collisions(self):
    if self.soil_layer.plant_sprites:
      for plant in self.soil_layer.plant_sprites.sprites():
        if plant.harvastable and plant.rect.colliderect(self.player.hitbox):
          self.player_add(plant.plant_type)
          plant.kill() 
          Particle((plant.rect.topleft), plant.image, self.all_sprites, z = LAYERS['main'])
          self.soil_layer.grid[plant.rect.centery//TILE_SIZE][plant.rect.centerx//TILE_SIZE].remove('P')  
          
  
  
  def run(self, dt):
    
    
    
    self.display_surface.fill((0,0,0))
    self.all_sprites.custom_draw(self.player) 
    
    if self.shop_active:
      self.menu.update()
    else:
      self.all_sprites.update(dt)
      self.plant_collisions()
     
    
    self.overlay.display()
    
    if self.raining and not self.shop_active:
      self.rain.update()
    
    self.sky.display(dt) 
    
    
    if self.player.sleep:
      self.transition.play(dt) 
    
    
    
    
    
    
  
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
          
  
  
