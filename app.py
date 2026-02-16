from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.auth import auth_bp
from routes.curriculum import curriculum_bp
from routes.analytics import analytics_bp
from routes.ai import ai_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Database
init_db()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(curriculum_bp, url_prefix='/api/curriculum')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(ai_bp, url_prefix='/api/ai')

@app.route('/')
def home():
    return {"message": "SmartCurriculum API is running"}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
