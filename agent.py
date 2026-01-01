import os
from fastapi import FastAPI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

app = FastAPI()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

@app.get("/")
def read_root():
    return {"status": "running", "message": "AI Agent API"}

@app.get("/ask")
def ask(q: str):
    response = llm.invoke([HumanMessage(content=q)])
    return {"question": q, "answer": response.content}