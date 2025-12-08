# 114-1 資料庫系統
### 科技116 周庭伊

---
<details>
  <summary>🗂️ HW1: 美式餐廳訂位系統</summary>
  
  <br>
  使用 Python Flask 和 MySQL 建立的單一資料表網頁應用程式。系統模擬一個美式餐廳的後台訂位功能。

  ### 功能
  * **新增 (Create)**: 使用者可透過網頁表單提交新的訂位資料。
  * **讀取 (Read)**: 在首頁以表格形式清楚地展示所有訂位清單。
  * **更新 (Update)**: 提供「編輯」功能，讓使用者能修改單筆訂位的詳細資訊。
  * **刪除 (Delete)**: 提供「刪除」功能，可以移除指定的訂位紀錄。
  
  <img width="477" height="250" alt="螢幕擷取畫面 2025-11-03 002528" src="https://github.com/user-attachments/assets/3d45b37f-2b81-44f9-ac98-42f98464c322" />
  
  * **HW1 影片連結**:
    **[ https://www.youtube.com/watch?v=Mpe8EFFMM-Q ]**
</details>

<details>
  <summary>🗂️ HW2: 學生選課系統</summary>
  
  <br>
  用於演示三資料表的關聯式資料庫設計，並實作了完整的 CRUD 功能以及 `JOIN` 查詢。

  ### 功能
  * **多資料表 CRUD**:
    * `學生管理`: 完整的「新增、讀取、更新、刪除」學生功能。
    * `課程管理`: 完整的「新增、讀取、更新、刪除」課程功能。
    * `選課管理`: 完整的「新增、讀取、更新、刪除」選課紀錄功能，使用下拉選單關聯學生與課程。
  * **JOIN 查詢 (作業重點)**:
    * 建立了一個「選課報表」頁面。
    * 此頁面使用 `INNER JOIN` 語法，串聯 `students`、`courses` 和 `enrollments` 三張資料表。

  ### 操作示意圖
  本系統的資料庫架構包含 `students`、`courses` 以及作為關聯橋梁的 `enrollments`。
  
  <img width="475" height="255" alt="學生清單" src="https://github.com/user-attachments/assets/6c69a911-bce5-43c2-bc70-4e14ad2f152d" />
  <img width="475" height="255" alt="課程管理" src="https://github.com/user-attachments/assets/c7cd25be-4686-468c-b2c5-dd8a1d0e44ac" />
  <img width="475" height="255" alt="選課管理" src="https://github.com/user-attachments/assets/7335e727-ad83-4ed2-a5a2-436a21ee27e3" />
  <img width="475" height="255" alt="選課報表" src="https://github.com/user-attachments/assets/6d2f653f-00ff-4fac-843d-6bf4289bd341" />

  * **HW2 影片連結**:
    **[ https://www.youtube.com/watch?v=JYJ_1Xpg8Bg ]**
</details>

<details open>
  <summary>🗂️ HW3: 學生管理系統 (Flask + MongoDB + Render)</summary>
  
  <br>
  將 HW2 的學生選課系統從 MySQL 遷移至 NoSQL 資料庫 (MongoDB Atlas)，並使用 Render 平台將應用程式部署到公有雲上。

  ### 功能
  * **資料庫遷移**: 
    * 將所有 SQL 邏輯 (CRUD, JOIN) 改寫為 MongoDB 的操作。
    * 處理 `ObjectId` 與網址路由的變更。
    * 使用 Python 迴圈與 `find_one` 模擬 `JOIN` 報表功能。
  * **insert_many (作業重點)**: 
    * 實作 `insert_many` 功能，在網頁上提供一個按鈕，可一次批次新增多筆學生資料到 MongoDB。
  * **雲端部署 (Render)**:
    * 使用 `requirements.txt` 管理依賴。
    * 設定環境變數 (Environment Variables) 來保護 MongoDB 連線密碼。
    * 成功部署，取得公開網址。

  * **HW3 雲端網址 (Public URL)**:
    **[https://database-hw3-o4lv.onrender.com/students]**
  
  * **HW3 影片連結 (Demo on Render)**:
    **[https://www.youtube.com/watch?v=kzt-tx7TUtU]**
</details>


<details open>
  <summary>► 🗂️ HW4: 進階功能 - 批量刪除與程式碼重構 (Bulk Delete & Refactoring)</summary>
  
  <br>
  本作業延續 HW3 的 MongoDB 架構，新增了符合使用者體驗的「批量刪除」功能，並對專案結構進行了優化 (前後端分離)。

  ### 核心功能 (Features)
  * **批量刪除 (Bulk Delete - 作業重點)**: 
    * **前端**: 使用 HTML Form 包覆表格，並在每一行資料前加入 `Checkbox` (複選框)，允許使用者一次勾選多位學生。
    * **後端**: 接收前端傳來的 ID 列表 (`selected_ids`)，將其轉換為 `ObjectId`，並使用 MongoDB 的 **`$in`** 運算子搭配 **`delete_many`** 指令，實現一次刪除多筆資料的高效操作。
  * **程式碼重構 (Refactoring)**:
    * 將原本混雜在 `appmongo.py` 中的 HTML 程式碼全數抽離。
    * 建立 **`templates`** 資料夾，並使用 Flask 的 **`render_template`** 函式來渲染頁面 (`students.html`, `edit.html` 等)。
    * 提升了程式碼的可讀性與維護性。

  * **HW4 影片連結 (YouTube)**:
    **[https://youtu.be/9wxwLkEWGiU]**
</details>

<details>
  <summary>🗂️ Final Proposal: NTNU Gourmet Scout</summary>
  * **影片連結**:
    **[ https://www.youtube.com/watch?v=YFXhNb_2epo ]**
</details>
