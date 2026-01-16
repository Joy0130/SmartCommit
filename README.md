# SmartCommit 🤖

使用 AI 自動生成符合 Conventional Commits 規範的 Git commit 訊息。

## 功能特色

- 🤖 **AI 智能生成**：使用 Google Gemini AI 分析程式碼變更，自動生成專業的 commit 訊息
- ✏️ **手動編輯**：可以編輯 AI 生成的訊息，保留個人風格
- ✅ **格式驗證**：自動檢查 commit 訊息是否符合 Conventional Commits 規範
- 🎯 **繁體中文支援**：生成的訊息使用繁體中文描述

## 安裝

### 方法 1：使用 pipx（推薦）⭐

**適合想要全域使用 `smartcommit` 指令的使用者**

```bash
# 1. 安裝 pipx（如果還沒有）
brew install pipx
pipx ensurepath

# 2. Clone 專案
git clone https://github.com/Joy0130/SmartCommit.git

# 3. 使用 pipx 安裝
pipx install /path/to/SmartCommit

使用 pipx 安裝後，可以用 pipx uninstall smartcommit 輕鬆移除

# 4. 設定 API 金鑰（在 SmartCommit 專案目錄）
cd SmartCommit
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

**安裝完成後，可以在任何目錄直接使用：**

```bash
cd /path/to/any/git/project
git add .
smartcommit  # 直接執行！
```

---

### 方法 2：開發模式（適合貢獻者）

```bash
# 1. Clone 專案
git clone https://github.com/Joy0130/SmartCommit.git
cd SmartCommit

# 2. 使用 uv 安裝依賴
uv sync

# 3. 設定 API 金鑰
echo "GEMINI_API_KEY=your_api_key_here" > .env

# 4. 使用 uv run 執行
uv run smartcommit
```

---

### 方法 3：簡單腳本方式

如果不想安裝，可以直接執行 Python 腳本：

```bash
# Clone 專案
git clone https://github.com/Joy0130/SmartCommit.git
cd SmartCommit

# 設定 API 金鑰
echo "GEMINI_API_KEY=your_api_key_here" > .env

# 在任何 Git 專案中使用
cd /path/to/your/project
git add .
python /path/to/SmartCommit/main.py
```

**提示**：可以在 `~/.zshrc` 或 `~/.bashrc` 加入 alias：

```bash
alias smartcommit='python /path/to/SmartCommit/main.py'
```

---

## 使用方式

```bash
# 1. 在您的 Git 專案中暫存變更
cd /path/to/your/project
git add .

# 2. 執行 smartcommit
smartcommit

# 3. 選擇操作
# - y: 使用 AI 生成的訊息
# - e: 編輯訊息
# - n: 取消提交
```

## Conventional Commits 規範

### 允許的 Commit Types

| Type       | 中文名稱      | 說明                                                                         |
| ---------- | ------------- | ---------------------------------------------------------------------------- |
| `feat`     | Feature       | 新增功能                                                                     |
| `fix`      | Bug Fix       | 修復 bug                                                                     |
| `docs`     | Documentation | 僅修改文件（如 README、API 文件），不影響程式碼                              |
| `style`    | Style         | 修改格式（空格、分號、縮排等），不影響程式邏輯<br/>（注意：不是指 CSS 樣式） |
| `refactor` | Refactoring   | 程式碼重構。既不是新增功能，也不是修補 Bug<br/>（例如：簡化邏輯、變數更名）  |
| `perf`     | Performance   | 專門為了提升效能的程式碼修改                                                 |
| `test`     | Test          | 新增測試案例或修正現有的測試                                                 |
| `build`    | Build         | 影響建置系統或外部依賴的更動<br/>（如 npm, gulp, broccoli, nuget 等）        |
| `ci`       | CI            | 修改 CI 設定檔與腳本<br/>（如 GitHub Actions, Travis, CircleCI）             |
| `chore`    | Chore         | 其他雜項修改，不修改原始碼或測試檔<br/>（例如：更新 .gitignore）             |
| `revert`   | Revert        | 恢復先前的提交                                                               |

### 格式範例

```
<type>: <subject>
```

**正確範例**：

- `feat: 新增使用者登入功能`
- `fix: 修復登入頁面顯示錯誤`
- `docs: 更新 API 文件`
- `refactor: 重構資料處理邏輯`

## 使用範例

### 使用 uv run

```bash
$ cd /path/to/your/project
$ git add .
$ uv run --directory /Users/joy/Documents/SmartCommit smartcommit

🤖 AI 正在分析程式碼變更，請稍候...

------------------------------------
📝 建議訊息: feat: 新增使用者登入功能
------------------------------------

請選擇操作 (y=使用/e=編輯/n=取消): e

請輸入新的 commit 訊息（按 Enter 確認）:
feat: 新增使用者登入功能
> feat: 新增使用者登入與註冊功能

✅ 訊息格式正確！
📝 更新後的訊息: feat: 新增使用者登入與註冊功能

是否提交此訊息? (y/n): y
✅ 提交成功！
```

### 使用 Python 腳本

```bash
$ cd /path/to/your/project
$ git add .
$ python /Users/joy/Documents/SmartCommit/main.py

🤖 AI 正在分析程式碼變更，請稍候...
...
```

## 格式驗證

當您選擇編輯訊息時，程式會自動驗證格式：

❌ **常見錯誤**：

```bash
# 錯誤的 type
> feature: 新增功能
type 'feature' 不符合規範
 允許的 type: feat, fix, docs, style, refactor, test, chore, perf, ci, revert, build

# 缺少冒號
> feat 新增功能
格式錯誤：缺少冒號(:)，正確格式為 <type>: <subject>

# subject 為空
> feat:
subject 不可為空
```

## 故障排除

### API 金鑰錯誤

```
Error: 找不到 GEMINI_API_KEY，請檢查.env檔案
```

**解決方案**：確認 `.env` 檔案存在且包含有效的 API 金鑰

### 沒有暫存變更

```
message: 沒有偵測到暫存的變更(Staged Changes)，如有變更請先執行 git add
```

**解決方案**：先使用 `git add` 暫存您要提交的變更

### AI 生成失敗

```
Error: 無法生成 Commit 訊息 (可能是 API 錯誤或 Token 限制)
```

**解決方案**：

- 檢查網路連線
- 確認 API 金鑰是否有效
- 如果變更內容過大，可能需要手動編輯

## 開發指南

### 專案結構

```
SmartCommit/
├── smartcommit/           # 主要套件
│   ├── __init__.py       # 套件初始化
│   ├── core.py           # 核心功能（Git、AI、驗證）
│   └── cli.py            # CLI 入口點
├── pyproject.toml        # 專案配置
├── .env                  # API 金鑰（不要提交到 Git）
└── README.md             # 專案說明
```

### 開發模式安裝

```bash
# Clone 專案
git clone https://github.com/Joy0130/SmartCommit.git
cd SmartCommit

# 使用 uv 開發模式安裝
uv sync

# 或使用 pip
pip install -e .
```

### 執行測試

```bash
# 在測試專案中進行測試
cd /tmp
mkdir test-repo
cd test-repo
git init
echo "# Test" > README.md
git add README.md
smartcommit
```

### 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 專案
2. 創建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的變更 (`git commit -m 'feat: 新增某個很棒的功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request
