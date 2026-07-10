#!/usr/bin/env python3
"""金融数据 MCP 服务器入口。

基于 FastMCP 框架，为 AI 客户端提供中国 A 股/基金/宏观经济/市场行情的
实时金融数据工具。

启动方式:
    python server.py

或通过 MCP 配置文件启动:
    {
        "mcpServers": {
            "financial-data": {
                "command": "python",
                "args": ["server.py"]
            }
        }
    }

工具总数: 19 个
    - 股票工具: 6 个 (行情/K线/财务/列表/涨幅榜/跌幅榜)
    - 基金工具: 4 个 (列表/净值/持仓/业绩)
    - 宏观经济: 5 个 (GDP/CPI/PMI/货币供应/汇率)
    - 市场行情: 4 个 (指数/板块/市场宽度/北向资金)
"""

from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from mcp_financial_data import stock_tools, fund_tools, econ_tools, market_tools

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp-financial-data")

# 创建 FastMCP 服务器实例
mcp = FastMCP("financial-data")


# ============================================================================
# 股票数据工具 (6个)
# ============================================================================


@mcp.tool()
def get_stock_quote(symbol: str) -> str:
    """获取 A 股股票实时行情。

    返回最新交易日的开盘价、最高价、最低价、收盘价、成交量、成交额、
    涨跌幅、市盈率、市净率、总市值等核心行情字段。

    Args:
        symbol: 股票代码，6 位数字，如 ``600519``（贵州茅台）、``000001``（平安银行）。
            支持带前缀格式如 ``sh600519``、``sz000001``。

    Returns:
        markdown 格式的实时行情表。
    """
    return stock_tools.get_stock_quote(symbol)


@mcp.tool()
def get_stock_history(
    symbol: str,
    start: str = "",
    end: str = "",
    period: str = "daily",
) -> str:
    """获取 A 股股票历史 K 线数据。

    支持日线、周线、月线三种周期。默认返回最近约 90 天的数据。

    Args:
        symbol: 股票代码，6 位数字，如 ``600519``。
        start: 开始日期，格式 ``YYYYMMDD``，如 ``20240101``。默认为最近 90 天前。
        end: 结束日期，格式 ``YYYYMMDD``。默认为今天。
        period: K 线周期，可选 ``daily``（日线）、``weekly``（周线）、``monthly``（月线）。

    Returns:
        markdown 格式的历史 K 线表，包含日期、开盘、收盘、最高、最低、成交量、成交额。
    """
    return stock_tools.get_stock_history(symbol, start, end, period)


@mcp.tool()
def get_stock_financial(symbol: str) -> str:
    """获取 A 股股票核心财务指标。

    返回最新报告期的 PE（动态/TTM）、PB、总市值、流通市值，以及
    营收、净利润、ROE、毛利率、净利率等关键财务指标。

    Args:
        symbol: 股票代码，6 位数字，如 ``600519``。

    Returns:
        markdown 格式的财务指标表。
    """
    return stock_tools.get_stock_financial(symbol)


@mcp.tool()
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
    return stock_tools.get_stock_list(market)


@mcp.tool()
def get_top_gainers(count: int = 20) -> str:
    """获取 A 股涨幅排行榜。

    返回当日涨幅最高的股票列表。

    Args:
        count: 返回数量，默认 20，最大 100。

    Returns:
        markdown 格式的涨幅榜表，含代码、名称、最新价、涨跌幅、成交额。
    """
    return stock_tools.get_top_gainers(count)


@mcp.tool()
def get_top_losers(count: int = 20) -> str:
    """获取 A 股跌幅排行榜。

    返回当日跌幅最大的股票列表。

    Args:
        count: 返回数量，默认 20，最大 100。

    Returns:
        markdown 格式的跌幅榜表，含代码、名称、最新价、涨跌幅、成交额。
    """
    return stock_tools.get_top_losers(count)


# ============================================================================
# 基金数据工具 (4个)
# ============================================================================


