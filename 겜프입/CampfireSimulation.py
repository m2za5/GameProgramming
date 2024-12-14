import pygame
import os
import random

pygame.init()

low_fire_sound_path = r"C:\Users\2reny\Desktop\겜프입\Resources\SmallFire.mp3"  # 불이 약할 때
high_fire_sound_path = r"C:\Users\2reny\Desktop\겜프입\Resources\FIRE.mp3"  # 불이 활활 탈 때

low_fire_sound = pygame.mixer.Sound(low_fire_sound_path)
high_fire_sound = pygame.mixer.Sound(high_fire_sound_path)

low_fire_sound.set_volume(1)
high_fire_sound.set_volume(1)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
os.environ['SDL_VIDEO_WINDOW_POS'] = '%d, %d' % (150, 50)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Campfire Simulation')

FPS = 60
clock = pygame.time.Clock()

BACKGROUND_COLOR = (30, 35, 35)
WOOD_COLOR = (81, 40, 0)


image_path = r"C:\Users\2reny\Desktop\겜프입\Resources\woodFire.png"
if os.path.exists(image_path):
    campfire_image = pygame.image.load(image_path)
    campfire_image = pygame.transform.scale(campfire_image, (130, 130)) 
    campfire_rect = campfire_image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))


class Wood:
    FALLING = "falling"
    LANDED = "landed"
    BURNING = "burning"
    BURNT = "burnt"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 15
        self.color = [139, 69, 19]  
        self.vertical_speed = 0 
        self.gravity_force = 0.5 
        self.state = Wood.FALLING 
        self.has_landed = False  

    def fall_and_collide_with_ground(self):
        if self.state == Wood.FALLING:
            self.vertical_speed += self.gravity_force 
            self.y += self.vertical_speed

            if self.y + self.height >= campfire_rect.bottom - 50:
                self.y = campfire_rect.bottom - self.height - 50
                self.state = Wood.LANDED
                self.vertical_speed = 0

    def stack_on_other_wood(self, other_wood):
       if (self.x < other_wood.x + other_wood.width and
        self.x + self.width > other_wood.x and
        self.y + self.height > other_wood.y and
        self.y < other_wood.y + other_wood.height):
        self.y = other_wood.y - self.height
        self.has_landed = True
        self.state = Wood.LANDED
        self.vertical_speed = 0


    def burn_and_fade(self):
        if self.state == Wood.BURNING:
            for i in range(3): 
                if self.color[i] > 0:
                    self.color[i] -= 1  
                    if self.color[i] < 0:
                        self.color[i] = 0            
            if sum(self.color) == 0:
                self.state = Wood.BURNT  

    def render(self, screen):
        if self.state != Wood.BURNT: 
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update(self, all_woods):
        if self.state == Wood.FALLING:
            self.fall_and_collide_with_ground()

            for other_wood in all_woods:
                if other_wood != self and other_wood.state == Wood.LANDED:
                    self.stack_on_other_wood(other_wood)
            if self.state == Wood.LANDED and self.check_collision_with_fire():
                self.state = Wood.BURNING
        elif self.state == Wood.BURNING:
            self.burn_and_fade()
            if self.check_collision_with_fire():
                self.state = Wood.BURNING


    def check_collision_with_fire(self):
        if self.state in [Wood.LANDED, Wood.BURNING]:
            flame_top = flame.get_flame_center()
            in_campfire_box = (
                self.x < campfire_rect.right and
                self.x + self.width > campfire_rect.left and
                self.y < campfire_rect.bottom and
                self.y + self.height > campfire_rect.top
            )
            touching_flame_center = (
                self.x < campfire_rect.right and
                self.x + self.width > campfire_rect.left and
                self.y < flame_top + 50 and
                self.y + self.height > flame_top - 50
            )
            if in_campfire_box or touching_flame_center:
                return True
        return False

