import pygame
import math
import random
import os
from constants import *

class VictoryParticle:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.color = random.choice([GOLD, CYAN, WHITE, ORANGE, (255, 100, 100)])
        self.radius = random.randint(3, 6)
        self.dx = random.uniform(-3.5, 3.5); self.dy = random.uniform(-6.0, -2.0)
        self.alpha = 255; self.gravity = 0.12
    def update(self):
        self.x += self.dx; self.y += self.dy
        self.dy += self.gravity; self.alpha -= 5
        if self.alpha < 0: self.alpha = 0
    def draw(self, screen, cam_x=0, cam_y=0):
        if self.alpha > 0:
            surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, int(self.alpha)), (self.radius, self.radius), self.radius)
            screen.blit(surf, (int(self.x - cam_x), int(self.y - cam_y)))

class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, color):
        self.x = start_x + 90
        self.y = start_y 
        self.target_x = target_x + 90
        self.target_y = target_y
        self.color = color
        angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        self.speed = 20
        self.dx = math.cos(angle) * self.speed; self.dy = math.sin(angle) * self.speed
        self.trail = []
        
        self.img = None
        try:
            raw_img = pygame.image.load("assets/fire_ball.png").convert_alpha()
            angle_deg = math.degrees(-angle)
            self.img = pygame.transform.rotate(pygame.transform.scale(raw_img, (40, 40)), angle_deg)
        except: pass

    def update(self):
        self.x += self.dx; self.y += self.dy
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6: self.trail.pop(0)
        if math.hypot(self.target_x - self.x, self.target_y - self.y) < 30: return True
        return False
        
    def draw(self, screen):
        if len(self.trail) > 0:
            last_x, last_y = self.trail[-1]
            ring_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            ring_radius = int((pygame.time.get_ticks() % 20) + 5)
            ring_alpha = max(0, 255 - (ring_radius * 10))
            pygame.draw.circle(ring_surf, (*self.color, ring_alpha), (20, 20), ring_radius, 2)
            screen.blit(ring_surf, (int(last_x) - 20, int(last_y) - 20))
            
        for i, (tx, ty) in enumerate(self.trail):
            alpha = 255 * (i / len(self.trail))
            surf = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, int(alpha)), (6, 6), 6)
            screen.blit(surf, (int(tx)-6, int(ty)-6))
            
        if self.img:
            rect = self.img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.img, rect.topleft)
        else:
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 8)

class SummonJimat:
    def __init__(self, start_x, start_y, target_x, target_y, color):
        self.x = start_x; self.y = start_y
        self.target_x = target_x; self.target_y = target_y
        self.color = color
        angle = math.atan2(target_y - start_y, target_x - start_x)
        self.speed = 16
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.rotation = 0
    def update(self):
        self.x += self.dx; self.y += self.dy
        self.rotation += 20
        if math.hypot(self.target_x - self.x, self.target_y - self.y) < 18: return True
        return False
    def draw(self, screen, cam_x, cam_y):
        draw_x = int(self.x - cam_x)
        draw_y = int(self.y - cam_y)
        jimat_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(jimat_surf, self.color, (16, 16), 14)
        pygame.draw.circle(jimat_surf, WHITE, (16, 16), 7)
        pygame.draw.rect(jimat_surf, GOLD, (2, 14, 28, 4))
        rotated_surf = pygame.transform.rotate(jimat_surf, self.rotation)
        new_rect = rotated_surf.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated_surf, new_rect.topleft)

class AuraParticle:
    def __init__(self, x, y, color):
        self.x = x + random.randint(10, 170)
        self.y = y 
        self.color = color
        self.radius = random.randint(3, 7); self.alpha = 255
        self.speed = random.uniform(2.0, 5.0); self.wobble = random.uniform(-1.5, 1.5)
    def update(self):
        self.y -= self.speed; self.x += self.wobble
        self.alpha -= 10
        if self.alpha < 0: self.alpha = 0
    def draw(self, screen):
        if self.alpha > 0:
            surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, self.alpha), (self.radius, self.radius), self.radius)
            screen.blit(surf, (self.x, self.y))

