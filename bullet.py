"""Bullet class"""
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
