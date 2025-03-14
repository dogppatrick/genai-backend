# GenAIbackend

for interview only

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## 部署相關資訊

設定 env

cookiecutter 的部署是使用這個路徑設定
./.envs/.local/
依據 example.env 需要的參數填寫在這個檔案內
也可以直接複製進入
```
cat example.env > ./.envs/.local/.django 
cat example_postgres.env > ./.envs/.local/.postgres
```

設定完就可以直接使用 doekcer compose 部署
```
docker compose build
docker compose up -d
```

本機開發使用或想直接操作可以參考使用 poetry 做套件管理
原本架構的Dockerfile 是使用 pip install 的方式使用 requirements 安裝
應該不會是本次demo 的重點所以還不直接把原本框架的替換掉
另外重新整理使用套件，並且使用 poetry 也能增加本專案的可維護性

### 測試coverage  使用指令
To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

## 功能相關說明

### genaibackend.user
基本上套用原本 cookiecutter 的設定但是帳號是使用 email  
另外把 使用jwt token 的 login 放在這個 app 底下

---

### Conversation and Message Models
本部分說明了應用程序中用來管理對話、訊息和 AI 回應的模型。

## 1. **Conversation 模型**
`Conversation` 模型代表用戶與 AI 之間的對話。

### 欄位：
- `title`：用來儲存對話標題的字串欄位，可以為空或為 `null`。
- `user`：外鍵，關聯到 `User` 模型，表示與對話相關的用戶。
- `status`：用來表示對話狀態的選擇欄位，選項有：
  - `"Active"`（預設）
  - `"Deleted"`
- `model_version`：用來指定所使用的 AI 模型版本的字串欄位，預設為 `"gpt-4"`。


## 2. **Message 模型**
`Message` 模型代表對話中的訊息，訊息可以是用戶發送的或 AI 回應的。

### 欄位：
- `conversation`：外鍵，關聯到 `Conversation` 模型，表示該訊息屬於哪個對話。
- `sender`：選擇欄位，表示訊息的發送者，可以是 `"user"` 或 `"ai"`。
- `content`：長文本欄位，存儲訊息內容。
- `timestamp`：自動設置為訊息創建時間的日期時間欄位。
- `order`：正整數欄位，表示訊息在對話中的順序。
- `is_edited`：布林欄位，標誌訊息是否已被編輯。
- `is_deleted`：布林欄位，標誌訊息是否已刪除。
- `reply_to`：自引用外鍵，表示該訊息是回覆哪一條訊息。


## 3. **AIResponse 模型**
`AIResponse` 模型代表 AI 生成的回應，這些回應對應於 `Message` 模型中的某條訊息。

### 欄位：
- `message`：一對一外鍵，關聯到 `Message` 模型，表示該回應是針對某條訊息。
- `response_content`：長文本欄位，存儲 AI 回應的內容。
- `status`：選擇欄位，表示回應的狀態。可以是：
  - `"Generating"`（預設）
  - `"Completed"`
  - `"Error"`
- `error_message`：文本欄位，存儲 AI 回應錯誤的訊息。


## API 說明

此 API 用於管理用戶對話和訊息，包括創建對話、管理訊息內容及標記已刪除、編輯訊息等功能。

## 1. **ConversationViewSet**
管理用戶的對話。此視圖集支援對話的增、查、改、刪操作。

### 端點：
- `GET /conversations/`: 取得用戶所有對話，支持搜索和過濾。
- `POST /conversations/`: 創建新的對話。
- `GET /conversations/{id}/`: 獲取指定對話詳細資料。
- `PUT /conversations/{id}/`: 更新對話標題和狀態。

### 特點：
- 只允許已認證的用戶訪問。
- 支援搜尋功能，可根據標題過濾對話。
- 自定義分頁設置，每頁顯示 10 條記錄。

## 2. **MessageViewSet**
管理對話中的訊息，支持標記訊息已刪除和編輯訊息。

### 端點：
- `GET /messages/`: 取得用戶所有訊息。
- `PATCH /messages/{id}/mark_deleted/`: 標記訊息為已刪除。
- `PATCH /messages/{id}/edit_message/`: 編輯用戶發送的訊息。

### 特點：
- 只允許已認證的用戶訪問。
- 用戶只能編輯自己發送且未被刪除的訊息。

## 3. **StartConversationAPIView**
創建一個新的對話並立即開始，AI 回應會在訊息創建後自動生成。

### 端點：
- `POST /start_conversation/`: 創建新的對話並發送用戶訊息。

### 特點：
- 支援指定 AI 模型版本。
- 用戶的訊息會立即發送給 AI 並生成回應。

## 4. **AddMessageAPIView**
在現有對話中添加新的訊息。

### 端點：
- `POST /conversations/{id}/add_message/`: 在指定對話中添加新訊息，並生成 AI 回應。

### 特點：
- 支援 AI 自動回應生成。
- 只允許已認證的用戶訪問。
