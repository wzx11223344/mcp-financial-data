"""市场行情工具模块。

提供指数行情、板块涨跌幅、市场宽度、北向资金流向等工具，
数据来源为 akshare。

所有工具返回 markdown 格式字符串，适合 MCP 客户端直接消费。
"""

from __future__ import annotations

import logging

import akshare as ak
import pandas as pd

from .utils import format_dataframe, handle_error, safe_float

logger = logging.getLogger(__name__)


def get_index_data(symbol: str = "sh000001") -> str:
    """获取 A 股指数实时行情。

    返回指定指数的实时行情数据。

    Args:
        symbol: 指数代码，常用代码：
            - ``sh000001``：上证指数（默认）
            - ``sz399001``：深证成指
            - ``sz399006``：创业板指
            - ``sh000688``：科创50
            - ``sh000300``：沪深300
            - ``sh000905``：中证500
            - ``sh000016``：上证50

    Returns:
        markdown 格式的指数行情表。
    """
    func_name = "get_index_data"
    try:
        symbol = symbol.strip().lower()

        # 获取指数实时行情
        df = ak.stock_zh_index_spot_em(symbol="指数成分")

        if df is None or df.empty:
            # 尝试备用接口
            df = ak.stock_zh_index_spot_sina()

        if df is None or df.empty:
            return f"**未获取到指数 {symbol} 的行情数据**"

        # 查找目标指数
        # 常见列名：代码
        code_col = None
        for col in ("代码", "指数代码", "symbol", "code"):
            if col in df.columns:
                code_col = col
                break

        if code_col is None:
            return "**数据中缺少代码列**"

        # 标准化查找
        symbol_clean = symbol.replace("sh", "").replace("sz", "").replace("bj", "")
        mask = df[code_col].astype(str).str.contains(symbol_clean, na=False)
        row = df[mask]

        if row.empty:
            # 返回全部指数列表供用户选择
            cols = [c for c in ("代码", "名称", "最新价", "涨跌幅", "涨跌额", "成交额") if c in df.columns]
            df_display = df[cols].copy() if cols else df
            return "## 主要指数行情\n\n" + format_dataframe(df_display, max_rows=30)

        row = row.iloc[0]

        # 组装单行结果
        items = []
        for col in df.columns:
            items.append({"字段": col, "数值": row[col]})

        result = pd.DataFrame(items)

        name = row.get("名称", symbol)
        return f"## {name}（{symbol}）实时行情\n\n" + format_dataframe(result, max_rows=30)

    except Exception as e:
        return handle_error(func_name, e)


def get_sector_performance() -> str:
    """获取 A 股板块涨跌幅排行。

    返回当日行业板块的涨跌幅排名。

    Returns:
        markdown 格式的板块涨跌幅表。
    """
    func_name = "get_sector_performance"
    try:
        # 获取行业板块行情
        df = ak.stock_board_industry_name_em()

        if df is None or df.empty:
            # 尝试备用接口
            df = ak.stock_sector_spot(indicator="新浪行业")

        if df is None or df.empty:
            return "**未获取到板块行情数据**"

        # 按涨跌幅排序
        for sort_col in ("涨跌幅", "changepercent"):
            if sort_col in df.columns:
                df = df.sort_values(by=sort_col, ascending=False)
                break

        # 选择关键列
        preferred_cols = [
            "板块名称", "最新价", "涨跌额", "涨跌幅",
            "总市值", "换手率", "上涨家数", "下跌家数",
            "领涨股票", "领涨股票-涨跌幅",
        ]
        available_cols = [c for c in preferred_cols if c in df.columns]
        if available_cols:
            df = df[available_cols].copy()

        return "## 行业板块涨跌幅排行\n\n" + format_dataframe(df, max_rows=50)

    except Exception as e:
        return handle_error(func_name, e)


def get_market_breadth() -> str:
    """获取 A 股市场宽度数据。

    返回当日全市场的涨跌家数、涨停跌停数量等市场宽度指标。

    Returns:
        markdown 格式的市场宽度表。
    """
    func_name = "get_market_breadth"
    try:
        df = ak.stock_zh_a_spot_em()

        if df is None or df.empty:
            return "**未获取到市场行情数据**"

        total = len(df)

        # 涨跌统计
        up_count = 0
        down_count = 0
        flat_count = 0
        limit_up = 0
        limit_down = 0

        if "涨跌幅" in df.columns:
            up_count = int((df["涨跌幅"].apply(lambda x: safe_float(x)) > 0).sum())
            down_count = int((df["涨跌幅"].apply(lambda x: safe_float(x)) < 0).sum())
            flat_count = int((df["涨跌幅"].apply(lambda x: safe_float(x)) == 0).sum())
            limit_up = int((df["涨跌幅"].apply(lambda x: safe_float(x)) >= 9.9).sum())
            limit_down = int((df["涨跌幅"].apply(lambda x: safe_float(x)) <= -9.9).sum())

        # 计算总成交额
        total_amount = 0.0
        if "成交额" in df.columns:
            total_amount = df["成交额"].apply(lambda x: safe_float(x)).sum() / 1e8  # 转为亿

        result = pd.DataFrame(
            {
                "指标": [
                    "总股票数",
                    "上涨家数",
                    "下跌家数",
                    "平盘家数",
                    "涨停家数(>=9.9%)",
                    "跌停家数(<=-9.9%)",
                    "总成交额(亿)",
                    "涨跌比",
                ],
                "数值": [
                    total,
                    up_count,
                    down_count,
                    flat_count,
                    limit_up,
                    limit_down,
                    round(total_amount, 2),
                    f"{up_count}:{down_count}" if down_count > 0 else f"{up_count}:0",
                ],
            }
        )

        return "## A 股市场宽度\n\n" + format_dataframe(result, max_rows=20)

    except Exception as e:
        return handle_error(func_name, e)


def get_north_flow() -> str:
    """获取北向资金（沪深港通）流向数据。

    返回最近几日的北向资金净买入数据。

    Returns:
        markdown 格式的北向资金流向表。
    """
    func_name = "get_north_flow"
    try:
        # 获取北向资金流入数据
        df = ak.stock_hsgt_north_net_flow_in_em(symbol="北上")

        if df is None or df.empty:
            # 尝试备用接口
            df = ak.stock_hsgt_north_net_flow_in_em(symbol="沪股通")

        if df is None or df.empty:
            return "**未获取到北向资金数据**"

        # 取最近 30 条
        df_display = df.tail(30) if len(df) > 30 else df

        # 重命名常见列
        col_map = {
            "日期": "日期",
            "当日资金流入": "当日流入(元)",
            "当日资金余额": "当日余额(元)",
            "历史资金净流入": "历史净流入(元)",
            "当日成交净买额": "当日净买额(元)",
        }
        rename_cols = {k: v for k, v in col_map.items() if k in df.columns}
        df_display = df_display.rename(columns=rename_cols)

        return "## 北向资金流向（最近 30 日）\n\n" + format_dataframe(df_display, max_rows=30)

    except Exception as e:
        return handle_error(func_name, e)
