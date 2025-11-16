"""
Control Server - Runs with sudo to handle keyboard and mouse control
Listens for commands via local socket
"""

import keyboard
import socket
import json
import sys
from mouse_controller import MouseController


class ControlServer:
    def __init__(self, port=9999):
        self.controller = MouseController()
        self.port = port
        self.running = True
        
        # Card cycling state
        self.current_card_cycle = 0
        self.last_action_was_card_select = False
        
        # Setup socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', self.port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(0.1)  # Non-blocking with timeout
        
    def cycle_card_select(self):
        """Cycle through cards 1-4"""
        if self.last_action_was_card_select:
            self.current_card_cycle = (self.current_card_cycle + 1) % 4
        else:
            self.current_card_cycle = 0
        
        self.last_action_was_card_select = True
        card_number = self.current_card_cycle + 1
        print(f"🎴 Cycling to card {card_number}")
        self.controller.select_card(card_number)
    
    def handle_command(self, command):
        """Execute a command"""
        action = command.get('action')
        
        if action == 'select_card':
            card = command.get('card', 1)
            self.controller.select_card(card)
            self.last_action_was_card_select = False
        elif action == 'cycle_card':
            self.cycle_card_select()
        elif action == 'move_up':
            self.controller.move_up()
            self.last_action_was_card_select = False
        elif action == 'move_down':
            self.controller.move_down()
            self.last_action_was_card_select = False
        elif action == 'move_left':
            self.controller.move_left()
            self.last_action_was_card_select = False
        elif action == 'move_right':
            self.controller.move_right()
            self.last_action_was_card_select = False
        elif action == 'place_card':
            self.controller.place_card()
            self.last_action_was_card_select = False
        elif action == 'reset':
            self.controller.reset()
            self.last_action_was_card_select = False
        elif action == 'exit':
            self.running = False
        else:
            print(f"⚠️  Unknown action: {action}")
    
    def run(self):
        """Start the control server"""
        print("=" * 60)
        print("Clash Royale Control Server")
        print("=" * 60)
        print(f"\n🎮 Control server listening on localhost:{self.port}")
        print("\n🎹 Keyboard Controls:")
        print("  1, 2, 3, 4  - Select card from deck")
        print("  Arrow Keys  - Move/drag card on field")
        print("  SPACE       - Place card (release and return to Card 1)")
        print("  R           - Reset (cancel placement)")
        print("  ESC         - Exit program")
        print("\n💡 Run the audio client in a separate terminal (without sudo):")
        print("    python3 audio_client.py")
        print("=" * 60)
        print()
        
        # Register keyboard hotkeys
        keyboard.add_hotkey('1', lambda: self.controller.select_card(1), suppress=False)
        keyboard.add_hotkey('2', lambda: self.controller.select_card(2), suppress=False)
        keyboard.add_hotkey('3', lambda: self.controller.select_card(3), suppress=False)
        keyboard.add_hotkey('4', lambda: self.controller.select_card(4), suppress=False)
        keyboard.add_hotkey('up', self.controller.move_up, suppress=False)
        keyboard.add_hotkey('down', self.controller.move_down, suppress=False)
        keyboard.add_hotkey('left', self.controller.move_left, suppress=False)
        keyboard.add_hotkey('right', self.controller.move_right, suppress=False)
        keyboard.add_hotkey('space', self.controller.place_card, suppress=False)
        keyboard.add_hotkey('r', self.controller.reset, suppress=False)
        keyboard.add_hotkey('esc', self.on_exit, suppress=False)
        
        print("✓ Keyboard controls registered")
        print("✓ Waiting for audio client connection...\n")
        
        client_socket = None
        
        try:
            while self.running:
                # Accept new connections
                if client_socket is None:
                    try:
                        client_socket, addr = self.server_socket.accept()
                        client_socket.settimeout(0.1)
                        print(f"✓ Audio client connected from {addr}")
                    except socket.timeout:
                        pass
                
                # Receive commands from client
                if client_socket:
                    try:
                        data = client_socket.recv(1024)
                        if data:
                            command = json.loads(data.decode('utf-8'))
                            self.handle_command(command)
                        else:
                            # Client disconnected
                            print("✗ Audio client disconnected")
                            client_socket.close()
                            client_socket = None
                    except socket.timeout:
                        pass
                    except (ConnectionResetError, BrokenPipeError):
                        print("✗ Audio client disconnected")
                        client_socket.close()
                        client_socket = None
                    except json.JSONDecodeError:
                        print("⚠️  Received invalid JSON")
        
        except KeyboardInterrupt:
            pass
        
        finally:
            if client_socket:
                client_socket.close()
            self.server_socket.close()
            print("\n\nControl server stopped.")
    
    def on_exit(self):
        """Cleanup and exit"""
        print("\n\nExiting...")
        if self.controller.mouse_pressed:
            self.controller.reset()
        self.running = False


if __name__ == "__main__":
    try:
        server = ControlServer()
        server.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
