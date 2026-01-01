import os
from fastapi import FastAPI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

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