class HealParticle:
    def __init__(self, x, y, color):
        self.x = x + random.randint(0, 40); self.y = y + random.randint(10, 50)
        self.color = color; self.radius = random.randint(3, 6); self.alpha = 255
        self.speed = random.uniform(1.0, 3.0)
    def update(self):
        self.y -= self.speed; self.alpha -= 8
        if self.alpha < 0: self.alpha = 0
    def draw(self, screen):
        if self.alpha > 0:
            surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, self.alpha), (self.radius, self.radius), self.radius)
            screen.blit(surf, (self.x, self.y))

class RainDrop:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH); self.y = random.randint(-50, 0)
        self.speed_y = random.randint(10, 15); self.speed_x = random.randint(-2, 1)
        self.length = random.randint(10, 20)
    def update(self):
        self.x += self.speed_x; self.y += self.speed_y
    def draw(self, screen):
        pygame.draw.line(screen, LIGHT_BLUE, (self.x, self.y), (self.x + self.speed_x, self.y + self.length), 1)

class Stardust:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH); self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.1, 0.5); self.radius = random.uniform(0.5, 2.0)
        self.alpha = random.randint(50, 200); self.alpha_dir = 1 if random.random() > 0.5 else -1
    def update(self):
        self.y -= self.speed
        if self.y < 0:
            self.y = SCREEN_HEIGHT; self.x = random.randint(0, SCREEN_WIDTH)
        self.alpha += self.alpha_dir * 2
        if self.alpha > 255: self.alpha, self.alpha_dir = 255, -1
        elif self.alpha < 50: self.alpha, self.alpha_dir = 50, 1
    def draw(self, screen):
        surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 215, 0, self.alpha), (self.radius, self.radius), self.radius)
        screen.blit(surf, (self.x, self.y))

class FloatingText:
    def __init__(self, text, x, y, color, is_crit=False):
        font_size = 40 if is_crit else 32
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.image = self.font.render(text, True, color)
        self.shadow = self.font.render(text, True, BLACK)
        self.x = x; self.y = y; self.alpha = 255
        
        self.vy = random.uniform(-6, -9) if is_crit else random.uniform(-4, -6)
        self.vx = random.uniform(-2, 2)
        self.gravity = 0.4

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 5 
        if self.alpha < 0: self.alpha = 0
        self.image.set_alpha(self.alpha); self.shadow.set_alpha(self.alpha)

    def draw(self, screen):
        if self.alpha > 0:
            screen.blit(self.shadow, (self.x + 2, self.y + 2)); screen.blit(self.image, (self.x, self.y))

class Item:
    def __init__(self, name, description): self.name, self.description = name, description
    def use(self, target): pass

class HealthPotion(Item):
    def __init__(self):
        super().__init__("Jamu Sehat", "Memulihkan 150 HP")
        self.heal_amount = 150
    def use(self, target):
        target.hp += self.heal_amount; target.status_effect = None 
        return f"+{self.heal_amount} HP"

class AttackPotion(Item):
    def __init__(self):
        super().__init__("Jamu Kuat", "Meningkatkan Serangan +20")
        self.buff_amount = 20
    def use(self, target):
        target.base_attack += self.buff_amount
        return f"+{self.buff_amount} ATT!"

class Skill:
    def __init__(self, name, power, element, skill_type="Melee"):
        self.name, self.power, self.element, self.skill_type = name, power, element, skill_type

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, image_path=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color; self.image = None; self.image_path = image_path 
        
        self.frames = None
        self.direction = 0     
        self.anim_frame = 0
        self.anim_speed = 80   
        self.last_update = pygame.time.get_ticks()
        self.is_moving = False
        
        if image_path and os.path.exists(image_path):
            try:
                img = pygame.image.load(image_path).convert_alpha()
                if img.get_width() >= width * 4: 
                    self.frames = []
                    frame_w = img.get_width() // 8
                    frame_h = img.get_height() // 4
                    for row in range(4):
                        row_frames = []
                        for col in range(8):
                            frame = img.subsurface((col * frame_w, row * frame_h, frame_w, frame_h))
                            row_frames.append(pygame.transform.scale(frame, (width, height)))
                        self.frames.append(row_frames)
                    self.image = self.frames[0][0]
                else: self.image = pygame.transform.scale(img, (width, height))
            except: pass 

    def update_animation(self):
        if not self.frames: return
        now = pygame.time.get_ticks()
        if now - self.last_update > self.anim_speed:
            self.last_update = now
            if self.is_moving:
                self.anim_frame = (self.anim_frame + 1) % 8
            else:
                self.anim_frame = 0 
                
        safe_dir = self.direction % 4
        self.image = self.frames[safe_dir][self.anim_frame]

    def draw(self, screen, cam_x=0, cam_y=0):
        draw_rect = self.rect.move(-cam_x, -cam_y)
        pygame.draw.ellipse(screen, (15, 30, 15), (draw_rect.x, draw_rect.y + draw_rect.height - 8, draw_rect.width, 12))
        bounce = 0 if not self.is_moving else math.sin(pygame.time.get_ticks() * 0.008) * 1.5
        if self.image: screen.blit(self.image, (draw_rect.x, draw_rect.y + bounce))
        else: pygame.draw.rect(screen, self.color, (draw_rect.x, draw_rect.y + bounce, draw_rect.width, draw_rect.height))

class OverworldMonster(Entity):
    def __init__(self, x, y, m_type, image_path=None):
        super().__init__(x, y, MONSTER_SIZE, MONSTER_SIZE, RED, image_path)
        self.m_type = m_type; self.base_y = y; self.anim_offset = random.randint(0, 100)
        self.start_x = x; self.patrol_timer = random.randint(0, 60); self.dx = 0; self.dy = 0

    def update(self):
        self.patrol_timer -= 1
        if self.patrol_timer <= 0:
            self.dx = random.choice([-1, 0, 1])
            self.patrol_timer = random.randint(15, 45) 
        self.rect.x += self.dx
        
        if self.dx == 0 and self.dy == 0:
            self.is_moving = False
            self.anim_frame = 0
        else:
            self.is_moving = True
            if self.dx > 0: self.direction = 3 
            elif self.dx < 0: self.direction = 2 
        self.update_animation()
        
        if self.rect.x < self.start_x - 40: self.rect.x = self.start_x - 40
        if self.rect.x > self.start_x + 40: self.rect.x = self.start_x + 40

class NPC(Entity):
    def __init__(self, x, y, name, dialog_message, image_path="assets/npc.png"):
        super().__init__(x, y, NPC_SIZE, NPC_SIZE, YELLOW, image_path) 
        self.name = name; self.message = dialog_message
        self.start_x = x; self.start_y = y
        self.patrol_timer = random.randint(0, 60); self.dx = 0; self.dy = 0

    def update(self):
        if self.name == "Nyai": 
            self.is_moving = False; self.anim_frame = 0; self.direction = 0
            self.update_animation(); return 
            
        self.patrol_timer -= 1
        if self.patrol_timer <= 0:
            direction = random.choice([(0,0), (-1,0), (1,0), (0,-1), (0,1)])
            self.dx, self.dy = direction
            self.patrol_timer = random.randint(15, 45)
        self.rect.x += self.dx; self.rect.y += self.dy
        
        if self.dx == 0 and self.dy == 0:
            self.is_moving = False
            self.anim_frame = 0
        else:
            self.is_moving = True
            if self.dx > 0: self.direction = 3
            elif self.dx < 0: self.direction = 2
            elif self.dy > 0: self.direction = 0
            elif self.dy < 0: self.direction = 1
        self.update_animation()
        
        self.rect.x = max(self.start_x - 50, min(self.rect.x, self.start_x + 50))
        self.rect.y = max(self.start_y - 50, min(self.rect.y, self.start_y + 50))

