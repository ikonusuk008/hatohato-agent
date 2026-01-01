import os
import json
from datetime import datetime
from typing import Any, Dict

# ログディレクトリ
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

class Guardrails:
    """入出力の検証とログ出力を行うガードレール"""
    
    # 禁止ワード（有害な入力をブロック）
    BLOCKED_WORDS = ["削除して", "全部消して", "システム終了", "drop table"]
    
    # 許可するタスク操作
    ALLOWED_ACTIONS = ["add", "list", "complete", "search"]
    
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
    
    def validate_input(self, user_input: str) -> Dict[str, Any]:
        """
        入力を検証する
        
        Returns:
            {"valid": bool, "message": str, "sanitized_input": str}
        """
        # 空チェック
        if not user_input or not user_input.strip():
            return {
                "valid": False,
                "message": "入力が空です",
                "sanitized_input": ""
            }
        
        # 長さチェック
        if len(user_input) > 500:
            return {
                "valid": False,
                "message": "入力が長すぎます（500文字以内）",
                "sanitized_input": ""
            }
        
        # 禁止ワードチェック
        lower_input = user_input.lower()
        for word in self.BLOCKED_WORDS:
            if word.lower() in lower_input:
                self._log("blocked_input", {
                    "input": user_input,
                    "blocked_word": word
                })
                return {
                    "valid": False,
                    "message": f"禁止されている操作です",
                    "sanitized_input": ""
                }
        
        # 検証OK
        sanitized = user_input.strip()
        self._log("validated_input", {"input": sanitized})
        
        return {
            "valid": True,
            "message": "OK",
            "sanitized_input": sanitized
        }
    
    def validate_output(self, action: str, result: Any) -> Dict[str, Any]:
        """
        出力を検証する
        
        Returns:
            {"valid": bool, "message": str, "result": Any}
        """
        # アクションチェック
        if action not in self.ALLOWED_ACTIONS:
            self._log("blocked_action", {
                "action": action,
                "result": str(result)
            })
            return {
                "valid": False,
                "message": f"許可されていないアクション: {action}",
                "result": None
            }
        
        # 検証OK
        self._log("validated_output", {
            "action": action,
            "result": str(result)
        })
        
        return {
            "valid": True,
            "message": "OK",
            "result": result
        }
    
    def _log(self, log_type: str, data: Dict[str, Any]):
        """ログをファイルに出力"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": log_type,
            "data": data
        }
        
        # 日付ごとのログファイル
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(LOG_DIR, f"{date_str}.json")
        
        # 追記モードで書き込み
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_logs(self, date_str: str = None) -> list:
        """ログを取得"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        log_file = os.path.join(LOG_DIR, f"{date_str}.json")
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
        
        return logs