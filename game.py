"""Game engine"""
import pygame
import math
import time
from src.player import Player
from src.bullet import Bullet

class GameEngine:
    def __init__(self, width=1080, height=1920):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("TikTok Stream Game")
        self.clock = pygame.time.Clock()
        self.running = False
        self.fps = 60
        self.players = {}
        self.bullets = []
        self.current_time = 0
        
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.WHITE = (255, 255, 255)
        
        self.small_font = pygame.font.Font(None, 20)
        self.medium_font = pygame.font.Font(None, 24)
    
    def run(self, command_source):
        self.running = True
        print("Game engine started")
        
        while self.running:
            self.current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self._process_commands(command_source)
            self._update()
            self._render()
            self.clock.tick(self.fps)
        
        pygame.quit()
    
    def _process_commands(self, command_source):
        while command_source.has_commands():
            command = command_source.get_command()
            if command:
                self._handle_command(command)
    
    def _handle_command(self, command):
        user_id = command.get("user_id", "unknown")
        nickname = command.get("nickname", "Player")
        cmd = command.get("command", "").lower()
        
        if cmd == "spawn":
            if user_id not in self.players:
                x = 540 + (hash(user_id) % 200 - 100)
                y = 960 + (hash(user_id + "y") % 200 - 100)
                player = Player(user_id, nickname, x, y)
                self.players[user_id] = player
                print(f"[Game] {nickname} spawned")
        
        elif cmd == "move_up" and user_id in self.players:
            self.players[user_id].move_up()
        elif cmd == "move_down" and user_id in self.players:
            self.players[user_id].move_down()
        elif cmd == "move_left" and user_id in self.players:
            self.players[user_id].move_left()
        elif cmd == "move_right" and user_id in self.players:
            self.players[user_id].move_right()
        
        elif cmd == "stop_up" and user_id in self.players:
            self.players[user_id].stop_up()
        elif cmd == "stop_down" and user_id in self.players:
            self.players[user_id].stop_down()
        elif cmd == "stop_left" and user_id in self.players:
            self.players[user_id].stop_left()
        elif cmd == "stop_right" and user_id in self.players:
            self.players[user_id].stop_right()
        
        elif cmd == "attack" and user_id in self.players:
            self.players[user_id].start_attacking()
        elif cmd == "stop" and user_id in self.players:
            self.players[user_id].stop_attacking()
    
    def _update(self):
        for player in self.players.values():
            player.update(self.current_time, self.width, self.height)
            
            if player.is_attacking and player.can_shoot(self.current_time):
                player.shoot(self.current_time)
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    vx = math.cos(rad)
                    vy = math.sin(rad)
                    bullet = Bullet(player.x, player.y, vx, vy, player.user_id, damage=5)
                    self.bullets.append(bullet)
        
        for bullet in self.bullets[:]:
            bullet.update(self.width, self.height)
            if not bullet.is_active():
                self.bullets.remove(bullet)
        
        self._check_collisions()
        
        dead_players = [uid for uid, p in self.players.items() if not p.is_alive()]
        for uid in dead_players:
            del self.players[uid]
    
    def _check_collisions(self):
        for bullet in self.bullets[:]:
            for player in self.players.values():
                if bullet.owner_id == player.user_id:
                    continue
                dx = bullet.x - player.x
                dy = bullet.y - player.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < player.radius + bullet.width:
                    player.take_damage(bullet.damage)
                    bullet.deactivate()
                    break
    
    def _render(self):
        self.screen.fill(self.BLACK)
        
        for player in self.players.values():
            pygame.draw.circle(self.screen, self.GREEN, (int(player.x), int(player.y)), player.radius)
            
            nick_text = self.small_font.render(player.nickname[:15], True, self.WHITE)
            nick_rect = nick_text.get_rect(center=(int(player.x), int(player.y) - 40))
            self.screen.blit(nick_text, nick_rect)
            
            bar_width = 50
            bar_height = 5
            hp_ratio = player.hp / player.max_hp
            
            pygame.draw.rect(self.screen, (100, 0, 0), 
                           (int(player.x) - bar_width//2, int(player.y) - 25, bar_width, bar_height))
            pygame.draw.rect(self.screen, self.RED, 
                           (int(player.x) - bar_width//2, int(player.y) - 25, int(bar_width * hp_ratio), bar_height))
            
            hp_text = self.small_font.render(f"HP: {int(player.hp)}/{int(player.max_hp)}", True, self.WHITE)
            hp_rect = hp_text.get_rect(center=(int(player.x), int(player.y) - 10))
            self.screen.blit(hp_text, hp_rect)
        
        for bullet in self.bullets:
            pygame.draw.rect(self.screen, self.RED, 
                           (int(bullet.x - bullet.width//2), int(bullet.y - bullet.height//2), bullet.width, bullet.height))
        
        player_count_text = self.medium_font.render(
            f"Players: {len(self.players)} | Bullets: {len(self.bullets)}", True, self.WHITE)
        self.screen.blit(player_count_text, (10, 10))
        
        pygame.display.flip()
