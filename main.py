from flask import Flask, request, redirect, url_for, render_template_string, flash
import mysql.connector
from mysql.connector import pooling

app = Flask(__name__)
app.secret_key = "dev"  # 用於 flash 訊息；作業環境夠用

# === 依你的 MySQL 帳密調整 ===
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "hazell9",         # 或 root（不建議），請改成你實際帳號
    "password": "Rabin41271115H",# 請改成你的密碼
    "database": "db_2025",     # 作業指定的 DB 名稱
}
cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **DB_CONFIG)

# 簡單首頁：導到新增頁
@app.route("/")
def home():
    return redirect(url_for("add_employee_form"))

# 新增頁（GET 顯示表單，POST 寫入 DB）
@app.route("/add", methods=["GET", "POST"])
def add_employee_form():
    if request.method == "POST":
        employee_ID = request.form.get("employee_ID", "").strip()
        first_name  = request.form.get("first_name", "").strip()
        last_name   = request.form.get("last_name", "").strip()

        # 依作業需求，同時儲存 employee_name（可用 first+last 合併）
        employee_name = f"{first_name} {last_name}".strip()

        if not employee_ID.isdigit():
            flash("employee_ID 必須是數字")
            return redirect(url_for("add_employee_form"))

        try:
            conn = cnxpool.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO employee (employee_ID, employee_name, first_name, last_name)
                VALUES (%s, %s, %s, %s)
            """, (int(employee_ID), employee_name, first_name, last_name))
            conn.commit()
            flash("新增成功！")
        except mysql.connector.Error as e:
            flash(f"寫入失敗：{e}")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass

        return redirect(url_for("add_employee_form"))

    # GET：顯示表單 + 目前清單
    rows = []
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT employee_ID, employee_name, first_name, last_name FROM employee ORDER BY employee_ID")
        rows = cur.fetchall()
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

    tmpl = """
    <!doctype html>
    <html lang="zh-Hant"><head>
      <meta charset="utf-8">
      <title>HW1: Add Employee</title>
      <style>
        body{font-family:Arial,"Microsoft JhengHei",sans-serif;margin:24px;}
        form{margin-bottom:20px;}
        label{display:block;margin:8px 0 4px;}
        input{padding:6px 10px;min-width:260px;}
        button{padding:8px 14px;margin-top:10px;cursor:pointer}
        table{border-collapse:collapse;min-width:700px;margin-top:16px;}
        th,td{border:1px solid #ccc;padding:8px 12px;text-align:left;}
        th{background:#f7f7f7}
        .flash{color:#d21;margin:8px 0;}
      </style>
    </head><body>
      <h2>HW1：Flask → MySQL 新增員工</h2>

      {% with messages = get_flashed_messages() %}
        {% if messages %}
          {% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}
        {% endif %}
      {% endwith %}

      <form method="post" action="{{ url_for('add_employee_form') }}">
        <label>employee_ID（數字，主鍵）</label>
        <input name="employee_ID" required>
        <label>first_name</label>
        <input name="first_name" required>
        <label>last_name</label>
        <input name="last_name" required>
        <button type="submit">新增</button>
      </form>

      <h3>目前資料（employee）</h3>
      <table>
        <thead><tr>
          <th>employee_ID</th><th>employee_name</th><th>first_name</th><th>last_name</th>
        </tr></thead>
        <tbody>
          {% for r in rows %}
          <tr>
            <td>{{ r[0] }}</td>
            <td>{{ r[1] }}</td>
            <td>{{ r[2] }}</td>
            <td>{{ r[3] }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </body></html>
    """
    return render_template_string(tmpl, rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
