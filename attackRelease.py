import os
from pydub import AudioSegment

def apply_attack_release(segment, attack_ms=30, release_ms=40):
    segment = segment.fade_in(attack_ms).fade_out(release_ms)
    return segment

def process_file(file_path, output_folder):
    # Extract the base name of the file (without extension)
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    # Load the audio file
    audio = AudioSegment.from_file(file_path)

    # Apply attack and release
    processed_audio = apply_attack_release(audio)

    # Export the processed audio
    output_path = os.path.join(output_folder, f"{base_name}_processed.wav")
    processed_audio.export(output_path, format="wav")
    print(f"Processed file saved to: {output_path}")

def process_folder(input_folder, output_folder):
    if not os.path.exists(output_folder):
        print(f"Creating output folder: {output_folder}")
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.wav'):
            print(f"Processing {file_name}")
            file_path = os.path.join(input_folder, file_name)
            process_file(file_path, output_folder)

# Example usage
input_folder = './scratchFX_selectedCuts'
output_folder = './scratchFX_ARoutput'
process_folder(input_folder, output_folder)