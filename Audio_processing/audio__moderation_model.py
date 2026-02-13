import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout

DATASET_PATH = "dataset"
SAMPLE_RATE = 22050
DURATION = 6  # Clip audio to 6 seconds (or pad if shorter)
N_MELS = 128
INPUT_SHAPE = (N_MELS, 130, 1) # 130 is approx frames for 6s @ 22050Hz with default hop_length

# Define your specific mappings
UNSAFE_CLASSES = ['Shout', 'scream', 'Chainsaw', 'Bellow', 'Battle_cry', 'gun_shot', 'angry','scream', 'car_crash', 'jambret', 'maling', 'rampok']
SAFE_CLASSES = ['rain', 'thunderstorm', 'wind', 'road_traffic', 'engine_idling', 'conversation']

def extract_features(file_path):
    """Loads audio and converts to Mel Spectrogram."""
    try:
        # Load audio (automatically resamples to 22050Hz)
        audio, _ = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)
        
        # Pad audio if it's shorter than DURATION
        target_len = SAMPLE_RATE * DURATION
        if len(audio) < target_len:
            audio = np.pad(audio, (0, target_len - len(audio)))
        else:
            audio = audio[:target_len]
            
        # Compute Mel Spectrogram
        mel_spec = librosa.feature.melspectrogram(y=audio, sr=SAMPLE_RATE, n_mels=N_MELS)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Add channel dimension for CNN (1 channel like grayscale image)
        return mel_spec_db[..., np.newaxis]
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def load_dataset(dataset_path):
    features = []
    labels = []
    
    print("Loading data...")
    for folder in os.listdir(dataset_path):
        folder_path = os.path.join(dataset_path, folder)
        if os.path.isdir(folder_path):
            # Determine label based on folder name
            if folder in UNSAFE_CLASSES:
                label = 1 
            elif folder in SAFE_CLASSES:
                label = 0 
            else:
                continue 
            
            # Process files in the folder
            for filename in os.listdir(folder_path):
                if filename.endswith(('.wav', '.mp3')):
                    file_path = os.path.join(folder_path, filename)
                    data = extract_features(file_path)
                    if data is not None:
                        # Ensure consistent shape (handling minor frame diffs)
                        if data.shape[1] != INPUT_SHAPE[1]:
                             data = tf.image.resize(data, (INPUT_SHAPE[0], INPUT_SHAPE[1])).numpy()
                        features.append(data)
                        labels.append(label)
    
    return np.array(features), np.array(labels)

# 1. Load Data
X, y = load_dataset(DATASET_PATH)
print(f"Dataset loaded. Shape: {X.shape}")

# 2. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Build Model (CNN)
model = Sequential([
    # First Convolutional Block
    Conv2D(32, (3, 3), activation='relu', input_shape=INPUT_SHAPE),
    MaxPooling2D((2, 2)),
    
    # Second Convolutional Block
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    
    # Flatten and Dense Layers
    Flatten(),
    Dense(64, activation='relu'),
    Dropout(0.5), # Prevents overfitting
    Dense(1, activation='sigmoid') # Output: 0 (Safe) to 1 (Unsafe)
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 4. Train
print("Starting training...")
history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))

# 5. Test with a dummy prediction
print("\nEvaluation complete. Saving model...")
model.save('audio_moderation_model.h5')
print("Model saved as audio_moderation_model.h5")