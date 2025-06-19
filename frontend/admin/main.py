"""
MFG Drone Admin Frontend
管理者用フロントエンド - 物体学習、ドローン制御、追跡開始/停止
"""

from flask import Flask, render_template
import os
import logging

# Import blueprints
from routes import dashboard_bp, drone_control_bp, ai_tracking_bp, monitoring_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(drone_control_bp)
    app.register_blueprint(ai_tracking_bp)
    app.register_blueprint(monitoring_bp)
    
    # Main route - redirect to dashboard
    @app.route('/')
    def index():
        return render_template('dashboard.html')
    
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "message": "MFG Drone Admin Frontend is running"}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('base.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Server Error: {error}')
        return render_template('base.html'), 500
    
    logger.info('MFG Drone Admin Frontend initialized successfully')
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    logger.info('Starting MFG Drone Admin Frontend on port 5001')
    app.run(host='0.0.0.0', port=5001, debug=True)