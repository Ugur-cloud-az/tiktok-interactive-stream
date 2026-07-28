#!/usr/bin/env python3
import os

def setup_project():
    """Create complete project structure."""
    
    # Create directories
    os.makedirs("src", exist_ok=True)
    
    # Create requirements.txt
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write("pygame>=2.6.0\n")
    
    # Create src/__init__.py
    with open("src/__init__.py", "w", encoding="utf-8") as f:
        f.write('"""TikTok Stream Game"""\n__version__ = "1.0.0"\n')
    
    # Create src/player.py
    with open("src/player.py", "w", encoding="utf-8") as f:
        f.write('''"""Player class"""
import math

class Player:
    def __init__(self, user_id, nickname, x=540, y=960, radius=20):
        self.user_id = user_id
        self.nickname = nickname
        self.x = x
        self.y = y
        self.radius = radius
        self.max_hp = 100
        self.hp = self.max_hp
        self.speed = 5
        self.is_attacking = False
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        self.last_shot_time = 0
        self.shoot_cooldown = 0.5
    
    def update(self, current_time, screen_width=1080, screen_height=1920):
        if self.moving_up:
            self.y = max(self.radius, self.y - self.speed)
        if self.moving_down:
            self.y = min(screen_height - self.radius, self.y + self.speed)
        if self.moving_left:
            self.x = max(self.radius, self.x - self.speed)
        if self.moving_right:
            self.x = min(screen_width - self.radius, self.x + self.speed)
    
    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
    
    def is_alive(self):
        return self.hp > 0
    
    def can_shoot(self, current_time):
        return current_time - self.last_shot_time >= self.shoot_cooldown
    
    def shoot(self, current_time):
        if self.can_shoot(current_time):
            self.last_shot_time = current_time
            return True
        return False
    
    def move_up(self):
        self.moving_up = True
    
    def move_down(self):
        self.moving_down = True
    
    def move_left(self):
        self.moving_left = True
    
    def move_right(self):
        self.moving_right = True
    
    def stop_up(self):
        self.moving_up = False
    
    def stop_down(self):
        self.moving_down = False
    
    def stop_left(self):
        self.moving_left = False
    
    def stop_right(self):
        self.moving_right = False
    
    def start_attacking(self):
        self.is_attacking = True
    
    def stop_attacking(self):
        self.is_attacking = False
''')
    
    # Create src/bullet.py
    with open("src/bullet.py", "w", encoding="utf-8") as f:
        f.write('''"""Bullet class"""
import math

class Bullet:
    def __init__(self, x, y, vx, vy, owner_id, damage=5, width=10, height=5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.owner_id = owner_id
        self.damage = damage
        self.width = width
        self.height = height
        self.speed = 8
        self.active = True
    
    def update(self, screen_width=1080, screen_height=1920):
        magnitude = math.sqrt(self.vx**2 + self.vy**2)
        if magnitude > 0:
            vx_norm = self.vx / magnitude
            vy_norm = self.vy / magnitude
        else:
            vx_norm = 0
            vy_norm = -1
        
        self.x += vx_norm * self.speed
        self.y += vy_norm * self.speed
        
        if self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height:
            self.active = False
    
    def is_active(self):
        return self.active
    
    def deactivate(self):
        self.active = False
''')
    
    # Create src/network.py
    with open("src/network.py", "w", encoding="utf-8") as f:
        f.write('''"""Network server"""
import socket
import threading
import json
from queue import Queue

class NetworkServer:
    def __init__(self, host="localhost", port=5555):
        self.host = host
        self.port = port
        self.command_queue = Queue()
        self.running = False
        self.server_thread = None
        self.socket = None
    
    def start(self):
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"Network server started on {self.host}:{self.port}")
    
    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
    
    def _run_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.settimeout(1.0)
            
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(1024)
                    command = data.decode('utf-8')
                    self._parse_command(command)
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"Server error: {e}")
    
    def _parse_command(self, command):
        try:
            cmd_dict = json.loads(command)
            self.command_queue.put(cmd_dict)
        except:
            pass
    
    def get_command(self):
        try:
            return self.command_queue.get_nowait()
        except:
            return None
    
    def has_commands(self):
        return not self.command_queue.empty()
''')
    
    # Create src/chat_sim.py
    with open("src/chat_sim.py", "w", encoding="utf-8") as f:
        f.write('''"""Chat simulator"""
import threading
import time
import random
from queue import Queue

class ChatSimulator:
    def __init__(self, command_queue=None):
        self.command_queue = command_queue or Queue()
        self.running = False
        self.sim_thread = None
        self.user_pool = [
            {"user_id": f"user_{i:03d}", "nickname": f"Player{i}"}
            for i in range(1, 6)
        ]
        self.active_players = set()
    
    def start(self):
        self.running = True
        self.sim_thread = threading.Thread(target=self._run_simulator, daemon=True)
        self.sim_thread.start()
        print("Chat Simulator started")
    
    def stop(self):
        self.running = False
    
    def _run_simulator(self):
        spawn_delay = 1
        while self.running:
            user = random.choice(self.user_pool)
            user_id = user["user_id"]
            nickname = user["nickname"]
            
            if user_id not in self.active_players:
                if random.random() < 0.7 and spawn_delay > 0:
                    spawn_delay -= 1
                    command = {
                        "user_id": user_id,
                        "nickname": nickname,
                        "command": "spawn"
                    }
                    self.command_queue.put(command)
                    self.active_players.add(user_id)
                    print(f"[Chat] {nickname} spawned")
            elif random.random() < 0.8:
                actions = ["move_up", "move_down", "move_left", "move_right", "attack", "stop"]
                action = random.choice(actions)
                command = {
                    "user_id": user_id,
                    "nickname": nickname,
                    "command": action
                }
                self.command_queue.put(command)
                if action != "stop":
                    print(f"[Chat] {nickname} -> {action}")
            
            time.sleep(random.uniform(2, 5))
    
    def get_command(self):
        try:
            return self.command_queue.get_nowait()
        except:
            return None
''')
    
    # Create src/game.py
    with open("src/game.py", "w", encoding="utf-8") as f:
        f.write('''"""Game engine"""
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
''')
    
    # Create main.py
    with open("main.py", "w", encoding="utf-8") as f:
        f.write('''#!/usr/bin/env python3
"""Main entry point"""
from src.game import GameEngine
from src.network import NetworkServer
from src.chat_sim import ChatSimulator

def main():
    print("=" * 50)
    print("TikTok Stream Game - Starting...")
    print("=" * 50)
    
    network = NetworkServer(host="localhost", port=5555)
    network.start()
    
    chat_sim = ChatSimulator(command_queue=None)
    chat_sim.start()
    
    game = GameEngine(width=1080, height=1920)
    
    class CommandAggregator:
        def __init__(self, network, chat):
            self.network = network
            self.chat = chat
        
        def get_command(self):
            cmd = self.network.get_command()
            if cmd:
                return cmd
            return self.chat.get_command()
        
        def has_commands(self):
            return self.network.has_commands() or not self.chat.command_queue.empty()
    
    command_source = CommandAggregator(network, chat_sim)
    
    try:
        print()
        print("=" * 50)
        print("Game is running! Press ESC to exit...")
        print("=" * 50)
        game.run(command_source)
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        network.stop()
        chat_sim.stop()
        print("Shutdown complete")

if __name__ == "__main__":
    main()
''')
    
    print("Project setup completed!")
    print("\nNext steps:")
    print("1. pip install -r requirements.txt")
    print("2. python main.py")

if __name__ == "__main__":
    setup_project()