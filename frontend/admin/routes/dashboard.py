"""
ダッシュボード画面ルート
"""

from flask import Blueprint, render_template, jsonify
from services.drone_api_client import DroneAPIClient

dashboard_bp = Blueprint('dashboard', __name__)
api_client = DroneAPIClient()

@dashboard_bp.route('/')
def index():
    """メインダッシュボード画面"""
    return render_template('dashboard.html')

@dashboard_bp.route('/api/status')
def get_status():
    """システム状態API"""
    try:
        # バックエンドAPIからドローン状態を取得
        drone_status = api_client.get_drone_status()
        return jsonify({
            'status': 'success',
            'data': drone_status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500