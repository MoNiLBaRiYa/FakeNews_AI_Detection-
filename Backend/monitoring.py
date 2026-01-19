"""Monitoring and alerting system."""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitor application health and send alerts."""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'failed_requests': 0,
            'slow_requests': 0,
            'errors': [],
            'last_check': datetime.utcnow(),
            'uptime_start': datetime.utcnow()
        }
        self.thresholds = {
            'error_rate': 5.0,  # 5% error rate
            'slow_request_rate': 10.0,  # 10% slow requests
            'response_time': 5.0  # 5 seconds
        }
        self.alert_cooldown = 300  # 5 minutes between alerts
        self.last_alert = {}
    
    def record_request(self, response_time: float, status_code: int):
        """
        Record a request.
        
        Args:
            response_time: Request response time in seconds
            status_code: HTTP status code
        """
        self.metrics['total_requests'] += 1
        
        if status_code >= 400:
            self.metrics['failed_requests'] += 1
        
        if response_time > self.thresholds['response_time']:
            self.metrics['slow_requests'] += 1
        
        # Check if alert needed
        self._check_alerts()
    
    def record_error(self, error: str, context: dict = None):
        """
        Record an error.
        
        Args:
            error: Error message
            context: Additional context
        """
        self.metrics['errors'].append({
            'error': error,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Keep only last 100 errors
        if len(self.metrics['errors']) > 100:
            self.metrics['errors'] = self.metrics['errors'][-100:]
        
        logger.error(f"Error recorded: {error}")
    
    def get_health_status(self) -> Dict:
        """
        Get current health status.
        
        Returns:
            Dictionary with health metrics
        """
        total = self.metrics['total_requests']
        failed = self.metrics['failed_requests']
        slow = self.metrics['slow_requests']
        
        error_rate = (failed / total * 100) if total > 0 else 0
        slow_rate = (slow / total * 100) if total > 0 else 0
        
        uptime = datetime.utcnow() - self.metrics['uptime_start']
        
        status = 'healthy'
        if error_rate > self.thresholds['error_rate']:
            status = 'unhealthy'
        elif slow_rate > self.thresholds['slow_request_rate']:
            status = 'degraded'
        
        return {
            'status': status,
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_human': str(uptime),
            'total_requests': total,
            'failed_requests': failed,
            'slow_requests': slow,
            'error_rate': round(error_rate, 2),
            'slow_request_rate': round(slow_rate, 2),
            'recent_errors': self.metrics['errors'][-10:],
            'last_check': self.metrics['last_check'].isoformat()
        }
    
    def _check_alerts(self):
        """Check if alerts need to be sent."""
        total = self.metrics['total_requests']
        if total < 10:  # Need minimum requests
            return
        
        failed = self.metrics['failed_requests']
        slow = self.metrics['slow_requests']
        
        error_rate = (failed / total * 100)
        slow_rate = (slow / total * 100)
        
        # Check error rate
        if error_rate > self.thresholds['error_rate']:
            self._send_alert(
                'High Error Rate',
                f'Error rate is {error_rate:.2f}% (threshold: {self.thresholds["error_rate"]}%)'
            )
        
        # Check slow request rate
        if slow_rate > self.thresholds['slow_request_rate']:
            self._send_alert(
                'High Slow Request Rate',
                f'Slow request rate is {slow_rate:.2f}% (threshold: {self.thresholds["slow_request_rate"]}%)'
            )
    
    def _send_alert(self, alert_type: str, message: str):
        """
        Send alert (email, SMS, etc.).
        
        Args:
            alert_type: Type of alert
            message: Alert message
        """
        # Check cooldown
        now = time.time()
        if alert_type in self.last_alert:
            if now - self.last_alert[alert_type] < self.alert_cooldown:
                return  # Still in cooldown
        
        self.last_alert[alert_type] = now
        
        # Log alert
        logger.warning(f"ALERT: {alert_type} - {message}")
        
        # Send email alert (if configured)
        self._send_email_alert(alert_type, message)
    
    def _send_email_alert(self, alert_type: str, message: str):
        """
        Send email alert.
        
        Args:
            alert_type: Type of alert
            message: Alert message
        """
        email_enabled = os.getenv('ALERT_EMAIL_ENABLED', 'False').lower() == 'true'
        if not email_enabled:
            return
        
        try:
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_user = os.getenv('SMTP_USER', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')
            alert_email = os.getenv('ALERT_EMAIL', '')
            
            if not all([smtp_user, smtp_password, alert_email]):
                return
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = alert_email
            msg['Subject'] = f'[ALERT] {alert_type} - Fake News Detector'
            
            body = f"""
            Alert Type: {alert_type}
            Message: {message}
            Time: {datetime.utcnow().isoformat()}
            
            Health Status:
            {self.get_health_status()}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Alert email sent: {alert_type}")
        
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def reset_metrics(self):
        """Reset metrics (for testing or periodic reset)."""
        self.metrics = {
            'total_requests': 0,
            'failed_requests': 0,
            'slow_requests': 0,
            'errors': [],
            'last_check': datetime.utcnow(),
            'uptime_start': self.metrics['uptime_start']  # Keep uptime
        }
        logger.info("Metrics reset")

# Global health monitor
health_monitor = HealthMonitor()

def get_health_monitor():
    """Get global health monitor instance."""
    return health_monitor
