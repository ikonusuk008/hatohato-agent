import os
from fastapi import FastAPI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from playwright.sync_api import sync_playwright

app = FastAPI()

llm = ChatAnthropic(
    model="claude-3-5-haiku-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

@app.get("/")
def read_root():
    return {"status": "running", "message": "AI Agent API (Claude)"}

@app.get("/ask")
def ask(q: str):
    response = llm.invoke([HumanMessage(content=q)])
    return {"question": q, "answer": response.content}

@app.get("/summarize")
def summarize(url: str):
    # Playwrightでページ取得
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        content = page.inner_text("body")[:5000]  # 最初の5000文字
        browser.close()
    
    # Claudeで要約
    prompt = f"""以下のWebページの内容を日本語で簡潔に要約してください。

【ページ内容】
{content}

【要約】"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "url": url,
        "summary": response.content
    }