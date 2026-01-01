FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /app

# システム依存パッケージ（Playwright用）
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwrightブラウザをインストール
RUN playwright install chromium

# アプリケーションをコピー
COPY src/ ./src/
COPY mock/ ./mock/
COPY logs/ ./logs/

# 環境変数
ENV PYTHONUNBUFFERED=1

# ポート
EXPOSE 8000

# 起動コマンド
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]