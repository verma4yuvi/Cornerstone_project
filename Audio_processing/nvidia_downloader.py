import os
import shutil
from datasets import load_dataset
from huggingface_hub import snapshot_download
from tqdm import tqdm

# --- CONFIGURATION ---
REPO_ID = "nvidia/Nemotron-Content-Safety-Audio-Dataset"
RAW_DOWNLOAD_DIR = "./temp_raw_download"  # Where raw files go temporarily
OUTPUT_DIR = "./nemotron_4_classes"       # Your final sorted data

# Define mappings
LABEL_MAPPING = {
    "Violence": "violence", "Threat": "violence", "Guns": "violence", "Suicide": "violence",
    "Sexual": "sexual_content",
    "Hate": "hate_speech", "Harassment": "hate_speech", "Profanity": "hate_speech",
    "Safe": "safe"
}

def get_target_folder(violation_string, safe_label):
    if safe_label == 'safe' or not violation_string: return "safe"
    v_str = str(violation_string)
    if "Sexual" in v_str: return "sexual_content"
    if "Hate" in v_str or "Harassment" in v_str or "Profanity" in v_str: return "hate_speech"
    if "Violence" in v_str or "Threat" in v_str or "Guns" in v_str or "Suicide" in v_str: return "violence"
    return "other_unsafe"

def find_file_in_dir(root_dir, filename):
    """Recursively searches for a filename in a directory."""
    for dirpath, _, filenames in os.walk(root_dir):
        if filename in filenames:
            return os.path.join(dirpath, filename)
    return None

def main():
    # 1. DOWNLOAD RAW FILES (The Audio)
    print(f"1. Downloading raw repository to '{RAW_DOWNLOAD_DIR}'...")
    # This downloads the .wav files that load_dataset missed
    snapshot_path = snapshot_download(
        repo_id=REPO_ID, 
        repo_type="dataset", 
        local_dir=RAW_DOWNLOAD_DIR,
        allow_patterns=["*.wav", "*.mp3", "*.flac"], # Only get audio files
        resume_download=True
    )

    # 2. LOAD METADATA (The Labels)
    print(f"2. Loading metadata table...")
    try:
        # We use the metadata to tell us WHICH file belongs to WHICH category
        dataset = load_dataset(REPO_ID, split="test")
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return

    # 3. MATCH AND MOVE
    print(f"3. Sorting files into '{OUTPUT_DIR}'...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    stats = {k: 0 for k in set(LABEL_MAPPING.values())}
    stats["other_unsafe"] = 0
    missing_files = 0

    for row in tqdm(dataset):
        # Get the filename from metadata
        filename = row.get('audio_filename')
        if not filename: continue

        # Find the actual file in the downloaded folder
        src_path = find_file_in_dir(snapshot_path, filename)
        
        if src_path:
            # Determine target folder
            folder_name = get_target_folder(row.get('violated_categories'), row.get('prompt_label'))
            
            # Create destination
            target_folder = os.path.join(OUTPUT_DIR, folder_name)
            os.makedirs(target_folder, exist_ok=True)
            
            # Copy file
            dst_path = os.path.join(target_folder, filename)
            shutil.copy2(src_path, dst_path)
            
            stats[folder_name] += 1
        else:
            missing_files += 1

    print("\n" + "="*30)
    print("SORTING COMPLETE")
    print("="*30)
    for category, count in stats.items():
        print(f" - {category}: {count} files")
    print(f" - Missing/Not Found: {missing_files}")
    
    print(f"\nData is located in: {os.path.abspath(OUTPUT_DIR)}")
    print(f"(You can now delete the '{RAW_DOWNLOAD_DIR}' folder to save space)")

if __name__ == "__main__":
    main()