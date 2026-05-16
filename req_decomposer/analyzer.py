"""
核心分析逻辑模块

作为模板模式和 AI 模式的统一调度入口，
根据用户选择的模式将需求分析请求路由到对应引擎。
"""

from .templates import DecomposedResult, template_analyze
from .ai_engine import ai_analyze


def analyze(
    text: str,
    mode: str = "template",
    api_key: str | None = None,
    model: str = "gpt-4o-mini",
    base_url: str | None = None,
) -> DecomposedResult:
    """
    需求拆解的核心调度入口。

    根据指定的模式（template / ai）将分析请求路由到对应的引擎，
    返回统一格式的拆解结果。

    Args:
        text: 原始需求描述文本
        mode: 分析模式，"template" 为模板模式，"ai" 为 AI 模式
        api_key: OpenAI API Key（仅 AI 模式需要）
        model: OpenAI 模型名称（仅 AI 模式需要），默认 gpt-4o-mini
        base_url: API 基础地址（仅 AI 模式需要），可用于兼容接口

    Returns:
        DecomposedResult 拆解结果对象

    Raises:
        ValueError: 当模式参数不合法或输入文本为空时抛出
        RuntimeError: 当 AI 模式下 API 调用失败时抛出
    """
    if not text or not text.strip():
        raise ValueError("需求描述文本不能为空")

    if mode == "template":
        return template_analyze(text)
    elif mode == "ai":
        return ai_analyze(text, api_key=api_key, model=model, base_url=base_url)
    else:
        raise ValueError(
            f"不支持的模式: '{mode}'，请选择 'template'（模板模式）或 'ai'（AI 模式）"
        )
