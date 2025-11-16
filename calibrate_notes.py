"""
Note Frequency Calibration Tool
Use this to find the exact frequencies your recorder produces
"""

import numpy as np
import pyaudio
import time

SAMPLE_RATE = 44100  # Using same rate as your working code
CHUNK_SIZE = 1024  # Using same chunk size as your working code

def get_frequency(audio_data):
    """Analyze audio data and return dominant frequency"""
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    
    # Check volume
    volume = np.abs(audio_array).mean()
    if volume < 100:  # Lowered threshold from 500 to 100
        return None, volume
    
    # Apply FFT
    fft = np.fft.rfft(audio_array)
    fft_magnitude = np.abs(fft)
    
    # Find peak frequency
    peak_index = np.argmax(fft_magnitude)
    frequency = peak_index * SAMPLE_RATE / len(audio_array)
    
    return frequency, volume

def main():
    print("=" * 60)
    print("Note Frequency Calibration Tool")
    print("=" * 60)
    print("\nThis tool will help you find the exact frequencies")
    print("your recorder produces for each note.")
    print("\nInstructions:")
    print("1. Play each note clearly and steadily")
    print("2. The tool will show the detected frequency")
    print("3. Write down the frequency range for each note")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    print()
    
    audio = pyaudio.PyAudio()
    
    print("Using default audio input device...")
    
    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
    except Exception as e:
        print(f"ERROR: Could not open audio stream: {e}")
        print("\nTroubleshooting:")
        print("1. Check if your microphone is working")
        print("2. Try: pulseaudio --start")
        print("3. Check system audio settings")
        audio.terminate()
        return
    
    print("🎤 Microphone active - play your notes!\n")
    print("DEBUG: Listening for audio...")
    print("(If nothing appears, try speaking/tapping the mic to test)\n")
    
    freq_buffer = []
    last_print_time = 0
    last_debug_time = 0
    
    try:
        while True:
            audio_data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            frequency, volume = get_frequency(audio_data)
            
            current_time = time.time()
            
            # Debug: print volume every 2 seconds
            if current_time - last_debug_time > 2:
                print(f"DEBUG: Volume level: {volume:5.0f} | Frequency: {frequency if frequency else 'None'}")
                last_debug_time = current_time
            
            if frequency and 200 < frequency < 700:
                freq_buffer.append(frequency)
                
                # Print average every 0.5 seconds
                if current_time - last_print_time > 0.5 and len(freq_buffer) > 0:
                    avg_freq = np.mean(freq_buffer)
                    min_freq = np.min(freq_buffer)
                    max_freq = np.max(freq_buffer)
                    
                    print(f"🎵 Frequency: {avg_freq:6.1f} Hz  "
                          f"(Range: {min_freq:6.1f} - {max_freq:6.1f} Hz)  "
                          f"Volume: {volume:5.0f}")
                    
                    freq_buffer = []
                    last_print_time = current_time
    
    except KeyboardInterrupt:
        print("\n\nStopping...")
    
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("Done!")

if __name__ == "__main__":
    main()
