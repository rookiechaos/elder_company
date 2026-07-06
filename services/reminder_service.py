"""
Reminder Service
AI-generated reminders with a gentle tone
"""

from typing import Dict, Any, Optional
from datetime import datetime
from services.logging_service import logger


class ReminderService:
    """Reminder service"""
    
    @staticmethod
    def generate_gentle_reminder(
        reminder_type: str,
        task_title: Optional[str] = None,
        schedule_title: Optional[str] = None,
        due_time: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate gentle-tone reminder (AI)
        
        Args:
            reminder_type: Reminder type (task, schedule, medication, exercise, etc.)
            task_title: Task title (optional)
            schedule_title: Schedule title (optional)
            due_time: Due time (optional)
            context: Context (optional)
            
        Returns:
            Gentle-tone reminder text
        """
        try:
            from services.ai_providers import get_ai_provider
            
            ai_provider = get_ai_provider()
            
            # Build prompt
            time_str = ""
            if due_time:
                time_str = f"時間：{due_time.strftime('%H:%M')}"
            
            title = task_title or schedule_title or ""
            
            prompt = f"""以下の情報に基づいて、温かく優しいトーンのリマインダーメッセージを生成してください。

リマインダータイプ：{reminder_type}
タイトル：{title}
{time_str}

要件：
1. 温かく、優しいトーン
2. 催促感を避ける
3. 30字以内
4. 日本語で
5. 「一緒に確認しましょうか？」のような協力的な表現を含める

例：
- 「お時間です。お薬を飲む時間になりました。一緒に確認しましょうか？」
- 「今日は素晴らしい一日でした。3つのタスクを一緒に完了しました！」
"""
            
            messages = [
                {"role": "system", "content": "あなたは介護の専門家で、温かく優しいトーンのリマインダーメッセージを生成するアシスタントです。催促感を避け、協力的な表現を使用します。"},
                {"role": "user", "content": prompt}
            ]
            
            # Handle async/sync invocation
            import asyncio
            import inspect
            
            try:
                if inspect.iscoroutinefunction(ai_provider.chat):
                    loop = asyncio.get_event_loop()
                    response = loop.run_until_complete(
                        ai_provider.chat(
                            messages=messages,
                            temperature=0.7,
                            max_tokens=150
                        )
                    )
                else:
                    response = ai_provider.chat(
                        messages=messages,
                        temperature=0.7,
                        max_tokens=150
                    )
                
                reminder = response.get("text", "").strip()
                
                # Use fallback reminder if AI generation fails
                if not reminder or len(reminder) < 10:
                    return ReminderService._get_fallback_reminder(reminder_type, title)
                
                return reminder
                
            except Exception as e:
                logger.log_warning(f"Failed to call AI provider for reminder: {e}")
                return ReminderService._get_fallback_reminder(reminder_type, title)
            
        except Exception as e:
            logger.log_warning(f"Failed to generate AI reminder: {e}")
            return ReminderService._get_fallback_reminder(reminder_type, title)
    
    @staticmethod
    def _get_fallback_reminder(reminder_type: str, title: str) -> str:
        """
        Get fallback reminder when AI unavailable
        
        Args:
            reminder_type: Reminder type
            title: Title
            
        Returns:
            Fallback reminder text
        """
        fallback_reminders = {
            "task": f"お時間です。{title}の時間になりました。一緒に確認しましょうか？",
            "schedule": f"お時間です。{title}の時間になりました。",
            "medication": "お時間です。お薬を飲む時間になりました。一緒に確認しましょうか？",
            "exercise": "お時間です。運動の時間になりました。一緒に始めましょうか？",
            "appointment": "お時間です。予約の時間が近づいています。準備を始めましょうか？"
        }
        
        if reminder_type in fallback_reminders:
            return fallback_reminders[reminder_type]
        
        if title:
            return f"お時間です。{title}の時間になりました。一緒に確認しましょうか？"
        
        return "お時間です。確認しましょうか？"
