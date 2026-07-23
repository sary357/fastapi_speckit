# Quickstart: Like/Dislike 與留言收集 API

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contract**: [contracts/openapi.yaml](./contracts/openapi.yaml)

本文件說明如何在本地端以 Docker 啟動本功能並驗證其行為，對應規格的驗收情境。

## 前置需求

- Docker 與 Docker Compose（v2，即 `docker compose` 指令）已安裝
- （選用）本地 Python 3.14+ 環境，若要在容器外執行測試

> **注意**：`docker-compose.yml`、`requirements.txt`、`.env.example` 已由本計畫產生於
> repository 根目錄；`api` 服務直接使用官方 `python:3.14-slim` 映像並掛載原始碼執行，
> 不需另外的 `Dockerfile`。但 `src/`、`migrations/`、`alembic.ini` 等應用程式原始碼是由
> `/speckit.tasks` 與 `/speckit.implement` 階段建立；在這些檔案建立完成前，`docker compose
> up` 會因容器內找不到 `src/main.py` 而啟動失敗，屬預期現象。

## 環境變數

複製 `.env.example` 為 `.env` 並視需要調整：

```bash
cp .env.example .env
```

## 啟動本地端環境

```bash
docker compose up
```

此指令會啟動兩個服務：

- `db`：PostgreSQL 資料庫（依 [research.md](./research.md) 第 7 節）
- `api`：容器啟動時會先安裝 `requirements.txt` 相依套件，再啟動本 API 服務，監聽於
  `http://localhost:8000`（首次啟動需等待套件安裝完成）

## 驗證：讚／不讚反應（User Story 1）

```bash
# 送出「讚」
curl -i -X POST http://localhost:8000/api/reactions \
  -H "Content-Type: application/json" \
  -d '{"reaction_type": "like"}'

# 送出「不讚」
curl -i -X POST http://localhost:8000/api/reactions \
  -H "Content-Type: application/json" \
  -d '{"reaction_type": "dislike"}'
```

**預期結果**：兩次請求皆回應 HTTP 200 與 `{"status": "OK"}`（對應 spec.md 驗收情境 1、2）。

## 驗證：留言（User Story 2）

```bash
# 送出有效留言
curl -i -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -d '{"content": "這是一則測試留言"}'

# 送出空白留言（應被拒絕）
curl -i -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -d '{"content": "   "}'
```

**預期結果**：第一次請求回應 HTTP 200 與 `{"status": "OK"}`；第二次請求應被拒絕（HTTP 422），
且不應被記錄為有效留言（對應 spec.md 驗收情境 1、2 與 FR-008）。

```bash
# 送出超過 1000 字元長度限制的留言（應被拒絕）
curl -i -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"$(python3 -c 'print("a" * 1001)')\"}"
```

**預期結果**：回應 HTTP 422，且不應被記錄為有效留言（對應 FR-008、SC-007）。

## 驗證：速率限制（Rate Limiting）

```bash
# 連續送出 6 次讚反應（同一來源 IP，1 分鐘內）
for i in 1 2 3 4 5 6; do
  curl -i -X POST http://localhost:8000/api/reactions \
    -H "Content-Type: application/json" \
    -d '{"reaction_type": "like"}'
done
```

**預期結果**：前 5 次請求回應 HTTP 200 與 `{"status": "OK"}`；第 6 次請求回應 HTTP 429，
且不應被記錄為有效資料（對應 FR-012、SC-006）。

## 驗證：資料已正確記錄

透過 `db` 容器直接查詢，確認 `received_at`（UTC）與 `source_ip` 已正確寫入：

```bash
docker compose exec db psql -U postgres -d feedback \
  -c "SELECT reaction_type, received_at, source_ip FROM reactions ORDER BY received_at DESC LIMIT 5;"

docker compose exec db psql -U postgres -d feedback \
  -c "SELECT content, received_at, source_ip FROM comments ORDER BY received_at DESC LIMIT 5;"
```

## 執行自動化測試

```bash
docker compose exec api pytest
```

或於本地 Python 環境（需自行設定 `DATABASE_URL` 指向測試資料庫）：

```bash
pip install -r requirements.txt
pytest
```

## 關閉環境

```bash
docker compose down
```

加上 `-v` 可一併移除資料庫資料卷（僅限本地測試資料，正式環境請勿使用）：

```bash
docker compose down -v
```
