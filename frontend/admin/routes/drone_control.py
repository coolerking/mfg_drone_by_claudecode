"""
ドローン制御画面ルート
"""

from flask import Blueprint, render_template, request, jsonify
from services.drone_api_client import DroneAPIClient

drone_control_bp = Blueprint('drone_control', __name__)
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

# API エンドポイント
@drone_control_bp.route('/api/connect', methods=['POST'])
def connect_drone():
    """ドローン接続API"""
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
            'message': f'接続に失敗しました: {str(e)}'
        }), 500

@drone_control_bp.route('/api/disconnect', methods=['POST'])
def disconnect_drone():
    """ドローン切断API"""
    try:
        result = api_client.disconnect_drone()
        return jsonify({
            'status': 'success',
            'message': 'ドローンから切断しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'切断に失敗しました: {str(e)}'
        }), 500

@drone_control_bp.route('/api/takeoff', methods=['POST'])
def takeoff():
    """離陸API"""
    try:
        result = api_client.takeoff()
        return jsonify({
            'status': 'success',
            'message': '離陸しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'離陸に失敗しました: {str(e)}'
        }), 500

@drone_control_bp.route('/api/land', methods=['POST'])
def land():
    """着陸API"""
    try:
        result = api_client.land()
        return jsonify({
            'status': 'success',
            'message': '着陸しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'着陸に失敗しました: {str(e)}'
        }), 500

@drone_control_bp.route('/api/emergency', methods=['POST'])
def emergency_stop():
    """緊急停止API"""
    try:
        result = api_client.emergency_stop()
        return jsonify({
            'status': 'success',
            'message': '緊急停止しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'緊急停止に失敗しました: {str(e)}'
        }), 500

@drone_control_bp.route('/api/move', methods=['POST'])
def move_drone():
    """ドローン移動API"""
    try:
        data = request.get_json()
        direction = data.get('direction')
        distance = data.get('distance', 50)
        
        result = api_client.move_drone(direction, distance)
        return jsonify({
            'status': 'success',
            'message': f'{direction}に{distance}cm移動しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'移動に失敗しました: {str(e)}'
        }), 500