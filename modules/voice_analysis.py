import os
import warnings

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

import streamlit as st
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from io import BytesIO
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from datetime import datetime
import soundfile as sf
import pickle
from database.mongodb_handler import MongoDBHandler

# Load model, scaler and encoder at module level (cached)
@st.cache_resource
def load_emotion_model():
    """Load the trained CNN model, scaler, and encoder"""
    try:
        # Build model architecture (since JSON loading has compatibility issues with Keras 3)
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Conv1D, MaxPooling1D, Dropout, Flatten, Dense, BatchNormalization
        
        model = Sequential([
            Conv1D(512, kernel_size=5, strides=1, padding='same', activation='relu', input_shape=(2376, 1)),
            BatchNormalization(),
            MaxPooling1D(pool_size=5, strides=2, padding='same'),
            
            Conv1D(512, kernel_size=5, strides=1, padding='same', activation='relu'),
            BatchNormalization(),
            MaxPooling1D(pool_size=5, strides=2, padding='same'),
            Dropout(0.2),
            
            Conv1D(256, kernel_size=5, strides=1, padding='same', activation='relu'),
            BatchNormalization(),
            MaxPooling1D(pool_size=5, strides=2, padding='same'),
            
            Conv1D(256, kernel_size=3, strides=1, padding='same', activation='relu'),
            BatchNormalization(),
            MaxPooling1D(pool_size=5, strides=2, padding='same'),
            Dropout(0.2),
            
            Conv1D(128, kernel_size=3, strides=1, padding='same', activation='relu'),
            BatchNormalization(),
            MaxPooling1D(pool_size=3, strides=2, padding='same'),
            Dropout(0.2),
            
            Flatten(),
            Dense(512, activation='relu'),
            BatchNormalization(),
            Dense(7, activation='softmax')
        ])
        
        # Load model weights
        model.load_weights('Models/best_model1_weights.h5')
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
        # Load scaler
        with open('Models/scaler2.pickle', 'rb') as f:
            scaler = pickle.load(f)
        
        # Load encoder
        with open('Models/encoder2.pickle', 'rb') as f:
            encoder = pickle.load(f)
        
        return model, scaler, encoder
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None, None

# Audio feature extraction functions (from the notebook)
def zcr(data, frame_length=2048, hop_length=512):
    """Extract Zero Crossing Rate"""
    zcr = librosa.feature.zero_crossing_rate(data, frame_length=frame_length, hop_length=hop_length)
    return np.squeeze(zcr)

def rmse(data, frame_length=2048, hop_length=512):
    """Extract Root Mean Square Energy"""
    rmse = librosa.feature.rms(y=data, frame_length=frame_length, hop_length=hop_length)
    return np.squeeze(rmse)

def mfcc(data, sr, frame_length=2048, hop_length=512, flatten: bool = True):
    """Extract MFCC features"""
    mfcc_feat = librosa.feature.mfcc(y=data, sr=sr, n_mfcc=20)
    return np.squeeze(mfcc_feat.T) if not flatten else np.ravel(mfcc_feat.T)

def extract_features(data, sr=22050, frame_length=2048, hop_length=512):
    """Extract all audio features for model input"""
    result = np.array([])
    
    result = np.hstack((result,
                        zcr(data, frame_length, hop_length),
                        rmse(data, frame_length, hop_length),
                        mfcc(data, sr, frame_length, hop_length)
                       ))
    return result

def get_predict_feat(audio_data, sr, scaler):
    """Get features for prediction from audio data"""
    try:
        # Extract features from the audio
        res = extract_features(audio_data, sr)
        result = np.array(res)
        
        # Check if we have the right number of features
        if result.shape[0] != 2376:
            # Pad or truncate to 2376
            if result.shape[0] < 2376:
                # Pad with zeros
                result = np.pad(result, (0, 2376 - result.shape[0]), mode='constant')
            else:
                # Truncate
                result = result[:2376]
        
        result = np.reshape(result, newshape=(1, 2376))
        
        # Scale the features
        i_result = scaler.transform(result)
        
        # Expand dimensions for CNN input
        final_result = np.expand_dims(i_result, axis=2)
        
        return final_result
    except Exception as e:
        raise Exception(f"Feature extraction error: {str(e)}")

