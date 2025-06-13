"""
Model Blueprint
モデル訓練・管理機能のルーティング
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from services.api_client import api_client
import os
from typing import List
from werkzeug.datastructures import FileStorage

model_bp = Blueprint('model', __name__, url_prefix='/model')


@model_bp.route('/')
def index():
    """モデル管理メインページ"""
    return render_template('model/index.html')


@model_bp.route('/training')
def training():
    """モデル訓練ページ"""
    return render_template('model/training.html')


@model_bp.route('/management')
def management():
    """モデル管理ページ"""
    # 既存モデル一覧を取得
    models_result = api_client.list_models()
    
    if models_result["success"]:
        models = models_result["models"]
    else:
        models = []
        flash(f"モデル一覧の取得に失敗しました: {models_result['error']}", 'error')
    
    return render_template('model/management.html', models=models)


@model_bp.route('/api/train', methods=['POST'])
def api_train():
    """モデル訓練API"""
    try:
        # フォームデータの取得
        object_name = request.form.get('object_name', '').strip()
        if not object_name:
            return jsonify({
                "success": False,
                "error": "オブジェクト名が入力されていません"
            }), 400
        
        # アップロードされたファイルの取得
        uploaded_files = request.files.getlist('images')
        if not uploaded_files or len(uploaded_files) == 0:
            return jsonify({
                "success": False,
                "error": "画像ファイルが選択されていません"
            }), 400
        
        # 空のファイルを除外
        valid_files = []
        for file in uploaded_files:
            if file and file.filename and file.filename != '':
                valid_files.append(file)
        
        if len(valid_files) == 0:
            return jsonify({
                "success": False,
                "error": "有効な画像ファイルが見つかりません"
            }), 400
        
        # ファイルバリデーション
        validation_result = api_client.validate_image_files(valid_files)
        if not validation_result["valid"]:
            return jsonify({
                "success": False,
                "error": "ファイルバリデーションエラー",
                "details": validation_result["errors"]
            }), 400
        
        # バックエンドAPIに訓練リクエスト送信
        result = api_client.train_model(object_name, valid_files)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "task_id": result["task_id"],
                "message": result["message"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"],
                "code": result.get("code", "UNKNOWN_ERROR")
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"サーバーエラー: {str(e)}"
        }), 500


@model_bp.route('/api/list')
def api_list():
    """モデル一覧取得API"""
    try:
        result = api_client.list_models()
        
        if result["success"]:
            return jsonify({
                "success": True,
                "models": result["models"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"],
                "code": result.get("code", "UNKNOWN_ERROR")
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"サーバーエラー: {str(e)}"
        }), 500


@model_bp.route('/api/validate', methods=['POST'])
def api_validate():
    """画像ファイルバリデーションAPI"""
    try:
        uploaded_files = request.files.getlist('images')
        
        if not uploaded_files:
            return jsonify({
                "valid": False,
                "errors": ["画像ファイルが選択されていません"]
            })
        
        # 空のファイルを除外
        valid_files = []
        for file in uploaded_files:
            if file and file.filename and file.filename != '':
                valid_files.append(file)
        
        if len(valid_files) == 0:
            return jsonify({
                "valid": False,
                "errors": ["有効な画像ファイルが見つかりません"]
            })
        
        result = api_client.validate_image_files(valid_files)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "valid": False,
            "errors": [f"バリデーションエラー: {str(e)}"]
        }), 500