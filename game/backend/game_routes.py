"""
Game API Routes - Game session management and tracking
游戏API路由 - 游戏会话管理和追踪
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Literal
from sqlalchemy.orm import Session
from datetime import datetime
import json
import re
from utils.time_utils import utc_now

# Import from backend (adjust path as needed)
# 从后端导入（根据实际路径调整）
import sys
from pathlib import Path

# Add backend to path if needed
backend_path = Path(__file__).parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from services.logging_service import logger
    from config.database import get_db
    from api.auth_routes import get_current_user
    from middleware.rate_limit import rate_limit
    from exceptions import ValidationError, AuthenticationError, AuthorizationError
    from utils.security import sanitize_input
except ImportError as e:
    # Fallback for development/testing
    import logging
    logger = logging.getLogger(__name__)
    def get_current_user():
        return None
    def rate_limit(limit):
        def decorator(func):
            return func
        return decorator
    class ValidationError(Exception):
        pass
    class AuthenticationError(Exception):
        pass
    class AuthorizationError(Exception):
        pass
    def sanitize_input(text, max_length=None):
        return text or ""
    def get_db():
        return None
    logger.warning(f"Some imports failed: {e}. Using fallback implementations.")

router = APIRouter(prefix="/api/games", tags=["games"])
security = HTTPBearer()

# Game API rate limits
GAME_RATE_LIMITS = {
    "start": "10/minute",
    "update": "60/minute",
    "complete": "20/minute",
    "history": "30/minute",
    "stats": "20/minute",
}


class GameStartRequest(BaseModel):
    """开始游戏请求"""
    game_type: Literal['memory_match', 'story_chain', 'number_puzzle', 'music_rhythm', 'picture_sort']
    player1_id: str = Field(..., min_length=1, max_length=100)
    player2_id: str = Field(..., min_length=1, max_length=100)
    difficulty: Literal['easy', 'medium', 'hard']
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('player1_id', 'player2_id')
    def validate_user_id(cls, v):
        """验证用户ID格式"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid user ID format')
        if len(v) > 100:
            raise ValueError('User ID too long')
        return v
    
    @validator('settings')
    def validate_settings(cls, v):
        """验证设置参数"""
        if not isinstance(v, dict):
            raise ValueError('Settings must be a dictionary')
        
        # 限制设置大小（防止DoS）
        settings_str = json.dumps(v)
        if len(settings_str) > 10000:
            raise ValueError('Settings too large (max 10KB)')
        
        return v


class GameUpdateRequest(BaseModel):
    """更新游戏状态请求"""
    session_id: str = Field(..., min_length=1, max_length=100)
    game_state: Dict[str, Any]
    action: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    @validator('session_id')
    def validate_session_id(cls, v):
        """验证会话ID格式"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid session ID format')
        return v
    
    @validator('game_state')
    def validate_game_state(cls, v):
        """验证游戏状态大小"""
        state_str = json.dumps(v)
        if len(state_str) > 100000:  # 100KB limit
            raise ValueError('Game state too large (max 100KB)')
        return v


class GameCompleteRequest(BaseModel):
    """完成游戏请求"""
    session_id: str = Field(..., min_length=1, max_length=100)
    final_state: Dict[str, Any]
    
    @validator('session_id')
    def validate_session_id(cls, v):
        """验证会话ID格式"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid session ID format')
        return v
    
    @validator('final_state')
    def validate_final_state(cls, v):
        """验证最终状态"""
        if not isinstance(v, dict):
            raise ValueError('Final state must be a dictionary')
        
        # 验证分数范围
        score = v.get('score')
        if score is not None:
            if not isinstance(score, (int, float)):
                raise ValueError('Score must be a number')
            if score < 0 or score > 100:
                raise ValueError('Score must be between 0 and 100')
        
        return v


