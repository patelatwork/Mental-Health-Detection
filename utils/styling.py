import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: #ffffff;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 2px solid #c4f0ed;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #000000;
    }
    
    /* Sidebar Toggle Button - Make it more visible */
    button[kind="header"] {
        background-color: #c4f0ed !important;
        color: #000000 !important;
        border-radius: 8px !important;
        padding: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    button[kind="header"]:hover {
        background-color: #a8e4e0 !important;
        transform: scale(1.1) !important;
    }
    
    /* Collapsed sidebar button */
    [data-testid="collapsedControl"] {
        background-color: #c4f0ed !important;
        color: #000000 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        box-shadow: 0 4px 12px rgba(196, 240, 237, 0.4) !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        background-color: #a8e4e0 !important;
        transform: scale(1.15) !important;
        box-shadow: 0 6px 16px rgba(196, 240, 237, 0.5) !important;
    }
    
    /* Headers */
    h1 {
        color: #000000;
        font-weight: 700;
        padding-bottom: 10px;
        border-bottom: 3px solid #c4f0ed;
    }
    
    h2 {
        color: #000000;
        font-weight: 600;
    }
    
    h3 {
        color: #000000;
        font-weight: 500;
    }
    
    /* Cards and Containers */
    .element-container div.stButton > button {
        background: #c4f0ed;
        color: #000000;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(196, 240, 237, 0.3);
    }
    
    .element-container div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(196, 240, 237, 0.4);
        background: #a8e4e0;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #000000;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #000000;
        font-weight: 600;
    }
    
    /* Info Boxes */
    .stAlert {
        background-color: #f0fdf4;
        border-left: 4px solid #c4f0ed;
        border-radius: 8px;
        padding: 1rem;
        color: #000000;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background-color: white;
        border: 2px dashed #c4f0ed;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #a8e4e0;
        background-color: #f0fdf4;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid #c4f0ed;
        border-radius: 8px;
        padding: 10px;
        transition: all 0.3s ease;
        color: #000000;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #a8e4e0;
        box-shadow: 0 0 0 3px rgba(196, 240, 237, 0.1);
    }
    
    /* Select Box */
    .stSelectbox > div > div {
        border: 2px solid #c4f0ed;
        border-radius: 8px;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: #c4f0ed;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 10px 20px;
        color: #000000;
        border: 2px solid #c4f0ed;
    }
    
    .stTabs [aria-selected="true"] {
        background: #c4f0ed;
        color: #000000;
        border-color: #c4f0ed;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        border: 2px solid #c4f0ed;
        border-radius: 8px;
        color: #000000;
        font-weight: 600;
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 2px solid #c4f0ed;
        border-radius: 8px;
    }
    
    /* Success/Warning/Error Messages */
    .stSuccess {
        background-color: #d4f4dd;
        border-left: 4px solid #c4f0ed;
        color: #000000;
    }
    
    .stWarning {
        background-color: #fff4e5;
        border-left: 4px solid #ff9800;
        color: #000000;
    }
    
    .stError {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        color: #000000;
    }
    
    /* Custom Card Style */
    .custom-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(196, 240, 237, 0.15);
        margin: 10px 0;
        border: 1px solid #c4f0ed;
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(196, 240, 237, 0.25);
    }
    
    /* Risk Level Badges */
    .risk-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        margin: 5px;
    }
    
    .risk-low {
        background-color: #d4f4dd;
        color: #000000;
    }
    
    .risk-moderate {
        background-color: #fff4e5;
        color: #000000;
    }
    
    .risk-high {
        background-color: #fee2e2;
        color: #000000;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f0fdf4;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c4f0ed;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a8e4e0;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Make sidebar toggle SUPER visible */
    button[data-testid="baseButton-header"] {
        background-color: #c4f0ed !important;
        color: #000000 !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        padding: 8px !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 9999 !important;
        box-shadow: 0 4px 12px rgba(196, 240, 237, 0.6) !important;
        border: 3px solid white !important;
    }
    
    button[data-testid="baseButton-header"]:hover {
        background-color: #a8e4e0 !important;
        transform: scale(1.2) !important;
        box-shadow: 0 6px 20px rgba(196, 240, 237, 0.8) !important;
    }
    
    /* Collapsed sidebar button - MEGA visible */
    section[data-testid="stSidebarCollapsedControl"] {
        position: fixed !important;
        top: 60px !important;
        left: 10px !important;
        z-index: 9999 !important;
    }
    
    section[data-testid="stSidebarCollapsedControl"] button {
        background: #c4f0ed !important;
        color: #000000 !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 20px rgba(196, 240, 237, 0.6) !important;
        border: 3px solid white !important;
        animation: pulse 2s infinite !important;
    }
    
    section[data-testid="stSidebarCollapsedControl"] button:hover {
        background: #a8e4e0 !important;
        transform: scale(1.15) !important;
        box-shadow: 0 8px 25px rgba(196, 240, 237, 0.8) !important;
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 6px 20px rgba(196, 240, 237, 0.6);
        }
        50% {
            box-shadow: 0 6px 30px rgba(196, 240, 237, 0.9);
        }
    }
    </style>
    """, unsafe_allow_html=True)
