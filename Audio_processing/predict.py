import numpy as np
import librosa
import tensorflow as tf
import os

# --- CONFIGURATION (Must match training!) ---
MODEL_PATH = 'audio_moderation_model.h5'
SAMPLE_RATE = 22050
DURATION = 3  # Seconds
N_MELS = 128
INPUT_SHAPE = (N_MELS, 130) # The target shape for the spectrogram

def preprocess_single_file(file_path):
    """
    Loads and preprocesses a single audio file to match the model's expected input.
    """
    try:
        # 1. Load Audio
        audio, _ = librosa.load(file_path, sr=SAMPLE_RATE, duration=DURATION)
        
        # 2. Pad or Truncate to exact length
        target_len = SAMPLE_RATE * DURATION
        if len(audio) < target_len:
            audio = np.pad(audio, (0, target_len - len(audio)))
        else:
            audio = audio[:target_len]
            
        # 3. Create Mel Spectrogram
        mel_spec = librosa.feature.melspectrogram(y=audio, sr=SAMPLE_RATE, n_mels=N_MELS)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # 4. Add Channel Dimension (Shape becomes: 128, 130, 1)
        mel_spec_db = mel_spec_db[..., np.newaxis]
        
        # 5. Resize to ensure exact dimensions (fixing any frame count off-by-one errors)
        # We perform this using TensorFlow to exactly match the training logic
        mel_spec_db = tf.image.resize(mel_spec_db, (INPUT_SHAPE[0], INPUT_SHAPE[1])).numpy()

        # 6. Add Batch Dimension (Model expects a list of items, so we make a list of 1)
        # Shape becomes: (1, 128, 130, 1)
        return np.expand_dims(mel_spec_db, axis=0)

    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

def predict_audio(file_path):
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file '{MODEL_PATH}' not found. Train the model first!")
        return

    # Load the trained model
    print(f"Loading model from {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH)
    
    # Preprocess the input audio
    input_data = preprocess_single_file(file_path)
    
    if input_data is None:
        return

    # Make Prediction
    prediction_score = model.predict(input_data)[0][0]
    
    # Interpret Result (Threshold is usually 0.5)
    if prediction_score > 0.5:
        label = "UNSAFE 🔴"
        confidence = prediction_score * 100
    else:
        label = "SAFE 🟢"
        confidence = (1 - prediction_score) * 100
        
    print("-" * 30)
    print(f"File:       {os.path.basename(file_path)}")
    print(f"Prediction: {label}")
    print(f"Confidence: {confidence:.2f}%")
    print(f"Raw Score:  {prediction_score:.4f} (0=Safe, 1=Unsafe)")
    print("-" * 30)

# --- EXAMPLE USAGE ---
# Replace this with the path to the file you want to test
test_file = "dataset/car_crash/audio_001.wav" 

if __name__ == "__main__":
    # You can change the filename above or input it manually here
    test_file = "testfile.wav"
    predict_audio(test_file)