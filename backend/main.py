import logging
import os
import time
import uuid

from flask import Flask, g, request, jsonify
from flask_cors import CORS
from logging_config import configure_logging

from routes.user_routes import user_bp
from routes.farm_routes import farm_bp
from routes.weather_routes import weather_bp
from routes.crop_routes import crop_bp
from routes.fertilizer_routes import fertilizer_bp
from routes.auth_routes import auth_bp
from routes.soil_routes import soil_bp

from auth.auth_service import bcrypt
from routes.history_routes import history_bp
from routes.location_routes import location_bp
from models.soil_model import initialize_soil_data


# 🔥 Setup logging
configure_logging()
logger = logging.getLogger(__name__)

# ✅ Create app FIRST
app = Flask(__name__)

# 🔥 Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"], "allow_headers": ["Content-Type", "Authorization"]}})

# 🔥 Init bcrypt AFTER app
bcrypt.init_app(app)

# 🔥 Register routes
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(farm_bp, url_prefix="/api/farm")
app.register_blueprint(weather_bp, url_prefix="/api/weather")
app.register_blueprint(crop_bp, url_prefix="/api/crop")
app.register_blueprint(fertilizer_bp, url_prefix="/api/fertilizer")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(history_bp, url_prefix="/api/history")
app.register_blueprint(soil_bp, url_prefix="/api/soil")
app.register_blueprint(location_bp, url_prefix="/api/location")

# 🔥 Initialize soil data on startup
try:
    initialize_soil_data()
except Exception as e:
    logger.warning(f"Soil data initialization: {str(e)}")


# 🔥 Request logging
@app.before_request
def log_request_start():
    g.request_id = str(uuid.uuid4())
    g.request_start_time = time.time()
    logger.info(
        "Request started",
        extra={
            "event": "request_start",
            "request_id": g.request_id,
            "method": request.method,
            "path": request.path,
        },
    )

@app.after_request
def log_request_end(response):
    duration_ms = round((time.time() - g.get("request_start_time", time.time())) * 1000, 2)
    logger.info(
        "Request completed",
        extra={
            "event": "request_end",
            "request_id": g.get("request_id"),
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    response.headers["X-Request-ID"] = g.get("request_id", "")
    return response

# 🔥 Home route
@app.route("/")
def home():
    return {"msg": "Backend running 🚀"}

# 🔥 Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(
        "Unhandled exception",
        extra={
            "event": "error",
            "request_id": getattr(g, "request_id", None),
            "error": str(e)
        }
    )

    return jsonify({
        "success": False,
        "message": "Internal server error",
        "request_id": getattr(g, "request_id", None)
    }), 500

# 🔥 Run app
if __name__ == "__main__":
    logger.info(
        "Backend running",
        extra={"event": "app_startup", "status_code": 200}
    )
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")), debug=debug)