"""
AI物体追跡・モデル管理画面ルート
"""

from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from services.drone_api_client import DroneAPIClient

ai_tracking_bp = Blueprint('ai_tracking', __name__)
api_client = DroneAPIClient()

@ai_tracking_bp.route('/tracking')
def tracking():
    """物体追跡画面"""
    return render_template('tracking.html')

@ai_tracking_bp.route('/models')
def models():
    """モデル管理画面"""
    return render_template('models.html')

@ai_tracking_bp.route('/camera')
def camera():
    """カメラ・映像画面"""
    return render_template('camera.html')

# API エンドポイント
@ai_tracking_bp.route('/api/tracking/start', methods=['POST'])
def start_tracking():
    """物体追跡開始API"""
    try:
        data = request.get_json()
        target_object = data.get('target_object')
        tracking_mode = data.get('tracking_mode', 'center')
        
        result = api_client.start_tracking(target_object, tracking_mode)
        return jsonify({
            'status': 'success',
            'message': f'物体追跡を開始しました: {target_object}',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'追跡開始に失敗しました: {str(e)}'
        }), 500

@ai_tracking_bp.route('/api/tracking/stop', methods=['POST'])
def stop_tracking():
    """物体追跡停止API"""
    try:
        result = api_client.stop_tracking()
        return jsonify({
            'status': 'success',
            'message': '物体追跡を停止しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'追跡停止に失敗しました: {str(e)}'
        }), 500

@ai_tracking_bp.route('/api/tracking/status')
def tracking_status():
    """追跡状態取得API"""
    try:
        result = api_client.get_tracking_status()
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@ai_tracking_bp.route('/api/models', methods=['GET'])
def get_models():
    """モデル一覧取得API"""
    try:
        result = api_client.get_models()
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@ai_tracking_bp.route('/api/models/upload', methods=['POST'])
def upload_training_images():
    """学習画像アップロードAPI"""
    try:
        if 'images' not in request.files:
            return jsonify({
                'status': 'error',
                'message': '画像ファイルが選択されていません'
            }), 400
        
        files = request.files.getlist('images')
        object_name = request.form.get('object_name')
        
        if not object_name:
            return jsonify({
                'status': 'error',
                'message': 'オブジェクト名が指定されていません'
            }), 400
        
        # 画像ファイルをアップロード
        uploaded_files = []
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                # 一時的にローカルに保存してからバックエンドに送信
                temp_path = f"/tmp/{filename}"
                file.save(temp_path)
                uploaded_files.append(temp_path)
        
        result = api_client.upload_training_images(object_name, uploaded_files)
        
        # 一時ファイルを削除
        for temp_path in uploaded_files:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return jsonify({
            'status': 'success',
            'message': f'{len(uploaded_files)}枚の画像をアップロードしました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'アップロードに失敗しました: {str(e)}'
        }), 500

@ai_tracking_bp.route('/api/models/train', methods=['POST'])
def train_model():
    """モデル訓練API"""
    try:
        data = request.get_json()
        object_name = data.get('object_name')
        
        result = api_client.train_model(object_name)
        return jsonify({
            'status': 'success',
            'message': f'モデル訓練を開始しました: {object_name}',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'訓練開始に失敗しました: {str(e)}'
        }), 500

@ai_tracking_bp.route('/api/camera/stream')
def camera_stream():
    """カメラストリーム取得API"""
    try:
        # バックエンドのストリームURLを返す
        stream_url = api_client.get_camera_stream_url()
        return jsonify({
            'status': 'success',
            'data': {
                'stream_url': stream_url
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500