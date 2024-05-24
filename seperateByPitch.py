import os
import shutil
import librosa
import numpy as np
from pydub import AudioSegment
from sklearn.cluster import KMeans

def detect_pitch(file_path):
    y, sr = librosa.load(file_path, sr=None)
    if len(y) < 2048:
        n_fft = len(y) // 2  # Use smaller n_fft for short audio
    else:
        n_fft = 2048
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr, n_fft=n_fft)
    pitch_values = pitches[magnitudes > np.median(magnitudes)]
    if len(pitch_values) > 0:
        pitch = pitch_values.mean()
        return pitch if not np.isnan(pitch) else None
    else:
        return None

def analyze_pitches(input_folder):
    pitches = []
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.wav'):
            print(f"Analyzing pitch for {file_name}")
            file_path = os.path.join(input_folder, file_name)
            pitch = detect_pitch(file_path)
            if pitch is not None:
                pitches.append(pitch)
    return np.array(pitches)

def determine_cutoffs(pitches):
    pitches = pitches.reshape(-1, 1)
    kmeans = KMeans(n_clusters=3, random_state=0).fit(pitches)
    centers = sorted(kmeans.cluster_centers_.flatten())
    low_mid_cutoff = (centers[0] + centers[1]) / 2
    mid_high_cutoff = (centers[1] + centers[2]) / 2
    print(f"Low-mid cutoff: {low_mid_cutoff}")
    print(f"Mid-high cutoff: {mid_high_cutoff}")
    print(f"High pitch range: {mid_high_cutoff} and above")
    return low_mid_cutoff, mid_high_cutoff

def categorize_pitch(pitch, low_mid_cutoff, mid_high_cutoff):
    if pitch < low_mid_cutoff:
        return 'low'
    elif pitch < mid_high_cutoff:
        return 'mid'
    else:
        return 'high'

def process_file(file_path, output_folders, low_mid_cutoff, mid_high_cutoff):
    pitch = detect_pitch(file_path)
    if pitch is None:
        category = 'unclassified'
    else:
        category = categorize_pitch(pitch, low_mid_cutoff, mid_high_cutoff)
    
    base_name = os.path.basename(file_path)
    destination = os.path.join(output_folders[category], base_name)
    shutil.copy(file_path, destination)
    return category, destination

def clear_output_folders(output_folders):
    for folder in output_folders.values():
        if os.path.exists(folder):
            print(f"Clearing output folder: {folder}")
            shutil.rmtree(folder)
        os.makedirs(folder)

def process_folder(input_folder, output_folder_base):
    output_folders = {
        'low': os.path.join(output_folder_base, 'low'),
        'mid': os.path.join(output_folder_base, 'mid'),
        'high': os.path.join(output_folder_base, 'high'),
        'unclassified': os.path.join(output_folder_base, 'unclassified')
    }

    clear_output_folders(output_folders)

    for folder in output_folders.values():
        if not os.path.exists(folder):
            print(f"Creating output folder: {folder}")
            os.makedirs(folder)

    pitches = analyze_pitches(input_folder)
    if len(pitches) > 0:
        low_mid_cutoff, mid_high_cutoff = determine_cutoffs(pitches)
    else:
        low_mid_cutoff, mid_high_cutoff = 0, 0  # Default cutoffs if no valid pitches are found

    pitch_counts = {'low': 0, 'mid': 0, 'high': 0, 'unclassified': 0}
    categorized_files = {'low': [], 'mid': [], 'high': [], 'unclassified': []}


    for file_name in os.listdir(input_folder):
        if file_name.endswith('.wav'):
            file_path = os.path.join(input_folder, file_name)
            category, destination = process_file(file_path, output_folders, low_mid_cutoff, mid_high_cutoff)
            pitch_counts[category] += 1
            categorized_files[category].append(destination)

    return pitch_counts, categorized_files

def generate_js_file(categorized_files, output_file):
    with open(output_file, 'w') as f:
        f.write("const soundOptions = {\n")
        for category in ['high', 'mid', 'low']:
            if category in categorized_files:
                files = [os.path.relpath(file, os.path.dirname(output_file)) for file in categorized_files[category]]
                f.write(f"  {category}: {files},\n")
        f.write("};\n\n")
        f.write("export default soundOptions;\n")

# Example usage
input_folder = 'scratchFX_ARoutput'
output_folder_base = 'scratchFX_byPitch'
js_output_file = 'path_to_your_output_js_file.js'

pitch_counts, categorized_files = process_folder(input_folder, output_folder_base)
generate_js_file(categorized_files, js_output_file)

print("File distribution by pitch category:")
print(pitch_counts)
