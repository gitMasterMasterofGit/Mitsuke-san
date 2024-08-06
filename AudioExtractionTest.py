import os
import wave
import time
import numpy as np
import sounddevice as sd
import wave

devices = sd.query_devices()
for i, device in enumerate(devices):
        print(f"Device {i}: {device['name']}")
        print(f"  Max input channels: {device['max_input_channels']}")
        print(f"  Max output channels: {device['max_output_channels']}")

# Audio stream parameters
chunk = 1024
sample_rate = 44100  # Replace with the appropriate sample rate
channels = 2
chunk_duration = chunk / sample_rate  # Duration of each chunk in seconds
max_duration = 60  # Maximum duration of a single file in seconds

def create_wave_file(filename):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(2)  # 16-bit audio
    wf.setframerate(sample_rate)
    return wf

# Setup for recording
chunk_size = int(sample_rate * chunk_duration)  # Number of samples per chunk
max_chunks_per_file = int(max_duration / chunk_duration)  # Number of chunks per file
file_index = 0

save_directory = "AudioFiles"

# Start recording
recording_start_time = time.time()
try:
    # Open an initial WAV file
    wave_filename = os.path.join(save_directory, f'output_{file_index}.wav')
    wave_file = create_wave_file(wave_filename)
    print(f"Recording to file output_{file_index}.wav")

    # Start the audio stream
    with sd.InputStream(samplerate=sample_rate, device=12, channels=channels, dtype='int16') as stream:
        while True:
            # Read audio data from the stream
            audio_chunk = stream.read(chunk_size)[0]

            # Write the chunk to the current file
            wave_file.writeframes(audio_chunk.tobytes())
            
            # Check if we need to rotate the file
            if int(time.time() - recording_start_time) >= (max_duration * (file_index + 1)):
                # Close the current file
                wave_file.close()
                
                # Move to the next file
                file_index += 1
                wave_filename = os.path.join(save_directory, f'output_{file_index}.wav')
                wave_file = create_wave_file(wave_filename)
                print(f"Recording to file output_{file_index}.wav")
                
                # Update start time for the new file
                recording_start_time = time.time()

except KeyboardInterrupt:
    print("Recording stopped by user")

finally:
    # Close the last file
    wave_file.close()
    print(f"Audio saved to output_{file_index}.wav")