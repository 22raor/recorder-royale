# Clash Royale Recorder Controller

Control Clash Royale on Android emulator (i'd recommend Waydroid!) using a recorder! Play musical notes to control card placement and movement. 

## Architecture

The system uses a **split architecture** to handle Linux permission requirements:

- **Control Server** (`control_server.py`) - Runs with sudo for keyboard/mouse control
- **Audio Client** (`audio_client.py`) - Runs without sudo for microphone access
- They communicate via local socket on port 9999

## Required Files

- `control_server.py` - Main control server (requires sudo)
- `audio_client.py` - Audio recognition client (no sudo)
- `virtual_mouse.py` - Virtual mouse device for Wayland
- `mouse_controller.py` - Card selection and movement logic
- `note_recognizer.py` - Audio frequency detection
- `calibrate_notes.py` - Tool to find your recorder's frequencies

## Installation

1. **Install dependencies**:
   ```bash
   # System packages
   sudo apt-get install portaudio19-dev python3-pyaudio
   
   # Python packages
   pip install numpy pyaudio evdev keyboard
   ```

2. **Setup uinput permissions** (one-time setup):
   ```bash
   echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' | sudo tee /etc/udev/rules.d/99-uinput.rules
   sudo usermod -aG input $USER
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```
   
   Then **log out and log back in** for permissions to take effect.

## Quick Start

### 1. Calibrate Your Recorder

Find the frequencies your recorder produces:

```bash
python3 calibrate_notes.py
```

Play each note and record the frequencies. Update `note_recognizer.py` with your values.

### 2. Start the Control Server

In terminal 1 (with sudo):
```bash
sudo python3 control_server.py
```

### 3. Start the Audio Client

In terminal 2 (without sudo):
```bash
python3 audio_client.py
```

### 4. Play!

Position your mouse at Card 1 in Clash Royale, then use either:

**Keyboard Controls:**
- `1, 2, 3, 4` - Select card
- `Arrow Keys` - Move/drag card
- `Space` - Place card
- `R` - Reset/cancel
- `ESC` - Exit

**Recorder Controls:**
- `C` - Cycle cards (1→2→3→4→1)
- `D` - Up
- `E` - Down
- `F` - Left
- `G` - Right
- `A` - Place

## Card Positions

Default calibrated positions (relative to Card 1):
- Card 1: (0, 0) - baseline
- Card 2: (+103, 0)
- Card 3: (+180, 0)
- Card 4: (+270, 0)

Adjust `CARD_OFFSETS` in `mouse_controller.py` if needed.

## Tuning

If note recognition needs adjustment, edit `note_recognizer.py`:

- `NOTE_RANGES` - Frequency ranges for each note
- `MIN_NOTE_DURATION` - Minimum note length (default: 50ms)
- `SILENCE_THRESHOLD` - Silence to end note (default: 100ms)
- `DROPOUT_TOLERANCE` - Tolerate brief dropouts (default: 50ms)
- Volume threshold in `get_frequency()` (default: 200)


