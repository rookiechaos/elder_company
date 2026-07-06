/**
 * Security Utilities - Frontend security functions
 * 安全工具 - 前端安全函数
 */

/**
 * Sanitize user input to prevent XSS attacks
 * 清理用户输入，防止XSS攻击
 */
export function sanitizeInput(input, maxLength = 1000) {
  if (!input || typeof input !== 'string') {
    return '';
  }
  
  // Remove dangerous characters and patterns
  let sanitized = input
    .replace(/[<>]/g, '')  // Remove HTML tag characters
    .replace(/javascript:/gi, '')  // Remove javascript: protocol
    .replace(/on\w+=/gi, '')  // Remove event handlers
    .replace(/data:/gi, '')  // Remove data: protocol (for images)
    .trim();
  
  // Length limit
  if (maxLength && sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }
  
  return sanitized;
}

/**
 * Validate game ID
 * 验证游戏ID
 */
export function validateGameId(gameId) {
  const allowedGames = ['memory', 'story', 'number', 'music', 'picture'];
  return allowedGames.includes(gameId);
}

/**
 * Validate difficulty level
 * 验证难度等级
 */
export function validateDifficulty(difficulty) {
  return ['easy', 'medium', 'hard'].includes(difficulty);
}

/**
 * Validate user ID format
 * 验证用户ID格式
 */
export function validateUserId(userId) {
  if (!userId || typeof userId !== 'string') {
    return false;
  }
  
  // Allow alphanumeric, underscore, and hyphen
  const userIdPattern = /^[a-zA-Z0-9_-]+$/;
  if (!userIdPattern.test(userId)) {
    return false;
  }
  
  // Length check
  if (userId.length < 1 || userId.length > 100) {
    return false;
  }
  
  return true;
}

/**
 * Validate game action
 * 验证游戏操作
 */
export function validateGameAction(action, gameState, gameType) {
  if (!action || typeof action !== 'object') {
    return { valid: false, error: 'Invalid action format' };
  }
  
  // Validate action type
  const validActionTypes = getValidActionTypes(gameType);
  if (!validActionTypes.includes(action.type)) {
    return { valid: false, error: 'Invalid action type' };
  }
  
  // Validate timestamp
  if (action.timestamp) {
    const actionTime = new Date(action.timestamp);
    const now = new Date();
    const timeDiff = Math.abs(now - actionTime) / 1000; // seconds
    
    if (timeDiff > 300) {  // 5 minutes
      return { valid: false, error: 'Action timestamp too old' };
    }
    if (actionTime > now) {
      return { valid: false, error: 'Action timestamp in future' };
    }
  }
  
  // Game-specific validation
  switch (gameType) {
    case 'memory':
      return validateMemoryAction(action, gameState);
    case 'story':
      return validateStoryAction(action, gameState);
    case 'number':
      return validateNumberAction(action, gameState);
    case 'music':
      return validateMusicAction(action, gameState);
    case 'picture':
      return validatePictureAction(action, gameState);
    default:
      return { valid: false, error: 'Unknown game type' };
  }
}

/**
 * Get valid action types for a game
 * 获取游戏的有效操作类型
 */
function getValidActionTypes(gameType) {
  const actionTypes = {
    memory: ['FLIP_CARD', 'RESET', 'PAUSE'],
    story: ['ADD_SENTENCE', 'MODIFY_SENTENCE', 'SAVE_STORY'],
    number: ['DRAG_NUMBER', 'SUBMIT_ANSWER', 'USE_HINT'],
    music: ['TAP_RHYTHM', 'PAUSE', 'RESUME'],
    picture: ['DRAG_IMAGE', 'SUBMIT_CATEGORY', 'RESET']
  };
  
  return actionTypes[gameType] || [];
}

/**
 * Validate memory match game action
 * 验证记忆配对游戏操作
 */
function validateMemoryAction(action, gameState) {
  if (action.type === 'FLIP_CARD') {
    const cardIndex = action.cardIndex;
    
    if (typeof cardIndex !== 'number') {
      return { valid: false, error: 'Invalid card index type' };
    }
    
    const cards = gameState?.cards || [];
    if (cardIndex < 0 || cardIndex >= cards.length) {
      return { valid: false, error: 'Card index out of range' };
    }
    
    // Check if card is already flipped
    const flippedCards = gameState?.flippedCards || [];
    if (flippedCards.includes(cardIndex)) {
      return { valid: false, error: 'Card already flipped' };
    }
    
    // Check if too many cards are flipped
    if (flippedCards.length >= 2) {
      return { valid: false, error: 'Cannot flip more than 2 cards' };
    }
  }
  
  return { valid: true };
}

