"""
Drone Control Blueprint
ドローン制御関連のルートを定義
"""

from flask import Blueprint, request, jsonify, render_template
from services.api_client import api_client
import logging

logger = logging.getLogger(__name__)

drone_bp = Blueprint('drone', __name__, url_prefix='/drone')

@drone_bp.route('/dashboard')
def dashboard():
    """ドローン制御ダッシュボード"""
    return render_template('drone/dashboard.html')

@drone_bp.route('/connect', methods=['POST'])
def connect():
    """ドローン接続"""
    try:
        result = api_client.connect_drone()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Connect error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500

@drone_bp.route('/disconnect', methods=['POST'])
def disconnect():
    """ドローン切断"""
    try:
        result = api_client.disconnect_drone()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500

@drone_bp.route('/takeoff', methods=['POST'])
def takeoff():
    """離陸"""
    try:
        result = api_client.takeoff()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Takeoff error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500

@drone_bp.route('/land', methods=['POST'])
def land():
    """着陸"""
    try:
        result = api_client.land()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Land error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500

@drone_bp.route('/emergency', methods=['POST'])
def emergency():
    """緊急停止"""
    try:
        result = api_client.emergency_stop()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Emergency error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500

@drone_bp.route('/hover', methods=['POST'])
def hover():
    """ホバリング"""
    try:
        result = api_client.hover()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Hover error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500

@drone_bp.route('/move', methods=['POST'])
def move():
    """基本移動"""
    try:
        data = request.get_json()
        direction = data.get('direction')
        distance = data.get('distance')
        
        if not direction or not distance:
            return jsonify({
                "success": False,
                "data": {"error": "Direction and distance are required"},
                "status_code": 400
            }), 400
        
        result = api_client.move_drone(direction, int(distance))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Move error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500

@drone_bp.route('/rotate', methods=['POST'])
def rotate():
    """回転"""
    try:
        data = request.get_json()
        direction = data.get('direction')
        angle = data.get('angle')
        
        if not direction or not angle:
            return jsonify({
                "success": False,
                "data": {"error": "Direction and angle are required"},
                "status_code": 400
            }), 400
        
        result = api_client.rotate_drone(direction, int(angle))
        return jsonify(result)
    except Exception as e:
        logger.error(f"Rotate error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500

@drone_bp.route('/status', methods=['GET'])
def status():
    """ドローン状態取得"""
    try:
        result = api_client.get_drone_status()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500

@drone_bp.route('/sensors', methods=['GET'])
def sensors():
    """センサー情報一括取得"""
    try:
        # 複数のセンサー情報を一括取得
        battery = api_client.get_battery()
        height = api_client.get_height()
        temperature = api_client.get_temperature()
        
        sensors_data = {
            "battery": battery.get("data", {}).get("battery", 0) if battery.get("success") else 0,
            "height": height.get("data", {}).get("height", 0) if height.get("success") else 0,
            "temperature": temperature.get("data", {}).get("temperature", 0) if temperature.get("success") else 0
        }
        
        return jsonify({
            "success": True,
            "data": sensors_data,
            "status_code": 200
        })
    except Exception as e:
        logger.error(f"Sensors error: {e}")
        return jsonify({
            "success": False,
            "data": {"error": str(e)},
            "status_code": 500
        }), 500