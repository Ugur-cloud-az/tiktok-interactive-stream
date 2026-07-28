#!/usr/bin/env python3
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
