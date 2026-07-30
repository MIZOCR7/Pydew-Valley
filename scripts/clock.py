import pygame


class Clock:
  def __init__(self, time_speed = 1):
    
    self.display_surf = pygame.display.get_surface()
    self.time_speed = time_speed
    self.minutes_total = 6 * 60
    
    self.font = pygame.font.Font('assets/font/LycheeSoda.ttf', 50)
  
  def update(self, dt):
    self.minutes_total += dt * 60 * self.time_speed
    
    if self.minutes_total >= 1440:
      self.minutes_total -= 1440 
    
  def get_hours(self):
    return int(self.minutes_total // 60)
  
  def get_minutes(self):
    return int(self.minutes_total % 60)
  
  def draw(self):
    hours = self.get_hours()
    minutes = self.get_minutes()
    time_str = f'{hours:02d}:{minutes:02d}'
    
    shadow_surf = self.font.render(time_str, True, (0,0,0))
    text_surf = self.font.render(time_str, True, (255,255,255))
    
    pos = (self.display_surf.get_width() - 110, 20)
    
    self.display_surf.blit(shadow_surf, (pos[0] + 2, pos[1] + 2))
    self.display_surf.blit(text_surf, pos) 
