# 認證系統需求文件 (Authentication System Requirements)

## 1. 概述與目標

Work Exchange Platform 需要提供多元化的用戶認證與授權解決方案，支持不同的登入方式以提升用戶體驗與平台易用性。本文件定義系統應支持的所有認證方式及其相應的實現要求。

## 2. 目標受眾

- 新用戶/遊客（尋求註冊）
- 已註冊的 Helper
- 已註冊的 Host
- 雙角色用戶（同時為 Helper 和 Host）

## 3. 認證方式需求

### 3.1 電郵/密碼認證（Email/Password Authentication）

**狀態**：✅ 已實現

#### 功能描述
- 支持使用電郵與密碼進行註冊
- 支持使用電郵與密碼進行登入
- 支持密碼重設功能
- 支持電郵驗證（強制性）
- 支持會話管理與登出

#### 技術實現
- 框架：Django `allauth` + `dj-rest-auth`
- 端點：
  - 註冊：`POST /api/auth/registration/`
  - 登入：`POST /api/auth/login/`
  - 登出：`POST /api/auth/logout/`
  - 密碼重設：`POST /api/auth/password/reset/`

#### 安全需求
- 密碼使用 Argon2 加密演算法儲存
- 支持最少 8 字元密碼驗證
- 支持禁用常見密碼列表
- 支持用戶屬性相似性驗證
- 支持純數字密碼檢查

---

### 3.2 Google 信箱登入（Google OAuth2 Authentication）

**狀態**：✅ 已實現

#### 功能描述
- 支持使用 Google 帳號進行一鍵登入/註冊
- 自動將 Google 使用者信息關聯至系統用戶
- 支持多個社交帳號綁定/解綁至同一用戶

#### 技術實現
- 框架：Django `allauth` Google Provider
- 端點：`POST /api/social-auth/google/`
- 請求參數：`access_token`（來自 Google OAuth2）
- 響應：JWT tokens + 用戶資訊

#### 權限範圍
- `profile` - 用戶基本資訊
- `email` - 電郵地址

#### 流程
1. 前端使用 Google SDK 取得 access token
2. 前端發送 access token 至後端
3. 後端驗證並建立/更新用戶
4. 後端返回 JWT tokens

---

### 3.3 Facebook 帳號登入（Facebook OAuth2 Authentication）

**狀態**：✅ 已實現

#### 功能描述
- 支持使用 Facebook 帳號進行一鍵登入/註冊
- 自動將 Facebook 使用者信息關聯至系統用戶
- 支持多個社交帳號綁定/解綁至同一用戶

#### 技術實現
- 框架：Django `allauth` Facebook Provider
- 端點：`POST /api/social-auth/facebook/`
- 請求參數：`access_token`（來自 Facebook OAuth2）
- 響應：JWT tokens + 用戶資訊

#### 權限範圍
- `email` - 使用者電郵
- `public_profile` - 基本公開資訊（姓名、頭像等）

#### 取得用戶信息
- `id`, `email`, `first_name`, `last_name`, `name`
- `picture`, `short_name`, `name_format`

#### 流程
1. 前端使用 Facebook SDK 取得 access token
2. 前端發送 access token 至後端
3. 後端驗證並建立/更新用戶（Facebook App 版本：v20.0）
4. 後端返回 JWT tokens

#### 相關文件
- 實現指南：[FACEBOOK_LOGIN_GUIDE.md](../../FACEBOOK_LOGIN_GUIDE.md)

---

### 3.4 Apple ID 登入（Apple Sign In Authentication）

**狀態**：✅ 已實現

#### 功能描述
- 支持使用 Apple ID 進行一鍵登入/註冊
- 支持隱私中繼電郵服務（Private Email Relay）
- 自動將 Apple 使用者信息關聯至系統用戶
- 支持多個社交帳號綁定/解綁至同一用戶

#### 技術實現
- 框架：Django `allauth` Apple Provider
- 端點：`POST /api/social-auth/apple/`
- 請求參數：`id_token`（來自 Apple OAuth2）
- 響應：JWT tokens + 用戶資訊

#### Django 設定
已在 `config/settings/base.py` 中配置：

```python
INSTALLED_APPS += [
    "allauth.socialaccount.providers.apple",
]

SOCIALACCOUNT_PROVIDERS = {
    "apple": {
        "SCOPE": [
            "email",
            "name",
        ],
        "AUTH_PARAMS": {
            "response_mode": "form_post",
        },
    },
}
```

