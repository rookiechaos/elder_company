"""
Task Queue Service - Background task processing
"""

import os
import uuid
import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from utils.time_utils import utc_now
from enum import Enum
import threading
from collections import deque


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskQueue:
    """Simple in-memory task queue (for development)"""
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.task_queue: deque = deque()
        self.workers: list = []
        self.running = False
        self.lock = threading.Lock()
    
    def start(self):
        """Start task queue workers"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True, name=f"TaskWorker-{i}")
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop task queue workers"""
        self.running = False
        for worker in self.workers:
            worker.join(timeout=1)
        self.workers.clear()
    
    def add_task(
        self,
        task_type: str,
        task_data: Dict[str, Any],
        callback: Optional[Callable] = None
    ) -> str:
        """
        Add a task to the queue
        
        Args:
            task_type: Type of task (e.g., 'image_optimize', 'batch_process')
            task_data: Task data
            callback: Optional callback function
        
        Returns:
            Task ID
        """
        task_id = f"{task_type}_{uuid.uuid4().hex[:12]}"
        
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "task_data": task_data,
            "status": TaskStatus.PENDING.value,
            "created_at": utc_now().isoformat(),
            "callback": callback
        }
        
        with self.lock:
            self.tasks[task_id] = task
            self.task_queue.append(task_id)
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                # Remove callback from response (not serializable)
                result = {k: v for k, v in task.items() if k != "callback"}
                return result
            return None
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Update task status"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = status.value
                self.tasks[task_id]["updated_at"] = utc_now().isoformat()
                
                if result:
                    self.tasks[task_id]["result"] = result
                if error:
                    self.tasks[task_id]["error"] = error
                
                if status == TaskStatus.COMPLETED:
                    self.tasks[task_id]["completed_at"] = utc_now().isoformat()
                elif status == TaskStatus.FAILED:
                    self.tasks[task_id]["failed_at"] = utc_now().isoformat()
    
    def _worker(self):
        """Worker thread that processes tasks"""
        while self.running:
            task_id = None
            try:
                with self.lock:
                    if self.task_queue:
                        task_id = self.task_queue.popleft()
                
                if task_id:
                    self._process_task(task_id)
                else:
                    import time
                    time.sleep(0.1)  # Wait a bit before checking again
            except Exception as e:
                if task_id:
                    self.update_task_status(task_id, TaskStatus.FAILED, error=str(e))
    
    def _process_task(self, task_id: str):
        """Process a single task"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return
        
        self.update_task_status(task_id, TaskStatus.PROCESSING)
        
        try:
            task_type = task["task_type"]
            task_data = task["task_data"]
            callback = task.get("callback")
            
            # Execute task
            if callback:
                result = callback(task_data)
            else:
                result = self._default_task_handler(task_type, task_data)
            
            self.update_task_status(task_id, TaskStatus.COMPLETED, result=result)
            
            # Send notification on completion
            try:
                from services.notification_service import get_notification_service
                notification = get_notification_service()
                notification.notify_task_completion(
                    task_id=task_id,
                    task_type=task_type,
                    result=result
                )
            except (ImportError, AttributeError) as notify_error:
                # Don't fail task if notification service is not available
                from services.logging_service import logger
                logger.log_warning(
                    f"Notification service not available: {notify_error}",
                    {"task_id": task_id, "task_type": task_type}
                )
            except Exception as notify_error:
                # Don't fail task if notification fails
                from services.logging_service import logger
                logger.log_warning(
                    f"Failed to send notification: {notify_error}",
                    {"task_id": task_id, "task_type": task_type}
                )
        except ValueError as e:
            # Validation errors
            self.update_task_status(task_id, TaskStatus.FAILED, error=str(e))
            self._send_failure_notification(task_id, task_type, str(e))
        except (ConnectionError, TimeoutError) as e:
            # Network-related errors
            self.update_task_status(task_id, TaskStatus.FAILED, error=str(e))
            self._send_failure_notification(task_id, task_type, str(e))
        except Exception as e:
            # Catch-all for unexpected errors
            self.update_task_status(task_id, TaskStatus.FAILED, error=str(e))
            self._send_failure_notification(task_id, task_type, str(e))
    
    def _send_failure_notification(self, task_id: str, task_type: str, error: str) -> None:
        """Send failure notification (helper method)"""
        try:
            from services.notification_service import get_notification_service
            notification = get_notification_service()
            notification.notify_task_failure(
                task_id=task_id,
                task_type=task_type,
                error=error
            )
        except (ImportError, AttributeError) as notify_error:
            # Notification service not available
            from services.logging_service import logger
            logger.log_warning(
                f"Notification service not available: {notify_error}",
                {"task_id": task_id, "task_type": task_type}
            )
        except Exception as notify_error:
            from services.logging_service import logger
            logger.log_warning(
                f"Failed to send failure notification: {notify_error}",
                {"task_id": task_id, "task_type": task_type}
            )
    
    def _default_task_handler(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default task handler for processing tasks.
        
        Args:
            task_type: Type of task to process
            task_data: Task data dictionary
            
        Returns:
            Dictionary containing task result
            
        Raises:
            ValueError: If task type is unknown
        """
        if task_type == "image_optimize":
            from services.image_optimizer import get_image_optimizer
            optimizer = get_image_optimizer()
            return optimizer.optimize_image(**task_data)
        elif task_type == "batch_image_optimize":
            from services.image_optimizer import get_image_optimizer
            optimizer = get_image_optimizer()
            image_paths = task_data.get("image_paths", [])
            options = task_data.get("options", {})
            return optimizer.optimize_batch(image_paths, options)
        else:
            raise ValueError(f"Unknown task type: {task_type}")


# Global task queue instance
_task_queue: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    """Get global task queue instance"""
    global _task_queue
    if _task_queue is None:
        max_workers = int(os.getenv("TASK_QUEUE_WORKERS", "2"))
        _task_queue = TaskQueue(max_workers=max_workers)
        _task_queue.start()
    return _task_queue


def init_task_queue():
    """Initialize task queue (call on app startup)"""
    get_task_queue()
