# 店家招募流程 (Host Recruitment Flow) PRD

## 1. 需求 (Requirements)

為了讓店家 (Host) 能夠順利地在平台上招募小幫手，並管理招募狀態與後續的行事曆安排，我們需要完善店家的招募流程。
- **建立 Profile 與職缺**：店家需要先建立店家 Profile，接著建立職缺 (Vacancy)。
- **設定職缺時間與狀態**：店家可以為職缺選取一段特定時間 (Vacancy Availability) 與人數上限 (Capacity，上限為 20 人)。若當前時間超過該時段，或店家將職缺狀態設為「未開始招聘 (Unavailable/Full)」，該職缺就不會顯示給小幫手。
- **小幫手申請與重疊時間檢查**：小幫手可以自己設定時間發送申請，但其申請的時間必須與店家設定的職缺時間有重疊 (Overlap)。
- **審核履歷與扣除名額**：店家可以審核履歷並決定是否同意。當店家同意小幫手的申請後 (狀態轉為 Accepted)，該職缺對應時段的剩餘名額需自動扣除 1 (即 current_helpers + 1)。
- **後續聯絡與行事曆同步**：
  - 小幫手後續換宿的時間以當初申請的時間為主。
  - 當申請被接受時，系統需同步將該換宿行程更新到店家的行事曆 (Calendar) 上。
  - 店家具有編輯行事曆調整小幫手換宿日期的功能。若小幫手需要修改時間，需向店家提出需求，由店家端更新行事曆。

## 2. 當前實作落差分析 (Gap Analysis)

經檢視當前的 API 與 Model 實作，發現有以下不足之處，尚未能完整提供上述需求：

1. **職缺顯示過濾 (Vacancy List Filtering)**：
   - 目前的 API (`GET /hosts/{host_id}/vacancies`) 會回傳該店家的所有職缺，**並未**根據「超過特定時間」或「狀態非 Recruiting」進行過濾。需要一個能讓小幫手搜尋與過濾有效職缺的 API。
2. **申請重疊時間檢查 (Application Time Overlap)**：
   - 目前 `ApplicationControllerAPI.create_application` 已有檢查小幫手申請的 `start_date` 與 `end_date` 是否落在 `VacancyAvailability` 內且未滿額的功能，這部分實作基本符合要求。
3. **同意申請後自動扣除名額 (Capacity Deduction)**：
   - 目前 `ApplicationControllerAPI.update_application_status` 只更新了 Application 的狀態為 `Accepted`，**並未**找到對應的 `VacancyAvailability` 並增加 `current_helpers` (或減少剩餘容量)。
4. **行事曆模型與同步 (Calendar Sync & Models)**：
   - 目前系統完全**缺乏 Calendar / Event 相關的 Model 與 API** (`features/calendar` 不存在)。
   - 當申請被接受時，無法自動建立對應的行事曆事件。
   - 缺乏讓店家編輯行事曆、調整小幫手日期的 Calendar API。

## 3. 期望功能與實作計畫 (Expected Features & Implementation Plan)

### Phase 1: 職缺顯示過濾與名額連動
- **擴充職缺列表 API**：提供專用的職缺搜尋/列表 API，僅回傳狀態為 `Recruiting` 且有效日期尚未過期的職缺與其可用時段。
- **修改 Application Status API**：在 `PATCH /applications/{application_id}/status` 中，當狀態變更為 `Accepted` 時，找出對應的 `VacancyAvailability`，檢查是否超過人數上限 20，並將 `current_helpers` 加 1。若取消接受，則需扣回。

### Phase 2: 行事曆模組 (Calendar Module)
- **Model 定義**：
  - 建立 `features/calendar/models.py`，包含 `CalendarEvent` (或 `HostCalendar`) Model。
  - 屬性需包含：關聯的店家 (Host) 與小幫手 (Helper)、開始日期、結束日期、對應的 Application ID、備註等。
- **自動建立事件**：
  - 結合 Phase 1 的 Application Status 更新，當狀態為 `Accepted` 時，自動寫入一筆 `CalendarEvent`。
- **Calendar API (Host)**：
  - 實作 `GET /calendar/events`：讓店家檢視自己的行事曆。
  - 實作 `PATCH /calendar/events/{event_id}`：讓店家可以編輯該事件（例如調整小幫手的 `start_date` 與 `end_date`）。

## 4. API 設計草案 (Draft API Design)

- `GET /vacancies/search` : 供小幫手搜尋可用職缺 (過濾已過期或非招募中)。
- `PATCH /applications/{id}/status` : (現有) 增強其邏輯，處理名額增減與觸發 Calendar Event 建立。
- `GET /hosts/{host_id}/calendar` : 取得某店家的行事曆事件列表。
- `PATCH /calendar/events/{event_id}` : 店家修改特定的換宿行程日期。
