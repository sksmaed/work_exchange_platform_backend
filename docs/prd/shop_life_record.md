# 店家生活紀錄 (Shop Life Record) PRD

## 1. 需求 (Requirements)

為了讓店家能夠在平台上展示日常生活與工作環境，吸引更多小幫手，同時促進社群互動，我們需要提供「店家生活紀錄」功能，涵蓋**相簿 (Album)** 與**貼文 (Post)** 兩個子模組。

### 1.1 相簿 (Album)

- **每個店家固定一個相簿**：相簿隨店家 Profile 自動建立，無需手動管理（無建立、編輯、刪除相簿的操作）。
- **圖片管理**：店家可在相簿內新增或移除圖片。
- **相簿瀏覽**：平台上所有人（包含未登入訪客）均可瀏覽店家的相簿及其圖片。

### 1.2 貼文 (Post)

- **店家發布貼文**：店家可以發布包含文字與圖片的貼文，圖片支援多張上傳。
- **貼文瀏覽**：平台上所有人均可瀏覽店家的貼文列表與單篇貼文內容。
- **留言 (Comment)**：已登入的使用者可以在貼文下方留言；留言者可以刪除自己的留言，店家可以刪除其貼文下的任意留言。
- **愛心 (Like)**：已登入的使用者可以對貼文按愛心或取消愛心。

## 2. 當前實作落差分析 (Gap Analysis)

目前系統中尚無「店家生活紀錄」相關的 Model 或 API 實作，需全新建立以下內容：

1. **相簿功能缺失**：系統中無 `AlbumPhoto` 相關的 Model、Schema 與 API（相簿本身以店家 Profile 為錨點，無獨立 Album 表）。
2. **貼文功能缺失**：系統中無 `Post`、`PostPhoto`、`Comment`、`Like` 相關的 Model、Schema 與 API。
3. **圖片儲存整合**：目前尚未確認統一的圖片上傳機制，需在此模組中定義或複用現有方案。

## 3. 期望功能與實作計畫 (Expected Features & Implementation Plan)

### Phase 1: 相簿模組 (Album Module)

- **Model 定義**：
  - `AlbumPhoto`：關聯店家 (`Host`)、圖片 URL、排序索引、建立時間。（相簿即為該店家的所有 `AlbumPhoto`，不需獨立的 `Album` 表）
- **API 實作**：
  - `GET /hosts/{host_id}/album`：取得店家的相簿（所有圖片列表）（所有人可存取）。
  - `POST /hosts/{host_id}/album/photos`：店家上傳圖片至相簿（僅限本人）。
  - `DELETE /hosts/{host_id}/album/photos/{photo_id}`：店家移除相簿內的圖片（僅限本人）。

### Phase 2: 貼文模組 (Post Module)

- **Model 定義**：
  - `Post`：關聯店家 (`Host`)、文字內容、建立時間、更新時間、愛心數、留言數。
  - `PostPhoto`：關聯 `Post`、圖片 URL、排序索引。
  - `Comment`：關聯 `Post`、留言者 (`User`)、留言內容、建立時間。
  - `PostLike`：關聯 `Post`、按愛心的使用者 (`User`)、按愛心時間（唯一約束：同一使用者對同一貼文只能按一次）。
- **API 實作**：
  - `POST /hosts/{host_id}/posts`：店家發布貼文（包含文字與圖片）（僅限本人）。
  - `PATCH /posts/{post_id}`：店家編輯貼文內容（僅限本人）。
  - `DELETE /posts/{post_id}`：店家刪除貼文（僅限本人，連同相關圖片、留言與愛心一併刪除）。
  - `GET /hosts/{host_id}/posts`：取得店家的貼文列表，依建立時間倒序排列（所有人可存取）。
  - `GET /posts/{post_id}`：取得單一貼文詳細資訊（所有人可存取）。
  - `POST /posts/{post_id}/comments`：已登入使用者對貼文留言。
  - `DELETE /posts/{post_id}/comments/{comment_id}`：留言者刪除自己的留言，或店家刪除其貼文下的留言。
  - `GET /posts/{post_id}/comments`：取得貼文的留言列表（所有人可存取）。
  - `POST /posts/{post_id}/likes`：已登入使用者對貼文按愛心（重複按則取消愛心，實作 toggle 邏輯）。

## 4. API 設計草案 (Draft API Design)

### 相簿

| Method   | Endpoint                                              | 說明               | 權限     |
|----------|-------------------------------------------------------|--------------------|----------|
| `GET`    | `/hosts/{host_id}/album`                              | 取得店家相簿圖片   | 所有人   |
| `POST`   | `/hosts/{host_id}/album/photos`                       | 上傳圖片至相簿     | 店家本人 |
| `DELETE` | `/hosts/{host_id}/album/photos/{photo_id}`            | 移除相簿圖片       | 店家本人 |

### 貼文

| Method   | Endpoint                                        | 說明                   | 權限                     |
|----------|-------------------------------------------------|------------------------|--------------------------|
| `POST`   | `/hosts/{host_id}/posts`                        | 發布貼文               | 店家本人                 |
| `GET`    | `/hosts/{host_id}/posts`                        | 取得店家貼文列表       | 所有人                   |
| `GET`    | `/posts/{post_id}`                              | 取得貼文詳情           | 所有人                   |
| `PATCH`  | `/posts/{post_id}`                              | 編輯貼文               | 店家本人                 |
| `DELETE` | `/posts/{post_id}`                              | 刪除貼文               | 店家本人                 |
| `GET`    | `/posts/{post_id}/comments`                     | 取得貼文留言列表       | 所有人                   |
| `POST`   | `/posts/{post_id}/comments`                     | 新增留言               | 已登入使用者             |
| `DELETE` | `/posts/{post_id}/comments/{comment_id}`        | 刪除留言               | 留言者本人 / 店家        |
| `POST`   | `/posts/{post_id}/likes`                        | 按愛心 / 取消愛心      | 已登入使用者             |

## 5. 非功能性需求 (Non-Functional Requirements)

- **分頁**：相簿列表、貼文列表、留言列表均需支援分頁（pagination）。
- **圖片上傳**：支援多張圖片同時上傳，單張圖片大小限制建議不超過 10 MB。
- **索引優化**：`Post`、`Comment`、`PostLike` 需對 `host_id`、`post_id`、`user_id` 等外鍵欄位建立索引，以優化查詢效能。
- **唯一性約束**：`PostLike` 需對 `(post_id, user_id)` 建立唯一約束，避免重複愛心。
