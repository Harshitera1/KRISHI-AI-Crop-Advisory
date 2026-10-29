# ⚡ QUICK START GUIDE - KRISHI AI Refactored

## 🌾 Overview

KRISHI AI is a smart crop recommendation system using ML models, voice input, location-based analysis, and dual language support.

**Current Branch:** `feature/ai-upgrade`

---

## 🚀 Installation & Setup

### 1️⃣ **Install Dependencies**

```bash
# Navigate to project root
cd /Users/harshitkumar/Desktop/KRISHI/KRISHI-AI-Crop-

# Install all requirements
pip install -r requirements.txt
```

**Key packages:**
- `Flask` - Backend API
- `Streamlit` - Frontend UI
- `joblib` - ML model loading
- `streamlit-folium` - Interactive maps
- `speech_recognition` - Voice input
- `gtts` - Text-to-speech
- `pymongo` - Database

---

## 2️⃣ **Start Backend Server**

```bash
# Terminal 1 - Backend
cd backend

# Run Flask server
python main.py

# Expected output:
# * Running on http://127.0.0.1:5001
# * ML Model Loaded Successfully
```

**Ensure MongoDB is running!**

---

## 3️⃣ **Start Frontend Application**

```bash
# Terminal 2 - Frontend
cd frontend

# Run Streamlit app
streamlit run app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8502
```

---

## 🎮 **Using the Application**

### First Time Setup:
1. **Sign Up**: Create account (username + password)
2. **Log In**: Enter credentials
3. **Select Language**: English or हिंदी (sidebar)
4. **Ready!** Start getting recommendations

---

## 📍 **Two Input Methods:**

### **METHOD 1: Map-Based Location**
```
✅ Best for: Visual selection
   1. Select "Map-Based Location" from radio button
   2. Click on map to select your region
   3. System finds nearest matched location
   4. Fill crop analysis form
   5. Click "Get Recommendation"
   6. Best crop is spoken aloud with location name
```

### **METHOD 2: Voice-Based Location**
```
🎤 Best for: Farmers unfamiliar with maps
   1. Select "Voice-Based Location" from radio button
   2. Click "Listen for Voice" button
   3. Say your location: "Delhi", "Meerut", "Punjab", etc.
   4. System matches to closest location
   5. Fill crop analysis form
   6. Click "Get Recommendation"
   7. Best crop is spoken for that XYZ location
```

---

## 📊 **Features:**

### Backend Features:
- ✅ ML model (crop_model.pkl) active
- ✅ Location service with detailed database
- ✅ Voice controller for voice input handling
- ✅ Synchronous voice processing
- ✅ Both languages support (EN/HI)
- ✅ Region-based crop filtering
- ✅ Fertilizer recommendations

### Frontend Features:
- ✅ Earthy color scheme (browns, muted greens)
- ✅ Simple, clean interface
- ✅ Separated map and voice flows
- ✅ Interactive folium maps
- ✅ Top 3 crop recommendations
- ✅ Yield comparison charts
- ✅ Weather display
- ✅ Recent history dashboard
- ✅ Both languages (EN/हिंदी)

---

## 🔧 **Key Controllers:**

1. **crop_controller.py** - Main recommendation logic
2. **voice_controller.py** - Voice input handling (NEW)
3. **location_service.py** - Location database & matching (NEW)
4. **crop_service.py** - ML model predictions
5. **fertilizer_service.py** - Fertilizer recommendations

---

## 📱 **Location Database:**

Available locations for voice/map input:
- Delhi, Meerut, Punjab, Haryana, Uttar Pradesh
- Bihar, West Bengal, Jharkhand, Maharashtra
- Madhya Pradesh, Karnataka, Tamil Nadu
- Telangana, Andhra Pradesh

---

## 🐛 **Troubleshooting:**

| Issue | Solution |
|-------|----------|
| Port 5001 in use | Kill process: `lsof -ti:5001 \| xargs kill -9` |
| No microphone found | Ensure mic is connected, allow permissions |
| Voice not heard | Check language setting, speaker volume |
| Location not matched | Use major city names (Delhi, Meerut, etc.) |
| Model not loading | Verify `backend/models/crop_model.pkl` exists |
| Database connection error | Ensure MongoDB is running |

---

## 📞 **Support:**

For issues with:
- **Backend**: Check logs in `backend/logging_config.py`
- **Frontend**: Check browser console & Streamlit terminal
- **Voice**: Enable microphone permissions in system settings

---



## 🌐 **Features Overview**

### 📍 **Interactive Map**
- Real-time map selection
- Auto-detects city name
- Shows exact coordinates
- Reverse geocoding included

### 🗣️ **Voice Input**
- Speak naturally
- Auto-triggers recommendations
- No manual button click needed
- Supports English voice recognition

### 🌍 **Language Support**
- Switch between English & हिंदी (Hindi)
- All UI translates instantly
- Backend supports translations

### 📊 **Region-Based NPK**
- Varies by geographic location
- Supports 4 major regions of India
- Customized for each crop
- Based on soil and climate

### 🧪 **Smart Fertilizer Recommendations**
- Specific fertilizer types
- Exact dosages (kg/hectare)
- Region-specific values
- Detailed descriptions

### 🎨 **Premium UI**
- Modern gradient backgrounds
- Glass-morphism card design
- Smooth animations
- Responsive layout

---

