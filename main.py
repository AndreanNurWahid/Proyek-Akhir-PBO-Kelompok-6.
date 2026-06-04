import pygame
import sys
import random
import math
import os
import json
from constants import *
from entities import Player, Monster, Skill, FloatingText, HealthPotion, AttackPotion, NPC, RainDrop, Stardust, OverworldMonster, HealParticle, Projectile, VictoryParticle, SummonJimat

class GameEngine:
    def __init__(self):
        pygame.init()
        self.volume = 0.5
        self.diff_hard = False
        self.language_indo = True
        
        self.audio_muted = False
        self.sfx_nav = None
        try: 
            pygame.mixer.init() 
            if os.path.exists("assets/sfx_click.wav"): 
                self.sfx_nav = pygame.mixer.Sound("assets/sfx_click.wav")
            elif os.path.exists("assets/sfx_swoosh.wav"):
                self.sfx_nav = pygame.mixer.Sound("assets/sfx_swoosh.wav")
            pygame.mixer.music.set_volume(self.volume)
        except: pass
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nusantara Mon - Definitive Edition")
        self.clock = pygame.time.Clock()
        
        self.font_title = pygame.font.SysFont("Verdana", 64, bold=True)
        self.font = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 18)
        self.font_mini = pygame.font.SysFont("Arial", 14, bold=True) 
        
        self.menu_bg_img = self.load_img_safe("assets/menu_bg.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.select_bg_img = self.load_img_safe("assets/select_bg.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.map_bg_img = self.load_img_safe("assets/map.png", (MAP_WIDTH, MAP_HEIGHT))
        self.battle_bg_img = self.load_img_safe("assets/battle_bg.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.minimap_img = self.load_img_safe("assets/minimap.png", (160, 120))
        self.bg_pengaturan = self.load_img_safe("assets/bg_pengaturan.png", (600, 400))
        
        self.loading_bg_img = self.load_img_safe("assets/loading_bg.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.boss_bg_img = self.load_img_safe("assets/boss_bg.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.player = Player()
        self.wild_monster = None
        self.floating_texts, self.particles, self.rain_drops, self.victory_particles = [], [], [], []
        self.menu_stardust = [Stardust() for _ in range(70)] 
        
        self.active_jimat = None
        self.target_monster_ref = None
        self.jimat_delay_timer = 0
        self.wipe_radius = 0
        self.active_projectile, self.pending_attack = None, None
        self.attack_hit, self.melee_timer = False, 0
        self.loading_timer = 0 
        
        self.claw_effect_img = self.load_img_safe("assets/cakar_effect.png", (120, 120))
        self.show_claw_effect = False
        self.claw_effect_timer = 0
        
        self.map_monsters = self.get_initial_monsters()
        self.npcs = [
            NPC(150, 150, "Prabu Siliwangi", "Restu alam semesta memulihkan partnermu.", "assets/prabu.png"),
            NPC(150, 400, "Nyai Brintik", "Pendekar, bawa jamu tradisional ini!.", "assets/nyai.png"),
            NPC(900, 400, "Gajah Mada", "Bantu aku kalahkan 2 Leak-Mon liar.", "assets/gajahmada.png")
        ]
        self.guard_npc = NPC(600, 100, "Kian Santang", "Capai Level 3 & Selesaikan Misi!", "assets/kiansantang.png")
        self.boss_npc = NPC(1000, 750, "Raja Jin", "MANUSIA KECIL! KAU BERANI MENANTANGKU?!", "assets/raja_jin.png")
        
        self.state, self.battle_state, self.battle_msg = "", "PLAYER_TURN", ""
        self.action_timer, self.is_boss_fight = 0, False
        
        self.menu_index = 0 
        self.char_select_index = 0 
        self.settings_index = 0 
        
        self.is_fullscreen = False
        self.fast_text = False
        
        self.cam_x, self.cam_y = 0, 0
        self.text_idx, self.text_timer = 0, 0
        self.shake_timer, self.damage_flash = 0, False
        self.flash_color, self.flash_timer = None, 0
        
        self.change_state("MENU") 

    def load_img_safe(self, filepath, size=None):
        if os.path.exists(filepath):
            try:
                img = pygame.image.load(filepath).convert_alpha()
                if size: img = pygame.transform.scale(img, size)
                return img
            except: pass
        return None

    def play_sfx(self):
        try: 
            if self.sfx_nav and self.volume > 0 and not self.audio_muted: self.sfx_nav.play()
        except: pass

    def play_bgm(self, filepath):
        if os.path.exists(filepath):
            try:
                if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(0 if self.audio_muted else self.volume)
                pygame.mixer.music.play(-1)
            except: pass

    def toggle_audio(self):
        self.audio_muted = not self.audio_muted
        try:
            if self.audio_muted: pygame.mixer.music.set_volume(0)
            else: pygame.mixer.music.set_volume(self.volume)
        except: pass

    def change_state(self, new_state):
        self.state = new_state
        if new_state in ["MENU", "CHARACTER_SELECT"]: self.play_bgm("assets/bgm_menu.mp3")
        elif new_state == "MAP": self.play_bgm("assets/bgm_map.mp3")
        elif new_state == "BATTLE": self.play_bgm("assets/bgm_battle.mp3")

    def trigger_shake(self, color=None):
        self.shake_timer = pygame.time.get_ticks()
        self.damage_flash = True
        self.flash_color = color

    def mock_file_handling_save(self):
        data = {"level": self.player.partner.level if self.player.partner else 1, "quests": self.player.quests}
        with open("save_data.json", "w") as f: json.dump(data, f)
        
    def mock_file_handling_load(self):
        if os.path.exists("save_data.json"):
            self.floating_texts.append(FloatingText("Data Berhasil Dimuat!", SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2, GOLD))
            return True
        return False

    def get_initial_monsters(self):
        return [
            OverworldMonster(300, 150, "Buto Ijo", "assets/buto_ijo.png"),
            OverworldMonster(450, 600, "Leak-Mon", "assets/leak.png"),
            OverworldMonster(900, 300, "Cendrawasih", "assets/cendrawasih.png"),
            OverworldMonster(100, 400, "Leak-Mon", "assets/leak.png"),
            OverworldMonster(100, 700, "Buto Ijo", "assets/buto_ijo.png")
        ]

    def spawn_specific_monster(self, m_type):
        self.is_boss_fight = False
        if m_type == "Buto Ijo":
            self.wild_monster = Monster("Buto Ijo", 550, 250, GREEN, "Earth", 220, 12, "assets/buto_ijo.png")
            self.wild_monster.learn_skill(Skill("Hantaman Bumi", 20, "Earth", "Melee"))
        elif m_type == "Leak-Mon":
            self.wild_monster = Monster("Leak-Mon", 550, 250, RED, "Fire", 90, 26, "assets/leak.png")
            self.wild_monster.learn_skill(Skill("Semburan Api", 35, "Fire", "Ranged"))
        else:
            self.wild_monster = Monster("Cendrawasih", 550, 250, GOLD, "Water", 100, 18, "assets/cendrawasih.png")
            self.wild_monster.learn_skill(Skill("Semburan Air", 25, "Water", "Ranged"))

    def spawn_boss(self):
        self.is_boss_fight = True
        self.wild_monster = Monster("Raja Jin", 550, 250, PURPLE, "Normal", 450, 30, "assets/raja_jin.png")
        self.wild_monster.learn_skill(Skill("Pukulan Hampa", 40, "Normal", "Melee"))

    def start_dialog(self, npc):
        self.active_npc = npc
        self.change_state("DIALOG")
        self.text_idx = 0 
        self.text_timer = pygame.time.get_ticks()
        
        dx = self.player.rect.centerx - npc.rect.centerx
        dy = self.player.rect.centery - npc.rect.centery
        
        if abs(dx) > abs(dy):
            npc.direction = 3 if dx > 0 else 2
        else:
            npc.direction = 0 if dy > 0 else 1
            
        npc.is_moving = False
        npc.anim_frame = 0
        npc.update_animation()

    def draw_minimap(self):
        mm_w, mm_h = 160, 120
        mm_x, mm_y = 20, 20
        if hasattr(self, 'minimap_img') and self.minimap_img:
            self.screen.blit(self.minimap_img, (mm_x, mm_y))
        else:
            surf = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
            surf.fill((10, 15, 20, 180)); self.screen.blit(surf, (mm_x, mm_y))
            
        pygame.draw.rect(self.screen, GOLD, (mm_x, mm_y, mm_w, mm_h), 2)
        sx, sy = mm_w / MAP_WIDTH, mm_h / MAP_HEIGHT
        
        for npc in self.npcs + [self.guard_npc, self.boss_npc]:
            px, py = mm_x + int(npc.rect.centerx * sx), mm_y + int(npc.rect.centery * sy)
            warna_npc = PURPLE if npc.name == "Raja Jin" else YELLOW
            
            pygame.draw.circle(self.screen, BLACK, (px, py), 6)
            pygame.draw.circle(self.screen, warna_npc, (px, py), 4)

        for m in self.map_monsters:
            if math.hypot(self.player.rect.centerx - m.rect.centerx, self.player.rect.centery - m.rect.centery) <= RADAR_VIEW_DISTANCE:
                px, py = mm_x + int(m.rect.centerx * sx), mm_y + int(m.rect.centery * sy)
                pygame.draw.circle(self.screen, BLACK, (px, py), 6) 
                pygame.draw.circle(self.screen, RED, (px, py), 4) 
                
        px, py = mm_x + int(self.player.rect.centerx * sx), mm_y + int(self.player.rect.centery * sy)
        pygame.draw.circle(self.screen, BLACK, (px, py), 8) 
        pygame.draw.circle(self.screen, CYAN, (px, py), 6) 

    def run(self):
        while True:
            self.handle_events()
            self.update_logic()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
            if event.type == pygame.KEYDOWN and self.state not in ["TRANSITION_THROW", "WIPE_IN", "LOADING"]:
                
                if self.state == "MENU":
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        self.play_sfx()
                        if event.key == pygame.K_UP: self.menu_index = 4 if self.menu_index == 0 else (self.menu_index - 1) % 5
                        elif event.key == pygame.K_DOWN: self.menu_index = 0 if self.menu_index == 4 else (self.menu_index + 1) % 5
                        elif event.key == pygame.K_LEFT: self.menu_index = 4
                        elif event.key == pygame.K_RIGHT: self.menu_index = 0
                            
                    elif event.key == pygame.K_RETURN:
                        self.play_sfx()
                        if self.menu_index == 0: self.change_state("CHARACTER_SELECT")
                        elif self.menu_index == 1: 
                            if not self.mock_file_handling_load(): self.change_state("CHARACTER_SELECT")
                        elif self.menu_index == 2: self.change_state("SETTINGS")
                        elif self.menu_index == 3: pygame.quit(); sys.exit()
                        elif self.menu_index == 4: self.toggle_audio()

                elif self.state == "SETTINGS":
                    if event.key in [pygame.K_UP, pygame.K_DOWN]:
                        self.play_sfx()
                        self.settings_index = (self.settings_index - 1) % 4 if event.key == pygame.K_UP else (self.settings_index + 1) % 4
                    
                    elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        self.play_sfx()
                        if self.settings_index == 0: 
                            self.language_indo = not self.language_indo
                        elif self.settings_index == 1: 
                            self.is_fullscreen = not self.is_fullscreen
                            if self.is_fullscreen: self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                            else: self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                        elif self.settings_index == 2: 
                            if event.key == pygame.K_LEFT: self.volume = max(0.0, self.volume - 0.1)
                            elif event.key == pygame.K_RIGHT: self.volume = min(1.0, self.volume + 0.1)
                            try: 
                                self.audio_muted = False
                                pygame.mixer.music.set_volume(self.volume)
                            except: pass
                            
                    elif event.key == pygame.K_RETURN and self.settings_index == 3:
                        self.play_sfx(); self.change_state("MENU")

                elif self.state == "CHARACTER_SELECT":
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        self.play_sfx()
                        if event.key == pygame.K_LEFT: self.char_select_index = 0
                        elif event.key == pygame.K_RIGHT: self.char_select_index = 1
                            
                    elif event.key == pygame.K_RETURN:
                        self.play_sfx()
                        if self.char_select_index == 0:
                            self.player.partner = Monster("Garuda-Mon", 150, 250, CYAN, "Wind", 150, 20, "assets/garuda.png")
                            self.player.partner.learn_skill(Skill("Patukan", 15, "Normal", "Melee"))
                            self.player.partner.learn_skill(Skill("Semburan Api", 30, "Wind", "Ranged"))
                        elif self.char_select_index == 1:
                            self.player.partner = Monster("Hanuman-Mon", 150, 250, GOLD, "Earth", 160, 18, "assets/hanuman.png")
                            self.player.partner.learn_skill(Skill("Tabrak", 15, "Normal", "Melee"))
                            self.player.partner.learn_skill(Skill("Lemparan Batu", 30, "Earth", "Ranged"))
                        self.change_state("LOADING")
                        self.loading_timer = pygame.time.get_ticks()
                            
                elif self.state == "DIALOG" and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                    if self.text_idx < len(self.active_npc.message):
                        self.text_idx = len(self.active_npc.message) 
                    else:
                        if self.active_npc == self.boss_npc:
                            self.target_monster_ref = self.boss_npc
                            jimat_color = CYAN if self.player.partner.element == "Wind" else GOLD
                            self.active_jimat = SummonJimat(self.player.rect.centerx, self.player.rect.centery, self.boss_npc.rect.centerx, self.boss_npc.rect.centery, jimat_color)
                            self.change_state("TRANSITION_THROW")
                        else:
                            self.change_state("MAP")
                            if self.player.rect.x < self.active_npc.rect.x: self.player.rect.x -= 20
                            else: self.player.rect.x += 20

                elif self.state == "BATTLE" and self.battle_state == "PLAYER_TURN":
                    if event.key == pygame.K_1 and len(self.player.partner.skills) > 0: self.start_attack(self.player.partner, self.wild_monster, 0)
                    elif event.key == pygame.K_2 and len(self.player.partner.skills) > 1: self.start_attack(self.player.partner, self.wild_monster, 1)
                    elif event.key == pygame.K_3:
                        if len(self.player.partner.skills) > 2: self.start_attack(self.player.partner, self.wild_monster, 2)
                        else: self.use_item() 
                    elif event.key == pygame.K_4 and len(self.player.partner.skills) > 3: self.start_attack(self.player.partner, self.wild_monster, 3)
                    elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN: self.use_item()

                elif self.state == "BATTLE_END" and event.key == pygame.K_RETURN:
                    self.player.partner.status_effect = None
                    self.player.rect.x -= 50 
                    self.mock_file_handling_save() 
                    if self.is_boss_fight: self.change_state("CREDITS")
                    else: 
                        self.change_state("MAP")
                        for _ in range(20): self.victory_particles.append(VictoryParticle(self.player.rect.centerx, self.player.rect.top))

    def use_item(self):
        if len(self.player.inventory) > 0:
            item = self.player.inventory.pop(0) 
            msg = item.use(self.player.partner) 
            color = GREEN if item.name == "Jamu Sehat" else GOLD
            for _ in range(15): self.particles.append(HealParticle(self.player.partner.rect.x, self.player.partner.rect.y, color))
            self.floating_texts.append(FloatingText(msg, self.player.partner.rect.x + 30, self.player.partner.rect.y, DARK_GREEN))
            self.battle_msg = f"Memakai {item.name}."; self.battle_state = "ENEMY_TURN"; self.action_timer = pygame.time.get_ticks()

    def start_attack(self, attacker, defender, skill_index):
        skill = attacker.skills[skill_index]
        self.pending_attack = {"attacker": attacker, "defender": defender, "skill": skill}
        self.attack_hit = False
        self.battle_msg = f"{attacker.name} -> {skill.name}!"
        
        if skill.skill_type == "Ranged":
            color = CYAN if skill.element == "Wind" else ORANGE if skill.element == "Fire" else GOLD if skill.element == "Earth" else BLUE
            center_y = 450 - 90 
            self.active_projectile = Projectile(attacker.rect.x, center_y, defender.rect.x, center_y, color)
        else: 
            self.melee_timer = pygame.time.get_ticks()
            
        self.battle_state = "ANIMATING"

    def finish_attack(self, attacker, defender, skill):
        if defender.name == "Cendrawasih" and random.randint(1, 100) <= 20:
            self.battle_msg = "Meleset!"; return

        if attacker.status_effect == "Terbakar":
            attacker.hp -= 5
            self.floating_texts.append(FloatingText("5 DMG", attacker.rect.x + 30, attacker.rect.y - 20, ORANGE))
            if attacker.hp <= 0:
                self.check_battle_over(); return 
                
        if skill.skill_type == "Melee":
            self.show_claw_effect = True
            self.claw_effect_timer = pygame.time.get_ticks()

        diff_mult = 1.5 if self.diff_hard and attacker == self.wild_monster else 1.0
        damage, text_color, enraged, is_crit = defender.take_damage(skill, attacker.base_attack, diff_mult)
        crit_text = f"CRITICAL! {damage} DMG" if is_crit else f"{damage} DMG"
        self.floating_texts.append(FloatingText(crit_text, defender.rect.x + 30, 450 - 150, text_color, is_crit))
        
        self.trigger_shake((200, 0, 0)) 
        if enraged: self.battle_msg = "Raja Jin Mengamuk!"

    def check_battle_over(self):
        if self.wild_monster.hp <= 0:
            self.change_state("BATTLE_END")
            drop_msg = ""
            if not self.is_boss_fight and random.randint(1, 100) <= 40:
                new_item = random.choice([HealthPotion(), AttackPotion()])
                self.player.inventory.append(new_item)
                drop_msg = f" [Drop: {new_item.name}]"
            if self.wild_monster.name in self.player.quests: self.player.quests[self.wild_monster.name] += 1
                
            if self.is_boss_fight:
                self.battle_msg = "KEMENANGAN TELAK ATAS RAJA JIN!"
                self.boss_npc.rect.x = -1000 
            else:
                leveled_up, evolved = self.player.partner.gain_exp(50)
                if evolved: self.battle_msg = f"Evolusi Partner!{drop_msg}"
                elif leveled_up: self.battle_msg = f"Level Up Partner!{drop_msg}"
                else: self.battle_msg = f"Menang!{drop_msg}"
                
            for _ in range(25): self.victory_particles.append(VictoryParticle(self.wild_monster.rect.centerx, 450))
                
        elif self.player.partner.hp <= 0:
            self.player.rect.x, self.player.rect.y = 100, 300
            self.player.partner.hp = self.player.partner.max_hp
            self.change_state("MAP")
            self.map_monsters = self.get_initial_monsters()
        else:
            self.battle_state = "ENEMY_TURN" if self.battle_state == "ANIMATING" and self.pending_attack["attacker"] == self.player.partner else "PLAYER_TURN"

    def update_logic(self):
        if self.state in ["MENU", "CREDITS", "SETTINGS"]:
            for star in self.menu_stardust: star.update()
            return
            
        if self.state == "LOADING":
            elapsed = pygame.time.get_ticks() - self.loading_timer
            if elapsed >= 3500: 
                self.change_state("MAP")
            return
            
        if self.state == "TRANSITION_THROW":
            if self.active_jimat:
                if self.active_jimat.update():
                    self.active_jimat = None
                    self.jimat_delay_timer = pygame.time.get_ticks()
                    self.trigger_shake(WHITE) 
                    for _ in range(25): self.victory_particles.append(VictoryParticle(self.target_monster_ref.rect.centerx, self.target_monster_ref.rect.centery))
            else:
                if pygame.time.get_ticks() - self.jimat_delay_timer > 300:
                    if self.target_monster_ref == self.boss_npc: self.spawn_boss()
                    else:
                        if self.target_monster_ref in self.map_monsters: self.map_monsters.remove(self.target_monster_ref)
                        self.spawn_specific_monster(self.target_monster_ref.m_type)
                    self.wipe_radius = int(math.hypot(SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.change_state("WIPE_IN")
            
            for vp in self.victory_particles[:]:
                vp.update()
                if vp.alpha <= 0: self.victory_particles.remove(vp)
            return

        elif self.state == "WIPE_IN":
            self.wipe_radius -= 25
            if self.wipe_radius <= 0:
                self.wipe_radius = 0
                self.change_state("BATTLE")
                self.battle_state = "PLAYER_TURN"
                self.battle_msg = f"Lawan {self.wild_monster.name}!"
            return

        if self.state in ["MAP", "DIALOG"]:
            if len(self.map_monsters) == 0:
                self.map_monsters = self.get_initial_monsters()
                if self.state == "MAP": 
                    self.floating_texts.append(FloatingText("Monster Liar Muncul Kembali!", self.player.rect.x - 50, self.player.rect.y - 40, GOLD))

            for m in self.map_monsters: m.update()
            for npc in self.npcs:
                if self.state == "DIALOG" and self.active_npc == npc:
                    npc.is_moving = False; npc.anim_frame = 0; npc.update_animation()
                else: npc.update()
            
            for vp in self.victory_particles[:]:
                vp.update()
                if vp.alpha <= 0: self.victory_particles.remove(vp)
            
            time_cycle = (self.player.steps_taken // 1000) % 3
            if time_cycle == 2: 
                if len(self.rain_drops) < 150: self.rain_drops.append(RainDrop())
            else: self.rain_drops.clear() 
                
            for drop in self.rain_drops[:]:
                drop.update()
                if drop.y > SCREEN_HEIGHT: self.rain_drops.remove(drop)

            if self.state == "MAP":
                old_x, old_y = self.player.rect.x, self.player.rect.y
                self.player.update_motion()
                self.cam_x = max(0, min(self.player.rect.centerx - SCREEN_WIDTH // 2, MAP_WIDTH - SCREEN_WIDTH))
                self.cam_y = max(0, min(self.player.rect.centery - SCREEN_HEIGHT // 2, MAP_HEIGHT - SCREEN_HEIGHT))

                for m in self.map_monsters[:]:
                    if self.player.rect.colliderect(m.rect):
                        self.player.rect.x, self.player.rect.y = old_x, old_y
                        self.target_monster_ref = m
                        jimat_color = CYAN if self.player.partner.element == "Wind" else GOLD
                        self.active_jimat = SummonJimat(self.player.rect.centerx, self.player.rect.centery, m.rect.centerx, m.rect.centery, jimat_color)
                        self.change_state("TRANSITION_THROW")
                        break

                if self.player.rect.colliderect(self.guard_npc.rect):
                    self.player.rect.x, self.player.rect.y = old_x, old_y 
                    if self.player.partner.level >= 3 and self.player.quests["Leak-Mon"] >= 2:
                        self.guard_npc.message = "Jalan terbuka untukmu, Pendekar!."
                        self.guard_npc.rect.x = -1000 
                    else: self.guard_npc.message = f"Selesaikan Misi! (Leak-Mon dikalahkan: {self.player.quests['Leak-Mon']}/2)"
                    self.start_dialog(self.guard_npc)

                elif self.player.rect.colliderect(self.boss_npc.rect):
                    self.player.rect.x, self.player.rect.y = old_x, old_y
                    self.start_dialog(self.boss_npc)
                else:
                    for npc in self.npcs:
                        if self.player.rect.colliderect(npc.rect):
                            self.player.rect.x, self.player.rect.y = old_x, old_y
                            if npc.name == "Gajah Mada": npc.message = f"Target kuota Leak-Mon: {self.player.quests['Leak-Mon']}/2"
                            if npc.name == "Prabu Siliwangi": self.player.partner.hp = self.player.partner.max_hp
                            elif npc.name == "Nyai" and len(self.player.inventory) < 5: self.player.inventory.append(HealthPotion())
                            self.start_dialog(npc)
                            
            elif self.state == "DIALOG":
                text_speed = 10 if self.fast_text else 30
                if self.text_idx < len(self.active_npc.message):
                    if pygame.time.get_ticks() - self.text_timer > text_speed: 
                        self.text_idx += 1; self.text_timer = pygame.time.get_ticks()

        elif self.state == "BATTLE":
            for p in self.particles[:]:
                p.update()
                if p.alpha <= 0: self.particles.remove(p)
            for vp in self.victory_particles[:]:
                vp.update()
                if vp.alpha <= 0: self.victory_particles.remove(vp)
            for ft in self.floating_texts[:]:
                ft.update()
                if ft.alpha <= 0: self.floating_texts.remove(ft)

            if self.battle_state == "ANIMATING":
                att, defend, skill = self.pending_attack["attacker"], self.pending_attack["defender"], self.pending_attack["skill"]
                if skill.skill_type == "Ranged":
                    if self.active_projectile:
                        if self.active_projectile.update():
                            self.finish_attack(att, defend, skill)
                            self.active_projectile = None
                            self.check_battle_over()
                            if self.state == "BATTLE": 
                                self.battle_state = "ENEMY_TURN" if att == self.player.partner else "PLAYER_TURN"
                                self.action_timer = pygame.time.get_ticks()
                else: 
                    elapsed = pygame.time.get_ticks() - self.melee_timer
                    direction = 1 if att == self.player.partner else -1
                    dash_dist = 180 
                    jump_height = 80 
                    
                    if elapsed < 200: 
                        progress = elapsed / 200
                        att.render_offset_x = progress * dash_dist * direction
                        if jump_height > 0: att.render_offset_y = -math.sin(progress * math.pi) * jump_height
                    else:
                        if not self.attack_hit:
                            self.finish_attack(att, defend, skill); self.attack_hit = True
                        if elapsed < 400: 
                            progress = (elapsed - 200) / 200
                            att.render_offset_x = (1 - progress) * dash_dist * direction
                            if jump_height > 0: att.render_offset_y = 0 
                        else:
                            att.render_offset_x = 0
                            att.render_offset_y = 0
                            self.check_battle_over()
                            if self.state == "BATTLE":
                                self.battle_state = "ENEMY_TURN" if att == self.player.partner else "PLAYER_TURN"
                                self.action_timer = pygame.time.get_ticks()

            elif self.battle_state == "ENEMY_TURN":
                if pygame.time.get_ticks() - self.action_timer > 1500:
                    random_skill_idx = random.randint(0, len(self.wild_monster.skills) - 1)
                    self.start_attack(self.wild_monster, self.player.partner, random_skill_idx)

    def draw(self):
        self.screen.fill(BLACK)

        shake_x, shake_y = 0, 0
        if self.damage_flash and pygame.time.get_ticks() - self.shake_timer < 250:
            shake_x, shake_y = random.randint(-10, 10), random.randint(-10, 10)
        else: self.damage_flash = False

        if self.state == "MENU":
            if self.menu_bg_img: self.screen.blit(self.menu_bg_img, (shake_x, shake_y))
            else:
                pygame.draw.rect(self.screen, (15, 35, 15), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
                for star in self.menu_stardust: star.draw(self.screen)
                
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100)); self.screen.blit(overlay, (0, 0))
            
            title_bounce = math.sin(pygame.time.get_ticks() * 0.002) * 8
            title_text = self.font_title.render("NUSANTARA-MON", True, GOLD)
            title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
            self.screen.blit(title_text, (title_x, 120 + title_bounce))
            
            menu_options = [
                ("MULAI PERTARUNGAN", pygame.Rect(SCREEN_WIDTH//2 - 150, 260, 300, 45), self.font_small),
                ("LANJUTKAN", pygame.Rect(SCREEN_WIDTH//2 - 150, 320, 300, 45), self.font_small),
                ("PENGATURAN", pygame.Rect(SCREEN_WIDTH//2 - 150, 380, 300, 45), self.font_small),
                ("KELUAR GAME", pygame.Rect(SCREEN_WIDTH//2 - 150, 440, 300, 45), self.font_small),
                (f"AUDIO: {'OFF' if self.audio_muted else 'ON'}", pygame.Rect(30, SCREEN_HEIGHT - 60, 140, 40), self.font_mini)
            ]

            for i, (text, rect, font_type) in enumerate(menu_options):
                if i == self.menu_index:
                    pygame.draw.rect(self.screen, (40, 40, 10, 220), rect, border_radius=8)
                    pygame.draw.rect(self.screen, GOLD, rect, 3, border_radius=8)
                    alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 255)
                    text_surf = font_type.render(text, True, WHITE)
                    text_surf.set_alpha(max(100, alpha))
                else:
                    pygame.draw.rect(self.screen, (20, 20, 25, 180), rect, border_radius=8)
                    pygame.draw.rect(self.screen, GREY, rect, 2, border_radius=8)
                    text_surf = font_type.render(text, True, LIGHT_GREY)
                self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        elif self.state == "LOADING":
            if self.loading_bg_img: self.screen.blit(self.loading_bg_img, (0, 0))
            else: self.screen.fill(BLACK)
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 15, 20, 180)) 
            self.screen.blit(overlay, (0, 0))
            
            elapsed = pygame.time.get_ticks() - self.loading_timer
            progress = min(1.0, elapsed / 3000)
            
            bar_w, bar_h = 400, 20
            bar_x = (SCREEN_WIDTH // 2) - (bar_w // 2)
            bar_y = (SCREEN_HEIGHT // 2) + 60
            
            pygame.draw.rect(self.screen, (30, 35, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
            pygame.draw.rect(self.screen, GOLD, (bar_x, bar_y, int(bar_w * progress), bar_h), border_radius=10)
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)
            
            texts = ["Menyelaraskan Energi Elemen...", "Membangkitkan Roh Penjaga...", "Siap Memasuki Pertarungan!"]
            text_idx = min(2, int(progress * 3))
            loading_txt = self.font_small.render(texts[text_idx], True, LIGHT_GREY)
            self.screen.blit(loading_txt, loading_txt.get_rect(center=(SCREEN_WIDTH // 2, bar_y - 30)))
            
            bounce = math.sin(pygame.time.get_ticks() * 0.008) * 8
            title_txt = self.font_title.render("LOADING", True, WHITE)
            self.screen.blit(title_txt, title_txt.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) - 50 + bounce)))
            
        elif self.state == "SETTINGS":
            if self.menu_bg_img: self.screen.blit(self.menu_bg_img, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)); self.screen.blit(overlay, (0, 0))
            
            bg_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 200, 600, 400)
            
            if hasattr(self, 'bg_pengaturan') and self.bg_pengaturan: 
                self.screen.blit(self.bg_pengaturan, bg_rect.topleft)
            else:
                pygame.draw.rect(self.screen, (245, 230, 200), bg_rect, border_radius=15)
                pygame.draw.rect(self.screen, (120, 70, 20), bg_rect, 5, border_radius=15)
            
            self.screen.blit(self.font_title.render("PENGATURAN", True, (120, 70, 20)), (SCREEN_WIDTH//2 - 250, bg_rect.y + 30))
            
            bahasa_text = "EASY" if self.language_indo else "HARD"
            layar_text = "AKTIF" if self.is_fullscreen else "NONAKTIF"
            
            set_options = [
                (f"TINGKAT: {bahasa_text}", pygame.Rect(SCREEN_WIDTH//2 - 200, bg_rect.y + 120, 400, 45)),
                (f"LAYAR PENUH: {layar_text}", pygame.Rect(SCREEN_WIDTH//2 - 200, bg_rect.y + 180, 400, 45)),
                ("VOLUME:", pygame.Rect(SCREEN_WIDTH//2 - 200, bg_rect.y + 240, 400, 45)),
                ("SIMPAN & KEMBALI", pygame.Rect(SCREEN_WIDTH//2 - 200, bg_rect.y + 320, 400, 50))
            ]
            
            for i, (text, rect) in enumerate(set_options):
                if i == self.settings_index:
                    pygame.draw.rect(self.screen, (220, 180, 100), rect, border_radius=8)
                    pygame.draw.rect(self.screen, (120, 70, 20), rect, 3, border_radius=8)
                    txt_color = BLACK
                else:
                    pygame.draw.rect(self.screen, (240, 210, 160), rect, border_radius=8)
                    pygame.draw.rect(self.screen, (180, 130, 80), rect, 2, border_radius=8)
                    txt_color = GREY
                
                if i == 2: 
                    self.screen.blit(self.font_small.render(text, True, txt_color), (rect.x + 20, rect.y + 12))
                    bar_w = 150
                    bar_x = rect.x + 220
                    bar_y = rect.y + 12
                    pygame.draw.rect(self.screen, (80, 40, 10), (bar_x, bar_y, bar_w, 20), border_radius=10) 
                    pygame.draw.rect(self.screen, GOLD, (bar_x, bar_y, int(bar_w * self.volume), 20), border_radius=10) 
                    pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, 20), 2, border_radius=10) 
                    vol_txt = self.font_mini.render(f"{int(self.volume * 100)}%", True, WHITE)
                    self.screen.blit(vol_txt, vol_txt.get_rect(center=(bar_x + bar_w//2, bar_y + 10)))
                else:
                    txt_surf = self.font_small.render(text, True, txt_color)
                    self.screen.blit(txt_surf, txt_surf.get_rect(center=rect.center))
            
        elif self.state == "CHARACTER_SELECT":
            if self.select_bg_img: self.screen.blit(self.select_bg_img, (0, 0))
            else:
                for star in self.menu_stardust: star.draw(self.screen)
            
            panel_y = 50
            panel_w, panel_h = 300, 400
            panel_rect_1 = pygame.Rect(80, panel_y, panel_w, panel_h)
            panel_rect_2 = pygame.Rect(420, panel_y, panel_w, panel_h)

            pygame.draw.rect(self.screen, (20, 25, 30, 220), panel_rect_1, border_radius=15)
            pygame.draw.rect(self.screen, (20, 25, 30, 220), panel_rect_2, border_radius=15)

            portrait_rect_1 = pygame.Rect(100, 70, 260, 260)
            try: self.screen.blit(pygame.transform.scale(pygame.image.load("assets/portrait_garuda.png").convert_alpha(), (260, 260)), portrait_rect_1)
            except: pygame.draw.rect(self.screen, (30, 40, 50), portrait_rect_1, border_radius=10)
            
            portrait_rect_2 = pygame.Rect(440, 70, 260, 260)
            try: self.screen.blit(pygame.transform.scale(pygame.image.load("assets/portrait_hanuman.png").convert_alpha(), (260, 260)), portrait_rect_2)
            except: pygame.draw.rect(self.screen, (50, 40, 30), portrait_rect_2, border_radius=10)

            info_y = 350
            self.screen.blit(self.font_mini.render("Elemen: ANGIN", True, CYAN), (100, info_y))
            self.screen.blit(self.font_mini.render("Skill Inti: Patukan, Semburan Api", True, WHITE), (100, info_y + 20))
            
            self.screen.blit(self.font_mini.render("Elemen: BUMI", True, GOLD), (440, info_y))
            self.screen.blit(self.font_mini.render("Skill Inti: Tabrak, Lemparan Batu", True, WHITE), (440, info_y + 20))

            btn_garuda_rect = pygame.Rect(130, 480, 200, 45)
            btn_hanuman_rect = pygame.Rect(470, 480, 200, 45)

            if self.char_select_index == 0:
                pygame.draw.rect(self.screen, CYAN, panel_rect_1, 4, border_radius=15)
                pygame.draw.rect(self.screen, CYAN, btn_garuda_rect, 4, border_radius=8)
                pygame.draw.rect(self.screen, GREY, panel_rect_2, 2, border_radius=15)
                pygame.draw.rect(self.screen, GREY, btn_hanuman_rect, 2, border_radius=8)
            elif self.char_select_index == 1:
                pygame.draw.rect(self.screen, GREY, panel_rect_1, 2, border_radius=15)
                pygame.draw.rect(self.screen, GREY, btn_garuda_rect, 2, border_radius=8)
                pygame.draw.rect(self.screen, GOLD, panel_rect_2, 4, border_radius=15)
                pygame.draw.rect(self.screen, GOLD, btn_hanuman_rect, 4, border_radius=8)
                
            pygame.draw.rect(self.screen, (30, 60, 80), btn_garuda_rect, border_radius=8)
            self.screen.blit(self.font_small.render(" GARUDA-MON", True, WHITE), self.font_small.render(" GARUDA-MON", True, WHITE).get_rect(center=btn_garuda_rect.center))
            pygame.draw.rect(self.screen, (80, 50, 30), btn_hanuman_rect, border_radius=8)
            self.screen.blit(self.font_small.render(" HANUMAN-MON", True, WHITE), self.font_small.render(" HANUMAN-MON", True, WHITE).get_rect(center=btn_hanuman_rect.center))

            if self.flash_color:
                flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                flash_surf.fill(self.flash_color); flash_surf.set_alpha(150)
                self.screen.blit(flash_surf, (0, 0))

        elif self.state in ["MAP", "DIALOG", "TRANSITION_THROW", "WIPE_IN"]:
            if self.map_bg_img: self.screen.blit(self.map_bg_img, (-self.cam_x + shake_x, -self.cam_y + shake_y))
            else: self.screen.fill(GREEN)
            
            for m in self.map_monsters: m.draw(self.screen, self.cam_x, self.cam_y)
            for npc in self.npcs: npc.draw(self.screen, self.cam_x, self.cam_y)
            self.guard_npc.draw(self.screen, self.cam_x, self.cam_y)
            self.boss_npc.draw(self.screen, self.cam_x, self.cam_y)
            self.player.draw(self.screen, self.cam_x, self.cam_y)
            
            if self.state == "TRANSITION_THROW" and self.active_jimat:
                self.active_jimat.draw(self.screen, self.cam_x, self.cam_y)
            
            for vp in self.victory_particles: vp.draw(self.screen, self.cam_x, self.cam_y)
            for drop in self.rain_drops: drop.draw(self.screen)
            
            time_cycle = (self.player.steps_taken // 1000) % 3
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            if time_cycle == 1: overlay.fill((255, 100, 0, 40))
            elif time_cycle == 2: overlay.fill((0, 0, 80, 120))
            self.screen.blit(overlay, (0, 0))
            
            for ft in self.floating_texts: ft.draw(self.screen)
            self.player.draw_ml_hud(self.screen, self.font_mini, self.cam_x, self.cam_y)
            self.draw_minimap()

            if self.state == "DIALOG" and self.active_npc:
                dialog_bg = pygame.Surface((700, 110), pygame.SRCALPHA)
                dialog_bg.fill((10, 15, 20, 230)); self.screen.blit(dialog_bg, (50, 440))
                pygame.draw.rect(self.screen, GREY, (50, 440, 700, 110), 1)
                name_bg = pygame.Surface((200, 35), pygame.SRCALPHA)
                name_bg.fill((5, 5, 10, 255)); self.screen.blit(name_bg, (50, 405))
                pygame.draw.rect(self.screen, GOLD, (50, 405, 200, 35), 1)
                self.screen.blit(self.font.render(self.active_npc.name, True, GOLD), (60, 410))
                
                displayed_text = self.active_npc.message[:self.text_idx]
                self.screen.blit(self.font.render(displayed_text, True, WHITE), (70, 470))
                if self.text_idx >= len(self.active_npc.message) and (pygame.time.get_ticks() // 300) % 2 == 0:
                    pygame.draw.polygon(self.screen, GOLD, [(720, 520), (740, 520), (730, 535)])

            if self.state == "WIPE_IN":
                pygame.draw.circle(self.screen, BLACK, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), int(self.wipe_radius) + 1500, 1500)

        elif self.state in ["BATTLE", "BATTLE_END"]:
            if self.is_boss_fight and self.boss_bg_img:
                self.screen.blit(self.boss_bg_img, (shake_x, shake_y))
            elif self.battle_bg_img: 
                self.screen.blit(self.battle_bg_img, (shake_x, shake_y))
            else: self.screen.fill(GREY)
                
            self.player.partner.draw_battle(self.screen, self.font_small, shake_x, shake_y)
            self.wild_monster.draw_battle(self.screen, self.font_small, shake_x, shake_y)
            
            vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(vignette, (0, 0, 0, 60), (0, 0, SCREEN_WIDTH, 70))
            pygame.draw.rect(vignette, (0, 0, 0, 120), (0, SCREEN_HEIGHT - 180, SCREEN_WIDTH, 180))
            self.screen.blit(vignette, (0, 0))
            
            if self.show_claw_effect:
                c_elapsed = pygame.time.get_ticks() - self.claw_effect_timer
                if c_elapsed < 200:
                    target = self.wild_monster if self.pending_attack["attacker"] == self.player.partner else self.player.partner
                    target_x = target.rect.x + target.render_offset_x + shake_x
                    target_y = 450 - 90 - 60 
                    if self.claw_effect_img:
                        self.screen.blit(self.claw_effect_img, (target_x + 30, target_y))
                    else:
                        pygame.draw.line(self.screen, WHITE, (target_x+30, target_y+30), (target_x+150, target_y+150), 5)
                        pygame.draw.line(self.screen, WHITE, (target_x+150, target_y+30), (target_x+30, target_y+150), 5)
                else:
                    self.show_claw_effect = False
            
            if self.active_projectile: self.active_projectile.draw(self.screen)
            for p in self.particles: p.draw(self.screen)
            for vp in self.victory_particles: vp.draw(self.screen) 
            
            if self.is_boss_fight and self.wild_monster.name == "Raja Jin":
                pygame.draw.rect(self.screen, BLACK, (190, 30, 420, 30))
                pygame.draw.rect(self.screen, WHITE, (190, 30, 420, 30), 2)
                pygame.draw.rect(self.screen, RED, (200, 35, 400, 20))
                pygame.draw.rect(self.screen, PURPLE, (200, 35, int(400 * (self.wild_monster.hp / self.wild_monster.max_hp)), 20))
                self.screen.blit(self.font.render("RAJA JIN", True, WHITE), (350, 5))
            
            for ft in self.floating_texts: ft.draw(self.screen)

            menu_bg = pygame.Surface((740, 140), pygame.SRCALPHA)
            menu_bg.fill((10, 15, 20, 230)); self.screen.blit(menu_bg, (30, 430))
            pygame.draw.rect(self.screen, GREY, (30, 430, 740, 140), 1) 
            self.screen.blit(self.font_small.render(self.battle_msg, True, GOLD), (50, 445))
            
            if self.battle_state == "PLAYER_TURN" and self.state != "BATTLE_END":
                pygame.draw.line(self.screen, GREY, (30, 475), (770, 475), 1)
                s1 = self.player.partner.skills[0].name
                s2 = self.player.partner.skills[1].name if len(self.player.partner.skills) > 1 else ""
                s3 = self.player.partner.skills[2].name if len(self.player.partner.skills) > 2 else ""
                s4 = self.player.partner.skills[3].name if len(self.player.partner.skills) > 3 else ""
                item_info = f"Jamu ({len(self.player.inventory)})"
                
                btn_color = (40, 45, 50)
                pygame.draw.rect(self.screen, btn_color, (50, 485, 300, 30), border_radius=5)
                pygame.draw.rect(self.screen, btn_color, (390, 485, 300, 30), border_radius=5)
                pygame.draw.rect(self.screen, btn_color, (50, 525, 300, 30), border_radius=5)
                pygame.draw.rect(self.screen, btn_color, (390, 525, 300, 30), border_radius=5)

                self.screen.blit(self.font_small.render(f"[1] {s1}", True, WHITE), (60, 490))
                self.screen.blit(self.font_small.render(f"[2] {s2}", True, WHITE), (400, 490))
                
                if s3:
                    self.screen.blit(self.font_small.render(f"[3] {s3}", True, WHITE), (60, 530))
                    if s4: self.screen.blit(self.font_small.render(f"[4] {s4}", True, WHITE), (400, 530))
                    else: self.screen.blit(self.font_small.render(f"[SPACE] Item: {item_info}", True, WHITE), (400, 530))
                else:
                    self.screen.blit(self.font_small.render(f"[3] Item: {item_info}", True, WHITE), (60, 530))
                    self.screen.blit(self.font_small.render(f"[4] LOCKED", True, GREY), (400, 530))

        if self.damage_flash and self.flash_color:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill(self.flash_color); flash_surf.set_alpha(150)
            self.screen.blit(flash_surf, (0, 0))
            
        pygame.display.flip()

if __name__ == "__main__":
    game = GameEngine(); game.run()