"""
Audio Client - Runs WITHOUT sudo to capture audio and recognize notes
Sends control commands to the control server via socket
"""

import socket
import json
import sys
from note_recognizer import NoteRecognizer


class AudioClient:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.socket = None
        self.running = True
        
        # Note to action mapping
        self.note_actions = {
            'C': 'cycle_card',    # Cycle through cards 1-4
            'D': 'move_up',       # Up
            'E': 'move_down',     # Down
            'F': 'move_left',     # Left
            'G': 'move_right',    # Right
            'A': 'place_card',    # Place
        }
        
        # Initialize note recognizer
        self.note_recognizer = NoteRecognizer(self.on_note_detected)
    
    def connect(self):
        """Connect to the control server"""
        print("Connecting to control server...")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✓ Connected to control server at {self.host}:{self.port}\n")
            return True
        except ConnectionRefusedError:
            print(f"✗ Could not connect to control server at {self.host}:{self.port}")
            print("\n💡 Make sure the control server is running:")
            print("    sudo python3 control_server.py")
            return False
    
    def send_command(self, action, **kwargs):
        """Send a command to the control server"""
        if not self.socket:
            return
        
        try:
            command = {'action': action, **kwargs}
            self.socket.sendall(json.dumps(command).encode('utf-8'))
        except (BrokenPipeError, ConnectionResetError):
            print("✗ Lost connection to control server")
            self.running = False
    
    def on_note_detected(self, note):
        """Called when a note is detected from the recorder"""
        if note in self.note_actions:
            action = self.note_actions[note]
            print(f"🎵 Note {note} detected → {action}")
            self.send_command(action)
        else:
            print(f"⚠️  Unknown note: {note}")
    
    def run(self):
        """Start the audio client"""
        print("=" * 60)
        print("Clash Royale Audio Client")
        print("=" * 60)
        print("\n🎵 Recorder Note Controls:")
        print("  C  - Select Card (cycles: 1→2→3→4→1...)")
        print("  D  - Up")
        print("  E  - Down")
        print("  F  - Left")
        print("  G  - Right")
        print("  A  - Place")
        print("\n  Note: Playing C multiple times cycles through cards.")
        print("        Any other action resets cycling back to Card 1.")
        print("=" * 60)
        print()
        
        # Connect to control server
        if not self.connect():
            sys.exit(1)
        
        # Start note recognition
        print("Starting note recognition...")
        self.note_recognizer.start()
        print("✓ Note recognition started")
        print("\n🎤 Play your recorder notes!\n")
        print("Press Ctrl+C to exit")
        print("=" * 60)
        print()
        
        try:
            # Keep the program running
            while self.running:
                import time
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup and exit"""
        print("\n\nExiting...")
        
        # Stop note recognition
        self.note_recognizer.stop()
        
        # Close socket
        if self.socket:
            self.send_command('exit')
            self.socket.close()
        
        print("Audio client stopped.")


if __name__ == "__main__":
    try:
        client = AudioClient()
        client.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
