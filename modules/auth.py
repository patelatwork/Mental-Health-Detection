import streamlit as st
from database.mongodb_handler import MongoDBHandler
import os

def show_login_page(db_handler: MongoDBHandler):
    """Display login/signup page"""
    st.markdown("""
        <style>
        .auth-container {
            max-width: 500px;
            margin: 20px auto;
            padding: 40px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .auth-title {
            text-align: center;
            color: #000000;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            margin-top: 20px;
        }
        .auth-subtitle {
            text-align: center;
            color: #666666;
            font-size: 16px;
            margin-bottom: 30px;
        }
        .hero-banner {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 30px;
            overflow: hidden;
        }
        .hero-banner img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Hero Banner with Image
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="hero-banner">', unsafe_allow_html=True)
        st.markdown('<div class="auth-title">Mental Health AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-subtitle">Your Personal Wellness Companion</div>', unsafe_allow_html=True)
        # Use the actual mental health hero image
        image_path = "assets/mental_health_hero.webp"
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            st.error("Mental health hero image not found. Please ensure 'assets/mental_health_hero.webp' exists.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Title and Form Section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("### Welcome Back")
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", key="login_username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
                submit = st.form_submit_button(" Login", type="primary", use_container_width=True)
                
                if submit:
                    if username and password:
                        user = db_handler.authenticate_user(username, password)
                        if user:
                            # Set session state immediately
                            st.session_state['authenticated'] = True
                            st.session_state['user_id'] = user['user_id']
                            st.session_state['username'] = user['username']
                            st.session_state['email'] = user['email']
                            st.session_state['selected_page'] = "Dashboard"
                            # Quick rerun without waiting
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter both username and password")
        
        with tab2:
            st.markdown("###  Create Account")
            with st.form("signup_form", clear_on_submit=False):
                new_username = st.text_input("Username", key="signup_username", placeholder="Choose a username")
                new_email = st.text_input("Email", key="signup_email", placeholder="Enter your email")
                new_password = st.text_input("Password", type="password", key="signup_password", placeholder="Choose a password (min 6 chars)")
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Confirm your password")
                submit_signup = st.form_submit_button(" Create Account", type="primary", use_container_width=True)
                
                if submit_signup:
                    if new_username and new_email and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error(" Passwords do not match")
                        elif len(new_password) < 6:
                            st.error(" Password must be at least 6 characters long")
                        else:
                            success = db_handler.create_user(new_username, new_password, new_email)
                            if success:
                                st.success(" Account created successfully! Please login.")
                            else:
                                st.error(" Username already exists. Please choose a different username.")
                    else:
                        st.warning("Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def logout():
    """Logout user"""
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = None
    st.session_state['email'] = None
    st.rerun()
