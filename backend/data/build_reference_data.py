"""Write the district gazetteer and crop reference cards used at runtime."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

# district, state, zone, lat, lng, soil, N, P, K, ph, crops, season, aliases
ROWS = [
    ("Delhi", "Delhi", "North", 28.6139, 77.2090, "Loamy", 40, 18, 90, 7.6, ["wheat", "rice", "mustard"], "Rabi", ["new delhi", "delhi ncr"]),
    ("Amritsar", "Punjab", "North", 31.6340, 74.8723, "Loamy", 55, 22, 110, 7.5, ["wheat", "rice", "maize"], "Rabi/Kharif", ["amritsar city"]),
    ("Ludhiana", "Punjab", "North", 30.9010, 75.8573, "Loamy", 58, 24, 120, 7.6, ["wheat", "rice", "cotton", "maize"], "Rabi/Kharif", ["ludhiana city"]),
    ("Bathinda", "Punjab", "North", 30.2110, 74.9455, "Sandy", 42, 18, 95, 7.8, ["cotton", "wheat", "rice"], "Kharif/Rabi", ["bhatinda"]),
    ("Patiala", "Punjab", "North", 30.3398, 76.3869, "Loamy", 52, 21, 105, 7.4, ["wheat", "rice", "maize"], "Rabi/Kharif", []),
    ("Karnal", "Haryana", "North", 29.6857, 76.9905, "Loamy", 50, 20, 100, 7.5, ["wheat", "rice", "chickpea"], "Rabi", []),
    ("Hisar", "Haryana", "North", 29.1492, 75.7217, "Sandy", 36, 16, 80, 7.9, ["cotton", "wheat", "mustard"], "Rabi/Kharif", ["hissar"]),
    ("Rohtak", "Haryana", "North", 28.8955, 76.6066, "Loamy", 44, 18, 90, 7.6, ["wheat", "rice", "mustard"], "Rabi", []),
    ("Gurugram", "Haryana", "North", 28.4595, 77.0266, "Loamy", 38, 16, 85, 7.7, ["wheat", "mustard", "millet"], "Rabi", ["gurgaon"]),
    ("Lucknow", "Uttar Pradesh", "North", 26.8467, 80.9462, "Loamy", 48, 20, 100, 7.3, ["wheat", "rice", "lentil", "mango"], "Rabi/Kharif", []),
    ("Meerut", "Uttar Pradesh", "North", 28.9845, 77.7064, "Loamy", 46, 20, 95, 7.4, ["wheat", "sugarcane", "rice"], "Rabi/Kharif", ["meerut city"]),
    ("Kanpur", "Uttar Pradesh", "North", 26.4499, 80.3319, "Loamy", 44, 22, 100, 7.4, ["wheat", "rice", "pulses"], "Rabi/Kharif", ["kanpur nagar"]),
    ("Varanasi", "Uttar Pradesh", "North", 25.3176, 82.9739, "Loamy", 42, 18, 90, 7.2, ["rice", "wheat", "lentil"], "Kharif/Rabi", ["banaras", "kashi"]),
    ("Gorakhpur", "Uttar Pradesh", "North", 26.7606, 83.3732, "Loamy", 40, 18, 88, 7.1, ["rice", "wheat", "sugarcane"], "Kharif/Rabi", []),
    ("Agra", "Uttar Pradesh", "North", 27.1767, 78.0081, "Sandy", 34, 15, 75, 7.8, ["wheat", "mustard", "potato"], "Rabi", []),
    ("Bareilly", "Uttar Pradesh", "North", 28.3670, 79.4304, "Loamy", 45, 19, 92, 7.3, ["wheat", "rice", "sugarcane"], "Rabi/Kharif", []),
    ("Prayagraj", "Uttar Pradesh", "North", 25.4358, 81.8463, "Loamy", 40, 17, 85, 7.3, ["wheat", "rice", "pulses"], "Rabi/Kharif", ["allahabad"]),
    ("Jhansi", "Uttar Pradesh", "North", 25.4484, 78.5685, "Sandy", 32, 14, 70, 7.2, ["wheat", "chickpea", "pulses"], "Rabi", []),
    ("Dehradun", "Uttarakhand", "North", 30.3165, 78.0322, "Loamy", 38, 18, 80, 6.6, ["rice", "wheat", "maize"], "Kharif/Rabi", []),
    ("Udham Singh Nagar", "Uttarakhand", "North", 28.9875, 79.4141, "Loamy", 50, 22, 100, 7.2, ["rice", "wheat", "sugarcane"], "Kharif/Rabi", ["rudrapur"]),
    ("Nainital", "Uttarakhand", "North", 29.3803, 79.4636, "Loamy", 36, 16, 78, 6.4, ["maize", "rice", "fruit"], "Kharif", []),
    ("Jaipur", "Rajasthan", "North", 26.9124, 75.7873, "Sandy", 28, 12, 70, 7.9, ["mustard", "wheat", "pulses"], "Rabi", []),
    ("Jodhpur", "Rajasthan", "North", 26.2389, 73.0243, "Sandy", 22, 10, 60, 8.1, ["millet", "mustard", "mothbeans", "pulses"], "Kharif/Rabi", []),
    ("Kota", "Rajasthan", "North", 25.2138, 75.8648, "Clay", 40, 18, 90, 7.4, ["wheat", "soybean", "coriander"], "Rabi/Kharif", []),
    ("Sri Ganganagar", "Rajasthan", "North", 29.9038, 73.8772, "Loamy", 48, 20, 95, 7.7, ["wheat", "cotton", "mustard"], "Rabi/Kharif", ["ganganagar"]),
    ("Bikaner", "Rajasthan", "North", 28.0229, 73.3119, "Sandy", 20, 9, 55, 8.2, ["millet", "mothbeans", "mustard"], "Kharif/Rabi", []),
    ("Udaipur", "Rajasthan", "North", 24.5854, 73.7125, "Loamy", 34, 16, 75, 7.1, ["maize", "wheat", "pulses"], "Kharif/Rabi", []),
    ("Alwar", "Rajasthan", "North", 27.5530, 76.6346, "Sandy", 32, 14, 72, 7.8, ["mustard", "wheat", "millet"], "Rabi", []),
    ("Shimla", "Himachal Pradesh", "North", 31.1048, 77.1734, "Loamy", 30, 20, 80, 6.2, ["apple", "maize", "vegetables"], "Annual", []),
    ("Kangra", "Himachal Pradesh", "North", 32.2190, 76.3234, "Loamy", 34, 18, 78, 6.4, ["rice", "maize", "wheat"], "Kharif/Rabi", ["dharamshala"]),
    ("Jammu", "Jammu and Kashmir", "North", 32.7266, 74.8570, "Loamy", 36, 16, 80, 7.2, ["wheat", "rice", "maize"], "Rabi/Kharif", []),
    ("Srinagar", "Jammu and Kashmir", "North", 34.0837, 74.7973, "Loamy", 32, 18, 75, 6.8, ["rice", "maize", "apple"], "Kharif", []),
    ("Leh", "Ladakh", "North", 34.1526, 77.5771, "Sandy", 18, 10, 50, 7.6, ["barley", "vegetables"], "Summer", ["ladakh"]),
    ("Patna", "Bihar", "East", 25.5941, 85.1376, "Loamy", 46, 20, 95, 7.1, ["rice", "wheat", "maize", "lentil"], "Kharif/Rabi", []),
    ("Muzaffarpur", "Bihar", "East", 26.1209, 85.3647, "Loamy", 42, 18, 88, 7.0, ["rice", "lychee", "wheat", "maize"], "Kharif/Rabi", []),
    ("Bhagalpur", "Bihar", "East", 25.2425, 86.9842, "Loamy", 40, 17, 85, 6.9, ["rice", "wheat", "maize"], "Kharif/Rabi", []),
    ("Gaya", "Bihar", "East", 24.7955, 84.9994, "Loamy", 38, 16, 80, 7.0, ["rice", "wheat", "pulses"], "Kharif/Rabi", []),
    ("Purnia", "Bihar", "East", 25.7771, 87.4753, "Loamy", 44, 18, 90, 6.8, ["rice", "maize", "jute"], "Kharif", []),
    ("Kolkata", "West Bengal", "East", 22.5726, 88.3639, "Clay", 50, 24, 110, 6.7, ["rice", "jute", "vegetables"], "Kharif", ["calcutta"]),
    ("Bardhaman", "West Bengal", "East", 23.2324, 87.8615, "Loamy", 48, 22, 100, 6.6, ["rice", "potato", "jute"], "Kharif/Rabi", ["burdwan"]),
    ("Nadia", "West Bengal", "East", 23.4009, 88.5014, "Loamy", 46, 20, 95, 6.7, ["rice", "jute", "lentil"], "Kharif", ["krishnanagar"]),
    ("Malda", "West Bengal", "East", 25.0108, 88.1411, "Loamy", 42, 18, 88, 6.6, ["mango", "rice", "jute"], "Annual", []),
    ("Darjeeling", "West Bengal", "East", 27.0360, 88.2627, "Loamy", 36, 16, 70, 5.8, ["tea", "maize", "vegetables"], "Annual", []),
    ("Ranchi", "Jharkhand", "East", 23.3441, 85.3096, "Loamy", 34, 15, 70, 6.2, ["rice", "maize", "pulses"], "Kharif", []),
    ("Dhanbad", "Jharkhand", "East", 23.7957, 86.4304, "Loamy", 32, 14, 68, 6.3, ["rice", "maize", "vegetables"], "Kharif", []),
    ("Bhubaneswar", "Odisha", "East", 20.2961, 85.8245, "Loamy", 40, 16, 80, 6.4, ["rice", "pulses", "vegetables"], "Kharif", []),
    ("Cuttack", "Odisha", "East", 20.4625, 85.8830, "Clay", 44, 18, 85, 6.3, ["rice", "jute", "pulses"], "Kharif", []),
    ("Sambalpur", "Odisha", "East", 21.4669, 83.9756, "Loamy", 38, 15, 75, 6.2, ["rice", "pulses", "oilseeds"], "Kharif", []),
    ("Balasore", "Odisha", "East", 21.4942, 86.9335, "Clay", 42, 17, 82, 6.4, ["rice", "jute", "vegetables"], "Kharif", ["baleswar"]),
    ("Kamrup", "Assam", "East", 26.1445, 91.7362, "Clay", 40, 16, 78, 5.6, ["rice", "jute", "vegetables"], "Kharif", ["guwahati"]),
    ("Jorhat", "Assam", "East", 26.7509, 94.2037, "Loamy", 38, 15, 72, 5.4, ["rice", "tea", "vegetables"], "Kharif", []),
    ("Dibrugarh", "Assam", "East", 27.4728, 94.9120, "Loamy", 36, 14, 70, 5.3, ["rice", "tea"], "Kharif", []),
    ("West Tripura", "Tripura", "East", 23.8315, 91.2868, "Loamy", 36, 15, 74, 5.7, ["rice", "rubber", "vegetables"], "Kharif", ["agartala"]),
    ("Imphal West", "Manipur", "East", 24.8170, 93.9368, "Loamy", 34, 14, 70, 5.8, ["rice", "vegetables"], "Kharif", ["imphal"]),
    ("East Khasi Hills", "Meghalaya", "East", 25.5788, 91.8933, "Loamy", 30, 14, 65, 5.5, ["rice", "potato", "maize"], "Kharif", ["shillong"]),
    ("Aizawl", "Mizoram", "East", 23.7271, 92.7176, "Loamy", 28, 12, 60, 5.6, ["rice", "maize", "vegetables"], "Kharif", []),
    ("Kohima", "Nagaland", "East", 25.6751, 94.1086, "Loamy", 28, 12, 58, 5.5, ["rice", "maize", "vegetables"], "Kharif", []),
    ("Papum Pare", "Arunachal Pradesh", "East", 27.0844, 93.6053, "Loamy", 26, 12, 55, 5.6, ["rice", "maize"], "Kharif", ["itanagar"]),
    ("Gangtok", "Sikkim", "East", 27.3389, 88.6065, "Loamy", 30, 16, 68, 5.7, ["maize", "rice", "cardamom"], "Kharif", []),
    ("Bhopal", "Madhya Pradesh", "Central", 23.2599, 77.4126, "Loamy", 40, 22, 80, 7.2, ["wheat", "chickpea", "soybean"], "Rabi/Kharif", []),
    ("Indore", "Madhya Pradesh", "Central", 22.7196, 75.8577, "Clay", 42, 24, 85, 7.4, ["soybean", "wheat", "chickpea"], "Kharif/Rabi", []),
    ("Jabalpur", "Madhya Pradesh", "Central", 23.1815, 79.9864, "Loamy", 38, 18, 75, 7.0, ["rice", "wheat", "pulses"], "Kharif/Rabi", []),
    ("Gwalior", "Madhya Pradesh", "Central", 26.2183, 78.1828, "Loamy", 36, 16, 72, 7.3, ["wheat", "mustard", "pulses"], "Rabi", []),
    ("Sagar", "Madhya Pradesh", "Central", 23.8388, 78.7378, "Clay", 34, 16, 70, 7.1, ["wheat", "chickpea", "soybean"], "Rabi/Kharif", []),
    ("Narmadapuram", "Madhya Pradesh", "Central", 22.7519, 77.7289, "Loamy", 38, 18, 76, 7.0, ["wheat", "soybean", "pulses"], "Rabi/Kharif", ["hoshangabad"]),
    ("Raipur", "Chhattisgarh", "Central", 21.2514, 81.6296, "Loamy", 40, 16, 78, 6.6, ["rice", "pulses"], "Kharif", []),
    ("Durg", "Chhattisgarh", "Central", 21.1904, 81.2849, "Loamy", 38, 15, 74, 6.5, ["rice", "pulses"], "Kharif", []),
    ("Bilaspur", "Chhattisgarh", "Central", 22.0797, 82.1409, "Loamy", 36, 15, 72, 6.5, ["rice", "wheat", "pulses"], "Kharif/Rabi", []),
    ("Pune", "Maharashtra", "Central", 18.5204, 73.8567, "Loamy", 36, 16, 70, 7.2, ["sugarcane", "jowar", "vegetables", "grapes"], "Kharif/Rabi", []),
    ("Nagpur", "Maharashtra", "Central", 21.1458, 79.0882, "Clay", 40, 18, 80, 7.0, ["cotton", "soybean", "orange", "pigeonpeas"], "Kharif", []),
    ("Nashik", "Maharashtra", "Central", 19.9975, 73.7898, "Loamy", 34, 16, 68, 7.1, ["grapes", "onion", "maize"], "Annual", []),
    ("Chhatrapati Sambhajinagar", "Maharashtra", "Central", 19.8762, 75.3433, "Clay", 38, 17, 74, 7.3, ["cotton", "pigeonpeas", "maize"], "Kharif", ["aurangabad"]),
    ("Amravati", "Maharashtra", "Central", 20.9374, 77.7796, "Clay", 40, 18, 78, 7.2, ["cotton", "soybean", "pigeonpeas", "orange"], "Kharif", []),
    ("Kolhapur", "Maharashtra", "Central", 16.7050, 74.2433, "Loamy", 42, 18, 80, 6.8, ["sugarcane", "rice", "jowar"], "Annual", []),
    ("Mumbai", "Maharashtra", "Central", 19.0760, 72.8777, "Sandy", 30, 14, 60, 7.0, ["vegetables", "rice"], "Kharif", ["bombay"]),
    ("Ahmedabad", "Gujarat", "Central", 23.0225, 72.5714, "Sandy", 32, 14, 65, 7.6, ["cotton", "wheat", "castor"], "Kharif/Rabi", ["ahmedabad city"]),
    ("Rajkot", "Gujarat", "Central", 22.3039, 70.8022, "Clay", 36, 16, 70, 7.8, ["cotton", "groundnut", "wheat"], "Kharif/Rabi", []),
    ("Surat", "Gujarat", "Central", 21.1702, 72.8311, "Clay", 40, 18, 78, 7.2, ["sugarcane", "banana", "rice"], "Annual", []),
    ("Vadodara", "Gujarat", "Central", 22.3072, 73.1812, "Loamy", 36, 16, 72, 7.4, ["cotton", "tobacco", "banana"], "Kharif", ["baroda"]),
    ("Junagadh", "Gujarat", "Central", 21.5222, 70.4579, "Clay", 34, 16, 68, 7.6, ["groundnut", "cotton", "mango"], "Kharif", []),
    ("Kachchh", "Gujarat", "Central", 23.2420, 69.6669, "Sandy", 22, 10, 55, 8.0, ["cotton", "castor", "dates"], "Kharif", ["bhuj", "kutch"]),
    ("Bengaluru", "Karnataka", "South", 12.9716, 77.5946, "Sandy", 34, 15, 65, 6.4, ["ragi", "maize", "vegetables"], "Kharif", ["bangalore", "bengaluru urban"]),
    ("Belagavi", "Karnataka", "South", 15.8497, 74.4977, "Loamy", 40, 18, 75, 7.0, ["sugarcane", "maize", "jowar", "cotton"], "Kharif/Rabi", ["belgaum"]),
    ("Mysuru", "Karnataka", "South", 12.2958, 76.6394, "Loamy", 36, 16, 70, 6.6, ["rice", "ragi", "sugarcane"], "Kharif", ["mysore"]),
    ("Raichur", "Karnataka", "South", 16.2120, 77.3566, "Clay", 38, 16, 72, 7.4, ["rice", "cotton", "pigeonpeas"], "Kharif", []),
    ("Dharwad", "Karnataka", "South", 15.4589, 75.0078, "Loamy", 36, 16, 68, 6.8, ["jowar", "cotton", "maize", "chilli"], "Kharif", []),
    ("Shivamogga", "Karnataka", "South", 13.9299, 75.5681, "Loamy", 34, 14, 64, 6.2, ["rice", "arecanut", "maize"], "Kharif", ["shimoga"]),
    ("Chennai", "Tamil Nadu", "South", 13.0827, 80.2707, "Sandy", 30, 14, 60, 7.0, ["rice", "groundnut", "vegetables"], "Kharif", ["madras"]),
    ("Coimbatore", "Tamil Nadu", "South", 11.0168, 76.9558, "Loamy", 38, 16, 72, 7.1, ["cotton", "coconut", "maize"], "Kharif/Rabi", []),
    ("Madurai", "Tamil Nadu", "South", 9.9252, 78.1198, "Loamy", 34, 15, 66, 7.2, ["rice", "cotton", "banana"], "Kharif", []),
    ("Thanjavur", "Tamil Nadu", "South", 10.7870, 79.1378, "Clay", 42, 18, 80, 6.8, ["rice", "pulses", "coconut"], "Kharif", ["tanjore"]),
    ("Salem", "Tamil Nadu", "South", 11.6643, 78.1460, "Loamy", 32, 14, 62, 7.0, ["mango", "tapioca", "maize"], "Annual", []),
    ("Hyderabad", "Telangana", "South", 17.3850, 78.4867, "Loamy", 36, 16, 70, 7.0, ["cotton", "rice", "maize"], "Kharif", []),
    ("Warangal", "Telangana", "South", 17.9689, 79.5941, "Clay", 40, 18, 76, 7.1, ["rice", "cotton", "maize", "chilli"], "Kharif", ["hanamkonda"]),
    ("Nizamabad", "Telangana", "South", 18.6725, 78.0941, "Clay", 38, 16, 72, 7.0, ["rice", "turmeric", "maize"], "Kharif", []),
    ("Karimnagar", "Telangana", "South", 18.4386, 79.1288, "Loamy", 36, 16, 70, 6.9, ["rice", "cotton", "maize"], "Kharif", []),
    ("NTR", "Andhra Pradesh", "South", 16.5062, 80.6480, "Loamy", 40, 18, 78, 7.2, ["rice", "chilli", "cotton"], "Kharif", ["vijayawada"]),
    ("Guntur", "Andhra Pradesh", "South", 16.3067, 80.4365, "Clay", 42, 18, 80, 7.4, ["cotton", "chilli", "rice"], "Kharif", []),
    ("Visakhapatnam", "Andhra Pradesh", "South", 17.6868, 83.2185, "Loamy", 34, 14, 64, 6.6, ["rice", "sugarcane", "cashew"], "Kharif", ["vizag"]),
    ("Anantapur", "Andhra Pradesh", "South", 14.6819, 77.6006, "Sandy", 28, 12, 58, 7.6, ["groundnut", "pigeonpeas", "castor"], "Kharif", ["anantapuramu"]),
    ("Tirupati", "Andhra Pradesh", "South", 13.6288, 79.4192, "Loamy", 32, 14, 62, 6.8, ["rice", "groundnut", "sugarcane"], "Kharif", ["chittoor"]),
    ("Thiruvananthapuram", "Kerala", "South", 8.5241, 76.9366, "Loamy", 32, 14, 70, 5.8, ["coconut", "rice", "banana"], "Annual", ["trivandrum"]),
    ("Thrissur", "Kerala", "South", 10.5276, 76.2144, "Loamy", 34, 15, 72, 5.7, ["coconut", "rice", "banana"], "Annual", ["trichur"]),
    ("Palakkad", "Kerala", "South", 10.7867, 76.6548, "Loamy", 36, 16, 74, 6.2, ["rice", "coconut", "banana"], "Kharif", ["palghat"]),
    ("Alappuzha", "Kerala", "South", 9.4981, 76.3388, "Clay", 34, 14, 70, 5.5, ["rice", "coconut"], "Kharif", ["alleppey"]),
    ("North Goa", "Goa", "South", 15.4909, 73.8278, "Loamy", 32, 14, 64, 6.0, ["rice", "coconut", "cashew"], "Kharif", ["panaji", "goa"]),
    ("South Andaman", "Andaman and Nicobar Islands", "South", 11.6234, 92.7265, "Loamy", 30, 12, 60, 5.8, ["coconut", "rice", "arecanut"], "Annual", ["port blair"]),
    ("Puducherry", "Puducherry", "South", 11.9416, 79.8083, "Sandy", 32, 14, 62, 6.8, ["rice", "coconut", "pulses"], "Kharif", ["pondicherry"]),
]

TRAINING = {
    "apple": {"N": 20.8, "P": 134.2, "K": 199.9, "temperature": 22.6, "humidity": 92.3, "ph": 5.9, "rainfall": 112.7},
    "banana": {"N": 100.2, "P": 82.0, "K": 50.0, "temperature": 27.4, "humidity": 80.4, "ph": 6.0, "rainfall": 104.6},
    "blackgram": {"N": 40.0, "P": 67.5, "K": 19.2, "temperature": 30.0, "humidity": 65.1, "ph": 7.1, "rainfall": 67.9},
    "chickpea": {"N": 40.1, "P": 67.8, "K": 79.9, "temperature": 18.9, "humidity": 16.9, "ph": 7.3, "rainfall": 80.1},
    "coconut": {"N": 22.0, "P": 16.9, "K": 30.6, "temperature": 27.4, "humidity": 94.8, "ph": 6.0, "rainfall": 175.7},
    "coffee": {"N": 101.2, "P": 28.7, "K": 29.9, "temperature": 25.5, "humidity": 58.9, "ph": 6.8, "rainfall": 158.1},
    "cotton": {"N": 117.8, "P": 46.2, "K": 19.6, "temperature": 24.0, "humidity": 79.8, "ph": 6.9, "rainfall": 80.4},
    "grapes": {"N": 23.2, "P": 132.5, "K": 200.1, "temperature": 23.8, "humidity": 81.9, "ph": 6.0, "rainfall": 69.6},
    "jute": {"N": 78.4, "P": 46.9, "K": 40.0, "temperature": 25.0, "humidity": 79.6, "ph": 6.7, "rainfall": 174.8},
    "kidneybeans": {"N": 20.8, "P": 67.5, "K": 20.1, "temperature": 20.1, "humidity": 21.6, "ph": 5.7, "rainfall": 105.9},
    "lentil": {"N": 18.8, "P": 68.4, "K": 19.4, "temperature": 24.5, "humidity": 64.8, "ph": 6.9, "rainfall": 45.7},
    "maize": {"N": 77.8, "P": 48.4, "K": 19.8, "temperature": 22.4, "humidity": 65.1, "ph": 6.2, "rainfall": 84.8},
    "mango": {"N": 20.1, "P": 27.2, "K": 29.9, "temperature": 31.2, "humidity": 50.2, "ph": 5.8, "rainfall": 94.7},
    "mothbeans": {"N": 21.4, "P": 48.0, "K": 20.2, "temperature": 28.2, "humidity": 53.2, "ph": 6.8, "rainfall": 51.2},
    "mungbean": {"N": 21.0, "P": 47.3, "K": 19.9, "temperature": 28.5, "humidity": 85.5, "ph": 6.7, "rainfall": 48.4},
    "muskmelon": {"N": 100.3, "P": 17.7, "K": 50.1, "temperature": 28.7, "humidity": 92.3, "ph": 6.4, "rainfall": 24.7},
    "orange": {"N": 19.6, "P": 16.6, "K": 10.0, "temperature": 22.8, "humidity": 92.2, "ph": 7.0, "rainfall": 110.5},
    "papaya": {"N": 49.9, "P": 59.0, "K": 50.0, "temperature": 33.7, "humidity": 92.4, "ph": 6.7, "rainfall": 142.6},
    "pigeonpeas": {"N": 20.7, "P": 67.7, "K": 20.3, "temperature": 27.7, "humidity": 48.1, "ph": 5.8, "rainfall": 149.5},
    "pomegranate": {"N": 18.9, "P": 18.8, "K": 40.2, "temperature": 21.8, "humidity": 90.1, "ph": 6.4, "rainfall": 107.5},
    "rice": {"N": 79.9, "P": 47.6, "K": 39.9, "temperature": 23.7, "humidity": 82.3, "ph": 6.4, "rainfall": 236.2},
    "watermelon": {"N": 99.4, "P": 17.0, "K": 50.2, "temperature": 25.6, "humidity": 85.2, "ph": 6.5, "rainfall": 50.8},
}

# yield_low/high are indicative tonnes per hectare of the usual harvested form.
# msp is INR per quintal from the 2024-25 CACP schedule where a crop has an MSP.
# Null MSP means the crop is not on that schedule.
CARDS = {
    "rice": {"season": "Kharif", "yield_low": 3.5, "yield_high": 6.0, "yield_unit": "t/ha paddy", "msp_inr_per_quintal": 2300, "msp_note": "Paddy (common), 2024-25 CACP reference", "states": ["West Bengal", "Uttar Pradesh", "Punjab", "Andhra Pradesh", "Telangana", "Odisha", "Chhattisgarh", "Bihar"], "challenges": ["Standing water and blast risk in humid weeks", "Needs a reliable irrigation or monsoon window", "Excess nitrogen delays maturity and invites pests"]},
    "maize": {"season": "Kharif/Rabi", "yield_low": 2.5, "yield_high": 5.5, "yield_unit": "t/ha grain", "msp_inr_per_quintal": 2225, "msp_note": "Maize, 2024-25 CACP reference", "states": ["Karnataka", "Madhya Pradesh", "Bihar", "Tamil Nadu", "Maharashtra"], "challenges": ["Fall armyworm in the early whorl stage", "Moisture stress at tasselling cuts grain set", "Stored grain needs drying to avoid mould"]},
    "chickpea": {"season": "Rabi", "yield_low": 0.8, "yield_high": 1.6, "yield_unit": "t/ha grain", "msp_inr_per_quintal": 5440, "msp_note": "Gram, 2024-25 CACP reference", "states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh"], "challenges": ["Wilt and pod borer in warm dry spells", "Waterlogging at sowing", "Frost at flowering in the north"]},
    "kidneybeans": {"season": "Kharif/Rabi", "yield_low": 1.0, "yield_high": 1.8, "yield_unit": "t/ha grain", "msp_inr_per_quintal": None, "msp_note": "No separate CACP MSP. Local market price varies by grade.", "states": ["Himachal Pradesh", "Uttarakhand", "Jammu and Kashmir", "Maharashtra"], "challenges": ["Cool-season crop, poor fit for hot plains", "Anthracnose in wet weather", "Needs well drained soil"]},
    "pigeonpeas": {"season": "Kharif", "yield_low": 0.8, "yield_high": 1.5, "yield_unit": "t/ha grain", "msp_inr_per_quintal": 7550, "msp_note": "Tur (arhar), 2024-25 CACP reference", "states": ["Maharashtra", "Karnataka", "Madhya Pradesh", "Uttar Pradesh", "Gujarat"], "challenges": ["Pod borer and wilt", "Long duration ties up the field", "Flower drop if rain fails at pod set"]},
    "mothbeans": {"season": "Kharif", "yield_low": 0.4, "yield_high": 0.8, "yield_unit": "t/ha grain", "msp_inr_per_quintal": None, "msp_note": "No separate CACP MSP. Treated as a dryland pulse in local markets.", "states": ["Rajasthan", "Gujarat", "Haryana", "Maharashtra"], "challenges": ["Very low yield if the monsoon misses", "Yellow mosaic in humid pockets", "Poor price discovery outside dry districts"]},
    "mungbean": {"season": "Kharif/Summer", "yield_low": 0.5, "yield_high": 1.2, "yield_unit": "t/ha grain", "msp_inr_per_quintal": 8682, "msp_note": "Moong, 2024-25 CACP reference", "states": ["Rajasthan", "Maharashtra", "Andhra Pradesh", "Odisha", "Bihar"], "challenges": ["Yellow mosaic virus", "Short window before the next rain", "Pod shattering if harvest is late"]},
    "blackgram": {"season": "Kharif", "yield_low": 0.5, "yield_high": 1.0, "yield_unit": "t/ha grain", "msp_inr_per_quintal": 7400, "msp_note": "Urad, 2024-25 CACP reference", "states": ["Madhya Pradesh", "Uttar Pradesh", "Andhra Pradesh", "Tamil Nadu", "Rajasthan"], "challenges": ["Yellow mosaic and powdery mildew", "Waterlogging", "Uneven maturity at harvest"]},
    "lentil": {"season": "Rabi", "yield_low": 0.8, "yield_high": 1.4, "yield_unit": "t/ha grain", "msp_inr_per_quintal": 6425, "msp_note": "Masur, 2024-25 CACP reference", "states": ["Madhya Pradesh", "Uttar Pradesh", "Bihar", "West Bengal"], "challenges": ["Wilt and rust", "Late sowing after rice delays maturity into heat", "Needs a firm seedbed after paddy"]},
    "pomegranate": {"season": "Annual", "yield_low": 8.0, "yield_high": 15.0, "yield_unit": "t/ha fruit", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. Orchard price depends on grade and season.", "states": ["Maharashtra", "Karnataka", "Gujarat", "Andhra Pradesh"], "challenges": ["Bacterial blight", "Fruit cracking if irrigation swings", "Several years before full bearing"]},
    "banana": {"season": "Annual", "yield_low": 30.0, "yield_high": 45.0, "yield_unit": "t/ha fruit", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. Local wholesale price moves with supply.", "states": ["Tamil Nadu", "Maharashtra", "Gujarat", "Andhra Pradesh"], "challenges": ["Wind lodging", "Panama wilt and sigatoka", "Needs steady moisture and mulch"]},
    "mango": {"season": "Annual", "yield_low": 8.0, "yield_high": 15.0, "yield_unit": "t/ha fruit", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. Price is seasonal and variety-specific.", "states": ["Uttar Pradesh", "Andhra Pradesh", "Bihar", "Karnataka", "Gujarat"], "challenges": ["Alternate bearing", "Hopper and powdery mildew at flowering", "Storm loss of immature fruit"]},
    "grapes": {"season": "Annual", "yield_low": 15.0, "yield_high": 25.0, "yield_unit": "t/ha fruit", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. Price depends on table or raisin grade.", "states": ["Maharashtra", "Karnataka"], "challenges": ["Downy mildew in wet weather", "High potassium demand, often above the form limit of 150", "Needs trellis, pruning, and reliable water"]},
    "watermelon": {"season": "Summer", "yield_low": 20.0, "yield_high": 35.0, "yield_unit": "t/ha fruit", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. A short-season market crop.", "states": ["Uttar Pradesh", "Karnataka", "Andhra Pradesh", "Maharashtra"], "challenges": ["Needs well drained sand and steady water", "Fruit fly and mildew", "A glut can collapse the local price"]},
    "muskmelon": {"season": "Summer", "yield_low": 15.0, "yield_high": 25.0, "yield_unit": "t/ha fruit", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. A short-season market crop.", "states": ["Uttar Pradesh", "Punjab", "Rajasthan", "Maharashtra"], "challenges": ["Very low rainfall fit, so irrigation is essential", "Powdery mildew", "Short shelf life after harvest"]},
    "apple": {"season": "Annual", "yield_low": 8.0, "yield_high": 15.0, "yield_unit": "t/ha fruit", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. A temperate orchard crop.", "states": ["Jammu and Kashmir", "Himachal Pradesh", "Uttarakhand"], "challenges": ["Needs winter chill, a poor fit for the plains", "Training-table potassium is often above 150, which this form cannot send", "Scab and hail", "Several years before bearing"]},
    "orange": {"season": "Annual", "yield_low": 10.0, "yield_high": 20.0, "yield_unit": "t/ha fruit", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. Includes mandarin-type orchards in local trade.", "states": ["Maharashtra", "Madhya Pradesh", "Punjab", "Rajasthan"], "challenges": ["Citrus decline and phytophthora", "Needs drainage", "Alternate bearing in some varieties"]},
    "papaya": {"season": "Annual", "yield_low": 40.0, "yield_high": 70.0, "yield_unit": "t/ha fruit", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. A short-lived orchard crop.", "states": ["Andhra Pradesh", "Gujarat", "Karnataka", "Maharashtra"], "challenges": ["Papaya ringspot virus", "Waterlogging kills the root", "Wind damage to the stem"]},
    "coconut": {"season": "Annual", "yield_low": 1.5, "yield_high": 2.5, "yield_unit": "t/ha copra equivalent", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP for coconut. Copra prices are announced separately and vary by centre.", "states": ["Kerala", "Tamil Nadu", "Karnataka", "Andhra Pradesh"], "challenges": ["Root wilt and rhinoceros beetle", "Several years to bearing", "Price cycles on copra"]},
    "cotton": {"season": "Kharif", "yield_low": 1.5, "yield_high": 2.5, "yield_unit": "t/ha seed cotton", "msp_inr_per_quintal": 7121, "msp_note": "Medium staple cotton, 2024-25 CACP reference", "states": ["Gujarat", "Maharashtra", "Telangana", "Karnataka", "Haryana", "Punjab"], "challenges": ["Pink bollworm", "Needs a dry picking window", "High nitrogen demand within the 0 to 150 form range"]},
    "jute": {"season": "Kharif", "yield_low": 2.2, "yield_high": 3.2, "yield_unit": "t/ha fibre", "msp_inr_per_quintal": 5335, "msp_note": "Jute, 2024-25 CACP reference", "states": ["West Bengal", "Bihar", "Assam", "Odisha"], "challenges": ["Needs retting water after harvest", "Waterlogging of the seedling", "Fibre quality drops if harvest is late"]},
    "coffee": {"season": "Annual", "yield_low": 0.6, "yield_high": 1.2, "yield_unit": "t/ha clean coffee", "msp_inr_per_quintal": None, "msp_note": "No CACP MSP. Coffee Board and export prices vary by grade.", "states": ["Karnataka", "Kerala", "Tamil Nadu"], "challenges": ["Needs shade and a hill climate", "White stem borer and leaf rust", "Not a fit for open plains"]},
}


def _jitter(name, base, spread, low, high):
    shift = (sum(ord(char) for char in name) % (spread * 2 + 1)) - spread
    return max(low, min(high, base + shift))


def extra_profiles():
    """Towns and districts added so a village is nearer a known profile."""
    import importlib.util

    path = Path(__file__).with_name("extra_places.py")
    spec = importlib.util.spec_from_file_location("extra_places", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    EXTRA = module.EXTRA
    STATE_PROFILES = module.STATE_PROFILES

    rows = []
    for name, state, lat, lng in EXTRA:
        profile = STATE_PROFILES.get(state)
        if not profile:
            continue
        zone, soil, nitrogen, phosphorus, potassium, ph, crops, season = profile
        rows.append((
            name,
            state,
            zone,
            lat,
            lng,
            soil,
            _jitter(name, nitrogen, 4, 8, 140),
            _jitter(name + "p", phosphorus, 3, 6, 80),
            _jitter(name + "k", potassium, 6, 20, 140),
            round(_jitter(name + "h", int(ph * 10), 2, 52, 84) / 10, 1),
            crops,
            season,
            [],
        ))
    return rows


def main():
    districts = []
    seen = set()
    for row in list(ROWS) + extra_profiles():
        district, state, zone, lat, lng, soil, n, p, k, ph, crops, season, aliases = row
        key = district.lower()
        if key in seen:
            continue
        seen.add(key)
        districts.append({
            "district": district,
            "state": state,
            "zone": zone,
            "lat": lat,
            "lng": lng,
            "soil": soil,
            "N": n,
            "P": p,
            "K": k,
            "ph": ph,
            "crops": crops,
            "season": season,
            "aliases": aliases,
        })
    gazetteer = {
        "note": "Reference profiles for nearest-land matching. Nutrient values are typical planning estimates, not a soil test for a field.",
        "distance_note_km": {"local": 40, "near": 150},
        "districts": districts,
    }
    cards = {}
    for name, card in CARDS.items():
        # Coconut must not inherit the jute MSP. The draft note above is corrected here.
        if name == "coconut":
            card = {
                **card,
                "msp_inr_per_quintal": None,
                "msp_note": "No CACP MSP for coconut. Copra and ball copra prices are announced separately and vary by centre.",
            }
        cards[name] = {
            **card,
            "training_profile": TRAINING[name],
            "price_disclaimer": "Indicative reference only. This is not a live mandi rate. Confirm the current government notification and the local market before a sale.",
        }
    (OUT / "district_gazetteer.json").write_text(json.dumps(gazetteer, indent=2), encoding="utf-8")
    (OUT / "crop_cards.json").write_text(json.dumps({"crops": cards}, indent=2), encoding="utf-8")
    print(f"districts={len(districts)} crops={len(cards)}")


if __name__ == "__main__":
    main()
