# 在 Google Antigravity 与 Gemini AI 中使用 REA

[English](antigravity-guide.md) · **简体中文** · [返回列表](../README.zh-CN.md)

本指南介绍如何在 **Google Antigravity** 中，结合 **Gemini AI**（例如 Gemini 3.8 Flash 和 Gemini Pro）使用 **Reverse Engineer Anything (REA)** 以及 **AI 重建引擎**。

---

## 1. 为什么选择 Antigravity 与 Gemini 进行逆向工程？

Gemini 模型具备超长上下文窗口、强大的底层代码推理和多轮架构综合能力。Antigravity 将这些优势与以下特性相结合：
- **渐进式 Skill 加载**：像 `reverse-engineer-anything` 和 `ai-rebuild-engine` 这样的技能仅在需要时按需注入上下文。
- **专用 Subagent（子代理）**：无缝委派给 `reverse-engineer-expert` 专家代理，处理深度反编译与长时间逆向任务。
- **交互式工作流与快捷命令**：通过 `/plan`、`/boost` 以及后台任务高效迭代。
- **零依赖本地辅助工具**：内置 `scripts/rea_helper.py`，无需复杂依赖即可在 Windows、Linux 和 macOS 上即开即用。

---

## 2. 仓库内置的 Antigravity 定制套件

本项目提供了即插即用的 Antigravity 工作区与全局插件配置：

```
.agents/
├── plugin.json                                # Antigravity 插件清单
├── mcp_config.json                            # REA MCP 服务配置
├── agents/
│   └── reverse-engineer-expert.md             # 逆向专家 Subagent 定义
├── rules/
│   ├── AGENTS.md                              # 通用 Agent 逆向规则
│   └── GEMINI.md                              # Gemini 强制证据优先准则
└── skills/
    ├── reverse-engineer-anything/             # REA 逆向分析主 Skill
    │   ├── SKILL.md
    │   └── references/
    │       ├── target-routing.md
    │       ├── evidence-guide.md
    │       └── tools-and-fallbacks.md
    └── ai-rebuild-engine/                     # 净室差分重建 Skill
        ├── SKILL.md
        └── references/
            ├── differential-testing.md
            └── clean-room-protocol.md
```

---

## 3. 快速安装与配置

### 方式 A：Windows PowerShell 自动安装
运行内置脚本：
```powershell
.\scripts\setup-antigravity.ps1
```
该脚本将检查 Python 与 Node.js 环境，验证 `scripts/rea_helper.py`，并将插件全局注册至 `~/.gemini/config/plugins/reverse-engineer-anything`。

### 方式 B：Linux / macOS 自动安装
```bash
bash scripts/setup-antigravity.sh
```

---

## 4. 端到端典型实战流程

### 实战 1：Windows PE 原生二进制分析
1. **静态分流**：
   在 Antigravity 中提问：
   > "分析 `sample.exe`，计算其熵值和各节表，判断是否存在加壳。"
   Antigravity 会自动执行：
   ```powershell
   python scripts/rea_helper.py identify sample.exe
   python scripts/rea_helper.py pe-info sample.exe
   ```
2. **提取关键逻辑与字符串**：
   ```powershell
   python scripts/rea_helper.py strings sample.exe --min-len 6 --filter url,api
   ```
3. **证据引用**：
   Gemini 在分析报告中会清晰标明偏移地址（如 `[EVD-01]`, `0x1400019C0`）并附带真实的汇编反编译片段。

---

### 实战 2：Electron 桌面应用拆解
1. **解包 ASAR 归档**：
   > "解包 `resources/app.asar` 并梳理 IPC 通信路由。"
   Antigravity 执行：
   ```powershell
   python scripts/rea_helper.py asar-unpack resources/app.asar unpacked_app/
   ```
2. **追踪 IPC 桥接**：
   Gemini 解析 `unpacked_app/package.json`、`preload.js` 与 `main.js`，梳理所有的 `ipcRenderer.send` 与 `ipcMain.handle` 事件流，并输出 Mermaid 序列图。

---

### 实战 3：净室差分对照式重写
1. **捕获测试向量**：
   Antigravity 记录原二进制程序在各种输入下的输入输出与返回码，生成 `tests/vectors.json`。
2. **现代语言重写**：
   Gemini 遵循净室设计规范，使用 Rust、Go 或 TypeScript 编写全新实现。
3. **差分回归测试**：
   ```powershell
   python scripts/rea_helper.py diff-test --original original.exe --rebuild target/release/rebuild.exe --vectors tests/vectors.json
   ```
   确保新代码与原二进制实现 100% 行为一致后完成交付。

