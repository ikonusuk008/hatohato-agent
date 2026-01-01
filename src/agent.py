import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import tool, AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from tools import TaskTool

# LLM初期化
llm = ChatAnthropic(
    model="claude-3-5-haiku-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# TaskTool インスタンス
task_tool = TaskTool()

# LangChain Tools 定義
@tool
def add_task(task_name: str, priority: str = "medium", due_date: str = "") -> str:
    """
    タスクを追加します。
    
    Args:
        task_name: タスクの名前（例：「牛乳を買う」「会議の準備」）
        priority: 優先度。low（低）、medium（中）、high（高）から選択
        due_date: 期限。YYYY-MM-DD形式（例：2026-01-15）。省略可。
    
    Returns:
        実行結果のメッセージ
    """
    result = task_tool.add_task(task_name, priority, due_date)
    if result["success"]:
        return f"タスク「{task_name}」を追加しました（優先度: {priority}）"
    else:
        return f"エラー: {result['message']}"

@tool
def list_tasks() -> str:
    """
    登録されているタスクの一覧を取得します。
    
    Returns:
        タスク一覧
    """
    result = task_tool.list_tasks()
    if result["success"]:
        if result["count"] == 0:
            return "タスクはありません"
        return f"タスク一覧（{result['count']}件）:\n" + "\n".join(result["tasks"])
    else:
        return f"エラー: {result['message']}"

@tool
def search_tasks(keyword: str) -> str:
    """
    キーワードでタスクを検索します。
    
    Args:
        keyword: 検索キーワード
    
    Returns:
        検索結果
    """
    result = task_tool.search_task(keyword)
    if result["success"]:
        if result["count"] == 0:
            return f"「{keyword}」に一致するタスクはありません"
        return f"検索結果（{result['count']}件）:\n" + "\n".join(result["tasks"])
    else:
        return f"エラー: {result['message']}"

# ツール一覧
tools = [add_task, list_tasks, search_tasks]

# プロンプト
prompt = ChatPromptTemplate.from_messages([
    ("system", """あなたはタスク管理アシスタントです。
ユーザーの指示に従って、タスクの追加・一覧表示・検索を行います。

指示の例：
- 「牛乳を買うを追加して」→ add_task を使用
- 「タスク一覧を見せて」→ list_tasks を使用
- 「買い物のタスクを探して」→ search_tasks を使用

自然な日本語で応答してください。"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Agent作成
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_agent(user_input: str) -> str:
    """
    エージェントを実行する
    
    Args:
        user_input: ユーザーの入力
    
    Returns:
        エージェントの応答
    """
    try:
        result = agent_executor.invoke({"input": user_input})
        return result["output"]
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"