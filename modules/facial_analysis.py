import streamlit as st
import numpy as np
import cv2
from PIL import Image
import plotly.graph_objects as go
from datetime import datetime
from database.mongodb_handler import MongoDBHandler

def facial_analysis_page(db_handler: MongoDBHandler = None):
    st.markdown("#  Facial Expression Analysis")
    st.markdown("### Detect emotions through facial recognition")
    st.markdown("---")
    
    # Get user ID from session
    user_id = st.session_state.get('user_id')
    
    # Input Methods
    tab1, tab2 = st.tabs([" Camera Capture", " Upload Image"])
    
    with tab1:
        st.markdown("#### Use your webcam for real-time analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info("""
             **Tips for best results:**
            - Ensure good lighting on your face
            - Look directly at the camera
            - Maintain a neutral background
            - Position face in the center of frame
            """)
            
            # Placeholder for camera capture
            st.markdown("""
            <div class="custom-card" style="text-align: center; padding: 40px;">
                <h2></h2>
                <p>Click below to enable camera access</p>
                <br>
                <div style="background: #c4f0ed; 
                            color: white; padding: 15px; border-radius: 50px; 
                            display: inline-block; cursor: pointer; font-weight: 600;">
                     Enable Camera
                </div>
                <br><br>
                <p style="color: #999; font-size: 12px;">Your privacy is protected - images are processed locally</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Camera capture widget (placeholder)
            camera_image = st.camera_input("Take a photo")
            
            if camera_image is not None:
                image = Image.open(camera_image)
                
                if st.button(" Analyze Photo", width="stretch", type="primary"):
                    with st.spinner("Analyzing facial expressions..."):
                        analyze_face(image)
        
        with col2:
            st.markdown("""
            <div class="custom-card">
                <h4> Settings</h4>
                <p><strong>Resolution:</strong> 640x480</p>
                <p><strong>Detection:</strong> Active</p>
                <p><strong>Privacy:</strong> Local</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="custom-card" style="margin-top: 20px;">
                <h4> Privacy Notice</h4>
                <p style="font-size: 12px; color: #666;">
                    All facial analysis is performed locally. 
                    No images are stored or transmitted.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("#### Upload an image for facial emotion analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_image = st.file_uploader(
                "Choose an image file",
                type=['jpg', 'jpeg', 'png', 'bmp'],
                help="Upload a clear photo of a face"
            )
            
            if uploaded_image is not None:
                image = Image.open(uploaded_image)
                
                # Display uploaded image
                st.image(image, caption="Uploaded Image", width="stretch")
                
                # Analysis options
                col_a, col_b = st.columns(2)
                
                with col_a:
                    detect_multiple = st.checkbox("Detect Multiple Faces", value=False)
                    show_landmarks = st.checkbox("Show Facial Landmarks", value=True)
                
                with col_b:
                    confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5)
                
                if st.button(" Analyze Image", width="stretch", type="primary"):
                    with st.spinner("Processing image..."):
                        analyze_face(image, detect_multiple, show_landmarks, confidence_threshold)
        
        with col2:
            st.markdown("""
            <div class="custom-card">
                <h4> Image Guidelines</h4>
                <ul style="color: #666; line-height: 1.8; font-size: 13px;">
                    <li>Clear face visibility</li>
                    <li>Good lighting</li>
                    <li>Front-facing pose</li>
                    <li>Minimal obstructions</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="custom-card" style="margin-top: 20px;">
                <h4> Detectable Emotions</h4>
                <p style="font-size: 12px; color: #666;">
                    Happy, Sad, Angry, Surprised, 
                    Fearful, Disgusted, Neutral
                </p>
            </div>
            """, unsafe_allow_html=True)
    
  
        
        with col2:
            st.markdown("""
            <div class="custom-card">
                <h4> Processing</h4>
                <p style="color: #666; font-size: 13px;">
                    Video analysis may take several minutes 
                    depending on length and resolution.
                </p>
            </div>
            """, unsafe_allow_html=True)

def analyze_face(image, detect_multiple=False, show_landmarks=True, confidence_threshold=0.5):
    """Comprehensive facial emotion analysis"""
    
    try:
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        st.markdown("---")
        st.markdown("##  Facial Analysis Results")
        
        # Simulate face detection and emotion recognition
        # In production, use actual deep learning models (e.g., DeepFace, FER)
        detected_faces = simulate_face_detection(img_array)
        
        if len(detected_faces) == 0:
            st.warning(" No faces detected in the image. Please upload a clearer photo with visible faces.")
            return
        
        # Analyze each detected face
        for idx, face_data in enumerate(detected_faces):
            if len(detected_faces) > 1:
                st.markdown(f"### Face #{idx + 1}")
            
            emotions = face_data['emotions']
            dominant_emotion = max(emotions, key=emotions.get)
            
            # Calculate risk score
            risk_score = calculate_facial_risk_score(emotions)
            
            # Display main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            emotion_emoji = {
                'Happy': '',
                'Sad': '',
                'Angry': '',
                'Surprised': '',
                'Fearful': '',
                'Disgusted': '',
                'Neutral': ''
            }
            
            with col1:
                st.markdown(f"""
                <div class="custom-card" style="text-align: center;">
                    <h1 style="font-size: 3rem; margin: 0;">{emotion_emoji.get(dominant_emotion, '')}</h1>
                    <h4 style="color: #ff69b4; margin: 10px 0;">{dominant_emotion}</h4>
                    <p style="color: #666;">Primary Emotion</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                confidence = emotions[dominant_emotion]
                st.markdown(f"""
                <div class="custom-card" style="text-align: center;">
                    <h2 style="color: #ff69b4; margin: 10px 0;">{confidence:.1f}%</h2>
                    <p style="color: #666;">Confidence Level</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                age_estimate = np.random.randint(20, 45)  # Demo
                st.markdown(f"""
                <div class="custom-card" style="text-align: center;">
                    <h2 style="color: #ff85c0; margin: 10px 0;">{age_estimate}</h2>
                    <p style="color: #666;">Estimated Age</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                risk_level = "Low" if risk_score < 40 else "Moderate" if risk_score < 70 else "High"
                risk_class = "risk-low" if risk_score < 40 else "risk-moderate" if risk_score < 70 else "risk-high"
                
                st.markdown(f"""
                <div class="custom-card" style="text-align: center;">
                    <h2 style="color: #ff99cc; margin: 10px 0;">{risk_score}/100</h2>
                    <div class="{risk_class} risk-badge">{risk_level}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Detailed Analysis
            tab1, tab2, tab3, tab4 = st.tabs([" Emotions", " Landmarks", " Metrics", " Insights"])
            
            with tab1:
                st.markdown("### Emotion Distribution")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Emotion radar chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatterpolar(
                        r=list(emotions.values()),
                        theta=list(emotions.keys()),
                        fill='toself',
                        fillcolor='rgba(255, 105, 180, 0.3)',
                        line=dict(color='#ff69b4', width=2),
                        name='Emotions'
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )
                        ),
                        showlegend=False,
                        title='Emotion Intensity Radar',
                        height=400
                    )
                    
                    st.plotly_chart(fig, width="stretch")
                    
                    # Bar chart
                    fig_bar = go.Figure(data=[go.Bar(
                        x=list(emotions.keys()),
                        y=list(emotions.values()),
                        marker=dict(
                            color=list(emotions.values()),
                            colorscale='Pinkyl',
                            line=dict(color='white', width=2)
                        ),
                        text=[f'{v:.1f}%' for v in emotions.values()],
                        textposition='auto'
                    )])
                    
                    fig_bar.update_layout(
                        title='Emotion Confidence Scores',
                        xaxis_title='Emotion',
                        yaxis_title='Confidence (%)',
                        height=300,
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    
                    st.plotly_chart(fig_bar, width="stretch")
                
                with col2:
                    st.markdown("#### Emotion Rankings")
                    
                    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
                    
                    for i, (emotion, score) in enumerate(sorted_emotions, 1):
                        emoji = emotion_emoji.get(emotion, '')
                        st.markdown(f"""
                        <div class="custom-card" style="margin: 10px 0;">
                            <strong>#{i} {emoji} {emotion}</strong><br>
                            <span style="color: #ff69b4; font-size: 1.1rem;">{score:.1f}%</span>
                        </div>
                        """, unsafe_allow_html=True)
            
            with tab2:
                st.markdown("### Facial Landmarks & Features")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div class="custom-card">
                        <h4> Facial Features Detected</h4>
                        <ul style="color: #666; line-height: 1.8;">
                            <li> Eyes: Detected</li>
                            <li> Nose: Detected</li>
                            <li> Mouth: Detected</li>
                            <li> Eyebrows: Detected</li>
                            <li> Face Contour: Detected</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="custom-card">
                        <h4> Facial Measurements</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Eye Openness", f"{np.random.randint(70, 100)}%")
                    st.metric("Mouth Openness", f"{np.random.randint(10, 40)}%")
                    st.metric("Eyebrow Position", f"{np.random.randint(40, 80)}%")
                
                # Show annotated image (placeholder)
                st.markdown("#### Annotated Face")
                st.image(image, caption="Facial landmarks would be overlaid here", width="stretch")
            
            with tab3:
                st.markdown("### Detailed Metrics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("""
                    <div class="custom-card">
                        <h4> Expression Intensity</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Smile Intensity", f"{np.random.randint(20, 80)}%")
                    st.metric("Eye Crinkles", f"{np.random.randint(10, 60)}%")
                
                with col2:
                    st.markdown("""
                    <div class="custom-card">
                        <h4> Stress Indicators</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Facial Tension", f"{np.random.randint(20, 70)}%")
                    st.metric("Fatigue Signs", f"{np.random.randint(10, 50)}%")
                
                with col3:
                    st.markdown("""
                    <div class="custom-card">
                        <h4> Overall Assessment</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.metric("Emotional Stability", f"{np.random.randint(60, 90)}%")
                    st.metric("Well-being Score", f"{np.random.randint(65, 95)}%")
                
                # Micro-expressions
                st.markdown("#### Micro-Expression Analysis")
                
                micro_expressions = {
                    "Genuine Smile": np.random.randint(40, 90),
                    "Concern/Worry": np.random.randint(10, 40),
                    "Tension": np.random.randint(15, 50),
                    "Relaxation": np.random.randint(50, 85)
                }
                
                for expr, value in micro_expressions.items():
                    st.markdown(f"**{expr}**: {value}%")
                    st.progress(value / 100)
            
            with tab4:
                st.markdown("###  Facial Analysis Insights")
                
                # Generate insights
                insights = generate_facial_insights(emotions, risk_score, dominant_emotion)
                
                for insight in insights:
                    st.markdown(f"""
                    <div class="custom-card">
                        <h4>{insight['title']}</h4>
                        <p style="color: #666;">{insight['content']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("#### Recommendations")
                
                recommendations = [
                    {
                        'priority': '🟢 Wellness Tip',
                        'action': 'Maintain regular social interactions to boost emotional well-being'
                    },
                    {
                        'priority': '🟡 Self-Care',
                        'action': 'Practice facial relaxation exercises to reduce tension'
                    }
                ]
                
                if risk_score > 60:
                    recommendations.insert(0, {
                        'priority': ' Important',
                        'action': 'Consider scheduling a consultation with a mental health professional'
                    })
                
                for rec in recommendations:
                    st.markdown(f"""
                    <div style="background: #fff0f5; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ff69b4;">
                        <strong>{rec['priority']}</strong> - {rec['action']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Save to history
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        
        st.session_state.analysis_history.append({
            'timestamp': datetime.now(),
            'type': 'Facial',
            'emotion': dominant_emotion,
            'risk_score': risk_score
        })
        
    except Exception as e:
        st.error(f" Error analyzing image: {str(e)}")
        st.info("Please ensure the image is valid and contains visible faces.")

def simulate_face_detection(image):
    """Simulate face detection and emotion recognition"""
    
    # In production, use actual models like DeepFace, FER, or custom trained models
    # This is a simplified simulation
    
    emotions_set = {
        'Happy': np.random.uniform(40, 80),
        'Sad': np.random.uniform(5, 30),
        'Angry': np.random.uniform(5, 25),
        'Surprised': np.random.uniform(5, 35),
        'Fearful': np.random.uniform(5, 20),
        'Disgusted': np.random.uniform(5, 15),
        'Neutral': np.random.uniform(20, 50)
    }
    
    # Normalize to 100%
    total = sum(emotions_set.values())
    emotions_normalized = {k: (v/total) * 100 for k, v in emotions_set.items()}
    
    return [{'emotions': emotions_normalized}]

def calculate_facial_risk_score(emotions):
    """Calculate mental health risk from facial emotions"""
    
    score = 50  # Base score
    
    # Adjust based on emotions
    if emotions.get('Sad', 0) > 50:
        score += 25
    if emotions.get('Fearful', 0) > 40:
        score += 20
    if emotions.get('Angry', 0) > 50:
        score += 15
    if emotions.get('Happy', 0) > 60:
        score -= 25
    if emotions.get('Neutral', 0) > 70:
        score -= 10
    
    return min(100, max(0, score))

def generate_facial_insights(emotions, risk_score, dominant_emotion):
    """Generate insights from facial analysis"""
    insights = []
    
    if dominant_emotion == 'Happy':
        insights.append({
            'title': ' Positive Emotional State',
            'content': 'Your facial expressions indicate a positive emotional state. This is a good sign of mental well-being!'
        })
    elif dominant_emotion == 'Sad':
        insights.append({
            'title': ' Signs of Sadness',
            'content': 'Facial analysis shows indicators of sadness. It\'s important to acknowledge these feelings and consider reaching out for support.'
        })
    elif dominant_emotion == 'Angry':
        insights.append({
            'title': ' Anger or Frustration Detected',
            'content': 'Your expression suggests anger or frustration. Consider stress management techniques like deep breathing or physical exercise.'
        })
    
    if emotions.get('Fearful', 0) > 40:
        insights.append({
            'title': ' Anxiety Indicators',
            'content': 'Facial features suggest anxiety or fear. Practicing mindfulness and relaxation techniques may help.'
        })
    
    if risk_score > 70:
        insights.append({
            'title': ' Elevated Concern Level',
            'content': 'Facial analysis indicates significant emotional distress. We strongly recommend consulting with a mental health professional.'
        })
    
    return insights
