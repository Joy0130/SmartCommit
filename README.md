# SmartCommit 🤖

使用 AI 自動生成符合 Conventional Commits 規範的 Git commit 訊息。

## 📚 branch 分支功能

- main：請參閱此檔案說明
- ai：請切換到 **ai** 分支，參考 ai 分支的 README.md

## ✨ 功能特色

- 🤖 **AI 智能生成**：使用 Google Gemini AI 分析程式碼變更，自動生成專業的 commit 訊息
- ✏️ **手動編輯**：可以編輯 AI 生成的訊息，保留個人風格
- ✅ **格式驗證**：自動檢查 commit 訊息是否符合 Conventional Commits 規範
- 🎯 **繁體中文支援**：生成的訊息使用繁體中文描述
- 🚀 **全域命令**：安裝後可在任何 Git 專案中直接使用

## 📋 安裝需求

- Python 3.10+
- [pipx](https://github.com/pypa/pipx)（推薦）
- Google Gemini API 金鑰
- Git

## 🚀 快速開始

### 1. 安裝 pipx

```bash
# macOS
brew install pipx
pipx ensurepath

# Linux/WSL
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

重新啟動終端或執行 `source ~/.zshrc` (或 `~/.bashrc`)

### 2. 安裝 SmartCommit

```bash
# Clone 專案
git clone https://github.com/Joy0130/SmartCommit.git

# 使用 pipx 安裝（全域可用）
pipx install SmartCommit/
```

### 3. 設定 API 金鑰

在 SmartCommit 專案目錄建立 `.env` 檔案：

```bash
cd SmartCommit
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

> **如何取得 API 金鑰？**  
> 前往 [Google AI Studio](https://aistudio.google.com/apikey) 免費取得您的 Gemini API 金鑰

### 4. 開始使用

```bash
# 在任何 Git 專案中
cd /path/to/your/project

# 暫存變更
git add .

# 執行 smartcommit
smartcommit
```

就這麼簡單！✨

## 📖 使用範例

```bash
$ cd /path/to/your/project
$ git add .
$ smartcommit

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
✅ 提交成功！可以使用 git push 上傳
```

## 🎯 操作選項

執行 `smartcommit` 後，您有三個選項：

- **`y`** - 直接使用 AI 生成的訊息提交
- **`e`** - 編輯訊息後再提交
- **`n`** - 取消提交

## 📝 Conventional Commits 規範

SmartCommit 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範。

### 允許的 Commit Types

| Type       | 說明                       | 範例                               |
| ---------- | -------------------------- | ---------------------------------- |
| `feat`     | 新增功能                   | `feat: 新增使用者登入功能`         |
| `fix`      | 修復 bug                   | `fix: 修復登入頁面顯示錯誤`        |
| `docs`     | 文件修改                   | `docs: 更新 API 文件`              |
| `style`    | 格式修改（不影響程式邏輯） | `style: 調整程式碼縮排`            |
| `refactor` | 程式碼重構                 | `refactor: 重構資料處理邏輯`       |
| `perf`     | 效能優化                   | `perf: 優化資料庫查詢效能`         |
| `test`     | 測試相關                   | `test: 新增登入功能測試`           |
| `build`    | 建置系統修改               | `build: 更新依賴套件版本`          |
| `ci`       | CI 設定修改                | `ci: 新增 GitHub Actions 工作流程` |
| `chore`    | 雜項修改                   | `chore: 更新 .gitignore`           |
| `revert`   | 恢復先前提交               | `revert: 恢復登入功能變更`         |

### 格式範例

```
<type>: <subject>
```

**正確範例**：

- ✅ `feat: 新增使用者登入功能`
- ✅ `fix: 修復登入頁面顯示錯誤`
- ✅ `docs: 更新 README 安裝說明`

**錯誤範例**：

- ❌ `feature: 新增功能` （type 錯誤，應為 `feat`）
- ❌ `feat 新增功能` （缺少冒號）
- ❌ `feat:` （subject 為空）

## �️ 進階使用

### 查看版本

```bash
smartcommit --version
```

### 查看幫助

```bash
smartcommit --help
```

### 更新 SmartCommit

```bash
cd /path/to/SmartCommit
git pull
pipx install . --force
```

### 移除 SmartCommit

```bash
pipx uninstall smartcommit
```

## 🔧 故障排除

### ❌ 找不到 GEMINI_API_KEY

```
❌ Error: 找不到 GEMINI_API_KEY
請在當前目錄建立 .env 檔案，內容：GEMINI_API_KEY=你的金鑰
```

**解決方案**：

1. 確認 SmartCommit 專案目錄中有 `.env` 檔案
2. 檢查 `.env` 內容格式正確：`GEMINI_API_KEY=your_key_here`
3. API 金鑰沒有多餘的引號或空格

### ❌ 沒有偵測到暫存的變更

```
⚠️ 沒有偵測到暫存的變更(Staged Changes)，如有變更請先執行 git add
```

**解決方案**：先使用 `git add` 暫存您要提交的變更

```bash
git add .                    # 暫存所有變更
git add file1.py file2.py   # 暫存特定檔案
```

### ❌ AI 生成失敗

```
❌ AI 生成失敗: ...
```

**可能原因**：

- 網路連線問題
- API 金鑰無效或過期
- API 配額已用完
- 變更內容過大

**解決方案**：

1. 檢查網路連線
2. 確認 API 金鑰有效
3. 查看 [Google AI Studio](https://aistudio.google.com/) 配額使用狀況

## 👨‍💻 開發者指南

### 專案結構

```
SmartCommit/
├── smartcommit/           # 主要套件
│   ├── __init__.py       # 套件初始化
│   ├── core.py           # 核心功能（Git、AI、驗證）
│   └── cli.py            # CLI 入口點
├── install.sh            # 自動安裝腳本
├── pyproject.toml        # 專案配置
├── .env                  # API 金鑰（不提交到 Git）
└── README.md             # 專案說明
```

### 開發模式安裝

如果您想要貢獻程式碼或開發新功能：

```bash
# Clone 專案
git clone https://github.com/Joy0130/SmartCommit.git
cd SmartCommit

# 使用 uv 安裝依賴（開發模式）
uv sync

# 執行（開發模式）
uv run smartcommit

# 或使用 pipx 可編輯安裝
pipx install -e .
```

### 執行測試

```bash
# 建立測試專案
cd /tmp
mkdir test-repo
cd test-repo
git init

# 建立測試檔案
echo "# Test" > README.md
git add README.md

# 測試 smartcommit
smartcommit
```

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 專案
2. 創建您的特性分支：`git checkout -b feature/AmazingFeature`
3. 提交您的變更：`git commit -m 'feat: 新增某個很棒的功能'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 開啟 Pull Request

## 📄 授權

MIT License

## 🙏 致謝

- [Google Gemini](https://ai.google.dev/) - 提供強大的 AI 能力
- [Conventional Commits](https://www.conventionalcommits.org/) - 提供 commit 訊息規範

---

**享受使用 SmartCommit 的樂趣！** 🚀

有任何問題或建議，歡迎在 [GitHub Issues](https://github.com/Joy0130/SmartCommit/issues) 提出。
