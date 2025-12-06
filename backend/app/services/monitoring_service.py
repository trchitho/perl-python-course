"""
Monitoring Service - System, Container, and Component Status Tracking

This module provides comprehensive monitoring capabilities for the e-learning platform.
It tracks system health, container status, and component metrics.
"""

import psutil
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import threading
import json


# ========================= Data Models =========================

@dataclass
class SystemMetrics:
    """System-level metrics"""
    timestamp: str
    uptime_seconds: int
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    memory_available_mb: int
    disk_free_gb: int
    process_count: int
    active_connections: int = 0
    requests_per_minute: int = 0
    error_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ContainerStatus:
    """Container/Service status"""
    name: str
    status: str  # running, stopped, error, unknown
    timestamp: str
    memory_usage_mb: int = 0
    memory_limit_mb: int = 0
    cpu_percent: float = 0.0
    uptime_seconds: int = 0
    restart_count: int = 0
    last_error: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ComponentStatus:
    """Component/Service status"""
    name: str
    status: str  # healthy, warning, degraded, critical, unknown
    timestamp: str
    response_time_ms: float = 0.0
    error_count: int = 0
    success_count: int = 0
    last_check_time: str = ""
    details: Dict = None
    
    def to_dict(self):
        data = asdict(self)
        if self.details:
            data['details'] = self.details
        return data


@dataclass
class OverallStatus:
    """Overall system status"""
    status: str  # healthy, warning, degraded, critical
    system: SystemMetrics
    containers: List[ContainerStatus]
    components: List[ComponentStatus]
    timestamp: str
    alerts: List[Dict]
    
    def to_dict(self):
        return {
            'status': self.status,
            'system': self.system.to_dict(),
            'containers': [c.to_dict() for c in self.containers],
            'components': [c.to_dict() for c in self.components],
            'timestamp': self.timestamp,
            'alerts': self.alerts
        }


# ========================= Status Aggregation =========================

class StatusAggregator:
    """Aggregate multiple statuses to determine overall health"""
    
    STATUS_PRIORITY = {
        'critical': 4,
        'degraded': 3,
        'warning': 2,
        'healthy': 1,
        'running': 1,
        'stopped': 3,
        'error': 4,
        'unknown': 0
    }
    
    @classmethod
    def aggregate(cls, *statuses: str) -> str:
        """
        Combine multiple statuses
        Returns the highest priority status
        """
        if not statuses:
            return 'unknown'
        
        max_status = max(statuses, key=lambda s: cls.STATUS_PRIORITY.get(s, 0))
        return max_status
    
    @classmethod
    def get_http_code(cls, status: str) -> int:
        """Convert status to HTTP code"""
        codes = {
            'healthy': 200,
            'warning': 202,
            'degraded': 203,
            'critical': 503,
            'unknown': 418
        }
        return codes.get(status, 418)


# ========================= Alert Management =========================

class AlertManager:
    """Manage alerts based on thresholds"""
    
    THRESHOLDS = {
        'cpu_usage': {'warning': 70, 'critical': 90},
        'memory_usage': {'warning': 75, 'critical': 90},
        'disk_usage': {'warning': 80, 'critical': 95},
        'error_rate': {'warning': 1, 'critical': 5},
        'response_time_ms': {'warning': 500, 'critical': 2000},
        'db_connections': {'warning': 80, 'critical': 100}
    }
    
    def __init__(self):
        self.active_alerts: Dict[str, Dict] = {}
    
    def check_metrics(self, metrics: SystemMetrics) -> List[Dict]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # Check CPU
        if metrics.cpu_percent > self.THRESHOLDS['cpu_usage']['critical']:
            alerts.append(self._create_alert(
                'critical', 
                f"CPU usage critical: {metrics.cpu_percent}%"
            ))
        elif metrics.cpu_percent > self.THRESHOLDS['cpu_usage']['warning']:
            alerts.append(self._create_alert(
                'warning',
                f"CPU usage high: {metrics.cpu_percent}%"
            ))
        
        # Check Memory
        if metrics.memory_percent > self.THRESHOLDS['memory_usage']['critical']:
            alerts.append(self._create_alert(
                'critical',
                f"Memory usage critical: {metrics.memory_percent}%"
            ))
        elif metrics.memory_percent > self.THRESHOLDS['memory_usage']['warning']:
            alerts.append(self._create_alert(
                'warning',
                f"Memory usage high: {metrics.memory_percent}%"
            ))
        
        # Check Disk
        if metrics.disk_percent > self.THRESHOLDS['disk_usage']['critical']:
            alerts.append(self._create_alert(
                'critical',
                f"Disk usage critical: {metrics.disk_percent}%"
            ))
        elif metrics.disk_percent > self.THRESHOLDS['disk_usage']['warning']:
            alerts.append(self._create_alert(
                'warning',
                f"Disk usage high: {metrics.disk_percent}%"
            ))
        
        # Check Error Rate
        if metrics.error_rate > self.THRESHOLDS['error_rate']['critical']:
            alerts.append(self._create_alert(
                'critical',
                f"Error rate critical: {metrics.error_rate}%"
            ))
        elif metrics.error_rate > self.THRESHOLDS['error_rate']['warning']:
            alerts.append(self._create_alert(
                'warning',
                f"Error rate high: {metrics.error_rate}%"
            ))
        
        return alerts
    
    def _create_alert(self, severity: str, message: str) -> Dict:
        """Create alert dictionary"""
        return {
            'severity': severity,
            'message': message,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'id': f"{severity}_{int(time.time())}"
        }


