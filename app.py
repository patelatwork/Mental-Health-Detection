import os
import warnings

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

# Import analysis modules
from modules.text_analysis import text_analysis_page
from modules.voice_analysis import voice_analysis_page
from modules.facial_analysis import facial_analysis_page
from modules.dashboard import dashboard_page
from modules.auth import show_login_page, check_authentication, logout
from database.mongodb_handler import MongoDBHandler
from utils.styling import apply_custom_css

# Page Configuration
st.set_page_config(
    page_title="Mental Health Early Detection AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Initialize MongoDB connection
@st.cache_resource
def init_db():
    """Initialize database connection"""
    try:
        # You can change this connection string to your MongoDB connection
        # For local MongoDB: "mongodb://localhost:27017/"
        # For MongoDB Atlas: "mongodb+srv://username:password@cluster.mongodb.net/"
        db = MongoDBHandler("mongodb://localhost:27017/")
        return db
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

def main():
    # Initialize database
    db_handler = init_db()
    
    # Check authentication
    if not check_authentication():
        show_login_page(db_handler)
        return
    
    # Initialize session state for selected page
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "Dashboard"
    
    # Sidebar
    with st.sidebar:
        st.image("assets/logo.jpg", width=200) if st.session_state.get('show_logo', False) else None
        
        st.markdown(f"### Welcome, {st.session_state.get('username', 'User')}")
        st.markdown("Mental Health Early Detection System")
        st.markdown("---")
        
        # Logout button
        if st.button("Logout", width="stretch"):
            logout()
        
        # Navigation Menu
        selected = option_menu(
            menu_title="Analysis Type",
            options=["Dashboard", "Text Analysis", "Voice Analysis", "Facial Analysis"],
            icons=["speedometer2", "chat-text", "mic", "camera"],
            menu_icon="cast",
            default_index=["Dashboard", "Text Analysis", "Voice Analysis", "Facial Analysis"].index(st.session_state.selected_page),
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
                    "color": "#000000"
                },
                "nav-link-selected": {"background-color": "#c4f0ed", "color": "#000000"},
            }
        )
        
        # Update session state
        st.session_state.selected_page = selected
        
        st.markdown("---")
        
        # About Section
        with st.expander("About"):
            st.markdown("""
            **Mental Health AI** uses advanced machine learning to detect early signs of:
            - Stress
            - Depression
            - Anxiety
            
            Our multi-modal approach analyzes:
            - Text patterns
            - Voice emotions
            """)
        
        # Privacy Notice
        with st.expander("Privacy"):
            st.markdown("""
            - All data is processed locally
            - No data is stored permanently
            - HIPAA compliant design
            - Ethical AI practices
            """)
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #000000; font-size: 12px;'>
        Made with care for Mental Health Awareness<br>
        © 2025 AI for Good
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content Area - Show current page
    if st.session_state.selected_page == "Dashboard":
        dashboard_page(db_handler)
    elif st.session_state.selected_page == "Text Analysis":
        text_analysis_page(db_handler)
    elif st.session_state.selected_page == "Voice Analysis":
        voice_analysis_page(db_handler)
    elif st.session_state.selected_page == "Facial Analysis":
        facial_analysis_page(db_handler)

if __name__ == "__main__":
    main()
