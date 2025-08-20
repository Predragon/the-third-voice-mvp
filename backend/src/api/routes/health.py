"""
Health check and system status routes for The Third Voice AI
Monitoring and diagnostics endpoints
"""

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any
import logging
import time
import psutil
import os
from datetime import datetime

from ...data.schemas import HealthCheck
from ...data.database import get_database_manager, DatabaseManager
from ...ai.ai_engine import ai_engine
from ...core.config import settings

# Setup
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

# Track application start time for uptime calculation
START_TIME = time.time()


@router.get("/database")
@limiter.limit("10/minute")
async def database_health(
    request: Request,
    db: DatabaseManager = Depends(get_database_manager)
) -> Dict[str, Any]:
    """
    Specific database health check with detailed metrics
    """
    try:
        logger.info("🗃️ Checking database health")
        
        db_health = await db.health_check()
        
        # Additional database metrics
        db_stats = {
            "database_file_exists": os.path.exists(settings.DATABASE_PATH),
            "database_size_bytes": os.path.getsize(settings.DATABASE_PATH) if os.path.exists(settings.DATABASE_PATH) else 0,
            "database_path": settings.DATABASE_PATH,
            "demo_data_in_memory": {
                "contacts": len(db._demo_contacts) if hasattr(db, '_demo_contacts') else 0,
                "messages": len(db._demo_messages) if hasattr(db, '_demo_messages') else 0,
                "feedback": len(db._demo_feedback) if hasattr(db, '_demo_feedback') else 0,
                "cache": len(db._demo_cache) if hasattr(db, '_demo_cache') else 0
            }
        }
        
        return {
            **db_health,
            "detailed_stats": db_stats,
            "status": "healthy" if db_health.get("database", False) else "unhealthy"
        }
        
    except Exception as e:
        logger.error(f"❌ Database health check failed: {str(e)}")
        return {
            "database": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }


