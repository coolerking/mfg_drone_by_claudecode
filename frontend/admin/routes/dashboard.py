"""
Dashboard routes - ダッシュボード機能
システム状態、ライブ映像、メトリクス表示
"""

from flask import Blueprint, render_template, jsonify
from services.drone_api_client import DroneAPIClient

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
api_client = DroneAPIClient()

@dashboard_bp.route('/')
def dashboard():
    """ダッシュボードメイン画面"""
    return render_template('dashboard.html')

@dashboard_bp.route('/api/system-status')
def system_status():
    """システム状態API"""
    try:
        # バックエンドAPIからシステム状態を取得
        connection_status = api_client.get_connection_status()
        battery_info = api_client.get_battery_info()
        sensor_data = api_client.get_sensor_summary()
        
        return jsonify({
            'status': 'success',
            'data': {
                'connection': connection_status,
                'battery': battery_info,
                'sensors': sensor_data,
                'timestamp': api_client.get_current_timestamp()
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'システム状態取得エラー: {str(e)}'
        }), 500

@dashboard_bp.route('/api/live-metrics')
def live_metrics():
    """リアルタイムメトリクスAPI"""
    try:
        metrics = api_client.get_live_metrics()
        return jsonify({
            'status': 'success',
            'data': metrics
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'メトリクス取得エラー: {str(e)}'
        }), 500