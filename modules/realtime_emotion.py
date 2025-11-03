import os
import warnings

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

import streamlit as st
import numpy as np
import cv2
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from database.mongodb_handler import MongoDBHandler
import time

# Load emotion detection model
@st.cache_resource
def load_emotion_detection_model():
    """Load the pre-trained emotion detection CNN model"""
    try:
        # Create the model architecture
        model = Sequential()
        
        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 1)))
        model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        
        model.add(Flatten())
        model.add(Dense(1024, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(7, activation='softmax'))
        
        # Load weights
        model.load_weights('Models/emotion_model.h5')
        
        # Load Haar Cascade for face detection
        face_cascade = cv2.CascadeClassifier('Models/efficient-v2.xml')
        
        return model, face_cascade
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

def calculate_wellness_score(emotion_counts, total_frames):
    """Calculate wellness score based on detected emotions (0-10 scale)"""
    if total_frames == 0:
        return 5.0
    
    # Positive emotions contribute positively
    positive_emotions = ['Happy', 'Neutral', 'Surprised']
    negative_emotions = ['Sad', 'Angry', 'Fearful', 'Disgusted']
    
    positive_score = sum(emotion_counts.get(e, 0) for e in positive_emotions)
    negative_score = sum(emotion_counts.get(e, 0) for e in negative_emotions)
    
    # Calculate wellness on 0-10 scale
    if (positive_score + negative_score) > 0:
        wellness = (positive_score / (positive_score + negative_score)) * 10
    else:
        wellness = 5.0
    
    return round(wellness, 1)

def calculate_risk_score(emotion_counts, total_frames):
    """Calculate mental health risk score (0-10 scale)"""
    if total_frames == 0:
        return 0.0
    
    # Risk weights for concerning emotions
    risk_weights = {
        'Sad': 0.45,
        'Fearful': 0.40,
        'Angry': 0.30,
        'Disgusted': 0.20
    }
    
    risk = 0
    for emotion, weight in risk_weights.items():
        emotion_percentage = (emotion_counts.get(emotion, 0) / total_frames) * 100
        if emotion_percentage > 20:
            risk += (emotion_percentage / 100) * weight
    
    # Bonus risk if multiple negative emotions are present
    negative_count = sum(1 for e in ['Sad', 'Fearful', 'Angry', 'Disgusted'] 
                        if (emotion_counts.get(e, 0) / total_frames * 100) > 20)
    if negative_count >= 2:
        risk += 0.5
    
    risk_score = min(10.0, risk * 10)
    return round(risk_score, 1)

def realtime_emotion_page(db_handler: MongoDBHandler = None):
    st.markdown("#  Real-Time Emotion Detection")
    st.markdown("### Live facial emotion analysis using your webcam")
    st.markdown("---")
    
    # Get user ID from session
    user_id = st.session_state.get('user_id')
    
    # Load model
    model, face_cascade = load_emotion_detection_model()
    
    if model is None or face_cascade is None:
        st.error(" Failed to load emotion detection model. Please ensure model files are in the Models folder:")
        st.info("""
        Required files:
        - `Models/emotion_model.h5`
        - `Models/efficient-v2.xml`
        """)
        return
    
    # Emotion dictionary
    emotion_dict = {
        0: "Angry", 
        1: "Disgusted", 
        2: "Fearful", 
        3: "Happy", 
        4: "Neutral", 
        5: "Sad", 
        6: "Surprised"
    }
    
    emotion_emoji = {
        'Angry': '😠',
        'Disgusted': '🤢',
        'Fearful': '😨',
        'Happy': '😊',
        'Neutral': '😐',
        'Sad': '😢',
        'Surprised': '😲'
    }
    
    # Instructions
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
         **Instructions:**
        - Click "Start Webcam" to begin emotion detection
        - Your webcam will activate and detect emotions in real-time
        - The system will track your emotions over the session
        - Click "Stop & Analyze" to end the session and view detailed results
        - All data is processed locally for your privacy
        """)
    
    with col2:
        st.markdown("""
        <div class="custom-card">
            <h4> Detectable Emotions</h4>
            <ul style="font-size: 13px; line-height: 2;">
                <li>😊 Happy</li>
                <li>😢 Sad</li>
                <li>😠 Angry</li>
                <li>😲 Surprised</li>
                <li>😨 Fearful</li>
                <li>🤢 Disgusted</li>
                <li>😐 Neutral</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Session controls
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        start_btn = st.button(" Start Webcam", type="primary", use_container_width=True)
    
    with col_btn2:
        stop_btn = st.button(" Stop & Analyze", type="secondary", use_container_width=True)
    
    # Initialize session state
    if 'camera_running' not in st.session_state:
        st.session_state.camera_running = False
    
    if 'emotion_log' not in st.session_state:
        st.session_state.emotion_log = []
    
    if 'emotion_counts' not in st.session_state:
        st.session_state.emotion_counts = {emotion: 0 for emotion in emotion_dict.values()}
    
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = None
    
    # Start webcam
    if start_btn:
        st.session_state.camera_running = True
        st.session_state.emotion_log = []
        st.session_state.emotion_counts = {emotion: 0 for emotion in emotion_dict.values()}
        st.session_state.session_start_time = datetime.now()
        st.rerun()
    
    # Stop webcam and analyze
    if stop_btn:
        st.session_state.camera_running = False
        st.rerun()
    
    # Camera display and detection
    if st.session_state.camera_running:
        st.markdown("###  Live Feed")
        
        # Placeholder for video and metrics
        video_placeholder = st.empty()
        metrics_placeholder = st.empty()
        
        # Open webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error(" Could not access webcam. Please check your camera permissions.")
            st.session_state.camera_running = False
            return
        
        frame_count = 0
        
        try:
            while st.session_state.camera_running:
                ret, frame = cap.read()
                
                if not ret:
                    st.warning(" Failed to capture frame from webcam")
                    break
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
                
                current_emotion = None
                confidence = 0
                
                for (x, y, w, h) in faces:
                    # Draw rectangle around face
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (0, 255, 255), 2)
                    
                    # Extract face ROI
                    roi_gray = gray[y:y + h, x:x + w]
                    
                    # Preprocess for model
                    cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
                    
                    # Predict emotion
                    prediction = model.predict(cropped_img, verbose=0)
                    maxindex = int(np.argmax(prediction))
                    current_emotion = emotion_dict[maxindex]
                    confidence = float(prediction[0][maxindex]) * 100
                    
                    # Draw emotion text
                    cv2.putText(
                        frame, 
                        f"{current_emotion} ({confidence:.1f}%)", 
                        (x+20, y-60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.8, 
                        (255, 255, 255), 
                        2, 
                        cv2.LINE_AA
                    )
                    
                    # Log emotion
                    if frame_count % 10 == 0:  # Log every 10 frames to avoid too much data
                        st.session_state.emotion_log.append({
                            'timestamp': datetime.now(),
                            'emotion': current_emotion,
                            'confidence': confidence
                        })
                        st.session_state.emotion_counts[current_emotion] += 1
                
                # Convert BGR to RGB for display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Display frame
                video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                
                # Display live metrics
                if current_emotion:
                    with metrics_placeholder.container():
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Current Emotion", f"{emotion_emoji.get(current_emotion, '🎭')} {current_emotion}")
                        
                        with col2:
                            st.metric("Confidence", f"{confidence:.1f}%")
                        
                        with col3:
                            st.metric("Frames Analyzed", len(st.session_state.emotion_log))
                        
                        with col4:
                            if st.session_state.session_start_time:
                                duration = (datetime.now() - st.session_state.session_start_time).seconds
                                st.metric("Duration", f"{duration}s")
                
                frame_count += 1
                
                # Small delay to control frame rate
                time.sleep(0.03)  # ~30 FPS
                
        finally:
            cap.release()
    
    # Display analysis results if session stopped
    elif len(st.session_state.emotion_log) > 0:
        display_analysis_results(
            st.session_state.emotion_log, 
            st.session_state.emotion_counts,
            emotion_emoji,
            db_handler,
            user_id
        )

def display_analysis_results(emotion_log, emotion_counts, emotion_emoji, db_handler, user_id):
    """Display comprehensive analysis of the emotion detection session"""
    
    st.markdown("---")
    st.markdown("##  Session Analysis Results")
    
    total_frames = len(emotion_log)
    
    if total_frames == 0:
        st.warning("No emotions detected in this session.")
        return
    
    # Calculate scores
    wellness_score = calculate_wellness_score(emotion_counts, total_frames)
    risk_score = calculate_risk_score(emotion_counts, total_frames)
    
    # Get dominant emotion
    dominant_emotion = max(emotion_counts, key=emotion_counts.get)
    dominant_percentage = (emotion_counts[dominant_emotion] / total_frames) * 100
    
    # Calculate average confidence
    avg_confidence = np.mean([log['confidence'] for log in emotion_log])
    
    # Session duration
    if len(emotion_log) > 1:
        session_duration = (emotion_log[-1]['timestamp'] - emotion_log[0]['timestamp']).seconds
    else:
        session_duration = 0
    
    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
            <h1 style="font-size: 3rem; margin: 0;">{emotion_emoji.get(dominant_emotion, '🎭')}</h1>
            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #e0e0e0;">
            <h4 style="color: #ff69b4; margin: 10px 0;">{dominant_emotion}</h4>
            <p style="color: #666; margin: 5px 0;">{dominant_percentage:.1f}% of session</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
            <h2 style="color: #4ecdc4; margin: 10px 0; font-size: 2.5rem;">{wellness_score:.1f}/10</h2>
            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #e0e0e0;">
            <p style="color: #666; margin: 5px 0;">Wellness Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
            <h2 style="color: #ff85c0; margin: 10px 0; font-size: 2.5rem;">{avg_confidence:.1f}%</h2>
            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #e0e0e0;">
            <p style="color: #666; margin: 5px 0;">Avg Confidence</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        risk_level = "Low" if risk_score < 4 else "Moderate" if risk_score < 7 else "High"
        risk_class = "risk-low" if risk_score < 4 else "risk-moderate" if risk_score < 7 else "risk-high"
        
        st.markdown(f"""
        <div class="custom-card" style="text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center;">
            <h2 style="color: #ff99cc; margin: 10px 0; font-size: 2.5rem;">{risk_score:.1f}/10</h2>
            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #e0e0e0;">
            <div class="{risk_class} risk-badge" style="margin: 10px auto;">{risk_level} Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Analysis Tabs
    tab1, tab2, tab3 = st.tabs([" Emotion Distribution", " Timeline", " Session Details"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Emotion distribution chart
            fig = go.Figure(data=[go.Bar(
                x=list(emotion_counts.values()),
                y=list(emotion_counts.keys()),
                orientation='h',
                marker=dict(
                    color=['#ff6b6b', '#ee5a6f', '#c44569', '#4ecdc4', '#95afc0', '#686de0', '#ffbe76'],
                    line=dict(color='white', width=2)
                ),
                text=[f'{v} ({v/total_frames*100:.1f}%)' for v in emotion_counts.values()],
                textposition='auto'
            )])
            
            fig.update_layout(
                title='Emotion Distribution Throughout Session',
                xaxis_title='Number of Detections',
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("###  Top 3 Emotions")
            sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
            
            for i, (emotion, count) in enumerate(sorted_emotions[:3], 1):
                percentage = (count / total_frames) * 100
                st.markdown(f"""
                <div class="custom-card">
                    <strong>#{i} {emotion_emoji.get(emotion, '🎭')} {emotion}</strong><br>
                    <span style="color: #ff69b4; font-size: 1.2rem; font-weight: 600;">
                        {count} times ({percentage:.1f}%)
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Emotion Timeline")
        
        # Create timeline dataframe
        df = pd.DataFrame(emotion_log)
        
        if len(df) > 0:
            # Create timeline plot
            fig = go.Figure()
            
            # Map emotions to numeric values for plotting
            emotion_to_num = {emotion: i for i, emotion in enumerate(emotion_counts.keys())}
            df['emotion_num'] = df['emotion'].map(emotion_to_num)
            
            # Create time series
            df['seconds'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()
            
            fig.add_trace(go.Scatter(
                x=df['seconds'],
                y=df['emotion_num'],
                mode='lines+markers',
                name='Emotion',
                line=dict(color='#ff69b4', width=2),
                marker=dict(size=8, color='#ff85c0'),
                hovertemplate='<b>Time:</b> %{x:.1f}s<br><b>Emotion:</b> %{text}<br><b>Confidence:</b> %{customdata:.1f}%',
                text=df['emotion'],
                customdata=df['confidence']
            ))
            
            fig.update_layout(
                title='Emotion Changes Over Time',
                xaxis_title='Time (seconds)',
                yaxis_title='Emotion',
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(emotion_to_num.values()),
                    ticktext=list(emotion_to_num.keys())
                ),
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Confidence timeline
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=df['seconds'],
                y=df['confidence'],
                mode='lines',
                name='Confidence',
                line=dict(color='#4ecdc4', width=2),
                fill='tozeroy',
                fillcolor='rgba(78, 205, 196, 0.2)'
            ))
            
            fig2.update_layout(
                title='Detection Confidence Over Time',
                xaxis_title='Time (seconds)',
                yaxis_title='Confidence (%)',
                height=300,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("###  Session Statistics")
            st.markdown(f"""
            <div class="custom-card">
                <p><strong>Total Frames Analyzed:</strong> {total_frames}</p>
                <p><strong>Session Duration:</strong> {session_duration} seconds</p>
                <p><strong>Average Confidence:</strong> {avg_confidence:.1f}%</p>
                <p><strong>Dominant Emotion:</strong> {dominant_emotion} ({dominant_percentage:.1f}%)</p>
                <p><strong>Unique Emotions Detected:</strong> {sum(1 for count in emotion_counts.values() if count > 0)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("###  Recommendations")
            
            if risk_score >= 7:
                st.error("""
                **High Risk Detected**
                - Consider speaking with a mental health professional
                - Practice stress-reduction techniques
                - Ensure adequate rest and self-care
                """)
            elif risk_score >= 4:
                st.warning("""
                **Moderate Concerns**
                - Monitor your emotional state
                - Engage in relaxing activities
                - Connect with friends or family
                """)
            else:
                st.success("""
                **Looking Good!**
                - Maintain your positive habits
                - Continue self-care practices
                - Keep tracking your emotions
                """)
    
    # Save to MongoDB if available
    if db_handler and user_id:
        try:
            # Prepare emotions dictionary
            emotions_dict = {emotion.lower(): float(count/total_frames*100) for emotion, count in emotion_counts.items()}
            
            # Prepare analysis data
            analysis_data = {
                'emotion': dominant_emotion.lower(),
                'emotions': emotions_dict,
                'wellness_score': wellness_score,
                'risk_score': risk_score,
                'sentiment': 'Positive' if wellness_score > 6 else 'Neutral' if wellness_score > 4 else 'Negative',
                'session_duration': f"{session_duration}s",
                'total_frames': total_frames,
                'avg_confidence': float(avg_confidence)
            }
            
            # Save analysis to database
            success = db_handler.save_analysis(
                user_id=user_id,
                analysis_type='realtime_emotion',
                analysis_data=analysis_data
            )
            
            if success:
                st.success(" Session results saved to your dashboard!")
            else:
                st.warning(" Could not save results to database")
        except Exception as e:
            print(f"Database error: {str(e)}")
    
    # Download button for emotion log
    st.markdown("---")
    st.markdown("###  Export Session Data")
    
    # Create CSV
    df = pd.DataFrame(emotion_log)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label=" Download Emotion Log (CSV)",
        data=csv,
        file_name=f"emotion_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )
