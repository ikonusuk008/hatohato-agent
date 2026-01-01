import os
from typing import Optional
from playwright.sync_api import sync_playwright

# モックページのパス
MOCK_DIR = os.path.join(os.path.dirname(__file__), "..", "mock")

class TaskTool:
    """Playwrightでタスク管理ページを操作するTool"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or f"file://{os.path.abspath(MOCK_DIR)}/index.html"
    
    def add_task(self, task_name: str, priority: str = "medium", due_date: str = "") -> dict:
        """
        タスクを追加する
        
        Args:
            task_name: タスク名
            priority: 優先度 (low/medium/high)
            due_date: 期限 (YYYY-MM-DD形式)
        
        Returns:
            {"success": bool, "message": str}
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # ページを開く
                page.goto(self.base_url)
                page.wait_for_load_state("networkidle")
                
                # タスク名を入力
                page.fill("#taskName", task_name)
                
                # 優先度を選択
                if priority in ["low", "medium", "high"]:
                    page.select_option("#priority", priority)
                
                # 期限を入力
                if due_date:
                    page.fill("#dueDate", due_date)
                
                # 送信ボタンをクリック
                page.click("#submitBtn")
                
                # 成功メッセージを確認
                page.wait_for_selector(".message.success", timeout=5000)
                message = page.inner_text("#message")
                
                # スクリーンショットを保存（デバッグ用）
                screenshot_path = os.path.join(MOCK_DIR, "..", "logs", "last_action.png")
                page.screenshot(path=screenshot_path)
                
                browser.close()
                
                return {
                    "success": True,
                    "message": message,
                    "task": {
                        "name": task_name,
                        "priority": priority,
                        "due_date": due_date
                    }
                }
                
            except Exception as e:
                browser.close()
                return {
                    "success": False,
                    "message": f"エラー: {str(e)}",
                    "task": None
                }
    
    def list_tasks(self) -> dict:
        """
        タスク一覧を取得する
        
        Returns:
            {"success": bool, "tasks": list}
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto(self.base_url)
                page.wait_for_load_state("networkidle")
                
                # タスク一覧を取得
                tasks = page.query_selector_all(".task-item")
                task_list = []
                
                for task in tasks:
                    text = task.inner_text()
                    task_list.append(text)
                
                browser.close()
                
                return {
                    "success": True,
                    "tasks": task_list,
                    "count": len(task_list)
                }
                
            except Exception as e:
                browser.close()
                return {
                    "success": False,
                    "tasks": [],
                    "message": f"エラー: {str(e)}"
                }
    
    def search_task(self, keyword: str) -> dict:
        """
        タスクを検索する
        
        Args:
            keyword: 検索キーワード
        
        Returns:
            {"success": bool, "tasks": list}
        """
        result = self.list_tasks()
        
        if not result["success"]:
            return result
        
        # キーワードでフィルタ
        filtered = [t for t in result["tasks"] if keyword.lower() in t.lower()]
        
        return {
            "success": True,
            "tasks": filtered,
            "count": len(filtered),
            "keyword": keyword
        }


# LangChain Tool用のラッパー関数
def add_task_tool(task_name: str, priority: str = "medium", due_date: str = "") -> str:
    """タスクを追加するTool"""
    tool = TaskTool()
    result = tool.add_task(task_name, priority, due_date)
    return str(result)

def list_tasks_tool() -> str:
    """タスク一覧を取得するTool"""
    tool = TaskTool()
    result = tool.list_tasks()
    return str(result)

def search_task_tool(keyword: str) -> str:
    """タスクを検索するTool"""
    tool = TaskTool()
    result = tool.search_task(keyword)
    return str(result)