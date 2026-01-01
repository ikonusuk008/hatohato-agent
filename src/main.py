import os
import sys

# srcフォルダをパスに追加
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from guardrails import Guardrails
from agent import run_agent

app = FastAPI(
    title="AIタスク管理Bot",
    description="LangChain + Playwright + Guardrails を使用したAIエージェント",
    version="1.0.0"
)

# Guardrails初期化
guardrails = Guardrails()

# モックページを静的ファイルとして提供
MOCK_DIR = os.path.join(os.path.dirname(__file__), "..", "mock")
app.mount("/mock", StaticFiles(directory=MOCK_DIR, html=True), name="mock")

# リクエストモデル
class TaskRequest(BaseModel):
    message: str

# レスポンスモデル
class TaskResponse(BaseModel):
    success: bool
    message: str
    input_validation: dict
    output_validation: dict = None

@app.get("/")
def read_root():
    return {
        "status": "running",
        "message": "AIタスク管理Bot",
        "endpoints": {
            "POST /task": "タスク操作（自然言語）",
            "GET /logs": "ログ取得",
            "GET /mock/": "タスク管理ページ"
        }
    }

@app.post("/task", response_model=TaskResponse)
def handle_task(request: TaskRequest):
    """
    自然言語でタスクを操作する
    
    例：
    - 「牛乳を買うを追加して」
    - 「タスク一覧を見せて」
    - 「買い物のタスクを探して」
    """
    # 1. 入力検証（Guardrails）
    input_validation = guardrails.validate_input(request.message)
    
    if not input_validation["valid"]:
        return TaskResponse(
            success=False,
            message=input_validation["message"],
            input_validation=input_validation
        )
    
    # 2. エージェント実行（LangChain Agent + Playwright Tool）
    agent_response = run_agent(input_validation["sanitized_input"])
    
    # 3. 出力検証（Guardrails）
    # アクションを推測（簡易実装）
    action = "add"
    if "一覧" in request.message or "リスト" in request.message:
        action = "list"
    elif "検索" in request.message or "探して" in request.message:
        action = "search"
    
    output_validation = guardrails.validate_output(action, agent_response)
    
    if not output_validation["valid"]:
        return TaskResponse(
            success=False,
            message=output_validation["message"],
            input_validation=input_validation,
            output_validation=output_validation
        )
    
    # 4. 結果を返す
    return TaskResponse(
        success=True,
        message=agent_response,
        input_validation=input_validation,
        output_validation=output_validation
    )

@app.get("/logs")
def get_logs(date: str = None):
    """ログを取得する"""
    logs = guardrails.get_logs(date)
    return {
        "date": date or "today",
        "count": len(logs),
        "logs": logs
    }

@app.get("/health")
def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}