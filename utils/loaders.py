"""
Custom loaders and UI components for Mental Health Detection
Uses Hydralit Components for professional loading animations
"""
import streamlit as st
import time
from hydralit_components import HyLoader, Loaders

def show_loader(text="Loading...", duration=2, loader_name=None):
    """
    Show a Hydralit loader with animation
    
    Args:
        text (str): Loading text to display
        duration (float): Duration in seconds (for simulation)
        loader_name (str): Type of loader from Loaders enum (default: STANDARD)
    """
    if loader_name is None:
        loader_name = Loaders.standard_loaders[0]  # Standard pulse loader
    
    with HyLoader(text, loader_name=loader_name):
        time.sleep(duration)
    
    return None


def show_success_animation(text="Success!", duration=2):
    """
    Show a success animation
    
    Args:
        text (str): Success message
        duration (float): Duration to display
    """
    success_placeholder = st.empty()
    
    success_placeholder.markdown(f"""
        <style>
        .success-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(40, 167, 69, 0.3);
            animation: fadeIn 0.5s ease-in;
        }}
        .success-checkmark {{
            width: 80px;
            height: 80px;
            margin-bottom: 20px;
        }}
        .success-checkmark path {{
            stroke: white;
            stroke-width: 6;
            stroke-dasharray: 100;
            stroke-dashoffset: 100;
            animation: checkmark 0.5s 0.3s ease-in-out forwards;
        }}
        @keyframes checkmark {{
            to {{
                stroke-dashoffset: 0;
            }}
        }}
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: scale(0.8);
            }}
            to {{
                opacity: 1;
                transform: scale(1);
            }}
        }}
        .success-text {{
            font-size: 20px;
            color: white;
            font-weight: 700;
            text-align: center;
        }}
        </style>
        <div class="success-container">
            <svg class="success-checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
                <circle cx="26" cy="26" r="25" fill="none"/>
                <path fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
            </svg>
            <div class="success-text">✓ {text}</div>
        </div>
    """, unsafe_allow_html=True)
    
    time.sleep(duration)
    success_placeholder.empty()


def show_progress_bar(text="Processing...", steps=10, step_duration=0.2):
    """
    Show an animated progress bar
    
    Args:
        text (str): Progress text
        steps (int): Number of steps
        step_duration (float): Duration per step
    """
    progress_container = st.empty()
    
    for i in range(steps + 1):
        progress = int((i / steps) * 100)
        
        progress_container.markdown(f"""
            <style>
            .progress-container {{
                padding: 30px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }}
            .progress-text {{
                font-size: 16px;
                color: #000000;
                margin-bottom: 15px;
                font-weight: 600;
            }}
            .progress-bar-bg {{
                width: 100%;
                height: 30px;
                background: #f0fdf4;
                border-radius: 15px;
                overflow: hidden;
            }}
            .progress-bar-fill {{
                height: 100%;
                background: linear-gradient(90deg, #c4f0ed 0%, #20c997 100%);
                width: {progress}%;
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 700;
            }}
            </style>
            <div class="progress-container">
                <div class="progress-text">{text}</div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill">{progress}%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        time.sleep(step_duration)
    
    return progress_container


def show_page_transition(from_page, to_page):
    """
    Show a smooth page transition animation
    
    Args:
        from_page (str): Current page name
        to_page (str): Target page name
    """
    transition_placeholder = st.empty()
    
    transition_placeholder.markdown(f"""
        <style>
        @keyframes slideOut {{
            from {{
                opacity: 1;
                transform: translateX(0);
            }}
            to {{
                opacity: 0;
                transform: translateX(-100%);
            }}
        }}
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(100%);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        .transition-container {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, #c4f0ed 0%, #f0fdf4 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            animation: slideIn 0.3s ease-in, slideOut 0.3s 0.5s ease-out;
        }}
        .transition-text {{
            font-size: 24px;
            color: #000000;
            font-weight: 700;
        }}
        .transition-icon {{
            font-size: 48px;
            margin-bottom: 20px;
        }}
        </style>
        <div class="transition-container">
            <div class="transition-icon">🔄</div>
            <div class="transition-text">Loading {to_page}...</div>
        </div>
    """, unsafe_allow_html=True)
    
    time.sleep(0.8)
    transition_placeholder.empty()


def add_loading_css():
    """
    Add global CSS for loading states with blur effect
    """
    st.markdown("""
        <style>
        /* Smooth transitions for all elements */
        * {
            transition: all 0.3s ease;
        }
        
        /* Fade in animation for new content */
        .stMarkdown, .stPlotlyChart, .stDataFrame {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Loading button styles */
        .stButton>button:disabled {
            background: linear-gradient(90deg, #c4f0ed 0%, #20c997 100%);
            background-size: 200% 100%;
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% {
                background-position: -200% 0;
            }
            100% {
                background-position: 200% 0;
            }
        }
        
        /* Skeleton loading for cards */
        .loading-skeleton {
            background: linear-gradient(90deg, #f0fdf4 25%, #c4f0ed 50%, #f0fdf4 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            border-radius: 10px;
            height: 100px;
        }
        
        @keyframes loading {
            0% {
                background-position: -200% 0;
            }
            100% {
                background-position: 200% 0;
            }
        }
        
        /* Blur effect for Hydralit loader background */
        div[data-testid="stAppViewContainer"] {
            transition: filter 0.3s ease-in-out;
        }
        
        /* Style Hydralit loader container with backdrop blur */
        .hyloader {
            backdrop-filter: blur(8px) brightness(0.95) !important;
            -webkit-backdrop-filter: blur(8px) brightness(0.95) !important;
            background: rgba(255, 255, 255, 0.85) !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            z-index: 999999 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            animation: fadeIn 0.3s ease-in !important;
        }
        
        /* Center the loader content */
        .hyloader > div {
            background: white !important;
            padding: 40px 60px !important;
            border-radius: 20px !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15) !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            gap: 20px !important;
        }
        
        /* Style the loader text */
        .hyloader h3 {
            color: #000000 !important;
            font-weight: 600 !important;
            margin: 0 !important;
            font-size: 18px !important;
        }
        
        /* Make loader animations more prominent */
        .hyloader svg,
        .hyloader div[class*="loader"] {
            transform: scale(1.2) !important;
        }
        </style>
    """, unsafe_allow_html=True)
