简历博客 Demo（Flask + Vue3 + MySQL 连接池）

快速开始（Windows / PowerShell）

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

数据库准备

1) 在 MySQL 中创建数据库 `flaskdemo`（或自定义名称）。
2) 在 Navicat 选择数据库执行 `schema.sql`。

运行

```powershell
# 可直接右键运行 app.py 或：
python app.py
```

访问 http://127.0.0.1:5000/ （Vue 前端页）。

环境变量（可选，默认 root/123456@127.0.0.1:3306/flaskdemo）

- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

接口

- POST /api/register {username,password}
- POST /api/login {username,password}
- POST /api/logout
- GET /api/posts
- GET /api/posts/<id>
- POST /api/posts {title,body,author_id}
- POST /api/posts/<id> {title,body,author_id}
- POST /api/posts/<id>/delete {author_id}

学习指南（文件结构与运行流程）

1) app.py（后端主程序）
- 使用 Flask 提供 HTTP 接口；使用 DBUtils+PyMySQL 构建 MySQL 连接池。
- 重要部分：
  - POOL = PooledDB(...): 配置连接池（最大连接数、空闲连接等），默认连接 127.0.0.1:3306 的 flaskdemo 库，也可通过环境变量覆盖。
  - /api/register: 注册新用户；先查重，再插入。
  - /api/login: 校验用户名与密码，返回 userId 与 username。
  - /api/logout: 简化模拟登出（无会话存储）。
  - /api/posts: 列表文章（含作者名）。
  - /api/posts/<id>: 获取文章详情。
  - /api/posts（POST）: 新建文章，需传 author_id。
  - /api/posts/<id>（POST）: 编辑文章，仅作者本人可编辑。
  - /api/posts/<id>/delete（POST）: 删除文章，仅作者本人可删。
  - / 与 /favicon.ico: 分别返回前端页面和避免 404 的占位响应。

2) templates/vue.html（前端页面 - 使用 Vue3 CDN）
- 未登录：只显示登录/注册卡片；表单切换时清空或保留用户名；错误/成功用 alert 弹窗提示。
- 登录后：显示仪表台（发布文章表单 + 文章列表、编辑/删除按钮），作者才可编辑/删除。
- 与后端交互：使用 fetch 访问 /api/* 路由。

3) schema.sql（数据库结构）
- users: 存放用户（username 唯一）。
- posts: 存放文章（title+body+author_id），外键关联 users.id，作者删除时文章一起删除（级联）。

4) requirements.txt（依赖）
- Flask: Web 框架。
- DBUtils: 连接池实现。
- PyMySQL: MySQL 驱动。
- waitress: 可选的 WSGI 服务器（生产部署使用）。

端到端数据流（简化）
- 注册：Vue 调 /api/register -> Flask 用连接池写入 users -> 返回成功 -> 前端切到“登录”。
- 登录：Vue 调 /api/login -> Flask 校验用户 -> 返回 userId/username -> 前端进入仪表台。
- 发文：Vue 调 /api/posts（POST）携带 author_id -> Flask 写入 posts -> 刷新列表。
- 编辑：Vue 调 /api/posts/<id>（POST）-> Flask 验证作者身份 -> 更新。
- 删除：Vue 调 /api/posts/<id>/delete（POST）-> Flask 验证作者身份 -> 删除并刷新列表。

结构

```
blogs/
  app.py
  wsgi.py
  requirements.txt
  templates/
    base.html
    index.html
  static/
    css/
      main.css
  README.md
```

环境变量（可选）
- FLASK_DEBUG=1 启用调试
- PORT=5000 自定义端口（app.py 会读取）


