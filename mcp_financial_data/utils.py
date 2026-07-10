"""公共工具函数模块。

提供 DataFrame 格式化、安全类型转换、数据截断等通用功能，
供所有 *_tools 模块复用。
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def format_dataframe(df: pd.DataFrame, max_rows: int = 50) -> str:
    """将 DataFrame 转换为 markdown 表格字符串。

    自动截断超过 ``max_rows`` 的行数，并在末尾提示截断信息。
    对于 NaN 值显示为 ``-``。

    Args:
        df: 要格式化的 DataFrame。
        max_rows: 最大显示行数，默认 50。

    Returns:
        markdown 格式的表格字符串。如果 ``df`` 为空或为 None，返回提示信息。
    """
    if df is None or not isinstance(df, pd.DataFrame):
        return "**无数据**"

    if df.empty:
        return "**数据为空**"

    # 截断
    truncated = False
    total_rows = len(df)
    if total_rows > max_rows:
        df = df.head(max_rows)
        truncated = True

    # 填充 NaN
    df = df.fillna("-")

    # 转换所有列为字符串，避免类型问题
    df = df.astype(str)

    md = df.to_markdown(index=False)

    if truncated:
        md += f"\n\n*（已截断，共 {total_rows} 行，仅显示前 {max_rows} 行）*"

    return md


def safe_float(val: Any, default: float = 0.0) -> float:
    """安全地将任意值转换为 float。

    处理 None、空字符串、非数字字符串等异常情况。

    Args:
        val: 要转换的值。
        default: 转换失败时返回的默认值。

    Returns:
        转换后的 float 值，或默认值。
    """
    if val is None:
        return default
    try:
        if isinstance(val, str):
            val = val.strip().replace(",", "").replace("%", "")
            if val in ("", "-", "--", "nan", "NaN", "None"):
                return default
        return float(val)
    except (ValueError, TypeError):
        return default


def truncate_data(data: Any, max_rows: int = 50) -> Any:
    """截断数据至最大行数。

    支持 DataFrame、list、dict（含 list 值）等类型。

    Args:
        data: 要截断的数据。
        max_rows: 最大行数/项数。

    Returns:
        截断后的数据（同类型）。
    """
    if data is None:
        return None

    if isinstance(data, pd.DataFrame):
        if len(data) > max_rows:
            return data.head(max_rows)
        return data

    if isinstance(data, list):
        if len(data) > max_rows:
            return data[:max_rows]
        return data

    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, list) and len(value) > max_rows:
                result[key] = value[:max_rows]
            elif isinstance(value, pd.DataFrame) and len(value) > max_rows:
                result[key] = value.head(max_rows)
            else:
                result[key] = value
        return result

    return data


def handle_error(func_name: str, error: Exception) -> str:
    """统一错误处理，生成友好的错误信息字符串。

    Args:
        func_name: 出错的函数/工具名称。
        error: 捕获的异常对象。

    Returns:
        markdown 格式的错误提示字符串。
    """
    error_msg = str(error)
    logger.error("工具 %s 执行失败: %s", func_name, error_msg, exc_info=True)

    # 常见错误模式友好提示
    if "ModuleNotFoundError" in error_msg or "No module named" in error_msg:
        hint = "请检查 akshare 是否已安装：`pip install akshare`"
    elif "ConnectionError" in error_msg or "MaxRetryError" in error_msg or "timeout" in error_msg.lower():
        hint = "网络连接超时，请检查网络后重试"
    elif "KeyError" in error_msg:
        hint = f"数据字段不存在，接口可能已更新（{error_msg}）"
    elif "AttributeError" in error_msg:
        hint = f"akshare 接口可能已变更：{error_msg}"
    else:
        hint = error_msg

    return f"**[获取数据失败 - {func_name}]**\n\n错误: {hint}"


def normalize_symbol(symbol: str) -> str:
    """标准化股票代码格式。

    自动补全 6 位代码前缀的零，并处理常见格式变体。

    Args:
        symbol: 股票代码，如 ``000001``、``sz000001``、``600519``。

    Returns:
        标准化的 6 位代码字符串。
    """
    if not symbol:
        return symbol

    symbol = symbol.strip().lower()

    # 去除常见前缀
    for prefix in ("sh", "sz", "bj", ".sh", ".sz", ".bj"):
        if symbol.startswith(prefix):
            symbol = symbol[len(prefix):]
            break

    # 去除后缀
    for suffix in (".sh", ".sz", ".bj", ".ss"):
        if symbol.endswith(suffix):
            symbol = symbol[: -len(suffix)]
            break

    # 补零
    symbol = symbol.zfill(6)

    return symbol
