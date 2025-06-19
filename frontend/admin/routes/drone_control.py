"""
Drone Control routes - ドローン制御機能
接続管理、飛行制御、移動制御
"""

from flask import Blueprint, render_template, request, jsonify
from services.drone_api_client import DroneAPIClient

drone_control_bp = Blueprint('drone_control', __name__, url_prefix='/drone')
api_client = DroneAPIClient()

@drone_control_bp.route('/connection')
def connection():
    """ドローン接続管理画面"""
    return render_template('connection.html')

@drone_control_bp.route('/flight')
def flight_control():
    """基本飛行制御画面"""
    return render_template('flight_control.html')

@drone_control_bp.route('/movement')
def movement_control():
    """移動制御画面"""
    return render_template('movement_control.html')

# Connection API endpoints
@drone_control_bp.route('/api/connect', methods=['POST'])
def connect_drone():
    """ドローン接続"""
    try:
        result = api_client.connect_drone()
        return jsonify({
            'status': 'success',
            'message': 'ドローンに接続しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'接続エラー: {str(e)}'
        }), 500

@drone_control_bp.route('/api/disconnect', methods=['POST'])
def disconnect_drone():
    """ドローン切断"""
    try:
        result = api_client.disconnect_drone()
        return jsonify({
            'status': 'success',
            'message': 'ドローンを切断しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'切断エラー: {str(e)}'
        }), 500

@drone_control_bp.route('/api/status')
def connection_status():
    """接続状態確認"""
    try:
        status = api_client.get_connection_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'状態確認エラー: {str(e)}'
        }), 500

# Flight Control API endpoints
@drone_control_bp.route('/api/takeoff', methods=['POST'])
def takeoff():
    """離陸"""
    try:
        result = api_client.takeoff()
        return jsonify({
            'status': 'success',
            'message': 'ドローンが離陸しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'離陸エラー: {str(e)}'
        }), 500

@drone_control_bp.route('/api/land', methods=['POST'])
def land():
    """着陸"""
    try:
        result = api_client.land()
        return jsonify({
            'status': 'success',
            'message': 'ドローンが着陸しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'着陸エラー: {str(e)}'
        }), 500

@drone_control_bp.route('/api/emergency', methods=['POST'])
def emergency_stop():
    """緊急停止"""
    try:
        result = api_client.emergency_stop()
        return jsonify({
            'status': 'success',
            'message': '緊急停止を実行しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'緊急停止エラー: {str(e)}'
        }), 500

# Movement Control API endpoints
@drone_control_bp.route('/api/move', methods=['POST'])
def move_drone():
    """ドローン移動制御"""
    try:
        data = request.get_json()
        direction = data.get('direction')
        distance = data.get('distance', 20)
        
        result = api_client.move_drone(direction, distance)
        return jsonify({
            'status': 'success',
            'message': f'{direction}方向に{distance}cm移動しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'移動エラー: {str(e)}'
        }), 500

@drone_control_bp.route('/api/rotate', methods=['POST'])
def rotate_drone():
    """ドローン回転制御"""
    try:
        data = request.get_json()
        direction = data.get('direction')  # 'cw' or 'ccw'
        angle = data.get('angle', 90)
        
        result = api_client.rotate_drone(direction, angle)
        return jsonify({
            'status': 'success',
            'message': f'{direction}方向に{angle}度回転しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'回転エラー: {str(e)}'
        }), 500