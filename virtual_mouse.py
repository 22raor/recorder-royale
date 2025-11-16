"""
Virtual Mouse using uinput
Creates a kernel-level virtual mouse device that works on Wayland
"""

import time
from evdev import UInput, ecodes


class VirtualMouse:
    def __init__(self):
        """Initialize virtual mouse device"""
        # Define the capabilities of our virtual mouse
        cap = {
            ecodes.EV_REL: (ecodes.REL_X, ecodes.REL_Y),  # Relative movement
            ecodes.EV_KEY: (ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE),  # Mouse buttons
        }
        
        try:
            self.ui = UInput(cap, name='clash-virtual-mouse', version=0x3)
            print("✓ Virtual mouse device created successfully!")
            print(f"  Device: {self.ui.device.path}")
            time.sleep(0.1)  # Give the system time to register the device
        except Exception as e:
            print(f"✗ Failed to create virtual mouse: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure you're running with sudo")
            print("2. Load uinput module: sudo modprobe uinput")
            print("3. Check permissions: ls -l /dev/uinput")
            raise
    
    def move(self, dx, dy):
        """Move mouse relatively by (dx, dy) pixels"""
        # Break large movements into smaller chunks for smoother motion
        steps = max(abs(dx), abs(dy)) // 10 + 1
        
        for i in range(steps):
            step_dx = dx // steps if i < steps - 1 else dx - (dx // steps) * (steps - 1)
            step_dy = dy // steps if i < steps - 1 else dy - (dy // steps) * (steps - 1)
            
            if step_dx != 0:
                self.ui.write(ecodes.EV_REL, ecodes.REL_X, step_dx)
            if step_dy != 0:
                self.ui.write(ecodes.EV_REL, ecodes.REL_Y, step_dy)
            
            self.ui.syn()
            time.sleep(0.001)  # Small delay for smooth movement
    
    def mouse_down(self, button=None):
        """Press mouse button down"""
        if button is None:
            button = ecodes.BTN_LEFT
        self.ui.write(ecodes.EV_KEY, button, 1)
        self.ui.syn()
    
    def mouse_up(self, button=None):
        """Release mouse button"""
        if button is None:
            button = ecodes.BTN_LEFT
        self.ui.write(ecodes.EV_KEY, button, 0)
        self.ui.syn()
    
    def click(self, button=None):
        """Perform a complete click"""
        if button is None:
            button = ecodes.BTN_LEFT
        self.mouse_down(button)
        time.sleep(0.05)
        self.mouse_up(button)
    
    def close(self):
        """Clean up the virtual device"""
        if hasattr(self, 'ui'):
            self.ui.close()
            print("Virtual mouse device closed")


if __name__ == "__main__":
    """Test the virtual mouse"""
    print("Testing Virtual Mouse...")
    print("Make sure you run this with sudo!")
    print()
    
    try:
        mouse = VirtualMouse()
        
        print("\nMoving mouse in a square pattern...")
        print("(Watch your cursor move!)")
        time.sleep(1)
        
        # Move in a square
        print("→ Moving right 200px")
        mouse.move(200, 0)
        time.sleep(0.5)
        
        print("↓ Moving down 200px")
        mouse.move(0, 200)
        time.sleep(0.5)
        
        print("← Moving left 200px")
        mouse.move(-200, 0)
        time.sleep(0.5)
        
        print("↑ Moving up 200px")
        mouse.move(0, -200)
        time.sleep(0.5)
        
        print("\n✓ Test complete!")
        
        mouse.close()
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