@mcp.tool()
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
    return fund_tools.get_fund_list(fund_type)


@mcp.tool()
def get_fund_nav(fund_code: str) -> str:
    """获取基金净值历史数据。

    返回指定基金的单位净值和累计净值历史记录。

    Args:
        fund_code: 基金代码，如 ``000001``（华夏成长）、``161725``（招商中证白酒）。

    Returns:
        markdown 格式的基金净值历史表。
    """
    return fund_tools.get_fund_nav(fund_code)


@mcp.tool()
def get_fund_holdings(fund_code: str) -> str:
    """获取基金持仓数据。

    返回指定基金的重仓股列表及持仓比例。

    Args:
        fund_code: 基金代码，如 ``161725``。

    Returns:
        markdown 格式的基金持仓表，含股票代码、股票名称、持仓占比等。
    """
    return fund_tools.get_fund_holdings(fund_code)


@mcp.tool()
def get_fund_performance(fund_code: str) -> str:
    """获取基金业绩表现数据。

    返回指定基金的近 1 周、近 1 月、近 3 月、近 6 月、近 1 年、
    近 3 年等各阶段收益率。

    Args:
        fund_code: 基金代码，如 ``161725``。

    Returns:
        markdown 格式的基金业绩表。
    """
    return fund_tools.get_fund_performance(fund_code)


# ============================================================================
# 宏观经济数据工具 (5个)
# ============================================================================


@mcp.tool()
def get_gdp_data() -> str:
    """获取中国 GDP 数据。

    返回最近几年的 GDP 季度数据，包括 GDP 总量、同比增长率等。

    Returns:
        markdown 格式的 GDP 数据表。
    """
    return econ_tools.get_gdp_data()


@mcp.tool()
def get_cpi_data() -> str:
    """获取中国 CPI（居民消费价格指数）数据。

    返回最近几年的月度 CPI 数据，包括同比、环比涨跌幅。

    Returns:
        markdown 格式的 CPI 数据表。
    """
    return econ_tools.get_cpi_data()


@mcp.tool()
def get_pmi_data() -> str:
    """获取中国 PMI（采购经理指数）数据。

    返回最近几年的月度 PMI 数据，包括制造业和非制造业 PMI。

    Returns:
        markdown 格式的 PMI 数据表。
    """
    return econ_tools.get_pmi_data()


@mcp.tool()
def get_money_supply() -> str:
    """获取中国货币供应量数据（M0/M1/M2）。

    返回最近几年的月度货币供应量数据，包括 M0、M1、M2 的绝对值及同比增速。

    Returns:
        markdown 格式的货币供应量表。
    """
    return econ_tools.get_money_supply()


@mcp.tool()
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
    return econ_tools.get_fx_rate(currency)


# ============================================================================
# 市场行情工具 (4个)
# ============================================================================


@mcp.tool()
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
    return market_tools.get_index_data(symbol)


@mcp.tool()
def get_sector_performance() -> str:
    """获取 A 股板块涨跌幅排行。

    返回当日行业板块的涨跌幅排名。

    Returns:
        markdown 格式的板块涨跌幅表。
    """
    return market_tools.get_sector_performance()


@mcp.tool()
def get_market_breadth() -> str:
    """获取 A 股市场宽度数据。

    返回当日全市场的涨跌家数、涨停跌停数量、总成交额等市场宽度指标。

    Returns:
        markdown 格式的市场宽度表。
    """
    return market_tools.get_market_breadth()


@mcp.tool()
def get_north_flow() -> str:
    """获取北向资金（沪深港通）流向数据。

    返回最近 30 日的北向资金净买入数据。

    Returns:
        markdown 格式的北向资金流向表。
    """
    return market_tools.get_north_flow()


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    logger.info("启动金融数据 MCP 服务器...")
    logger.info("已注册 19 个工具: 股票(6) + 基金(4) + 宏观(5) + 市场(4)")
    mcp.run()
