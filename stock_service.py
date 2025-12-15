import httpx
import logging
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger("StockMonitor")


class StockService:
    def __init__(self):
        self.headers = {"Referer": "http://finance.sina.com.cn"}

    async def fetch_prices(self, codes: List[str]) -> Dict[str, float]:
        """
        从新浪财经获取股票当前价格
        """
        if not codes:
            return {}

        # 新浪接口支持一次请求多个，用逗号分隔
        codes_str = ",".join(codes)
        url = f"http://hq.sinajs.cn/list={codes_str}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                text = response.text

            prices = {}
            # 解析返回数据
            # 格式: var hq_str_sh600519="贵州茅台,1558.00,1560.00,1555.50,..."
            lines = text.strip().split("\n")
            for line in lines:
                if not line:
                    continue

                # 提取股票代码
                # var hq_str_sh600519="...
                parts = line.split("=")
                if len(parts) < 2:
                    continue

                code_part = parts[0]
                data_part = parts[1]

                code = code_part.split("_")[-1]  # 获取 sh600519

                # 提取价格
                # "贵州茅台,1558.00,1560.00,1555.50,..."
                data_values = data_part.strip('"').split(",")
                if len(data_values) > 3:
                    current_price = float(data_values[3])
                    # 如果停牌或未开盘，价格可能为 0，可以用昨收 (index 2) 代替，或者保持 0
                    if current_price == 0.0 and len(data_values) > 2:
                        current_price = float(data_values[2])

                    prices[code] = current_price

            return prices

        except Exception as e:
            logger.error(f"获取股价失败: {e}")
            return {}

    def calculate_portfolio(
        self, portfolio_config: List[Dict[str, Any]], current_prices: Dict[str, float]
    ):
        """
        计算持仓总市值和各股票占比
        """
        total_value = 0.0
        holdings = []

        # 1. 计算单只股票市值和总市值
        for item in portfolio_config:
            code = item["code"]
            shares = item["held_shares"]
            price = current_prices.get(code, 0.0)

            market_value = price * shares
            total_value += market_value

            holdings.append(
                {
                    "code": code,
                    "name": item.get("name", code),
                    "price": price,
                    "shares": shares,
                    "market_value": market_value,
                    "min_pct": item.get("min_percentage", 0),
                    "max_pct": item.get("max_percentage", 100),
                }
            )

        # 2. 计算百分比并检查
        alerts = []
        if total_value > 0:
            for holding in holdings:
                current_pct = (holding["market_value"] / total_value) * 100
                holding["current_pct"] = current_pct

                if current_pct < holding["min_pct"]:
                    alerts.append(
                        f"{holding['name']}({holding['code']}) 现价:{holding['price']} 占比:{current_pct:.4f}% < Min:{holding['min_pct']}%"
                    )
                elif current_pct > holding["max_pct"]:
                    alerts.append(
                        f"{holding['name']}({holding['code']}) 现价:{holding['price']} 占比:{current_pct:.4f}% > Max:{holding['max_pct']}%"
                    )

        return total_value, holdings, alerts
