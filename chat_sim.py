"""Chat simulator"""
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
