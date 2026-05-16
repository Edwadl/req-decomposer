"""
命令行入口模块

提供 req-decomposer 的 CLI 交互界面，
支持从命令行参数或文件读取需求文本，选择分析模式，输出到终端或 Markdown 文件。
"""

import sys

import click

from .analyzer import analyze
from .formatter import format_terminal, format_markdown, save_markdown
from . import __version__


@click.command()
@click.version_option(version=__version__, prog_name="req-decomposer")
@click.option(
    "--text", "-t",
    type=str,
    default=None,
    help="直接输入需求描述文本",
)
@click.option(
    "--file", "-f",
    type=click.Path(exists=True),
    default=None,
    help="从文件读取需求描述文本",
)
@click.option(
    "--mode", "-m",
    type=click.Choice(["template", "ai"]),
    default="template",
    help="分析模式：template（模板模式，默认）或 ai（AI 模式）",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="输出 Markdown 文件路径（不指定则仅终端输出）",
)
@click.option(
    "--api-key",
    type=str,
    default=None,
    help="OpenAI API Key（AI 模式下使用，也可通过 OPENAI_API_KEY 环境变量设置）",
)
@click.option(
    "--model",
    type=str,
    default="gpt-4o-mini",
    help="OpenAI 模型名称（AI 模式下使用，默认 gpt-4o-mini）",
)
@click.option(
    "--base-url",
    type=str,
    default=None,
    help="API 基础地址（可用于兼容 OpenAI 接口的服务）",
)
def main(
    text: str | None,
    file: str | None,
    mode: str,
    output: str | None,
    api_key: str | None,
    model: str,
    base_url: str | None,
) -> None:
    """
    📋 req-decomposer - 需求文档拆解框架

    将模糊的需求描述自动拆解为结构化输出，包括：
    用户故事、功能点列表、边界条件和验收标准。

    示例：

    \b
      # 模板模式 - 直接输入文本
      req-decomposer -t "实现用户登录功能"
    \b
      # 模板模式 - 从文件读取
      req-decomposer -f requirement.txt
    \b
      # AI 模式
      req-decomposer -t "实现用户登录功能" --mode ai
    \b
      # 导出为 Markdown
      req-decomposer -f requirement.txt -o output.md
    """
    # ===== 参数校验 =====
    if not text and not file:
        click.echo("❌ 错误：请通过 --text 或 --file 提供需求描述", err=True)
        sys.exit(1)

    # 读取需求文本
    requirement_text = ""
    if text:
        requirement_text = text
    if file:
        try:
            with open(file, "r", encoding="utf-8") as f:
                requirement_text = f.read()
        except IOError as e:
            click.echo(f"❌ 文件读取失败: {e}", err=True)
            sys.exit(1)

    if not requirement_text.strip():
        click.echo("❌ 错误：需求描述文本为空", err=True)
        sys.exit(1)

    # ===== 执行分析 =====
    click.echo(f"🔍 正在分析需求（模式: {mode}）...\n")

    try:
        result = analyze(
            text=requirement_text,
            mode=mode,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    except ValueError as e:
        click.echo(f"❌ 参数错误: {e}", err=True)
        sys.exit(1)
    except RuntimeError as e:
        click.echo(f"❌ 分析失败: {e}", err=True)
        sys.exit(1)

    # ===== 输出结果 =====
    # 终端输出
    terminal_output = format_terminal(result)
    click.echo(terminal_output)

    # Markdown 文件输出
    if output:
        try:
            md_content = format_markdown(result, source_text=requirement_text)
            save_markdown(md_content, output)
            click.echo(f"📄 Markdown 报告已保存至: {output}")
        except OSError as e:
            click.echo(f"❌ 文件保存失败: {e}", err=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
