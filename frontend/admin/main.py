"""
MFG Drone Admin Frontend
管理者用フロントエンド - ドローン制御、カメラ・メディア管理、物体学習・追跡
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-for-mfg-drone')

# 設定
BACKEND_API_URL = os.environ.get('BACKEND_API_URL', 'http://localhost:8000')
UPLOAD_FOLDER = os.path.join(app.static_folder or 'static', 'uploads')
MEDIA_FOLDER = os.path.join(app.static_folder or 'static', 'media')

# メディアフォルダ作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MEDIA_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """メイン管理画面"""
    return render_template('admin.html', 
                         backend_api_url=BACKEND_API_URL,
                         timestamp=datetime.now().isoformat())

@app.route('/health')
def health_check():
    """ヘルスチェック"""
    return jsonify({
        "status": "healthy",
        "service": "MFG Drone Admin Frontend",
        "timestamp": datetime.now().isoformat(),
        "backend_api_url": BACKEND_API_URL
    })

@app.route('/api/config')
def get_config():
    """フロントエンド設定情報取得"""
    return jsonify({
        "backend_api_url": BACKEND_API_URL,
        "upload_folder": UPLOAD_FOLDER,
        "media_folder": MEDIA_FOLDER,
        "version": "1.0.0",
        "features": {
            "camera_control": True,
            "media_management": True,
            "drone_control": True,
            "sensor_monitoring": True,
            "object_tracking": True,
            "model_training": True
        }
    })

@app.route('/api/media')
def list_media():
    """メディアファイル一覧取得"""
    try:
        media_files = []
        
        # メディアフォルダ内のファイルをスキャン
        if os.path.exists(MEDIA_FOLDER):
            for filename in os.listdir(MEDIA_FOLDER):
                filepath = os.path.join(MEDIA_FOLDER, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    file_info = {
                        "name": filename,
                        "path": f"/media/{filename}",
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": "photo" if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) else "video"
                    }
                    media_files.append(file_info)
        
        # 作成日時でソート（新しい順）
        media_files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            "media_files": media_files,
            "total_count": len(media_files),
            "total_size": sum(f['size'] for f in media_files)
        })
    except Exception as e:
        logger.error(f"Media list error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/media/<path:filename>')
def serve_media(filename):
    """メディアファイル配信"""
    try:
        return send_from_directory(MEDIA_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route('/api/media/<filename>', methods=['DELETE'])
def delete_media(filename):
    """メディアファイル削除"""
    try:
        filepath = os.path.join(MEDIA_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted media file: {filename}")
            return jsonify({"message": f"File {filename} deleted successfully"})
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        logger.error(f"Media delete error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/storage')
def get_storage_info():
    """ストレージ使用量情報取得"""
    try:
        total_size = 0
        file_count = 0
        
        if os.path.exists(MEDIA_FOLDER):
            for filename in os.listdir(MEDIA_FOLDER):
                filepath = os.path.join(MEDIA_FOLDER, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
                    file_count += 1
        
        # ディスク使用量（簡易版）
        import shutil
        disk_total, disk_used, disk_free = shutil.disk_usage(MEDIA_FOLDER)
        
        return jsonify({
            "media_size": total_size,
            "media_count": file_count,
            "disk_total": disk_total,
            "disk_used": disk_used,
            "disk_free": disk_free,
            "media_size_mb": round(total_size / (1024 * 1024), 2),
            "disk_total_gb": round(disk_total / (1024 * 1024 * 1024), 2),
            "disk_used_gb": round(disk_used / (1024 * 1024 * 1024), 2),
            "disk_free_gb": round(disk_free / (1024 * 1024 * 1024), 2)
        })
    except Exception as e:
        logger.error(f"Storage info error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """ファイルアップロード（将来の機能拡張用）"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file:
            # ファイル名の安全化
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            logger.info(f"File uploaded: {filename}")
            return jsonify({
                "message": "File uploaded successfully",
                "filename": filename,
                "path": f"/uploads/{filename}"
            })
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラ"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラ"""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.before_request
def log_request():
    """リクエストログ"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.after_request
def after_request(response):
    """レスポンスヘッダー設定"""
    # CORS設定（開発環境用）
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    logger.info("Starting MFG Drone Admin Frontend...")
    logger.info(f"Backend API URL: {BACKEND_API_URL}")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"Media folder: {MEDIA_FOLDER}")
    
    app.run(host='0.0.0.0', port=5001, debug=True)