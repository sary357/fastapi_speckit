# Like/Dislike 與留言收集 API

無需身份驗證的後端 API，用於收集使用者的讚／不讚反應與留言。

**功能**:
- 👍 送出「讚」反應
- 👎 送出「不讚」反應
- 💬 送出留言（最多 1000 字元）
- 🚦 每來源 IP 每分鐘限制 5 次請求（兩端點合計）

## 快速開始（本地測試）

### 前提條件

- Docker & Docker Compose
- Python 3.14+ (用於本地開發)

### 使用 Docker Compose 啟動

```bash
# 啟動 API 與 PostgreSQL
docker compose up

# API 將在 http://localhost:8000 可用
# 健康檢查: http://localhost:8000/health
# OpenAPI 文件: http://localhost:8000/docs
```

### 本地開發（不使用 Docker）

```bash
# 建立虛擬環境
python3.14 -m venv venv
source venv/bin/activate

# 安裝相依套件
pip install -r requirements.txt

# 設定環境變數（複製並修改範例）
cp .env.example .env

# 執行資料庫遷移
alembic upgrade head

# 啟動開發伺服器
uvicorn src.main:app --reload
```

## API 端點

### POST /api/reactions

送出讚或不讚反應

**請求**:
```json
{
  "reaction_type": "like"
}
```

**回應** (200):
```json
{
  "status": "OK"
}
```

### POST /api/comments

送出留言

**請求**:
```json
{
  "content": "This is a comment"
}
```

**回應** (200):
```json
{
  "status": "OK"
}
```

## 測試

### 執行所有測試

```bash
# 需要 PostgreSQL 運行
pytest

# 含覆蓋率報告
pytest --cov=src
```

### 契約測試（無需資料庫）

```bash
pytest tests/contract/
```

### 手動測試（使用 docker compose）

```bash
# 啟動服務
docker compose up

# 在另一個終端，執行測試指令
# 測試讚反應
curl -X POST http://localhost:8000/api/reactions \
  -H "Content-Type: application/json" \
  -d '{"reaction_type": "like"}'

# 測試留言
curl -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello!"}'

# 測試速率限制（第 6 個請求應回 429）
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/reactions \
    -H "Content-Type: application/json" \
    -d '{"reaction_type": "like"}'
  echo ""
done

# 測試超長留言（應回 422）
curl -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -d '{"content": "'$(python3 -c 'print("a" * 1001)')'"}' 
```

## 環境變數

見 `.env.example`：

- `DATABASE_URL`: PostgreSQL 連線字串（預設：`postgresql+asyncpg://postgres:postgres@db:5432/feedback`）
- `ENVIRONMENT`: 執行環境（開發 vs 正式）

## 開發

### 程式碼品質

```bash
# Linting with ruff
ruff check src/

# 格式化 with black
black src/ tests/

# 自動修復
ruff check --fix src/
```

### 資料庫遷移

```bash
# 建立新遷移
alembic revision --autogenerate -m "描述"

# 套用遷移
alembic upgrade head

# 回復遷移
alembic downgrade -1
```

## 架構

- **FastAPI**: 現代 Python Web 框架
- **SQLAlchemy**: 非同步 ORM
- **PostgreSQL**: 資料庫
- **slowapi**: 速率限制
- **Pydantic**: 資料驗證

## 測試覆蓋

- 契約測試: POST 請求與回應格式
- 整合測試: 資料庫持久化
- 單元測試: 業務邏輯驗證
- 目標覆蓋率: >= 80%

## 授權

[MIT License](LICENSE)

fastAPI PoC for speckit
