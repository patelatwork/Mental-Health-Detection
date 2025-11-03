"""
Text Emotion Analysis Module
Real-time text-based emotion detection using HuggingFace transformers
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

# Import database handler
try:
    from database.mongodb_handler import MongoDBHandler
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

# Import styling utilities
try:
    from utils.styling import apply_common_styling
except ImportError:
    apply_common_styling = None


@st.cache_resource
def load_text_emotion_model():
    """
    Load the pre-trained emotion detection model
    Uses caching to avoid reloading on every interaction
    """
    try:
        classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
        return classifier
    except Exception as e:
        st.error(f"Error loading emotion model: {str(e)}")
        return None


def analyze_text_emotion(text, classifier):
    """
    Analyze emotion in a given text
    
    Args:
        text (str): Input text to analyze
        classifier: Pre-loaded emotion classifier
        
    Returns:
        list: List of emotion predictions with scores
    """
    try:
        if not text or len(text.strip()) == 0:
            return None
        
        results = classifier(text)[0]
        # Sort by score descending
        results_sorted = sorted(results, key=lambda x: x['score'], reverse=True)
        return results_sorted
    except Exception as e:
        st.error(f"Error analyzing text: {str(e)}")
        return None


def calculate_wellness_score(emotion_data):
    """
    Calculate wellness score (0-10) based on emotion distribution
    
    Positive emotions: joy, surprise
    Negative emotions: anger, sadness, fear, disgust
    Neutral: neutral
    
    Args:
        emotion_data (dict): Dictionary with emotion counts/scores
        
    Returns:
        float: Wellness score between 0 and 10
    """
    positive_emotions = ['joy', 'surprise']
    negative_emotions = ['anger', 'sadness', 'fear', 'disgust']
    
    positive_score = sum(emotion_data.get(emotion, 0) for emotion in positive_emotions)
    negative_score = sum(emotion_data.get(emotion, 0) for emotion in negative_emotions)
    neutral_score = emotion_data.get('neutral', 0)
    
    total = positive_score + negative_score + neutral_score
    
    if total == 0:
        return 5.0
    
    # Wellness = (positive + 0.5*neutral) / total * 10
    wellness = ((positive_score + 0.5 * neutral_score) / total) * 10
    
    return round(wellness, 2)


def calculate_risk_score(emotion_data):
    """
    Calculate depression risk score (0-10) based on negative emotions
    
    Weighted by clinical relevance:
    - Sadness: 0.45 (strongest indicator)
    - Fear: 0.30
    - Anger: 0.20
    - Disgust: 0.15
    
    Args:
        emotion_data (dict): Dictionary with emotion counts/scores
        
    Returns:
        float: Risk score between 0 and 10
    """
    weights = {
        'sadness': 0.45,
        'fear': 0.30,
        'anger': 0.20,
        'disgust': 0.15
    }
    
    total_entries = sum(emotion_data.values())
    
    if total_entries == 0:
        return 0.0
    
    risk_score = 0
    for emotion, weight in weights.items():
        if emotion in emotion_data:
            # Proportion of this emotion * weight * 10
            proportion = emotion_data[emotion] / total_entries
            risk_score += proportion * weight * 10
    
    return round(risk_score, 2)


def get_risk_level(risk_score):
    """
    Determine risk level based on risk score
    
    Args:
        risk_score (float): Risk score between 0 and 10
        
    Returns:
        tuple: (level_name, color, icon)
    """
    if risk_score >= 7.0:
        return ("Critical Risk", "#dc3545", "⚠️")
    elif risk_score >= 5.0:
        return ("High Risk", "#fd7e14", "⚡")
    elif risk_score >= 3.0:
        return ("Moderate Risk", "#ffc107", "⚠")
    elif risk_score >= 1.0:
        return ("Low Risk", "#20c997", "ℹ️")
    else:
        return ("Minimal Risk", "#28a745", "✓")


def get_wellness_level(wellness_score):
    """
    Determine wellness level based on wellness score
    
    Args:
        wellness_score (float): Wellness score between 0 and 10
        
    Returns:
        tuple: (level_name, color, icon)
    """
    if wellness_score >= 8.0:
        return ("Excellent", "#28a745", "😊")
    elif wellness_score >= 6.0:
        return ("Good", "#20c997", "🙂")
    elif wellness_score >= 4.0:
        return ("Fair", "#ffc107", "😐")
    elif wellness_score >= 2.0:
        return ("Poor", "#fd7e14", "😟")
    else:
        return ("Critical", "#dc3545", "😢")


def display_emotion_results(results, text_input):
    """
    Display emotion analysis results with visualizations
    
    Args:
        results (list): Emotion predictions with scores
        text_input (str): Original text input
    """
    st.subheader("📊 Emotion Analysis Results")
    
    # Create columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Text being analyzed
        st.markdown("**Analyzed Text:**")
        st.info(text_input)
        
        # Top 3 emotions
        st.markdown("**Top 3 Detected Emotions:**")
        for i, emotion in enumerate(results[:3], 1):
            label = emotion['label'].capitalize()
            score = emotion['score'] * 100
            
            # Progress bar
            st.write(f"{i}. **{label}**")
            st.progress(emotion['score'])
            st.caption(f"Confidence: {score:.1f}%")
    
    with col2:
        # Dominant emotion display
        dominant = results[0]
        st.markdown("**Dominant Emotion**")
        
        # Get emoji for emotion
        emotion_emojis = {
            'joy': '😊',
            'sadness': '😢',
            'anger': '😠',
            'fear': '😨',
            'surprise': '😲',
            'disgust': '🤢',
            'neutral': '😐'
        }
        
        emoji = emotion_emojis.get(dominant['label'], '🎭')
        st.markdown(f"<h1 style='text-align: center;'>{emoji}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{dominant['label'].capitalize()}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{dominant['score']*100:.1f}% confidence</p>", unsafe_allow_html=True)
    
    # Emotion distribution chart
    st.markdown("---")
    st.markdown("**📈 Emotion Distribution**")
    
    # Prepare data for chart
    emotions = [e['label'].capitalize() for e in results]
    scores = [e['score'] * 100 for e in results]
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=emotions,
            y=scores,
            marker_color=['#28a745', '#dc3545', '#fd7e14', '#ffc107', '#17a2b8', '#6c757d', '#6f42c1'],
            text=[f"{s:.1f}%" for s in scores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Emotion Scores",
        xaxis_title="Emotion",
        yaxis_title="Confidence (%)",
        yaxis_range=[0, 100],
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_session_analytics(session_data):
    """
    Display analytics for the current text analysis session
    
    Args:
        session_data (list): List of all text analyses in session
    """
    if not session_data or len(session_data) == 0:
        st.info("No texts analyzed yet. Start typing to begin!")
        return
    
    st.markdown("---")
    st.subheader("📊 Session Analytics")
    
    # Aggregate emotion data
    emotion_counts = {
        'joy': 0, 'sadness': 0, 'anger': 0, 'fear': 0,
        'surprise': 0, 'disgust': 0, 'neutral': 0
    }
    
    for entry in session_data:
        dominant_emotion = entry['dominant_emotion']
        emotion_counts[dominant_emotion] += 1
    
    # Calculate scores
    wellness_score = calculate_wellness_score(emotion_counts)
    risk_score = calculate_risk_score(emotion_counts)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Texts Analyzed", len(session_data))
    
    with col2:
        wellness_level, wellness_color, wellness_icon = get_wellness_level(wellness_score)
        st.metric("Wellness Score", f"{wellness_score}/10", delta=wellness_level)
    
    with col3:
        risk_level, risk_color, risk_icon = get_risk_level(risk_score)
        st.metric("Risk Score", f"{risk_score}/10", delta=risk_level)
    
    with col4:
        dominant_overall = max(emotion_counts.items(), key=lambda x: x[1])
        st.metric("Most Common", dominant_overall[0].capitalize())
    
    # Emotion timeline
    st.markdown("---")
    st.markdown("**📈 Emotion Timeline**")
    
    # Prepare timeline data
    timeline_df = pd.DataFrame([
        {
            'Text #': i + 1,
            'Emotion': entry['dominant_emotion'].capitalize(),
            'Confidence': entry['confidence'],
            'Timestamp': entry['timestamp']
        }
        for i, entry in enumerate(session_data)
    ])
    
    # Create timeline chart
    emotion_colors = {
        'Joy': '#28a745',
        'Sadness': '#dc3545',
        'Anger': '#fd7e14',
        'Fear': '#ffc107',
        'Surprise': '#17a2b8',
        'Disgust': '#6c757d',
        'Neutral': '#6f42c1'
    }
    
    fig = px.scatter(
        timeline_df,
        x='Text #',
        y='Confidence',
        color='Emotion',
        size='Confidence',
        hover_data=['Timestamp'],
        color_discrete_map=emotion_colors,
        title="Emotion Progression Over Session"
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Emotion distribution pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🥧 Emotion Distribution**")
        
        # Filter out zero counts
        non_zero_emotions = {k: v for k, v in emotion_counts.items() if v > 0}
        
        fig = go.Figure(data=[go.Pie(
            labels=[k.capitalize() for k in non_zero_emotions.keys()],
            values=list(non_zero_emotions.values()),
            marker_colors=['#28a745', '#dc3545', '#fd7e14', '#ffc107', '#17a2b8', '#6c757d', '#6f42c1']
        )])
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**📋 Session Summary**")
        
        # Create summary dataframe
        summary_data = []
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / len(session_data)) * 100
                summary_data.append({
                    'Emotion': emotion.capitalize(),
                    'Count': count,
                    'Percentage': f"{percentage:.1f}%"
                })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)


def export_session_to_csv(session_data):
    """
    Export session data to CSV format
    
    Args:
        session_data (list): Session data to export
        
    Returns:
        str: CSV data as string
    """
    df = pd.DataFrame([
        {
            'Timestamp': entry['timestamp'],
            'Text': entry['text'],
            'Dominant_Emotion': entry['dominant_emotion'],
            'Confidence': entry['confidence'],
            'All_Emotions': str(entry['all_emotions'])
        }
        for entry in session_data
    ])
    
    return df.to_csv(index=False)


def text_emotion_page():
    """
    Main function for the text emotion analysis page
    """
    # Apply styling if available
    if apply_common_styling:
        apply_common_styling()
    
    # Page header
    st.title("📝 Text Emotion Analysis")
    st.markdown("Analyze emotions in text using advanced AI")
    st.markdown("---")
    
    # Load model
    with st.spinner("Loading emotion detection model..."):
        classifier = load_text_emotion_model()
    
    if classifier is None:
        st.error("Failed to load emotion detection model. Please check your internet connection and try again.")
        return
    
    st.success("✅ Model loaded successfully!")
    
    # Initialize session state
    if 'text_session_data' not in st.session_state:
        st.session_state.text_session_data = []
    if 'text_session_start' not in st.session_state:
        st.session_state.text_session_start = datetime.now()
    
    # Session controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.info(f"📊 Session started: {st.session_state.text_session_start.strftime('%I:%M %p')}")
    
    with col2:
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.text_session_data = []
            st.session_state.text_session_start = datetime.now()
            st.rerun()
    
    with col3:
        if len(st.session_state.text_session_data) > 0:
            csv_data = export_session_to_csv(st.session_state.text_session_data)
            st.download_button(
                label="💾 Export CSV",
                data=csv_data,
                file_name=f"text_emotions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Text input methods
    st.subheader("✍️ Input Text")
    
    input_method = st.radio(
        "Choose input method:",
        ["Single Text", "Batch Analysis", "File Upload"],
        horizontal=True
    )
    
    # Single text analysis
    if input_method == "Single Text":
        text_input = st.text_area(
            "Enter text to analyze:",
            height=150,
            placeholder="Type or paste your text here..."
        )
        
        if st.button("🔍 Analyze Emotion", type="primary", use_container_width=True):
            if text_input and len(text_input.strip()) > 0:
                with st.spinner("Analyzing emotion..."):
                    results = analyze_text_emotion(text_input, classifier)
                
                if results:
                    # Display results
                    display_emotion_results(results, text_input)
                    
                    # Save to session
                    session_entry = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'text': text_input,
                        'dominant_emotion': results[0]['label'],
                        'confidence': results[0]['score'],
                        'all_emotions': {e['label']: e['score'] for e in results}
                    }
                    st.session_state.text_session_data.append(session_entry)
                    
                    st.success("✅ Analysis complete! Results saved to session.")
            else:
                st.warning("⚠️ Please enter some text to analyze.")
    
    # Batch analysis
    elif input_method == "Batch Analysis":
        st.info("Enter multiple texts (one per line) for batch analysis")
        
        batch_input = st.text_area(
            "Enter texts (one per line):",
            height=200,
            placeholder="Text 1\nText 2\nText 3\n..."
        )
        
        if st.button("🔍 Analyze Batch", type="primary", use_container_width=True):
            if batch_input:
                texts = [t.strip() for t in batch_input.split('\n') if t.strip()]
                
                if len(texts) > 0:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    batch_results = []
                    
                    for i, text in enumerate(texts):
                        status_text.text(f"Analyzing text {i+1}/{len(texts)}...")
                        progress_bar.progress((i + 1) / len(texts))
                        
                        results = analyze_text_emotion(text, classifier)
                        
                        if results:
                            batch_results.append({
                                'Text': text[:50] + "..." if len(text) > 50 else text,
                                'Emotion': results[0]['label'].capitalize(),
                                'Confidence': f"{results[0]['score']*100:.1f}%",
                                'Full_Text': text,
                                'Full_Results': results
                            })
                            
                            # Save to session
                            session_entry = {
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'text': text,
                                'dominant_emotion': results[0]['label'],
                                'confidence': results[0]['score'],
                                'all_emotions': {e['label']: e['score'] for e in results}
                            }
                            st.session_state.text_session_data.append(session_entry)
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success(f"✅ Analyzed {len(batch_results)} texts successfully!")
                    
                    # Display batch results
                    st.subheader("📊 Batch Results")
                    results_df = pd.DataFrame([
                        {
                            'Text': r['Text'],
                            'Emotion': r['Emotion'],
                            'Confidence': r['Confidence']
                        }
                        for r in batch_results
                    ])
                    st.dataframe(results_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("⚠️ No valid texts found. Please enter at least one text.")
            else:
                st.warning("⚠️ Please enter some texts to analyze.")
    
    # File upload
    elif input_method == "File Upload":
        st.info("Upload a text file (.txt) or CSV file for analysis")
        
        uploaded_file = st.file_uploader("Choose a file", type=['txt', 'csv'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.txt'):
                    content = uploaded_file.read().decode('utf-8')
                    texts = [t.strip() for t in content.split('\n') if t.strip()]
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    # Try to find text column
                    text_columns = [col for col in df.columns if 'text' in col.lower()]
                    if text_columns:
                        texts = df[text_columns[0]].dropna().tolist()
                    else:
                        texts = df.iloc[:, 0].dropna().tolist()
                
                st.info(f"Found {len(texts)} texts in file")
                
                if st.button("🔍 Analyze File", type="primary", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    file_results = []
                    
                    for i, text in enumerate(texts[:100]):  # Limit to 100 texts
                        status_text.text(f"Analyzing text {i+1}/{min(len(texts), 100)}...")
                        progress_bar.progress((i + 1) / min(len(texts), 100))
                        
                        results = analyze_text_emotion(str(text), classifier)
                        
                        if results:
                            file_results.append({
                                'Text': str(text)[:50] + "..." if len(str(text)) > 50 else str(text),
                                'Emotion': results[0]['label'].capitalize(),
                                'Confidence': f"{results[0]['score']*100:.1f}%"
                            })
                            
                            # Save to session
                            session_entry = {
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'text': str(text),
                                'dominant_emotion': results[0]['label'],
                                'confidence': results[0]['score'],
                                'all_emotions': {e['label']: e['score'] for e in results}
                            }
                            st.session_state.text_session_data.append(session_entry)
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success(f"✅ Analyzed {len(file_results)} texts from file!")
                    
                    # Display results
                    st.subheader("📊 File Analysis Results")
                    results_df = pd.DataFrame(file_results)
                    st.dataframe(results_df, use_container_width=True, hide_index=True)
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    # Display session analytics
    st.markdown("---")
    display_session_analytics(st.session_state.text_session_data)
    
    # Save to database option
    if MONGODB_AVAILABLE and len(st.session_state.text_session_data) > 0:
        st.markdown("---")
        st.subheader("💾 Save Session")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            session_name = st.text_input(
                "Session Name:",
                value=f"Text Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        
        with col2:
            if st.button("💾 Save to Database", use_container_width=True, type="primary"):
                try:
                    db = MongoDBHandler()
                    
                    # Aggregate emotion data
                    emotion_counts = {
                        'joy': 0, 'sadness': 0, 'anger': 0, 'fear': 0,
                        'surprise': 0, 'disgust': 0, 'neutral': 0
                    }
                    
                    for entry in st.session_state.text_session_data:
                        dominant_emotion = entry['dominant_emotion']
                        emotion_counts[dominant_emotion] += 1
                    
                    wellness_score = calculate_wellness_score(emotion_counts)
                    risk_score = calculate_risk_score(emotion_counts)
                    
                    session_doc = {
                        'session_name': session_name,
                        'session_type': 'text_emotion',
                        'start_time': st.session_state.text_session_start,
                        'end_time': datetime.now(),
                        'total_texts': len(st.session_state.text_session_data),
                        'emotion_distribution': emotion_counts,
                        'wellness_score': wellness_score,
                        'risk_score': risk_score,
                        'analyses': st.session_state.text_session_data,
                        'created_at': datetime.now()
                    }
                    
                    db.save_analysis_result(session_doc)
                    st.success("✅ Session saved to database successfully!")
                    
                except Exception as e:
                    st.error(f"Error saving to database: {str(e)}")


if __name__ == "__main__":
    text_emotion_page()
