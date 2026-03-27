# CoderResearch v3.0

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/React-18-61DAFB.svg" alt="React 18">
  <img src="https://img.shields.io/badge/TypeScript-5.0-3178C6.svg" alt="TypeScript">
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/TailwindCSS-3.3-06B6D4.svg" alt="TailwindCSS">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
</p>

<p align="center">
  <b>定性研究智能编码系统</b><br>
  <span style="color: #666">基于扎根理论方法论的 AI 辅助质性分析平台</span>
</p>

---

## ✨ 特性

- 🤖 **AI 辅助编码** - 智能生成初始代码，提升编码效率
- 📊 **三级编码工作流** - 开放编码 → 轴心编码 → 选择性编码
- 🎨 **终末地风格 UI** - 深色科技感界面，沉浸式研究体验
- 🔄 **实时协作** - 会话管理，随时保存和恢复研究进度
- 📈 **数据可视化** - 编码分布、类属关系图表
- 📤 **多格式导出** - 支持 NVivo、Atlas.ti、DOCX 等格式

---

## 🖼️ 界面预览

> 终末地风格深色主题，橙色强调色

```
┌─────────────────────────────────────────────────────────────┐
│  [Logo] CoderResearch    [概览] [导入] [代码本] [类属] [设置] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ 📊 代码数量   │ │ 📁 类属数量   │ │ 📝 文本片段   │        │
│  │    42        │ │     8        │ │    156       │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 最近代码                                    [+]      │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 🔸 用户体验优化    [open]    human        [🗑️]       │   │
│  │ 🔸 AI工具依赖     [open]    ai            [🗑️]       │   │
│  │ 🔸 情感支持需求    [open]    human        [🗑️]       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ 技术架构

### 全栈技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **前端** | React | 18.2+ | 组件化 UI |
| | TypeScript | 5.3+ | 类型安全 |
| | TailwindCSS | 3.3+ | 原子化 CSS |
| | Vite | 5.0+ | 构建工具 |
| | Zustand | 4.4+ | 状态管理 |
| | React Query | 5.0+ | 服务端状态 |
| **后端** | FastAPI | 0.104+ | 异步 API |
| | Python | 3.11+ | 编程语言 |
| | Pydantic | 2.5+ | 数据验证 |
| **数据库** | SQLite | 3.40+ | 本地存储 |
| | aiosqlite | 0.19+ | 异步驱动 |

### 项目结构

```
CoderResearch/
├── 📁 backend/                 # FastAPI 后端
│   ├── 📄 main.py              # 应用入口 + 路由注册
│   ├── 📄 database.py          # SQLite 数据库连接
│   ├── 📄 models.py            # Pydantic 数据模型
│   ├── 📄 requirements.txt     # Python 依赖
│   └── 📁 routers/             # API 路由模块
│       ├── 📄 codes.py         # 代码 CRUD
│       ├── 📄 categories.py    # 类属管理
│       ├── 📄 sessions.py      # 会话管理
│       └── 📄 import_data.py   # 文件导入
│
├── 📁 frontend/                # React 前端
│   ├── 📁 src/
│   │   ├── 📁 components/      # UI 组件
│   │   │   ├── 📄 Layout.tsx
│   │   │   ├── 📄 Sidebar.tsx
│   │   │   ├── 📄 Card.tsx
│   │   │   └── 📄 Button.tsx
│   │   ├── 📁 pages/           # 页面组件
│   │   │   ├── 📄 Overview.tsx    # 概览页
│   │   │   ├── 📄 CodesPage.tsx   # 代码本
│   │   │   └── 📄 ImportPage.tsx  # 导入页
│   │   ├── 📁 api/             # API 客户端
│   │   │   └── 📄 client.ts
│   │   ├── 📁 store/           # Zustand 状态
│   │   │   └── 📄 index.ts
│   │   ├── 📁 types/           # TypeScript 类型
│   │   │   └── 📄 index.ts
│   │   ├── 📄 App.tsx          # 根组件
│   │   ├── 📄 main.tsx         # 入口
│   │   └── 📄 index.css        # 全局样式
│   ├── 📄 package.json
│   ├── 📄 tailwind.config.js   # 终末地主题配置
│   └── 📄 vite.config.ts       # Vite 配置
│
├── 📄 start.py                 # 🚀 一键启动脚本
├── 📄 README.md                # 项目文档
└── 📄 LICENSE                  # MIT 许可证
```

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.11 或更高版本
- **Node.js**: 18 或更高版本
- **Git**: 用于克隆仓库

### 一键启动（推荐）

```bash
# 克隆仓库
git clone <repository-url>
cd CoderResearch

