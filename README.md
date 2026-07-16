# 金融数据 MCP 服务器 (mcp-financial-data)

[![CI](https://github.com/wzx11223344/mcp-financial-data/actions/workflows/ci.yml/badge.svg)](https://github.com/wzx11223344/mcp-financial-data/actions/workflows/ci.yml)

基于 [MCP (Model Context Protocol)](https://modelcontextprotocol.io) 协议的金融数据服务器，使用 [FastMCP](https://github.com/jlowin/fastmcp) 框架构建，为 AI 客户端提供实时的中国 A 股 / 基金 / 宏观经济 / 市场行情数据工具。

## 功能特性

- **19 个金融数据工具**，覆盖四大领域
- 使用 [akshare](https://akshare.akfamily.xyz/) 获取真实金融数据
- 所有工具返回 markdown 格式字符串，适合 AI 客户端直接消费
- 完整的类型提示和 docstring，MCP 自动生成 JSON Schema
- 统一的错误处理，网络异常或接口变更时返回友好提示
- 自动数据截断，防止输出过大

## 项目结构

```
mcp-financial-data/
├── server.py                    # MCP Server 入口（FastMCP）
├── mcp_financial_data/
│   ├── __init__.py               # 包初始化
│   ├── stock_tools.py            # 股票数据工具（6个）
│   ├── fund_tools.py             # 基金数据工具（4个）
│   ├── econ_tools.py             # 宏观经济数据工具（5个）
│   ├── market_tools.py           # 市场行情工具（4个）
│   └── utils.py                  # 公共工具函数
├── README.md
├── SKILL.md
└── requirements.txt
```

## 工具列表

### 股票数据工具 (6个)

| 工具名 | 功能描述 |
|--------|----------|
| `get_stock_quote` | 获取股票实时行情（开高低收量额、PE/PB/市值） |
| `get_stock_history` | 获取历史 K 线（日/周/月，前复权） |
| `get_stock_financial` | 获取财务指标（ROE/PE/PB/营收/净利润） |
| `get_stock_list` | 获取股票列表（沪深300/中证500/上证50/全A） |
| `get_top_gainers` | 获取涨幅排行榜 |
| `get_top_losers` | 获取跌幅排行榜 |

### 基金数据工具 (4个)

| 工具名 | 功能描述 |
|--------|----------|
| `get_fund_list` | 获取基金列表（股票型/混合型/债券型/指数型/QDII/ETF/LOF） |
| `get_fund_nav` | 获取基金净值历史 |
| `get_fund_holdings` | 获取基金重仓股持仓 |
| `get_fund_performance` | 获取基金业绩（近1周/1月/3月/6月/1年/3年收益） |

### 宏观经济数据工具 (5个)

| 工具名 | 功能描述 |
|--------|----------|
| `get_gdp_data` | 获取中国 GDP 季度数据 |
| `get_cpi_data` | 获取中国 CPI 月度数据 |
| `get_pmi_data` | 获取中国 PMI 月度数据 |
| `get_money_supply` | 获取货币供应量（M0/M1/M2） |
| `get_fx_rate` | 获取汇率数据（美元/欧元/日元/英镑/港元） |

### 市场行情工具 (4个)

| 工具名 | 功能描述 |
|--------|----------|
| `get_index_data` | 获取指数行情（上证/深证/创业板/科创50/沪深300） |
| `get_sector_performance` | 获取板块涨跌幅排行 |
| `get_market_breadth` | 获取市场宽度（涨跌家数/涨停跌停/总成交额） |
| `get_north_flow` | 获取北向资金流向 |

## 安装

```bash
# 克隆项目
git clone <repo-url>
cd mcp-financial-data

# 安装依赖
pip install -r requirements.txt
```

## 配置 MCP 客户端

### Claude Desktop / Claude Code

在 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "financial-data": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/mcp-financial-data"
    }
  }
}
```

### 其他 MCP 客户端

```json
{
  "mcpServers": {
    "financial-data": {
      "command": "python",
      "args": ["/path/to/mcp-financial-data/server.py"]
    }
  }
}
```

## 使用示例

启动服务器后，AI 客户端会自动发现所有工具。示例对话：

- "查询贵州茅台的实时行情" → 调用 `get_stock_quote("600519")`
- "查看沪深300成分股" → 调用 `get_stock_list("hs300")`
- "今天涨幅前20的股票" → 调用 `get_top_gainers(20)`
- "基金161725的净值历史" → 调用 `get_fund_nav("161725")`
- "最新的GDP数据" → 调用 `get_gdp_data()`
- "上证指数今天怎么样" → 调用 `get_index_data("sh000001")`
- "北向资金最近流向" → 调用 `get_north_flow()`

## 技术栈

- **MCP Protocol**: `mcp` (Model Context Protocol SDK)
- **Server Framework**: FastMCP
- **Data Source**: akshare (免费开源金融数据接口库)
- **Data Processing**: pandas
- **Python**: 3.10+

## 开发

### 运行服务器

```bash
python server.py
```

### 验证语法

```bash
python -m py_compile server.py
python -m py_compile mcp_financial_data/*.py
```

### 添加新工具

1. 在对应的 `*_tools.py` 文件中实现工具函数
2. 在 `server.py` 中用 `@mcp.tool()` 装饰器注册
3. 确保有完整的类型提示和 docstring
4. 用 `py_compile` 验证语法

## 测试

运行单元测试：

```bash
pip install pytest flake8
pytest tests/ -v --tb=short
```

代码质量检查：

```bash
flake8 . --count --max-line-length=120 --statistics

## License

MIT