class Monster(Entity):
    def __init__(self, name, x, y, color, element, hp, attack, image_path=None):
        super().__init__(x, y, 100, 100, color, image_path)
        self.name = name; self.element = element; self.level = 1; self.exp = 0
        self.max_hp = hp; self._hp = hp; self.base_attack = attack
        self.skills = []; self.status_effect = None 
        self.base_y = y; self.anim_offset = random.randint(0, 100)
        self.is_enraged = False
        
        self.render_offset_x = 0
        self.render_offset_y = 0 
        self.aura_particles = [] 

    @property
    def hp(self): return self._hp
    @hp.setter
    def hp(self, value): self._hp = max(0, min(value, self.max_hp))

    def learn_skill(self, skill): self.skills.append(skill)

    def trigger_enrage(self):
        if not self.is_enraged and self.name == "Raja Jin":
            self.is_enraged = True; self.base_attack *= 1.5 
            self.learn_skill(Skill("Kiamat", 80, "Fire", "Ranged")); return True
        return False

    def take_damage(self, skill, attacker_attack, diff_multiplier=1.0):
        multiplier = ELEMENT_CHART.get(skill.element, {}).get(self.element, 1.0)
        raw_damage = skill.power + (attacker_attack * 0.8)
        is_crit = random.randint(1, 100) <= 20
        if is_crit: raw_damage *= 1.6
        
        final_damage = int((raw_damage * multiplier) * diff_multiplier)
        self.hp -= final_damage 
        
        if skill.element == "Fire" and random.randint(1, 100) <= 30: self.status_effect = "Terbakar"
        text_color = WHITE
        if multiplier > 1.0: text_color = GOLD
        elif multiplier < 1.0: text_color = GREY
        if is_crit: text_color = ORANGE
        enraged_now = False
        if self.hp <= self.max_hp // 2: enraged_now = self.trigger_enrage()
        return final_damage, text_color, enraged_now, is_crit

    def gain_exp(self, amount):
        self.exp += amount
        leveled_up, evolved = False, False
        if self.exp >= 100:
            self.level += 1; self.exp -= 100
            self.max_hp += 80; self.hp = self.max_hp; self.base_attack += 20
            leveled_up = True
            if self.level == 2 and len(self.skills) < 3:
                if self.element == "Wind": self.learn_skill(Skill("Cakar Angin", 40, "Wind", "Melee"))
                elif self.element == "Earth": self.learn_skill(Skill("Pukulan Bumi", 40, "Earth", "Melee"))
        return leveled_up, evolved

    def draw_battle(self, screen, font, shake_x=0, shake_y=0):
        scale_size = 180
        idle_bounce = math.sin(pygame.time.get_ticks() * 0.005 + self.anim_offset) * 5
        
        ground_y = 400
        draw_x = self.rect.x + self.render_offset_x + shake_x
        draw_y = ground_y - scale_size + self.render_offset_y + shake_y + idle_bounce

        shadow_y = ground_y - 15
        pygame.draw.ellipse(screen, (30, 30, 30), (draw_x + 10, shadow_y, scale_size - 20, 25))
        
        if self.hp > 0 and self.hp <= self.max_hp * 0.3:
            if len(self.aura_particles) < 35:
                aura_color = RED if self.element == "Fire" else BLUE if self.element == "Water" else GOLD
                self.aura_particles.append(AuraParticle(draw_x, draw_y + random.randint(10, scale_size), aura_color))
        if self.status_effect == "Terbakar" and random.randint(1, 10) <= 4:
             self.aura_particles.append(AuraParticle(draw_x, draw_y + random.randint(0, scale_size - 20), ORANGE))

        for p in self.aura_particles[:]:
            p.update()
            if p.alpha <= 0: self.aura_particles.remove(p)
            p.draw(screen)

        if not self.image and self.image_path and os.path.exists(self.image_path):
            try: self.image = pygame.image.load(self.image_path).convert_alpha()
            except: pass

        is_enemy = self.rect.x > SCREEN_WIDTH // 2
        if self.image: 
            scaled_img = pygame.transform.scale(self.image, (scale_size, scale_size))
            if is_enemy:
                if self.frames and len(self.frames) >= 3:
                    scaled_img = pygame.transform.scale(self.frames[2][0], (scale_size, scale_size))
                else:
                    scaled_img = pygame.transform.flip(scaled_img, True, False)
            else:
                if self.frames and len(self.frames) >= 4:
                    scaled_img = pygame.transform.scale(self.frames[3][0], (scale_size, scale_size))
                
            screen.blit(scaled_img, (draw_x, draw_y))
        else: 
            surf = pygame.Surface((scale_size, scale_size), pygame.SRCALPHA)
            surf.fill((*self.color, 150)) 
            screen.blit(surf, (draw_x, draw_y))
        
        bar_width = 100
        bar_x = draw_x + (scale_size // 2) - (bar_width // 2)
        bar_y = ground_y - scale_size - 40 
        
        pygame.draw.rect(screen, BLACK, (bar_x - 2, bar_y - 2, bar_width + 4, 12))
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, 8))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (0, 220, 50), (bar_x, bar_y, int(bar_width * hp_ratio), 8))
        
        segments = 4
        seg_w = bar_width / segments
        for i in range(1, segments):
            pygame.draw.line(screen, BLACK, (bar_x + int(seg_w * i), bar_y), (bar_x + int(seg_w * i), bar_y + 7), 2)
        
        circle_x, circle_y = bar_x - 12, bar_y + 4
        pygame.draw.circle(screen, GOLD, (circle_x, circle_y), 12)
        pygame.draw.circle(screen, BLACK, (circle_x, circle_y), 9)
        lvl_txt = font.render(str(self.level), True, GOLD)
        screen.blit(lvl_txt, lvl_txt.get_rect(center=(circle_x, circle_y + 1)))

        name_txt = font.render(self.name, True, RED if self.is_enraged else WHITE)
        screen.blit(name_txt, name_txt.get_rect(midbottom=(bar_x + (bar_width//2), bar_y - 5)))

class Player(Entity):
    def __init__(self):
        super().__init__(100, 300, PLAYER_SIZE, PLAYER_SIZE, BLUE, "assets/player.png")
        self.speed = 5; self.partner = None 
        self.inventory = [HealthPotion(), HealthPotion(), AttackPotion()] 
        self.quests = {"Leak-Mon": 0, "Buto Ijo": 0, "Cendrawasih": 0}; self.steps_taken = 0 
        
    def update_motion(self):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        self.dx, self.dy = 0, 0
        
        if keys[pygame.K_w]: 
            self.rect.y -= self.speed; self.dy = -1
        elif keys[pygame.K_s]: 
            self.rect.y += self.speed; self.dy = 1
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]: 
            self.rect.x -= self.speed; self.dx = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: 
            self.rect.x += self.speed; self.dx = 1
            
        if self.dx == 0 and self.dy == 0:
            self.is_moving = False
            self.anim_frame = 0 
        else:
            self.is_moving = True
            self.steps_taken += 1
            if self.dx > 0: self.direction = 3
            elif self.dx < 0: self.direction = 2
            elif self.dy > 0: self.direction = 0
            elif self.dy < 0: self.direction = 1
            
        self.update_animation()
        
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH - PLAYER_SIZE))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - PLAYER_SIZE))

    def draw_ml_hud(self, screen, font, cam_x=0, cam_y=0):
        if not self.partner: return
        bar_width = 48 
        bar_x = (self.rect.centerx - cam_x) - (bar_width // 2)
        bar_y = (self.rect.top - cam_y) - 18
        
        pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, 9))
        hp_ratio = self.partner.hp / self.partner.max_hp
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, 4))
        pygame.draw.rect(screen, (0, 220, 50), (bar_x, bar_y, int(bar_width * hp_ratio), 4))
        
        segment_width = bar_width // 3
        pygame.draw.line(screen, BLACK, (bar_x + segment_width, bar_y), (bar_x + segment_width, bar_y + 3), 1)
        pygame.draw.line(screen, BLACK, (bar_x + 2*segment_width, bar_y), (bar_x + 2*segment_width, bar_y + 3), 1)
        
        exp_ratio = self.partner.exp / 100
        pygame.draw.rect(screen, GREY, (bar_x, bar_y + 5, bar_width, 2))
        pygame.draw.rect(screen, CYAN, (bar_x, bar_y + 5, int(bar_width * exp_ratio), 2))
        
        circle_x, circle_y = bar_x - 10, bar_y + 3
        pygame.draw.circle(screen, GOLD, (circle_x, circle_y), 9)
        pygame.draw.circle(screen, BLACK, (circle_x, circle_y), 7)
        lvl_txt = font.render(str(self.partner.level), True, GOLD)
        screen.blit(lvl_txt, lvl_txt.get_rect(center=(circle_x, circle_y)))