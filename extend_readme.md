# Gen AI 自動回覆平台後端系統

## 目前開發狀態與未來調整項目

### 1. API 整合

目前系統已實作 API 整合，可以使用 Postman 或 Swagger 來模擬前端使用情境。這些 API 能夠處理用戶查詢並返回生成的回覆。

### 2. 進階資源處理

對於需要處理較為複雜的資源，例如網頁資料或圖片，可以額外建立 `AImodel` 應用來專門管理這些資源，或是儲存相關配置設定。這樣可以保持系統結構的清晰和擴展性。

### 3. 身份驗證

本專案基於 `cookiecutter-django`，預設包含 `allauth` 模組。由於此專案為 demo 版本，未實作如 Google 登入等第三方身份驗證功能，若有需要可根據需求擴展。

### 4. 即時通信 (WebSocket)

如果專案是全端，則可以考慮整合 Django Channels 來支持 WebSocket，即時處理前端與後端的通信。這可以提升用戶體驗，尤其是在高頻率交互的情境下。

## 未來開發建議

### 1. 全文檢索優化

若使用 MongoDB，支援 TTL（存活時間）與正則表達式，這對於大量資料的全文檢索有顯著的效能提升。建議對會話紀錄資料進行全文檢索設計時，利用 MongoDB 提供的這些特性來加速搜尋。

### 2. 資料庫效能優化

考慮到 Django ORM 在處理大規模資料時的效能問題，建議將對話紀錄的元資料儲存於 MongoDB，以支援高效能查詢。同時，將「熱資料」或關聯性較強的資料儲存於 PostgreSQL。這樣能在確保資料存取效能的情況下，兼顧資料庫的穩定性與可擴展性。

## 技術架構與設計

- **資料庫設計**：本系統目前使用 PostgreSQL 作為主要資料庫，對話紀錄的元資料可能會選擇 MongoDB 儲存，以應對未來規模擴展和高效能需求。
- **非同步處理**：為了提高系統效能，生成回覆的過程是透過 Celery 任務處理的。這樣能讓系統在處理用戶查詢時不會因等待 AI 回覆而阻塞其他請求。
- **API 設計**：我們設計了簡單的 RESTful API，確保資料的安全性和效能，並能靈活應對未來擴展需求。

## 開發與擴展建議

- **多模型支援**：目前已考慮系統未來可能需要接入更多的 AI 模型，建議使用模組化設計來支持不同場景下自動選擇 AI 模型或回覆模板。
- **全端支援**：若需要進一步加強前端與後端的實時交互，未來可以使用 WebSocket 來支持即時回覆，並提高用戶互動體驗。

## 結論

此專案在架構設計上考慮了擴展性和可維護性。透過將資料分開存儲並使用非同步處理，我們確保了系統的高效性和穩定性。隨著需求的增長，系統將能夠輕鬆擴展以支持更多的功能和場景。
