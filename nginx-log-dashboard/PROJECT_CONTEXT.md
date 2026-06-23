# Nginx Log Dashboard 项目上下文快照

更新时间：2026-06-17  
用途：后续与本项目相关的任务，先读取本文件，避免重复读取大文件、浏览器长文档、完整 DOM 和历史日志。

## 项目定位

本项目是面向内网离线部署的 DMZ1 Nginx 日志可观测性看板。当前策略已经收敛为：只采集并展示 DMZ1 区 Nginx 日志，不再收集 DMZ1 以外区域日志。

项目表达重点：

- 基于 Nginx Request ID 的入口链路串联。
- 展示 DMZ1 网络边界层可观测信息。
- 支撑南北向入口排障、上游异常定位、边缘调度建议和治理效果验证。
- 不能夸大为完整微服务/中间件全链路追踪；当前是 DMZ1 边界追踪与下游关联锚点。

## 目录与关键文件

根目录：`I:\codex\projects\logsview\nginx-log-dashboard`

关键文件：

- `main.py`：FastAPI 服务端、API、WebSocket、demo 数据。
- `metrics.py`：DMZ1 指标聚合，60 秒窗口，最多 10000 条样本。
- `log_parser.py`：Nginx access log 解析，支持 key=value 扩展字段。
- `agent.py`：日志采集 agent，按批发送到服务端。
- `static/index.html`：单文件原生前端看板。
- `start.sh`：服务端 dashboard 启动脚本，环境变量在脚本顶部配置。
- `start_agent.sh`：agent 启动脚本，agent 环境变量外置到脚本顶部。
- `DEPLOY.md`：离线部署说明。
- `bundle_offline.py`：生成离线包。
- `dist/nginx-log-dashboard-offline.zip`：当前离线部署包。

不应优先读取：

- `pylib*` 目录：离线依赖，体积大，除非排查依赖版本问题。
- `local-server.log`、`refresh-test.log`：历史验证日志，非必要不读全文。
- `static/index.html` 全文：需要时用 `Select-String` 或按行局部读取。

## 当前功能状态

服务端：

- `GET /` 返回 `static/index.html`。
- `GET /api/metrics` 返回聚合指标。
- `POST /api/ingest` 接收 agent 批量日志，只接受 `zone=DMZ1`，其他区域忽略。
- `GET /api/traces/{request_id}` 查询同一 Request ID 记录。
- `WS /ws` 每 2 秒推送 metrics。
- `DEMO_MODE=1` 时启动 demo 数据线程。

已修复：

- 浏览器刷新 dashboard 时旧 WebSocket 关闭导致后台报错：
  - 报错类型：`websockets.exceptions.ConnectionClosedOK: received 1001 (going away)`
  - 修复位置：`main.py`
  - 修复方式：`from websockets.exceptions import ConnectionClosed`，并在 `websocket_endpoint` 中捕获 `(WebSocketDisconnect, ConnectionClosed)`。

前端：

- 已修复中文乱码。
- 已新增四个核心区域：
  - Request ID 链路瀑布
  - 网络边界性能归因
  - 边缘治理决策建议
  - 治理效果验证
- 请求表支持点击 Request ID，同步更新详情和链路瀑布。
- 点击事件已改为事件委托：`$("requests").onclick=...`，避免实时刷新导致行元素失效。
- 桌面与 390px 移动端验证过无横向溢出。

离线包：

- 当前包路径：`dist/nginx-log-dashboard-offline.zip`
- 当前 SHA256：`99194E5312EDD0E2B61605BD5787042338572C30B2231DA23A7AC1ABE4E4A4DB`

## 数据模型与展示字段

日志记录核心字段：

- `timestamp`
- `request_time`
- `upstream_time`
- `status`
- `url`
- `method`
- `source`
- `request_id`
- `remote_addr`
- `upstream`
- `zone`
- `agent_queue_pct`
- `agent_dropped`
- `sample_rate`
- `log_rate_bps`

当前 Nginx 日志解析支持四种 positional 格式：

1. 测试无 Request ID：
   `"$request" $status $body_bytes_sent $request_time $upstream_response_time "$referer" "$ua" "$xff" "$host"`
2. 测试有 Request ID：
   `"$request" $request_id $status $body_bytes_sent $request_time $upstream_response_time "$referer" "$ua" "$xff" "$host"`