def verify_game_session_access(
    session_id: str,
    user_id: str,
    db: Session
) -> bool:
    """
    验证用户是否有权限访问游戏会话
    
    Args:
        session_id: 游戏会话ID
        user_id: 用户ID
        db: 数据库会话
        
    Returns:
        True if user has access, False otherwise
    """
    # TODO: 实现数据库查询验证
    # 这里需要创建GameSessionDB模型
    # session = db.query(GameSessionDB).filter(
    #     GameSessionDB.session_id == session_id
    # ).first()
    # 
    # if not session:
    #     return False
    # 
    # if session.player1_id != user_id and session.player2_id != user_id:
    #     return False
    
    return True  # 临时返回True，等待数据库模型实现


def validate_game_state_server(game_state: Dict[str, Any], game_type: str) -> tuple[bool, Optional[str]]:
    """
    服务器端验证游戏状态
    
    Args:
        game_state: 游戏状态字典
        game_type: 游戏类型
        
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(game_state, dict):
        return False, "Game state must be a dictionary"
    
    # 验证游戏类型
    valid_types = ['memory_match', 'story_chain', 'number_puzzle', 'music_rhythm', 'picture_sort']
    if game_type not in valid_types:
        return False, f"Invalid game type: {game_type}"
    
    # 验证状态大小
    state_str = json.dumps(game_state)
    if len(state_str) > 100000:  # 100KB
        return False, "Game state too large"
    
    # 游戏特定验证
    if game_type == 'memory_match':
        return validate_memory_match_state(game_state)
    elif game_type == 'story_chain':
        return validate_story_chain_state(game_state)
    # ... 其他游戏验证
    
    return True, None


def validate_memory_match_state(game_state: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """验证记忆配对游戏状态"""
    cards = game_state.get('cards', [])
    
    # 验证卡片数量
    if len(cards) > 24:  # 最大12对
        return False, "Too many cards (max 24)"
    
    # 验证卡片格式
    for card in cards:
        if not isinstance(card, dict):
            return False, "Invalid card format"
        if 'id' not in card or 'value' not in card:
            return False, "Card missing required fields"
    
    # 验证进度
    progress = game_state.get('progress', 0)
    if not isinstance(progress, (int, float)):
        return False, "Progress must be a number"
    if progress < 0 or progress > 100:
        return False, "Progress must be between 0 and 100"
    
    return True, None


def validate_story_chain_state(game_state: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """验证故事接龙游戏状态"""
    sentences = game_state.get('sentences', [])
    
    # 验证句子数量
    if len(sentences) > 100:
        return False, "Too many sentences (max 100)"
    
    # 验证每个句子
    for sentence in sentences:
        if not isinstance(sentence, str):
            return False, "Sentence must be a string"
        if len(sentence) > 500:
            return False, "Sentence too long (max 500 characters)"
        
        # 清理句子内容
        sanitized = sanitize_input(sentence, 500)
        if len(sanitized) != len(sentence):
            return False, "Sentence contains invalid characters"
    
    return True, None


def detect_cheating_patterns(
    session_id: str,
    game_state: Dict[str, Any],
    final_state: Optional[Dict[str, Any]] = None
) -> List[str]:
    """
    检测可能的作弊模式
    
    Args:
        session_id: 游戏会话ID
        game_state: 游戏状态
        final_state: 最终状态（如果完成）
        
    Returns:
        警告列表
    """
    warnings = []
    
    # 检测异常高分
    if final_state:
        score = final_state.get('score')
        if score is not None and score > 100:
            warnings.append("Score exceeds maximum possible (100)")
    
    # 检测状态不一致
    progress = game_state.get('progress', 0)
    if progress < 0 or progress > 100:
        warnings.append("Progress value out of range")
    
    # 检测异常大的状态
    state_str = json.dumps(game_state)
    if len(state_str) > 50000:  # 50KB
        warnings.append("Game state unusually large")
    
    return warnings


@router.post("/start")
@rate_limit(limit=GAME_RATE_LIMITS["start"])
async def start_game(
    request: GameStartRequest,
    http_request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    开始游戏会话
    
    需要认证，验证用户权限
    """
    if not current_user:
        raise AuthenticationError("Authentication required")
    
    # 验证用户ID
    if request.player1_id != current_user.get("user_id"):
        raise AuthorizationError("Cannot start game for other user")
    
    # 验证用户ID格式
    if not re.match(r'^[a-zA-Z0-9_-]+$', request.player2_id):
        raise ValidationError("Invalid player2_id format")
    
    try:
        # 生成会话ID
        from utils.security import generate_secure_token
        session_id = f"game_{generate_secure_token(16)}"
        
        # 初始化游戏状态
        initial_state = initialize_game_state(request.game_type, request.difficulty, request.settings)
        
        # 验证初始状态
        is_valid, error_msg = validate_game_state_server(initial_state, request.game_type)
        if not is_valid:
            raise ValidationError(f"Invalid game state: {error_msg}")
        
        # TODO: 保存到数据库
        # game_session = GameSessionDB(
        #     session_id=session_id,
        #     game_type=request.game_type,
        #     player1_id=request.player1_id,
        #     player2_id=request.player2_id,
        #     difficulty=request.difficulty,
        #     game_state=initial_state,
        #     start_time=datetime.utcnow()
        # )
        # db.add(game_session)
        # db.commit()
        
        logger.log_api_request(
            endpoint="/api/games/start",
            method="POST",
            user_id=request.player1_id,
            org_id=None,
            status_code=200,
            response_time_ms=0
        )
        
        return {
            "session_id": session_id,
            "game_state": initial_state,
            "created_at": utc_now().isoformat()
        }
    except (ValidationError, AuthenticationError, AuthorizationError):
        raise
    except Exception as e:
        logger.log_error(e, {"action": "start_game", "user_id": request.player1_id})
        raise HTTPException(status_code=500, detail=f"Failed to start game: {str(e)}")


