"""
Image Optimization API Routes
Image Optimization API Routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import uuid
from datetime import datetime

from services.image_optimizer import get_image_optimizer
from services.storage_service import get_storage_service
from services.task_queue import get_task_queue
from services.logging_service import logger

router = APIRouter(prefix="/api/images", tags=["image-optimization"])


class OptimizationOptions(BaseModel):
    """Optimization options"""
    quality: int = 85
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    format: Optional[str] = None  # 'webp', 'jpeg', 'png'
    progressive: bool = True


class BatchOptimizationRequest(BaseModel):
    """Batch optimization request"""
    image_paths: List[str]
    options: Optional[OptimizationOptions] = None


# Store optimization tasks
optimization_tasks: Dict[str, Dict[str, Any]] = {}


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Form("images"),
    optimize: bool = Form(True),
    quality: int = Form(85)
):
    """Upload image to storage service"""
    try:
        # Validate file upload
        from utils.security import validate_file_upload
        max_size = 10 * 1024 * 1024  # 10MB
        allowed_extensions = ["jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"]
        
        is_valid, error_msg = validate_file_upload(
            filename=file.filename or "",
            content_type=file.content_type,
            max_size=max_size,
            allowed_extensions=allowed_extensions
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {max_size / (1024*1024):.1f}MB"
            )
        
        # Reset file pointer for storage service
        await file.seek(0)
        
        storage = get_storage_service()
        
        # Upload file
        upload_result = storage.upload_file(
            file.file,
            filename=file.filename,
            folder=folder,
            public=True
        )
        
        # Optimize if requested
        if optimize and upload_result.get("success"):
            optimizer = get_image_optimizer()
            optimize_result = optimizer.optimize_image(
                upload_result["path"],
                quality=quality,
                format="webp"
            )
            
            if optimize_result.get("success"):
                # Replace original with optimized version
                if os.path.exists(optimize_result["optimized_path"]):
                    # Update upload result with optimized info
                    upload_result["optimized"] = {
                        "path": optimize_result["optimized_path"],
                        "url": storage.get_file_url(optimize_result["optimized_path"]),
                        "size": optimize_result["optimized_size"],
                        "compression_ratio": optimize_result["compression_ratio"]
                    }
        
        return {
            "message": "Image uploaded successfully",
            "file": upload_result
        }
    
    except Exception as e:
        logger.log_error(e, {"action": "upload_image"})
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@router.post("/optimize")
async def optimize_image(
    file: UploadFile = File(...),
    quality: int = Form(85),
    max_width: Optional[int] = Form(None),
    max_height: Optional[int] = Form(None),
    format: Optional[str] = Form(None),
    progressive: bool = Form(True)
):
    """Optimize a single image"""
    try:
        # Validate file upload
        from utils.security import validate_file_upload
        max_size = 10 * 1024 * 1024  # 10MB
        allowed_extensions = ["jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"]
        
        is_valid, error_msg = validate_file_upload(
            filename=file.filename or "",
            content_type=file.content_type,
            max_size=max_size,
            allowed_extensions=allowed_extensions
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        optimizer = get_image_optimizer()
        
        # Save uploaded file temporarily
        temp_dir = "/tmp/image_optimization"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Validate filename to prevent path traversal
        safe_filename = os.path.basename(file.filename or "image") if file.filename else "image"
        if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{safe_filename}")
        
        # Check file size
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {max_size / (1024*1024):.1f}MB"
            )
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Optimize image
        result = optimizer.optimize_image(
            temp_path,
            quality=quality,
            max_width=max_width,
            max_height=max_height,
            format=format,
            progressive=progressive
        )
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Optimization failed"))
        
        return result
    
    except Exception as e:
        logger.log_error(e, {"action": "optimize_image"})
        raise HTTPException(status_code=500, detail=f"Failed to optimize image: {str(e)}")


@router.post("/optimize/batch")
async def optimize_batch_images(
    request: BatchOptimizationRequest,
    use_queue: bool = Form(True)
):
    """Batch optimize images (supports task queue)"""
    try:
        if use_queue:
            # Use task queue for background processing
            task_queue = get_task_queue()
            
            options = request.options.dict() if request.options else {}
            task_data = {
                "image_paths": request.image_paths,
                "options": options
            }
            
            task_id = task_queue.add_task(
                task_type="batch_image_optimize",
                task_data=task_data
            )
            
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Batch optimization queued",
                "total_images": len(request.image_paths),
                "check_status_url": f"/api/images/optimize/task/{task_id}"
            }
        else:
            # Synchronous processing (for small batches)
            optimizer = get_image_optimizer()
            options = request.options.dict() if request.options else {}
            result = optimizer.optimize_batch(request.image_paths, options)
            
            return {
                "status": "completed",
                "message": "Batch optimization completed",
                "result": result
            }
    
    except Exception as e:
        logger.log_error(e, {"action": "optimize_batch_images"})
        raise HTTPException(status_code=500, detail=f"Failed to start batch optimization: {str(e)}")


@router.post("/compress/batch")
async def compress_batch_images(
    image_paths: List[str] = Form(...),
    quality: int = Form(85),
    use_queue: bool = Form(True)
):
    """Batch compress images"""
    try:
        optimizer = get_image_optimizer()
        
        if use_queue:
            task_queue = get_task_queue()
            task_data = {
                "image_paths": image_paths,
                "options": {"quality": quality}
            }
            
            task_id = task_queue.add_task(
                task_type="batch_image_optimize",
                task_data=task_data
            )
            
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Batch compression queued",
                "total_images": len(image_paths),
                "check_status_url": f"/api/images/optimize/task/{task_id}"
            }
        else:
            result = optimizer.compress_batch(image_paths, quality=quality)
            return {
                "status": "completed",
                "message": "Batch compression completed",
                "result": result
            }
    
    except Exception as e:
        logger.log_error(e, {"action": "compress_batch_images"})
        raise HTTPException(status_code=500, detail=f"Failed to compress images: {str(e)}")


@router.post("/convert/batch/webp")
async def convert_batch_to_webp(
    image_paths: List[str] = Form(...),
    quality: int = Form(85),
    use_queue: bool = Form(True)
):
    """Batch convert to WebP format"""
    try:
        optimizer = get_image_optimizer()
        
        if use_queue:
            task_queue = get_task_queue()
            task_data = {
                "image_paths": image_paths,
                "options": {"format": "webp", "quality": quality}
            }
            
            task_id = task_queue.add_task(
                task_type="batch_image_optimize",
                task_data=task_data
            )
            
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Batch WebP conversion queued",
                "total_images": len(image_paths),
                "check_status_url": f"/api/images/optimize/task/{task_id}"
            }
        else:
            result = optimizer.convert_batch_to_webp(image_paths, quality=quality)
            return {
                "status": "completed",
                "message": "Batch WebP conversion completed",
                "result": result
            }
    
    except Exception as e:
        logger.log_error(e, {"action": "convert_batch_to_webp"})
        raise HTTPException(status_code=500, detail=f"Failed to convert to WebP: {str(e)}")


@router.post("/resize/batch")
async def resize_batch_images(
    image_paths: List[str] = Form(...),
    max_width: int = Form(...),
    max_height: int = Form(...),
    maintain_aspect: bool = Form(True),
    use_queue: bool = Form(True)
):
    """Batch resize images"""
    try:
        optimizer = get_image_optimizer()
        
        if use_queue:
            task_queue = get_task_queue()
            task_data = {
                "image_paths": image_paths,
                "options": {
                    "max_width": max_width if maintain_aspect else None,
                    "max_height": max_height if maintain_aspect else None
                }
            }
            
            task_id = task_queue.add_task(
                task_type="batch_image_optimize",
                task_data=task_data
            )
            
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Batch resize queued",
                "total_images": len(image_paths),
                "check_status_url": f"/api/images/optimize/task/{task_id}"
            }
        else:
            result = optimizer.resize_batch(
                image_paths,
                max_width=max_width,
                max_height=max_height,
                maintain_aspect=maintain_aspect
            )
            return {
                "status": "completed",
                "message": "Batch resize completed",
                "result": result
            }
    
    except Exception as e:
        logger.log_error(e, {"action": "resize_batch_images"})
        raise HTTPException(status_code=500, detail=f"Failed to resize images: {str(e)}")


@router.get("/optimize/task/{task_id}")
async def get_optimization_task_status(task_id: str):
    """Get optimization task status"""
    try:
        task_queue = get_task_queue()
        task = task_queue.get_task(task_id)
        
        if not task:
            # Check legacy tasks
            if task_id in optimization_tasks:
                return optimization_tasks[task_id]
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task
    
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "get_optimization_task_status"})
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@router.post("/convert/webp")
async def convert_to_webp(
    file: UploadFile = File(...),
    quality: int = Form(85)
):
    """Convert image to WebP format"""
    try:
        # Validate file upload
        from utils.security import validate_file_upload
        max_size = 10 * 1024 * 1024  # 10MB
        allowed_extensions = ["jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"]
        
        is_valid, error_msg = validate_file_upload(
            filename=file.filename or "",
            content_type=file.content_type,
            max_size=max_size,
            allowed_extensions=allowed_extensions
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        optimizer = get_image_optimizer()
        
        # Save uploaded file temporarily
        temp_dir = "/tmp/image_optimization"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Validate filename to prevent path traversal
        safe_filename = os.path.basename(file.filename or "image") if file.filename else "image"
        if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{safe_filename}")
        
        # Check file size
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {max_size / (1024*1024):.1f}MB"
            )
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Convert to WebP
        result = optimizer.convert_to_webp(temp_path, quality=quality)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Conversion failed"))
        
        return result
    
    except Exception as e:
        logger.log_error(e, {"action": "convert_to_webp"})
        raise HTTPException(status_code=500, detail=f"Failed to convert to WebP: {str(e)}")


@router.get("/info")
async def get_image_info(path: str):
    """Get image information"""
    try:
        optimizer = get_image_optimizer()
        info = optimizer.get_image_info(path)
        
        if "error" in info:
            raise HTTPException(status_code=400, detail=info["error"])
        
        return info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "get_image_info"})
        raise HTTPException(status_code=500, detail=f"Failed to get image info: {str(e)}")