3. 生产无 Request ID：
   `"$request" $status $request_length $body_bytes_sent $request_time "$referer" "$ua" "$xff"`
4. 生产有 Request ID：
   `"$request" $request_id $status $request_length $body_bytes_sent $request_time "$referer" "$ua" "$xff"`

解析器会通过 `"$request"` 后第一个 token 是否为 HTTP 状态码判断是否存在 Request ID，并通过后续字段数量和位置区分测试/生产格式。解析结果会带 `log_format`，取值包括：

- `test_without_request_id`
- `test_with_request_id`
- `production_without_request_id`
- `production_with_request_id`

`metrics.py` 当前聚合：

- overall：avg、p50、p95、p99、qps、error_rate、client_error_rate、request_id_coverage。
- nodes：按 `source` 聚合。
- upstreams：按 `upstream` 聚合。
- routes：按归一化 route 聚合。
- status_distribution。
- alerts。
- agents。
- recent_timeline。
- recent_requests。

注意：`agent.py` 中 `SAMPLE_RATE` 当前主要作为上报元数据，未真正执行抽样丢弃。生产大流量前如果继续强调采样能力，需要先实现真实采样、聚合或本地缓冲策略。

## 启动方式

Linux/内网部署：

```bash
./start.sh dashboard
./start_agent.sh
```

本地 Windows 开发：

```cmd
start_local.cmd
```

本地服务默认：

- URL：`http://127.0.0.1:8000/`
- `LOG_FILE_PATH=sample_access.log`
- `DEMO_MODE=1`

## 已验证事项

最近验证：

- Python 语法：用 `compile(...)` 方式检查，避免 `py_compile` 写入 `__pycache__` 权限问题。
- WebSocket 刷新修复：
  - 模拟 `ConnectionClosedOK(1001 going away)`：端点正常返回。
  - 浏览器连续刷新 5 次：后台日志无 `Exception in ASGI application`、无 `ConnectionClosedOK` traceback。
- API 活性：`GET /api/metrics` 正常。
- 前端四区域存在并渲染实时数据。

## 后续高价值改进

1. 真实采样与限流：
   - 在 agent 侧按 `SAMPLE_RATE` 真正抽样。
   - 错误、慢请求、低频接口可全量保留；健康 2xx 可采样。

2. 低资源服务端保护：
   - `MetricsCollector` 当前只保留内存窗口，适合轻量展示。
   - 如日志突增，需限制 ingest 单批大小、请求体大小和 agent 重试频率。

3. 更强 Request ID 机制表达：
   - Nginx log_format 建议增加：
     - `$request_id`
     - `$request_time`
     - `$upstream_response_time`
     - `$upstream_connect_time`
     - `$upstream_header_time`
     - `$upstream_addr`
     - `$upstream_status`
   - 当前 parser 还未完整解析 connect/header/status 等更细字段。

4. UI 可继续优化：
   - Request ID 瀑布目前基于 `request_time - upstream_time` 做边界耗时估计。
   - 若日志新增 connect/header/response 分段，可改为真实 Nginx upstream 阶段瀑布。

## 节省上下文约定

后续任务请优先执行：

1. 先读本文件：`PROJECT_CONTEXT.md`。
2. 只按需读取关键文件局部：
   - `Select-String`
   - `Get-Content -TotalCount`
   - `Get-Content | Select-Object -Skip ... -First ...`
   - `rg -n`
3. 不重复输出 Browser 完整 API 文档。
4. 如果 Browser 已初始化，直接复用现有 `browser`、`tab`。
5. 浏览器验证优先使用定向 `evaluate`，不要输出完整 `domSnapshot()`。
6. 不读取 `pylib*`、完整日志、完整 HTML，除非问题确实指向这些文件。
7. 打包只在用户需要部署包或修改影响部署结果时执行。
8. 中间回复保持一句话，最终只列变更、验证、路径和必要注意事项。

## Browser 使用注意

Browser skill 首次使用会强制读取完整 API 文档，token 消耗很高。优化方式：

- 同一线程只初始化一次。
- 初始化前检查变量是否存在：

```js
typeof browser !== "undefined"
```

- 后续只用定向检查，例如：

```js
await tab.playwright.evaluate(() => ({
  title: document.title,
  hasWaterfall: !!document.querySelector("#waterfall"),
  overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
}))
```

不要为了页面验证输出整页 DOM 或截图，除非用户明确要求视觉截图。
