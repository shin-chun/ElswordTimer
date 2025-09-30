## 📁 專案結構說明
```plaintext
elsword_timer/
├── main.py                  # 程式入口點
├── timer/                   # 計時器邏輯模組（class Timer, TimerManager）
│   ├── __init__.py
│   ├── core.py              # 核心邏輯（狀態機、倒數）
│   └── manager.py           # 管理多個 Timer
├── gui/                     # GUI 顯示模組（PySide6 視窗）
│   ├── __init__.py
│   └── countdown_window.py  # 倒數視窗設計
├── hotkey/                  # 熱鍵邏輯模組
│   ├── __init__.py
│   ├── recorder.py          # 錄製熱鍵
│   └── controller.py        # 三鍵觸發邏輯
├── settings/                # 設定檔與匯入邏輯
│   ├── __init__.py
│   ├── loader.py            # 讀取 JSON5 / YAML
│   └── default.yaml         # 預設技能設定
├── assets/                  # 靜態資源（QSS、音效、圖片）
│   ├── style.qss
│   ├── ding.wav
│   └── icon.png
├── tests/                   # 測試模組（可用 pytest）
│   └── test_timer.py
├── requirements.txt         # 套件清單
└── README.md                # 專案說明文件
```
### 下載開啟說明
1. 下載ZIP檔》解壓縮》至dist文件夾》右鍵點選ElswordTimer的exe檔並以「以系統管理員身份開啟」》

2. 不再每次開啟時重覆相同動作根據以下操作：
右鍵點選ElswordTimer的exe檔》內容》相容性》勾選「以系統管理員身份開啟」  #此法以後左鍵點開即可

### 使用說明

1. 目前時間重置設F8為快捷，不要以F8當作計時觸發。
   
2. 此程式由可設置單鍵、多鍵觸發，若為多鍵設定如：「a,b,c」~必需依照順序按下才能計時，若輸入「a a b b b c」程式會自動刪去重覆項變「a b c」並觸發計時，但中途不可安插其它鍵~ 已修正，只要時間內按完皆可觸發。
   
3. 按鍵組合」及「第二組按鍵組合」只要有一組成立皆可觸發計時，若不需要第二組按鍵可直接空白。
   
4. 秒數內未完成組合即清除按鍵記憶，即使按鍵相同依舊視同無效。


### 按鍵設定
1. a到z ： 全小寫，直接輸入，記得鍵與鍵之間要逗號「不可全形」。
   
2. f1到f12 ： f要小寫，遊戲中可能會被綁定按鍵而設定失效，請確認是以系統管理員身份開啟，若還是不行請更改按鍵 。

3. 特殊按鍵：
   
         ctrl、right ctrl 
         shift、right shift
         alt、right alt
         left、right、up、down (方向鍵指令）

### 未來更新方向

一、一視窗介面美化或優化

二、修改計時判定方式，讓使用者在可以更靈活的使用按鍵，不會被觸發條件限制到副本實際的使用（已修改計時判定，若未發現其它問題暫不會再修改）

三、音效增設開關、並增加音效更改的自訂義

四、按鍵指令的新增除了依賴使用者自行輸入，目前考慮增訂錄制功能

五、增設重置計時開關的自訂義

六、後續將會拆分程式碼及資料分層結構
