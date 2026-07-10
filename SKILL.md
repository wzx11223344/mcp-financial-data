# SKILL.md - 金融数据MCP服务器

## 概述

**名称**: mcp-financial-data  
**版本**: 1.0.0  
**描述**: 基于 MCP 协议的金融数据服务器，提供中国 A 股/基金/宏观经济/市场行情的实时数据工具  
**框架**: FastMCP + akshare  
**工具数量**: 19 个

## 安装

```bash
pip install -r requirements.txt
```

## 启动

```bash
python server.py
```

## MCP 配置

```json
{
  "mcpServers": {
    "financial-data": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
```

## 工具清单

### 股票 (stock_tools.py) - 6个

| 工具 | 参数 | 说明 |
|------|------|------|
| `get_stock_quote` | `symbol: str` | 实时行情 |
| `get_stock_history` | `symbol, start="", end="", period="daily"` | 历史K线 |
| `get_stock_financial` | `symbol: str` | 财务指标 |
| `get_stock_list` | `market="hs300"` | 成分股列表 |
| `get_top_gainers` | `count=20` | 涨幅榜 |
| `get_top_losers` | `count=20` | 跌幅榜 |

### 基金 (fund_tools.py) - 4个

| 工具 | 参数 | 说明 |
|------|------|------|
| `get_fund_list` | `fund_type="stock"` | 基金列表 |
| `get_fund_nav` | `fund_code: str` | 净值历史 |
| `get_fund_holdings` | `fund_code: str` | 重仓持仓 |
| `get_fund_performance` | `fund_code: str` | 业绩表现 |

### 宏观经济 (econ_tools.py) - 5个

| 工具 | 参数 | 说明 |
|------|------|------|
| `get_gdp_data` | 无 | GDP数据 |
| `get_cpi_data` | 无 | CPI数据 |
| `get_pmi_data` | 无 | PMI数据 |
| `get_money_supply` | 无 | 货币供应M0/M1/M2 |
| `get_fx_rate` | `currency="usd"` | 汇率数据 |

### 市场行情 (market_tools.py) - 4个

| 工具 | 参数 | 说明 |
|------|------|------|
| `get_index_data` | `symbol="sh000001"` | 指数行情 |
| `get_sector_performance` | 无 | 板块涨跌 |
| `get_market_breadth` | 无 | 市场宽度 |
| `get_north_flow` | 无 | 北向资金 |

## 参数说明

### 常用参数值

**股票代码 (symbol)**
- 6位数字: `600519`, `000001`, `002594`
- 带前缀: `sh600519`, `sz000001`

**市场标识 (market)**
- `hs300`: 沪深300
- `zz500`: 中证500
- `sz50`: 上证50
- `all`: 全A

**K线周期 (period)**
- `daily`: 日线
- `weekly`: 周线
- `monthly`: 月线

**基金类型 (fund_type)**
- `stock`: 股票型
- `mixed`: 混合型
- `bond`: 债券型
- `index`: 指数型
- `qdii`: QDII
- `etf`: ETF
- `lof`: LOF
- `all`: 全部

**货币代码 (currency)**
- `usd`: 美元
- `eur`: 欧元
- `jpy`: 日元
- `gbp`: 英镑
- `hkd`: 港元

**指数代码 (symbol)**
- `sh000001`: 上证指数
- `sz399001`: 深证成指
- `sz399006`: 创业板指
- `sh000688`: 科创50
- `sh000300`: 沪深300
- `sh000905`: 中证500
- `sh000016`: 上证50

## 返回格式

所有工具返回 markdown 格式字符串，例如：

```markdown
## 贵州茅台（600519）实时行情

| 项目 | 数值 |
|------|------|
| 股票代码 | 600519 |
| 最新价 | 1680.00 |
| 涨跌幅(%) | 2.35 |
| 成交额(元) | 3500000000 |
```

## 错误处理

- 网络超时: 返回友好提示建议重试
- 代码不存在: 返回未找到提示
- 接口变更: 返回 akshare 接口可能已变更的提示
- 所有错误以 markdown 格式返回，不会中断服务

## 依赖

- mcp (MCP SDK)
- akshare (>=1.10)
- pandas (>=2.0)
- tabulate (markdown表格渲染)
