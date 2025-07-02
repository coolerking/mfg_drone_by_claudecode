"""
Phase 4 API Router
Security, alerting, and performance monitoring endpoints
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query, Security
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..security import (
    require_admin, 
    require_dashboard, 
    require_read,
    api_key_manager,
    get_api_key,
    validate_input_security
)
from ..core.alert_service import AlertService, AlertLevel, AlertType
from ..core.performance_service import PerformanceService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instances (will be injected)
alert_service: AlertService = None
performance_service: PerformanceService = None

def get_alert_service() -> AlertService:
    """Get alert service instance"""
    global alert_service
    if alert_service is None:
        raise HTTPException(status_code=503, detail="Alert service not initialized")
    return alert_service

def get_performance_service() -> PerformanceService:
    """Get performance service instance"""
    global performance_service
    if performance_service is None:
        raise HTTPException(status_code=503, detail="Performance service not initialized")
    return performance_service

# Rate limiter for Phase 4 endpoints
def get_limiter():
    from ..main import app
    return app.state.limiter

# Security Management Endpoints

@router.get("/security/api-keys")
async def list_api_keys(
    _: str = Depends(require_admin)
):
    """
    API キー一覧取得
    
    管理者権限でAPI キーの一覧を取得します。
    """
    try:
        api_keys = api_key_manager.list_api_keys()
        logger.info("Retrieved API keys list")
        return {"api_keys": api_keys, "total_count": len(api_keys)}
    except Exception as e:
        logger.error(f"Error listing API keys: {str(e)}")
        raise HTTPException(status_code=500, detail="API キー一覧の取得に失敗しました")

@router.post("/security/api-keys")
async def generate_api_key(
    name: str = Query(..., description="API キー名"),
    permissions: str = Query(..., description="権限（カンマ区切り）"),
    expires_days: Optional[int] = Query(None, description="有効期限（日数）"),
    _: str = Depends(require_admin)
):
    """
    API キー生成
    
    新しいAPI キーを生成します。
    """
    try:
        # Validate and parse permissions
        permission_list = [p.strip() for p in permissions.split(",")]
        valid_permissions = {"read", "write", "admin", "dashboard"}
        
        for perm in permission_list:
            if perm not in valid_permissions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid permission: {perm}. Valid: {valid_permissions}"
                )
        
        # Validate inputs
        name = validate_input_security(name, 100)
        
        # Generate API key
        api_key = api_key_manager.generate_api_key(name, permission_list, expires_days)
        
        logger.info(f"Generated new API key: {name}")
        return {
            "success": True,
            "api_key": api_key,
            "name": name,
            "permissions": permission_list,
            "expires_days": expires_days
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating API key: {str(e)}")
        raise HTTPException(status_code=500, detail="API キーの生成に失敗しました")

@router.delete("/security/api-keys/{api_key}")
async def revoke_api_key(
    api_key: str,
    _: str = Depends(require_admin)
):
    """
    API キー削除
    
    指定されたAPI キーを削除します。
    """
    try:
        success = api_key_manager.revoke_api_key(api_key)
        if success:
            logger.info(f"Revoked API key: {api_key[:8]}...")
            return {"success": True, "message": "API キーが削除されました"}
        else:
            raise HTTPException(status_code=404, detail="API キーが見つかりません")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {str(e)}")
        raise HTTPException(status_code=500, detail="API キーの削除に失敗しました")

@router.get("/security/config")
async def get_security_config(
    _: str = Depends(require_admin)
):
    """
    セキュリティ設定取得
    
    現在のセキュリティ設定を取得します。
    """
    try:
        from ..security import get_security_config
        config = get_security_config()
        logger.debug("Retrieved security configuration")
        return config
    except Exception as e:
        logger.error(f"Error getting security config: {str(e)}")
        raise HTTPException(status_code=500, detail="セキュリティ設定の取得に失敗しました")

# Alert Management Endpoints

@router.get("/alerts")
async def get_alerts(
    level: Optional[str] = Query(None, description="アラートレベル"),
    alert_type: Optional[str] = Query(None, description="アラートタイプ"),
    limit: Optional[int] = Query(100, description="最大件数"),
    unresolved_only: bool = Query(False, description="未解決のみ"),
    alert_svc: AlertService = Depends(get_alert_service),
    _: str = Depends(require_dashboard)
):
    """
    アラート一覧取得
    
    システムアラートの一覧を取得します。
    """
    try:
        # Convert string enums
        alert_level = AlertLevel(level) if level else None
        alert_type_enum = AlertType(alert_type) if alert_type else None
        
        alerts = alert_svc.get_alerts(
            level=alert_level,
            alert_type=alert_type_enum,
            limit=limit,
            unresolved_only=unresolved_only
        )
        
        logger.debug(f"Retrieved {len(alerts)} alerts")
        return {"alerts": alerts, "total_count": len(alerts)}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="アラートの取得に失敗しました")

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    alert_svc: AlertService = Depends(get_alert_service),
    _: str = Depends(require_dashboard)
):
    """
    アラート確認
    
    指定されたアラートを確認済みとしてマークします。
    """
    try:
        success = alert_svc.acknowledge_alert(alert_id)
        if success:
            logger.info(f"Acknowledged alert: {alert_id}")
            return {"success": True, "message": "アラートが確認されました"}
        else:
            raise HTTPException(status_code=404, detail="アラートが見つかりません")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        raise HTTPException(status_code=500, detail="アラートの確認に失敗しました")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    alert_svc: AlertService = Depends(get_alert_service),
    _: str = Depends(require_dashboard)
):
    """
    アラート解決
    
    指定されたアラートを解決済みとしてマークします。
    """
    try:
        success = alert_svc.resolve_alert(alert_id)
        if success:
            logger.info(f"Resolved alert: {alert_id}")
            return {"success": True, "message": "アラートが解決されました"}
        else:
            raise HTTPException(status_code=404, detail="アラートが見つかりません")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        raise HTTPException(status_code=500, detail="アラートの解決に失敗しました")

@router.get("/alerts/summary")
async def get_alert_summary(
    alert_svc: AlertService = Depends(get_alert_service),
    _: str = Depends(require_dashboard)
):
    """
    アラート概要取得
    
    アラートの統計情報を取得します。
    """
    try:
        summary = alert_svc.get_alert_summary()
        logger.debug("Retrieved alert summary")
        return summary
    except Exception as e:
        logger.error(f"Error getting alert summary: {str(e)}")
        raise HTTPException(status_code=500, detail="アラート概要の取得に失敗しました")

@router.get("/alerts/rules")
async def get_alert_rules(
    alert_svc: AlertService = Depends(get_alert_service),
    _: str = Depends(require_dashboard)
):
    """
    アラートルール一覧取得
    
    設定されているアラートルールの一覧を取得します。
    """
    try:
        rules = alert_svc.get_alert_rules()
        logger.debug(f"Retrieved {len(rules)} alert rules")
        return {"rules": rules, "total_count": len(rules)}
    except Exception as e:
        logger.error(f"Error getting alert rules: {str(e)}")
        raise HTTPException(status_code=500, detail="アラートルールの取得に失敗しました")

# Performance Monitoring Endpoints

@router.get("/performance/summary")
async def get_performance_summary(
    perf_svc: PerformanceService = Depends(get_performance_service),
    _: str = Depends(require_dashboard)
):
    """
    パフォーマンス概要取得
    
    システムパフォーマンスの概要を取得します。
    """
    try:
        summary = perf_svc.get_performance_summary()
        logger.debug("Retrieved performance summary")
        return summary
    except Exception as e:
        logger.error(f"Error getting performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail="パフォーマンス概要の取得に失敗しました")

@router.get("/performance/metrics")
async def get_performance_metrics(
    metric_name: Optional[str] = Query(None, description="メトリック名"),
    duration_minutes: int = Query(60, description="期間（分）"),
    perf_svc: PerformanceService = Depends(get_performance_service),
    _: str = Depends(require_dashboard)
):
    """
    パフォーマンスメトリック取得
    
    詳細なパフォーマンスメトリックを取得します。
    """
    try:
        metrics = perf_svc.metrics.get_metrics(metric_name, duration_minutes)
        
        if metric_name:
            summary = perf_svc.metrics.get_metric_summary(metric_name, duration_minutes)
            return {"metrics": metrics, "summary": summary}
        else:
            return {"metrics": metrics, "total_count": len(metrics)}
            
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="パフォーマンスメトリックの取得に失敗しました")

@router.get("/performance/api")
async def get_api_performance(
    endpoint: Optional[str] = Query(None, description="エンドポイント"),
    perf_svc: PerformanceService = Depends(get_performance_service),
    _: str = Depends(require_dashboard)
):
    """
    API パフォーマンス取得
    
    API エンドポイントのパフォーマンス統計を取得します。
    """
    try:
        performance = perf_svc.get_api_performance(endpoint)
        logger.debug(f"Retrieved API performance for: {endpoint or 'all'}")
        return performance
    except Exception as e:
        logger.error(f"Error getting API performance: {str(e)}")
        raise HTTPException(status_code=500, detail="API パフォーマンスの取得に失敗しました")

@router.post("/performance/optimize")
async def optimize_performance(
    perf_svc: PerformanceService = Depends(get_performance_service),
    _: str = Depends(require_admin)
):
    """
    パフォーマンス最適化実行
    
    システムパフォーマンスの最適化を実行します。
    """
    try:
        result = perf_svc.optimize_performance()
        logger.info("Performance optimization completed")
        return result
    except Exception as e:
        logger.error(f"Error optimizing performance: {str(e)}")
        raise HTTPException(status_code=500, detail="パフォーマンス最適化に失敗しました")

@router.get("/performance/cache/stats")
async def get_cache_stats(
    perf_svc: PerformanceService = Depends(get_performance_service),
    _: str = Depends(require_dashboard)
):
    """
    キャッシュ統計取得
    
    キャッシュの使用状況統計を取得します。
    """
    try:
        stats = perf_svc.cache.get_stats()
        logger.debug("Retrieved cache statistics")
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail="キャッシュ統計の取得に失敗しました")

@router.delete("/performance/cache")
async def clear_cache(
    perf_svc: PerformanceService = Depends(get_performance_service),
    _: str = Depends(require_admin)
):
    """
    キャッシュクリア
    
    すべてのキャッシュエントリをクリアします。
    """
    try:
        perf_svc.cache.clear()
        logger.info("Cache cleared")
        return {"success": True, "message": "キャッシュがクリアされました"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail="キャッシュのクリアに失敗しました")

# System Health Endpoints

@router.get("/health/detailed")
async def get_detailed_health(
    alert_svc: AlertService = Depends(get_alert_service),
    perf_svc: PerformanceService = Depends(get_performance_service),
    _: str = Depends(require_dashboard)
):
    """
    詳細ヘルスチェック
    
    システムの詳細な健全性情報を取得します。
    """
    try:
        # Get system performance
        system_perf = perf_svc.get_system_performance()
        
        # Get alert summary
        alert_summary = alert_svc.get_alert_summary()
        
        # Get cache stats
        cache_stats = perf_svc.cache.get_stats()
        
        # Calculate overall health score
        health_score = 100
        
        # Deduct points for high resource usage
        if system_perf["cpu"]["usage_percent"] > 80:
            health_score -= 20
        if system_perf["memory"]["usage_percent"] > 80:
            health_score -= 20
        if system_perf["disk"]["usage_percent"] > 90:
            health_score -= 30
            
        # Deduct points for unresolved alerts
        critical_alerts = alert_summary.get("critical_alerts_24h", 0)
        unresolved_alerts = alert_summary.get("unresolved_alerts", 0)
        health_score -= min(critical_alerts * 10, 30)
        health_score -= min(unresolved_alerts * 2, 20)
        
        health_score = max(health_score, 0)
        
        # Determine health status
        if health_score >= 80:
            health_status = "healthy"
        elif health_score >= 60:
            health_status = "warning"
        elif health_score >= 40:
            health_status = "degraded"
        else:
            health_status = "critical"
            
        return {
            "health_status": health_status,
            "health_score": health_score,
            "system_performance": system_perf,
            "alert_summary": alert_summary,
            "cache_statistics": cache_stats,
            "monitoring_active": alert_svc.monitoring_active,
            "timestamp": system_perf["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error getting detailed health: {str(e)}")
        raise HTTPException(status_code=500, detail="詳細ヘルスチェックに失敗しました")

def initialize_phase4_router(
    alert_svc: AlertService,
    perf_svc: PerformanceService
):
    """Initialize the Phase 4 router with service instances"""
    global alert_service, performance_service
    alert_service = alert_svc
    performance_service = perf_svc
    logger.info("Phase 4 router initialized with service instances")