@router.post("/update")
@rate_limit(limit=GAME_RATE_LIMITS["update"])
async def update_game(
    request: GameUpdateRequest,
    http_request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新游戏状态
    
    需要认证，验证会话访问权限
    """
    if not current_user:
        raise AuthenticationError("Authentication required")
    
    user_id = current_user.get("user_id")
    
    # 验证会话访问权限
    if not verify_game_session_access(request.session_id, user_id, db):
        raise AuthorizationError("Access denied to this game session")
    
    # 验证游戏状态
    # 需要从数据库获取游戏类型
    # game_session = db.query(GameSessionDB).filter(...).first()
    # game_type = game_session.game_type
    
    # 临时使用请求中的信息（实际应从数据库获取）
    game_type = "memory_match"  # TODO: 从数据库获取
    
    is_valid, error_msg = validate_game_state_server(request.game_state, game_type)
    if not is_valid:
        raise ValidationError(f"Invalid game state: {error_msg}")
    
    # 验证时间戳
    if request.timestamp:
        try:
            action_time = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
            time_diff = (utc_now() - action_time.replace(tzinfo=None)).total_seconds()
            
            if abs(time_diff) > 300:  # 5分钟
                raise ValidationError("Action timestamp too old or in future")
        except Exception:
            raise ValidationError("Invalid timestamp format")
    
    # 检测作弊模式
    warnings = detect_cheating_patterns(request.session_id, request.game_state)
    if warnings:
        logger.log_warning(
            f"Cheating patterns detected in game session {request.session_id}",
            {"warnings": warnings, "user_id": user_id}
        )
    
    try:
        # TODO: 更新数据库
        # game_session.game_state = request.game_state
        # game_session.completion = request.game_state.get('progress', 0)
        # db.commit()
        
        return {
            "success": True,
            "session_id": request.session_id,
            "warnings": warnings if warnings else None
        }
    except Exception as e:
        logger.log_error(e, {"action": "update_game", "session_id": request.session_id})
        raise HTTPException(status_code=500, detail=f"Failed to update game: {str(e)}")


@router.post("/complete")
@rate_limit(limit=GAME_RATE_LIMITS["complete"])
async def complete_game(
    request: GameCompleteRequest,
    http_request: Request,
    current_user: Optional[dict] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    完成游戏会话
    
    需要认证，验证会话访问权限，验证最终状态
    """
    if not current_user:
        raise AuthenticationError("Authentication required")
    
    user_id = current_user.get("user_id")
    
    # 验证会话访问权限
    if not verify_game_session_access(request.session_id, user_id, db):
        raise AuthorizationError("Access denied to this game session")
    
    # 检测作弊模式
    warnings = detect_cheating_patterns(
        request.session_id,
        {},
        request.final_state
    )
    
    if warnings:
        logger.log_warning(
            f"Cheating patterns detected when completing game {request.session_id}",
            {"warnings": warnings, "user_id": user_id}
        )
    
    try:
        # TODO: 更新数据库
        # game_session.end_time = datetime.utcnow()
        # game_session.score = request.final_state.get('score')
        # game_session.completion = 100
        # db.commit()
        
        return {
            "success": True,
            "session_id": request.session_id,
            "warnings": warnings if warnings else None,
            "achievements": []  # TODO: 计算成就
        }
    except Exception as e:
        logger.log_error(e, {"action": "complete_game", "session_id": request.session_id})
        raise HTTPException(status_code=500, detail=f"Failed to complete game: {str(e)}")


@router.get("/history")
@rate_limit(limit=GAME_RATE_LIMITS["history"])
async def get_game_history(
    user_id: str,
    game_type: Optional[str] = None,
    limit: int = 10,
    current_user: Optional[dict] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取游戏历史
    
    需要认证，只能查看自己的历史
    """
    if not current_user:
        raise AuthenticationError("Authentication required")
    
    # 验证只能查看自己的历史
    if user_id != current_user.get("user_id"):
        raise AuthorizationError("Cannot access other user's game history")
    
    # 验证limit参数
    if limit < 1 or limit > 100:
        raise ValidationError("Limit must be between 1 and 100")
    
    # 验证game_type
    if game_type:
        valid_types = ['memory_match', 'story_chain', 'number_puzzle', 'music_rhythm', 'picture_sort']
        if game_type not in valid_types:
            raise ValidationError(f"Invalid game type: {game_type}")
    
    try:
        # TODO: 从数据库查询
        # sessions = db.query(GameSessionDB).filter(
        #     GameSessionDB.player1_id == user_id
        # ).limit(limit).all()
        
        return {
            "sessions": [],
            "total": 0
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_game_history", "user_id": user_id})
        raise HTTPException(status_code=500, detail=f"Failed to get game history: {str(e)}")


@router.get("/stats")
@rate_limit(limit=GAME_RATE_LIMITS["stats"])
async def get_game_stats(
    user_id: str,
    current_user: Optional[dict] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取游戏统计
    
    需要认证，只能查看自己的统计
    """
    if not current_user:
        raise AuthenticationError("Authentication required")
    
    # 验证只能查看自己的统计
    if user_id != current_user.get("user_id"):
        raise AuthorizationError("Cannot access other user's game stats")
    
    try:
        # TODO: 从数据库计算统计
        return {
            "user_id": user_id,
            "total_sessions": 0,
            "games": {}
        }
    except Exception as e:
        logger.log_error(e, {"action": "get_game_stats", "user_id": user_id})
        raise HTTPException(status_code=500, detail=f"Failed to get game stats: {str(e)}")


def initialize_game_state(game_type: str, difficulty: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    初始化游戏状态
    
    Args:
        game_type: 游戏类型
        difficulty: 难度等级
        settings: 自定义设置
        
    Returns:
        初始游戏状态
    """
    base_state = {
        "progress": 0,
        "start_time": utc_now().isoformat()
    }
    
    if game_type == 'memory_match':
        # 根据难度设置卡片对数
        card_pairs = {
            'easy': 4,
            'medium': 8,
            'hard': 12
        }.get(difficulty, 8)
        
        # 生成卡片
        cards = []
        for i in range(card_pairs):
            cards.append({"id": f"card_{i}_1", "value": i, "flipped": False})
            cards.append({"id": f"card_{i}_2", "value": i, "flipped": False})
        
        # 打乱卡片顺序
        import random
        random.shuffle(cards)
        
        base_state.update({
            "cards": cards,
            "flippedCards": [],
            "matches": 0,
            "turns": 0
        })
    
    elif game_type == 'story_chain':
        base_state.update({
            "sentences": [],
            "current_turn": "player1",
            "theme": settings.get("theme", "general")
        })
    
    # ... 其他游戏类型的初始化
    
    return base_state
