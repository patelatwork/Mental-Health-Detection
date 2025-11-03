import streamlit as st
from database.mongodb_handler import MongoDBHandler
import os
import streamlit.components.v1 as components

def set_session_cookie(session_token: str):
    """Set session token in browser localStorage using JavaScript"""
    components.html(
        f"""
        <script>
            localStorage.setItem('mental_health_session', '{session_token}');
            console.log('Session token saved to localStorage');
        </script>
        """,
        height=0,
    )

def get_session_cookie():
    """Get session token from browser localStorage using JavaScript"""
    # This will inject JavaScript that reads from localStorage and sets a query param
    session_token = st.query_params.get("session_token", None)
    
    if not session_token:
        # Try to get from localStorage via query param on first load
        components.html(
            """
            <script>
                const token = localStorage.getItem('mental_health_session');
                if (token && !window.location.search.includes('session_token')) {
                    const url = new URL(window.location);
                    url.searchParams.set('session_token', token);
                    window.location.href = url.toString();
                }
            </script>
            """,
            height=0,
        )
    
    return session_token

def clear_session_cookie():
    """Clear session token from browser localStorage"""
    components.html(
        """
        <script>
            localStorage.removeItem('mental_health_session');
            console.log('Session token removed from localStorage');
        </script>
        """,
        height=0,
    )

def init_session_from_cookie(db_handler: MongoDBHandler):
    """Initialize session from localStorage if exists"""
    if db_handler is None:
        print("Debug: db_handler is None")
        return False
    
    # Skip if already authenticated in this session
    if st.session_state.get('authenticated', False):
        print("Debug: Already authenticated in session state")
        return True
    
    try:
        print("Debug: Getting session token from localStorage...")
        session_token = get_session_cookie()
        print(f"Debug: Session token: {session_token[:20] if session_token else 'None'}...")
        
        if session_token:
            # Validate session with database
            print("Debug: Validating session with database...")
            session_data = db_handler.get_session(session_token)
            
            if session_data:
                # Restore session state
                st.session_state['authenticated'] = True
                st.session_state['user_id'] = session_data['user_id']
                st.session_state['username'] = session_data['username']
                st.session_state['email'] = session_data['email']
                st.session_state['session_token'] = session_token
                print(f"✓ Session restored for user: {session_data['username']}")
                st.rerun()  # Force rerun to update UI
                return True
            else:
                # Invalid or expired session, remove from localStorage
                print("Debug: Session invalid or expired")
                clear_session_cookie()
                # Clear query param
                if "session_token" in st.query_params:
                    del st.query_params["session_token"]
                return False
    except Exception as e:
        print(f"Error initializing session from localStorage: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("Debug: No session token found")
    return False


def show_login_page(db_handler: MongoDBHandler):
    """Display login/signup page"""
    
    # Check if database is available
    if db_handler is None:
        st.error("⚠️ Database is unavailable. Please free up disk space or check MongoDB configuration.")
        st.info("**Demo Mode:** You can continue without login to explore the app's features.")
        
        if st.button("🚀 Continue in Demo Mode", type="primary", use_container_width=True):
            # Set demo session
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = 'demo_user'
            st.session_state['username'] = 'Demo User'
            st.session_state['email'] = 'demo@example.com'
            st.rerun()
        
        st.markdown("---")
        st.markdown("### How to fix:")
        st.markdown("""
        1. **Free up disk space**: MongoDB needs at least 500MB of free space
        2. **Stop MongoDB**: Run `net stop MongoDB` in PowerShell as Administrator
        3. **Clean temporary files**: Delete files from `C:\\Windows\\Temp` and `%TEMP%`
        4. **Restart MongoDB**: Run `net start MongoDB` after freeing space
        """)
        return
    
    st.markdown("""
        <style>
        /* Light background for entire page */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
        }
        
        /* Reduce top padding/margin */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        
        .auth-container {
            max-width: 500px;
            margin: 10px auto;
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
            margin-top: 0px;
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
            margin-bottom: 20px;
            margin-top: 0px;
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
        st.markdown('<div class="auth-title">Care Nest</div>', unsafe_allow_html=True)
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
                            # Create server-side session
                            session_token = db_handler.create_session(
                                user['user_id'],
                                user['username'],
                                user['email'],
                                expiry_days=30
                            )
                            
                            if session_token:
                                # Save session token to localStorage
                                set_session_cookie(session_token)
                                
                                # Also set in query params for immediate use
                                st.query_params["session_token"] = session_token
                                
                                # Set session state
                                st.session_state['authenticated'] = True
                                st.session_state['user_id'] = user['user_id']
                                st.session_state['username'] = user['username']
                                st.session_state['email'] = user['email']
                                st.session_state['session_token'] = session_token
                                st.session_state['selected_page'] = "Dashboard"
                                
                                print(f"✓ Session created for user: {user['username']}")
                                print(f"✓ Token saved to localStorage: {session_token[:20]}...")
                                
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Failed to create session. Please try again.")
                        else:
                            st.error(" Invalid username or password")
                            st.info(" **Tip:** If MongoDB is not running, use **Demo Mode** button above to continue without login.")
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
                            elif success is False:
                                st.error(" Username already exists. Please choose a different username.")
                            else:
                                st.error(" Failed to create account. Database may be unavailable.")
                                st.info(" **Tip:** Use **Demo Mode** button above to continue without creating an account.")
                    else:
                        st.warning("Please fill in all fields")

def check_authentication(db_handler: MongoDBHandler = None):
    """Check if user is authenticated"""
    # First check session state
    if st.session_state.get('authenticated', False):
        return True
    
    # If not in session state, try to restore from cookie
    if db_handler:
        return init_session_from_cookie(db_handler)
    
    return False

def logout(db_handler: MongoDBHandler = None):
    """Logout user - clear session and localStorage"""
    try:
        # Delete server-side session if exists
        if db_handler and 'session_token' in st.session_state:
            session_token = st.session_state.get('session_token')
            if session_token:
                db_handler.delete_session(session_token)
        
        # Clear localStorage
        clear_session_cookie()
        
        # Clear query param
        if "session_token" in st.query_params:
            del st.query_params["session_token"]
    except Exception as e:
        print(f"Error during logout: {str(e)}")
    
    # Clear session state
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None
    st.session_state['username'] = None
    st.session_state['email'] = None
    st.session_state['session_token'] = None
    st.rerun()
