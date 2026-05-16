"""
AI 模式实现模块

通过调用 OpenAI API，利用大语言模型对需求描述进行智能分析，
生成更精准、更贴合上下文的拆解结果。
"""

import json
import os
from typing import Optional

from .templates import DecomposedResult


# AI 分析的系统提示词
SYSTEM_PROMPT = """你是一位资深的需求分析师，擅长将模糊的需求描述拆解为结构化的需求文档。

请按照以下四个维度对输入的需求进行拆解，并严格以 JSON 格式输出：

1. **用户故事** (user_stories): 使用 "As a [角色], I want [功能], so that [价值]" 格式
2. **功能点列表** (functional_points): 每个功能点包含 "description" 和 "priority" 两个字段
   - priority 使用 MoSCoW 优先级: Must / Should / Could / Won't
3. **边界条件与异常场景** (boundary_conditions): 列出可能的边界条件和异常情况
4. **验收标准** (acceptance_criteria): 使用 Given-When-Then 格式

输出 JSON 格式示例：
{
  "user_stories": [
    "As a 管理员, I want 查看实时传感器数据, so that 及时发现异常并处理"
  ],
  "functional_points": [
    {"description": "实时数据展示看板", "priority": "Must"},
    {"description": "历史数据趋势图表", "priority": "Should"}
  ],
  "boundary_conditions": [
    "传感器数据丢失时的降级展示",
    "网络延迟超过5秒时的超时处理"
  ],
  "acceptance_criteria": [
    "Given 传感器已连接, When 管理员打开监控看板, Then 3秒内展示最新数据"
  ]
}

要求：
- 用户故事要覆盖所有涉及的角色
- 功能点拆解要细粒度，避免过于笼统
- 边界条件要考虑网络、数据、权限等多维度异常
- 验收标准要具体可测量
- 只输出 JSON，不要输出其他内容"""


def ai_analyze(
    text: str,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
) -> DecomposedResult:
    """
    AI 模式的核心分析入口。

    调用 OpenAI API，利用大语言模型对需求文本进行智能拆解。

    Args:
        text: 原始需求描述文本
        api_key: OpenAI API Key，默认从环境变量 OPENAI_API_KEY 获取
        model: 使用的模型名称，默认 gpt-4o-mini
        base_url: API 基础地址，默认从环境变量 OPENAI_BASE_URL 获取

    Returns:
        DecomposedResult 拆解结果对象

    Raises:
        ValueError: 当输入文本为空时抛出
        RuntimeError: 当 API 调用失败时抛出
    """
    if not text or not text.strip():
        raise ValueError("需求描述文本不能为空")

    text = text.strip()

    # 获取 API Key
    key = api_key or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError(
            "未提供 OpenAI API Key。请通过 --api-key 参数或 OPENAI_API_KEY 环境变量设置。"
        )

    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "未安装 openai 库，请运行: pip install openai"
        )

    # 构建 API 客户端
    client_kwargs = {"api_key": key}
    url = base_url or os.environ.get("OPENAI_BASE_URL")
    if url:
        client_kwargs["base_url"] = url

    client = OpenAI(**client_kwargs)

    # 调用 API
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"请分析以下需求描述：\n\n{text}"},
            ],
            temperature=0.3,  # 较低温度以保证输出的稳定性和结构化
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI API 调用失败: {e}") from e

    # 解析 API 返回结果
    content = response.choices[0].message.content.strip()

    # 尝试提取 JSON 内容（处理可能的 markdown 代码块包裹）
    json_str = _extract_json(content)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"AI 返回的结果无法解析为 JSON。原始内容:\n{content}\n错误: {e}"
        ) from e

    # 将 JSON 转换为 DecomposedResult
    return _parse_ai_response(data)


def _extract_json(text: str) -> str:
    """
    从文本中提取 JSON 内容。

    处理 AI 返回内容可能被 ```json ... ``` 包裹的情况。

    Args:
        text: 可能包含 JSON 的文本

    Returns:
        纯 JSON 字符串
    """
    # 尝试匹配 markdown 代码块中的 JSON
    import re
    match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def _parse_ai_response(data: dict) -> DecomposedResult:
    """
    将 AI 返回的 JSON 数据解析为 DecomposedResult 对象。

    Args:
        data: AI 返回的 JSON 字典

    Returns:
        DecomposedResult 拆解结果对象
    """
    # 解析用户故事
    user_stories = data.get("user_stories", [])
    if not isinstance(user_stories, list):
        user_stories = [str(user_stories)]

    # 解析功能点
    functional_points = []
    for point in data.get("functional_points", []):
        if isinstance(point, dict):
            desc = point.get("description", "")
            priority = point.get("priority", "Should")
            # 校验优先级合法性
            if priority not in ("Must", "Should", "Could", "Won't"):
                priority = "Should"
            functional_points.append((desc, priority))
        elif isinstance(point, str):
            functional_points.append((point, "Should"))

    # 解析边界条件
    boundary_conditions = data.get("boundary_conditions", [])
    if not isinstance(boundary_conditions, list):
        boundary_conditions = [str(boundary_conditions)]

    # 解析验收标准
    acceptance_criteria = data.get("acceptance_criteria", [])
    if not isinstance(acceptance_criteria, list):
        acceptance_criteria = [str(acceptance_criteria)]

    return DecomposedResult(
        user_stories=user_stories,
        functional_points=functional_points,
        boundary_conditions=boundary_conditions,
        acceptance_criteria=acceptance_criteria,
    )
