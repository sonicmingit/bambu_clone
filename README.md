# bambu_clone

## 项目简介

该仓库是对 Bambu 网站的后端能力的一个精简克隆，重点演示模型资源的读取、附件下载以及后台同步控制等核心流程。当前实现采用内存数据源和存储，便于在本地快速启动与测试。

## 目录结构

- `backend/`：主要后端代码，包含 Flask 应用工厂、蓝图路由、内存数据库/存储服务及单元测试。
- `frontend/`：基于 Vite + Vue 的前端展示页面，可直接浏览演示模型数据。
- `flask/`：为单元测试提供的轻量 Flask 兼容层，用于在未安装官方 Flask 依赖时运行。
- `requirements.txt`：运行服务与测试所需的 Python 依赖列表。

## 后端能力概览

后端通过 `backend.app.create_app` 提供 Flask 应用工厂，初始化内存数据库、文件存储和同步管理器，并注册两个蓝图：

- **模型接口**（`/api/models`）：
  - `GET /api/models` 返回所有模型列表。
  - `GET /api/models/<model_id>` 返回单个模型元数据。
  - `GET /api/models/<model_id>/attachment` 提供模型关联附件下载。
- **后台同步接口**（`/api/admin`）：
  - `POST /api/admin/sync` 需要 `X-Admin-Token` 头部，触发一次同步任务。
  - `GET /api/admin/sync` 需要相同令牌，返回当前同步状态。

核心业务依赖定义在 `backend/services.py`：

- `InMemoryDatabase` 提供静态模型数据。
- `InMemoryStorage` 以内存方式存放附件内容。
- `SyncManager` 维护同步任务状态（运行次数、最后触发时间等）。

为了兼容 WSGI/ASGI 托管，`backend/main.py` 暴露了一个可供服务器加载的 `app` 对象，并附带 `GET /health` 健康检查。

## 环境准备

- Python 3.11+
- 推荐使用虚拟环境（`python -m venv .venv`）

安装依赖：

```bash
pip install -r requirements.txt
```

> **提示**：仓库内置的 `flask/` 目录实现了一个最小化的 Flask 兼容层，便于在无外部依赖的情况下运行单元测试。如果已经通过 `pip` 安装了官方 Flask，可以删除或重命名本地 `flask` 目录以使用完整框架功能。

## 启动与部署

### 本地开发

1. 启动后端接口
   ```bash
   export FLASK_APP=backend.main:app
   flask run --reload
   ```
   后端默认监听在 `http://localhost:5000`，并通过 `/api/models`、`/api/admin/sync` 等接口提供数据。
2. 启动前端展示页（需 Node.js 18+）
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   前端开发服务器启动后访问 `http://localhost:5173` 即可在浏览器查看“模型资源展示”页面，页面会直接调用后端接口渲染数据。

在部署到生产环境时，可选择任意 WSGI 服务器（如 Gunicorn、uWSGI）加载 `backend.main:app`，并将前端构建产物托管在静态服务器或 CDN 上，同时通过反向代理将 `/api` 路由指向后端服务。

### Docker 部署

仓库内提供了可直接构建的 `Dockerfile` 与 `docker-compose.yml`，便于在容器环境中运行后端服务。

构建并启动服务：

```bash
docker compose up --build
```

容器启动后：

- 后端服务监听在 `http://localhost:8000`，提供 `/api/*` 接口。
- 前端开发服务器监听在 `http://localhost:5173`，打开即可看到演示页面。

如需修改前端在开发模式下的后端代理目标，可调整 `frontend/vite.config.js` 或在启动命令中覆盖 `VITE_BACKEND_TARGET` 环境变量。

### 演示数据

内存数据库默认预置了 5 条模型记录以及相应的附件文件，覆盖常见的生产、实验、地区化、遗留和离线批处理等场景，可直接用于接口联调与功能演示。

## 测试

项目包含针对模型接口与后台接口的单元测试。安装依赖后运行：

```bash
pytest
```

全部测试应通过以验证主要功能。

## 已知情况

- 当前数据和附件均来自内存，适合演示与联调，生产环境需替换为真实数据库与对象存储实现。
- 当前前端为轻量级展示页面，可在此基础上扩展完整站点能力。

