import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from textblob import TextBlob
import re
from collections import Counter
from datetime import datetime
from database.mongodb_handler import MongoDBHandler
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

# Load emotion detection model (cached)
@st.cache_resource
def load_emotion_model():
    """Load the emotion detection model"""
    try:
        return pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
    except Exception as e:
        st.error(f"Error loading emotion model: {str(e)}")
        return None

def text_analysis_page(db_handler: MongoDBHandler = None):
    st.markdown("#  Text Analysis")
    st.markdown("### Analyze written communication for emotional indicators")
    st.markdown("---")
    
    # Get user ID from session
    user_id = st.session_state.get('user_id')
    
    # Input Methods
    tab1, tab2, tab3 = st.tabs([" Type Text", " Upload File", " Chat History"])
    
    with tab1:
        st.markdown("#### Enter your text for analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            text_input = st.text_area(
                "Share your thoughts, feelings, or journal entry:",
                height=200,
                placeholder="Type or paste your text here... The more you write, the better the analysis."
            )
        
        with col2:
            # Calculate stats dynamically
            if text_input:
                word_count = len(text_input.split())
                char_count = len(text_input)
                sent_count = len(re.split(r'[.!?]+', text_input))
            else:
                word_count = 0
                char_count = 0
                sent_count = 0
            
            # Display dynamic stats in a compact card
            st.markdown(f"""
            <div class="custom-card" style="text-align: center; padding: 12px; height: 200px; display: flex; flex-direction: column; justify-content: space-around; overflow: hidden; box-sizing: border-box;">
                <h4 style="color: #000000; margin: 0; padding: 0; font-size: 16px; font-weight: 600;"> Quick Stats</h4>
                <div style="padding: 3px 0;">
                    <p style="color: #666; margin: 0; padding: 0; font-size: 11px;">Characters</p>
                    <h3 style="color: #c4f0ed; margin: 2px 0; padding: 0; font-size: 22px; font-weight: 700; line-height: 1;">{char_count}</h3>
                </div>
                <div style="padding: 3px 0;">
                    <p style="color: #666; margin: 0; padding: 0; font-size: 11px;">Words</p>
                    <h3 style="color: #c4f0ed; margin: 2px 0; padding: 0; font-size: 22px; font-weight: 700; line-height: 1;">{word_count}</h3>
                </div>
                <div style="padding: 3px 0;">
                    <p style="color: #666; margin: 0; padding: 0; font-size: 11px;">Sentences</p>
                    <h3 style="color: #c4f0ed; margin: 2px 0; padding: 0; font-size: 22px; font-weight: 700; line-height: 1;">{sent_count}</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        analyze_button = st.button(" Analyze Text", use_container_width=True, type="primary")
        
        if analyze_button and text_input:
            analyze_text(text_input, db_handler=db_handler, user_id=user_id)
        elif analyze_button:
            st.warning(" Please enter some text to analyze.")
    
    with tab2:
        st.markdown("#### Upload a text file or document")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'csv', 'doc', 'docx'],
            help="Upload a text file, journal entry, or chat export"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                st.success(f" File uploaded successfully: {uploaded_file.name}")
                
                if st.button(" Analyze Uploaded File", type="primary"):
                    analyze_text(content, db_handler=db_handler, user_id=user_id)
            except Exception as e:
                st.error(f" Error reading file: {str(e)}")
    
    with tab3:
        st.markdown("#### Analyze chat history or social media posts")
        
        st.info(" Paste conversation history from messaging apps or social media exports")
        
        chat_input = st.text_area(
            "Paste chat history:",
            height=250,
            placeholder="Example:\n[2025-01-15 10:30] User: I've been feeling overwhelmed lately\n[2025-01-15 10:32] User: Work is stressing me out"
        )
        
        if st.button(" Analyze Chat History", type="primary"):
            if chat_input:
                analyze_text(chat_input, is_chat=True, db_handler=db_handler, user_id=user_id)
            else:
                st.warning(" Please paste chat history to analyze.")

def analyze_text(text, is_chat=False, db_handler=None, user_id=None):
    """Perform comprehensive text analysis with emotion detection"""
    
    st.markdown("---")
    st.markdown("##  Analysis Results")
    
    # Load emotion detection model
    emotion_classifier = load_emotion_model()
    
    if emotion_classifier is None:
        st.error("Failed to load emotion detection model. Using basic analysis.")
        emotion_results = None
    else:
        # Analyze emotions
        with st.spinner("Detecting emotions..."):
            emotion_results = emotion_classifier(text)[0]
            emotion_results = sorted(emotion_results, key=lambda x: x['score'], reverse=True)
    
    # Get dominant emotion
    if emotion_results:
        dominant_emotion = emotion_results[0]
        emotion_label = dominant_emotion['label'].capitalize()
        emotion_confidence = dominant_emotion['score'] * 100
        
        # Map emotions to colors and emojis
        emotion_config = {
            'joy': {'color': '#28a745', 'emoji': '😊', 'category': 'positive'},
            'sadness': {'color': '#dc3545', 'emoji': '😢', 'category': 'negative'},
            'anger': {'color': '#fd7e14', 'emoji': '😠', 'category': 'negative'},
            'fear': {'color': '#ffc107', 'emoji': '😨', 'category': 'negative'},
            'surprise': {'color': '#17a2b8', 'emoji': '😲', 'category': 'positive'},
            'disgust': {'color': '#6c757d', 'emoji': '🤢', 'category': 'negative'},
            'neutral': {'color': '#6f42c1', 'emoji': '😐', 'category': 'neutral'}
        }
        
        config = emotion_config.get(dominant_emotion['label'], {'color': '#6c757d', 'emoji': '😐', 'category': 'neutral'})
        emotion_color = config['color']
        emotion_emoji = config['emoji']
        
        # Calculate depression risk score based on negative emotions
        negative_weights = {
            'sadness': 0.45,
            'fear': 0.30,
            'anger': 0.20,
            'disgust': 0.15
        }
        
        risk_score = 0
        for emotion in emotion_results:
            if emotion['label'] in negative_weights:
                risk_score += emotion['score'] * negative_weights[emotion['label']] * 100
        
        risk_score = min(100, risk_score)
        
        # Calculate wellness score
        positive_score = sum(e['score'] for e in emotion_results if e['label'] in ['joy', 'surprise'])
        negative_score = sum(e['score'] for e in emotion_results if e['label'] in ['sadness', 'fear', 'anger', 'disgust'])
        neutral_score = sum(e['score'] for e in emotion_results if e['label'] == 'neutral')
        
        total_score = positive_score + negative_score + neutral_score
        if total_score > 0:
            wellness_score = ((positive_score + 0.5 * neutral_score) / total_score) * 100
        else:
            wellness_score = 50
    else:
        # Fallback to TextBlob
        blob = TextBlob(text)
        sentiment_polarity = blob.sentiment.polarity
        
        if sentiment_polarity > 0.1:
            emotion_label = "Positive"
            emotion_color = "#28a745"
            emotion_emoji = "😊"
        elif sentiment_polarity < -0.1:
            emotion_label = "Negative"
            emotion_color = "#dc3545"
            emotion_emoji = "😢"
        else:
            emotion_label = "Neutral"
            emotion_color = "#6c757d"
            emotion_emoji = "😐"
        
        emotion_confidence = abs(sentiment_polarity) * 100
        risk_score = max(0, -sentiment_polarity * 100)
        wellness_score = max(0, sentiment_polarity * 100)
    
    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h1 style="font-size: 3rem; margin: 0;">{emotion_emoji}</h1>
            <h4 style="color: {emotion_color}; margin: 10px 0;">{emotion_label}</h4>
            <p style="color: #666;">Dominant Emotion</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h2 style="color: {emotion_color}; margin: 10px 0;">{emotion_confidence:.1f}%</h2>
            <p style="color: #666;">Confidence</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h2 style="color: #28a745; margin: 10px 0;">{wellness_score:.0f}/100</h2>
            <p style="color: #666;">Wellness Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        risk_level = "Low" if risk_score < 30 else "Moderate" if risk_score < 50 else "High" if risk_score < 70 else "Critical"
        risk_colors = {"Low": "#28a745", "Moderate": "#ffc107", "High": "#fd7e14", "Critical": "#dc3545"}
        risk_color = risk_colors.get(risk_level, "#6c757d")
        
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h2 style="color: {risk_color}; margin: 10px 0;">{risk_score:.0f}/100</h2>
            <p style="color: #666;">Depression Risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Analysis Sections
    tab1, tab2 = st.tabs([" Emotion Detection", " Insights & Recommendations"])
    
    with tab1:
        st.markdown("### Detected Emotions")
        
        if emotion_results:
            # Display all emotions with confidence
            st.markdown("**All Detected Emotions:**")
            
            for i, emotion in enumerate(emotion_results, 1):
                label = emotion['label'].capitalize()
                score = emotion['score'] * 100
                
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**{i}. {label}**")
                    st.progress(emotion['score'])
                with col_b:
                    st.metric("", f"{score:.1f}%")
            
            st.markdown("---")
            
            # Emotion distribution chart
            st.markdown("**Emotion Distribution:**")
            
            emotions_df = pd.DataFrame([
                {'Emotion': e['label'].capitalize(), 'Confidence': e['score'] * 100}
                for e in emotion_results
            ])
            
            fig = px.bar(
                emotions_df,
                x='Emotion',
                y='Confidence',
                color='Emotion',
                color_discrete_map={
                    'Joy': '#28a745',
                    'Sadness': '#dc3545',
                    'Anger': '#fd7e14',
                    'Fear': '#ffc107',
                    'Surprise': '#17a2b8',
                    'Disgust': '#6c757d',
                    'Neutral': '#6f42c1'
                },
                text='Confidence'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(
                height=400,
                showlegend=False,
                yaxis_title="Confidence (%)",
                xaxis_title="Emotion"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Emotion detection model not available. Using basic sentiment analysis.")
    
    # Calculate text statistics and keywords for tab2 use
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Depression-specific keyword detection
    depression_keywords = {
        'critical': ['suicide', 'kill myself', 'want to die', 'end it all', 'better off dead', 'no reason to live'],
        'high': ['depressed', 'depression', 'hate myself', 'worthless', 'hopeless', 'pointless', 'useless', 'failure', 'alone', 'lonely', 'empty'],
        'moderate': ['sad', 'unhappy', 'down', 'upset', 'stressed', 'anxious', 'worried', 'tired', 'exhausted', 'overwhelmed'],
        'positive': ['happy', 'joy', 'excited', 'love', 'grateful', 'thankful', 'blessed', 'amazing', 'wonderful', 'great', 'good', 'better']
    }
    
    text_lower = text.lower()
    
    found_keywords = {
        'critical': [kw for kw in depression_keywords['critical'] if kw in text_lower],
        'high': [kw for kw in depression_keywords['high'] if kw in text_lower],
        'moderate': [kw for kw in depression_keywords['moderate'] if kw in text_lower],
        'positive': [kw for kw in depression_keywords['positive'] if kw in text_lower]
    }
    
    with tab2:
        st.markdown("###  Personalized Insights & Recommendations")
        
        # Generate personalized recommendations based on analysis
        critical_count = len(found_keywords['critical'])
        concern_count = len(found_keywords['high']) + len(found_keywords['moderate'])
        positive_count = len(found_keywords['positive'])
        
        # Display wellness score
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <h4 style="color: white; margin: 0;"> Wellness Score</h4>
                <h1 style="color: white; margin: 15px 0; font-size: 48px;">{wellness_score:.0f}</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 0;">out of 100</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center; background: {'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' if critical_count > 0 or concern_count > 3 else 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}; color: white;">
                <h4 style="color: white; margin: 0;"> Risk Level</h4>
                <h2 style="color: white; margin: 15px 0;">{risk_level}</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 0;">{risk_score:.0f}% concern</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="custom-card" style="text-align: center; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333;">
                <h4 style="color: #333; margin: 0;">😊 Dominant Emotion</h4>
                <h2 style="color: #333; margin: 15px 0;">{emotion_label}</h2>
                <p style="color: #666; margin: 0;">{emotion_confidence:.1f}% confidence</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Personalized recommendations based on risk level
        st.markdown("####  Recommended Actions")
        
        if critical_count > 0:
            st.error("""
            ** Immediate Support Needed**
            
            Your text contains concerning language. Please consider:
            - **Call National Suicide Prevention Lifeline: 988** (US)
            - Talk to a trusted friend, family member, or counselor immediately
            - Visit your nearest emergency room if you're in immediate danger
            - Use Crisis Text Line: Text HOME to 741741
            """)
        elif concern_count > 5 or risk_level in ["High", "Moderate"]:
            st.warning("""
            Self-Care Recommendations
            
            Your text shows signs of emotional distress. Consider:
            -  Practice mindfulness or meditation (10 minutes daily)
            -  Reach out to a mental health professional or counselor
            -  Physical activity: Take a 20-minute walk outdoors
            -  Continue journaling your thoughts and feelings
            -  Connect with supportive friends or family members
            """)
        elif positive_count > concern_count:
            st.success("""
            ** Keep Up the Positive Momentum!**
            
            Your text reflects positive emotions. To maintain wellness:
            -  Set achievable goals for the week
            -  Practice gratitude journaling
            -  Share your positive energy with others
            -  Maintain healthy habits: sleep, exercise, nutrition
            -  Engage in activities you enjoy
            """)
        else:
            st.info("""
            ** Maintain Your Mental Wellness**
            
            Your emotional state appears balanced. Continue to:
            -  Keep journaling regularly to track your mood
            -  Practice stress management techniques
            -  Stay connected with your support network
            -  Focus on personal growth activities
            -  Schedule regular check-ins with yourself
            """)
        
        st.markdown("---")
        
        # Quick resources
        st.markdown("####  Mental Health Resources")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Crisis Support:**
            -  Suicide Prevention: **988**
            -  Crisis Text Line: Text **HOME** to **741741**
            -  International: findahelpline.com
            """)
        
        with col2:
            st.markdown("""
            **Professional Help:**
            -  Psychology Today: Find a Therapist
            -  BetterHelp: Online Counseling
            -  SAMHSA Helpline: 1-800-662-4357
            """)
    
    # Save to session state history
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    st.session_state.analysis_history.append({
        'timestamp': datetime.now(),
        'type': 'Text',
        'emotion': emotion_label,
        'risk_score': risk_score
    })
    
    # Save to MongoDB
    if db_handler and user_id:
        # Build emotions dict
        emotions_dict = {}
        if emotion_results:
            emotions_dict = {e['label']: float(e['score']) for e in emotion_results}
        
        analysis_data = {
            'text': text[:500],  # Save first 500 chars for privacy
            'dominant_emotion': emotion_label,
            'emotion_confidence': float(emotion_confidence),
            'emotions': emotions_dict,
            'risk_level': risk_level,
            'risk_score': float(risk_score),
            'wellness_score': float(wellness_score),
            'word_count': len(text.split()),
            'is_chat': is_chat,
            'keywords_found': found_keywords
        }
        
        success = db_handler.save_analysis(user_id, 'text_analysis', analysis_data)
        if success:
            st.success(" Analysis saved to your history!")
        else:
            st.warning(" Could not save to history, but analysis completed successfully.")
