# Implementation Plan: Like/Dislike 與留言收集 API

**Branch**: `001-like-dislike-comments-api` | **Date**: 2026-07-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-like-dislike-comments-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command; its definition describes the execution workflow.

**Language**: Per the project constitution (Principle I, Language and Localization Standards), this
plan MUST be written in Traditional Chinese (zh-TW).

## Summary

提供一個無需身份驗證的後端 API，包含兩個寫入端點：（1）接收使用者送出的「讚／不讚」反應，
（2）接收使用者送出的留言。兩者皆須記錄收到時間（UTC）與來源 IP，成功處理後回應
`{"status": "OK"}`；留言內容需限制在 1 至 1000 字元，且兩端點皆須套用每來源 IP 每分鐘
最多 3 次的速率限制（FR-012）。技術上採用 Python 3.14+ 搭配 FastAPI 建構 API，資料以
PostgreSQL 持久化保存，並提供 docker compose 設定檔（不另外撰寫 Dockerfile，直接以官方
Python 映像掛載原始碼執行），讓開發者可在本地端以容器方式啟動 API 與資料庫進行測試。

## Technical Context

**Language/Version**: Python 3.14+

**Primary Dependencies**: FastAPI、Uvicorn（ASGI 伺服器）、SQLAlchemy 2.x（async ORM）、
asyncpg（PostgreSQL 非同步驅動）、Alembic（資料庫遷移）、Pydantic v2 / pydantic-settings（設定與請求驗證）、
slowapi（per-IP 速率限制，落實 FR-012）

**Storage**: PostgreSQL（本地測試透過 docker compose 啟動獨立容器）

**Testing**: pytest、pytest-asyncio、httpx（透過 FastAPI 的 ASGITransport/TestClient 呼叫 API 進行契約與整合測試）

**Target Platform**: Linux 容器（Docker），可部署於任何支援 Docker 的伺服器環境

**Project Type**: web-service（單一後端 API 專案，無前端）

**Performance Goals**: 依規格 SC-003，至少同時支援 100 個並發提交請求且不遺失資料或回應錯誤；
依專案憲章 V（效能要求），API 回應時間目標對齊 p95 < 200ms、p99 < 500ms

**Constraints**: 使用者送出請求後 1 秒內需收到回應（規格 SC-001）；本版本不得引入任何身份驗證
或授權機制（規格 FR-009）；每個來源 IP 每分鐘最多 3 次請求（規格 FR-012）；留言內容長度須
介於 1 至 1000 字元（規格 FR-008）；本地測試環境須可用 `docker compose` 一鍵啟動 API 與
資料庫，且不額外撰寫 Dockerfile（依使用者要求，直接以官方 Python 映像執行）

**Scale/Scope**: 2 個寫入端點（讚／不讚反應、留言），資料模型為輕量事件紀錄，無查詢／統計端點、
無使用者介面

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 適用性 | 檢核結果 |
|---|---|---|
| I. 語言與在地化標準 | 適用 | `spec.md`、`plan.md` 均以繁體中文撰寫；本功能無使用者介面文字，UI 文案相關條款不適用 |
| II. 程式碼品質 | 適用 | 採用 Pydantic/SQLAlchemy 型別化模型、`ruff`/`black` 自動化 lint 與格式化；函式維持精簡、單一職責 |
| III. 測試標準 | 適用 | 採用 pytest 依測試金字塔（單元／整合／契約）撰寫測試，CI 中自動執行 |
| IV. 使用者體驗一致性 | 不適用 | 本功能為純後端 API，無使用者介面、無設計系統或無障礙需求 |
| V. 效能要求 | 適用 | API 回應時間目標對齊 p95<200ms／p99<500ms；以非同步 FastAPI + 資料庫連線池滿足規格 SC-003 的並發需求；以 `slowapi` 落實每來源 IP 每分鐘 3 次的速率限制（FR-012），符合憲章「所有公開端點需速率限制」之規定；並已於 tasks.md 安排負載測試任務（模擬 100 個不同來源 IP 併發送出請求，驗證 SC-003），以符合憲章「重大發布前需完成負載測試」之規定 |
| VI. 程式碼審查標準 | 適用（流程面） | 交付時遵循 PR 審查流程；非本計畫的產出範圍，於實作/審查階段落實 |
| VII. 文件要求 | 適用 | FastAPI 自動產生 OpenAPI 文件；README 補充本地啟動與測試說明 |
| VIII. 安全標準 | 適用 | 使用 SQLAlchemy 參數化查詢防止 SQL Injection、Pydantic 進行輸入驗證；資料庫憑證以環境變數管理、不寫入程式碼或版控；來源 IP 屬個資範疇，於文件中註記留存政策待未來版本評估合規需求 |

**結論**：無違反項目，不需填寫 Complexity Tracking。

**Phase 1 設計後複查**：完成 `research.md`、`data-model.md`、`contracts/openapi.yaml` 與
`quickstart.md` 後重新檢視上表，設計內容（非同步 FastAPI、SQLAlchemy 參數化查詢、Pydantic
輸入驗證、環境變數管理憑證、Docker 容器化）與初次檢核結論一致，未新增任何違反憲章原則之
設計決策。

## Project Structure

### Documentation (this feature)

```text
specs/001-like-dislike-comments-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── main.py                  # FastAPI 應用程式進入點，掛載路由
├── core/
│   └── config.py             # 環境設定（DATABASE_URL 等），以 pydantic-settings 讀取環境變數
├── db/
│   ├── base.py                # SQLAlchemy Base 與共用設定
│   └── session.py             # 非同步資料庫連線 / Session 管理
├── models/
│   ├── reaction.py            # ReactionRecord ORM 模型
│   └── comment.py             # CommentRecord ORM 模型
├── schemas/
│   ├── reaction.py            # 讚／不讚請求與回應的 Pydantic Schema
│   └── comment.py             # 留言請求與回應的 Pydantic Schema
├── api/
│   └── routes/
│       ├── reactions.py       # POST /api/reactions 路由
│       └── comments.py        # POST /api/comments 路由
└── services/
    ├── reaction_service.py    # 讚／不讚寫入邏輯（含來源 IP、UTC 時間擷取）
    └── comment_service.py     # 留言寫入邏輯（含驗證、來源 IP、UTC 時間擷取）

migrations/                    # Alembic 資料庫遷移腳本

tests/
├── contract/                  # 針對兩個端點的請求/回應契約測試
├── integration/                # 端到端整合測試（含資料庫）
└── unit/                      # 服務層與工具函式的單元測試

docker-compose.yml               # 本地端測試：直接以官方 python:3.14-slim 映像掛載原始碼啟動 API + PostgreSQL 容器
.env.example                     # 環境變數範例（DATABASE_URL 等）
requirements.txt                 # Python 相依套件清單
```

**Structure Decision**: 採用單一專案結構（Option 1），因本功能僅為單一後端 API 服務、無前端或
行動端。API 程式碼置於 `src/`，依 FastAPI 慣例拆分為 `api`（路由）、`schemas`（請求/回應驗證）、
`models`（ORM 資料模型）、`services`（商業邏輯）、`db`（連線管理）與 `core`（設定）。測試依測試
金字塔拆分為 `tests/contract`、`tests/integration`、`tests/unit`。依使用者要求，本地測試不另外
撰寫 Dockerfile；`docker-compose.yml`（置於 repository 根目錄）中的 `api` 服務直接使用官方
`python:3.14-slim` 映像，以 volume 掛載專案原始碼並於容器啟動時安裝相依套件、執行 `uvicorn`。

## Complexity Tracking

> 本計畫未違反任何憲章原則，故不需填寫此表。
