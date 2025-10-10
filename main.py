import os
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string, flash

import mysql.connector
from mysql.connector import pooling

app = Flask(__name__)
app.secret_key = "dev"

# ======= MySQL 連線設定 =======
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "hazell9",
    "password": "Rabin41271115H",
    "database": "db_2025",
}
cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **DB_CONFIG)


# =======不用輸入秒數=======
def to_sql_datetime(dt_str: str) -> str:
    # 接收 <input type="datetime-local"> 的字串，例如 "2025-10-10T23:14"
    if not dt_str:
        return None
    # 將 'T' 替換為空格，並在結尾補上秒數 ":00"
    return dt_str.replace("T", " ") + ":00"

@app.route("/")
def home():
    return redirect(url_for("reserve"))

# ======= 建立 / 清單（同頁） =======
@app.route("/reserve", methods=["GET", "POST"])
def reserve():
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        adults = int(request.form.get("adults", 0) or 0)
        children = int(request.form.get("children", 0) or 0)
        reserve_time = to_sql_datetime(request.form.get("reserve_time", "").strip())
        phone = request.form.get("phone", "").strip()
        note = request.form.get("note", "").strip()
        is_birthday = 1 if request.form.get("is_birthday") == "on" else 0

        if not customer_name or not reserve_time:
            flash("請輸入姓名與訂位時間")
            return redirect(url_for("reserve"))

        try:
            conn = cnxpool.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO reservation
                (customer_name, adults, children, reserve_time, is_birthday, phone, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (customer_name, adults, children, reserve_time, is_birthday, phone, note))
            conn.commit()
            flash("✅ 訂位新增成功")
        except mysql.connector.Error as e:
            flash(f"❌ 新增錯誤：{e}")
        finally:
            # 確保 conn 變數存在且連線是開啟的，才執行關閉
            if 'conn' in locals() and conn.is_connected():
                cur.close()
                conn.close()

        return redirect(url_for("reserve"))

    # GET 請求：讀取清單
    rows = []
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT reserve_id, customer_name, adults, children, reserve_time, is_birthday, phone, note
            FROM reservation
            ORDER BY reserve_id ASC
        """)
        rows = cur.fetchall()
    except mysql.connector.Error as e:
        flash(f"❌ 讀取清單錯誤：{e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()

    tmpl = """
    <!doctype html>
    <html lang="zh-Hant"><head>
      <meta charset="utf-8">
      <title>美式餐廳線上訂位系統</title>
      <style>
        body{font-family:Arial,"Microsoft JhengHei",sans-serif;background:#fafafa;margin:0;}
        .wrap{max-width:980px;margin:32px auto;padding:0 20px;}
        .card{background:#fff;border-radius:14px;box-shadow:0 6px 18px rgba(0,0,0,0.08);padding:22px;}
        h1{color:#b13c2e;display:flex;align-items:center;gap:10px;margin:0 0 18px}
        .row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
        label{font-weight:bold;margin-top:10px;display:block}
        input,textarea{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;box-sizing:border-box}
        .actions{margin-top:14px}
        button{background:#b13c2e;color:#fff;border:none;padding:10px 16px;border-radius:8px;cursor:pointer}
        button:hover{background:#942b1f}
        table{border-collapse:collapse;width:100%;margin-top:18px;background:#fff;border-radius:12px;overflow:hidden}
        th,td{border-bottom:1px solid #eee;padding:10px;text-align:left}
        th{background:#f7f7f7}
        tr:last-child td{border-bottom:none}
        .flash{color:#c22;margin:10px 0}
        .text-center{text-align:center}
        .btn-sm{padding:6px 10px;border-radius:6px}
        .btn-ghost{background:#eee;color:#333}
        .btn-ghost:hover{background:#ddd}
        .inline-form{display:inline}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="card">
          <h1>🍔 美式餐廳線上訂位系統</h1>

          {% with messages = get_flashed_messages() %}
            {% if messages %}{% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}{% endif %}
          {% endwith %}

          <form method="post">
            <div class="row">
              <div>
                <label>姓名：</label>
                <input name="customer_name" required>
              </div>
              <div>
                <label>訂位時間：</label>
                <input type="datetime-local" name="reserve_time" required>
              </div>

              <div>
                <label>成人數：</label>
                <input type="number" name="adults" min="0" value="2">
              </div>
              <div>
                <label>孩童數：</label>
                <input type="number" name="children" min="0" value="0">
              </div>

              <div>
                <label>聯絡電話：</label>
                <input name="phone" placeholder="09xx-xxx-xxx">
              </div>
              <div>
                <label>是否壽星 🎂：</label>
                <input type="checkbox" name="is_birthday" style="transform:scale(1.3);margin-top:8px">
              </div>

              <div style="grid-column: span 2;">
                <label>備註：</label>
                <textarea name="note" placeholder="靠窗位、素食者等"></textarea>
              </div>
            </div>
            <div class="actions">
              <button type="submit">送出訂位</button>
            </div>
          </form>
        </div>

        <div class="card" style="margin-top:18px">
          <h2 style="margin:0 0 8px">📋 訂位清單</h2>
          <table>
            <tr>
              <th>ID</th><th>姓名</th><th>成人</th><th>兒童</th>
              <th>時間</th><th>壽星</th><th>電話</th><th>備註</th><th class="text-center">操作</th>
            </tr>
            {% for r in rows %}
            <tr>
              <td>{{r[0]}}</td>
              <td>{{r[1]}}</td>
              <td>{{r[2]}}</td>
              <td>{{r[3]}}</td>
              <td>{{r[4]}}</td>
              <td>{% if r[5]==1 %}🎉{% else %}-{% endif %}</td>
              <td>{{r[6]}}</td>
              <td>{{r[7]}}</td>
              <td class="text-center">
                <a class="btn-sm btn-ghost" href="{{ url_for('edit_reservation', reserve_id=r[0]) }}">編輯</a>
                <form class="inline-form" method="post" action="{{ url_for('delete_reservation', reserve_id=r[0]) }}" onsubmit="return confirm('確定刪除這筆訂位嗎？');">
                  <button class="btn-sm" type="submit">刪除</button>
                </form>
              </td>
            </tr>
            {% endfor %}
          </table>
        </div>
      </div>
    </body></html>
    """
    return render_template_string(tmpl, rows=rows)

# ======= 刪除 =======
@app.route("/delete/<int:reserve_id>", methods=["POST"])
def delete_reservation(reserve_id):
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM reservation WHERE reserve_id = %s", (reserve_id,))
        conn.commit()
        flash("已刪除一筆訂位")
    except mysql.connector.Error as e:
        flash(f"刪除失敗：{e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()
    return redirect(url_for("reserve"))

# ======= 編輯（GET 顯示、POST 儲存） =======
@app.route("/edit/<int:reserve_id>", methods=["GET", "POST"])
def edit_reservation(reserve_id):
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        adults = int(request.form.get("adults", 0) or 0)
        children = int(request.form.get("children", 0) or 0)
        reserve_time = to_sql_datetime(request.form.get("reserve_time", "").strip())
        phone = request.form.get("phone", "").strip()
        note = request.form.get("note", "").strip()
        is_birthday = 1 if request.form.get("is_birthday") == "on" else 0

        try:
            conn = cnxpool.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE reservation
                SET customer_name=%s, adults=%s, children=%s, reserve_time=%s,
                    is_birthday=%s, phone=%s, note=%s
                WHERE reserve_id=%s
            """, (customer_name, adults, children, reserve_time, is_birthday, phone, note, reserve_id))
            conn.commit()
            flash("已更新訂位")
        except mysql.connector.Error as e:
            flash(f"更新失敗：{e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cur.close()
                conn.close()
        return redirect(url_for("reserve"))

    # GET：讀取單筆資料以顯示編輯表單
    r = None
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT reserve_id, customer_name, adults, children, reserve_time, is_birthday, phone, note
            FROM reservation WHERE reserve_id=%s
        """, (reserve_id,))
        r = cur.fetchone()
    except mysql.connector.Error as e:
        flash(f"❌ 讀取訂位資料錯誤：{e}")
        return redirect(url_for("reserve"))
    finally:
        if 'conn' in locals() and conn.is_connected():
            cur.close()
            conn.close()

    if not r:
        flash("找不到這筆資料")
        return redirect(url_for("reserve"))

    # 將資料庫的 datetime 格式轉換為 input[type=datetime-local] 需要的 'YYYY-MM-DDTHH:MM' 格式
    dt_value = ""
    if r[4]:
        try:
            dt_value = datetime.strftime(r[4], "%Y-%m-%dT%H:%M")
        except Exception:
            # 備用方案，處理非標準的日期時間字串
            dt_value = str(r[4]).replace(" ", "T")[:16]

    tmpl = """
    <!doctype html>
    <html lang="zh-Hant"><head>
      <meta charset="utf-8">
      <title>編輯訂位</title>
      <style>
        body{font-family:Arial,"Microsoft JhengHei",sans-serif;background:#fafafa;margin:0}
        .wrap{max-width:720px;margin:40px auto;padding:0 20px}
        .card{background:#fff;padding:22px;border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,.08)}
        label{font-weight:bold;margin-top:10px;display:block}
        input,textarea{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;box-sizing:border-box}
        .actions{margin-top:14px;display:flex;gap:10px}
        button{background:#b13c2e;color:#fff;border:none;padding:10px 16px;border-radius:8px;cursor:pointer}
        a.btn{background:#eee;color:#333;text-decoration:none;display:inline-block;padding:10px 16px;border-radius:8px}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="card">
          <h2>編輯訂位 #{{r[0]}}</h2>
          <form method="post">
            <label>姓名</label><input name="customer_name" value="{{r[1]}}" required>
            <label>成人</label><input type="number" name="adults" min="0" value="{{r[2]}}">
            <label>兒童</label><input type="number" name="children" min="0" value="{{r[3]}}">
            <label>時間</label><input type="datetime-local" name="reserve_time" value="{{dt_value}}" required>
            <label>電話</label><input name="phone" value="{{r[6]}}">
            <label>是否壽星</label><input type="checkbox" name="is_birthday" {% if r[5]==1 %}checked{% endif %}>
            <label>備註</label><textarea name="note">{{r[7]}}</textarea>
            <div class="actions">
              <button type="submit">儲存</button>
              <a class="btn" href="{{ url_for('reserve') }}">返回</a>
            </div>
          </form>
        </div>
      </div>
    </body></html>
    """
    return render_template_string(tmpl, r=r, dt_value=dt_value)

if __name__ == "__main__":
    app.run(debug=True)