import os
import warnings
import logging
import time

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

# Suppress torch warnings and errors
logging.getLogger('torch').setLevel(logging.ERROR)
logging.getLogger('streamlit.watcher.local_sources_watcher').setLevel(logging.ERROR)

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

# Set page config FIRST before any other Streamlit commands
st.set_page_config(
    page_title="Mental Health Early Detection AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import analysis modules
from modules.text_analysis import text_analysis_page
from modules.voice_analysis import voice_analysis_page
from modules.realtime_emotion import realtime_emotion_page
from modules.dashboard import dashboard_page
from modules.auth import show_login_page, check_authentication, logout
from database.mongodb_handler import MongoDBHandler
from utils.styling import apply_custom_css

# Apply custom styling
apply_custom_css()

# Initialize MongoDB connection
@st.cache_resource
def init_db():
    """Initialize database connection"""
    try:
        # MongoDB Atlas cloud connection
        # Using cloud database instead of local MongoDB
        db = MongoDBHandler("mongodb+srv://aadipatel1911:MyPassword123@cluster0.lp33q.mongodb.net/carenestt?retryWrites=true&w=majority&appName=Cluster0")
        return db
    except Exception as e:
        # Check if it's a disk space error
        error_msg = str(e)
        if "OutOfDiskSpace" in error_msg or "available disk space" in error_msg:
            st.warning(" MongoDB requires more disk space. Running in demo mode without database.")
        else:
            st.warning(f" Database connection failed: {error_msg}. Running in demo mode.")
        return None

def main():
    # Initialize database connection (cached, only runs once)
    if 'db_handler' not in st.session_state:
        st.session_state.db_handler = init_db()
    
    db_handler = st.session_state.db_handler
    
    # Check authentication (will restore from cookie if exists)
    if not check_authentication(db_handler):
        show_login_page(db_handler)
        return
    
    # Initialize session state for selected page
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "Dashboard"
    
    # Sidebar with optimized rendering
    with st.sidebar:
        st.markdown(f"###  Welcome, {st.session_state.get('username', 'User')}")
        st.markdown("**Mental Health Early Detection System**")
        st.markdown("---")
        
        # Navigation Menu with icons
        selected = option_menu(
            menu_title=" Analysis Type",
            options=["Dashboard", "Text Analysis", "Voice Analysis", "Real-Time Emotion"],
            icons=["speedometer2", "chat-text", "mic", "camera-video"],
            menu_icon="cast",
            default_index=["Dashboard", "Text Analysis", "Voice Analysis", "Real-Time Emotion"].index(st.session_state.selected_page),
            styles={
                "container": {"padding": "0!important", "background-color": "#ffffff"},
                "icon": {"color": "#c4f0ed", "font-size": "20px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px",
                    "padding": "10px",
                    "--hover-color": "#f0fdf4",
                    "border-radius": "10px",
                    "color": "#000000",
                    "transition": "all 0.3s ease"
                },
                "nav-link-selected": {"background-color": "#c4f0ed", "color": "#000000", "font-weight": "600"},
            }
        )
        
        st.markdown("---")
        
        # Compact About Section
        with st.expander("ℹ About"):
            st.markdown("""
            **Care Nest** uses advanced ML to detect:
            -  Stress & Anxiety
            -  Depression signs
            -  Mental wellness
            
            **Analysis Methods:**
            -  Text patterns
            -  Voice emotions
            -  Facial expressions
            -  Real-time video
            """)
        
        # Privacy Notice
        with st.expander(" Privacy"):
            st.markdown("""
             Your data is **private** and secure
            
             Personal dashboard & history
            
             HIPAA compliant design
            
             Ethical AI practices
            """)
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 11px; padding: 10px;'>
        💚 Made with care for Mental Health Awareness<br>
        © 2025 AI for Good
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Logout button at bottom
        if st.button(" Logout", type="secondary", use_container_width=True):
            logout(db_handler)
            st.rerun()
    
    # Main Content Area - With smooth page transitions
    if selected != st.session_state.selected_page:
        st.session_state.selected_page = selected
        st.rerun()
    
    # Render selected page with smooth loading
    try:
        if st.session_state.selected_page == "Dashboard":
            dashboard_page(db_handler)
        elif st.session_state.selected_page == "Text Analysis":
            text_analysis_page(db_handler)
        elif st.session_state.selected_page == "Voice Analysis":
            voice_analysis_page(db_handler)
        elif st.session_state.selected_page == "Real-Time Emotion":
            realtime_emotion_page(db_handler)
    except Exception as e:
        st.error(f" An error occurred: {str(e)}")
        st.info("Please try refreshing the page or contact support if the issue persists.")

if __name__ == "__main__":
    main()
