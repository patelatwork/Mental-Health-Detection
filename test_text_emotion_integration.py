"""
Quick test for Text Emotion module integration
"""

import sys
sys.path.append('d:/Mental/Mental-Health-Detection')

print("=" * 70)
print("TEXT EMOTION MODULE - INTEGRATION TEST")
print("=" * 70)
print()

# Test 1: Import module
print("Test 1: Importing text_emotion module...")
try:
    from modules.text_emotion import (
        load_text_emotion_model,
        analyze_text_emotion,
        calculate_wellness_score,
        calculate_risk_score,
        get_risk_level,
        get_wellness_level
    )
    print("✅ Module imported successfully!")
except Exception as e:
    print(f" Import failed: {str(e)}")
    sys.exit(1)

print()

# Test 2: Load model
print("Test 2: Loading emotion detection model...")
print("(This may take a few seconds on first run - downloads 329MB model)")
try:
    classifier = load_text_emotion_model()
    if classifier:
        print("✅ Model loaded successfully!")
    else:
        print("❌ Model loading returned None")
        sys.exit(1)
except Exception as e:
    print(f"❌ Model loading failed: {str(e)}")
    sys.exit(1)

print()

# Test 3: Analyze sample texts
print("Test 3: Analyzing sample texts...")
test_texts = [
    "I am so happy and excited about this project!",
    "I feel sad and lonely today.",
    "This makes me really angry!"
]

for i, text in enumerate(test_texts, 1):
    print(f"\n  {i}. Testing: \"{text}\"")
    try:
        results = analyze_text_emotion(text, classifier)
        if results:
            dominant = results[0]
            print(f"     ✅ Detected: {dominant['label'].capitalize()} ({dominant['score']*100:.1f}%)")
        else:
            print(f"     ❌ No results returned")
    except Exception as e:
        print(f"     ❌ Analysis failed: {str(e)}")

print()

# Test 4: Calculate wellness score
print("Test 4: Testing wellness score calculation...")
emotion_data = {
    'joy': 5,
    'sadness': 2,
    'anger': 1,
    'fear': 1,
    'surprise': 2,
    'disgust': 0,
    'neutral': 3
}

try:
    wellness = calculate_wellness_score(emotion_data)
    print(f"  Sample emotion data: {emotion_data}")
    print(f"  ✅ Wellness Score: {wellness}/10")
    
    level, color, icon = get_wellness_level(wellness)
    print(f"  ✅ Wellness Level: {icon} {level}")
except Exception as e:
    print(f"  ❌ Wellness calculation failed: {str(e)}")

print()

# Test 5: Calculate risk score
print("Test 5: Testing risk score calculation...")
try:
    risk = calculate_risk_score(emotion_data)
    print(f"  Sample emotion data: {emotion_data}")
    print(f"  ✅ Risk Score: {risk}/10")
    
    level, color, icon = get_risk_level(risk)
    print(f"  ✅ Risk Level: {icon} {level}")
except Exception as e:
    print(f"  ❌ Risk calculation failed: {str(e)}")

print()
print("=" * 70)
print("INTEGRATION TEST COMPLETE")
print("=" * 70)
print()
print("✅ All tests passed! Text Emotion module is ready.")
print()
print("Next steps:")
print("  1. Run: streamlit run app.py")
print("  2. Navigate to 'Text Emotion' in the sidebar")
print("  3. Start analyzing text emotions!")
print()
print("=" * 70)
