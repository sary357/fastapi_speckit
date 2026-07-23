---

description: "Task list template for feature implementation"
---

# Tasks: Like/Dislike 與留言收集 API

**Input**: Design documents from `/specs/001-like-dislike-comments-api/`

**Prerequisites**: plan.md（必要）、spec.md（必要，含使用者故事）、research.md、data-model.md、contracts/

**Tests**: 本次任務清單依使用者明確要求「拆解出測試程式碼的任務清單」，故每個使用者故事皆包含
測試任務（契約測試、整合測試、單元測試），並依 TDD 原則排在對應實作任務之前。

**Organization**: 任務依使用者故事分組，讓每個故事可獨立實作與測試。

**Language**: Per the project constitution (Principle I, Language and Localization Standards), task
descriptions MUST be written in Traditional Chinese (zh-TW).

## Format: `[ID] [P?] [Story] Description`

- **[P]**：可平行執行（不同檔案、無相依關係）
- **[Story]**：此任務所屬的使用者故事（US1、US2）
- 各任務描述皆包含明確檔案路徑

## Path Conventions

單一專案結構（依 [plan.md](./plan.md) 的 Structure Decision）：`src/`、`tests/`、
`migrations/` 位於 repository 根目錄。

---

## Phase 1: Setup（共用基礎建設）

**Purpose**: 專案初始化與基礎結構

- [x] T001 依 plan.md 的 Project Structure 建立目錄結構：`src/{core,db,models,schemas,api/routes,services}`、`tests/{contract,integration,unit}`、`migrations/`（含 `__init__.py` 等必要檔案）
- [x] T002 於 `pyproject.toml` 設定 `pytest`（含 `pytest-asyncio` 的 `asyncio_mode`）與測試涵蓋率門檻（依憲章 III，最低 80%）
- [x] T003 [P] 於 `pyproject.toml` 設定 `ruff`（lint）與 `black`（格式化）規則（依憲章 II、research.md 第 9 節）
- [x] T004 [P] 建立 `alembic.ini` 與 `migrations/env.py`，設定連線至 `DATABASE_URL`（依 research.md 第 2 節）

---

## Phase 2: Foundational（阻塞性先決條件）

**Purpose**: 所有使用者故事皆依賴的核心基礎建設

**⚠️ CRITICAL**: 本階段完成前，不得開始任何使用者故事的實作

- [x] T005 於 `src/core/config.py` 建立 `pydantic-settings` 設定類別，讀取 `DATABASE_URL` 等環境變數
- [x] T006 於 `src/db/base.py` 建立 SQLAlchemy `DeclarativeBase`
- [x] T007 於 `src/db/session.py` 建立非同步 engine 與 `AsyncSession` 相依注入（depends on T005, T006）
- [x] T008 [P] 於 `src/core/rate_limit.py` 建立共用的 `slowapi` `Limiter` 實例，以 `request.client.host` 為鍵值（依 research.md 第 8 節、規格 FR-012）
- [x] T009 於 `src/main.py` 建立 FastAPI 應用程式進入點，掛載 `Limiter`、註冊 429／422 錯誤處理器（depends on T008）
- [x] T010 [P] 於 `src/core/errors.py` 建立統一的驗證失敗與速率限制錯誤回應格式（呼應 contracts/openapi.yaml 的 `ErrorResponse`）

**Checkpoint**: 基礎建設完成，使用者故事可開始平行實作

---

## Phase 3: User Story 1 - 送出讚 (Like) 或不讚 (Dislike) 反應 (Priority: P1) 🎯 MVP

**Goal**: 使用者可透過 HTTP POST 送出讚／不讚反應，系統記錄 UTC 時間與來源 IP 並回應成功

**Independent Test**: 送出一次「讚」與一次「不讚」的 POST 請求，驗證皆回應 HTTP 200 與
`{"status": "OK"}`，且資料庫各自新增一筆對應的反應紀錄

### Tests for User Story 1 ⚠️

> **注意：以下測試須先撰寫並確認會失敗，之後才開始實作**

