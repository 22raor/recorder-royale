import time
from enum import Enum
from virtual_mouse import VirtualMouse


class State(Enum):
    IDLE = "idle"  # No card selected
    CARD_SELECTED = "card_selected"  # Card selected but not placed on field
    PLACING = "placing"  # Currently dragging card on field


class MouseController:
    def __init__(self):
        # Relative distances between cards (calculated from calibration)
        # Card 1 is at (1304, 1593) - this is our reference point (0, 0)
        # Card 2 is at (1507, 1588) - offset: (+203, -5)
        # Card 3 is at (1689, 1586) - offset: (+385, -7)
        # Card 4 is at (1869, 1583) - offset: (+565, -10)
        self.CARD_OFFSETS = {
            1: (0, 0),       # Card 1 - reference point
            2: (103, 0),    # Card 2 - relative to Card 1
            3: (180, 0),    # Card 3 - relative to Card 1
            4: (270, 0)    # Card 4 - relative to Card 1
        }
        
        # Movement step size
        self.MOVE_STEP = 50
        
        # State tracking
        self.state = State.IDLE
        self.current_card = None
        self.mouse_pressed = False
        
        # Relative position tracking (relative to Card 1)
        # Assume mouse starts on Card 1 position
        self.relative_x = 0
        self.relative_y = 0
        
        # Create virtual mouse device
        self.mouse = VirtualMouse()
        print("Virtual mouse ready!")
        
    def place_card(self):
        """Place the card at current position and return to Card 1"""
        if self.state == State.IDLE:
            print("No card to place")
            return
        
        print("Placing card...")
        
        # Release mouse if pressed
        if self.mouse_pressed:
            self.mouse.mouse_up()
            self.mouse_pressed = False
            print("  - Released mouse button")
        
        # Wait a moment for the card to register
        time.sleep(0.1)
        
        # Move back to Card 1 (reference position)
        print(f"  - Returning to Card 1 from ({self.relative_x}, {self.relative_y})")
        self.mouse.move(-self.relative_x, -self.relative_y)
        self.relative_x = 0
        self.relative_y = 0
        
        # Reset state
        self.state = State.IDLE
        self.current_card = None
        print("  - Returned to Card 1, ready for next card")
    
    def reset(self):
        """Cancel placement and return to bottom-right corner then back to Card 1"""
        print("Resetting (canceling)...")
        
        # if self.mouse_pressed:
            # Move way down (positive Y) and way left (positive X) to get card off screen
        self.mouse.move(-1000, 1000)
        time.sleep(0.1)
        # self.mouse.mouse_up()
        
        if self.mouse_pressed:
            self.mouse.mouse_up()
            self.mouse_pressed = False
            print("  - Released mouse button")
        print("  - Moved to bottom-left and released")
        
        # Move back to Card 1 reference position
        # Move left (negative X) and up (negative Y) to approximate Card 1
        self.mouse.move(550,-80)
        time.sleep(0.1)
        
        # Reset internal state
        self.state = State.IDLE
        self.current_card = None
        self.mouse_pressed = False
        self.relative_x = 0
        self.relative_y = 0
        print("  - State reset to IDLE, back at Card 1---")
        
    def select_card(self, card_number):
        """Select a card (1-4) from the deck"""
        if card_number not in [1, 2, 3, 4]:
            print(f"Invalid card number: {card_number}")
            return
        
        print(f"Selecting card {card_number}")
        
        
        # First reset if needed
        if self.state != State.IDLE:
            self.reset()
            # After reset, we need to move back to Card 1 reference position
            # Move back to relative (0, 0) which is Card 1
            self.mouse.move(-self.relative_x, -self.relative_y)
            time.sleep(0.2)
            self.relative_x = 0
            self.relative_y = 0
        
        if self.mouse_pressed:
            self.mouse.mouse_up()
            self.mouse_pressed = False
            print("  - Released mouse button")
        
        
        # Move to card position (relative to Card 1)
        offset_x, offset_y = self.CARD_OFFSETS[card_number]
        
        # If we're not at Card 1, first go back to Card 1
        if self.relative_x != 0 or self.relative_y != 0:
            self.mouse.move(-self.relative_x, -self.relative_y)
            time.sleep(0.1)
            self.relative_x = 0
            self.relative_y = 0
        
        # Now move to target card
        if offset_x != 0 or offset_y != 0:
            self.mouse.move(offset_x, offset_y)
            time.sleep(0.2)
            self.relative_x = offset_x
            self.relative_y = offset_y
        
        # Update state
        self.state = State.CARD_SELECTED
        self.current_card = card_number
        print(f"  - Card {card_number} selected at relative position ({self.relative_x}, {self.relative_y})")
        
    def move_up(self):
        """Move mouse up (or start dragging up if card selected)"""
        if self.state == State.IDLE:
            print("No card selected, move_up does nothing")
            return
        
        if self.state == State.CARD_SELECTED:
            # Click down and start dragging
            self.mouse.mouse_down()
            self.mouse_pressed = True
            self.state = State.PLACING
            print("Mouse pressed down, entering PLACING state")
        
        # Move up relatively
        self.mouse.move(0, -self.MOVE_STEP)
        time.sleep(0.1)
        self.relative_y -= self.MOVE_STEP
        print(f"  - Moved to relative position ({self.relative_x}, {self.relative_y})")
        
    def move_down(self):
        """Move mouse down (or start dragging down if card selected)"""
        if self.state == State.IDLE:
            print("No card selected, move_down does nothing")
            return
        
        if self.state == State.CARD_SELECTED:
            # Click down and start dragging
            self.mouse.mouse_down()
            self.mouse_pressed = True
            self.state = State.PLACING
            print("Mouse pressed down, entering PLACING state")
        
        # Move down relatively
        self.mouse.move(0, self.MOVE_STEP)
        time.sleep(0.1)
        self.relative_y += self.MOVE_STEP
        print(f"  - Moved to relative position ({self.relative_x}, {self.relative_y})")
        
    def move_left(self):
        """Move mouse left (or start dragging left if card selected)"""
        if self.state == State.IDLE:
            print("No card selected, move_left does nothing")
            return
        
        if self.state == State.CARD_SELECTED:
            # Click down and start dragging
            self.mouse.mouse_down()
            self.mouse_pressed = True
            self.state = State.PLACING
            print("Mouse pressed down, entering PLACING state")
        
        # Move left relatively
        self.mouse.move(-self.MOVE_STEP, 0)
        time.sleep(0.1)
        self.relative_x -= self.MOVE_STEP
        print(f"  - Moved to relative position ({self.relative_x}, {self.relative_y})")
        
    def move_right(self):
        """Move mouse right (or start dragging right if card selected)"""
        if self.state == State.IDLE:
            print("No card selected, move_right does nothing")
            return
        
        if self.state == State.CARD_SELECTED:
            # Click down and start dragging
            self.mouse.mouse_down()
            self.mouse_pressed = True
            self.state = State.PLACING
            print("Mouse pressed down, entering PLACING state")
        
        # Move right relatively
        self.mouse.move(self.MOVE_STEP, 0)
        time.sleep(0.1)
        self.relative_x += self.MOVE_STEP
        print(f"  - Moved to relative position ({self.relative_x}, {self.relative_y})")
