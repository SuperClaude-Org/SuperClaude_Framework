(function () {
  const HTTP_SERVER_ERROR = 500;
  const HTTP_CLIENT_ERROR = 400;
  const HTTP_GATEWAY_TIMEOUT = 504;
  const SLOW_REQUEST_SECONDS = 1;
  const TIMEOUT_REQUEST_SECONDS = 3;
  const IMBALANCED_TRAFFIC_SHARE = 0.45;
  const REQUEST_ID_COVERAGE_WARN = 0.99;
  const SEARCH_DEBOUNCE_MS = 250;
  const WS_RECONNECT_BASE_MS = 1000;
  const WS_RECONNECT_MAX_MS = 15000;
  const DEFAULT_STATE = {
    nodes: [],
    upstreams: [],
    routes: [],
    agents: [],
    alerts: [],
    recent_requests: [],
    recent_timeline: [],
    status_distribution: [],
  };

  let state = { ...DEFAULT_STATE };
  let selectedId = '';
  let reconnectTimer = null;
  let reconnectAttempt = 0;
  const scriptPath = new URL(document.currentScript.src).pathname;
  const appBasePath = scriptPath.endsWith('/static/index.js')
    ? scriptPath.slice(0, -'/static/index.js'.length)
    : '';
  const appPath = (path) => `${appBasePath}${path}`;

  const $ = (id) => document.getElementById(id);
  const esc = (value) =>
    String(value ?? '').replace(/[&<>"']/g, (char) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    }[char]));
  const ms = (value) => (Number(value || 0) * 1000).toFixed(1);
  const pct = (value) => (Number(value || 0) * 100).toFixed(1);
  const fmtBytes = (value) => (
    value >= 1048576
      ? `${(value / 1048576).toFixed(1)} MB/s`
      : `${(value / 1024).toFixed(0)} KB/s`
  );
  const debounce = (fn, delay) => {
    let timer = null;
    return (...args) => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => fn(...args), delay);
    };
  };

  function cls(value) {
    return value === 'critical' ? 'critical' : value === 'warning' ? 'warning' : 'healthy';
  }

  function statusText(value) {
    return value === 'critical' ? '异常' : value === 'warning' ? '关注' : '健康';
  }

  function avg(items, key) {
    return items.length ? items.reduce((sum, item) => sum + Number(item[key] || 0), 0) / items.length : 0;
  }

  function render(data) {
    state = { ...DEFAULT_STATE, ...data };
    $('qps').textContent = Number(state.qps || 0).toFixed(1);
    $('coverage').textContent = pct(state.request_id_coverage);
    $('p95').textContent = ms(state.p95);
    $('e5').textContent = pct(state.error_rate);
    $('nodeCount').textContent = state.node_count || 0;
    $('upCount').textContent = state.upstream_count || 0;
    renderCore();
    renderNodes();
    renderUpstreams();
    renderRoutes();
    renderAgents();
    renderAlerts();
    renderStatus();
    renderRequests();
    renderChart();
  }

  function selectedRequest() {
    const list = state.recent_requests || [];
    let selected = list.find((item) => item.request_id === selectedId);
    if (selected) return selected;
    selected = list.slice().reverse().find((item) => item.status >= HTTP_SERVER_ERROR || item.request_time >= SLOW_REQUEST_SECONDS) || list[list.length - 1];
    if (selected) selectedId = selected.request_id;
    return selected;
  }

  function renderCore() {
    renderWaterfall();
    renderBoundary();
    renderDecisions();
    renderVerification();
  }

  function renderWaterfall() {
    const request = selectedRequest();
    if (!request) {
      $('waterfallSummary').innerHTML = '<span class="empty">暂无 Request ID 链路数据</span>';
      $('waterfall').innerHTML = '';
      return;
    }

    const total = Math.max(Number(request.request_time || 0), 0.001);
    const upstream = Math.min(total, Number(request.upstream_time || 0));
    const edge = Math.max(0, total - upstream);
    const level = request.status >= HTTP_SERVER_ERROR ? 'critical' : total >= SLOW_REQUEST_SECONDS ? 'warning' : 'healthy';
    const edgeAccept = Math.min(edge, 0.005);
    const rows = [
      ['入口接收', request.source || 'DMZ1 Nginx', edgeAccept, 'edge'],
      ['边界处理', '路由、鉴权、转发开销', Math.max(0, edge - edgeAccept), 'edge'],
      ['上游响应', request.upstream || '未记录', upstream, request.status >= HTTP_SERVER_ERROR ? 'error' : 'upstream'],
    ];

    $('waterfallSummary').innerHTML = `<span><b>${esc(request.request_id || '-')}</b> · ${esc(`${request.method || ''} ${request.url || ''}`)}</span><span class="${level}">${request.status} · ${ms(total)}ms</span>`;
    $('waterfall').innerHTML = rows.map((row) => `<div class="wf-row"><div class="wf-label">${row[0]}<small>${esc(row[1])}</small></div><div class="wf-track"><div class="wf-fill ${row[3]}" style="width:${Math.max(1, row[2] / total * 100)}%"></div></div><div class="wf-time">${ms(row[2])}ms</div></div>`).join('');
  }

  function renderBoundary() {
    const requests = state.recent_requests || [];
    const total = avg(requests, 'request_time');
    const upstream = avg(requests, 'upstream_time');
    const edge = Math.max(0, total - upstream);
    const ratio = total ? upstream / total : 0;
    const timeout = requests.filter((item) => item.status === HTTP_GATEWAY_TIMEOUT || item.request_time >= TIMEOUT_REQUEST_SECONDS).length;
    const tiles = [
      ['平均总耗时', `${ms(total)}ms`, '客户端到 DMZ1 再到上游'],
      ['边界自身开销', `${ms(edge)}ms`, '总耗时减去上游响应'],
      ['上游耗时占比', `${pct(ratio)}%`, '识别瓶颈是否位于后端'],
      ['超时请求', `${timeout} 条`, '504 或总耗时超过 3 秒'],
    ];
    const parts = [
      ['Nginx 边界', edge, total ? edge / total : 0],
      ['Upstream', upstream, ratio],
    ];

    $('boundaryMetrics').innerHTML = tiles.map((item) => `<div class="metric-tile"><small>${item[0]}</small><strong>${item[1]}</strong><p>${item[2]}</p></div>`).join('');
    $('attribution').innerHTML = parts.map((item) => `<div class="attribution-row"><span>${item[0]}</span><div class="bar"><i style="width:${pct(item[2])}%"></i></div><b>${ms(item[1])}ms</b></div>`).join('');
  }

  function renderDecisions() {
    const items = (state.upstreams || [])
      .filter((item) => item.status !== 'healthy')
      .slice(0, 3)
      .map((item) => ({
        level: item.status,
        title: item.status === 'critical' ? '建议隔离异常上游' : '建议降低上游权重',
        detail: `${item.name} · P95 ${ms(item.p95)}ms · 5xx ${pct(item.error_rate)}% · 超时 ${item.timeouts}`,
        action: item.status === 'critical' ? '隔离候选' : '降权候选',
      }));

    const uneven = (state.nodes || []).find((item) => item.share > IMBALANCED_TRAFFIC_SHARE);
    if (uneven) {
      items.push({
        level: 'warning',
        title: '建议校正入口流量分配',
        detail: `${uneven.name} 承载 ${pct(uneven.share)}% 流量，超过单节点 45% 关注线`,
        action: '权重检查',
      });
    }

    if ((state.request_id_coverage || 0) < REQUEST_ID_COVERAGE_WARN) {
      items.push({
        level: 'critical',
        title: '补齐 Request ID 生成与透传',
        detail: `当前覆盖率 ${pct(state.request_id_coverage)}%，无法可靠串联全部边界请求`,
        action: '配置核查',
      });
    }

    if (!items.length) {
      items.push({
        level: 'healthy',
        title: '当前无需调整边缘策略',
        detail: '节点、上游和 Request ID 覆盖率均处于健康范围，继续观察实时窗口',
        action: '保持现状',
      });
    }

    $('decisions').innerHTML = items.slice(0, 4).map((item) => `<div class="decision ${item.level}"><i class="decision-dot"></i><div><div class="decision-title">${item.title}</div><div class="decision-detail">${esc(item.detail)}</div></div><span class="decision-action">${item.action}</span></div>`).join('');
  }

  function segmentStats(items) {
    const p95s = items.map((item) => Number(item.p95_time || 0)).sort((left, right) => left - right);
    const qps = avg(items, 'qps');
    const errors = items.reduce((sum, item) => sum + Number(item.errors || 0), 0);
    const requests = items.reduce((sum, item) => sum + Number(item.qps || 0), 0);
    return {
      p95: p95s.length ? p95s[Math.floor((p95s.length - 1) * 0.95)] : 0,
      qps,
      error: requests ? errors / requests : 0,
    };
  }

  function renderVerification() {
    const timeline = state.recent_timeline || [];
    const midpoint = Math.max(1, Math.floor(timeline.length / 2));
    const before = segmentStats(timeline.slice(0, midpoint));
    const after = segmentStats(timeline.slice(midpoint));
    const metrics = [
      ['P95', before.p95, after.p95, 'time'],
      ['5xx', before.error, after.error, 'pct'],
      ['吞吐', before.qps, after.qps, 'qps'],
    ];

    $('verification').innerHTML = metrics.map((metric) => {
      const lowerIsBetter = metric[0] !== '吞吐';
      const delta = metric[1] ? ((metric[2] - metric[1]) / metric[1]) : 0;
      const good = lowerIsBetter ? delta <= 0 : delta >= -0.1;
      const format = metric[3] === 'time'
        ? (value) => `${(value * 1000).toFixed(0)}ms`
        : metric[3] === 'pct'
          ? (value) => `${(value * 100).toFixed(1)}%`
          : (value) => value.toFixed(1);
      return `<div class="verify-item"><div class="verify-name">${metric[0]}</div><div class="verify-values"><span>${format(metric[1])}</span><b>→</b><strong>${format(metric[2])}</strong></div><div class="delta ${good ? 'healthy' : 'warning'}">${delta >= 0 ? '+' : ''}${pct(delta)}%</div></div>`;
    }).join('');

    const pDelta = before.p95 ? (after.p95 - before.p95) / before.p95 : 0;
    const eDelta = before.error ? (after.error - before.error) / before.error : 0;
    const level = pDelta > 0.2 || eDelta > 0.2 ? 'critical' : pDelta > 0.05 || eDelta > 0.05 ? 'warning' : 'healthy';
    const text = level === 'healthy'
      ? '后半窗口性能稳定或改善，可继续保持当前策略。'
      : level === 'warning'
        ? '后半窗口出现轻微退化，建议继续观察并核对异常 Request ID。'
        : '后半窗口延迟或错误明显恶化，建议暂停扩流并检查熔断候选。';
    $('verdict').className = `verdict ${level}`;
    $('verdict').innerHTML = `<strong>窗口结论：</strong>${text}`;
  }

  function renderNodes() {
    $('nodes').innerHTML = (state.nodes || []).map((item) => `<tr><td class="name">${esc(item.name)}</td><td>${pct(item.share)}%<div class="bar"><i style="width:${pct(item.share)}%"></i></div></td><td>${Number(item.qps || 0).toFixed(2)}</td><td>${ms(item.p95)}ms</td><td class="${item.error_rate ? 'critical' : 'healthy'}">${pct(item.error_rate)}%</td><td class="${cls(item.status)}">${statusText(item.status)}</td></tr>`).join('') || empty(6);
  }

  function renderUpstreams() {
    $('upstreams').innerHTML = (state.upstreams || []).map((item) => `<tr><td class="name">${esc(item.name)}</td><td>${item.requests}</td><td>${ms(item.p95)}ms</td><td class="${item.timeouts ? 'warning' : ''}">${item.timeouts}</td><td class="${item.error_rate ? 'critical' : 'healthy'}">${pct(item.error_rate)}%</td><td class="${cls(item.status)}">${statusText(item.status)}</td></tr>`).join('') || empty(6);
  }

  function renderRoutes() {
    $('routes').innerHTML = (state.routes || []).map((item) => `<tr><td class="route" title="${esc(item.route)}">${esc(item.route)}</td><td>${item.requests}</td><td class="${item.p95 >= SLOW_REQUEST_SECONDS ? 'warning' : ''}">${ms(item.p95)}ms</td><td>${ms(item.max)}ms</td><td class="${item.errors ? 'critical' : 'healthy'}">${item.errors}</td></tr>`).join('') || empty(5);
  }

  function renderAgents() {
    $('agents').innerHTML = (state.agents || []).map((item) => `<div class="agent"><div class="agent-title"><span class="name">${esc(item.name)}</span><span class="${item.online ? 'healthy' : 'critical'}">${item.online ? '在线' : '离线'}</span></div><div class="agent-data"><span>数据延迟<b>${Number(item.delay || 0).toFixed(1)}s</b></span><span>队列水位<b>${Number(item.queue_pct || 0).toFixed(0)}%</b></span><span>采样率<b>${pct(item.sample_rate)}%</b></span><span>日志速率<b>${fmtBytes(item.log_rate_bps)}</b></span><span>丢弃记录<b class="${item.dropped ? 'critical' : ''}">${item.dropped}</b></span></div></div>`).join('') || '<div class="empty">暂无 Agent 数据</div>';
  }

  function renderAlerts() {
    const alerts = state.alerts || [];
    $('alertCount').textContent = `${alerts.length} 条`;
    $('alerts').innerHTML = alerts.map((item) => `<div class="alert ${cls(item.level)}"><strong>${esc(item.type)}</strong><div><strong>${esc(item.target)}</strong><br><span>${esc(item.detail)}</span></div><span class="${cls(item.level)}">${item.level === 'critical' ? '高' : '中'}</span></div>`).join('') || '<div class="empty healthy">当前无告警</div>';
  }

  function renderStatus() {
    const data = state.status_distribution || [];
    const max = Math.max(1, ...data.map((item) => item.count));
    const colors = {
      '2xx': 'var(--green)',
      '3xx': 'var(--blue)',
      '4xx': 'var(--amber)',
      '5xx': 'var(--red)',
    };
    $('statusBars').innerHTML = data.map((item) => `<div class="status-col"><div style="height:${item.count / max * 130}px;background:${colors[item.name] || 'var(--muted)'}"></div><strong>${item.count}</strong>${item.name}</div>`).join('');
  }

  function filtered() {
    const query = $('search').value.trim().toLowerCase();
    return (state.recent_requests || [])
      .slice()
      .reverse()
      .filter((item) => !query || [item.request_id, item.url, item.remote_addr, item.source, item.upstream].join(' ').toLowerCase().includes(query));
  }

  function renderRequests() {
    $('requests').innerHTML = filtered().map((item) => `<tr data-id="${esc(item.request_id)}"><td>${new Date(item.timestamp * 1000).toLocaleTimeString('zh-CN', { hour12: false })}</td><td class="rid" title="${esc(item.request_id)}">${esc(item.request_id || '-')}</td><td>${esc(item.source)}</td><td>${esc(item.remote_addr || '-')}</td><td class="route">${esc(`${item.method || ''} ${item.url || ''}`)}</td><td class="name">${esc(item.upstream || '-')}</td><td class="${item.request_time >= SLOW_REQUEST_SECONDS ? 'warning' : ''}">${ms(item.request_time)}ms</td><td>${ms(item.upstream_time)}ms</td><td class="${item.status >= HTTP_SERVER_ERROR ? 'critical' : item.status >= HTTP_CLIENT_ERROR ? 'warning' : 'healthy'}">${item.status}</td></tr>`).join('') || empty(9);
  }

  function showDetail(id) {
    const request = (state.recent_requests || []).slice().reverse().find((item) => item.request_id === id);
    if (!request) return;
    selectedId = id;
    const fields = [
      ['Request ID', request.request_id],
      ['时间', new Date(request.timestamp * 1000).toLocaleString()],
      ['Nginx 节点', request.source],
      ['客户端 IP', request.remote_addr],
      ['请求', `${request.method || ''} ${request.url || ''}`],
      ['Upstream', request.upstream || '-'],
      ['总耗时', `${ms(request.request_time)}ms`],
      ['上游耗时', `${ms(request.upstream_time)}ms`],
      ['状态码', request.status],
    ];
    $('detail').className = 'request-detail show';
    $('detail').innerHTML = fields.map((field) => `<div class="detail-item"><small>${field[0]}</small><span>${esc(field[1])}</span></div>`).join('');
    renderWaterfall();
    window.scrollTo({ top: $('waterfall').getBoundingClientRect().top + window.scrollY - 120, behavior: 'smooth' });
  }

  function renderChart() {
    const svg = $('chart');
    const rect = svg.getBoundingClientRect();
    const width = Math.max(rect.width, 300);
    const height = Math.max(rect.height, 200);
    const data = state.recent_timeline || [];
    const avgTimes = data.map((item) => item.avg_time * 1000);
    const p95Times = data.map((item) => item.p95_time * 1000);
    const max = Math.max(100, ...avgTimes, ...p95Times);
    const left = 38;
    const top = 10;
    const right = 8;
    const bottom = 22;
    const plotWidth = width - left - right;
    const plotHeight = height - top - bottom;
    const path = (values) => values.map((value, index) => `${index ? 'L' : 'M'}${(left + (values.length === 1 ? plotWidth / 2 : index * plotWidth / (values.length - 1))).toFixed(1)} ${(top + plotHeight - value / max * plotHeight).toFixed(1)}`).join(' ');
    let grid = '';
    for (let index = 0; index < 5; index += 1) {
      const y = top + index * plotHeight / 4;
      grid += `<line class="gridline" x1="${left}" y1="${y}" x2="${width - right}" y2="${y}"/><text class="axis" x="2" y="${y + 3}">${Math.round(max - index * max / 4)}</text>`;
    }
    const avgPath = path(avgTimes);
    const p95Path = path(p95Times);
    const area = avgPath ? `${avgPath} L ${width - right} ${top + plotHeight} L ${left} ${top + plotHeight} Z` : '';
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.innerHTML = grid
      + (area ? `<path class="area" d="${area}"/>` : '')
      + (avgPath ? `<path class="avgline" d="${avgPath}"/>` : '')
      + (p95Path ? `<path class="p95line" d="${p95Path}"/>` : '')
      + `<text class="axis" x="${width - 22}" y="${height - 4}">ms</text>`;
  }

  function empty(colspan) {
    return `<tr><td colspan="${colspan}" class="empty">暂无数据</td></tr>`;
  }

  function renderConnectionError(message) {
    if ((state.alerts || []).length) return;
    $('alerts').innerHTML = `<div class="empty warning">${esc(message)}</div>`;
  }

  async function loadInitialMetrics() {
    try {
      const response = await fetch(appPath('/api/metrics'));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      render(await response.json());
    } catch (error) {
      renderConnectionError(`指标加载失败：${error.message}`);
    }
  }

  function scheduleReconnect() {
    window.clearTimeout(reconnectTimer);
    const delay = Math.min(WS_RECONNECT_MAX_MS, WS_RECONNECT_BASE_MS * (2 ** reconnectAttempt));
    reconnectAttempt += 1;
    reconnectTimer = window.setTimeout(connectWebSocket, delay);
  }

  function connectWebSocket() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${location.host}${appPath('/ws')}`);
    ws.onopen = () => {
      reconnectAttempt = 0;
    };
    ws.onmessage = (event) => {
      try {
        render(JSON.parse(event.data));
      } catch (error) {
        renderConnectionError(`实时数据解析失败：${error.message}`);
      }
    };
    ws.onerror = () => {
      renderConnectionError('实时连接异常，正在尝试重连');
    };
    ws.onclose = () => {
      renderConnectionError('实时连接已断开，正在尝试重连');
      scheduleReconnect();
    };
  }

  $('requests').onclick = (event) => {
    const row = event.target.closest('tr[data-id]');
    if (row) showDetail(row.dataset.id);
  };
  $('search').oninput = debounce(renderRequests, SEARCH_DEBOUNCE_MS);
  $('clear').onclick = () => {
    $('search').value = '';
    $('detail').className = 'request-detail';
    renderRequests();
  };
  window.onresize = debounce(renderChart, 100);

  connectWebSocket();
  loadInitialMetrics();
}());
