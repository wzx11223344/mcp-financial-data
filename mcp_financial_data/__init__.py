"""金融数据 MCP 服务器包。

提供中国 A 股、基金、宏观经济、市场行情等金融数据工具，
基于 MCP (Model Context Protocol) 协议，使用 FastMCP 框架。

子模块:
    - stock_tools: 股票数据工具（行情/K线/财务/列表/涨跌幅榜）
    - fund_tools: 基金数据工具（列表/净值/持仓/业绩）
    - econ_tools: 宏观经济数据工具（GDP/CPI/PMI/货币供应/汇率）
    - market_tools: 市场行情工具（指数/板块/市场宽度/北向资金）
    - utils: 公共工具函数
"""

from .utils import format_dataframe, handle_error, normalize_symbol, safe_float, truncate_data

__version__ = "1.0.0"
__author__ = "mcp-financial-data"
__description__ = "金融数据MCP服务器 - 基于FastMCP和akshare"

__all__ = [
    "format_dataframe",
    "handle_error",
    "normalize_symbol",
    "safe_float",
    "truncate_data",
    "__version__",
]
