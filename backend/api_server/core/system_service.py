"""
System Service
Handles system monitoring and dashboard functionality
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Dict, Any

import psutil

from ..models.model_models import SystemStatus
from ..models.drone_models import DroneStatus

logger = logging.getLogger(__name__)


class SystemService:
    """System monitoring service for dashboard functionality"""
    
    def __init__(self):
        self.start_time = time.time()
        self.system_metrics = {}
        
    async def get_system_status(self, drone_manager, vision_service, model_service) -> SystemStatus:
        """
        Get comprehensive system status
        
        Args:
            drone_manager: Drone manager instance
            vision_service: Vision service instance  
            model_service: Model service instance
            
        Returns:
            SystemStatus with current system metrics
        """
        # Get system resource usage
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get system temperature (if available)
        temperature = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Try to get CPU temperature
                for name, entries in temps.items():
                    if entries and 'cpu' in name.lower():
                        temperature = entries[0].current
                        break
                # Fallback to first available temperature
                if temperature is None and temps:
                    temperature = list(temps.values())[0][0].current
        except:
            temperature = None
        
        # Get connected drones count
        try:
            drones = await drone_manager.get_available_drones()
            connected_drones = len([d for d in drones if d.status == "connected"])
        except:
            connected_drones = 0
        
        # Get active tracking count
        try:
            tracking_status = await vision_service.get_tracking_status()
            active_tracking = 1 if tracking_status.is_active else 0
        except:
            active_tracking = 0
        
        # Get running training jobs count
        try:
            active_jobs = await model_service.get_active_training_jobs()
            running_training_jobs = len(active_jobs)
        except:
            running_training_jobs = 0
        
        # Calculate uptime
        uptime = int(time.time() - self.start_time)
        
        return SystemStatus(
            cpu_usage=round(cpu_usage, 1),
            memory_usage=round(memory.percent, 1),
            disk_usage=round(disk.percent, 1),
            temperature=round(temperature, 1) if temperature else None,
            connected_drones=connected_drones,
            active_tracking=active_tracking,
            running_training_jobs=running_training_jobs,
            uptime=uptime,
            last_updated=datetime.now()
        )
    
    async def get_all_drone_statuses(self, drone_manager) -> List[DroneStatus]:
        """
        Get status of all drones for dashboard
        
        Args:
            drone_manager: Drone manager instance
            
        Returns:
            List of DroneStatus objects
        """
        try:
            drones = await drone_manager.get_available_drones()
            statuses = []
            
            for drone in drones:
                try:
                    status = await drone_manager.get_drone_status(drone.id)
                    statuses.append(status)
                except Exception as e:
                    logger.warning(f"Could not get status for drone {drone.id}: {str(e)}")
                    # Create a basic status for disconnected drone
                    basic_status = DroneStatus(
                        drone_id=drone.id,
                        connection_status="disconnected",
                        flight_status="landed",
                        battery_level=0,
                        last_updated=datetime.now()
                    )
                    statuses.append(basic_status)
            
            return statuses
            
        except Exception as e:
            logger.error(f"Error getting drone statuses: {str(e)}")
            return []
    
    async def get_system_metrics_history(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Get system metrics history for charts/graphs
        
        Args:
            duration_minutes: Duration of history to return
            
        Returns:
            Dictionary with historical metrics data
        """
        # In a real implementation, this would return stored historical data
        # For now, we'll return simulated recent data
        
        import random
        current_time = datetime.now()
        timestamps = []
        cpu_data = []
        memory_data = []
        
        # Generate sample data points every minute for the duration
        for i in range(duration_minutes, 0, -1):
            timestamp = current_time.timestamp() - (i * 60)
            timestamps.append(timestamp)
            
            # Simulate realistic varying metrics
            base_cpu = 35
            base_memory = 60
            cpu_data.append(base_cpu + random.uniform(-10, 15))
            memory_data.append(base_memory + random.uniform(-15, 20))
        
        return {
            "timestamps": timestamps,
            "cpu_usage": cpu_data,
            "memory_usage": memory_data,
            "duration_minutes": duration_minutes,
            "generated_at": current_time
        }
    
    async def get_service_health_status(self, drone_manager, vision_service, model_service, dataset_service) -> Dict[str, Any]:
        """
        Get health status of all services
        
        Args:
            drone_manager: Drone manager instance
            vision_service: Vision service instance
            model_service: Model service instance  
            dataset_service: Dataset service instance
            
        Returns:
            Dictionary with service health information
        """
        services = {}
        
        # Check drone manager
        try:
            await drone_manager.get_available_drones()
            services["drone_manager"] = {"status": "healthy", "error": None}
        except Exception as e:
            services["drone_manager"] = {"status": "unhealthy", "error": str(e)}
        
        # Check vision service
        try:
            models = vision_service.get_available_models()
            services["vision_service"] = {
                "status": "healthy", 
                "error": None,
                "available_models": len(models)
            }
        except Exception as e:
            services["vision_service"] = {"status": "unhealthy", "error": str(e)}
        
        # Check model service
        try:
            models = await model_service.get_models()
            active_jobs = await model_service.get_active_training_jobs()
            services["model_service"] = {
                "status": "healthy",
                "error": None,
                "total_models": len(models),
                "active_jobs": len(active_jobs)
            }
        except Exception as e:
            services["model_service"] = {"status": "unhealthy", "error": str(e)}
        
        # Check dataset service
        try:
            datasets = await dataset_service.get_datasets()
            services["dataset_service"] = {
                "status": "healthy",
                "error": None,
                "total_datasets": len(datasets)
            }
        except Exception as e:
            services["dataset_service"] = {"status": "unhealthy", "error": str(e)}
        
        # Overall health
        unhealthy_services = [name for name, info in services.items() 
                            if info["status"] == "unhealthy"]
        
        overall_status = "healthy" if not unhealthy_services else "degraded"
        
        return {
            "overall_status": overall_status,
            "services": services,
            "unhealthy_services": unhealthy_services,
            "checked_at": datetime.now()
        }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get detailed performance metrics
        
        Returns:
            Dictionary with performance information
        """
        # CPU information
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_percent_per_core = psutil.cpu_percent(percpu=True)
        
        # Memory information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network information
        network_io = psutil.net_io_counters()
        
        # Process information
        process_count = len(psutil.pids())
        
        return {
            "cpu": {
                "count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None,
                "usage_percent": round(psutil.cpu_percent(), 1),
                "usage_per_core": [round(p, 1) for p in cpu_percent_per_core]
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": round(memory.percent, 1)
            },
            "swap": {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_gb": round(swap.used / (1024**3), 2),
                "usage_percent": round(swap.percent, 1)
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round(disk.percent, 1),
                "read_mb": round(disk_io.read_bytes / (1024**2), 2) if disk_io else None,
                "write_mb": round(disk_io.write_bytes / (1024**2), 2) if disk_io else None
            },
            "network": {
                "bytes_sent_mb": round(network_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(network_io.bytes_recv / (1024**2), 2),
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv
            },
            "processes": {
                "count": process_count
            },
            "uptime_seconds": int(time.time() - self.start_time),
            "timestamp": datetime.now()
        }
    
    def get_uptime_seconds(self) -> int:
        """Get system uptime in seconds"""
        return int(time.time() - self.start_time)
    
    async def shutdown(self):
        """Shutdown the system service"""
        logger.info("System service shutdown complete")