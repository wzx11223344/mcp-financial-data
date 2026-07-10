"""宏观经济数据工具模块。

提供 GDP、CPI、PMI、货币供应量、汇率等宏观经济数据工具，
数据来源为 akshare。

所有工具返回 markdown 格式字符串，适合 MCP 客户端直接消费。
"""

from __future__ import annotations

import logging

import akshare as ak
import pandas as pd

from .utils import format_dataframe, handle_error, safe_float

logger = logging.getLogger(__name__)


def get_gdp_data() -> str:
    """获取中国 GDP 数据。

    返回最近几年的 GDP 季度数据，包括 GDP 总量、同比增长率等。

    Returns:
        markdown 格式的 GDP 数据表。
    """
    func_name = "get_gdp_data"
    try:
        df = ak.macro_china_gdp()

        if df is None or df.empty:
            return "**未获取到 GDP 数据**"

        # 重命名常见列
        col_map = {
            "季度": "季度",
            "国内生产总值-绝对值": "GDP(亿元)",
            "国内生产总值-同比增长": "GDP同比(%)",
            "第一产业-绝对值": "第一产业(亿元)",
            "第二产业-绝对值": "第二产业(亿元)",
            "第三产业-绝对值": "第三产业(亿元)",
            "第一产业-同比增长": "第一产业同比(%)",
            "第二产业-同比增长": "第二产业同比(%)",
            "第三产业-同比增长": "第三产业同比(%)",
        }
        rename_cols = {k: v for k, v in col_map.items() if k in df.columns}
        df = df.rename(columns=rename_cols)

        # 取最近 20 条
        df_display = df.head(20) if len(df) > 20 else df

        return "## 中国 GDP 数据（最近 20 期）\n\n" + format_dataframe(df_display, max_rows=20)

    except Exception as e:
        return handle_error(func_name, e)


def get_cpi_data() -> str:
    """获取中国 CPI（居民消费价格指数）数据。

    返回最近几年的月度 CPI 数据，包括同比、环比涨跌幅。

    Returns:
        markdown 格式的 CPI 数据表。
    """
    func_name = "get_cpi_data"
    try:
        df = ak.macro_china_cpi()

        if df is None or df.empty:
            return "**未获取到 CPI 数据**"

        # 重命名常见列
        col_map = {
            "月份": "月份",
            "全国-当月": "全国CPI(当月同比%)",
            "全国-同比增长": "全国CPI(同比%)",
            "全国-环比增长": "全国CPI(环比%)",
            "全国-累计": "全国CPI(累计同比%)",
            "城市-当月": "城市CPI(当月同比%)",
            "农村-当月": "农村CPI(当月同比%)",
        }
        rename_cols = {k: v for k, v in col_map.items() if k in df.columns}
        df = df.rename(columns=rename_cols)

        # 取最近 24 条
        df_display = df.head(24) if len(df) > 24 else df

        return "## 中国 CPI 数据（最近 24 期）\n\n" + format_dataframe(df_display, max_rows=24)

    except Exception as e:
        return handle_error(func_name, e)


def get_pmi_data() -> str:
    """获取中国 PMI（采购经理指数）数据。

    返回最近几年的月度 PMI 数据，包括制造业和非制造业 PMI。

    Returns:
        markdown 格式的 PMI 数据表。
    """
    func_name = "get_pmi_data"
    try:
        df = ak.macro_china_pmi()

        if df is None or df.empty:
            return "**未获取到 PMI 数据**"

        # 重命名常见列
        col_map = {
            "月份": "月份",
            "制造业-LF": "制造业PMI",
            "制造业-同比增长": "制造业PMI(同比%)",
            "制造业-环比增长": "制造业PMI(环比%)",
            "非制造业-LF": "非制造业PMI",
            "非制造业-同比增长": "非制造业PMI(同比%)",
            "非制造业-环比增长": "非制造业PMI(环比%)",
        }
        rename_cols = {k: v for k, v in col_map.items() if k in df.columns}
        df = df.rename(columns=rename_cols)

        # 取最近 24 条
        df_display = df.head(24) if len(df) > 24 else df

        return "## 中国 PMI 数据（最近 24 期）\n\n" + format_dataframe(df_display, max_rows=24)

    except Exception as e:
        return handle_error(func_name, e)


def get_money_supply() -> str:
    """获取中国货币供应量数据（M0/M1/M2）。

    返回最近几年的月度货币供应量数据，包括 M0、M1、M2 的绝对值及同比增速。

    Returns:
        markdown 格式的货币供应量表。
    """
    func_name = "get_money_supply"
    try:
        df = ak.macro_china_money_supply()

        if df is None or df.empty:
            return "**未获取到货币供应量数据**"

        # 重命名常见列
        col_map = {
            "月份": "月份",
            "M2-数量": "M2(万亿元)",
            "M2-同比": "M2同比(%)",
            "M2-环比": "M2环比(%)",
            "M1-数量": "M1(万亿元)",
            "M1-同比": "M1同比(%)",
            "M1-环比": "M1环比(%)",
            "M0-数量": "M0(万亿元)",
            "M0-同比": "M0同比(%)",
            "M0-环比": "M0环比(%)",
        }
        rename_cols = {k: v for k, v in col_map.items() if k in df.columns}
        df = df.rename(columns=rename_cols)

        # 取最近 24 条
        df_display = df.head(24) if len(df) > 24 else df

        return "## 中国货币供应量 M0/M1/M2（最近 24 期）\n\n" + format_dataframe(df_display, max_rows=24)

    except Exception as e:
        return handle_error(func_name, e)


def get_fx_rate(currency: str = "usd") -> str:
    """获取人民币汇率数据。

    返回指定货币兑人民币的汇率历史数据。

    Args:
        currency: 货币代码，可选：
            - ``usd``：美元（默认）
            - ``eur``：欧元
            - ``jpy``：日元
            - ``gbp``：英镑
            - ``hkd``：港元

    Returns:
        markdown 格式的汇率数据表。
    """
    func_name = "get_fx_rate"
    try:
        currency = currency.lower().strip()

        # 获取人民币汇率中间价
        df = ak.currency_boc_sina(symbol=currency, start_date="20240101", end_date="20261231")

        if df is None or df.empty:
            # 尝试备用接口
            df = ak.fx_spot_quote()

        if df is None or df.empty:
            return f"**未获取到 {currency} 汇率数据**"

        # 取最近 30 条
        df_display = df.tail(30) if len(df) > 30 else df

        currency_name_map = {
            "usd": "美元",
            "eur": "欧元",
            "jpy": "日元",
            "gbp": "英镑",
            "hkd": "港元",
        }
        cn_name = currency_name_map.get(currency, currency.upper())

        return f"## {cn_name}兑人民币汇率（最近 30 期）\n\n" + format_dataframe(df_display, max_rows=30)

    except Exception as e:
        return handle_error(func_name, e)
