"""
Voice API Routes - Speech-to-text and text-to-speech
Voice API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from services.voice_service import get_voice_service
from services.logging_service import logger
from config.database import get_db

router = APIRouter(prefix="/api/voice", tags=["voice"])


class TextToSpeechRequest(BaseModel):
    """Text-to-speech request"""
    text: str
    language: str = "ja"  # ja, zh, en
    voice: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = Form("ja"),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Speech-to-text"""
    try:
        # Validate file upload
        from utils.security import validate_file_upload
        max_size = 10 * 1024 * 1024  # 10MB
        allowed_extensions = ["wav", "mp3", "m4a", "ogg", "flac", "webm"]
        
        is_valid, error_msg = validate_file_upload(
            filename=audio_file.filename or "",
            content_type=audio_file.content_type,
            max_size=max_size,
            allowed_extensions=allowed_extensions
        )
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        voice_service = get_voice_service()
        
        # Read audio file
        audio_data = await audio_file.read()
        
        # Check file size
        if len(audio_data) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {max_size / (1024*1024):.1f}MB"
            )
        
        # Convert to text
        result = voice_service.speech_to_text(
            audio_data=audio_data,
            language=language,
            user_id=user_id
        )
        
        # NSFW detection - check transcribed text
        from services.nsfw_detector import get_nsfw_detector
        nsfw_detector = get_nsfw_detector()
        transcribed_text = result.get("text", "")
        
        if transcribed_text:
            nsfw_result = await nsfw_detector.check(
                transcribed_text, language=language
            )
            
            if nsfw_detector.should_block(nsfw_result):
                logger.log_warning(
                    f"NSFW content blocked in speech-to-text",
                    {
                        "text_preview": transcribed_text[:50],
                        "level": nsfw_result.get("level"),
                        "reason": nsfw_result.get("reason")
                    }
                )
                raise HTTPException(
                    status_code=400,
                    detail=nsfw_detector.get_block_message(language)
                )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "speech_to_text"})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe: {str(e)}"
        )


@router.post("/text-to-speech")
async def text_to_speech(
    request: TextToSpeechRequest,
    db: Session = Depends(get_db)
):
    """Text-to-speech"""
    # NSFW detection - check input text
    from services.nsfw_detector import get_nsfw_detector
    nsfw_detector = get_nsfw_detector()
    nsfw_result = await nsfw_detector.check(
        request.text, language=request.language
    )
    
    if nsfw_detector.should_block(nsfw_result):
        logger.log_warning(
            f"NSFW content blocked in text-to-speech",
            {
                "text_preview": request.text[:50],
                "level": nsfw_result.get("level"),
                "reason": nsfw_result.get("reason")
            }
        )
        raise HTTPException(
            status_code=400,
            detail=nsfw_detector.get_block_message(request.language)
        )
    
    try:
        voice_service = get_voice_service()
        
        result = voice_service.text_to_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            user_id=request.user_id
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error(e, {"action": "text_to_speech"})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to synthesize speech: {str(e)}"
        )


@router.post("/save-voice-note")
async def save_voice_note(
    audio_file: UploadFile = File(...),
    user_id: str = Form(...),
    activity_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Save voice note"""
    try:
        voice_service = get_voice_service()
        
        audio_data = await audio_file.read()
        
        result = voice_service.save_voice_note(
            audio_data=audio_data,
            user_id=user_id,
            activity_id=activity_id
        )
        
        return {
            "message": "Voice note saved successfully",
            "note": result
        }
    except Exception as e:
        logger.log_error(e, {"action": "save_voice_note"})
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save voice note: {str(e)}"
        )
