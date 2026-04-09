# OPERATIONS.md

## 目标
这是一份面向当前 MVP 的运维 README。内容只覆盖已经上线并验证过的实际部署形态，不讨论未来理想方案。

适用范围：
- 生产部署
- 服务重启与巡检
- 环境变量与目录约定
- 常见故障排查
- 脚本化重放部署

---

## 当前生产拓扑

### 访问层
- 域名：`https://zzetz.cn`
- `80` 端口：HTTP，统一跳转到 HTTPS
- `443` 端口：`nginx` 提供静态前端和 `/api` 反向代理

### 应用层
- 前端：Vite 构建产物，由 `nginx` 从静态目录直接提供
- 后端：`gunicorn` + Flask
- 后端监听：`127.0.0.1:5050`
- `/api/*`：由 `nginx` 反代到 `127.0.0.1:5050`

### 数据与文件
- 数据库：SQLite
- 数据库文件：`/opt/zzetzMain/backend/app.db`
- 上传目录：`/opt/zzetzMain/backend/uploads`

---

## 关键路径

### 仓库与构建产物
- 代码目录：`/opt/zzetzMain`
- 前端静态目录：`/var/www/zzetz.cn`

### 服务配置
- systemd：`/etc/systemd/system/zzetz-backend.service`
- nginx：`/etc/nginx/conf.d/zzetz.cn.conf`
- 后端环境变量：`/opt/zzetzMain/backend/.env`

### 证书
- 证书目录：`/etc/letsencrypt/live/zzetz.cn/`
- 当前脚本默认依赖现有 `certbot` 证书，不负责申请证书

---

## 当前运行约定

### 后端服务
- 服务名：`zzetz-backend`
- 进程模型：`gunicorn --workers 2`
- 绑定地址：`127.0.0.1:5050`
- 当前超时：
  - `gunicorn --timeout 420`
  - `nginx proxy_*_timeout 420s`

### 为什么要放宽超时
- 一条真实消息可能包含两次 LLM 调用：
  - 阶段回复
  - 摘要提取
- 百炼兼容层在云服务器上的真实耗时可能达到几十秒甚至更久
- 如果只放宽应用超时，不放宽 `gunicorn` 或 `nginx`，生产会重新出现：
  - `500`：worker 被 `gunicorn` 提前杀掉
  - `504`：`nginx` 反代先超时

---

## Session 状态语义

当前生产会话状态不要再按旧理解使用：

- `draft`：刚创建，尚未进入真实处理
- `active`：当前正在占用并发槽位的处理中请求
- `queued`：等待进入处理槽位
- `in_progress`：已经处理过，仍在梳理流程中，但当前不占用活跃槽位
- `generating_document`：正在生成文档
- `completed`：文档已生成
- `failed`：处理失败

关键规则：
- `active` 只表示“当前正在处理”
- 处理结束后必须回到 `in_progress`，否则数据库会永久占满 5 个活跃槽位

---

## 环境变量