#### 權限範圍
- `email` - 使用者電郵
- `name` - 使用者名稱

#### 流程
1. 前端使用 Apple Sign In 取得 identity token（id_token）
2. 前端發送 id_token 至後端 `POST /api/social-auth/apple/`
3. 後端驗證 JWT token（使用 Apple 的公鑰）
4. 後端建立/更新用戶與社交帳號關聯
5. 後端返回 JWT tokens

#### 特殊考量
- 隱私中繼電郵：Apple 可能提供隐藏的電郵
- 用戶第一次登入時才能取得姓名資訊
- 需要定期刷新 Apple 簽名密鑰

---

## 4. Token 管理需求

### 4.1 JWT Token 配置

**狀態**：✅ 已實現

#### 規格
```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}
```

#### 特性
- Access Token 有效期：60 分鐘
- Refresh Token 有效期：7 天
- 啟用 Token 輪轉（Rotation）
- 舊 Token 自動進入黑名單
- 更新最後登入時間

---

## 5. 用戶資訊管理

### 5.1 用戶模型

**狀態**：✅ 已實現

#### 核心字段
- `username` - 唯一使用者名稱
- `email` - 唯一電郵地址
- `password` - 加密密碼
- `first_name` - 名字
- `last_name` - 姓氏
- `name` - 完整名稱
- `avatar` - 使用者頭像
- `user_type` - 角色類型（helper/host/both）
- `last_login_ip` - 最後登入 IP 位址

### 5.2 社交帳號關聯

**狀態**：✅ 已實現

#### 功能
- 支持一個用戶綁定多個社交帳號
- 數據庫表：`socialaccount_socialaccount`
- 支持帳號綁定/解綁操作

---

## 6. 非功能性需求

| 需求 | 狀態 | 說明 |
|------|------|------|
| 高可用性 | ✅ | 登入服務需要 99.9% 以上可用性 |
| 安全性 | ✅ | 敏感資訊加密存儲，使用 HTTPS |
| 可擴展性 | ✅ | 允許未來增加更多社交提供商 |
| 效能 | ✅ | API 響應時間 < 2 秒 |
| 審計日誌 | ⚠️ | 需要記錄所有認證事件 |

---

## 7. 實現檢查清單

### 已完成
- [x] Email/Password 註冊與登入
- [x] Google OAuth2 登入
- [x] Facebook OAuth2 登入
- [x] Apple Sign In 登入
  - [x] 安裝 `allauth` Apple provider
  - [x] 配置 `SOCIALACCOUNT_PROVIDERS`
  - [x] 建立 API 端點 `/api/social-auth/apple/`
- [x] JWT Token 管理
- [x] 用戶模型與角色管理
- [x] 社交帳號關聯

### 待完成
- [ ] 審計日誌系統
- [ ] 異常登入檢測
- [ ] 雙因素認證（MFA）- 未來功能

---

## 8. API 端點總結

| 方法 | 端點 | 功能 | 狀態 |
|------|------|------|------|
| POST | `/api/auth/registration/` | Email/密碼註冊 | ✅ |
| POST | `/api/auth/login/` | Email/密碼登入 | ✅ |
| POST | `/api/auth/logout/` | 登出 | ✅ |
| POST | `/api/auth/password/reset/` | 密碼重設 | ✅ |
| POST | `/api/social-auth/google/` | Google 登入 | ✅ |
| POST | `/api/social-auth/facebook/` | Facebook 登入 | ✅ |
| POST | `/api/social-auth/apple/` | Apple 登入 | ✅ |

---

## 9. 參考文件

- [Django Allauth 文檔](https://django-allauth.readthedocs.io/)
- [dj-rest-auth 文檔](https://dj-rest-auth.readthedocs.io/)
- [Facebook 登入指南](../../FACEBOOK_LOGIN_GUIDE.md)
- [Apple Sign In 官方文檔](https://developer.apple.com/sign-in-with-apple/)

---

## 10. 版本歷史

| 版本 | 日期 | 作者 | 變更 |
|------|------|------|------|
| 1.1 | 2026-03-21 | 實現團隊 | 完成 Apple Sign In 實現 |
| 1.0 | 2026-03-21 | 系統檢查 | 初版建立 |

