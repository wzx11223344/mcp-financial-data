"""股票数据工具模块。

提供 A 股实时行情、历史 K 线、财务指标、股票列表、涨跌幅榜等工具，
数据来源为 akshare。

所有工具返回 markdown 格式字符串，适合 MCP 客户端直接消费。
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd

from .utils import format_dataframe, handle_error, normalize_symbol, safe_float

logger = logging.getLogger(__name__)


def get_stock_quote(symbol: str) -> str:
    """获取 A 股股票实时行情。

    返回最新交易日的开盘价、最高价、最低价、收盘价、成交量、成交额、
    涨跌幅等核心行情字段。

    Args:
        symbol: 股票代码，6 位数字，如 ``600519``（贵州茅台）、``000001``（平安银行）。
            支持带前缀格式如 ``sh600519``、``sz000001``。

    Returns:
        markdown 格式的实时行情表。
    """
    func_name = "get_stock_quote"
    try:
        code = normalize_symbol(symbol)
        df = ak.stock_zh_a_spot_em()

        # 查找目标股票
        row = df[df["代码"] == code]
        if row.empty:
            return f"**未找到股票代码 {code}**\n\n请确认代码是否正确（6 位数字）。"

        row = row.iloc[0]

        # 提取关键字段
        result = pd.DataFrame(
            {
                "项目": [
                    "股票代码",
                    "股票名称",
                    "最新价",
                    "涨跌幅(%)",
                    "涨跌额",
                    "成交量(手)",
                    "成交额(元)",
                    "开盘价",
                    "最高价",
                    "最低价",
                    "昨收价",
                    "量比",
                    "换手率(%)",
                    "市盈率(动)",
                    "市净率",
                    "总市值(亿)",
                    "流通市值(亿)",
                ],
                "数值": [
                    row.get("代码", "-"),
                    row.get("名称", "-"),
                    safe_float(row.get("最新价", 0)),
                    safe_float(row.get("涨跌幅", 0)),
                    safe_float(row.get("涨跌额", 0)),
                    safe_float(row.get("成交量", 0)),
                    safe_float(row.get("成交额", 0)),
                    safe_float(row.get("开盘", 0)),
                    safe_float(row.get("最高", 0)),
                    safe_float(row.get("最低", 0)),
                    safe_float(row.get("昨收", 0)),
                    safe_float(row.get("量比", 0)),
                    safe_float(row.get("换手率", 0)),
                    safe_float(row.get("市盈率-动态", 0)),
                    safe_float(row.get("市净率", 0)),
                    safe_float(row.get("总市值", 0)) / 1e8,
                    safe_float(row.get("流通市值", 0)) / 1e8,
                ],
            }
        )

        return f"## {row.get('名称', code)}（{code}）实时行情\n\n" + format_dataframe(result, max_rows=30)

    except Exception as e:
        return handle_error(func_name, e)


def get_stock_history(
    symbol: str,
    start: str = "",
    end: str = "",
    period: str = "daily",
) -> str:
    """获取 A 股股票历史 K 线数据。

    支持日线、周线、月线三种周期。默认返回最近 60 个交易日数据。

    Args:
        symbol: 股票代码，6 位数字，如 ``600519``。
        start: 开始日期，格式 ``YYYYMMDD``，如 ``20240101``。
            默认为最近 60 个交易日。
        end: 结束日期，格式 ``YYYYMMDD``。
            默认为今天。
        period: K 线周期，可选 ``daily``（日线）、``weekly``（周线）、``monthly``（月线）。

    Returns:
        markdown 格式的历史 K 线表，包含日期、开盘、收盘、最高、最低、成交量、成交额。
    """
    func_name = "get_stock_history"
    try:
        code = normalize_symbol(symbol)

        # 处理日期
        if not end:
            end = datetime.now().strftime("%Y%m%d")
        if not start:
            start = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")

        # 映射周期
        period_map = {
            "daily": "daily",
            "weekly": "weekly",
            "monthly": "monthly",
        }
        ak_period = period_map.get(period, "daily")

        df = ak.stock_zh_a_hist(
            symbol=code,
            period=ak_period,
            start_date=start,
            end_date=end,
            adjust="qfq",  # 前复权
        )

        if df is None or df.empty:
            return f"**未找到 {code} 在 {start}~{end} 期间的历史数据**"

        # 重命名列
        col_map = {
            "日期": "日期",
            "开盘": "开盘价",
            "收盘": "收盘价",
            "最高": "最高价",
            "最低": "最低价",
            "成交量": "成交量",
            "成交额": "成交额",
            "振幅": "振幅(%)",
            "涨跌幅": "涨跌幅(%)",
            "涨跌额": "涨跌额",
            "换手率": "换手率(%)",
        }
        rename_cols = {k: v for k, v in col_map.items() if k in df.columns}
        df = df.rename(columns=rename_cols)

        return f"## {code} 历史 K 线（{period}，{start} ~ {end}）\n\n" + format_dataframe(df, max_rows=50)

    except Exception as e:
        return handle_error(func_name, e)


def get_stock_financial(symbol: str) -> str:
    """获取 A 股股票核心财务指标。

    返回最新报告期的 ROE、PE（动态/静态/TTM）、PB、营收、净利润、
    毛利率、净利率等关键财务指标。

    Args:
        symbol: 股票代码，6 位数字，如 ``600519``。

    Returns:
        markdown 格式的财务指标表。
    """
    func_name = "get_stock_financial"
    try:
        code = normalize_symbol(symbol)

        # 1. 从实时行情获取 PE/PB
        spot_df = ak.stock_zh_a_spot_em()
        spot_row = spot_df[spot_df["代码"] == code]
        if spot_row.empty:
            return f"**未找到股票代码 {code}**"

        spot_row = spot_row.iloc[0]
        pe_dynamic = safe_float(spot_row.get("市盈率-动态", 0))
        pe_ttm = safe_float(spot_row.get("市盈率-TTM", 0))
        pb = safe_float(spot_row.get("市净率", 0))

        # 2. 获取个股财务指标
        try:
            fin_df = ak.stock_financial_abstract(symbol=code)
            latest_fin = {}
            if fin_df is not None and not fin_df.empty:
                # 取最新一期
                latest_col = fin_df.columns[0] if len(fin_df.columns) > 0 else None
                if latest_col:
                    for _, row in fin_df.iterrows():
                        indicator = str(row.iloc[0]) if len(row) > 0 else ""
                        if latest_col in fin_df.columns:
                            latest_fin[indicator] = row[latest_col]
        except Exception:
            latest_fin = {}

        # 3. 组装结果
        result = pd.DataFrame(
            {
                "指标": [
                    "股票代码",
                    "市盈率(动态)",
                    "市盈率(TTM)",
                    "市净率",
                    "总市值(亿)",
                    "流通市值(亿)",
                ],
                "数值": [
                    code,
                    pe_dynamic,
                    pe_ttm,
                    pb,
                    safe_float(spot_row.get("总市值", 0)) / 1e8,
                    safe_float(spot_row.get("流通市值", 0)) / 1e8,
                ],
            }
        )

        # 追加财务摘要数据
        extra_rows = []
        for key in (
            "营业总收入",
            "净利润",
            "净资产收益率",
            "毛利率",
            "净利率",
        ):
            if key in latest_fin:
                extra_rows.append({"指标": key, "数值": latest_fin[key]})

        if extra_rows:
            extra_df = pd.DataFrame(extra_rows)
            result = pd.concat([result, extra_df], ignore_index=True)

        return f"## {code} 财务指标\n\n" + format_dataframe(result, max_rows=30)

    except Exception as e:
        return handle_error(func_name, e)


def get_stock_list(market: str = "hs300") -> str:
    """获取 A 股股票成分股列表。

    支持沪深 300、中证 500、上证 50、全 A 等主流指数成分股。

    Args:
        market: 市场标识，可选：
            - ``hs300``：沪深 300 成分股（默认）
            - ``zz500``：中证 500 成分股
            - ``sz50``：上证 50 成分股
            - ``all``：全 A 股列表

    Returns:
        markdown 格式的成分股列表，含代码、名称等。
    """
    func_name = "get_stock_list"
    try:
        market = market.lower().strip()

        if market == "hs300":
            df = ak.index_stock_cons_csindex(symbol="000300")
            title = "沪深 300 成分股"
        elif market == "zz500":
            df = ak.index_stock_cons_csindex(symbol="000905")
            title = "中证 500 成分股"
        elif market == "sz50":
            df = ak.index_stock_cons_csindex(symbol="000016")
            title = "上证 50 成分股"
        elif market == "all":
            df = ak.stock_zh_a_spot_em()
            df = df[["代码", "名称"]].copy()
            title = "全 A 股列表"
        else:
            return f"**不支持的市场标识: {market}**\n\n可选: hs300 / zz500 / sz50 / all"

        if market != "all":
            df = df.rename(columns={"成分券代码": "代码", "成分券名称": "名称"})
            df = df[["代码", "名称"]].copy() if "名称" in df.columns else df

        return f"## {title}（共 {len(df)} 只）\n\n" + format_dataframe(df, max_rows=50)

    except Exception as e:
        return handle_error(func_name, e)


def get_top_gainers(count: int = 20) -> str:
    """获取 A 股涨幅排行榜。

    返回当日涨幅最高的股票列表。

    Args:
        count: 返回数量，默认 20，最大 100。

    Returns:
        markdown 格式的涨幅榜表，含代码、名称、最新价、涨跌幅、成交额。
    """
    func_name = "get_top_gainers"
    try:
        count = max(1, min(count, 100))

        df = ak.stock_zh_a_spot_em()
        df = df.sort_values(by="涨跌幅", ascending=False).head(count)

        # 选择关键列
        cols = ["代码", "名称", "最新价", "涨跌幅", "涨跌额", "成交额", "换手率"]
        available_cols = [c for c in cols if c in df.columns]
        df = df[available_cols].copy()

        return f"## A 股涨幅榜 TOP {count}\n\n" + format_dataframe(df, max_rows=count)

    except Exception as e:
        return handle_error(func_name, e)


def get_top_losers(count: int = 20) -> str:
    """获取 A 股跌幅排行榜。

    返回当日跌幅最大的股票列表。

    Args:
        count: 返回数量，默认 20，最大 100。

    Returns:
        markdown 格式的跌幅榜表，含代码、名称、最新价、涨跌幅、成交额。
    """
    func_name = "get_top_losers"
    try:
        count = max(1, min(count, 100))

        df = ak.stock_zh_a_spot_em()
        df = df.sort_values(by="涨跌幅", ascending=True).head(count)

        # 选择关键列
        cols = ["代码", "名称", "最新价", "涨跌幅", "涨跌额", "成交额", "换手率"]
        available_cols = [c for c in cols if c in df.columns]
        df = df[available_cols].copy()

        return f"## A 股跌幅榜 TOP {count}\n\n" + format_dataframe(df, max_rows=count)

    except Exception as e:
        return handle_error(func_name, e)
