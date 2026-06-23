# DMZ1 Nginx Dashboard 离线部署

## 部署范围

当前版本只采集 DMZ1 区 Nginx access log：

- Dashboard 只接收 `zone=DMZ1` 的数据。
- 每台 DMZ1 Nginx 服务器运行一个 Agent。
- 不采集微服务网关、应用区和微服务节点日志。
- Dashboard 展示节点、upstream、路由、状态码、告警、Request ID
  和 Agent 采集健康。

目标环境：

- 麒麟 V10 ARM64/aarch64
- Python 3.7.9
- 完全隔离互联网

## 离线包

只传输：

```text
dist/nginx-log-dashboard-offline.zip
```

解压：

```bash
unzip nginx-log-dashboard-offline.zip
cd nginx-log-dashboard
chmod +x start.sh
chmod +x start_agent.sh
```

依赖位于 `pylib_py37/`，均为 Python 通用文件，不包含平台原生二进制。

## Shell 配置

Dashboard 通过 `start.sh` 启动，Agent 通过 `start_agent.sh` 启动。
两类环境变量分别放在对应脚本顶部，不需要在命令行手工 `export`。

### Dashboard 配置

在中心服务器编辑：

```bash
vi start.sh
```

修改：

```bash
PYTHON_BIN="/usr/bin/python3"
INGEST_TOKEN="change-this-token"
POLL_INTERVAL="0.5"

DASHBOARD_HOST="0.0.0.0"
DASHBOARD_PORT="8000"
DASHBOARD_LOG_FILE="sample_access.log"
DASHBOARD_DEMO_MODE="0"
```

生产环境必须保持：

```bash
DASHBOARD_DEMO_MODE="0"
```

### Agent 配置

在每台 DMZ1 Nginx 服务器编辑独立的 `start_agent.sh`：

```bash
vi start_agent.sh
```

修改脚本顶部：

```bash
PYTHON_BIN="/usr/bin/python3"
ZONE_NAME="DMZ1"
SOURCE_NAME="dmz1-nginx-01"
LOG_FILE_PATH="/var/log/nginx/access.log"

DASHBOARD_URL="http://中心服务器IP:8000"
INGEST_TOKEN="change-this-token"

SAMPLE_RATE="0.01"
BATCH_SIZE="500"
FLUSH_INTERVAL="2.0"
POLL_INTERVAL="0.5"
QUEUE_SIZE="100000"
```

不同节点必须使用不同的 `SOURCE_NAME`：

```text
dmz1-nginx-01
dmz1-nginx-02
dmz1-nginx-03
```

Dashboard 与所有 Agent 的 `INGEST_TOKEN` 必须一致。

## 启动

先在 Dashboard 服务器执行自检：

```bash
python3 deploy_offline.py
```

确认输出包含：

```text
后端依赖 : OK
前端资源 : OK
```

启动 Dashboard：

```bash
./start.sh dashboard
```

启动每台 Agent：

```bash
chmod +x start_agent.sh
./start_agent.sh
```

脚本启动时会打印实际使用的节点名、日志路径、监听地址和采样率。

## Nginx 日志格式

当前解析器兼容四种格式。

测试环境无 Request ID：

```nginx
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
    '$status $body_bytes_sent $request_time $upstream_response_time "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for" "$host"';
```

测试环境有 Request ID：

```nginx
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
    '$request_id $status $body_bytes_sent $request_time $upstream_response_time "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for" "$host"';
```

生产环境无 Request ID：

```nginx
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
    '$status $request_length $body_bytes_sent $request_time "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for"';
```

生产环境有 Request ID：

```nginx
log_format main '$remote_addr - $remote_user [$time_local] "$request" '
    '$request_id $status $request_length $body_bytes_sent $request_time "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for"';
```

如果已有上游透传 ID，建议优先使用请求头中的 ID，否则由 Nginx 生成：

```nginx
map $http_x_request_id $global_request_id {
    default $http_x_request_id;
    ""      $request_id;
}

proxy_set_header X-Request-ID $global_request_id;
```

此时把上述 `$request_id` 替换为 `$global_request_id`。

验证并重载：

```bash
nginx -t
systemctl reload nginx
```

## 验证

Dashboard 服务器：

```bash
curl http://127.0.0.1:8000/api/debug
curl http://127.0.0.1:8000/api/metrics
```

浏览器访问：

```text
http://Dashboard服务器IP:8000/
```

## systemd

Dashboard：

```ini
[Unit]
Description=DMZ1 Nginx Dashboard
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/nginx-log-dashboard
ExecStart=/opt/nginx-log-dashboard/start.sh dashboard
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Agent：

```ini
[Unit]
Description=DMZ1 Nginx Log Agent
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/nginx-log-dashboard
ExecStart=/opt/nginx-log-dashboard/start_agent.sh
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启用：

```bash
systemctl daemon-reload
systemctl enable --now dmz1-dashboard
# 或
systemctl enable --now dmz1-agent
```

## 故障排查

日志不可读：

```bash
ls -l /var/log/nginx/access.log
```

端口检查：

```bash
ss -lntp | grep 8000
```

Dashboard 连通性：

```bash
curl http://中心服务器IP:8000/api/debug
```

修改 `start.sh` 后重启对应 systemd 服务即可使环境配置生效。

## Background start/stop scripts

When starting the dashboard from an SSH session, use the background scripts instead of running the foreground command directly:

```bash
chmod +x start.sh start_server.sh stop_server.sh
./start_server.sh
```

The dashboard process is detached with `nohup` and `setsid` when available, so closing the SSH window or session will not stop it.

Runtime files:

```text
run/dashboard.pid
logs/dashboard.log
```

Stop the dashboard:

```bash
./stop_server.sh
```
