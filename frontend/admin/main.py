"""
MFG Drone Admin Frontend
管理者用フロントエンド - 物体学習、ドローン制御、追跡開始/停止
Phase 1: 基盤整備完了版
"""

import os
from flask import Flask, render_template

# ブループリントのインポート
from routes.dashboard import dashboard_bp
from routes.drone_control import drone_control_bp
from routes.ai_tracking import ai_tracking_bp
from routes.monitoring import monitoring_bp

def create_app():
    """Flaskアプリケーション作成"""
    app = Flask(__name__)
    
    # 設定
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-phase1')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB上限
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    
    # ブループリント登録
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(drone_control_bp)
    app.register_blueprint(ai_tracking_bp)
    app.register_blueprint(monitoring_bp)
    
    # メインルート（ダッシュボードにリダイレクト）
    @app.route('/')
    def index():
        return render_template('dashboard.html')
    
    # ヘルスチェック
    @app.route('/health')
    def health_check():
        return {
            "status": "healthy",
            "version": "1.0.0-phase1",
            "message": "MFG Drone Admin Frontend - Phase 1 基盤整備完了"
        }
    
    # 個別画面ルート
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/connection')
    def connection():
        return render_template('connection.html')
    
    @app.route('/flight')
    def flight_control():
        return render_template('flight_control.html')
    
    @app.route('/movement')
    def movement_control():
        return render_template('movement_control.html')
    
    @app.route('/camera')
    def camera():
        return render_template('camera.html')
    
    @app.route('/sensors')
    def sensors():
        return render_template('sensors.html')
    
    @app.route('/tracking')
    def tracking():
        return render_template('tracking.html')
    
    @app.route('/models')
    def models():
        return render_template('models.html')
    
    @app.route('/settings')
    def settings():
        return render_template('settings.html')
    
    # エラーハンドリング
    @app.errorhandler(404)
    def not_found(error):
        return render_template('dashboard.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error", "message": str(error)}, 500
    
    return app

app = create_app()

if __name__ == '__main__':
    # 開発サーバー起動
    print("🚁 MFG Drone Admin Frontend - Phase 1")
    print("📍 http://localhost:5001")
    print("🔧 基盤整備完了: アーキテクチャ、UI、API統合")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )