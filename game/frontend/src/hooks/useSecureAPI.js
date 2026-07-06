/**
 * Secure API Hook - Provides secure API request functions
 * 安全API Hook - 提供安全的API请求函数
 */

import { useState, useCallback } from 'react';
import { secureApiRequest, validateGameState, validateGameAction } from '../utils/security';

/**
 * Hook for making secure API requests
 * 用于进行安全API请求的Hook
 */
export function useSecureAPI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Secure API request with validation
   * 带验证的安全API请求
   */
  const secureRequest = useCallback(async (url, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      // Validate request data if provided
      if (options.body) {
        try {
          const bodyData = typeof options.body === 'string' 
            ? JSON.parse(options.body) 
            : options.body;
          
          // Validate game state if present
          if (bodyData.game_state) {
            const validation = validateGameState(
              bodyData.game_state,
              bodyData.game_type
            );
            if (!validation.valid) {
              throw new Error(validation.error);
            }
          }
          
          // Validate game action if present
          if (bodyData.action) {
            const validation = validateGameAction(
              bodyData.action,
              bodyData.game_state,
              bodyData.game_type
            );
            if (!validation.valid) {
              throw new Error(validation.error);
            }
          }
        } catch (e) {
          if (e.message.includes('valid')) {
            throw e;
          }
          // JSON parse error is OK, will be handled by server
        }
      }

      const response = await secureApiRequest(url, options);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Start a game session
   * 开始游戏会话
   */
  const startGame = useCallback(async (gameType, player1Id, player2Id, difficulty, settings = {}) => {
    return secureRequest('/api/games/start', {
      method: 'POST',
      body: JSON.stringify({
        game_type: gameType,
        player1_id: player1Id,
        player2_id: player2Id,
        difficulty: difficulty,
        settings: settings
      })
    });
  }, [secureRequest]);

  /**
   * Update game state
   * 更新游戏状态
   */
  const updateGame = useCallback(async (sessionId, gameState, action) => {
    return secureRequest('/api/games/update', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        game_state: gameState,
        action: action,
        timestamp: new Date().toISOString()
      })
    });
  }, [secureRequest]);

  /**
   * Complete game session
   * 完成游戏会话
   */
  const completeGame = useCallback(async (sessionId, finalState) => {
    return secureRequest('/api/games/complete', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        final_state: finalState
      })
    });
  }, [secureRequest]);

  /**
   * Get game history
   * 获取游戏历史
   */
  const getGameHistory = useCallback(async (userId, gameType, limit = 10) => {
    const params = new URLSearchParams({
      user_id: userId,
      game_type: gameType,
      limit: limit.toString()
    });
    
    return secureRequest(`/api/games/history?${params}`, {
      method: 'GET'
    });
  }, [secureRequest]);

  /**
   * Get game statistics
   * 获取游戏统计
   */
  const getGameStats = useCallback(async (userId) => {
    return secureRequest(`/api/games/stats?user_id=${userId}`, {
      method: 'GET'
    });
  }, [secureRequest]);

  return {
    loading,
    error,
    secureRequest,
    startGame,
    updateGame,
    completeGame,
    getGameHistory,
    getGameStats
  };
}
