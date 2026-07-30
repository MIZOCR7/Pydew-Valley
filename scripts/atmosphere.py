import pygame
from scripts.settings import *
from scripts.support import *
from scripts.sprites import Generic
from random import randint, random, choice
from scripts.timer import Timer


class Sky:
  def __init__(self):
    self.display_surface = pygame.display.get_surface()
    self.full_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    self.current_color = [255, 255, 255]

    self.color_curve = [
      (0,   (50, 50, 100)),     # midnight
      (300, (60, 55, 105)),     # 5:00 AM  – pre-dawn
      (360, (180, 130, 90)),    # 6:00 AM  – sunrise
      (420, (255, 210, 170)),   # 7:00 AM  – morning glow
      (540, (255, 245, 230)),   # 9:00 AM  – bright morning
      (720, (255, 255, 255)),   # 12:00 PM – noon
      (900, (255, 250, 240)),   # 3:00 PM  – afternoon
      (1020, (255, 210, 170)),  # 5:00 PM  – golden hour
      (1080, (210, 120, 60)),   # 6:00 PM  – sunset
      (1140, (90, 55, 80)),     # 7:00 PM  – dusk
      (1320, (55, 50, 95)),     # 10:00 PM – night
      (1440, (50, 50, 100)),    # midnight
    ]

  def get_color(self, minutes):
    for i in range(len(self.color_curve) - 1):
      t1, c1 = self.color_curve[i]
      t2, c2 = self.color_curve[i + 1]
      if t1 <= minutes <= t2:
        progress = (minutes - t1) / (t2 - t1)
        r = int(c1[0] + (c2[0] - c1[0]) * progress)
        g = int(c1[1] + (c2[1] - c1[1]) * progress)
        b = int(c1[2] + (c2[2] - c1[2]) * progress)
        return (r, g, b)
    return self.color_curve[-1][1]

  def display(self, minutes):
    color = self.get_color(minutes)
    self.current_color = list(color)
    self.full_surf.fill(self.current_color)
    self.display_surface.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


class Drop(Generic):
  def __init__(self, surf, pos, moving, groups, z):
    
    super().__init__(pos, surf, groups, z) 
    self.lifetime = randint(400, 500)
    self.start_time = pygame.time.get_ticks() 
    
    self.moving = moving
    if self.moving:
      self.pos = pygame.math.Vector2(self.rect.topleft)
      self.direction = pygame.math.Vector2(-2, 4)
      self.speed = randint(200, 250)
      
  def update(self, dt):
    if self.moving:
      self.pos += self.direction * self.speed * dt
      self.rect.topleft = (round(self.pos.x), round(self.pos.y))
      
    if pygame.time.get_ticks() - self.start_time >= self.lifetime:
      self.kill() 


class Rain:
  def __init__(self, all_sprites):
    self.all_sprites = all_sprites
    self.rain_drops = import_folder('assets/graphics/rain/drops/')
    self.rain_floor = import_folder('assets/graphics/rain/floor/')
    self.floor_w, self.floor_h = pygame.image.load('assets/graphics/world/ground.png').get_size()


  def create_floor(self):
    Drop(
      surf = choice(self.rain_floor),
      pos = (randint(0, self.floor_w), randint(0, self.floor_h)),
      moving= False,
      groups = self.all_sprites,
      z = LAYERS['rain floor'], 
    ) 
  
  def create_drops(self):
    Drop(
      surf = (choice(self.rain_drops)),
      pos = (randint(0, self.floor_w), randint(0, self.floor_h)),
      moving= True,
      groups = self.all_sprites,
      z = LAYERS['rain drops'],  
    ) 
  
  def update(self):
    self.create_floor()
    self.create_drops() 