/**
 * Validate story chain game action
 * 验证故事接龙游戏操作
 */
function validateStoryAction(action, gameState) {
  if (action.type === 'ADD_SENTENCE') {
    const sentence = action.sentence;
    
    if (typeof sentence !== 'string') {
      return { valid: false, error: 'Sentence must be a string' };
    }
    
    // Sanitize and validate sentence
    const sanitized = sanitizeInput(sentence, 500);
    if (sanitized.length === 0) {
      return { valid: false, error: 'Sentence cannot be empty' };
    }
    
    if (sanitized.length > 500) {
      return { valid: false, error: 'Sentence too long' };
    }
  }
  
  return { valid: true };
}

/**
 * Validate number puzzle game action
 * 验证数字拼图游戏操作
 */
function validateNumberAction(action, gameState) {
  if (action.type === 'DRAG_NUMBER') {
    const numberIndex = action.numberIndex;
    const targetIndex = action.targetIndex;
    
    if (typeof numberIndex !== 'number' || typeof targetIndex !== 'number') {
      return { valid: false, error: 'Invalid index type' };
    }
    
    const numbers = gameState?.numbers || [];
    if (numberIndex < 0 || numberIndex >= numbers.length) {
      return { valid: false, error: 'Number index out of range' };
    }
    
    if (targetIndex < 0 || targetIndex >= numbers.length) {
      return { valid: false, error: 'Target index out of range' };
    }
  }
  
  return { valid: true };
}

/**
 * Validate music rhythm game action
 * 验证音乐节奏游戏操作
 */
function validateMusicAction(action, gameState) {
  if (action.type === 'TAP_RHYTHM') {
    const timestamp = action.timestamp;
    
    if (typeof timestamp !== 'number') {
      return { valid: false, error: 'Invalid timestamp' };
    }
    
    // Validate timestamp is reasonable (within last 5 seconds)
    const now = Date.now();
    if (Math.abs(now - timestamp) > 5000) {
      return { valid: false, error: 'Timestamp out of range' };
    }
  }
  
  return { valid: true };
}

/**
 * Validate picture sort game action
 * 验证图片分类游戏操作
 */
function validatePictureAction(action, gameState) {
  if (action.type === 'DRAG_IMAGE') {
    const imageId = action.imageId;
    const category = action.category;
    
    if (typeof imageId !== 'string' || imageId.length === 0) {
      return { valid: false, error: 'Invalid image ID' };
    }
    
    if (typeof category !== 'string' || category.length === 0) {
      return { valid: false, error: 'Invalid category' };
    }
    
    // Validate category is allowed
    const allowedCategories = gameState?.categories || [];
    if (!allowedCategories.includes(category)) {
      return { valid: false, error: 'Invalid category' };
    }
  }
  
  return { valid: true };
}

/**
 * Validate game state
 * 验证游戏状态
 */
export function validateGameState(gameState, gameType) {
  if (!gameState || typeof gameState !== 'object') {
    return { valid: false, error: 'Invalid game state format' };
  }
  
  // Validate game type
  if (!validateGameId(gameType)) {
    return { valid: false, error: 'Invalid game type' };
  }
  
  // Check state size (prevent DoS)
  const stateStr = JSON.stringify(gameState);
  if (stateStr.length > 100000) {  // 100KB limit
    return { valid: false, error: 'Game state too large' };
  }
  
  // Game-specific validation
  switch (gameType) {
    case 'memory':
      return validateMemoryState(gameState);
    case 'story':
      return validateStoryState(gameState);
    case 'number':
      return validateNumberState(gameState);
    case 'music':
      return validateMusicState(gameState);
    case 'picture':
      return validatePictureState(gameState);
    default:
      return { valid: false, error: 'Unknown game type' };
  }
}

/**
 * Validate memory match game state
 * 验证记忆配对游戏状态
 */
function validateMemoryState(gameState) {
  const cards = gameState.cards || [];
  
  // Check card count (max 12 pairs = 24 cards)
  if (cards.length > 24) {
    return { valid: false, error: 'Too many cards' };
  }
  
  // Validate each card
  for (const card of cards) {
    if (!card.id || typeof card.value === 'undefined') {
      return { valid: false, error: 'Invalid card format' };
    }
  }
  
  // Validate progress
  if (gameState.progress !== undefined) {
    if (gameState.progress < 0 || gameState.progress > 100) {
      return { valid: false, error: 'Invalid progress value' };
    }
  }
  
  return { valid: true };
}

