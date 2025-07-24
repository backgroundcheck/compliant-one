"""
Compliant.one Logging Utilities
Centralized logging configuration for the platform
"""

import logging
import sys
from datetime import datetime
from typing import Optional

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Get configured logger instance
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Don't add handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Set level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

class ComplianceLogger:
    """
    Specialized logger for compliance operations
    Includes structured logging for audit trails
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger(f"compliance.{service_name}")
    
    def log_compliance_check(self, customer_id: str, recommendation: str, 
                           status: str, details: Optional[dict] = None):
        """Log compliance check result"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "customer_id": customer_id,
            "fatf_recommendation": recommendation,
            "status": status,
            "details": details or {}
        }
        
        if status in ["FAIL", "WARNING"]:
            self.logger.warning(f"Compliance Check: {log_data}")
        else:
            self.logger.info(f"Compliance Check: {log_data}")
    
    def log_security_event(self, event_type: str, details: dict):
        """Log security-related events"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "event_type": event_type,
            "details": details
        }
        
        self.logger.warning(f"Security Event: {log_data}")
    
    def log_audit_trail(self, action: str, user_id: str, resource: str, details: dict):
        """Log audit trail events"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "details": details
        }
        
        self.logger.info(f"Audit Trail: {log_data}")

def setup_compliance_logging():
    """Setup compliance-specific logging configuration"""
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add custom handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Compliance-specific formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S UTC'
    )
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # Set logging level for specific modules
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    return root_logger

# Initialize compliance logging on import
setup_compliance_logging()