- [x] T011 [P] [US1] 契約測試：`POST /api/reactions` 送出 `like` 回應 200 與 `{"status": "OK"}`，於 `tests/contract/test_reactions_contract.py`
- [x] T012 [P] [US1] 契約測試：`POST /api/reactions` 送出 `dislike` 回應 200 與 `{"status": "OK"}`，於 `tests/contract/test_reactions_contract.py`
- [x] T013 [P] [US1] 契約測試：`POST /api/reactions` 缺漏或不合法的 `reaction_type` 回應 422，於 `tests/contract/test_reactions_contract.py`
- [x] T014 [P] [US1] 契約測試：同一來源 IP 於 1 分鐘內第 4 次請求回應 429（依 FR-012、SC-006），於 `tests/contract/test_reactions_contract.py`
- [x] T015 [P] [US1] 整合測試：反應提交後，資料庫確實新增一筆包含正確 `reaction_type`、UTC `received_at`、`source_ip` 的紀錄，於 `tests/integration/test_reactions_integration.py`
- [x] T016 [P] [US1] 單元測試：`ReactionService` 對非法 `reaction_type` 拋出驗證錯誤，於 `tests/unit/test_reaction_service.py`

### Implementation for User Story 1

- [x] T017 [P] [US1] 建立 `ReactionRecord` ORM 模型（`reaction_type`、`received_at`、`source_ip`）於 `src/models/reaction.py`
- [x] T018 [P] [US1] 建立讚／不讚請求與回應的 Pydantic Schema 於 `src/schemas/reaction.py`
- [x] T019 [US1] 實作 `ReactionService`（寫入紀錄、擷取 UTC 時間與來源 IP）於 `src/services/reaction_service.py`（depends on T017, T018）
- [x] T020 [US1] 實作 `POST /api/reactions` 路由，套用速率限制裝飾器於 `src/api/routes/reactions.py`（depends on T019, T008）
- [x] T021 [US1] 新增 `reactions` 資料表的 Alembic migration 於 `migrations/versions/`
- [x] T022 [US1] 於 `src/main.py` 掛載 `reactions` 路由（depends on T020）

**Checkpoint**: User Story 1 應可獨立完整運作與測試

---

## Phase 4: User Story 2 - 送出留言 (Comment) (Priority: P2)

**Goal**: 使用者可透過 HTTP POST 送出留言，系統驗證內容、記錄 UTC 時間與來源 IP 並回應成功

**Independent Test**: 送出一筆有效留言的 POST 請求，驗證回應 HTTP 200 與 `{"status": "OK"}`，
且資料庫新增一筆對應的留言紀錄；送出空白或超長留言時應被拒絕

### Tests for User Story 2 ⚠️

> **注意：以下測試須先撰寫並確認會失敗，之後才開始實作**

- [x] T023 [P] [US2] 契約測試：`POST /api/comments` 送出有效留言回應 200 與 `{"status": "OK"}`，於 `tests/contract/test_comments_contract.py`
- [x] T024 [P] [US2] 契約測試：`POST /api/comments` 送出空白或缺漏留言回應 422（依 FR-008），於 `tests/contract/test_comments_contract.py`
- [x] T025 [P] [US2] 契約測試：`POST /api/comments` 送出超過 1000 字元的留言回應 422（依 FR-008、SC-007），於 `tests/contract/test_comments_contract.py`
- [x] T026 [P] [US2] 契約測試：同一來源 IP 於 1 分鐘內第 4 次留言請求回應 429（依 FR-012、SC-006），於 `tests/contract/test_comments_contract.py`
- [x] T027 [P] [US2] 整合測試：留言提交後，資料庫確實新增一筆包含正確 `content`、UTC `received_at`、`source_ip` 的紀錄，於 `tests/integration/test_comments_integration.py`
- [x] T028 [P] [US2] 單元測試：`CommentService` 拒絕空白／缺漏／超過 1000 字元的留言內容，於 `tests/unit/test_comment_service.py`

### Implementation for User Story 2

- [x] T029 [P] [US2] 建立 `CommentRecord` ORM 模型（`content`、`received_at`、`source_ip`）於 `src/models/comment.py`
- [x] T030 [P] [US2] 建立留言請求與回應的 Pydantic Schema（`min_length=1`、`max_length=1000`，去除前後空白後驗證非空）於 `src/schemas/comment.py`
- [x] T031 [US2] 實作 `CommentService`（驗證內容、寫入紀錄、擷取 UTC 時間與來源 IP）於 `src/services/comment_service.py`（depends on T029, T030）
- [x] T032 [US2] 實作 `POST /api/comments` 路由，套用速率限制裝飾器於 `src/api/routes/comments.py`（depends on T031, T008）
- [x] T033 [US2] 新增 `comments` 資料表的 Alembic migration 於 `migrations/versions/`
- [x] T034 [US2] 於 `src/main.py` 掛載 `comments` 路由（depends on T032）

**Checkpoint**: User Story 1 與 User Story 2 應皆可獨立運作

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: 影響多個使用者故事的改善項目

