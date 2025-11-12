### 基本設定
* Create R2 bucket 並啟用 Public access (才能用自訂網域與快取使用)
* Create 'Acess' & 'Secret' API Token：R2 Dashboard 右下方的 Account Details → API Token → {manage} (Token 只會顯示一次)
* 自訂網域：R2 Bucket → Settings → Public access → Custom domains
* 設定快取：Dashboard → 點擊欲設定網域 → Caching → Cache Rules → Cache level = Cache Everything (開 Smart Tiered Cache 可減少回源到 R2)
* CORS：前端 'fetch() R2 file' or 'PUT/POST'，須設定 CORS policy

### 注意事項
* 自訂網域只能讀取，寫入必須用 S3 API

### 回應標頭檢查
```bash
curl -svo NUL https://img.example.com/images/cat.jpg 2>&1 | findstr /i "cf-cache-status"
```
> cf-cache-status: DYNAMIC → Not CDN

> cf-cache-status: HIT → CDN ( Run again if 'MISS' )

[Github Link](https://github.com/NickGG1104/Little-projects/tree/main/Cloudflare)

### 測試單元起手式
* 對外保證什麼？
* 有哪幾種結果？
* 有碰外部資源嗎？
* 哪裡最容易出錯？