class FlameParticle:
    alpha_layer_qty = 2
    alpha_glow_difference_constant = 2

    def __init__(self, x, y, r=5):
        self.x = x
        self.y = y
        self.r = r
        self.original_r = r
        self.alpha_layers = FlameParticle.alpha_layer_qty
        self.alpha_glow = FlameParticle.alpha_glow_difference_constant
        max_surf_size = 2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        self.burn_rate = 0.1 * random.randint(1, 5)  

    def move_and_fade(self, rise_multiplier):
        self.y -= (4.5 - self.r) * rise_multiplier 
        self.x += random.uniform(-self.r * 1.2, self.r * 1.2)  
        self.original_r -= self.burn_rate
        self.r = max(1, int(self.original_r))  

    def render(self):
        max_surf_size = 2 * self.r * self.alpha_layers * self.alpha_layers * self.alpha_glow
        self.surf = pygame.Surface((max_surf_size, max_surf_size), pygame.SRCALPHA)
        for i in range(self.alpha_layers, -1, -1):
            alpha = 255 - i * (255 // self.alpha_layers - 5)
            if alpha <= 0:
                alpha = 0
            radius = self.r * i * i * self.alpha_glow
            if self.r == 4 or self.r == 3:
                r, g, b = (255, 0, 0)
            elif self.r == 2:
                r, g, b = (255, 150, 0)
            else:
                r, g, b = (50, 50, 50)
            color = (r, g, b, alpha)
            pygame.draw.circle(self.surf, color, (self.surf.get_width() // 2, self.surf.get_height() // 2), radius)
        screen.blit(self.surf, self.surf.get_rect(center=(self.x, self.y)))

class Flame:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.flame_intensity = 2  
        self.rise_multiplier = 1  
        self.max_rise_multiplier = 2  
        self.burn_rate_base = 0.1 
        self.burn_rate_multiplier = 1  
        self.flame_particles = []
        self.reset_timer = 0
        self.is_fire_burning = False
        for _ in range(self.flame_intensity * 25):
            self.flame_particles.append(FlameParticle(self.x + random.randint(-5, 5), self.y, random.randint(1, 5)))

    def increase_flame(self):
        self.flame_intensity = 20  
        self.rise_multiplier = 8 
        self.burn_rate_multiplier = 1.5  
        self.is_fire_burning = True

    def reset_flame(self):
        if self.flame_intensity > 2:
            self.flame_intensity -= 0.02  
        if self.rise_multiplier > 1:
            self.rise_multiplier -= 0.02  
        if self.burn_rate_multiplier < 1:
            self.burn_rate_multiplier += 0.02 
        self.is_fire_burning = False

    def render_flame(self):
        for particle in self.flame_particles[:]:
            if particle.original_r <= 0: 
                self.flame_particles.remove(particle)
                self.flame_particles.append(
                    FlameParticle(self.x + random.randint(-5, 5), self.y, random.randint(1, 5))
                )
                continue
            particle.burn_rate = self.burn_rate_base * self.burn_rate_multiplier
            particle.move_and_fade(self.rise_multiplier)
            particle.render()
    def get_flame_center(self):
        return self.y - (self.flame_intensity * 5) 
 
flame = Flame(campfire_rect.centerx, campfire_rect.top + 50)
wood_pieces = []

def play_fire_sound(flame):
    if flame.is_fire_burning: 
        if not pygame.mixer.Channel(0).get_busy():
            pygame.mixer.Channel(0).play(high_fire_sound)
        pygame.mixer.Channel(1).stop()
    else:
        if not pygame.mixer.Channel(1).get_busy():
            pygame.mixer.Channel(1).play(low_fire_sound)
        pygame.mixer.Channel(0).stop()

class SmokeParticle:
    def __init__(self, x, y, size=10):
        self.x = x
        self.y = y
        self.size = size 
        self.original_size = size
        self.lifetime = random.randint(50, 100) 
        self.color = (200, 200, 200)  
        self.opacity = 255 
        self.fade_rate = 5  
        self.rise_speed = random.uniform(1, 2) 
        self.spread = random.uniform(-1, 1)  

    def move_and_fade(self):
        self.y -= self.rise_speed  
        self.x += self.spread  
        self.opacity -= self.fade_rate  
        self.size -= 0.1  
        if self.size <= 0:
            self.size = 0
        if self.opacity <= 0:
            self.opacity = 0

    def is_dead(self):
        return self.opacity <= 0

    def render(self):
        if self.opacity > 0:
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, int(self.opacity)), (self.size, self.size), int(self.size))
            screen.blit(surface, (self.x - self.size, self.y - self.size))



class Smoke:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.smoke_particles = []
        self.smoke_intensity = 1 
        self.max_smoke_intensity = 4 

    def adjust_smoke_intensity(self, intensity):
        self.smoke_intensity = min(max(intensity, 1), self.max_smoke_intensity)

    def generate_particle(self, flame_intensity, flame_y):
        smoke_y = flame_y - 50 - flame_intensity * 5  
        for _ in range(int(flame_intensity // 1.5)): 
            self.smoke_particles.append(SmokeParticle(self.x, smoke_y))

    def render_smoke(self):
        for particle in self.smoke_particles[:]:
            particle.move_and_fade()
            particle.render()
            if particle.is_dead():
                self.smoke_particles.remove(particle)

smoke = Smoke(campfire_rect.centerx, campfire_rect.top + 70)

def handle_mouse_events(events):
    for event in events:
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  
            x, y = pygame.mouse.get_pos()
            wood_pieces.append(Wood(x, y - 50))  

def main_loop():
    smoke_timer = 0 
    while True:
        events = pygame.event.get()
        handle_mouse_events(events)
        screen.fill(BACKGROUND_COLOR)
        screen.blit(campfire_image, campfire_rect)

        #collision 영역 표시
        #pygame.draw.rect(screen, (255, 0, 0), campfire_rect, 2)
        #flame_top = flame.get_flame_center()
        #pygame.draw.line(screen, (255, 255, 0), (campfire_rect.left, flame_top), (campfire_rect.right, flame_top), 2)

        wood_burning = False
        for wood in wood_pieces[:]:

            wood.update(wood_pieces)
            wood.render(screen)
            
            if wood.state == Wood.LANDED and wood.check_collision_with_fire():
                wood.state = Wood.BURNING
            
            if wood.state == Wood.BURNING:
                wood_burning = True
                flame.increase_flame()  
            
            if wood.state == Wood.BURNT:
                wood_pieces.remove(wood)

        if not wood_burning:
            flame.reset_timer += 1
            if flame.reset_timer >= FPS * 2: 
                flame.reset_flame()
                smoke.adjust_smoke_intensity(max(1, smoke.smoke_intensity - 0.1))  
        else:
            flame.reset_timer = 0 
            smoke.adjust_smoke_intensity(min(smoke.max_smoke_intensity, smoke.smoke_intensity + 0.5))  
        
        play_fire_sound(flame)
         
        flame.render_flame()
        smoke_timer += 1
        if smoke_timer >= FPS // 8: 
            smoke.generate_particle(flame.flame_intensity, flame.get_flame_center())  
            smoke_timer = 0

        smoke.render_smoke()

        pygame.display.update()
        clock.tick(FPS)

main_loop()

