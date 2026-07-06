"""
Logging Service - Enterprise-grade logging and error tracking
"""

import logging
import sys
import os
from datetime import datetime
from utils.time_utils import utc_now
from typing import Optional, Dict, Any
import json
import traceback
from pathlib import Path

from utils.local_paths import ensure_local_dirs, local_path

ensure_local_dirs()
LOG_DIR = local_path("logs")


class StructuredLogger:
    """Structured logging for enterprise applications"""
    
    def __init__(self, name: str = "elder_company"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler for errors
        error_file = LOG_DIR / "error.log"
        error_handler = logging.FileHandler(error_file)
        error_handler.setLevel(logging.ERROR)
        error_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        error_handler.setFormatter(error_format)
        self.logger.addHandler(error_handler)
        
        # File handler for all logs
        all_logs_file = LOG_DIR / "app.log"
        all_logs_handler = logging.FileHandler(all_logs_file)
        all_logs_handler.setLevel(logging.INFO)
        all_logs_handler.setFormatter(error_format)
        self.logger.addHandler(all_logs_handler)
    
    def log_translation(
        self,
        user_id: str,
        org_id: Optional[str],
        source_lang: str,
        target_lang: str,
        text_length: int,
        translation_time_ms: int,
        success: bool,
        error: Optional[str] = None
    ):
        """Log translation event"""
        log_data = {
            "event": "translation",
            "timestamp": utc_now().isoformat(),
            "user_id": user_id,
            "org_id": org_id,
            "source_language": source_lang,
            "target_language": target_lang,
            "text_length": text_length,
            "translation_time_ms": translation_time_ms,
            "success": success,
            "error": error
        }
        
        if success:
            self.logger.info(f"Translation: {json.dumps(log_data)}")
        else:
            self.logger.error(f"Translation failed: {json.dumps(log_data)}")
    
    def log_api_request(
        self,
        endpoint: str,
        method: str,
        user_id: Optional[str],
        org_id: Optional[str],
        status_code: int,
        response_time_ms: int,
        error: Optional[str] = None
    ):
        """Log API request"""
        log_data = {
            "event": "api_request",
            "timestamp": utc_now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "org_id": org_id,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "error": error
        }
        
        # Sanitize sensitive information before logging
        from utils.security import sanitize_for_logging
        sanitized_data = sanitize_for_logging(log_data)
        
        if status_code >= 400:
            self.logger.warning(f"API request: {json.dumps(sanitized_data)}")
        else:
            self.logger.info(f"API request: {json.dumps(sanitized_data)}")
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None
    ):
        """Log error with context (with sensitive data sanitization)"""
        from utils.security import sanitize_for_logging, redact_local_paths
        
        error_data = {
            "event": "error",
            "timestamp": utc_now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": redact_local_paths(traceback.format_exc()),
            "user_id": user_id,
            "org_id": org_id,
            "context": context or {}
        }
        
        # Sanitize sensitive information before logging
        sanitized_data = sanitize_for_logging(error_data)
        self.logger.error(f"Error: {json.dumps(sanitized_data, default=str)}")
    
    def log_organization_event(
        self,
        event_type: str,
        org_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log organization-related events"""
        log_data = {
            "event": "organization",
            "event_type": event_type,
            "timestamp": utc_now().isoformat(),
            "org_id": org_id,
            "details": details or {}
        }
        
        self.logger.info(f"Organization event: {json.dumps(log_data)}")
    
    def log_warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        warning_data = {
            "event": "warning",
            "timestamp": utc_now().isoformat(),
            "message": message,
            "context": context or {}
        }
        self.logger.warning(f"Warning: {json.dumps(warning_data)}")
    
    def log_info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Log info message"""
        info_data = {
            "event": "info",
            "timestamp": utc_now().isoformat(),
            "message": message,
            "context": context or {}
        }
        self.logger.info(f"Info: {json.dumps(info_data)}")


# Global logger instance
logger = StructuredLogger()