## 🔍 **Testing the Features**

### Test Map Selection:
1. Login to the app
2. Look for "📍 Select Location on Map"
3. Click anywhere on the map
4. Verify location appears on right panel
5. Try clicking different cities

### Test Voice Input:
1. Ensure microphone is working
2. Click "🎤 Voice Input"
3. Speak: "Delhi loamy soil"
4. See recommendation auto-trigger
5. No need to click "Get Recommendation"

### Test Language Switching:
1. Get a recommendation in English
2. Go to sidebar settings
3. Switch to "हिंदी"
4. See all text change to Hindi
5. Switch back to verify

### Test NPK Values:
1. Select a location (e.g., Punjab)
2. Get recommendation for Wheat
3. Note NPK values shown
4. Change location to South India
5. Get Wheat recommendation again
6. See different NPK values for same crop!

### Test Fertilizer Info:
1. Get any crop recommendation
2. Scroll down to "🧪 Fertilizer Recommendation"
3. Verify shows:
   - Fertilizer type
   - NPK values for your region
   - Recommended dosage
   - Region information

---

## 📁 **Project Structure Changes**

```
KRISHI-AI-Crop-/
├── requirements.txt (UPDATED - new packages)
├── ENHANCED_FEATURES_GUIDE.md (NEW)
├── QUICK_START.md (NEW - this file)
│
├── frontend/
│   └── app.py (REWRITTEN - complete redesign)
│
├── backend/
│   ├── models/
│   │   └── npk_region_model.py (NEW - regional NPK database)
│   │
│   ├── services/
│   │   └── fertilizer_service.py (UPDATED - region-based NPK)
│   │
│   ├── controllers/
│   │   └── crop_controller.py (UPDATED - includes fertilizer)
│   │
│   └── utils/
│       └── translations.py (NEW - Hindi/English translations)
```

---

## 🐛 **Troubleshooting**

### Map Not Showing?
```
Error: "st_folium() got an unexpected keyword argument"
Solution:
  pip install --upgrade streamlit-folium folium
  streamlit run app.py --logger.level=debug
```

### Voice Recognition Not Working?
```
Error: "Could not request results from Google Speech Recognition"
Solution:
  1. Check internet connection
  2. Check microphone permissions
  3. Try speaking slowly and clearly
  4. Ensure no background noise
```

### Location Not Detected?
```
Error: "Could not reverse geocode coordinates"
Solution:
  1. Map might be zoomed too far
  2. Click in a more populated area
  3. Manually type city name in input
  4. Check internet connection
```

### Hindi Text Not Showing?
```
Error: "Mojibake or unreadable characters"
Solution:
  1. Streamlit auto-handles UTF-8, should work
  2. Try refreshing page (Cmd+Shift+R)
  3. Clear browser cache
  4. Use a modern browser (Chrome, Firefox, Safari)
```

### NPK Values Not Changing Between Regions?
```
Error: "Same NPK for different regions"
Solution:
  1. Ensure you're clicking on map to change location
  2. Backend needs to receive latitude/longitude
  3. Check browser console (F12) for errors
  4. Verify requests going to backend
```

### MongoDB Connection Error?
```
Error: "pymongo.errors.ConnectionFailure"
Solution:
  1. Start MongoDB: brew services start mongodb-community
  2. Check MongoDB running: brew services list
  3. Verify connection string in .env
  4. Restart backend server
```

---

## 🎯 **Key Features at a Glance**

| Feature | Before | After |
|---------|--------|-------|
| Location Input | Type city name | Click on interactive map |
| Voice Input | Requires manual confirmation | Auto-triggers recommendation |
| Languages | Only English | English + हिंदी + Extensible |
| NPK Adjustment | Global average | Region & crop specific |
| Fertilizer Info | Generic text | Detailed regional dosages |
| UI Design | Basic styling | Premium modern design |
| Mobile Friendly | Limited | Responsive layout |

---

## 💡 **Pro Tips**

1. **Better Map Selection**: Zoom in before clicking for precise location
2. **Faster Voice Input**: Speak clearly and pause between words
3. **Language Switching**: Switch before getting recommendations to see translated results
4. **NPK Exploration**: Try same crop in different regions to see differences
5. **Fertilizer Dosage**: Use recommended values as baseline, consult local agronomist
6. **History Tracking**: Check "📜 View History" to see past recommendations

---

## 📞 **Need Help?**

Check logs:
```bash
# Backend logs
tail -f backend.log

# Frontend logs
# Check browser console: F12 → Console tab

# Check specific errors
grep "ERROR" backend.log
```

---

## ✅ **Checklist Before Using**

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] MongoDB running
- [ ] Backend server started (port 5001)
- [ ] Frontend started (port 8501)
- [ ] Map loads without errors
- [ ] Can login/signup successfully
- [ ] Language switching works
- [ ] Microphone permission granted for voice input

---

## 🎉 **You're All Set!**

Your KRISHI AI application now has:
- ✅ Interactive map for location selection
- ✅ Voice input with auto-recommendation trigger
- ✅ Bilingual support (English & Hindi)
- ✅ Region-based NPK recommendations
- ✅ Smart fertilizer suggestions
- ✅ Premium modern UI design

**Ready to empower farmers!** 🌾🚜

---

**Last Updated**: April 30, 2026
**Version**: 2.0 (Enhanced with Maps, Voice, Language, and Regional NPK)