# ========================= System Monitor =========================

class SystemMonitor:
    """Monitor system-level metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times: List[float] = []
    
    def get_metrics(self) -> SystemMetrics:
        """Collect system metrics"""
        uptime = int(time.time() - self.start_time)
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process count
        process_count = len(psutil.pids())
        
        # Calculate averages
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        error_rate = (self.error_count / max(self.request_count, 1)) * 100 if self.request_count > 0 else 0
        
        return SystemMetrics(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            uptime_seconds=uptime,
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            memory_available_mb=memory.available // (1024 * 1024),
            disk_free_gb=disk.free // (1024 * 1024 * 1024),
            process_count=process_count,
            avg_response_time_ms=avg_response_time,
            error_rate=error_rate
        )
    
    def record_request(self, response_time_ms: float, is_error: bool = False):
        """Record API request"""
        self.request_count += 1
        if is_error:
            self.error_count += 1
        self.response_times.append(response_time_ms)
        
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]


# ========================= Container Monitor =========================

class ContainerMonitor:
    """Monitor container/service status"""
    
    def __init__(self):
        self.containers: Dict[str, ContainerStatus] = {}
    
    def register_container(self, name: str, status: str = 'running'):
        """Register a container for monitoring"""
        self.containers[name] = ContainerStatus(
            name=name,
            status=status,
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    def update_status(self, name: str, status: str, **kwargs):
        """Update container status"""
        if name not in self.containers:
            self.register_container(name)
        
        container = self.containers[name]
        container.status = status
        container.timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Update optional fields
        if 'memory_usage_mb' in kwargs:
            container.memory_usage_mb = kwargs['memory_usage_mb']
        if 'memory_limit_mb' in kwargs:
            container.memory_limit_mb = kwargs['memory_limit_mb']
        if 'cpu_percent' in kwargs:
            container.cpu_percent = kwargs['cpu_percent']
        if 'uptime_seconds' in kwargs:
            container.uptime_seconds = kwargs['uptime_seconds']
        if 'last_error' in kwargs:
            container.last_error = kwargs['last_error']
    
    def get_all_containers(self) -> List[ContainerStatus]:
        """Get all containers"""
        return list(self.containers.values())


# ========================= Component Monitor =========================

class ComponentMonitor:
    """Monitor component/service health"""
    
    def __init__(self):
        self.components: Dict[str, ComponentStatus] = {}
    
    def register_component(self, name: str):
        """Register a component for monitoring"""
        self.components[name] = ComponentStatus(
            name=name,
            status='unknown',
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    def update_status(self, name: str, status: str, **kwargs):
        """Update component status"""
        if name not in self.components:
            self.register_component(name)
        
        component = self.components[name]
        component.status = status
        component.timestamp = datetime.utcnow().isoformat() + 'Z'
        component.last_check_time = datetime.utcnow().isoformat() + 'Z'
        
        # Update optional fields
        if 'response_time_ms' in kwargs:
            component.response_time_ms = kwargs['response_time_ms']
        if 'error_count' in kwargs:
            component.error_count = kwargs['error_count']
        if 'success_count' in kwargs:
            component.success_count = kwargs['success_count']
        if 'details' in kwargs:
            component.details = kwargs['details']
    
    def get_all_components(self) -> List[ComponentStatus]:
        """Get all components"""
        return list(self.components.values())


# ========================= Monitoring Service =========================

class MonitoringService:
    """Main monitoring service - combines all monitors"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.container_monitor = ContainerMonitor()
        self.component_monitor = ComponentMonitor()
        self.alert_manager = AlertManager()
        self.status_aggregator = StatusAggregator()
    
    def initialize_containers(self):
        """Initialize container monitoring"""
        self.container_monitor.register_container('backend', 'running')
        self.container_monitor.register_container('database', 'running')
    
    def initialize_components(self):
        """Initialize component monitoring"""
        self.component_monitor.register_component('api-auth')
        self.component_monitor.register_component('api-quiz')
        self.component_monitor.register_component('api-courses')
        self.component_monitor.register_component('database-connection')
    
    def get_overall_status(self) -> OverallStatus:
        """Get overall system status"""
        # Collect metrics
        system_metrics = self.system_monitor.get_metrics()
        containers = self.container_monitor.get_all_containers()
        components = self.component_monitor.get_all_components()
        
        # Generate alerts
        alerts = self.alert_manager.check_metrics(system_metrics)
        
        # Aggregate status
        statuses = [
            system_metrics.cpu_percent < 70 and 'healthy' or 'warning',
            system_metrics.memory_percent < 75 and 'healthy' or 'warning',
            system_metrics.disk_percent < 80 and 'healthy' or 'warning'
        ]
        statuses.extend([c.status for c in containers])
        statuses.extend([c.status for c in components])
        
        overall_status = self.status_aggregator.aggregate(*statuses)
        
        return OverallStatus(
            status=overall_status,
            system=system_metrics,
            containers=containers,
            components=components,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            alerts=alerts
        )
    
    def record_request(self, endpoint: str, response_time_ms: float, is_error: bool = False):
        """Record request for monitoring"""
        self.system_monitor.record_request(response_time_ms, is_error)


# ========================= Global Instance =========================

# Create global monitoring service instance
monitoring_service = MonitoringService()

# Initialize
monitoring_service.initialize_containers()
monitoring_service.initialize_components()

print("[Monitoring] Service initialized")
print("[Monitoring] Containers registered:", len(monitoring_service.container_monitor.containers))
print("[Monitoring] Components registered:", len(monitoring_service.component_monitor.components))
