# Research: Like/Dislike 與留言收集 API

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

本文件記錄技術方案的決策依據。使用者已在需求中明確指定核心技術棧（Python 3.14+、
FastAPI、PostgreSQL、Docker／docker compose 供本地測試），故無 `NEEDS CLARIFICATION`
項目需要解決；以下記錄的是在此技術棧下，落實規格所需的具體技術選型。

## 1. Web 框架與非同步執行模型

- **Decision**: 使用 FastAPI + Uvicorn（ASGI），所有路由與資料庫存取皆採非同步
  （`async def`）實作。
- **Rationale**: FastAPI 為使用者明確指定的框架；非同步模型可在單一 process 內以較少
  的執行緒/連線資源處理更高並發，有助於滿足規格 SC-003（至少 100 個並發請求）與
  憲章效能要求（p95 < 200ms）。FastAPI 亦可依 Pydantic 模型自動產生 OpenAPI 文件，
  滿足憲章 VII（文件要求）。
- **Alternatives considered**: Flask + gunicorn（同步模型，多工需仰賴多 worker
  process，資源效率較低）；Django（過重，本功能僅需 2 個寫入端點，不需 ORM 以外的
  Admin/Template 等功能）。

## 2. 資料庫存取層

- **Decision**: 使用 SQLAlchemy 2.x 的 async ORM，搭配 `asyncpg` 作為 PostgreSQL
  驅動；以 Alembic 管理資料庫結構遷移（schema migrations）。
- **Rationale**: SQLAlchemy 的 ORM 查詢採參數化語法，直接滿足憲章 VIII（防止 SQL
  Injection）；async 版本與 FastAPI 的非同步模型一致，避免阻塞事件迴圈；Alembic 為
  SQLAlchemy 生態系標準遷移工具，可讓資料庫結構變更有版本紀錄可追蹤。
- **Alternatives considered**: 原生 `psycopg`／SQL 字串組裝（需自行處理參數化與遷移，
  風險與維運成本較高）；Tortoise ORM（生態系與型別工具較 SQLAlchemy 小眾）。

## 3. 請求驗證與序列化

- **Decision**: 使用 Pydantic v2 model 定義請求 Body（如 `type: Literal["like",
  "dislike"]`、`content: str`，並對 `content` 加上 `min_length=1` 與去除純空白的
  驗證）與回應 Schema。
- **Rationale**: FastAPI 原生整合 Pydantic，可在到達商業邏輯前於系統邊界完成輸入驗證
  （對齊憲章 II「輸入必須於系統邊界驗證」與規格 FR-008、FR-011：缺漏或空白留言需被
  拒絕並回覆錯誤）。驗證失敗時 FastAPI 預設回覆 422，符合「不得回應成功狀態」的要求。

## 4. UTC 時間戳記錄方式

- **Decision**: 在應用層以 `datetime.now(timezone.utc)` 於收到請求當下產生時間戳，
  寫入資料庫欄位型別為 `TIMESTAMP WITH TIME ZONE`（PostgreSQL `timestamptz`）。
- **Rationale**: 應用層產生時間戳可確保紀錄的時間即為「收到請求」的當下時間，語意上
  對應規格 FR-004／FR-007（收到時間）；`timestamptz` 型別由資料庫層保證時區正確性，
  避免因伺服器時區設定不同而產生時間誤差。
- **Alternatives considered**: 資料庫端 `now()` 預設值（時間為「寫入資料庫當下」而非
  「API 收到請求當下」，兩者在高負載排隊情境下可能有微小差異，故選擇於應用層明確賦值）。

## 5. 來源 IP 擷取方式

- **Decision**: 於本地／單機部署情境下，直接使用 FastAPI `Request.client.host` 作為
  來源 IP；若請求經反向代理轉送，`X-Forwarded-For` 標頭的解析策略留待未來版本依實際
  部署拓樸決定（依規格 Assumptions 已聲明此屬實作細節、不在本規格規範範圍）。
- **Rationale**: 本地 docker compose 測試環境中，API 容器直接接收客戶端連線，
  `Request.client.host` 即為實際來源 IP，可滿足規格 FR-004／FR-007 的最小需求。

## 6. 測試策略

