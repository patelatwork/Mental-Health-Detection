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
            st.markdown("""
            <div class="custom-card">
                <h4> Quick Stats</h4>
                <p><strong>Characters:</strong> <span id="char-count">0</span></p>
                <p><strong>Words:</strong> <span id="word-count">0</span></p>
                <p><strong>Sentences:</strong> <span id="sent-count">0</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            if text_input:
                word_count = len(text_input.split())
                char_count = len(text_input)
                sent_count = len(re.split(r'[.!?]+', text_input))
                
                st.metric("Characters", char_count)
                st.metric("Words", word_count)
                st.metric("Sentences", sent_count)
        
        analyze_button = st.button(" Analyze Text", use_container_width=True, type="primary")
        
        if analyze_button and text_input:
            with st.spinner("Analyzing your text..."):
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
                    with st.spinner("Processing file..."):
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
                with st.spinner("Analyzing conversation patterns..."):
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
    tab1, tab2, tab3 = st.tabs(["📊 Emotion Detection", "🔑 Key Phrases", "📝 Patterns"])
    
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
    
    with tab2:
        st.markdown("### Key Phrases & Words")
        
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ Positive Indicators")
            if found_keywords['positive']:
                for keyword in found_keywords['positive']:
                    st.markdown(f"- `{keyword}` ✓")
            else:
                st.info("No strong positive indicators found")
        
        with col2:
            st.markdown("#### ⚠️ Concern Indicators")
            
            if found_keywords['critical']:
                st.error("**🚨 Critical Keywords Detected:**")
                for keyword in found_keywords['critical']:
                    st.markdown(f"- `{keyword}` ⚠️")
                st.warning("**Please seek immediate professional help if you're having thoughts of self-harm.**")
            
            if found_keywords['high']:
                st.warning("**High-Risk Keywords:**")
                for keyword in found_keywords['high'][:5]:  # Limit to 5
                    st.markdown(f"- `{keyword}`")
            
            if found_keywords['moderate']:
                st.info("**Moderate Concern Keywords:**")
                for keyword in found_keywords['moderate'][:5]:  # Limit to 5
                    st.markdown(f"- `{keyword}`")
            
            if not any([found_keywords['critical'], found_keywords['high'], found_keywords['moderate']]):
                st.success("No significant concern indicators found")
        
        st.markdown("---")
        st.markdown("#### Most Frequent Words")
        
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter([w for w in words if len(w) > 3])
        
        if word_freq:
            df_words = pd.DataFrame(word_freq.most_common(15), columns=['Word', 'Frequency'])
            
            fig = px.bar(df_words, x='Frequency', y='Word', orientation='h',
                        color='Frequency', color_continuous_scale='Pinkyl')
            fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
            
            st.plotly_chart(fig, width="stretch")
    
    with tab3:
        st.markdown("### Communication Patterns")
        
        # Sentence length analysis
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Average Sentence Length", f"{np.mean(sentence_lengths):.1f} words")
            st.metric("Total Sentences", len(sentences))
            st.metric("Longest Sentence", f"{max(sentence_lengths)} words")
        
        with col2:
            # Sentence length distribution
            fig = go.Figure(data=[go.Histogram(
                x=sentence_lengths,
                marker=dict(color='#ff69b4'),
                nbinsx=20
            )])
            
            fig.update_layout(
                title='Sentence Length Distribution',
                xaxis_title='Words per Sentence',
                yaxis_title='Frequency',
                height=250,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, width="stretch")
        
        # Writing style analysis
        st.markdown("#### Writing Style Indicators")
        
        style_metrics = {
            "Personal Expression": min(100, text.lower().count('i ') * 5),
            "Question Frequency": min(100, text.count('?') * 10),
            "Exclamation Usage": min(100, text.count('!') * 8),
            "Descriptive Language": min(100, len([w for w in words if len(w) > 6]) * 2)
        }
        
        for metric, value in style_metrics.items():
            st.markdown(f"**{metric}**: {value}%")
            st.progress(value / 100)
    
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
            st.success("✅ Analysis saved to your history!")
        else:
            st.warning("⚠️ Could not save to history, but analysis completed successfully.")
