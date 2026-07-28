"""Network server"""
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
