# bambu_clone

## 项目简介

该仓库是对 Bambu 网站的后端能力的一个精简克隆，重点演示模型资源的读取、附件下载以及后台同步控制等核心流程。当前实现采用内存数据源和存储，便于在本地快速启动与测试。

## 目录结构

- `backend/`：主要后端代码，包含 Flask 应用工厂、蓝图路由、内存数据库/存储服务及单元测试。
- `frontend/`：占位的前端目录，尚未实现具体界面。
- `flask/`：为单元测试提供的轻量 Flask 兼容层，用于在未安装官方 Flask 依赖时运行。
- `requirements.txt`：运行服务与测试所需的 Python 依赖列表。

## 后端能力概览

后端通过 `backend.app.create_app` 提供 Flask 应用工厂，初始化内存数据库、文件存储和同步管理器，并注册两个蓝图：

- **模型接口**（`/models`）：
  - `GET /models` 返回所有模型列表。
  - `GET /models/<model_id>` 返回单个模型元数据。
  - `GET /models/<model_id>/attachment` 提供模型关联附件下载。
- **后台同步接口**（`/admin`）：
  - `POST /admin/sync` 需要 `X-Admin-Token` 头部，触发一次同步任务。
  - `GET /admin/sync` 需要相同令牌，返回当前同步状态。

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

1. 确保完成依赖安装，并使用官方 Flask 包。
2. 设置环境变量并启动开发服务器：
   ```bash
   export FLASK_APP=backend.main:app
   flask run --reload
   ```
3. 服务器启动后，可通过以下接口验证：
   - `GET /health` 检查服务是否健康。
   - `GET /models` 查看模型列表。
   - `GET /admin/sync`（携带正确的 `X-Admin-Token`）查看同步状态。

在部署到生产环境时，可选择任意 WSGI 服务器（如 Gunicorn、uWSGI），加载 `backend.main:app` 即可。

### Docker 部署

仓库内提供了可直接构建的 `Dockerfile` 与 `docker-compose.yml`，便于在容器环境中运行后端服务。

构建并启动服务：

```bash
docker compose up --build
```

容器启动后，服务会监听在 `http://localhost:8000`。默认使用 Gunicorn 作为 WSGI 服务器，可在 Compose 配置中自定义端口或环境变量。

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
- 项目主要覆盖后端功能，前端仍为空目录。

