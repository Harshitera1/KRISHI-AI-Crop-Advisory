import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not found in .env")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)

    # 🔥 Force connection check
    client.server_info()

    # Database
    db = client["krishi_db"]

    # Collections
    users_collection = db["users"]
    history_collection = db["history"]
    soil_collection = db["soil_data"]

    print("✅ MongoDB Atlas connected successfully")

except Exception as e:
    print("❌ MongoDB connection failed:", e)

    client = None
    db = None
    users_collection = None
    history_collection = None
    soil_collection = None