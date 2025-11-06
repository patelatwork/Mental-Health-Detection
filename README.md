# Mental Health Early Detection AI

An advanced AI-powered mental health detection system that analyzes text, voice, and real-time emotions to provide early indicators of mental health concerns. Built with Streamlit, TensorFlow, and modern NLP models.

---

## Table of Contents

- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Modules Overview](#modules-overview)
- [Database Configuration](#database-configuration)
- [Models Used](#models-used)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)
- [Authors](#authors)
- [Contact & Support](#contact--support)
- [Acknowledgments](#acknowledgments)
- [System Requirements](#system-requirements)
- [Updates & Changelog](#updates--changelog)

---

## Running the Application

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Webcam** (for real-time emotion detection)
- **Microphone** (optional, for voice recording)

### Step 1: Clone the Repository

```bash
git clone https://github.com/patelatwork/Mental-Health-Detection.git
cd Mental-Health-Detection
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** Installation may take several minutes due to large packages like TensorFlow and PyTorch.

### Step 4: Verify Model Files

Ensure all model files are present in the `Models/` directory:
- `best_model1_weights.h5`
- `CNN_model.json`
- `efficient-v2.xml`
- `emotion_model.h5`

#### Step 5: Run the Application

```bash
streamlit run app.py
```

### Step 6: Access the Application

- The app will automatically open in your default browser
- If not, navigate to: `http://localhost:8501`

### Step 7: Stop the Application

- Press `Ctrl + C` in the terminal

---

## Usage Guide

### Getting Started

1. **Register/Login**
   - Create a new account or login with existing credentials
   - Your session will persist across browser refreshes

2. **Navigate the Application**
   - Use the sidebar menu to switch between different analysis modules
   - Each module provides specific mental health detection capabilities

### Module Usage

#### Dashboard
- View your comprehensive mental health analytics
- Track emotion trends over time
- Review historical analysis data
- Monitor risk indicators

#### Text Analysis
- Enter or paste text for analysis
- Receive instant sentiment and emotion detection
- View polarity, subjectivity, and concern levels
- Identify critical keywords and patterns

#### Voice Analysis
- Upload an audio file (WAV, MP3, OGG)
- Or record audio directly in the browser
- Get emotion predictions from voice patterns
- View confidence scores and visualizations

#### Real-Time Emotion Detection
- Grant camera permissions when prompted
- See live emotion detection from facial expressions
- Track emotions in real-time
- Review emotion history

---

## Features

### **Authentication System**
- Secure user registration and login
- Session management with persistent authentication
- Password encryption and validation

### **Dashboard**
- Comprehensive mental health analytics
- Historical data visualization
- Emotion trend analysis
- Risk assessment metrics
- Interactive charts and graphs powered by Plotly

### **Text Analysis**
- Sentiment analysis of written text
- Emotion detection (joy, sadness, anger, fear, etc.)
- Mental health risk indicators
- Concern level assessment
- Critical keyword detection
- Polarity and subjectivity analysis
- Historical text analysis tracking

### **Voice Analysis**
- Real-time voice emotion recognition
- Audio file upload and analysis
- Emotion classification from speech patterns
- Voice-based mental health indicators
- Support for multiple audio formats (WAV, MP3, OGG)
- Spectrogram visualization
- Confidence scores for predictions

### **Real-Time Emotion Detection**
- Live webcam emotion detection
- Facial expression analysis
- Frame-by-frame emotion tracking
- Visual emotion indicators
- Real-time feedback
- Emotion history tracking

---

## Technology Stack

### **Frontend**
- **Streamlit** - Interactive web application framework
- **Plotly** - Interactive data visualizations
- **HTML/CSS** - Custom styling

### **Backend & AI/ML**
- **TensorFlow/Keras** - Deep learning models
- **Transformers (Hugging Face)** - Pre-trained NLP models
- **PyTorch** - Neural network operations
- **Librosa** - Audio processing and feature extraction
- **OpenCV** - Computer vision and facial detection
- **TextBlob** - Text sentiment analysis
- **scikit-learn** - Machine learning utilities

### **Database**
- **MongoDB Atlas** - Cloud-based NoSQL database
- **PyMongo** - MongoDB driver for Python

---

## Project Structure

```
Mental-Health-Detection/
│
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                # Streamlit app configuration
│
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore file
│
├── assets/                         # Static assets and images
│   ├── 1.png                      # UI images
│   ├── 2.png
│   ├── 3.png
│   ├── 4.png
│   ├── 5.png
│   ├── 6.png
│   ├── logo.jpg                   # Application logo
│   ├── mental_health_hero.webp    # Hero image
│   ├── 8049563.jpg                # Additional graphics
│   ├── 8049564.ai
│   ├── 8049565.eps
│   ├── Fonts.txt                  # Font resources
│   └── README.md                  # Assets documentation
│
├── data/                           # Data storage
│   └── data/                      # Nested data directory
│       ├── Audio Data/            # Voice analysis recordings
│       ├── Real Time Facial emotion data/  # Webcam emotion data
│       └── Text Analysis Data/    # Text analysis history
│
├── database/                       # Database handlers
│   ├── __init__.py
│   ├── mongodb_handler.py         # MongoDB operations
│   └── README.md                  # Database documentation
│
├── Models/                         # Pre-trained AI models
│   ├── best_model1_weights.h5     # Voice emotion model weights
│   ├── CNN_model.json             # CNN architecture
│   ├── efficient-v2.xml           # Face detection model
│   ├── emotion_model.h5           # Emotion recognition model
│   ├── encoder2.pickle            # Label encoder for emotions
│   └── scaler2.pickle             # Feature scaler
│
├── modules/                        # Feature modules
│   ├── __init__.py
│   ├── auth.py                    # Authentication module
│   ├── dashboard.py               # Dashboard and analytics
│   ├── realtime_emotion.py        # Real-time emotion detection
│   ├── text_analysis.py           # Text sentiment analysis
│   └── voice_analysis.py          # Voice emotion recognition
│
├── Notebooks/                      # Jupyter notebooks
│   ├── speech-emotion-recognition.ipynb  # Voice model training
│   ├── facial-analysis.ipynb      # Face emotion model training
│   └── Text-analysis.ipynb        # Text sentiment model training
│
└── utils/                          # Utility functions
    ├── __init__.py
    ├── loaders.py                 # Model loading utilities
    └── styling.py                 # UI styling functions
```

---

## Modules Overview

### Authentication (`modules/auth.py`)
- User registration and login
- Password hashing and validation
- Session token management
- Persistent authentication using localStorage

### Dashboard (`modules/dashboard.py`)
- User statistics and analytics
- Emotion distribution charts
- Time-series analysis
- Risk level indicators
- Interactive visualizations

### Text Analysis (`modules/text_analysis.py`)
- Sentiment classification
- Emotion detection (joy, sadness, anger, fear, surprise, love)
- Polarity and subjectivity scores
- Mental health concern detection
- Critical keyword identification
- Historical text tracking

### Voice Analysis (`modules/voice_analysis.py`)
- Audio preprocessing and feature extraction
- Mel-frequency cepstral coefficients (MFCC) analysis
- CNN-based emotion classification
- Support for multiple audio formats
- Real-time microphone recording

### Real-Time Emotion (`modules/realtime_emotion.py`)
- Webcam face detection using OpenCV
- Facial expression analysis
- Frame-by-frame emotion classification
- Live emotion tracking and visualization

---

## Database Configuration

The application uses **MongoDB Atlas** for cloud-based data storage.

### Connection Details

The MongoDB connection is configured in `app.py`:

```python
db = MongoDBHandler("mongodb+srv://username:password@cluster0.lp33q.mongodb.net/carenestt?retryWrites=true&w=majority&appName=Cluster0")
```

### Collections

- **users** - User account information
- **text_analysis** - Text analysis results
- **voice_analysis** - Voice analysis results
- **emotion_detection** - Real-time emotion data

### Fallback Mode

If database connection fails, the application runs in **demo mode** with limited functionality.

---

## Models Used

### Text Analysis
- **Hugging Face Transformers**: `j-hartmann/emotion-english-distilroberta-base`
- **TextBlob**: Sentiment polarity and subjectivity

### Voice Analysis
- **Custom CNN Model**: Trained on speech emotion datasets
- **Architecture**: Defined in `CNN_model.json`
- **Weights**: `best_model1_weights.h5`

### Real-Time Emotion Detection
- **Face Detection**: Haar Cascade Classifier (`efficient-v2.xml`)
- **Emotion Model**: CNN-based model (`emotion_model.h5`)
- **Emotions**: Angry, Disgust, Fear, Happy, Sad, Surprise, Neutral

---

## Contributing

We welcome contributions to improve the Mental Health Detection AI system!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution

- Additional emotion detection models
- Improved UI/UX design
- New analysis features
- Performance optimizations
- Documentation improvements
- Bug fixes and testing

---

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

---

## Disclaimer

**Important:** This application is designed for **educational and research purposes only**. It should **NOT** be used as a substitute for professional mental health diagnosis or treatment. 

- Always consult qualified mental health professionals for clinical assessment
- This tool provides indicators, not definitive diagnoses
- Results should be interpreted with caution and professional guidance

---

## Authors

**Team Bohar's Bit**

A 3-member team dedicated to mental health technology innovation:

- **Dhruv Patel** - [@patelatwork](https://github.com/patelatwork)
- **Vyom Nikhra** - [@vyom-nikhra](https://github.com/vyom-nikhra)
- **Vedant Maske** - [@Vedant00Maske](https://github.com/Vedant00Maske)

**Repository:** [Mental-Health-Detection](https://github.com/patelatwork/Mental-Health-Detection)

---

## Contact & Support

For questions, issues, or suggestions:
- **GitHub Issues**: [Create an issue](https://github.com/patelatwork/Mental-Health-Detection/issues)
- **Email**: 
  - Dhruv Patel: [dhruvsp2705@gmail.com](mailto:dhruvsp2705@gmail.com)
  - Vyom Nikhra: [vyomnikhra@gmail.com](mailto:vyomnikhra@gmail.com)
  - Vedant Maske: [vedantbhaskarrao.m23@iiits.in](mailto:vedantbhaskarrao.m23@iiits.in)

---

## Acknowledgments

- Hugging Face for pre-trained NLP models
- TensorFlow and Keras communities
- Streamlit for the amazing web framework
- OpenCV for computer vision tools
- MongoDB Atlas for cloud database services

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.14+, or Linux
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **Internet**: Stable connection for cloud features

### For Local Deployment
- **Python**: 3.8, 3.9, 3.10, or 3.11
- **GPU**: Optional, but recommended for faster processing (CUDA-compatible)

---

## Updates & Changelog

Stay tuned for updates and new features! Check the repository for:
- Latest releases
- Version history
- Feature roadmap
- Known issues

---

<div align="center">

**Made with care for Mental Health Awareness**

Star this repository if you find it helpful!

</div>
