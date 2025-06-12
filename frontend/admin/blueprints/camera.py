"""
Camera Blueprint - Routes for camera operations
カメラBlueprint - カメラ操作のためのルート
"""

from flask import Blueprint, request, jsonify, Response
from flask_socketio import emit
import logging
from services.camera_service import camera_service

logger = logging.getLogger(__name__)

camera_bp = Blueprint('camera', __name__, url_prefix='/api/camera')


@camera_bp.route('/stream/start', methods=['POST'])
def start_stream():
    """Start video streaming"""
    try:
        result = camera_service.start_stream()
        
        # Emit socket event for real-time updates
        emit('stream_started', result, broadcast=True)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Failed to start stream: {e}")
        error_response = {
            "status": "error",
            "message": str(e)
        }
        
        # Emit error event
        emit('error', error_response, broadcast=True)
        
        return jsonify(error_response), 500


@camera_bp.route('/stream/stop', methods=['POST'])
def stop_stream():
    """Stop video streaming"""
    try:
        result = camera_service.stop_stream()
        
        # Emit socket event for real-time updates
        emit('stream_stopped', result, broadcast=True)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Failed to stop stream: {e}")
        error_response = {
            "status": "error",
            "message": str(e)
        }
        
        # Emit error event
        emit('error', error_response, broadcast=True)
        
        return jsonify(error_response), 500


@camera_bp.route('/stream', methods=['GET'])
def get_stream():
    """Proxy video stream from backend"""
    try:
        import requests
        
        backend_stream_url = camera_service.get_stream_url()
        
        def generate():
            try:
                with requests.get(backend_stream_url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
            except Exception as e:
                logger.error(f"Stream proxy error: {e}")
                yield b'--frame\r\nContent-Type: text/plain\r\n\r\nStream Error\r\n'
        
        return Response(
            generate(),
            mimetype='multipart/x-mixed-replace; boundary=frame',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get stream: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@camera_bp.route('/photo', methods=['POST'])
def capture_photo():
    """Capture photo"""
    try:
        result = camera_service.capture_photo()
        
        # Emit socket event for real-time updates
        emit('photo_captured', result, broadcast=True)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Failed to capture photo: {e}")
        error_response = {
            "status": "error",
            "message": str(e)
        }
        
        # Emit error event
        emit('error', error_response, broadcast=True)
        
        return jsonify(error_response), 500


@camera_bp.route('/video/start', methods=['POST'])
def start_recording():
    """Start video recording"""
    try:
        result = camera_service.start_recording()
        
        # Emit socket event for real-time updates
        emit('recording_started', result, broadcast=True)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Failed to start recording: {e}")
        error_response = {
            "status": "error",
            "message": str(e)
        }
        
        # Emit error event
        emit('error', error_response, broadcast=True)
        
        return jsonify(error_response), 500


@camera_bp.route('/video/stop', methods=['POST'])
def stop_recording():
    """Stop video recording"""
    try:
        result = camera_service.stop_recording()
        
        # Emit socket event for real-time updates
        emit('recording_stopped', result, broadcast=True)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Failed to stop recording: {e}")
        error_response = {
            "status": "error",
            "message": str(e)
        }
        
        # Emit error event
        emit('error', error_response, broadcast=True)
        
        return jsonify(error_response), 500


@camera_bp.route('/settings', methods=['PUT'])
def update_settings():
    """Update camera settings"""
    try:
        settings = request.get_json()
        
        if not settings:
            return jsonify({
                "status": "error",
                "message": "No settings provided"
            }), 400
        
        result = camera_service.update_settings(settings)
        
        # Emit socket event for real-time updates
        emit('settings_updated', {
            **result,
            "settings": settings
        }, broadcast=True)
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Invalid settings: {e}")
        error_response = {
            "status": "error",
            "message": str(e)
        }
        return jsonify(error_response), 400
        
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        error_response = {
            "status": "error",
            "message": str(e)
        }
        
        # Emit error event
        emit('error', error_response, broadcast=True)
        
        return jsonify(error_response), 500


@camera_bp.route('/status', methods=['GET'])
def get_status():
    """Get camera status"""
    try:
        status = camera_service.get_camera_status()
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Failed to get camera status: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500