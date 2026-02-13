import pandas as pd
import os
import yt_dlp
import csv

# --- CONFIGURATION ---
TARGET_LABELS = [
     "Female speech", "Male speech"
]
DATA_DIR = "./audioset_data_neutral"
# AudioSet Metadata URLs
LABELS_URL = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv"
# We use the 'balanced_train' set for testing (smaller, faster). 
# Swap with 'unbalanced_train_segments.csv' for the massive full dataset.
SEGMENTS_URL = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/balanced_train_segments.csv" 

def ensure_metadata_exists():
    """Downloads AudioSet metadata CSVs if not present."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    labels_path = os.path.join(DATA_DIR, "class_labels_indices.csv")
    segments_path = os.path.join(DATA_DIR, "segments.csv")
    
    if not os.path.exists(labels_path):
        print(f"Downloading class labels from {LABELS_URL}...")
        pd.read_csv(LABELS_URL).to_csv(labels_path, index=False)
        
    if not os.path.exists(segments_path):
        print(f"Downloading segment metadata from {SEGMENTS_URL}...")
        # Skip header rows (quotechar issues often occur in raw AudioSet CSVs, simplified here)
        pd.read_csv(SEGMENTS_URL, header=2, quotechar='"', skipinitialspace=True).to_csv(segments_path, index=False)
        
    return labels_path, segments_path

def get_target_mids(labels_path, target_names):
    """Finds Machine IDs (MIDs) for the target labels."""
    df = pd.read_csv(labels_path)
    target_mids = []
    found_labels = []
    
    print("\nScanning for Label IDs...")
    for index, row in df.iterrows():
        display_name = row['display_name'].lower()
        # Check if any target label is in the display name
        if any(t.lower() in display_name for t in target_names):
            target_mids.append(row['mid'])
            found_labels.append(row['display_name'])
            print(f" -> Found match: '{row['display_name']}' (ID: {row['mid']})")
            
    return target_mids, found_labels

def download_clip(video_id, start_time, end_time, label_name, output_folder):
    """Downloads a specific range of audio using yt-dlp."""
    
    # Clean label name for filename
    safe_label = "".join([c if c.isalnum() else "_" for c in label_name])
    filename = f"{safe_label}_{video_id}_{int(start_time)}_{int(end_time)}"
    output_path = os.path.join(output_folder, filename)
    
    # yt-dlp configuration
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,  # No extension needed here, postprocessor adds it
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        # This downloads ONLY the specific range (saves bandwidth)
        'download_ranges': lambda info, ydl: [{'start_time': start_time, 'end_time': end_time}],
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        # print(f" [OK] Saved: {filename}.wav") # Optional verbose
        return True
    except Exception as e:
        # print(f" [ERR] Failed {video_id}: {e}") # Optional verbose
        return False

def main():
    labels_path, segments_path = ensure_metadata_exists()
    
    # 1. Get the IDs
    target_mids, found_names = get_target_mids(labels_path, TARGET_LABELS)
    if not target_mids:
        print("No matching labels found!")
        return

    # 2. Filter Segments
    print(f"\nFiltering segments for {len(found_names)} labels...")
    
    # Load segments manually to handle AudioSet's quirky formatting
    filtered_segments = []
    with open(segments_path, 'r') as f:
        reader = csv.reader(f, skipinitialspace=True)
        headers = next(reader) # Header
        
        for row in reader:
            try:
                # Row format: [videoId, startTime, endTime, labels_list]
                vid_id = row[0]
                start = float(row[1])
                end = float(row[2])
                labels = row[3] # String like "/m/09x0r,/m/05zppz"
                
                # Check if any of our target MIDs are in this row's label list
                if any(mid in labels for mid in target_mids):
                    # Find which readable label this corresponds to for folder organization
                    # (Just picking the first match for folder name)
                    matched_mid = next(mid for mid in target_mids if mid in labels)
                    # Look up display name for this MID
                    display_name = found_names[target_mids.index(matched_mid)]
                    
                    filtered_segments.append({
                        'id': vid_id, 'start': start, 'end': end, 'label': display_name
                    })
            except (IndexError, ValueError):
                continue

    print(f"Found {len(filtered_segments)} clips to download.")
    
    # 3. Download
    print("\nStarting Download...")
    success_count = 0
    
    for i, seg in enumerate(filtered_segments):
        # Create subfolder for specific class
        label_dir = os.path.join(DATA_DIR, "audio", seg['label'].replace(" ", "_"))
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)
            
        print(f"[{i+1}/{len(filtered_segments)}] Downloading {seg['label']} ({seg['id']})...", end="\r")
        
        if download_clip(seg['id'], seg['start'], seg['end'], seg['label'], label_dir):
            success_count += 1

    print(f"\n\nDone! Successfully downloaded {success_count} clips.")
    print(f"Files are located in: {os.path.abspath(os.path.join(DATA_DIR, 'audio'))}")

if __name__ == "__main__":
    main()