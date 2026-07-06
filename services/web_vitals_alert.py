"""
Web Vitals Alert Service - Alert thresholds and notifications
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.time_utils import utc_now
from enum import Enum
from config.settings import settings


class AlertLevel(Enum):
    """Alert level"""
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


class WebVitalsAlertService:
    """Service for Web Vitals alerts"""
    
    def _get_default_thresholds(self):
        """Get default thresholds from settings"""
        from config.settings import settings
        return {
            "LCP": {
                "good": settings.web_vitals_lcp_good,
                "needs_improvement": settings.web_vitals_lcp_needs_improvement,
                "poor": float('inf')
            },
            "FID": {
                "good": settings.web_vitals_fid_good,
                "needs_improvement": settings.web_vitals_fid_needs_improvement,
                "poor": float('inf')
            },
            "CLS": {
                "good": settings.web_vitals_cls_good,
                "needs_improvement": settings.web_vitals_cls_needs_improvement,
                "poor": float('inf')
            },
            "FCP": {
                "good": settings.web_vitals_fcp_good,
                "needs_improvement": settings.web_vitals_fcp_needs_improvement,
                "poor": float('inf')
            },
            "TTFB": {
                "good": settings.web_vitals_ttfb_good,
                "needs_improvement": settings.web_vitals_ttfb_needs_improvement,
                "poor": float('inf')
            },
            "TTI": {
                "good": settings.web_vitals_tti_good,
                "needs_improvement": settings.web_vitals_tti_needs_improvement,
                "poor": float('inf')
            }
        }
    
    def __init__(self, custom_thresholds: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialize Web Vitals alert service
        
        Args:
            custom_thresholds: Custom thresholds to override defaults
        """
        self.thresholds = self._get_default_thresholds()
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)
        
        # Load from environment if available
        self._load_thresholds_from_env()
        
        # Alert history
        self.alert_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    def _load_thresholds_from_env(self):
        """Load thresholds from environment variables"""
        for metric in self.thresholds.keys():
            good_key = f"WEB_VITALS_{metric}_GOOD"
            needs_improvement_key = f"WEB_VITALS_{metric}_NEEDS_IMPROVEMENT"
            
            if os.getenv(good_key):
                self.thresholds[metric]["good"] = float(os.getenv(good_key))
            if os.getenv(needs_improvement_key):
                self.thresholds[metric]["needs_improvement"] = float(os.getenv(needs_improvement_key))
    
    def check_metric(self, metric_name: str, value: float) -> Dict[str, Any]:
        """
        Check a metric value against thresholds
        
        Args:
            metric_name: Metric name (LCP, FID, CLS, etc.)
            value: Metric value
        
        Returns:
            Dict with alert level and details
        """
        threshold = self.thresholds.get(metric_name)
        if not threshold:
            return {
                "metric": metric_name,
                "value": value,
                "level": AlertLevel.GOOD.value,
                "alert": False,
                "message": f"No threshold defined for {metric_name}"
            }
        
        # Determine alert level
        if value <= threshold["good"]:
            level = AlertLevel.GOOD
            alert = False
        elif value <= threshold["needs_improvement"]:
            level = AlertLevel.NEEDS_IMPROVEMENT
            alert = os.getenv("WEB_VITALS_ALERT_NEEDS_IMPROVEMENT", "false").lower() == "true"
        else:
            level = AlertLevel.POOR
            alert = True
        
        result = {
            "metric": metric_name,
            "value": value,
            "level": level.value,
            "alert": alert,
            "threshold": threshold,
            "message": self._get_message(metric_name, value, level)
        }
        
        # Trigger alert if needed
        if alert:
            self._trigger_alert(result)
        
        return result
    
    def check_metrics(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Check multiple metrics
        
        Args:
            metrics: Dict of metric_name -> value
        
        Returns:
            Dict with all metric checks and summary
        """
        results = {}
        alerts = []
        
        for metric_name, value in metrics.items():
            result = self.check_metric(metric_name, value)
            results[metric_name] = result
            if result.get("alert"):
                alerts.append(result)
        
        return {
            "results": results,
            "alerts": alerts,
            "alert_count": len(alerts),
            "timestamp": utc_now().isoformat()
        }
    
    def _get_message(self, metric_name: str, value: float, level: AlertLevel) -> str:
        """Generate alert message"""
        threshold = self.thresholds[metric_name]
        
        if level == AlertLevel.GOOD:
            return f"{metric_name} performing well: {value}"
        elif level == AlertLevel.NEEDS_IMPROVEMENT:
            return f"{metric_name} needs improvement: {value} (threshold: {threshold['needs_improvement']})"
        else:
            return f"{metric_name} poor performance: {value} (threshold: {threshold['needs_improvement']})"
    
    def _trigger_alert(self, alert_data: Dict[str, Any]):
        """Trigger alert notification"""
        alert_record = {
            **alert_data,
            "timestamp": utc_now().isoformat(),
            "notified": False
        }
        
        # Add to history
        self.alert_history.append(alert_record)
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        # Send notification
        try:
            from services.notification_service import get_notification_service
            notification = get_notification_service()
            
            subject = f"Web Vitals alert: {alert_data['metric']} - {alert_data['level']}"
            body = f"""
Web Vitals performance alert

Metric: {alert_data['metric']}
Current value: {alert_data['value']}
Alert level: {alert_data['level']}
Message: {alert_data['message']}
Time: {alert_record['timestamp']}

Thresholds:
- Good: {alert_data['threshold']['good']}
- Needs improvement: {alert_data['threshold']['needs_improvement']}
"""
            html_body = f"""
<h2>Web Vitals performance alert</h2>
<p><strong>Metric:</strong> {alert_data['metric']}</p>
<p><strong>Current value:</strong> {alert_data['value']}</p>
<p><strong>Alert level:</strong> {alert_data['level']}</p>
<p><strong>Message:</strong> {alert_data['message']}</p>
<p><strong>Time:</strong> {alert_record['timestamp']}</p>
<h3>Threshold</h3>
<ul>
    <li>Good: {alert_data['threshold']['good']}</li>
    <li>Needs improvement: {alert_data['threshold']['needs_improvement']}</li>
</ul>
"""
            
            admin_email = os.getenv("ADMIN_EMAIL")
            if admin_email:
                notification.send_email(admin_email, subject, body, html_body)
                alert_record["notified"] = True
        except Exception as e:
            print(f"Failed to send Web Vitals alert: {e}")
    
    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        return self.alert_history[-limit:]
    
    def get_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get current thresholds"""
        return self.thresholds.copy()
    
    def update_thresholds(self, metric: str, thresholds: Dict[str, float]):
        """Update thresholds for a metric"""
        if metric in self.thresholds:
            self.thresholds[metric].update(thresholds)


# Global alert service instance
_alert_service: Optional[WebVitalsAlertService] = None


def get_web_vitals_alert_service() -> WebVitalsAlertService:
    """Get global Web Vitals alert service instance"""
    global _alert_service
    if _alert_service is None:
        _alert_service = WebVitalsAlertService()
    return _alert_service
