import json
import logging
import os
from typing import List, Optional
from pydantic import BaseModel

logger = logging.getLogger("StockMonitor")

CONFIG_FILE = "config.json"


# Pydantic 模型
class PortfolioItem(BaseModel):
    code: str
    name: str
    held_shares: int
    min_percentage: float
    max_percentage: float
    net_value: Optional[float] = None


class Settings(BaseModel):
    refresh_interval_seconds: int
    alert_interval_seconds: int
    notification_enabled: bool
    send_key: str = ""


class SettingsPublic(BaseModel):
    refresh_interval_seconds: int
    alert_interval_seconds: int
    notification_enabled: bool


class ConfigModel(BaseModel):
    settings: Settings
    portfolio: List[PortfolioItem]


class ConfigModelPublic(BaseModel):
    settings: SettingsPublic
    portfolio: List[PortfolioItem]


# 全局变量
current_config: Optional[ConfigModel] = None


def load_config():
    global current_config
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                current_config = ConfigModel(**data)
        else:
            # 默认配置
            current_config = ConfigModel(
                settings=Settings(
                    refresh_interval_seconds=5, notification_enabled=True
                ),
                portfolio=[],
            )
            save_config()
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        # Fallback
        current_config = ConfigModel(
            settings=Settings(refresh_interval_seconds=5, notification_enabled=True),
            portfolio=[],
        )


def save_config():
    global current_config
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(current_config.model_dump_json(indent=2))
    except Exception as e:
        logger.error(f"保存配置失败: {e}")


def get_config() -> Optional[ConfigModel]:
    return current_config


def set_config(new_config: ConfigModel):
    global current_config
    current_config = new_config
    save_config()
