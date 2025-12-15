import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, time

from fastapi import FastAPI

from stock_service import StockService
from notifier import send_alert
import config_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("StockMonitor")

# 全局变量
stock_service = StockService()
monitor_task = None


async def monitor_loop():
    logger.info("监控循环已启动")
    while True:
        try:
            # 交易时间检查: 周一至周五 09:30 - 15:00
            now = datetime.now()
            if now.weekday() > 4 or not (time(9, 30) <= now.time() <= time(15, 0)):
                await asyncio.sleep(60)
                continue

            current_config = config_manager.get_config()
            if not current_config:
                await asyncio.sleep(1)
                continue

            interval = current_config.settings.refresh_interval_seconds

            # 1. 获取所有股票代码
            codes = [item.code for item in current_config.portfolio]

            if codes:
                # 2. 获取价格
                prices = await stock_service.fetch_prices(codes)

                # 3. 计算和检查
                total_val, holdings, alerts = stock_service.calculate_portfolio(
                    [item.model_dump() for item in current_config.portfolio], prices
                )

                msg = "【持仓详情】\n\n" + "\n\n".join(
                    [
                        f"{h['name']}({h['code']}): 价格 {h['price']:.4f}, 持股 {h['shares']}, 市值 {h['market_value']:.4f}, 占比 {h.get('current_pct',0):.4f}%"
                        for h in holdings
                    ]
                )

                # logger.info(
                #     f"当前总市值: {total_val:.4f}, 检查完成. 警报数: {len(alerts)}\n{msg}"
                # )

                # 4. 发送警报
                if current_config.settings.notification_enabled and alerts:
                    msg = "【调仓提醒】\n\n" + "\n\n".join(alerts) + "\n\n" + msg
                    await send_alert("【调仓提醒】", msg)
                    await asyncio.sleep(
                        current_config.settings.alert_interval_seconds
                    )  # 警报间隔

            await asyncio.sleep(interval)

        except asyncio.CancelledError:
            logger.info("监控循环被取消")
            break
        except Exception as e:
            logger.error(f"监控循环发生错误: {e}")
            await asyncio.sleep(current_config.settings.alert_interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时加载配置
    config_manager.load_config()
    # 启动后台任务
    global monitor_task
    monitor_task = asyncio.create_task(monitor_loop())
    yield
    # 关闭时清理
    if monitor_task:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan, title="A-Share Stock Monitor")


@app.get("/")
async def root():
    return {"status": "running", "message": "Stock Monitor is active"}


@app.get("/config", response_model=config_manager.ConfigModel)
async def get_config_api():
    return config_manager.get_config()


@app.post("/config", response_model=config_manager.ConfigModel)
async def update_config_api(new_config: config_manager.ConfigModel):
    config_manager.set_config(new_config)
    logger.info("配置已通过 API 更新")
    return config_manager.get_config()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8256)
