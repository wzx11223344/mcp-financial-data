"""基金数据工具模块。

提供开放式基金列表、基金净值历史、基金持仓、基金业绩等工具，
数据来源为 akshare。

所有工具返回 markdown 格式字符串，适合 MCP 客户端直接消费。
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd

from .utils import format_dataframe, handle_error, safe_float

logger = logging.getLogger(__name__)


def get_fund_list(fund_type: str = "stock") -> str:
    """获取开放式基金列表。

    按基金类型筛选返回基金列表。

    Args:
        fund_type: 基金类型，可选：
            - ``stock``：股票型基金（默认）
            - ``mixed``：混合型基金
            - ``bond``：债券型基金
            - ``index``：指数型基金
            - ``qdii``：QDII 基金
            - ``etf``：ETF 基金
            - ``lof``：LOF 基金
            - ``all``：全部基金

    Returns:
        markdown 格式的基金列表，含基金代码、名称、类型等。
    """
    func_name = "get_fund_list"
    try:
        fund_type = fund_type.lower().strip()

        # 获取开放式基金列表
        df = ak.fund_open_fund_rank_em(symbol="全部")

        if df is None or df.empty:
            return "**未获取到基金列表数据**"

        # 类型映射
        type_filter_map = {
            "stock": "股票型",
            "mixed": "混合型",
            "bond": "债券型",
            "index": "指数型",
            "qdii": "QDII",
            "etf": "ETF",
            "lof": "LOF",
        }

        title = "开放式基金列表"

        if fund_type in type_filter_map:
            keyword = type_filter_map[fund_type]
            # 尝试按基金类型列筛选
            if "基金类型" in df.columns:
                mask = df["基金类型"].astype(str).str.contains(keyword, na=False)
                filtered = df[mask]
            else:
                filtered = df
            title = f"{keyword}基金列表"
            df_display = filtered
        else:
            df_display = df

        if df_display is None or df_display.empty:
            return f"**未找到类型为 {fund_type} 的基金**"

        # 选择关键列
        cols = ["基金代码", "基金简称", "日期", "单位净值", "累计净值", "日增长率", "近1周", "近1月", "近3月", "近6月", "近1年"]
        available_cols = [c for c in cols if c in df_display.columns]
        df_display = df_display[available_cols].copy()

        return f"## {title}（共 {len(df_display)} 只）\n\n" + format_dataframe(df_display, max_rows=50)

    except Exception as e:
        return handle_error(func_name, e)


def get_fund_nav(fund_code: str) -> str:
    """获取基金净值历史数据。

    返回指定基金的单位净值和累计净值历史记录。

    Args:
        fund_code: 基金代码，如 ``000001``（华夏成长）、``161725``（招商中证白酒）。

    Returns:
        markdown 格式的基金净值历史表。
    """
    func_name = "get_fund_nav"
    try:
        fund_code = fund_code.strip()

        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")

        if df is None or df.empty:
            return f"**未找到基金 {fund_code} 的净值数据**\n\n请确认基金代码是否正确。"

        # 重命名列
        col_map = {
            "净值日期": "日期",
            "单位净值": "单位净值",
            "日增长率": "日增长率(%)",
        }
        rename_cols = {k: v for k, v in col_map.items() if k in df.columns}
        df = df.rename(columns=rename_cols)

        # 默认只取最近 60 条
        if len(df) > 60:
            df_display = df.tail(60)
            truncate_note = f"（共 {len(df)} 条，仅显示最近 60 条）"
        else:
            df_display = df
            truncate_note = ""

        return f"## 基金 {fund_code} 净值历史{truncate_note}\n\n" + format_dataframe(df_display, max_rows=50)

    except Exception as e:
        return handle_error(func_name, e)


def get_fund_holdings(fund_code: str) -> str:
    """获取基金持仓数据。

    返回指定基金的重仓股列表及持仓比例。

    Args:
        fund_code: 基金代码，如 ``161725``。

    Returns:
        markdown 格式的基金持仓表，含股票代码、股票名称、持仓占比等。
    """
    func_name = "get_fund_holdings"
    try:
        fund_code = fund_code.strip()

        df = ak.fund_portfolio_hold_em(symbol=fund_code, date="2024")

        if df is None or df.empty:
            # 尝试获取最新年度
            current_year = datetime.now().year
            for year in range(current_year, current_year - 3, -1):
                df = ak.fund_portfolio_hold_em(symbol=fund_code, date=str(year))
                if df is not None and not df.empty:
                    break

        if df is None or df.empty:
            return f"**未找到基金 {fund_code} 的持仓数据**"

        # 重命名列
        col_map = {
            "序号": "序号",
            "股票代码": "股票代码",
            "股票名称": "股票名称",
            "占净值比例": "持仓占比(%)",
            "持股数": "持股数(股)",
            "持仓市值": "持仓市值(元)",
            "季度": "报告期",
        }
        rename_cols = {k: v for k, v in col_map.items() if k in df.columns}
        df = df.rename(columns=rename_cols)

        # 选择关键列
        preferred_cols = ["序号", "股票代码", "股票名称", "持仓占比(%)", "持股数(股)", "持仓市值(元)", "报告期"]
        available_cols = [c for c in preferred_cols if c in df.columns]
        if available_cols:
            df = df[available_cols].copy()

        return f"## 基金 {fund_code} 重仓股\n\n" + format_dataframe(df, max_rows=30)

    except Exception as e:
        return handle_error(func_name, e)


def get_fund_performance(fund_code: str) -> str:
    """获取基金业绩表现数据。

    返回指定基金的近 1 周、近 1 月、近 3 月、近 6 月、近 1 年、
    近 3 年等各阶段收益率及同类排名。

    Args:
        fund_code: 基金代码，如 ``161725``。

    Returns:
        markdown 格式的基金业绩表。
    """
    func_name = "get_fund_performance"
    try:
        fund_code = fund_code.strip()

        # 获取基金排行数据（含业绩）
        df = ak.fund_open_fund_rank_em(symbol="全部")

        if df is None or df.empty:
            return "**未获取到基金排行数据**"

        # 查找目标基金
        if "基金代码" not in df.columns:
            return "**数据中缺少基金代码列**"

        row = df[df["基金代码"].astype(str).str.strip() == fund_code]

        if row.empty:
            return f"**未找到基金代码 {fund_code}**\n\n请确认基金代码是否正确。"

        row = row.iloc[0]

        # 提取业绩指标
        perf_items = [
            ("基金代码", "基金代码"),
            ("基金简称", "基金简称"),
            ("日期", "日期"),
            ("单位净值", "单位净值"),
            ("累计净值", "累计净值"),
            ("日增长率", "日增长率(%)"),
            ("近1周", "近1周(%)"),
            ("近1月", "近1月(%)"),
            ("近3月", "近3月(%)"),
            ("近6月", "近6月(%)"),
            ("近1年", "近1年(%)"),
            ("近2年", "近2年(%)"),
            ("近3年", "近3年(%)"),
            ("今年来", "今年来(%)"),
            ("成立来", "成立来(%)"),
        ]

        labels = []
        values = []
        for col_name, label in perf_items:
            if col_name in row.index:
                labels.append(label)
                val = row[col_name]
                if "%" in label:
                    val = safe_float(val)
                values.append(val)

        result = pd.DataFrame({"指标": labels, "数值": values})

        return f"## 基金 {fund_code} 业绩表现\n\n" + format_dataframe(result, max_rows=30)

    except Exception as e:
        return handle_error(func_name, e)