`backend/.env` 至少应包含：

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=qwen3.5-plus
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_TIMEOUT=120
FLASK_ENV=production
FLASK_PORT=5050
UPLOAD_FOLDER=uploads
```

运维规则：
- 密钥只保留在服务器 `backend/.env`
- 不要把密钥提交回仓库
- 不要把本机 shell 代理环境当成服务依赖

### 本地部署凭据

如果需要从本机通过密码登录云机执行部署，可把本地 SSH 凭据放在仓库根目录 `.env`：

```bash
DEPLOY_HOST=129.204.9.74
DEPLOY_USER=root
DEPLOY_PASSWORD=...
```

规则：
- 根目录 `.env` 只用于本机运维，不用于应用运行
- 根目录 `.env` 已被 `.gitignore` 忽略，不要把这类密码写进仓库追踪文件
- 服务器运行时仍只读取 `/opt/zzetzMain/backend/.env`

---

## 一键部署

仓库内脚本：
- [scripts/deploy-zzetz-cn.sh](/Users/zzten/work/zzetzMain/scripts/deploy-zzetz-cn.sh)

脚本职责：
- `git fetch/pull`
- 前端依赖安装与构建
- 后端 venv 初始化与依赖安装
- 同步静态文件到 `nginx` 目录
- 写入 `systemd` 服务文件
- 写入 `nginx` 配置
- 重载服务
- 做基础健康检查

服务器上执行：

```bash
cd /opt/zzetzMain
bash scripts/deploy-zzetz-cn.sh
```

脚本前提：
- 仓库已 clone 到 `/opt/zzetzMain`
- `backend/.env` 已存在
- 机器已安装 `git python3 npm nginx systemctl curl`
- HTTPS 证书已存在

---

## 日常运维命令

### 查看服务状态
```bash
systemctl status zzetz-backend --no-pager
systemctl status nginx --no-pager
```

### 重启服务
```bash
systemctl restart zzetz-backend
systemctl reload nginx
```

### 查看日志
```bash
journalctl -u zzetz-backend -n 100 --no-pager
journalctl -u zzetz-backend -f
```

### 健康检查
```bash
curl http://127.0.0.1:5050/api/health
curl https://zzetz.cn/api/health
```

### 检查配置
```bash
nginx -t
systemctl daemon-reload
```

---

## 公网 E2E 浏览器规程

生产环境做 `agent-browser` 页面级验收时，当前项目有一个必须遵守的操作约定：

- `agent-browser snapshot -i` 会列出视口外的交互元素
- 但 `agent-browser click @ref` 对视口外元素不会稳定自动滚动
- 这类情况下命令可能返回 `Done`，但页面实际上没有收到任何 `pointer` / `mouse` / `click` 事件

### 结论

**在当前仓库的公网 E2E 中，凡是按钮可能不在首屏内时，必须先滚动到按钮进入当前视口，再执行点击。**

### 标准步骤

1. 打开页面并等待稳定：

```bash
agent-browser open https://zzetz.cn/...
agent-browser wait --load networkidle
agent-browser snapshot -i
```

2. 如果目标按钮不在首屏，先滚动，再重新抓取快照：

```bash
agent-browser scroll down 300
agent-browser snapshot -i
```

3. 确认按钮已进入当前视口后，再点击：

```bash
agent-browser click @eN
```

4. 点击后不要只看命令退出状态，要继续验证页面状态是否真的变化：

```bash
agent-browser snapshot -i
```

或配合真实 API / DevTools Network 复核是否真的发出了请求。

### 当前项目里必须先滚动再点的高风险位置

- 聊天页底部 `发送` 按钮
- 聊天页 `ready_to_generate` 后的“开始生成最终需求文档”按钮（当消息较多时）
- 后台页详情区的 `撤销 Token` 按钮（当列表较长、详情区域被压到下方时）

### 一般可直接点击的低风险位置

- 首页首屏 Hero 的“开始梳理我的网站”
- 首页 token 输入区的“进入对话”
- 后台首屏的“进入后台”（在默认桌面视口下通常位于首屏内）

### 诊断信号

如果出现以下现象，优先怀疑“按钮仍在视口外”而不是业务代码异常：

- `agent-browser click` 返回 `Done`
- 但页面没有进入 loading / typing / modal / route change
- DevTools 里没有对应的点击后网络请求
- 目标按钮文本、输入框内容、disabled 状态都没有变化

### 备用策略

如果必须继续验证真实链路，而 `agent-browser` 点击仍不稳定：

- 先滚动，再点击
- 若仍失败，用 DevTools 点击做对照，确认是否是浏览器工具问题
- 对消息发送、文档生成这类链路，可用真实 API 触发，再回到页面验证渲染结果

这个约定目前是**工具侧限制**，不是前端业务逻辑本身的已确认缺陷。

---

## 常见故障与处理

### 1. `/api/sessions/:token/messages` 返回 500
优先检查：
- `journalctl -u zzetz-backend -n 100 --no-pager`

重点判断：
- 是否是 `gunicorn` worker timeout
- 是否是模型调用失败

如果日志里有 `WORKER TIMEOUT`：
- 检查 `zzetz-backend.service` 是否仍然使用足够大的 `--timeout`

### 2. `/api/sessions/:token/messages` 返回 504
优先检查：
- `nginx` `/api/` 反代 timeout 是否被改小

当前要求：
- `proxy_connect_timeout 420s`
- `proxy_send_timeout 420s`
- `proxy_read_timeout 420s`
- `send_timeout 420s`

### 3. 新会话一直排队
常见原因：
- 旧会话状态残留在 `active` 或 `queued`

临时修复：
```bash
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect('/opt/zzetzMain/backend/app.db')
cur = conn.cursor()
cur.execute("update sessions set status='in_progress', queued_at=NULL where status in ('active','queued')")
conn.commit()
conn.close()
PY
```

如果这类问题再次出现：
- 先确认仓库版本是否包含消息路由里的状态回收修复

### 4. 服务器能联网，但 LLM 仍失败
优先检查：
- 是否受宿主机代理环境变量影响

当前代码已经显式设置：
- `httpx.post(..., trust_env=False)`

如果有人回退这个行为，线上会重新受到 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY` 等环境变量影响。

### 5. 服务器上直接调用模型很慢
可以用仓库内客户端做最小验证：

```bash
cd /opt/zzetzMain/backend
.venv/bin/python - <<'PY'
from app.config import _load_env_file
from app.services.llm_client import LLMClient
_load_env_file()
client = LLMClient.from_env()
resp = client.generate(
    instructions='你是一个中文助手，只回复ok',
    input_text='测试',
    timeout=30,
)
print(resp.text)
PY
```

如果这一层都失败：
- 问题在服务器到模型供应商之间，不在前端

---

## 变更原则

### 可以直接做的
- 拉取最新代码
- 重建前端静态资源
- 重启 `zzetz-backend`
- 重载 `nginx`
- 调整超时
- 做健康检查

### 需要谨慎的
- 改数据库状态
- 覆盖 `backend/.env`
- 改证书路径
- 改服务监听端口

### 不要做的
- 不要把 API key 写进仓库
- 不要把线上临时调试改动留在工作树里不提交也不还原
- 不要只改服务器、不回写仓库文档

---

## 推荐文档入口

- [README.md](/Users/zzten/work/zzetzMain/README.md)：开发者启动说明
- [ARCHITECTURE.md](/Users/zzten/work/zzetzMain/ARCHITECTURE.md)：系统架构与数据流
- [DOCUMENTATION.md](/Users/zzten/work/zzetzMain/DOCUMENTATION.md)：执行日志与验证记录
- [SESSION_CONTEXT.md](/Users/zzten/work/zzetzMain/SESSION_CONTEXT.md)：下一次会话恢复上下文
