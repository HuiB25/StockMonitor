import logging

import httpx
import config_manager

logger = logging.getLogger("StockMonitor")


async def send_alert(title: str, message: str):
    config = config_manager.get_config()

    payload = {"title": title, "desp": message}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://sctapi.ftqq.com/{config.settings.send_key}.send",
                data=payload,
                timeout=5.0,
            )

            response.raise_for_status()
            result = response.json()
    except httpx.RequestError as e:
        logger.error(f"通知发送网络错误: {e}")

    logger.info(f"ALERT: {message}")
