"""
AI Tracking routes - AI追跡・モデル管理機能
物体追跡、モデル管理、学習
"""

from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from services.drone_api_client import DroneAPIClient

ai_tracking_bp = Blueprint('ai_tracking', __name__, url_prefix='/ai')
api_client = DroneAPIClient()

@ai_tracking_bp.route('/tracking')
def tracking():
    """物体追跡画面"""
    return render_template('tracking.html')

@ai_tracking_bp.route('/models')
def models():
    """モデル管理画面"""
    return render_template('models.html')

# Object Tracking API endpoints
@ai_tracking_bp.route('/api/tracking/start', methods=['POST'])
def start_tracking():
    """物体追跡開始"""
    try:
        data = request.get_json()
        target_object = data.get('target_object')
        tracking_mode = data.get('tracking_mode', 'center')
        
        result = api_client.start_tracking(target_object, tracking_mode)
        return jsonify({
            'status': 'success',
            'message': f'{target_object}の追跡を開始しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'追跡開始エラー: {str(e)}'
        }), 500

@ai_tracking_bp.route('/api/tracking/stop', methods=['POST'])
def stop_tracking():
    """物体追跡停止"""
    try:
        result = api_client.stop_tracking()
        return jsonify({
            'status': 'success',
            'message': '追跡を停止しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'追跡停止エラー: {str(e)}'
        }), 500

@ai_tracking_bp.route('/api/tracking/status')
def tracking_status():
    """追跡状態確認"""
    try:
        status = api_client.get_tracking_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'追跡状態確認エラー: {str(e)}'
        }), 500

# Model Management API endpoints
@ai_tracking_bp.route('/api/models/list')
def list_models():
    """利用可能モデル一覧"""
    try:
        models = api_client.list_models()
        return jsonify({
            'status': 'success',
            'data': models
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'モデル一覧取得エラー: {str(e)}'
        }), 500

@ai_tracking_bp.route('/api/models/upload', methods=['POST'])
def upload_training_images():
    """学習用画像アップロード"""
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
        
        uploaded_files = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                # 一時保存して、バックエンドに送信
                uploaded_files.append(filename)
        
        result = api_client.upload_training_images(uploaded_files, object_name)
        return jsonify({
            'status': 'success',
            'message': f'{len(uploaded_files)}枚の画像をアップロードしました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'画像アップロードエラー: {str(e)}'
        }), 500

@ai_tracking_bp.route('/api/models/train', methods=['POST'])
def train_model():
    """モデル学習開始"""
    try:
        data = request.get_json()
        object_name = data.get('object_name')
        training_params = data.get('training_params', {})
        
        result = api_client.start_training(object_name, training_params)
        return jsonify({
            'status': 'success',
            'message': f'{object_name}のモデル学習を開始しました',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'モデル学習エラー: {str(e)}'
        }), 500

@ai_tracking_bp.route('/api/models/training/status/<training_id>')
def training_status(training_id):
    """学習進捗確認"""
    try:
        status = api_client.get_training_status(training_id)
        return jsonify({
            'status': 'success',
            'data': status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'学習状態確認エラー: {str(e)}'
        }), 500