"""
MFG Drone Tracking Blueprint
物体追跡制御機能のBlueprint
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_socketio import emit
import logging
from services.tracking_service import tracking_service

logger = logging.getLogger(__name__)

# Blueprint作成
tracking_bp = Blueprint('tracking', __name__, url_prefix='/tracking')

@tracking_bp.route('/control')
def control_dashboard():
    """追跡制御ダッシュボード"""
    try:
        # 利用可能モデル一覧を取得
        models_response = tracking_service.get_available_models()
        available_models = models_response.get('models', [])
        
        # 現在の追跡状態を取得
        status = tracking_service.get_tracking_status()
        
        return render_template(
            'tracking/control.html',
            available_models=available_models,
            tracking_status=status
        )
    except Exception as e:
        logger.error(f"追跡制御ダッシュボード表示エラー: {e}")
        return render_template(
            'tracking/control.html',
            available_models=[],
            tracking_status={'is_tracking': False, 'target_object': None},
            error="データ取得エラーが発生しました"
        )

@tracking_bp.route('/monitor')
def monitor_dashboard():
    """追跡状態監視ダッシュボード"""
    try:
        # 現在の追跡状態を取得
        status = tracking_service.get_tracking_status()
        return render_template('tracking/monitor.html', tracking_status=status)
    except Exception as e:
        logger.error(f"追跡監視ダッシュボード表示エラー: {e}")
        return render_template(
            'tracking/monitor.html',
            tracking_status={'is_tracking': False},
            error="監視データ取得エラーが発生しました"
        )

@tracking_bp.route('/visualization')
def visualization_dashboard():
    """追跡結果可視化ダッシュボード"""
    return render_template('tracking/visualization.html')

# API エンドポイント
@tracking_bp.route('/api/start', methods=['POST'])
def api_start_tracking():
    """追跡開始API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'リクエストデータが必要です'}), 400
        
        target_object = data.get('target_object')
        tracking_mode = data.get('tracking_mode', 'center')
        
        if not target_object:
            return jsonify({'error': 'target_objectが必要です'}), 400
        
        # バックエンドAPIに追跡開始を要求
        result = tracking_service.start_tracking(target_object, tracking_mode)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"追跡開始APIエラー: {e}")
        return jsonify({'error': '追跡開始に失敗しました'}), 500

@tracking_bp.route('/api/stop', methods=['POST'])
def api_stop_tracking():
    """追跡停止API"""
    try:
        # バックエンドAPIに追跡停止を要求
        result = tracking_service.stop_tracking()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"追跡停止APIエラー: {e}")
        return jsonify({'error': '追跡停止に失敗しました'}), 500

@tracking_bp.route('/api/status', methods=['GET'])
def api_get_status():
    """追跡状態取得API"""
    try:
        status = tracking_service.get_tracking_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"追跡状態取得APIエラー: {e}")
        return jsonify({'error': '状態取得に失敗しました'}), 500

@tracking_bp.route('/api/models', methods=['GET'])
def api_get_models():
    """利用可能モデル一覧取得API"""
    try:
        models = tracking_service.get_available_models()
        return jsonify(models)
        
    except Exception as e:
        logger.error(f"モデル一覧取得APIエラー: {e}")
        return jsonify({'error': 'モデル一覧取得に失敗しました'}), 500