def predict_emotion(audio_data, sr, model, scaler, encoder):
    """Predict emotion from audio using the trained CNN model"""
    try:
        # Get features
        features = get_predict_feat(audio_data, sr, scaler)
        
        # Make prediction
        predictions = model.predict(features, verbose=0)
        
        # Get emotion classes
        try:
            emotion_classes = encoder.categories_[0]
        except:
            # Fallback if categories_ doesn't work
            emotion_classes = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
        
        # Get predicted emotion (highest probability)
        predicted_idx = np.argmax(predictions[0])
        predicted_emotion = emotion_classes[predicted_idx]
        
        # Convert to string if it's a numpy scalar
        if hasattr(predicted_emotion, 'item'):
            predicted_emotion = predicted_emotion.item()
        predicted_emotion = str(predicted_emotion)
        
        # Get confidence scores for all emotions
        emotion_scores = {}
        for i, emotion in enumerate(emotion_classes):
            # Ensure emotion is a string
            emotion_str = str(emotion.item()) if hasattr(emotion, 'item') else str(emotion)
            emotion_scores[emotion_str.capitalize()] = float(predictions[0][i] * 100)
        
        return predicted_emotion.capitalize(), emotion_scores
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Unknown", {}

def calculate_wellness_score(emotion_scores, dominant_emotion):
    """Calculate wellness score based on emotion predictions"""
    # Positive emotions contribute positively
    positive_emotions = ['happy', 'calm', 'neutral', 'surprise']
    negative_emotions = ['sad', 'angry', 'fear', 'disgust']
    
    positive_score = sum(emotion_scores.get(e.capitalize(), 0) for e in positive_emotions)
    negative_score = sum(emotion_scores.get(e.capitalize(), 0) for e in negative_emotions)
    
    # Calculate wellness (0-100 scale)
    wellness = (positive_score / (positive_score + negative_score)) * 100 if (positive_score + negative_score) > 0 else 50
    
    return round(wellness, 1)

def calculate_risk_score(emotion_scores, dominant_emotion):
    """Calculate mental health risk score"""
    # High-risk emotions
    risk_emotions = {
        'sad': 1.5,
        'fear': 1.3,
        'disgust': 1.1,
        'angry': 1.2
    }
    
    risk = 0
    for emotion, weight in risk_emotions.items():
        risk += emotion_scores.get(emotion.capitalize(), 0) * weight
    
    # Normalize to 0-100
    risk_score = min(100, max(0, risk))
    
    return round(risk_score, 1)

