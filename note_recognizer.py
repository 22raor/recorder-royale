"""
Note Recognition System for Clash Royale Controller
Recognizes recorder notes from microphone input and triggers actions
"""

import numpy as np
import pyaudio
import threading
import time
from collections import deque


class NoteRecognizer:
    def __init__(self, callback):
        """
        Initialize note recognizer
        
        Args:
            callback: Function to call when a note is detected. 
                     Will be called with note name (e.g., 'C', 'D', 'E', etc.)
        """
        self.callback = callback
        
        # Audio settings
        self.SAMPLE_RATE = 44100  # Changed to match working calibration
        self.CHUNK_SIZE = 4096
        self.FORMAT = pyaudio.paInt16
        
        # Note definitions (frequency ranges in Hz for recorder notes)
        # Calibrated based on your actual recorder
        self.NOTE_RANGES = {
            'C': (500, 790),  # ~1033 Hz - Cycle through cards (1→2→3→4)
            'D': (900, 1000),   # ~990 Hz - Up
            'E': (1001, 1200),  # ~1162 Hz - Down
            'F': (1210, 1300),  # ~1119 Hz - Left
            'G': (1310, 3000),  # ~1205 Hz - Right
            'A': (800, 881),    # ~861 Hz - Place
        }
        
        # State tracking for debouncing
        self.current_note = None
        self.last_note_time = 0
        self.note_start_time = 0
        self.MIN_NOTE_DURATION = 0.05   # Minimum 50ms to register a note
        self.SILENCE_THRESHOLD = 0.1    # 100ms of continuous silence to end a note
        self.DROPOUT_TOLERANCE = 0.05   # Allow 50ms dropouts without ending the note
        self.last_detection_time = 0
        self.last_dropout_time = 0
        
        # Rolling buffer for frequency detection stability
        self.freq_buffer = deque(maxlen=5)  # Last 5 frequency readings for better smoothing
        
        # PyAudio setup
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        
        print("Note recognizer initialized")
        print("Note mappings:")
        for note, freq_range in self.NOTE_RANGES.items():
            print(f"  {note}: {freq_range[0]}-{freq_range[1]} Hz")
    
    def get_frequency(self, audio_data):
        """
        Analyze audio data and return dominant frequency using FFT
        """
        # Convert to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Check if signal is loud enough
        volume = np.abs(audio_array).mean()
        if volume < 200:  # Lower threshold from 300 to 200 for better detection
            return None
        
        # Apply FFT
        fft = np.fft.rfft(audio_array)
        fft_magnitude = np.abs(fft)
        
        # Find peak frequency
        peak_index = np.argmax(fft_magnitude)
        frequency = peak_index * self.SAMPLE_RATE / len(audio_array)
        
        # Ignore very low frequencies (noise) and frequencies outside recorder range
        if frequency < 500 or frequency > 3000:
            return None
        
        return frequency
    
    def frequency_to_note(self, frequency):
        """
        Convert frequency to note name based on defined ranges
        """
        if frequency is None:
            return None
        
        for note, (low, high) in self.NOTE_RANGES.items():
            if low <= frequency <= high:
                return note
        
        return None
    
    def process_audio(self):
        """
        Main audio processing loop - runs in background thread
        """
        print("Using default audio input device...")
        
        try:
            # Use default device without specifying index (same as calibrate_notes.py)
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=1,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE
            )
        except Exception as e:
            print(f"ERROR: Could not open audio stream: {e}")
            print("Note recognition disabled. Keyboard controls still work.")
            self.running = False
            return
        
        print("🎤 Microphone active - play notes on your recorder!")
        
        while self.running:
            try:
                # Read audio data
                audio_data = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                
                # Get frequency
                frequency = self.get_frequency(audio_data)
                # print(frequency)
                
                # Add to buffer for stability
                self.freq_buffer.append(frequency)
                
                # Get most common frequency from buffer (mode)
                if frequency is not None:
                    # Get stable frequency (majority vote)
                    non_none = [f for f in self.freq_buffer if f is not None]
                    if len(non_none) >= 2:
                        stable_frequency = np.median(non_none)
                    else:
                        stable_frequency = frequency
                else:
                    stable_frequency = None
                
                # Convert to note
                detected_note = self.frequency_to_note(stable_frequency)
                
                current_time = time.time()
                
                if detected_note:
                    self.last_detection_time = current_time
                    
                    if self.current_note is None:
                        # New note starting
                        self.current_note = detected_note
                        self.note_start_time = current_time
                        print(f"🎵 Note detected: {detected_note} ({stable_frequency:.1f} Hz)")
                    
                    elif detected_note != self.current_note:
                        # Different note - finish previous note and start new one
                        note_duration = current_time - self.note_start_time
                        if note_duration >= self.MIN_NOTE_DURATION:
                            print(f"✓ Note played: {self.current_note} (duration: {note_duration:.2f}s)")
                            self.callback(self.current_note)
                        
                        self.current_note = detected_note
                        self.note_start_time = current_time
                        print(f"🎵 Note detected: {detected_note} ({stable_frequency:.1f} Hz)")
                
                else:
                    # No note detected (silence or dropout)
                    if self.current_note is not None:
                        current_time = time.time()
                        silence_duration = current_time - self.last_detection_time
                        
                        # Only end note if silence is longer than dropout tolerance
                        if silence_duration >= self.DROPOUT_TOLERANCE:
                            # Check if this is real silence (beyond silence threshold)
                            if silence_duration >= self.SILENCE_THRESHOLD:
                                # Note finished
                                note_duration = self.last_detection_time - self.note_start_time
                                if note_duration >= self.MIN_NOTE_DURATION:
                                    print(f"✓ Note played: {self.current_note} (duration: {note_duration:.2f}s)")
                                    self.callback(self.current_note)
                                
                                self.current_note = None
                
            except Exception as e:
                print(f"Audio processing error: {e}")
                time.sleep(0.01)
    
    def start(self):
        """Start listening to microphone"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.process_audio, daemon=True)
            self.thread.start()
            print("Note recognition started")
    
    def stop(self):
        """Stop listening to microphone"""
        if self.running:
            self.running = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            print("Note recognition stopped")
    
    def __del__(self):
        """Cleanup"""
        self.stop()
        if hasattr(self, 'audio'):
            self.audio.terminate()


if __name__ == "__main__":
    """Test the note recognizer"""
    def on_note_detected(note):
        print(f">>> ACTION TRIGGERED: {note}")
    
    recognizer = NoteRecognizer(on_note_detected)
    
    try:
        recognizer.start()
        print("\nPlay notes on your recorder to test detection...")
        print("Press Ctrl+C to stop\n")
        
        # Keep running
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nStopping...")
        recognizer.stop()
