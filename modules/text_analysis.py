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
        
        analyze_button = st.button(" Analyze Text", width="stretch", type="primary")
        
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
    """Perform comprehensive text analysis"""
    
    st.markdown("---")
    st.markdown("##  Analysis Results")
    
    # Sentiment Analysis
    blob = TextBlob(text)
    sentiment_polarity = blob.sentiment.polarity
    sentiment_subjectivity = blob.sentiment.subjectivity
    
    # Determine sentiment category
    if sentiment_polarity > 0.1:
        sentiment_label = "Positive"
        sentiment_color = "#28a745"
        sentiment_emoji = ""
    elif sentiment_polarity < -0.1:
        sentiment_label = "Negative"
        sentiment_color = "#ff69b4"
        sentiment_emoji = ""
    else:
        sentiment_label = "Neutral"
        sentiment_color = "#ffa500"
        sentiment_emoji = ""
    
    # Calculate risk score (TODO: Replace with actual ML model)
    risk_score = 50  # Placeholder - will be replaced with model prediction
    
    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h1 style="font-size: 3rem; margin: 0;">{sentiment_emoji}</h1>
            <h4 style="color: {sentiment_color}; margin: 10px 0;">{sentiment_label}</h4>
            <p style="color: #666;">Overall Sentiment</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h2 style="color: #ff69b4; margin: 10px 0;">{abs(sentiment_polarity):.2f}</h2>
            <p style="color: #666;">Sentiment Intensity</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h2 style="color: #ff85c0; margin: 10px 0;">{sentiment_subjectivity:.2f}</h2>
            <p style="color: #666;">Subjectivity</p>
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
    
    # Detailed Analysis Sections
    tab1, tab2, tab3 = st.tabs(["📊 Emotion Detection", "🔑 Key Phrases", "📝 Patterns"])
    
    with tab1:
        st.markdown("### Detected Emotions")
        
        # TODO: Replace with actual emotion detection model
        st.info("🚧 Emotion detection will be implemented with ML model")
        st.markdown("**Note:** This section will use a trained model for accurate emotion detection from text.")
    
    with tab2:
        st.markdown("### Key Phrases & Words")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Positive Indicators")
            # TODO: Replace with actual keyword extraction model
            st.info("🚧 Positive keyword extraction will be implemented with ML model")
        
        with col2:
            st.markdown("#### Concern Indicators")
            # TODO: Replace with actual keyword extraction model
            st.info("🚧 Concern indicator extraction will be implemented with ML model")
        
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
        'sentiment': sentiment_label,
        'risk_score': risk_score
    })
    
    # Save to MongoDB
    if db_handler and user_id:
        analysis_data = {
            'text': text[:500],  # Save first 500 chars for privacy
            'sentiment': sentiment_label,
            'sentiment_polarity': float(sentiment_polarity),
            'sentiment_subjectivity': float(sentiment_subjectivity),
            'risk_level': risk_level,
            'risk_score': int(risk_score),
            'wellness_score': int(100 - risk_score),  # Inverse of risk
            'emotions': {},  # TODO: Will be populated by emotion detection model
            'word_count': len(text.split()),
            'is_chat': is_chat
        }
        
        success = db_handler.save_analysis(user_id, 'text_analysis', analysis_data)
        if success:
            st.success("✅ Analysis saved to your history!")
        else:
            st.warning("⚠️ Could not save to history, but analysis completed successfully.")