def voice_analysis_page(db_handler: MongoDBHandler = None):
    st.markdown("#  Voice & Speech Analysis")
    st.markdown("### Analyze vocal patterns and speech emotions")
    st.markdown("---")
    
    # Get user ID from session
    user_id = st.session_state.get('user_id')
    
    # Input Methods
    tab1, tab2 = st.tabs([" Record Audio", " Upload Audio File"])
    
    with tab1:
        st.markdown("#### Record your voice directly")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("""
             **Tips for best results:**
            - Speak naturally and clearly
            - Share your thoughts or feelings
            - Ensure minimal background noise
            - Allow browser microphone permissions
            - Recording will be at least 3 seconds
            """)
            
            # Streamlit audio input for recording
            st.markdown("##### Click below to start recording:")
            recorded_audio = st.audio_input("Record your voice", label_visibility="collapsed")
            
            if recorded_audio is not None:
                st.success(" Recording captured successfully!")
                
                # Display the recorded audio
                st.audio(recorded_audio)
                
                # Analysis options for recorded audio
                st.markdown("---")
                st.markdown("#### Analysis Options")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    extract_mfcc_rec = st.checkbox("Extract MFCC Features", value=True, key="mfcc_rec")
                
                with col_b:
                    show_spectrogram_rec = st.checkbox("Show Spectrogram", value=True, key="spec_rec")
                
                # Analyze button
                if st.button("Analyze Recording", width="stretch", type="primary", key="analyze_rec"):
                    with st.spinner(" Analyzing your voice..."):
                        # Process the recorded audio
                        analyze_audio(recorded_audio, duration=10, offset=0, 
                                    extract_mfcc_flag=extract_mfcc_rec, 
                                    show_spec=show_spectrogram_rec, 
                                    db_handler=db_handler)
        
        with col2:
            st.markdown("""
            <div class="custom-card">
                <h4> Recording Info</h4>
                <p><strong>Format:</strong> WAV</p>
                <p><strong>Sample Rate:</strong> 24 kHz</p>
                <p><strong>Status:</strong> Ready to record</p>
                <p style="margin-top: 15px; color: #666; font-size: 12px;">
                    Click the microphone button to start recording. 
                    The recording will stop automatically or when you click stop.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("####  Upload an audio file for analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_audio = st.file_uploader(
                "Choose an audio file",
                type=['wav', 'mp3', 'ogg', 'm4a', 'flac'],
                help="Upload an audio recording (WAV, MP3, OGG, M4A, or FLAC)"
            )
            
            if uploaded_audio is not None:
                st.success(f" File uploaded: {uploaded_audio.name}")
                
                # Display audio player
                st.audio(uploaded_audio, format=f'audio/{uploaded_audio.type.split("/")[-1]}')
                
                # Analysis options
                st.markdown("#### Analysis Configuration")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    duration = st.slider("Analysis Duration (seconds)", 3, 30, 10, key="duration_upload")
                    offset = st.slider("Start Offset (seconds)", 0, 10, 0, key="offset_upload")
                
                with col_b:
                    extract_mfcc = st.checkbox("Extract MFCC Features", value=True, key="mfcc_upload")
                    show_spectrogram = st.checkbox("Show Spectrogram", value=True, key="spec_upload")
                
                if st.button(" Analyze Audio", width="stretch", type="primary", key="analyze_upload"):
                    with st.spinner("Processing audio file..."):
                        # Get db_handler from the parent scope
                        analyze_audio(uploaded_audio, duration, offset, extract_mfcc, show_spectrogram, db_handler)
        
        with col2:
            st.markdown("""
            <div class="custom-card">
                <h4> Supported Formats</h4>
                <ul style="color: #666; line-height: 1.8;">
                    <li>WAV</li>
                    <li>MP3</li>
                    <li>OGG</li>
                    <li>M4A</li>
                    <li>FLAC</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="custom-card" style="margin-top: 20px;">
                <h4> Best Practices</h4>
                <ul style="color: #666; font-size: 12px; line-height: 1.6;">
                    <li>Clear audio quality</li>
                    <li>Minimal background noise</li>
                    <li>10-30 seconds length</li>
                    <li>Natural speech</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

def analyze_audio(audio_file, duration=10, offset=0, extract_mfcc_flag=True, show_spec=True, db_handler=None):
    """Comprehensive audio analysis using trained CNN model"""
    
    try:
        # Load the model, scaler, and encoder
        model, scaler, encoder = load_emotion_model()
        
        if model is None or scaler is None or encoder is None:
            st.error(" Failed to load emotion recognition model. Please check model files.")
            return
        
        # Load audio file (use 2.5 seconds with 0.6 offset as per notebook)
        audio_bytes = audio_file.read()
        y, sr = librosa.load(BytesIO(audio_bytes), duration=2.5, offset=0.6)
        
        st.markdown("---")
        st.markdown("##  Voice Analysis Results")
        
        # Get user ID from session
        user_id = st.session_state.get('user_id')
        
        # Use trained model for emotion prediction
        dominant_emotion, emotion_scores = predict_emotion(y, sr, model, scaler, encoder)
        
        # Calculate wellness and risk scores
        wellness_score = calculate_wellness_score(emotion_scores, dominant_emotion)
        risk_score = calculate_risk_score(emotion_scores, dominant_emotion)
        
        # Calculate additional audio features for visualization
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(tempo) if hasattr(tempo, 'item') else float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
        
        # Display main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        emotion_emoji = {
            'Happy': '😊',
            'Sad': '😢',
            'Angry': '😠',
            'Neutral': '😐',
            'Fear': '😨',
            'Fearful': '😨',
            'Calm': '😌',
            'Disgust': '🤢',
            'Surprise': '😮'
        }
        
        with col1:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <h1 style="font-size: 3rem; margin: 0;">{emotion_emoji.get(dominant_emotion, '🎭')}</h1>
                <hr style="margin: 15px 0; border: 0; border-top: 1px solid #e0e0e0;">
                <h4 style="color: #ff69b4; margin: 10px 0;">{dominant_emotion}</h4>
                <p style="color: #666; margin: 5px 0;">Detected Emotion</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <h2 style="color: #4ecdc4; margin: 10px 0; font-size: 2.5rem;">{wellness_score:.1f}/100</h2>
                <hr style="margin: 15px 0; border: 0; border-top: 1px solid #e0e0e0;">
                <p style="color: #666; margin: 5px 0;">Wellness Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            energy = np.mean(librosa.feature.rms(y=y))
            confidence = max(emotion_scores.values())
            st.markdown(f"""
            <div class="custom-card" style="text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <h2 style="color: #ff85c0; margin: 10px 0; font-size: 2.5rem;">{confidence:.1f}%</h2>
                <hr style="margin: 15px 0; border: 0; border-top: 1px solid #e0e0e0;">
                <p style="color: #666; margin: 5px 0;">Confidence</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            risk_level = "Low" if risk_score < 40 else "Moderate" if risk_score < 70 else "High"
            risk_class = "risk-low" if risk_score < 40 else "risk-moderate" if risk_score < 70 else "risk-high"
            
            st.markdown(f"""
            <div class="custom-card" style="text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
                <h2 style="color: #ff99cc; margin: 10px 0; font-size: 2.5rem;">{risk_score:.1f}/100</h2>
                <hr style="margin: 15px 0; border: 0; border-top: 1px solid #e0e0e0;">
                <div class="{risk_class} risk-badge" style="margin: 10px auto;">{risk_level} Risk</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Detailed Analysis
        tab1, tab2 = st.tabs([" Emotions", "Audio Features"])
        
        with tab1:
            st.markdown("### Emotion Detection Results")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Emotion scores chart
                fig = go.Figure(data=[go.Bar(
                    x=list(emotion_scores.values()),
                    y=list(emotion_scores.keys()),
                    orientation='h',
                    marker=dict(
                        color=['#ff69b4', '#ff85c0', '#ff99cc', '#ffb6c1', '#ffc0cb', '#ffe4e9'],
                        line=dict(color='white', width=2)
                    ),
                    text=[f'{v:.1f}%' for v in emotion_scores.values()],
                    textposition='auto'
                )])
                
                fig.update_layout(
                    title='Emotion Confidence Scores',
                    xaxis_title='Confidence (%)',
                    height=350,
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                st.markdown("#### Top 3 Emotions")
                sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
                
                for i, (emotion, score) in enumerate(sorted_emotions[:3], 1):
                    st.markdown(f"""
                    <div class="custom-card">
                        <strong>#{i} {emotion}</strong><br>
                        <span style="color: #ff69b4; font-size: 1.2rem; font-weight: 600;">{score:.1f}%</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### Audio Feature Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="custom-card">
                    <h4> Pitch Characteristics</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.metric("Avg Spectral Centroid", f"{np.mean(spectral_centroids):.0f} Hz")
                st.metric("Spectral Rolloff", f"{np.mean(spectral_rolloff):.0f} Hz")
            
            with col2:
                st.markdown("""
                <div class="custom-card">
                    <h4> Energy & Dynamics</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.metric("RMS Energy", f"{np.mean(librosa.feature.rms(y=y)):.3f}")
                st.metric("Zero Crossing Rate", f"{np.mean(zero_crossing_rate):.3f}")
            
            with col3:
                st.markdown("""
                <div class="custom-card">
                    <h4> Temporal Features</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.metric("Tempo", f"{tempo:.1f} BPM")
                st.metric("Duration", f"{len(y)/sr:.2f} sec")
            
            # Feature timeline
            st.markdown("#### Feature Evolution Over Time")
            
            time_frames = np.linspace(0, len(y)/sr, len(spectral_centroids))
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=time_frames,
                y=spectral_centroids,
                name='Spectral Centroid',
                line=dict(color='#ff69b4', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=time_frames,
                y=zero_crossing_rate * 1000,  # Scale for visibility
                name='Zero Crossing Rate (scaled)',
                line=dict(color='#ff85c0', width=2)
            ))
            
            fig.update_layout(
                title='Audio Features Over Time',
                xaxis_title='Time (seconds)',
                yaxis_title='Value',
                height=350,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, width="stretch")
        
        # Save to MongoDB if db_handler is available
        if db_handler and user_id:
            try:
                # Prepare emotions dictionary
                emotions_dict = {emotion.lower(): float(score) for emotion, score in emotion_scores.items()}
                
                # Save analysis to database
                db_handler.save_analysis(
                    user_id=user_id,
                    analysis_type='voice',
                    text_content=f"Audio analysis - Duration: {len(y)/sr:.2f}s",
                    emotions=emotions_dict,
                    wellness_score=wellness_score,
                    risk_score=risk_score,
                    dominant_emotion=dominant_emotion.lower()
                )
                # Silent save - no notification
            except Exception as e:
                # Silent error - just log
                print(f"Could not save to database: {str(e)}")
        
        # Save to session history
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        
        st.session_state.analysis_history.append({
            'timestamp': datetime.now(),
            'type': 'Voice',
            'emotion': dominant_emotion,
            'wellness_score': wellness_score,
            'risk_score': risk_score
        })
        
    except Exception as e:
        # Silent error handling - log to console only
        import traceback
        print(f"Error analyzing audio: {str(e)}")
        traceback.print_exc()
        
        

def plot_waveform(y, sr):
    """Plot audio waveform"""
    fig, ax = plt.subplots(figsize=(12, 3))
    librosa.display.waveshow(y, sr=sr, ax=ax, color='#ff69b4')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Audio Waveform', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig

def plot_spectrogram(y, sr):
    """Plot spectrogram"""
    fig, ax = plt.subplots(figsize=(12, 4))
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    img = librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', ax=ax, cmap='RdPu')
    ax.set_title('Spectrogram', fontsize=14, fontweight='bold')
    plt.colorbar(img, ax=ax, format='%+2.0f dB')
    plt.tight_layout()
    return fig

def generate_voice_insights(emotions, tempo, energy, risk_score):
    """Generate insights from voice analysis"""
    insights = []
    
    dominant_emotion = max(emotions, key=emotions.get)
    
    if emotions.get('Sad', 0) > 60:
        insights.append({
            'title': ' Sadness Detected in Voice',
            'content': 'Your vocal patterns show signs of sadness or low mood. Consider talking to someone about how you\'re feeling.'
        })
    
    if tempo < 90:
        insights.append({
            'title': ' Slower Speech Rate',
            'content': 'Slower speech can sometimes indicate fatigue or low energy. Ensure you\'re getting adequate rest.'
        })
    elif tempo > 140:
        insights.append({
            'title': ' Rapid Speech Detected',
            'content': 'Fast speech rate may indicate anxiety or stress. Try some calming breathing exercises.'
        })
    
    if risk_score > 70:
        insights.append({
            'title': ' Elevated Concern Level',
            'content': 'Voice analysis suggests heightened stress or emotional distress. We recommend consulting with a mental health professional.'
        })
    
    if emotions.get('Happy', 0) > 60:
        insights.append({
            'title': ' Positive Vocal Indicators',
            'content': 'Your voice reflects positive emotions. Continue engaging in activities that bring you joy!'
        })
    
    return insights
