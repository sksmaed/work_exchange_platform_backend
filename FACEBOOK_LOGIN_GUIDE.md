# Facebook 登入後端實現指南

本指南說明如何使用已實現的 Facebook 登入功能。

## 📋 已完成的設定

### 1. Django 設定
- ✅ 已新增 `allauth.socialaccount.providers.facebook` 到 `INSTALLED_APPS`
- ✅ 已配置 `SOCIALACCOUNT_PROVIDERS` 包含 Facebook 設定
- ✅ 已創建社交認證 API 端點

### 2. API 端點
已創建以下端點：

- **Facebook 登入**: `POST /api/social-auth/facebook/`
- **Google 登入**: `POST /api/social-auth/google/`

### 3. 資料庫設定
- ✅ 已執行必要的遷移
- ✅ 已創建測試用戶和 Facebook 應用設定

## 🚀 使用方法

### 1. 設定 Facebook 應用
1. 前往 [Facebook Developers](https://developers.facebook.com/)
2. 創建新的 Facebook 應用
3. 獲取 App ID 和 App Secret
4. 更新環境變數或直接在 Django admin 中更新

### 2. 更新環境變數
在您的 `.env` 檔案中：
```bash
FACEBOOK_APP_ID=你的-facebook-app-id
FACEBOOK_APP_SECRET=你的-facebook-app-secret
```

### 3. Django Admin 設定
1. 訪問 `http://localhost:8000/admin/`
2. 前往 "Social applications"
3. 編輯 Facebook 應用，更新正確的 client_id 和 secret

### 4. API 使用

#### Facebook 登入
```bash
curl -X POST http://localhost:8000/api/social-auth/facebook/ \
  -H "Content-Type: application/json" \
  -d '{"access_token": "facebook_access_token_from_frontend"}'
```

#### 預期回應
成功時：
```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "user": {
    "pk": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

錯誤時：
```json
{
  "error": "Facebook login failed",
  "details": "錯誤詳情"
}
```

## 🔧 前端整合

### JavaScript 範例
```javascript
// 1. 使用 Facebook SDK 獲取 access token
FB.login(function(response) {
  if (response.authResponse) {
    const accessToken = response.authResponse.accessToken;
    
    // 2. 發送到後端進行驗證
    fetch('/api/social-auth/facebook/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        access_token: accessToken
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.access_token) {
        // 登入成功，儲存 JWT token
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        
        // 重定向到主頁面
        window.location.href = '/dashboard/';
      } else {
        console.error('Login failed:', data.error);
      }
    });
  }
}, {scope: 'email,public_profile'});
```

## 📱 測試

### 1. 檢查 API 端點
訪問 `http://localhost:8000/api/docs/` 查看 API 文檔

### 2. 測試登入流程
1. 在前端使用 Facebook SDK 獲取 access token
2. 將 token 發送到 `/api/social-auth/facebook/`
3. 檢查是否收到 JWT tokens

## 🔐 安全注意事項

1. **HTTPS**: 生產環境必須使用 HTTPS
2. **CORS 設定**: 確保正確設定 CORS 允許的來源
3. **Token 安全**: JWT tokens 應安全儲存，避免 XSS 攻擊
4. **Facebook 應用設定**: 確保 Facebook 應用的重定向 URI 正確設定

## 🐛 故障排除

### 常見問題

1. **"Invalid access token"**
   - 檢查 Facebook 應用設定
   - 確認 access token 未過期

2. **"Facebook login failed"**
   - 檢查 Django admin 中的 Social Application 設定
   - 確認 App ID 和 Secret 正確

3. **CORS 錯誤**
   - 檢查 `CORS_ALLOWED_ORIGINS` 設定
   - 確保前端域名在允許清單中

### 除錯步驟
1. 檢查 Django 日誌
2. 驗證 Facebook 應用設定
3. 測試 Facebook Graph API 回應
4. 檢查資料庫中的 SocialAccount 記錄

## 📚 相關文檔

- [Django Allauth 文檔](https://django-allauth.readthedocs.io/)
- [Facebook for Developers](https://developers.facebook.com/docs/)
- [dj-rest-auth 文檔](https://dj-rest-auth.readthedocs.io/)

## 🎯 下一步

1. 配置前端 Facebook SDK
2. 設定正確的 Facebook 應用憑證
3. 測試完整的登入流程
4. 實現登出和 token 刷新功能
