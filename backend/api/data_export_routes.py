"""
Data Export Routes - GDPR compliant data export
Data Export Routes - GDPR-compliant data export
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from typing import Optional
from sqlalchemy.orm import Session
import json

from dependencies import require_auth, get_data_export_service_dependency
from services.data_export_service import DataExportService
from middleware.api_decorators import handle_api_errors
from exceptions import AuthenticationError

router = APIRouter(prefix="/api/data-export", tags=["data-export"])


@router.get("")
@handle_api_errors
async def export_user_data(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    current_user: dict = Depends(require_auth),
    export_service: DataExportService = Depends(get_data_export_service_dependency)
):
    """
    Export user data (GDPR compliant)
    
    Export all data for the current user, including:
    - Authentication info
    - User settings
    - Translation history
    - Customer/elder records
    - Device info
    - API keys (metadata)
    - Personalization data
    - Interaction history
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise AuthenticationError("User not authenticated")
    
    export_data = export_service.export_user_data(user_id, format=format)
    
    if format == "csv":
        # Return CSV files as downloadable
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f'attachment; filename="user_data_{user_id}_{export_data["exported_at"][:10]}.json"'
            }
        )
    else:
        # Return JSON
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f'attachment; filename="user_data_{user_id}_{export_data["exported_at"][:10]}.json"'
            }
        )


@router.get("/download")
@handle_api_errors
async def download_user_data(
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    current_user: dict = Depends(require_auth),
    export_service: DataExportService = Depends(get_data_export_service_dependency)
):
    """
    Download user data (direct file download)
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise AuthenticationError("User not authenticated")
    
    export_data = export_service.export_user_data(user_id, format=format)
    
    if format == "json":
        content = json.dumps(export_data, indent=2, ensure_ascii=False)
        media_type = "application/json"
        filename = f"user_data_{user_id}_{export_data['exported_at'][:10]}.json"
    else:
        # CSV format - combine all sections
        content = ""
        for section, csv_data in export_data.get("csv_data", {}).items():
            content += f"\n=== {section.upper()} ===\n"
            content += csv_data
            content += "\n"
        media_type = "text/csv"
        filename = f"user_data_{user_id}_{export_data['exported_at'][:10]}.csv"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
