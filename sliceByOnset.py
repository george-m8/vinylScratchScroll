import os
import librosa
import numpy as np
from pydub import AudioSegment

def find_onsets(signal, sr):
    onset_frames = librosa.onset.onset_detect(y=signal, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    return onset_times

def split_audio(file_path, output_folder):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    y, sr = librosa.load(file_path, sr=None)
    onsets = find_onsets(y, sr)
    print(f"Found {len(onsets)} onsets")
    
    audio = AudioSegment.from_file(file_path)
    onsets_ms = [int(t * 1000) for t in onsets]
    
    start = 0
    for i, end in enumerate(onsets_ms):
        segment = audio[start:end]
        segment.export(os.path.join(output_folder, f"{base_name}_segment_{i}.wav"), format="wav")
        start = end

    segment = audio[start:]
    segment.export(os.path.join(output_folder, f"{base_name}_segment_{len(onsets_ms)}.wav"), format="wav")

def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        print(f"Creating output folder: {output_folder}")
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.wav'):
            print(f"Processing {file_name}")
            file_path = os.path.join(input_folder, file_name)
            split_audio(file_path, output_folder)

# Example usage
input_folder = './scratchFX_input'
output_folder = 'scratchFX_output'
process_folder(input_folder, output_folder)
