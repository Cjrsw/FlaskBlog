import os
from typing import Any, Dict, List
from flask import Flask, request, jsonify, send_file
from dbutils.pooled_db import PooledDB
import pymysql

# 本文件是后端主程序：
# - 使用 Flask 提供 API
# - 使用 DBUtils(PooledDB) + PyMySQL 连接 MySQL
# - 所有接口都返回 JSON，供前端 Vue 页面调用


# 创建全局连接池（应用启动时初始化，不会立即创建物理连接，mincached=0 懒加载）
POOL = PooledDB(
    creator=pymysql,
    maxconnections=10,
    mincached=0,
    maxcached=3,
    blocking=True,
    setsession=[],
    ping=0,
    host=os.getenv("DB_HOST", "127.0.0.1"),    # 主机
    port=int(os.getenv("DB_PORT", "3306")),    # 端口
    user=os.getenv("DB_USER", "root"),         # 用户
    passwd=os.getenv("DB_PASSWORD", "123456"),  # 密码（你可改成环境变量）
    charset="utf8mb4",                           # 字符集
    db=os.getenv("DB_NAME", "flaskdemo"),       # 数据库名
    autocommit=True,                              # 自动提交，简化示例
)


def dictfetchall(cursor) -> List[Dict[str, Any]]:
    """工具函数：把游标结果转为 [{col: val}] 列表。"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


app = Flask(__name__)


@app.route("/") 
def home():
    # 返回内嵌 Vue3 的前端页面
    return send_file("templates/vue.html")


@app.route('/favicon.ico')
def favicon():
    # 避免浏览器请求 /favicon.ico 报 404 噪音
    return ('', 204)


@app.post('/api/register')
def api_register():
    """注册接口：
    - 校验必填 -> 查重 -> 插入 users
    """
    data = request.get_json(silent=True) or {}
    print(data)
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400
    conn = POOL.connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            return jsonify({"error": "用户名已存在"}), 409
        cursor.execute("INSERT INTO users(username, password) VALUES(%s,%s)", (username, password))
        return jsonify({"message": "注册成功"})
    finally:
        cursor.close()
        conn.close()


@app.post('/api/login')
def api_login():
    """登录接口：
    - 根据用户名查出密码 -> 对比 -> 返回 userId/username
    说明：为演示简化，未做密码哈希与会话
    """
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400
    conn = POOL.connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "用户不存在"}), 404
        user_id, pwd = row[0], row[1]
        if pwd != password:
            return jsonify({"error": "用户密码错误"}), 401
        return jsonify({"message": "登录成功", "userId": int(user_id), "username": username})
    finally:
        cursor.close()
        conn.close()


@app.post('/api/logout')
def api_logout():
    return jsonify({"message": "已退出登录"})


@app.get('/api/posts')
def api_posts_list():
    """文章列表：联表拿到作者名，按时间倒序"""
    conn = POOL.connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT p.id, p.title, p.body, p.created_at, p.updated_at,
                   u.id as author_id, u.username as author
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            ORDER BY p.created_at DESC
            """
        )
        rows = dictfetchall(cursor)
        return jsonify(rows)
    finally:
        cursor.close()
        conn.close()


@app.get('/api/posts/<int:post_id>')
def api_posts_detail(post_id: int):
    """文章详情：根据 id 查询"""
    conn = POOL.connection(); cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT p.id, p.title, p.body, p.created_at, p.updated_at,
                   u.id as author_id, u.username as author
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            WHERE p.id=%s
            """,
            (post_id,)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "文章不存在"}), 404
        columns = [col[0] for col in cursor.description]
        return jsonify(dict(zip(columns, row)))
    finally:
        cursor.close(); conn.close()


@app.post('/api/posts')
def api_posts_create():
    """创建文章：仅登录用户（需要 author_id）"""
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    body = (data.get('body') or '').strip()
    author_id = data.get('author_id')
    if not title or not body or not author_id:
        return jsonify({"error": "标题、正文、作者ID均不能为空"}), 400
    conn = POOL.connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE id=%s", (author_id,))
        if not cursor.fetchone():
            return jsonify({"error": "作者不存在"}), 400
        cursor.execute(
            "INSERT INTO posts(title, body, author_id) VALUES(%s,%s,%s)",
            (title, body, int(author_id))
        )
        post_id = cursor.lastrowid
        return jsonify({"message": "创建成功", "id": int(post_id)})
    finally:
        cursor.close(); conn.close()


@app.post('/api/posts/<int:post_id>')
def api_posts_update(post_id: int):
    """更新文章：必须作者本人"""
    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    body = (data.get('body') or '').strip()
    author_id = data.get('author_id')
    if not title or not body or not author_id:
        return jsonify({"error": "标题、正文、作者ID均不能为空"}), 400
    conn = POOL.connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT author_id FROM posts WHERE id=%s", (post_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "文章不存在"}), 404
        if int(row[0]) != int(author_id):
            return jsonify({"error": "无权限编辑（仅作者可编辑）"}), 403
        cursor.execute(
            "UPDATE posts SET title=%s, body=%s WHERE id=%s",
            (title, body, post_id)
        )
        return jsonify({"message": "已更新"})
    finally:
        cursor.close()
        conn.close()


@app.post('/api/posts/<int:post_id>/delete')
def api_posts_delete(post_id: int):
    """删除文章：必须作者本人"""
    data = request.get_json(silent=True) or {}
    author_id = data.get('author_id')
    print(author_id)
    if not author_id:
        return jsonify({"error": "缺少作者ID"}), 400
    conn = POOL.connection(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT author_id FROM posts WHERE id=%s", (post_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "文章不存在"}), 404
        if int(row[0]) != int(author_id):
            return jsonify({"error": "无权限删除（仅作者可删除）"}), 403
        cursor.execute("DELETE FROM posts WHERE id=%s", (post_id,))
        return jsonify({"message": "已删除"})
    finally:
        cursor.close(); conn.close()


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=debug)


