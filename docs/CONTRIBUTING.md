# 🤝 贡献指南

感谢你对 **req-decomposer** 项目的关注！我们欢迎任何形式的贡献。

## 📜 行为准则

请保持友善和尊重。我们致力于为所有人提供开放、包容的社区环境。

## 🛠️ 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/edward/req-decomposer/issues) 中搜索是否已有相关 Issue
2. 如果没有，创建新 Issue，包含以下信息：
   - **Bug 描述**：发生了什么问题
   - **复现步骤**：如何复现该 Bug
   - **预期行为**：你期望的正常行为
   - **实际行为**：实际发生的行为
   - **环境信息**：Python 版本、操作系统等

### 提出新功能

1. 在 [Issues](https://github.com/edward/req-decomposer/issues) 中创建 Feature Request
2. 描述功能需求、使用场景和预期效果
3. 等待维护者反馈后再开始开发

### 提交代码

1. **Fork 本仓库**
2. **创建功能分支**：
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **编写代码**：
   - 遵循现有代码风格
   - 添加必要的中文注释和 docstring
   - 确保所有现有测试通过
4. **提交 Commit**：
   ```bash
   git commit -m "feat: 添加 XXX 功能"
   ```
   Commit Message 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：
   - `feat:` 新功能
   - `fix:` Bug 修复
   - `docs:` 文档更新
   - `refactor:` 代码重构
   - `test:` 测试相关
   - `chore:` 构建/工具变动
5. **推送到 Fork 仓库**：
   ```bash
   git push origin feature/your-feature-name
   ```
6. **创建 Pull Request**：
   - 描述 PR 的目的和改动内容
   - 关联相关 Issue（如有）

## 🏗️ 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/edward/req-decomposer.git
cd req-decomposer

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -e .

# 验证安装
req-decomposer --version
```

## 📁 项目结构

```
req-decomposer/
├── req_decomposer/          # 核心代码
│   ├── cli.py               # 命令行入口
│   ├── analyzer.py           # 核心分析逻辑
│   ├── templates.py          # 模板模式实现
│   ├── ai_engine.py          # AI 模式实现
│   └── formatter.py          # 输出格式化
├── examples/                # 示例文件
├── docs/                    # 文档
└── tests/                   # 测试（待添加）
```

## 💡 贡献方向

以下是一些欢迎贡献的方向：

- 🧪 添加单元测试
- 🌐 支持更多语言的需求描述（如英文）
- 📊 支持更多输出格式（如 JSON、HTML）
- 🎨 优化模板模式的关键词匹配策略
- 🔌 支持更多 LLM 后端（如 Claude、本地模型）
- 📖 完善文档和使用教程

## ❓ 有问题？

随时在 [Issues](https://github.com/edward/req-decomposer/issues) 中提问，或通过邮件联系维护者。

感谢你的贡献！🎉
