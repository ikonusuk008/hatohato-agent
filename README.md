# hatohato-agent

AIエージェントAPI（Cap Info案件学習用）

## 技術スタック

- Python 3.12
- LangChain
- FastAPI
- Gemini API

## 起動方法
```bash
source ~/agent-env/bin/activate
export GOOGLE_API_KEY="your-api-key"
uvicorn agent:app --host 0.0.0.0 --port 8000
```

## エンドポイント

- `GET /` - ステータス確認
- `GET /ask?q=質問` - AIに質問