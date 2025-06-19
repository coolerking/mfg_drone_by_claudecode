"""
Routes package for MFG Drone Admin Frontend
ルート管理パッケージ
"""

from .dashboard import dashboard_bp
from .drone_control import drone_control_bp
from .ai_tracking import ai_tracking_bp
from .monitoring import monitoring_bp

__all__ = ['dashboard_bp', 'drone_control_bp', 'ai_tracking_bp', 'monitoring_bp']