- **Decision**: 使用 `pytest` + `pytest-asyncio` 撰寫測試；契約測試以 `httpx.
  ASGITransport` 直接呼叫 FastAPI app（不需啟動實際伺服器），整合測試使用測試用
  PostgreSQL（可用 docker compose 啟動的測試資料庫或 testcontainers）驗證資料實際
  落地；單元測試涵蓋服務層的驗證邏輯（如空白留言拒絕）。
- **Rationale**: 對齊憲章 III（測試標準）70/20/10 的測試金字塔比例，並確保 CI 中
  可自動化、確定性地執行。

## 7. 容器化與本地測試環境

- **Decision**: 不另外撰寫 `Dockerfile`；`docker-compose.yml` 的 `api` 服務直接使用官方
  `python:3.14-slim` 映像，並以 volume 將專案原始碼掛載進容器（`./:/app`），容器啟動時透過
  `command` 依序執行 `pip install -r requirements.txt` 與 `uvicorn src.main:app --host 0.0.0.0
  --port 8000 --reload`。`db` 服務使用 `postgres:16-alpine`，並以 healthcheck 確保 `api`
  服務等待 `db` 就緒後再啟動。
- **Rationale**: 使用者明確要求「Dockerfile 應該不需要，可以幫我移除」，僅需要
  `docker-compose.yml` 供本地端測試使用；直接掛載原始碼並於啟動時安裝相依套件，可在不維護
  額外 Dockerfile 的前提下，仍使用使用者指定的 Python 3.14+ 版本執行與測試 API。
- **Trade-offs**: 每次執行 `docker compose up` 時皆會重新安裝相依套件，啟動速度較預先建置映像
  慢；此外映像不含編譯產物、每次啟動皆需網路存取套件來源。此取捨僅適用於「本地端測試」情境
  （使用者明確用途），若未來需要建置可移植的正式環境映像，仍可另行評估是否加回 Dockerfile。
- **Alternatives considered**: 撰寫獨立 `Dockerfile` 並於 `docker-compose.yml` 中以 `build`
  建置映像（可預先安裝相依套件、啟動更快，但使用者已明確要求移除，故不採用）；使用 SQLite
  取代 PostgreSQL 做本地測試（與使用者明確指定的 PostgreSQL 不一致，且可能導致方言差異造成
  測試與正式環境行為不同，故不採用）。

## 8. 速率限制（Rate Limiting）實作方式

- **Decision**: 使用 `slowapi`（基於 `limits` 套件、專為 Starlette/FastAPI 設計的速率限制
  函式庫），以請求的來源 IP（`request.client.host`）作為限制鍵值，對 `POST /api/reactions`
  與 `POST /api/comments` 兩個端點套用「每分鐘 3 次」的限制（依規格 FR-012），儲存後端使用
  預設的記憶體內（in-memory）儲存。超過限制時，`slowapi` 預設回覆 HTTP 429。
- **Rationale**: `slowapi` 可直接以裝飾器套用於 FastAPI 路由，設定簡單、與規格描述的
  「每個來源 IP 每分鐘最多 3 次請求（兩端點合計）」語意相符；本功能為單一 process 部署
  （docker compose 單一 `api` 容器），記憶體內儲存已足夠，不需引入 Redis 等額外元件。
- **Trade-offs**: 記憶體內儲存的限制計數器僅存在於單一 process 內，若未來部署為多個
  `api` 副本（horizontal scaling），各副本會有各自獨立的計數、無法共享限制狀態；若日後有
  多副本部署需求，需改用 Redis 等集中式儲存後端（`slowapi` 支援此擴充，屬未來調整項目，
  已於 [plan.md](./plan.md) 憲章檢核中註記）。
- **Alternatives considered**: 自行以 middleware 實作計數器（需重複造輪子，測試與維護成本
  higher）；於反向代理層（如 Nginx）設定速率限制（本地測試情境未使用反向代理，故不適用）。

## 9. Lint／格式化工具

- **Decision**: 使用 `ruff`（lint，含部分 `flake8`/`isort` 規則）與 `black`（格式化）。
- **Rationale**: 對齊憲章 II（一致性、自動化格式化工具）；`ruff` 執行速度快，適合在
  CI 與本地開發迴圈中頻繁執行。

## 未解決事項

無。使用者已提供足夠的技術棧資訊，且規格中已將「反向代理下的真實 IP 取得方式」等
超出規格範疇的細節於 Assumptions 明確排除。
