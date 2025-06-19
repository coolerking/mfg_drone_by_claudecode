"""
Monitoring routes - 監視・設定機能
センサー監視、カメラ制御、システム設定
"""

from flask import Blueprint, render_template, request, jsonify
from services.drone_api_client import DroneAPIClient

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')
api_client = DroneAPIClient()

@monitoring_bp.route('/sensors')
def sensors():
    """センサー監視画面"""
    return render_template('sensors.html')

@monitoring_bp.route('/camera')
def camera():
    """カメラ・映像画面"""
    return render_template('camera.html')

@monitoring_bp.route('/settings')
def settings():
    """設定管理画面"""
    return render_template('settings.html')

# Sensor Monitoring API endpoints
@monitoring_bp.route('/api/sensors/all')
def get_all_sensors():
    """全センサーデータ取得"""
    try:
        sensors = api_client.get_all_sensor_data()
        return jsonify({
            'status': 'success',
            'data': sensors
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'センサーデータ取得エラー: {str(e)}'
        }), 500

@monitoring_bp.route('/api/sensors/battery')
def get_battery():
    """バッテリー情報取得"""
    try:
        battery = api_client.get_battery_info()
        return jsonify({
            'status': 'success',
            'data': battery
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'バッテリー情報取得エラー: {str(e)}'
        }), 500

@monitoring_bp.route('/api/sensors/attitude')
def get_attitude():
    """姿勢情報取得"""
    try:
        attitude = api_client.get_attitude_data()
        return jsonify({
            'status': 'success',
            'data': attitude
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'姿勢情報取得エラー: {str(e)}'
        }), 500

# Camera Control API endpoints
@monitoring_bp.route('/api/camera/stream/start', methods=['POST'])
def start_camera_stream():
    """カメラストリーミング開始"""
    try:
        result = api_client.start_camera_stream()
        return jsonify({
            'status': 'success',
            'message': 'カメラストリーミングを開始しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'ストリーミング開始エラー: {str(e)}'
        }), 500

@monitoring_bp.route('/api/camera/stream/stop', methods=['POST'])
def stop_camera_stream():
    """カメラストリーミング停止"""
    try:
        result = api_client.stop_camera_stream()
        return jsonify({
            'status': 'success',
            'message': 'カメラストリーミングを停止しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'ストリーミング停止エラー: {str(e)}'
        }), 500

@monitoring_bp.route('/api/camera/photo', methods=['POST'])
def take_photo():
    """写真撮影"""
    try:
        result = api_client.take_photo()
        return jsonify({
            'status': 'success',
            'message': '写真を撮影しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'撮影エラー: {str(e)}'
        }), 500

@monitoring_bp.route('/api/camera/video/start', methods=['POST'])
def start_video_recording():
    """動画録画開始"""
    try:
        result = api_client.start_video_recording()
        return jsonify({
            'status': 'success',
            'message': '動画録画を開始しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'録画開始エラー: {str(e)}'
        }), 500

@monitoring_bp.route('/api/camera/video/stop', methods=['POST'])
def stop_video_recording():
    """動画録画停止"""
    try:
        result = api_client.stop_video_recording()
        return jsonify({
            'status': 'success',
            'message': '動画録画を停止しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'録画停止エラー: {str(e)}'
        }), 500

# Settings API endpoints
@monitoring_bp.route('/api/settings/get')
def get_settings():
    """設定取得"""
    try:
        settings = api_client.get_drone_settings()
        return jsonify({
            'status': 'success',
            'data': settings
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'設定取得エラー: {str(e)}'
        }), 500

@monitoring_bp.route('/api/settings/update', methods=['POST'])
def update_settings():
    """設定更新"""
    try:
        data = request.get_json()
        result = api_client.update_drone_settings(data)
        return jsonify({
            'status': 'success',
            'message': '設定を更新しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'設定更新エラー: {str(e)}'
        }), 500