- [x] T035 [P] 單元測試：驗證速率限制器以「讚／不讚與留言兩端點合計」計算同一來源 IP 的請求次數，於 `tests/unit/test_rate_limit.py`
- [x] T036 [P] 執行 `pytest --cov` 確認整體測試涵蓋率達到憲章 III 要求的 80% 門檻
- [x] T037 依 [quickstart.md](./quickstart.md) 完整執行本地端 `docker compose` 驗證流程（讚／不讚、留言、速率限制、超長留言情境）
- [x] T038 [P] 於 `README.md` 補充本地啟動、`docker compose` 使用與測試執行說明
- [x] T039 安全性檢查：確認所有查詢皆為參數化（SQLAlchemy ORM）、輸入皆於系統邊界驗證、無憑證寫死於程式碼中（依憲章 VIII）
- [x] T040 負載測試：模擬至少 100 個不同來源 IP（避免觸發 FR-012 的 per-IP 速率限制）併發送出讚／不讚與留言請求，驗證全部成功回應且資料完整、無遺失（依規格 SC-003、憲章 V「重大發布前需完成負載測試」之規定），於 `tests/integration/test_load.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**：無相依，可立即開始
- **Foundational (Phase 2)**：依賴 Setup 完成 — 阻塞所有使用者故事
- **User Stories (Phase 3+)**：皆依賴 Foundational 完成
  - User Story 1（P1）與 User Story 2（P2）互不相依，可平行進行
  - 亦可依優先順序循序進行（P1 → P2）
- **Polish (Final Phase)**：依賴所需的使用者故事皆已完成

### User Story Dependencies

- **User Story 1 (P1)**：Foundational 完成後即可開始，不依賴其他使用者故事
- **User Story 2 (P2)**：Foundational 完成後即可開始；與 User Story 1 共用 Foundational 的速率限制器（T008），但功能上彼此獨立可測試

### Within Each User Story

- 測試（契約／整合／單元）須先撰寫並確認失敗，再開始實作
- Models 先於 Services
- Services 先於 API 路由
- 核心實作先於資料庫 migration 與路由掛載

### Parallel Opportunities

- Setup 階段標記 [P] 的任務可平行執行（T003、T004）
- Foundational 階段標記 [P] 的任務可平行執行（T008、T010）
- Foundational 完成後，User Story 1 與 User Story 2 可由不同開發者平行進行
- 同一使用者故事內標記 [P] 的測試與模型任務可平行執行

---

## Parallel Example: User Story 1

```bash
# 平行執行 User Story 1 的所有測試：
Task: "契約測試：POST /api/reactions 送出 like 回應 200 於 tests/contract/test_reactions_contract.py"
Task: "契約測試：POST /api/reactions 送出 dislike 回應 200 於 tests/contract/test_reactions_contract.py"
Task: "契約測試：POST /api/reactions 缺漏 reaction_type 回應 422 於 tests/contract/test_reactions_contract.py"
Task: "契約測試：同一 IP 第 4 次請求回應 429 於 tests/contract/test_reactions_contract.py"
Task: "整合測試：反應紀錄正確寫入於 tests/integration/test_reactions_integration.py"
Task: "單元測試：ReactionService 驗證邏輯於 tests/unit/test_reaction_service.py"

# 平行執行 User Story 1 的所有模型／Schema：
Task: "建立 ReactionRecord ORM 模型於 src/models/reaction.py"
Task: "建立讚／不讚 Pydantic Schema 於 src/schemas/reaction.py"
```

---

## Implementation Strategy

### MVP First (僅 User Story 1)

1. 完成 Phase 1：Setup
2. 完成 Phase 2：Foundational（關鍵 — 阻塞所有故事）
3. 完成 Phase 3：User Story 1
4. **停止並驗證**：獨立測試 User Story 1
5. 準備好即可部署／展示

### Incremental Delivery

1. 完成 Setup + Foundational → 基礎建設就緒
2. 加入 User Story 1 → 獨立測試 → 部署／展示（MVP！）
3. 加入 User Story 2 → 獨立測試 → 部署／展示
4. 每個故事皆在不破壞先前故事的前提下增加價值

### Parallel Team Strategy

多位開發者情境：

1. 團隊共同完成 Setup + Foundational
2. Foundational 完成後：
   - 開發者 A：User Story 1
   - 開發者 B：User Story 2
3. 各故事獨立完成並整合

---

## Notes

- [P] 任務 = 不同檔案、無相依關係
- [Story] 標籤將任務對應到特定使用者故事，便於追蹤
- 每個使用者故事應可獨立完成與測試
- 實作前須先確認測試會失敗
- 每完成一個任務或一組邏輯任務即進行提交
