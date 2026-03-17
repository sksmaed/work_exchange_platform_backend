# 小幫手申請流程 (Helper Application Flow) PRD

## 1. 需求 (Requirements)

為了讓小幫手能夠順利地在平台上尋找並申請換宿職缺，我們需要為小幫手建立一套完整的申請流程。
- 小幫手必須先建立/完善個人 Profile，其中包含「預計換宿時間」。預計換宿時間必須以「日」為單位，且**小幫手不可以選擇不連續的時段**（一次換宿必須是一段連續的日期）。
- 小幫手能根據已設定的 Profile 與換宿時間來過濾、搜尋合適的換宿店家與職缺。
- 小幫手可針對特定店家的職缺送出申請。
- 店家可檢視小幫手的申請並選擇接受或拒絕。

## 2. 詳細流程 (Detailed Flow)

1. **建立/更新個人 Profile**：
   - 小幫手使用者登入平台。
   - 進入個人資料頁面填寫/修改基本資料（自我介紹、專長等）以及預計換宿的時間區間（`start_date` 至 `end_date`）。
   - 前端與後端皆須驗證所選日期區間是否合法（例如：結束日期不可早於開始日期，且所選時段在儲存時視為一整段連續日期，不可間斷）。
2. **搜尋與篩選 (Search & Filter)**：
   - 系統依據小幫手的預計換宿時間，自動篩選出該時段仍有職缺（Vacancy）或未滿額的店家。
   - 小幫手亦可透過其他條件（如地點、專長需求等）進行進階篩選。
3. **瀏覽職缺並申請 (View and Apply)**：
   - 小幫手點擊感興趣的店家，進入店家與職缺詳情頁。
   - 選擇一個具體的職缺 (Vacancy) 並點擊申請。
   - 申請時，系統會記錄該次申請關聯的職缺、小幫手資訊、以及預計換宿時間，並將申請狀態設為 `Pending` (待處理)。
4. **店家回覆確認 (Host Review)**：
   - 店家收到申請通知。
   - 店家檢視小幫手 Profile 與申請詳情。
   - 店家將申請狀態更新為 `Accepted` (接受) 或 `Rejected` (拒絕)。

## 3. 期望功能 (Expected Features)

1. **Helper Profile Management API**:
   - 讓小幫手可以建立與更新個人資料（包含 `expected_time_periods` 或明確的開始與結束日期）。
   - 後端需具備「日期連續性」與「有效日期」的檢核機制。
2. **Vacancy Management API (Host)**:
   - 讓店家可以刊登、更新、發佈職缺資訊。
3. **Advanced Filter API**:
   - 店家與職缺列表 API 需支援以「日期（日為單位）」為條件的篩選。系統需判斷該職缺在指定日期內是否仍有空缺。
4. **Application API (現已部分實作)**:
   - 允許小幫手送出申請。
   - 允許店家更改申請狀態。

## 4. 實作計劃 (Implementation Plan)

### Phase 1: 小幫手 Profile API 與連續日期驗證
- **Schema 定義**: 在 `features/helper/schemas.py` 定義 Helper Profile 的建立與更新 Schema，並自訂 validator，驗證 `expected_time_periods` 必須為連續的日期區間（例如只接收明確的 `start_date` 和 `end_date` 格式，或檢查傳入的日期列表為連續天數）。
- **API 實作**: 在 `features/helper/apis.py` 實作 `GET /helper/profile` (取得自己 profile), `POST /helper/profile` (建立 profile) 以及 `PATCH /helper/profile` (更新 profile)。
- **測試撰寫**: 撰寫對應的 Unit Tests，特別著重於日期區間連續性的驗證。

### Phase 2: 職缺 (Vacancy) 刊登 API 
- **Schema 定義**: 在 `features/host/schemas.py` 中建立 Vacancy 相關的 Schema。
- **API 實作**: 在 `features/host/apis.py` 實作 Vacancy 的 CRUD。

### Phase 3: 篩選功能與搜尋優化
- **API 實作**: 更新 `HostControllerAPI.list_hosts` 與未來的職缺列表 API，加入日期的過濾條件。檢查投遞的連續日期是否與店家的需求相符，且職缺尚未額滿。

### Phase 4: 申請 API 補完與測試
- **API 更新**: 將已存在的 `create_application` 功能進行端到端測試，確保所有先決條件（Profile 建立、Vacancy 建立）都能正常運作，並通過系統完整的整合測試。
