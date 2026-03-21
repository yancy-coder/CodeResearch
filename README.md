# CoderResearch

## 定性研究智能编码系统

CoderResearch 是一个面向质性研究（Qualitative Research）的多 Agent 编码系统，基于扎根理论（Grounded Theory）方法论，支持从数据导入到理论建构的全流程自动化辅助。

## 🏗️ 系统架构

```
CoderResearch/
├── ImportEngine/          # 数据导入与预处理
├── CodeEngine/            # 三级编码引擎（开放→轴心→选择）
├── TheoryEngine/          # 理论建构与可视化
├── MemoEngine/            # 备忘录撰写与反思
├── ForumEngine/           # 多 Agent 编码协作
├── CodebookDB/            # 代码本数据库与版本控制
└── ReportEngine/          # 研究报告生成
```

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 运行示例
python -m CoderResearch.app
```

## 📚 核心功能

- **智能编码辅助**：AI 辅助开放编码，逐行生成初始代码
- **信度检验**：多编码者一致性计算（Kappa 系数）
- **负向案例追踪**：自动标记不符合理论的案例
- **版本控制**：代码演化历史追踪（Git 式管理）
- **协作讨论**：AI 质疑者角色，主动挑战研究者假设
- **多格式导出**：支持 NVivo、Atlas.ti、DOCX、LaTeX

## 📄 许可证

MIT License
