"""
输出格式化模块

将拆解结果格式化为终端友好输出和 Markdown 文件输出。
"""

from datetime import datetime
from .templates import DecomposedResult


# MoSCoW 优先级对应的 emoji 标识
PRIORITY_EMOJI = {
    "Must": "🔴",
    "Should": "🟡",
    "Could": "🟢",
    "Won't": "⚪",
}

# 各模块标题 emoji
SECTION_EMOJI = {
    "user_stories": "📖",
    "functional_points": "🎯",
    "boundary_conditions": "⚠️",
    "acceptance_criteria": "✅",
}


def format_terminal(result: DecomposedResult) -> str:
    """
    将拆解结果格式化为终端友好输出。

    使用分隔线、缩进和 emoji 让输出在终端中清晰易读。

    Args:
        result: 拆解结果对象

    Returns:
        格式化后的终端输出字符串
    """
    lines = []
    separator = "─" * 60

    # 标题
    lines.append("")
    lines.append(f"📋 需求拆解结果")
    lines.append(separator)

    # 用户故事
    lines.append("")
    lines.append(f"{SECTION_EMOJI['user_stories']} 用户故事 (User Stories)")
    lines.append(separator)
    for i, story in enumerate(result.user_stories, 1):
        lines.append(f"  {i}. {story}")

    # 功能点列表
    lines.append("")
    lines.append(f"{SECTION_EMOJI['functional_points']} 功能点列表 (Functional Points)")
    lines.append(separator)
    for i, (desc, priority) in enumerate(result.functional_points, 1):
        emoji = PRIORITY_EMOJI.get(priority, "🟡")
        lines.append(f"  {i}. [{emoji} {priority}] {desc}")

    # 边界条件与异常场景
    lines.append("")
    lines.append(f"{SECTION_EMOJI['boundary_conditions']} 边界条件 & 异常场景 (Edge Cases)")
    lines.append(separator)
    for i, condition in enumerate(result.boundary_conditions, 1):
        lines.append(f"  {i}. {condition}")

    # 验收标准
    lines.append("")
    lines.append(f"{SECTION_EMOJI['acceptance_criteria']} 验收标准 (Acceptance Criteria)")
    lines.append(separator)
    for i, criterion in enumerate(result.acceptance_criteria, 1):
        lines.append(f"  {i}. {criterion}")

    lines.append("")
    lines.append(separator)
    lines.append("")

    return "\n".join(lines)


def format_markdown(result: DecomposedResult, source_text: str = "") -> str:
    """
    将拆解结果格式化为 Markdown 文档。

    生成结构清晰、可直接用于项目文档的 Markdown 内容。

    Args:
        result: 拆解结果对象
        source_text: 原始需求描述文本（可选，用于在文档中记录来源）

    Returns:
        格式化后的 Markdown 字符串
    """
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 文档标题
    lines.append("# 📋 需求拆解报告")
    lines.append("")
    lines.append(f"> 生成时间：{now}")
    lines.append("> 生成工具：req-decomposer v1.0.0")
    lines.append("")

    # 原始需求（如果提供了源文本）
    if source_text:
        lines.append("## 📝 原始需求")
        lines.append("")
        lines.append("> " + source_text.replace("\n", "\n> "))
        lines.append("")

    # 用户故事
    lines.append("## 📖 用户故事 (User Stories)")
    lines.append("")
    for i, story in enumerate(result.user_stories, 1):
        lines.append(f"{i}. {story}")
    lines.append("")

    # 功能点列表
    lines.append("## 🎯 功能点列表 (Functional Points)")
    lines.append("")
    lines.append("| # | 功能描述 | 优先级 |")
    lines.append("|---|---------|--------|")
    for i, (desc, priority) in enumerate(result.functional_points, 1):
        emoji = PRIORITY_EMOJI.get(priority, "🟡")
        lines.append(f"| {i} | {desc} | {emoji} {priority} |")
    lines.append("")

    # 优先级说明
    lines.append("<details>")
    lines.append("<summary>📊 MoSCoW 优先级说明</summary>")
    lines.append("")
    lines.append("| 标识 | 含义 | 说明 |")
    lines.append("|------|------|------|")
    lines.append("| 🔴 Must | 必须有 | 核心功能，缺少则产品不可用 |")
    lines.append("| 🟡 Should | 应该有 | 重要功能，显著提升产品价值 |")
    lines.append("| 🟢 Could | 可以有 | 增强功能，锦上添花 |")
    lines.append("| ⚪ Won't | 暂不需要 | 当前版本排除，未来可能考虑 |")
    lines.append("")
    lines.append("</details>")
    lines.append("")

    # 边界条件与异常场景
    lines.append("## ⚠️ 边界条件 & 异常场景 (Edge Cases)")
    lines.append("")
    for i, condition in enumerate(result.boundary_conditions, 1):
        lines.append(f"{i}. {condition}")
    lines.append("")

    # 验收标准
    lines.append("## ✅ 验收标准 (Acceptance Criteria)")
    lines.append("")
    for i, criterion in enumerate(result.acceptance_criteria, 1):
        lines.append(f"{i}. {criterion}")
    lines.append("")

    # 页脚
    lines.append("---")
    lines.append("")
    lines.append("*本文档由 [req-decomposer](https://github.com/edward/req-decomposer) 自动生成*")

    return "\n".join(lines)


def save_markdown(content: str, filepath: str) -> None:
    """
    将 Markdown 内容保存到文件。

    Args:
        content: Markdown 格式的内容字符串
        filepath: 目标文件路径

    Raises:
        OSError: 文件写入失败时抛出
    """
    # 确保目录存在
    import os
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
