# CoderResearch v3.0

## 定性研究智能编码系统 - 全栈重构版

CoderResearch 是一个面向质性研究（Qualitative Research）的多 Agent 编码系统，基于扎根理论（Grounded Theory）方法论。

## 🆕 v3.0 全新架构

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 18 + TypeScript + TailwindCSS | 终末地风格 UI |
| **后端** | FastAPI + Python 3.11+ | 高性能异步 API |
| **数据库** | SQLite (aiosqlite) | 轻量级本地存储 |
| **状态管理** | Zustand + React Query | 简洁高效 |

### 项目结构

```
CoderResearch/
├── backend/              # FastAPI 后端
│   ├── main.py          # 应用入口
│   ├── database.py      # SQLite 数据库
│   ├── models.py        # Pydantic 模型
│   └── routers/         # API 路由
│       ├── codes.py
│       ├── categories.py
│       ├── sessions.py
│       └── import_data.py
│
├── frontend/            # React 前端
│   ├── src/
│   │   ├── components/  # UI 组件
│   │   ├── pages/       # 页面
│   │   ├── api/         # API 客户端
│   │   ├── store/       # 状态管理
│   │   └── types/       # TypeScript 类型
│   └── package.json
│
└── start.py             # 一键启动脚本
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+

### 安装与启动

```bash
# 一键启动（自动安装依赖）
python start.py

# 或手动启动
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 前端（新终端）
cd frontend
npm install
npm run dev
```

### 访问服务

- **前端界面**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

## 🎨 终末地 UI 风格

v3.0 采用《明日方舟：终末地》游戏 UI 设计风格：

- **深空黑** (#0a0a0f) 作为主背景
- **终末地橙** (#ff6b35) 作为强调色
- 几何线条分割，科技感十足
- 精细的动画过渡效果

## 📚 核心功能

- 📥 **数据导入**: 支持 TXT/Markdown 文件导入
- 🏷️ **开放编码**: AI 辅助逐行生成初始代码
- 📊 **轴心编码**: 归类、找关系、建维度
- 🎯 **选择性编码**: 识别核心类属，构建理论
- 📈 **可视化**: 编码分布、类属关系图表

## 📄 许可证

MIT License
