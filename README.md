# A-Share Stock Monitor

这是一个简单的 A 股持仓监控程序，运行在 Linux 服务器上。它会每隔几秒钟获取一次股价，计算持仓占比，并在超出设定范围时发送通知。

此项目的部分代码片段（或：README 初稿）是在 **GitHub Copilot** 的协助下完成的。

## 功能

* **实时监控**: 每 5 秒（可配置）从新浪财经接口获取最新股价。
* **交易时间智能休眠**: 仅在周一至周五 09:30 - 15:00 运行，非交易时间自动休眠。
* **持仓占比检查**: 自动计算每只股票的市值占比，若超出 `min_percentage` 或 `max_percentage` 则触发警报。
* **REST API**: 提供 HTTP 接口用于查看和动态修改配置（已隐藏敏感信息 `send_key`）。
* **Web 管理界面**: 提供基于 React + Ant Design 的可视化管理后台。
* **通知扩展**: 在 `notifier.py` 中进行消息推送，默认使用 Server酱推送微信服务号消息。

## 安装与运行

### 后端服务

1. **安装依赖**:

   ```bash
   pip install -r requirements.txt
   ```
2. **运行程序**:

   ```bash
   python main.py                # 默认 info 级别
   python main.py --log-level error
   ```

   后端默认运行在 `http://localhost:8256`。

### 前端管理页面

前端代码位于 `Web/` 目录下。

**方式一：集成模式（推荐）**

将前端构建为静态文件。

1. **构建前端**:

   ```bash
   cd Web
   npm install
   npm run build
   ```

   构建完成后会生成 `Web/dist` 目录。
2. **启动后端**:

   ```bash
   cd ..
   python main.py
   ```

   直接访问 `http://localhost:8256` 即可使用管理界面。

**方式二：开发模式**

如果需要修改前端代码，可以独立运行前端开发服务器。

1. **运行开发服务器**:
   ```bash
   cd Web
   npm run dev
   ```

   访问终端显示的地址（通常是 `http://localhost:5173`）。

## API 使用

默认运行在 `http://localhost:8256`。

* **查看状态**: `GET /status`
* **查看当前配置**: `GET /config` (不包含 `send_key`)
* **更新配置**: `POST /config`
  * 全量更新配置（无需传入 `send_key`，后端会自动保留原有的 key）。
