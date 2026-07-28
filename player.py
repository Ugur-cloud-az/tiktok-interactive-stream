"""Player class"""
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
