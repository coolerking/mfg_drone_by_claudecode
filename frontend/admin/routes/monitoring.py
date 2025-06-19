"""
システム監視・センサー画面ルート
"""

from flask import Blueprint, render_template, jsonify
from services.drone_api_client import DroneAPIClient

monitoring_bp = Blueprint('monitoring', __name__)
api_client = DroneAPIClient()

@monitoring_bp.route('/sensors')
def sensors():
    """センサー監視画面"""
    return render_template('sensors.html')

@monitoring_bp.route('/settings')
def settings():
    """設定画面"""
    return render_template('settings.html')

# API エンドポイント
@monitoring_bp.route('/api/sensors/battery')
def get_battery():
    """バッテリー情報取得API"""
    try:
        result = api_client.get_battery_level()
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@monitoring_bp.route('/api/sensors/altitude')
def get_altitude():
    """高度情報取得API"""
    try:
        result = api_client.get_altitude()
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@monitoring_bp.route('/api/sensors/attitude')
def get_attitude():
    """姿勢情報取得API"""
    try:
        result = api_client.get_attitude()
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@monitoring_bp.route('/api/sensors/all')
def get_all_sensors():
    """全センサー情報取得API"""
    try:
        result = api_client.get_all_sensors()
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@monitoring_bp.route('/api/settings', methods=['GET'])
def get_settings():
    """設定取得API"""
    try:
        result = api_client.get_settings()
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@monitoring_bp.route('/api/settings', methods=['POST'])
def update_settings():
    """設定更新API"""
    try:
        from flask import request
        settings_data = request.get_json()
        result = api_client.update_settings(settings_data)
        return jsonify({
            'status': 'success',
            'message': '設定を更新しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'設定更新に失敗しました: {str(e)}'
        }), 500