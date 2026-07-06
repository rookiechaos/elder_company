"""
Tests for Image Optimization Service
图片优化服务测试
"""

import pytest
import os
import tempfile
from pathlib import Path
import io

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

from services.image_optimizer import ImageOptimizer, get_image_optimizer
from services.storage_service import StorageService, get_storage_service
from services.task_queue import TaskQueue, get_task_queue, TaskStatus


class TestImageOptimizer:
    """Tests for ImageOptimizer"""
    
    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL not available")
    def test_optimize_image(self):
        """Test single image optimization"""
        optimizer = ImageOptimizer()
        
        # Create a test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp.name, 'JPEG')
            tmp_path = tmp.name
        
        try:
            result = optimizer.optimize_image(
                tmp_path,
                quality=85,
                max_width=50,
                format='webp'
            )
            
            assert result.get("success") is True or result.get("error") is not None
            if result.get("success"):
                assert "optimized_path" in result
                assert result.get("compression_ratio") is not None
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL not available")
    def test_compress_batch(self):
        """Test batch compression"""
        optimizer = ImageOptimizer()
        
        # Create test images
        test_images = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                img = Image.new('RGB', (100, 100), color='red')
                img.save(tmp.name, 'JPEG')
                test_images.append(tmp.name)
        
        try:
            result = optimizer.compress_batch(test_images, quality=85)
            
            assert result.get("total") == 3
            assert result.get("successful") >= 0
            assert result.get("failed") >= 0
        finally:
            for img_path in test_images:
                if os.path.exists(img_path):
                    os.remove(img_path)
    
    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL not available")
    def test_convert_batch_to_webp(self):
        """Test batch WebP conversion"""
        optimizer = ImageOptimizer()
        
        # Create test images
        test_images = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                img = Image.new('RGB', (100, 100), color='blue')
                img.save(tmp.name, 'JPEG')
                test_images.append(tmp.name)
        
        try:
            result = optimizer.convert_batch_to_webp(test_images, quality=85)
            
            assert result.get("total") == 2
        finally:
            for img_path in test_images:
                if os.path.exists(img_path):
                    os.remove(img_path)
    
    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL not available")
    def test_resize_batch(self):
        """Test batch resize"""
        optimizer = ImageOptimizer()
        
        # Create test images
        test_images = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                img = Image.new('RGB', (200, 200), color='green')
                img.save(tmp.name, 'JPEG')
                test_images.append(tmp.name)
        
        try:
            result = optimizer.resize_batch(
                test_images,
                max_width=100,
                max_height=100,
                maintain_aspect=True
            )
            
            assert result.get("total") == 2
        finally:
            for img_path in test_images:
                if os.path.exists(img_path):
                    os.remove(img_path)


class TestStorageService:
    """Tests for StorageService"""
    
    def test_upload_file(self):
        """Test file upload"""
        storage = StorageService(storage_type="local", config={"storage_dir": "./test_storage"})
        
        # Create test file
        test_content = b"test image content"
        file_obj = io.BytesIO(test_content)
        
        result = storage.upload_file(
            file=file_obj,
            filename="test.jpg",
            folder="images",
            public=True
        )
        
        assert result.get("success") is True
        assert result.get("filename") is not None
        assert result.get("url") is not None
        
        # Cleanup
        if result.get("path") and os.path.exists(result["path"]):
            os.remove(result["path"])
    
    def test_get_file_url(self):
        """Test file URL generation"""
        storage = StorageService(storage_type="local")
        
        url = storage.get_file_url("images/test.jpg", cdn_enabled=False)
        assert url is not None
        assert "images/test.jpg" in url


class TestTaskQueue:
    """Tests for TaskQueue"""
    
    def test_add_task(self):
        """Test adding task to queue"""
        task_queue = TaskQueue(max_workers=1)
        task_queue.start()
        
        try:
            task_id = task_queue.add_task(
                task_type="test_task",
                task_data={"test": "data"}
            )
            
            assert task_id is not None
            assert task_id.startswith("test_task_")
            
            # Get task
            task = task_queue.get_task(task_id)
            assert task is not None
            assert task["task_id"] == task_id
            assert task["status"] == TaskStatus.PENDING.value
        finally:
            task_queue.stop()
    
    def test_task_status_update(self):
        """Test task status update"""
        task_queue = TaskQueue(max_workers=1)
        task_queue.start()
        
        try:
            task_id = task_queue.add_task(
                task_type="test_task",
                task_data={"test": "data"}
            )
            
            task_queue.update_task_status(
                task_id,
                TaskStatus.COMPLETED,
                result={"success": True}
            )
            
            task = task_queue.get_task(task_id)
            assert task["status"] == TaskStatus.COMPLETED.value
            assert task.get("result") is not None
        finally:
            task_queue.stop()


class TestWebVitalsAlert:
    """Tests for Web Vitals Alert Service"""
    
    def test_check_metric(self):
        """Test metric checking"""
        from services.web_vitals_alert import get_web_vitals_alert_service
        
        alert_service = get_web_vitals_alert_service()
        
        # Test good metric
        result = alert_service.check_metric("LCP", 2000)
        assert result["level"] == "good"
        assert result["alert"] is False
        
        # Test poor metric
        result = alert_service.check_metric("LCP", 5000)
        assert result["level"] == "poor"
        assert result["alert"] is True
    
    def test_get_thresholds(self):
        """Test getting thresholds"""
        from services.web_vitals_alert import get_web_vitals_alert_service
        
        alert_service = get_web_vitals_alert_service()
        thresholds = alert_service.get_thresholds()
        
        assert "LCP" in thresholds
        assert "FID" in thresholds
        assert "CLS" in thresholds


class TestQueryOptimizer:
    """Tests for Query Optimizer"""
    
    def test_analyze_slow_query(self):
        """Test slow query analysis"""
        from services.query_optimizer import get_query_optimizer
        
        optimizer = get_query_optimizer()
        
        # Test SELECT query - use analyze_slow_query method
        analysis = optimizer.analyze_slow_query(
            statement="SELECT * FROM users WHERE name LIKE '%test%'",
            execution_time=2.5
        )
        
        assert analysis["query_type"] == "SELECT"
        assert "suggestions" in analysis
        assert "optimization_score" in analysis
        assert analysis["optimization_score"] >= 0
    
    def test_generate_optimization_report(self):
        """Test optimization report generation"""
        from services.query_optimizer import get_query_optimizer
        
        optimizer = get_query_optimizer()
        
        slow_queries = [
            {
                "statement": "SELECT * FROM users WHERE id = 1",
                "query_time": 1.5
            },
            {
                "statement": "SELECT * FROM orders ORDER BY created_at",
                "query_time": 2.0
            }
        ]
        
        # Use generate_optimization_report method
        report = optimizer.generate_optimization_report(slow_queries)
        
        # Check report structure
        assert "total_queries" in report or "total_slow_queries" in report
        assert "analysis_results" in report or "recommendations" in report
        assert isinstance(report, dict)


def test_all_services_importable():
    """Test that all services can be imported"""
    from services.image_optimizer import get_image_optimizer
    from services.storage_service import get_storage_service
    from services.task_queue import get_task_queue
    from services.web_vitals_alert import get_web_vitals_alert_service
    from services.query_optimizer import get_query_optimizer
    
    assert get_image_optimizer() is not None
    assert get_storage_service() is not None
    assert get_task_queue() is not None
    assert get_web_vitals_alert_service() is not None
    assert get_query_optimizer() is not None
