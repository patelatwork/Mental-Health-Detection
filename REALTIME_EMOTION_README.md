# Real-Time Emotion Detection Integration

## Overview
This module integrates the pre-trained Emotion Detection CNN model into the Mental Health Detection application for real-time video emotion analysis.

## Features

### 📹 Real-Time Webcam Analysis
- Live emotion detection from webcam feed
- 7 emotion categories: Happy, Sad, Angry, Surprised, Fearful, Disgusted, Neutral
- Real-time confidence scores
- Frame-by-frame emotion tracking

### 📊 Comprehensive Analytics
- **Wellness Score** (0-10): Measures overall emotional well-being
- **Risk Score** (0-10): Identifies potential mental health concerns
- **Emotion Distribution**: Visual breakdown of detected emotions
- **Timeline Analysis**: Emotion changes over the session
- **Session Statistics**: Detailed metrics and insights

### 💾 Data Management
- Automatic saving to MongoDB database
- CSV export of emotion logs
- Integration with user dashboard
- Privacy-focused local processing

## How It Works

### 1. Model Architecture
The emotion detection uses a CNN model with the following architecture:
- Input: 48x48 grayscale facial images
- 4 Convolutional layers with MaxPooling
- 2 Dropout layers for regularization
- 1 Fully connected layer (1024 neurons)
- Output: 7-class softmax for emotion classification

### 2. Face Detection
- Uses Haar Cascade Classifier for face detection
- Real-time processing at ~30 FPS
- Multiple face detection support

### 3. Emotion Classification
```python
Emotion Classes:
0: Angry
1: Disgusted
2: Fearful
3: Happy
4: Neutral
5: Sad
6: Surprised
```

### 4. Scoring System

**Wellness Score Calculation:**
- Positive emotions (Happy, Neutral, Surprised) increase score
- Negative emotions (Sad, Angry, Fearful, Disgusted) decrease score
- Range: 0-10 (higher is better)

**Risk Score Calculation:**
- Weighted by emotion severity: Sad (0.45), Fearful (0.40), Angry (0.30), Disgusted (0.20)
- Only emotions >20% presence contribute
- Bonus risk for multiple negative emotions
- Range: 0-10 (higher = more concern)

## Usage

### Running the Application
```bash
# Navigate to the Mental-Health-Detection directory
cd "d:\Mental\Mental-Health-Detection"

# Run the Streamlit app
streamlit run app.py
```

### Using Real-Time Emotion Detection
1. Login to the application
2. Navigate to "Real-Time Emotion" from the sidebar
3. Click "🎥 Start Webcam" to begin detection
4. Allow browser camera permissions
5. The system will detect and display emotions in real-time
6. Click "⏹️ Stop & Analyze" to end session and view results

### Interpreting Results

**Wellness Score:**
- 7-10: Positive emotional state
- 4-6: Neutral/Mixed state
- 0-3: Concerning emotional state

**Risk Level:**
- Low (0-3.9): Minimal concern
- Moderate (4-6.9): Monitor emotions
- High (7-10): Consider professional support

## Files Structure

```
Mental-Health-Detection/
├── Models/
│   ├── emotion_model.h5              # Pre-trained emotion CNN model
│   ├── haarcascade_frontalface_default.xml  # Face detection cascade
│   └── ...
├── modules/
│   ├── realtime_emotion.py          # Real-time emotion detection module
│   ├── facial_analysis.py           # Image-based facial analysis
│   ├── voice_analysis.py            # Voice emotion analysis
│   └── ...
└── app.py                            # Main Streamlit application
```

## Technical Details

### Model Specifications
- **Input Shape**: (48, 48, 1) - Grayscale images
- **Parameters**: ~2.3M trainable parameters
- **Accuracy**: ~63% on FER-2013 dataset
- **Inference Time**: ~26-40ms per frame

### Dependencies
```python
- TensorFlow >= 2.13.0
- OpenCV >= 4.8.0
- Streamlit >= 1.28.0
- NumPy >= 1.24.0
- Pandas >= 2.0.0
- Plotly >= 5.17.0
```

## Privacy & Security

🔒 **Privacy Features:**
- All processing is done locally on your device
- No images are stored or transmitted
- Webcam access is only active during sessions
- Data saved to database is anonymized
- Option to export and delete personal data

## Troubleshooting

### Webcam Not Detected
```python
# Check camera permissions in browser
# Try different camera index if you have multiple cameras
cap = cv2.VideoCapture(1)  # Try 1, 2, etc.
```

### Model Loading Error
- Ensure `emotion_model.h5` exists in `Models/` folder
- Ensure `haarcascade_frontalface_default.xml` exists in `Models/` folder
- Check file paths are correct

### Low FPS / Lag
- Close other applications using camera
- Reduce frame processing rate
- Check system resources

## Future Enhancements

🚀 **Planned Features:**
- [ ] Emotion heatmap visualization
- [ ] Multi-face tracking
- [ ] Export video with annotations
- [ ] Custom emotion thresholds
- [ ] Advanced analytics and insights
- [ ] Integration with wearable devices

## Credits

**Original Emotion Detection Model:**
- Repository: [atulapra/Emotion-detection](https://github.com/atulapra/Emotion-detection)
- Dataset: FER-2013
- Architecture: 4-layer CNN

**Mental Health Detection Integration:**
- Integrated by: AI Assistant
- Date: November 2, 2025
- Framework: Streamlit + TensorFlow

## License

This integration follows the license of both the original Emotion-detection project and the Mental-Health-Detection project.

---

**⚠️ Medical Disclaimer:** This tool is for informational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified health providers with questions you may have regarding mental health concerns.