/**
 * Validate story chain game state
 * 验证故事接龙游戏状态
 */
function validateStoryState(gameState) {
  const sentences = gameState.sentences || [];
  
  // Check sentence count
  if (sentences.length > 100) {
    return { valid: false, error: 'Too many sentences' };
  }
  
  // Validate each sentence
  for (const sentence of sentences) {
    if (typeof sentence !== 'string') {
      return { valid: false, error: 'Invalid sentence format' };
    }
    if (sentence.length > 500) {
      return { valid: false, error: 'Sentence too long' };
    }
  }
  
  return { valid: true };
}

/**
 * Validate number puzzle game state
 * 验证数字拼图游戏状态
 */
function validateNumberState(gameState) {
  const numbers = gameState.numbers || [];
  
  // Check number count
  if (numbers.length > 100) {
    return { valid: false, error: 'Too many numbers' };
  }
  
  // Validate each number
  for (const num of numbers) {
    if (typeof num !== 'number') {
      return { valid: false, error: 'Invalid number format' };
    }
    if (num < 0 || num > 1000) {
      return { valid: false, error: 'Number out of range' };
    }
  }
  
  return { valid: true };
}

/**
 * Validate music rhythm game state
 * 验证音乐节奏游戏状态
 */
function validateMusicState(gameState) {
  // Validate score
  if (gameState.score !== undefined) {
    if (typeof gameState.score !== 'number' || gameState.score < 0 || gameState.score > 100) {
      return { valid: false, error: 'Invalid score' };
    }
  }
  
  // Validate accuracy
  if (gameState.accuracy !== undefined) {
    if (typeof gameState.accuracy !== 'number' || gameState.accuracy < 0 || gameState.accuracy > 100) {
      return { valid: false, error: 'Invalid accuracy' };
    }
  }
  
  return { valid: true };
}

/**
 * Validate picture sort game state
 * 验证图片分类游戏状态
 */
function validatePictureState(gameState) {
  const images = gameState.images || [];
  
  // Check image count
  if (images.length > 50) {
    return { valid: false, error: 'Too many images' };
  }
  
  // Validate categories
  const categories = gameState.categories || [];
  if (categories.length < 2 || categories.length > 10) {
    return { valid: false, error: 'Invalid category count' };
  }
  
  return { valid: true };
}

/**
 * Generate CSRF token (client-side helper)
 * 生成CSRF Token（客户端辅助函数）
 */
export async function getCSRFToken() {
  try {
    const response = await fetch('/api/csrf-token', {
      method: 'GET',
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get CSRF token');
    }
    
    const data = await response.json();
    return data.token;
  } catch (error) {
    console.error('Error getting CSRF token:', error);
    return null;
  }
}

/**
 * Secure API request with CSRF token
 * 使用CSRF Token的安全API请求
 */
export async function secureApiRequest(url, options = {}) {
  const csrfToken = await getCSRFToken();
  
  // Get auth token from cookie (handled by browser)
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (csrfToken) {
    headers['X-CSRF-Token'] = csrfToken;
  }
  
  return fetch(url, {
    ...options,
    headers,
    credentials: 'include'  // Include cookies
  });
}

/**
 * Validate score is reasonable
 * 验证分数是否合理
 */
export function validateScore(score, gameType, difficulty) {
  if (typeof score !== 'number') {
    return { valid: false, error: 'Score must be a number' };
  }
  
  // Score should be between 0 and 100
  if (score < 0 || score > 100) {
    return { valid: false, error: 'Score out of range' };
  }
  
  return { valid: true };
}

/**
 * Detect suspicious activity
 * 检测可疑活动
 */
export function detectSuspiciousActivity(actions, gameState) {
  const warnings = [];
  
  // Check action frequency (too fast = possible automation)
  if (actions.length > 0) {
    const timeBetweenActions = [];
    for (let i = 1; i < actions.length; i++) {
      const timeDiff = actions[i].timestamp - actions[i - 1].timestamp;
      timeBetweenActions.push(timeDiff);
    }
    
    const avgTime = timeBetweenActions.reduce((a, b) => a + b, 0) / timeBetweenActions.length;
    if (avgTime < 100) {  // Less than 100ms between actions
      warnings.push('Actions too fast, possible automation');
    }
  }
  
  // Check for impossible scores
  if (gameState.score !== undefined) {
    if (gameState.score > 100) {
      warnings.push('Score exceeds maximum possible');
    }
  }
  
  return warnings;
}