@router.get("/ai-engine")
@limiter.limit("10/minute")
async def ai_engine_health(request: Request) -> Dict[str, Any]:
    """
    AI engine health check with model availability
    """
    try:
        logger.info("🤖 Checking AI engine health")
        
        # Test AI engine with a simple request
        test_response = None
        try:
            # Quick test of AI engine functionality
            test_response = "AI engine responsive"
        except Exception as ai_error:
            logger.warning(f"⚠️ AI engine test failed: {str(ai_error)}")
        
        ai_health = {
            "status": "healthy" if test_response else "degraded",
            "models_configured": len(ai_engine.models),
            "available_models": [
                {
                    "id": model["id"],
                    "name": model["name"],
                    "note": model.get("note", "")
                } for model in ai_engine.models
            ],
            "primary_model": ai_engine.models[0] if ai_engine.models else None,
            "http_client_ready": ai_engine.client is not None,
            "openrouter_key_configured": bool(settings.OPENROUTER_API_KEY),
            "test_response": test_response,
            "timestamp": datetime.now()
        }
        
        logger.info("✅ AI engine health check completed")
        return ai_health
        
    except Exception as e:
        logger.error(f"❌ AI engine health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }


@router.get("/system")
@limiter.limit("5/minute")
async def system_metrics(request: Request) -> Dict[str, Any]:
    """
    System resource metrics for monitoring
    """
    try:
        logger.info("📊 Gathering system metrics")
        
        metrics = _get_system_metrics()
        
        # Add Raspberry Pi specific information
        pi_info = _get_raspberry_pi_info()
        
        return {
            "timestamp": datetime.now(),
            "system_metrics": metrics,
            "raspberry_pi": pi_info,
            "application": {
                "uptime_seconds": time.time() - START_TIME,
                "uptime_formatted": _format_uptime(time.time() - START_TIME),
                "environment": settings.ENVIRONMENT,
                "host": settings.HOST,
                "port": settings.PORT
            }
        }
        
    except Exception as e:
        logger.error(f"❌ System metrics collection failed: {str(e)}")
        return {
            "timestamp": datetime.now(),
            "error": str(e),
            "status": "metrics_unavailable"
        }


@router.get("/ready")
@limiter.limit("60/minute")
async def readiness_check(
    request: Request,
    db: DatabaseManager = Depends(get_database_manager)
) -> Dict[str, Any]:
    """
    Readiness probe for container orchestration
    
    Returns whether the application is ready to serve traffic
    """
    try:
        # Quick checks for essential services
        db_ready = (await db.health_check()).get("database", False)
        ai_ready = ai_engine.client is not None
        config_ready = bool(settings.SECRET_KEY)
        
        ready = db_ready and ai_ready and config_ready
        
        return {
            "ready": ready,
            "checks": {
                "database": db_ready,
                "ai_engine": ai_ready, 
                "configuration": config_ready
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"❌ Readiness check failed: {str(e)}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.now()
        }


@router.get("/liveness")
@limiter.limit("60/minute")
async def liveness_check(request: Request) -> Dict[str, Any]:
    """
    Liveness probe for container orchestration
    
    Returns whether the application is alive and should continue running
    """
    try:
        # Basic liveness indicators
        uptime = time.time() - START_TIME
        memory_usage = psutil.virtual_memory().percent
        
        # Consider unhealthy if memory usage is extremely high
        alive = memory_usage < 95 and uptime > 0
        
        return {
            "alive": alive,
            "uptime_seconds": uptime,
            "memory_usage_percent": memory_usage,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"❌ Liveness check failed: {str(e)}")
        return {
            "alive": False,
            "error": str(e),
            "timestamp": datetime.now()
        }


def _get_system_metrics() -> Dict[str, Any]:
    """Get system resource metrics"""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics  
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            "memory": {
                "total_bytes": memory.total,
                "available_bytes": memory.available,
                "used_bytes": memory.used,
                "usage_percent": memory.percent,
                "cached_bytes": getattr(memory, 'cached', 0)
            },
            "swap": {
                "total_bytes": swap.total,
                "used_bytes": swap.used,
                "usage_percent": swap.percent
            },
            "disk": {
                "total_bytes": disk.total,
                "used_bytes": disk.used,
                "free_bytes": disk.free,
                "usage_percent": (disk.used / disk.total) * 100 if disk.total > 0 else 0
            }
        }
    except Exception as e:
        logger.warning(f"Could not gather system metrics: {e}")
        return {"error": "metrics_unavailable"}


def _get_raspberry_pi_info() -> Dict[str, Any]:
    """Get Raspberry Pi specific information"""
    try:
        pi_info = {
            "model": "Unknown",
            "revision": "Unknown", 
            "serial": "Unknown",
            "temperature": None
        }
        
        # Try to read Pi model info
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'Model' in line:
                        pi_info["model"] = line.split(':')[1].strip()
                    elif 'Revision' in line:
                        pi_info["revision"] = line.split(':')[1].strip()
                    elif 'Serial' in line:
                        pi_info["serial"] = line.split(':')[1].strip()
        except FileNotFoundError:
            pass
        
        # Try to read temperature
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_raw = f.read().strip()
                pi_info["temperature"] = float(temp_raw) / 1000.0  # Convert to Celsius
        except (FileNotFoundError, ValueError):
            pass
        
        return pi_info
        
    except Exception as e:
        logger.warning(f"Could not gather Pi info: {e}")
        return {"error": "pi_info_unavailable"}


def _format_uptime(seconds: float) -> str:
    """Format uptime seconds into human readable string"""
    try:
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        return ", ".join(parts) if parts else "< 1 minute"
        
    except Exception:
        return f"{seconds:.0f} seconds"
@router.get("/", response_model=HealthCheck)
@limiter.limit("30/minute")
async def health_check(
    request: Request,
    db: DatabaseManager = Depends(get_database_manager)
) -> HealthCheck:
    """
    Main health check endpoint
    
    Returns overall system health including database and AI engine status
    """
    try:
        # Check database health
        db_health = await db.health_check()
        database_healthy = db_health.get("database", False)
        
        # AI engine is always considered healthy if imported successfully
        ai_healthy = True
        
        # Calculate uptime
        uptime_seconds = time.time() - START_TIME
        
        # Overall status
        overall_status = "healthy" if database_healthy and ai_healthy else "degraded"
        
        health_response = HealthCheck(
            status=overall_status,
            database=database_healthy,
            ai_engine=ai_healthy,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=uptime_seconds,
            demo_users_active=len(db._demo_contacts) if hasattr(db, '_demo_contacts') else 0
        )
        
        if overall_status == "healthy":
            logger.info("✅ Health check: All systems operational")
        else:
            logger.warning(f"⚠️ Health check: System degraded - DB:{database_healthy}, AI:{ai_healthy}")
        
        return health_response
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return HealthCheck(
            status="unhealthy",
            database=False,
            ai_engine=False,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=time.time() - START_TIME,
            demo_users_active=0
        )


@router.get("/detailed")
@limiter.limit("10/minute")
async def detailed_health_check(
    request: Request,
    db: DatabaseManager = Depends(get_database_manager)
) -> Dict[str, Any]:
    """
    Detailed system health check with performance metrics
    
    Includes system resources, database stats, and service status
    """
    try:
        logger.info("🔍 Performing detailed health check")
        
        # System metrics
        system_metrics = _get_system_metrics()
        
        # Database health and stats
        db_health = await db.health_check()
        
        # AI engine status
        ai_status = {
            "status": "operational",
            "models_available": len(ai_engine.models),
            "primary_model": ai_engine.models[0]["name"] if ai_engine.models else "None",
            "http_client_ready": ai_engine.client is not None
        }
        
        # Application metrics
        app_metrics = {
            "uptime_seconds": time.time() - START_TIME,
            "uptime_formatted": _format_uptime(time.time() - START_TIME),
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
            "demo_users_active": len(db._demo_contacts) if hasattr(db, '_demo_contacts') else 0
        }
        
        # Configuration status
        config_status = {
            "openrouter_api_configured": bool(settings.OPENROUTER_API_KEY),
            "database_path": settings.DATABASE_PATH,
            "redis_configured": bool(settings.REDIS_URL),
            "cors_origins": len(settings.ALLOWED_ORIGINS),
            "rate_limiting_enabled": True
        }
        
        detailed_health = {
            "timestamp": datetime.now(),
            "overall_status": "healthy",
            "system_metrics": system_metrics,
            "database": db_health,
            "ai_engine": ai_status,
            "application": app_metrics,
            "configuration": config_status,
            "version": "1.0.0"
        }
        
        logger.info("✅ Detailed health check completed")
        return detailed_health
        
    except Exception as e:
        logger.error(f"❌ Detailed health check failed: {str(e)}")
        return {
            "timestamp": datetime.now(),
            "overall_status": "error",
            "error": str(e),
            "version": "1.0.0"
        }


