# A-Share Stock Monitor

这是一个简单的 A 股持仓监控程序，运行在 Linux 服务器上。它会每隔几秒钟获取一次股价，计算持仓占比，并在超出设定范围时发送通知。

此项目的部分代码片段（或：README 初稿）是在 **GitHub Copilot** 的协助下完成的。

## 功能

* **实时监控**: 每 5 秒（可配置）从新浪财经接口获取最新股价。
* **持仓占比检查**: 自动计算每只股票的市值占比，若超出 `min_percentage` 或 `max_percentage` 则触发警报。
* **REST API**: 提供 HTTP 接口用于查看和动态修改配置。
* **通知扩展**: 在 `notifier.py` 中进行消息推送，默认使用Server酱推送微信服务号消息。

## 安装与运行

1. **安装依赖**:

   ```bash
   pip install -r requirements.txt
   ```
2. **运行程序**:

   ```bash
   python main.py # 默认info级别
   python main.py --log-level error
   ```

## API 使用

默认运行在 `http://localhost:8000`。

* **查看当前配置**: `GET /config`
* **更新配置**: `POST /config`
  * 全量更新，传入整个config