# 一键启动（自动安装依赖）
python start.py
```

访问：
- 🌐 **前端界面**: http://localhost:5173
- 📚 **API 文档**: http://localhost:8000/docs
- 🔍 **健康检查**: http://localhost:8000/api/health

### 手动启动

**后端服务：**
```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --port 8000
```

**前端服务：**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 🎨 终末地 UI 设计系统

### 色彩规范

| 名称 | 色值 | 用途 |
|------|------|------|
| **深空黑** | `#0a0a0f` | 主背景 |
| **次级背景** | `#12121a` | 侧边栏、卡片背景 |
| **卡片背景** | `#1a1a25` | 内容卡片 |
| **终末地橙** | `#ff6b35` | 强调色、按钮、徽章 |
| **悬停橙** | `#ff8555` | 悬停状态 |
| **边框** | `#2a2a3a` | 分割线、边框 |
| **主文字** | `#ffffff` | 标题、重要文字 |
| **次级文字** | `#a0a0b0` | 正文、描述 |
| **弱化文字** | `#606070` | 辅助信息 |

### 组件样式

```css
/* 卡片样式 */
.ef-card {
  @apply bg-endfield-bg-card border border-endfield-border rounded-lg;
  @apply hover:border-endfield-accent/50 transition-all duration-200;
}

/* 按钮样式 */
.ef-btn-primary {
  @apply bg-endfield-accent text-white rounded-md;
  @apply hover:bg-endfield-accent-hover transition-colors;
}

/* 输入框样式 */
.ef-input {
  @apply bg-endfield-bg-secondary border border-endfield-border rounded-md;
  @apply focus:border-endfield-accent focus:ring-1 focus:ring-endfield-accent;
}
```

---

## 📡 API 文档

### 代码 (Codes)

| 方法 | 端点 | 描述 |
|------|------|------|
| `GET` | `/api/codes` | 获取所有代码（支持 `?level=open` 过滤） |
| `GET` | `/api/codes/{id}` | 获取单个代码 |
| `POST` | `/api/codes` | 创建新代码 |
| `PUT` | `/api/codes/{id}` | 更新代码 |
| `DELETE` | `/api/codes/{id}` | 删除代码 |

### 类属 (Categories)

| 方法 | 端点 | 描述 |
|------|------|------|
| `GET` | `/api/categories` | 获取所有类属 |
| `GET` | `/api/categories/{id}` | 获取单个类属 |
| `POST` | `/api/categories` | 创建类属 |

### 导入 (Import)

| 方法 | 端点 | 描述 |
|------|------|------|
| `POST` | `/api/import/text` | 上传文本文件（FormData） |
| `GET` | `/api/import/segments` | 获取所有文本片段 |
| `DELETE` | `/api/import/segments` | 清空文本片段 |

### 会话 (Sessions)

| 方法 | 端点 | 描述 |
|------|------|------|
| `GET` | `/api/sessions/{id}` | 获取会话数据 |
| `PUT` | `/api/sessions/{id}` | 更新会话数据 |

---

## 💻 开发指南

### 前端开发

```bash
cd frontend

# 安装新依赖
npm install <package-name>

# 运行测试
npm run test

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 后端开发

```bash
cd backend

# 添加新依赖
echo "package-name>=version" >> requirements.txt
pip install -r requirements.txt

# 运行测试
pytest

# 代码格式化
black .
isort .

# 类型检查
mypy .
```

### 数据库迁移

```bash
# 删除旧数据库（开发环境）
rm coderresearch_v3.db

# 重启服务，自动创建新表
uvicorn main:app --reload
```

---

## 🗺️ 路线图

- [x] FastAPI 后端重构
- [x] React + TypeScript 前端
- [x] 终末地风格 UI
- [x] SQLite 数据库
- [ ] AI 编码辅助集成
- [ ] 编码可视化图表
- [ ] 协作编码功能
- [ ] 多语言支持

---

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证。

---

<p align="center">
  <b>CoderResearch</b> - 让质性研究更智能<br>
  Made with ❤️ for Qualitative Researchers
</p>
