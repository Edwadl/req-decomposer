"""
模板模式实现模块

基于关键词匹配和预定义模板，在不依赖外部 API 的情况下
将需求描述拆解为结构化输出。
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DecomposedResult:
    """拆解结果数据类，统一存储所有拆解维度"""
    # 用户故事列表
    user_stories: list[str] = field(default_factory=list)
    # 功能点列表，每个元素为 (功能描述, 优先级)
    functional_points: list[tuple[str, str]] = field(default_factory=list)
    # 边界条件与异常场景
    boundary_conditions: list[str] = field(default_factory=list)
    # 验收标准列表
    acceptance_criteria: list[str] = field(default_factory=list)


# ===== 角色识别相关 =====

# 预定义角色关键词映射：关键词 → 对应角色
ROLE_KEYWORDS: dict[str, list[str]] = {
    "管理员": ["管理员", "管理端", "后台管理", "运维", "admin"],
    "普通用户": ["普通用户", "用户", "操作员", "终端用户"],
    "系统": ["系统", "平台", "自动", "定时", "服务端"],
    "访客": ["访客", "游客", "匿名用户", "未登录用户"],
    "开发者": ["开发者", "第三方", "API 调用方"],
}

# 需求意图关键词映射
INTENT_KEYWORDS: dict[str, list[str]] = {
    "查看": ["查看", "浏览", "展示", "显示", "查询", "搜索", "获取", "列表", "详情"],
    "管理": ["管理", "添加", "删除", "修改", "编辑", "更新", "创建", "新建", "增删改查"],
    "监控": ["监控", "监测", "告警", "报警", "预警", "通知", "提醒", "实时"],
    "配置": ["配置", "设置", "参数", "规则", "阈值", "策略", "偏好"],
    "导出": ["导出", "下载", "报表", "报告", "统计", "分析", "汇总"],
    "认证": ["登录", "注册", "认证", "授权", "权限", "鉴权", "身份"],
    "通信": ["推送", "发送", "接收", "消息", "通信", "联动"],
}

# MoSCoW 优先级推断关键词
PRIORITY_KEYWORDS: dict[str, list[str]] = {
    "Must": ["必须", "核心", "关键", "基础", "必要", "首要", "基本"],
    "Should": ["应该", "重要", "推荐", "一般", "常规", "标准", "期望"],
    "Could": ["可以", "可选", "增强", "附加", "额外", "提升体验"],
    "Won't": ["不需要", "排除", "暂不", "未来", "后续", "不在范围", "远期"],
}


def identify_roles(text: str) -> list[str]:
    """
    从需求文本中识别涉及的角色。

    按照角色关键词在文本中出现的频率进行排序，
    出现次数越多的角色排越前面。

    Args:
        text: 需求描述文本

    Returns:
        识别到的角色列表（按出现频率降序）
    """
    role_scores: dict[str, int] = {}
    for role, keywords in ROLE_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # 统计每个关键词在文本中出现的次数
            score += text.count(keyword)
        if score > 0:
            role_scores[role] = score

    # 按得分降序排列
    sorted_roles = sorted(role_scores.keys(), key=lambda r: role_scores[r], reverse=True)

    # 如果没有识别到任何角色，默认为"普通用户"
    if not sorted_roles:
        sorted_roles = ["普通用户"]

    return sorted_roles


def identify_intents(text: str) -> list[str]:
    """
    从需求文本中识别需求意图类型。

    按照意图关键词在文本中的命中数量排序，
    命中越多的意图排在越前面。

    Args:
        text: 需求描述文本

    Returns:
        识别到的意图类型列表（按命中频率降序）
    """
    intent_scores: dict[str, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            score += text.count(keyword)
        if score > 0:
            intent_scores[intent] = score

    sorted_intents = sorted(intent_scores.keys(), key=lambda i: intent_scores[i], reverse=True)

    if not sorted_intents:
        sorted_intents = ["查看"]

    return sorted_intents


def infer_priority(sentence: str) -> str:
    """
    根据句子中的关键词推断 MoSCoW 优先级。

    按优先级从高到低匹配：Must → Won't。
    一旦匹配到某个优先级的关键词，立即返回。

    Args:
        sentence: 单个需求描述句子

    Returns:
        MoSCoW 优先级标签 (Must/Should/Could/Won't)
    """
    # 按优先级从高到低检测
    for priority in ["Must", "Won't", "Should", "Could"]:
        for keyword in PRIORITY_KEYWORDS[priority]:
            if keyword in sentence:
                return priority
    return "Should"


def extract_requirement_sentences(text: str) -> list[str]:
    """
    从需求文本中提取核心需求句子。

    过滤掉标题、背景描述等非功能性句子，
    只保留描述具体功能需求的句子。

    识别规则：
    - 包含编号开头的行（如"1."、"2、"等）
    - 包含角色关键词的句子
    - 包含意图关键词的句子
    - 排除纯背景/标题类句子

    Args:
        text: 原始需求文本

    Returns:
        核心需求句子列表
    """
    # 按常见分隔符拆分
    lines = re.split(r'\n', text)
    sentences = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 按句号再拆分
        parts = re.split(r'[。;]', line)
        for part in parts:
            part = part.strip()
            if len(part) < 6:
                continue

            # 判断是否为核心需求句子
            if _is_requirement_sentence(part):
                sentences.append(part)

    return sentences


def _is_requirement_sentence(sentence: str) -> bool:
    """
    判断一个句子是否为功能性需求描述。

    识别标准：
    - 包含编号开头（1. 2. 3、 等）
    - 包含角色关键词 + 意图关键词的组合
    - 排除纯标题、背景描述和概述性语句

    Args:
        sentence: 待判断的句子

    Returns:
        True 表示是需求句子，False 表示不是
    """
    # 排除标题/标签类短句（以特定关键词开头或结尾的）
    title_keywords = ["项目背景", "核心需求", "需求描述", "功能需求", "非功能需求"]
    for pattern in title_keywords:
        if sentence.strip().startswith(pattern) or sentence.strip().endswith(pattern):
            return False

    # 排除纯描述性/背景类句子（包含项目描述词的为背景，非具体需求）
    background_patterns = ["我们计划", "我们希望", "项目背景", "开发一套", "用于", "实现"]
    for pattern in background_patterns:
        if pattern in sentence:
            return False

    # 编号开头的一定是需求
    if re.match(r'^[\d]+[.、)）]', sentence):
        return True

    # 需同时包含角色关键词和意图关键词，才视为有效需求句子
    has_role = False
    for keywords in ROLE_KEYWORDS.values():
        for keyword in keywords:
            if keyword in sentence:
                has_role = True
                break
        if has_role:
            break

    has_intent = False
    for keywords in INTENT_KEYWORDS.values():
        for keyword in keywords:
            if keyword in sentence:
                has_intent = True
                break
        if has_intent:
            break

    # 角色和意图同时出现，才是功能性需求
    if has_role and has_intent:
        return True

    # 只有意图没有角色，但有明确的动作词，也算需求
    if has_intent:
        action_words = ["必须", "应该", "可以", "需要", "支持", "提供", "实现", "能够"]
        for word in action_words:
            if word in sentence:
                return True

    return False


def generate_user_stories(roles: list[str], intents: list[str], text: str) -> list[str]:
    """
    基于需求句子生成用户故事。

    为每个需求句子匹配其最相关的角色和意图，
    生成精准的用户故事，而非全排列组合。

    用户故事格式: As a [角色], I want [功能], so that [价值]

    Args:
        roles: 识别到的角色列表
        intents: 识别到的意图列表
        text: 原始需求文本

    Returns:
        用户故事列表
    """
    stories = []
    sentences = extract_requirement_sentences(text)

    # 意图到价值描述的映射
    intent_value_map: dict[str, str] = {
        "查看": "及时获取所需信息，做出合理决策",
        "管理": "高效维护数据，保证信息准确与完整",
        "监控": "实时掌握系统状态，及时发现并处理异常",
        "配置": "灵活调整系统行为，满足不同场景需求",
        "导出": "方便进行线下分析和归档留存",
        "认证": "保障系统安全，确保合法访问",
        "通信": "及时获取重要通知，不错过关键事件",
    }

    for sentence in sentences:
        # 为每个句子找到最匹配的角色
        matched_role = _match_role_for_sentence(sentence, roles)
        # 为每个句子找到最匹配的意图
        matched_intent = _match_intent_for_sentence(sentence, intents)
        value = intent_value_map.get(matched_intent, "实现业务目标")

        # 精简句子中的动作描述
        action = _simplify_action(sentence)
        story = f"As a {matched_role}, I want {action}, so that {value}。"
        stories.append(story)

    if not stories:
        stories.append("As a 普通用户, I want 使用该系统功能, so that 实现业务需求。")

    return stories


def _match_role_for_sentence(sentence: str, roles: list[str]) -> str:
    """
    为单个需求句子匹配最相关的角色。

    优先匹配句子中最先出现的角色关键词，
    如果句子中没有任何角色关键词，则使用角色列表中的第一个。

    Args:
        sentence: 需求句子
        roles: 已识别的角色列表

    Returns:
        最匹配的角色名称
    """
    # 找到句子中最早出现的角色
    first_pos = len(sentence)
    first_role = None
    for role in roles:
        keywords = ROLE_KEYWORDS.get(role, [])
        for keyword in keywords:
            pos = sentence.find(keyword)
            if pos != -1 and pos < first_pos:
                first_pos = pos
                first_role = role

    if first_role:
        return first_role

    # 如果句子中没有明确角色，使用频率最高的角色
    return roles[0] if roles else "普通用户"


def _match_intent_for_sentence(sentence: str, intents: list[str]) -> str:
    """
    为单个需求句子匹配最相关的意图。

    优先匹配句子中直接出现的意图关键词。

    Args:
        sentence: 需求句子
        intents: 已识别的意图列表

    Returns:
        最匹配的意图类型
    """
    for intent in intents:
        keywords = INTENT_KEYWORDS.get(intent, [])
        for keyword in keywords:
            if keyword in sentence:
                return intent

    return intents[0] if intents else "查看"


def _simplify_action(sentence: str) -> str:
    """
    将需求句子精简为用户故事中的动作描述。

    去除编号前缀，保留核心动作内容，
    如果句子过长则截取关键部分。

    Args:
        sentence: 原始需求句子

    Returns:
        精简后的动作描述
    """
    # 去除编号前缀
    action = re.sub(r'^[\d]+[.、)）]\s*', '', sentence)
    # 如果超过40字，截取前40字
    if len(action) > 40:
        action = action[:40] + "..."
    return action


def generate_functional_points(text: str) -> list[tuple[str, str]]:
    """
    从需求文本中提取功能点并标注 MoSCoW 优先级。

    只提取核心需求句子作为功能点，
    根据关键词推断优先级。

    Args:
        text: 原始需求文本

    Returns:
        功能点列表，每个元素为 (功能描述, 优先级)
    """
    sentences = extract_requirement_sentences(text)
    points = []

    for sentence in sentences:
        # 去除编号前缀
        clean = re.sub(r'^[\d]+[.、)）]\s*', '', sentence)
        priority = infer_priority(sentence)
        points.append((clean, priority))

    if not points:
        points.append(("实现核心业务功能", "Must"))

    return points


def generate_boundary_conditions(text: str, intents: list[str]) -> list[str]:
    """
    根据需求意图生成常见的边界条件和异常场景。

    基于预定义的异常场景模板，结合识别到的意图类型，
    自动推导可能出现的边界与异常情况。

    Args:
        text: 原始需求文本
        intents: 识别到的意图列表

    Returns:
        边界条件与异常场景列表
    """
    conditions = []

    # 意图到典型边界/异常场景的映射
    boundary_templates: dict[str, list[str]] = {
        "查看": [
            "查询结果为空时的展示处理",
            "大量数据加载时的分页与性能",
            "网络异常导致数据加载失败",
        ],
        "管理": [
            "并发操作导致的数据冲突",
            "删除关联数据时的级联处理",
            "操作权限不足时的提示",
            "输入数据格式校验失败",
        ],
        "监控": [
            "传感器数据丢失或异常值处理",
            "告警风暴（短时间内大量告警）的抑制策略",
            "监控服务自身不可用时的降级方案",
            "网络中断后的数据缓存与重传",
        ],
        "配置": [
            "配置项非法值的校验与提示",
            "配置变更后的实时生效机制",
            "默认配置缺失时的兜底方案",
        ],
        "导出": [
            "导出数据量过大时的性能与超时处理",
            "导出格式不兼容的降级方案",
            "导出过程中网络中断的恢复",
        ],
        "认证": [
            "密码错误次数过多时的账户锁定",
            "Token 过期后的无感刷新机制",
            "多设备同时登录的冲突处理",
        ],
        "通信": [
            "消息推送失败的重试机制",
            "消息堆积的削峰与消费策略",
            "接收方离线时的消息暂存",
        ],
    }

    for intent in intents:
        templates = boundary_templates.get(intent, [])
        conditions.extend(templates)

    # 如果没有任何匹配，提供通用边界条件
    if not conditions:
        conditions = [
            "输入数据为空或格式异常时的处理",
            "高并发场景下的系统稳定性",
            "网络异常时的重试与降级方案",
        ]

    return conditions


def generate_acceptance_criteria(
    roles: list[str], intents: list[str], text: str
) -> list[str]:
    """
    基于角色和意图生成验收标准（Given-When-Then 格式）。

    每个意图生成对应的验收标准模板，
    用从文本中提取的目标对象填充模板。

    Args:
        roles: 识别到的角色列表
        intents: 识别到的意图列表
        text: 原始需求文本

    Returns:
        验收标准列表
    """
    criteria = []
    target = _extract_target(text)
    primary_role = roles[0] if roles else "用户"

    # 意图到 Given-When-Then 模板的映射
    criteria_templates: dict[str, list[str]] = {
        "查看": [
            f"Given {primary_role}已登录系统, When {primary_role}访问{target}数据页面, Then 系统正确展示{target}数据列表",
            "Given 查询条件已设置, When 用户执行查询操作, Then 返回匹配的结果并在3秒内展示",
        ],
        "管理": [
            f"Given {primary_role}具有管理权限, When {primary_role}提交新增/编辑表单, Then 数据正确保存并返回成功提示",
            "Given 数据记录存在, When 用户执行删除操作, Then 记录被标记删除且关联数据正确处理",
        ],
        "监控": [
            "Given 传感器已连接, When 传感器数据超过预设阈值, Then 系统在5秒内触发告警通知",
            "Given 监控服务运行中, When 传感器数据断连超过设定时间, Then 系统标记设备为离线并通知管理员",
        ],
        "配置": [
            f"Given {primary_role}具有配置权限, When {primary_role}修改系统配置项, Then 配置即时生效并记录操作日志",
        ],
        "导出": [
            "Given 数据查询结果不为空, When 用户点击导出按钮, Then 系统生成指定格式文件并提供下载",
        ],
        "认证": [
            "Given 用户输入正确的凭证, When 用户提交登录请求, Then 系统返回有效 Token 并跳转至主页",
            "Given 用户 Token 已过期, When 用户发起业务请求, Then 系统引导重新登录",
        ],
        "通信": [
            "Given 用户已订阅通知, When 触发通知事件, Then 用户在10秒内收到推送消息",
        ],
    }

    for intent in intents:
        templates = criteria_templates.get(intent, [])
        criteria.extend(templates)

    if not criteria:
        criteria.append(
            "Given 系统正常运行, When 用户执行核心操作, Then 系统返回预期结果且响应时间小于3秒"
        )

    return criteria


def _extract_target(text: str) -> str:
    """
    从需求文本中提取核心目标对象。

    通过启发式规则提取名词短语作为目标对象。

    Args:
        text: 原始需求文本

    Returns:
        目标对象字符串
    """
    # 尝试匹配"XX系统"、"XX平台"等模式
    system_match = re.search(r'([\u4e00-\u9fa5]{2,6})(?:系统|平台|模块|功能)', text)
    if system_match:
        return system_match.group(1)

    # 尝试匹配"XX管理"、"XX监控"等模式
    action_match = re.search(r'([\u4e00-\u9fa5]{2,6})(?:管理|监控|配置|查询)', text)
    if action_match:
        return action_match.group(1)

    return "相关"


def template_analyze(text: str) -> DecomposedResult:
    """
    模板模式的核心分析入口。

    通过关键词匹配和模板规则，将需求文本拆解为四个维度：
    - 用户故事
    - 功能点列表（含 MoSCoW 优先级）
    - 边界条件与异常场景
    - 验收标准（Given-When-Then）

    Args:
        text: 原始需求描述文本

    Returns:
        DecomposedResult 拆解结果对象

    Raises:
        ValueError: 当输入文本为空时抛出
    """
    if not text or not text.strip():
        raise ValueError("需求描述文本不能为空")

    text = text.strip()

    # 第一步：识别角色和意图
    roles = identify_roles(text)
    intents = identify_intents(text)

    # 第二步：基于角色和意图生成拆解结果
    result = DecomposedResult(
        user_stories=generate_user_stories(roles, intents, text),
        functional_points=generate_functional_points(text),
        boundary_conditions=generate_boundary_conditions(text, intents),
        acceptance_criteria=generate_acceptance_criteria(roles, intents, text),
    )

    return result
