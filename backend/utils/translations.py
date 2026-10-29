# 🌾 KRISHI AI - Multilingual Support
# Hindi and English translations

TRANSLATIONS = {
    "en": {
        # Header
        "title": "🌾 KRISHI AI",
        "subtitle": "Smart Crop Recommendation System",
        "tagline": "Empowering Farmers with Technology",

        # Auth
        "login_signup": "Login / Signup",
        "username": "Username",
        "password": "Password",
        "signup": "Signup",
        "login": "Login",
        "login_success": "Login successful",
        "login_error": "Login failed",
        "signup_success": "Signup successful",

        # Map
        "select_location": "Select Location on Map",
        "click_to_select": "Click on the map to select your location",
        "location_selected": "Location Selected ✓",
        "latitude": "Latitude",
        "longitude": "Longitude",

        # Inputs
        "soil_type": "Soil Type",
        "city": "City",
        "voice_input": "🎤 Speak Input",
        "speaking": "🎤 Speak city and soil...",
        "detected": "Detected",
        "language": "Language",

        # NPK
        "nitrogen": "Nitrogen (N)",
        "phosphorus": "Phosphorus (P)",
        "potassium": "Potassium (K)",
        "ph_level": "pH Level",
        "soil_data_auto": "🌱 Soil data auto-loaded",

        # Recommendations
        "get_recommendation": "🚀 Get Recommendation",
        "best_crop": "🌾 Best Crop",
        "top_crops": "🏆 Top 3 Crops",
        "confidence": "Confidence",

        # Weather
        "weather": "🌦 Weather",
        "temperature": "🌡 Temperature",
        "humidity": "💧 Humidity",
        "rainfall": "🌧 Rainfall",
        "condition": "☁ Condition",

        # Fertilizer
        "fertilizer": "🧪 Fertilizer Recommendation",
        "fertilizer_type": "Fertilizer Type",
        "dosage": "Recommended Dosage",
        "region": "Region",

        # History
        "view_history": "📜 View History",
        "history": "📜 History",
        "no_history": "No history found",

        # Errors
        "error": "Error",
        "success": "Success",
        "loading": "Loading...",
        "soil_types": ["Loamy", "Sandy", "Clay", "Silty", "Peaty"],
    },
    "hi": {
        # Header
        "title": "🌾 कृषि एआई",
        "subtitle": "स्मार्ट फसल सिफारिश प्रणाली",
        "tagline": "किसानों को तकनीक से सशक्त बनाना",

        # Auth
        "login_signup": "लॉगिन / साइन अप",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "signup": "साइन अप",
        "login": "लॉगिन",
        "login_success": "लॉगिन सफल",
        "login_error": "लॉगिन विफल",
        "signup_success": "साइन अप सफल",

        # Map
        "select_location": "मानचित्र पर स्थान चुनें",
        "click_to_select": "अपना स्थान चुनने के लिए मानचित्र पर क्लिक करें",
        "location_selected": "स्थान चुना गया ✓",
        "latitude": "अक्षांश",
        "longitude": "देशांतर",

        # Inputs
        "soil_type": "मिट्टी का प्रकार",
        "city": "शहर",
        "voice_input": "🎤 बोलें",
        "speaking": "🎤 शहर और मिट्टी कहें...",
        "detected": "पहचाना गया",
        "language": "भाषा",

        # NPK
        "nitrogen": "नाइट्रोजन (N)",
        "phosphorus": "फॉस्फोरस (P)",
        "potassium": "पोटेशियम (K)",
        "ph_level": "पीएच स्तर",
        "soil_data_auto": "🌱 मिट्टी डेटा स्वचालित रूप से लोड किया गया",

        # Recommendations
        "get_recommendation": "🚀 सिफारिश प्राप्त करें",
        "best_crop": "🌾 सर्वश्रेष्ठ फसल",
        "top_crops": "🏆 शीर्ष 3 फसलें",
        "confidence": "विश्वास",

        # Weather
        "weather": "🌦 मौसम",
        "temperature": "🌡 तापमान",
        "humidity": "💧 आर्द्रता",
        "rainfall": "🌧 वर्षा",
        "condition": "☁ स्थिति",

        # Fertilizer
        "fertilizer": "🧪 खाद की सिफारिश",
        "fertilizer_type": "खाद का प्रकार",
        "dosage": "अनुशंसित खुराक",
        "region": "क्षेत्र",

        # History
        "view_history": "📜 इतिहास देखें",
        "history": "📜 इतिहास",
        "no_history": "कोई इतिहास नहीं मिला",

        # Errors
        "error": "त्रुटि",
        "success": "सफल",
        "loading": "लोड हो रहा है...",
        "soil_types": ["दोमट", "बलुई", "मिट्टी", "सिल्टी", "पीटी"],
    }
}


def t(key, lang="en"):
    """
    Translate a key to the specified language
    """
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]
    elif "en" in TRANSLATIONS and key in TRANSLATIONS["en"]:
        return TRANSLATIONS["en"][key]
    else:
        return key
