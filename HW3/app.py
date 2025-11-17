import os
from flask import Flask, request, redirect, url_for, render_template_string, flash
import mysql.connector
from mysql.connector import pooling

app = Flask(__name__)
app.secret_key = "dev_hw2"

# ======= MySQL 連線設定 =======
DB_CONFIG = {
    "host": "localhost",
    "user": "hazell9",
    "password": "Rabin41271115H", # (你 HW1 的密碼)
    "database": "db_2025",
}
try:
    cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **DB_CONFIG)
    print("MySQL 連線池建立成功")
except mysql.connector.Error as err:
    print(f"MySQL 連線池建立失敗: {err}")
    exit()

# ======= 主頁面 (導向學生管理) =======
@app.route("/")
def home():
    # 我們把學生管理頁面當作首頁
    return redirect(url_for("manage_students"))

# ======= 
# 
# ↓↓↓ 你要把「步驟 4」的程式碼貼在這裡 ↓↓↓
#
# =======

# ======= 學生管理 =======
@app.route("/students", methods=["GET", "POST"])
def manage_students():
    conn = None
    cur = None
    rows = []

    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()

        # (Create) 處理 POST 請求：新增學生
        if request.method == "POST":
            student_name = request.form.get("student_name", "").strip()
            email = request.form.get("email", "").strip()

            if not student_name or not email:
                flash("請輸入姓名和 Email")
            else:
                try:
                    cur.execute(
                        "INSERT INTO students (student_name, email) VALUES (%s, %s)",
                        (student_name, email)
                    )
                    conn.commit()
                    flash(f"✅ 學生 {student_name} 新增成功")
                except mysql.connector.Error as e:
                    conn.rollback() # 新增失敗，復原
                    flash(f"❌ 新增錯誤 (Email可能重複)：{e}")
            
            return redirect(url_for("manage_students"))

        # (Read) 處理 GET 請求：顯示學生清單
        cur.execute("SELECT student_id, student_name, email FROM students ORDER BY student_id")
        rows = cur.fetchall()

    except mysql.connector.Error as e:
        flash(f"❌ 讀取資料庫錯誤：{e}")
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

    # (Template) 網頁模板
    tmpl = """
    <!doctype html>
    <title>學生管理</title> <style>
      body{font-family:Arial,sans-serif;margin:40px;background:#f4f4f4;}
      .wrap{max-width:800px;margin:auto;background:#fff;padding:20px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.1);}
      .flash{color:#c22;margin:10px 0;background:#fdd;padding:10px;border-radius:5px;}
      table{border-collapse:collapse;width:100%;margin-top:20px;}
      th,td{border:1px solid #ddd;padding:10px;text-align:left;}
      th{background:#f9f9f9;}
      form{margin-top:20px;padding:15px;background:#f0f7ff;border-radius:8px;}
      input{padding:8px;margin:5px;border:1px solid #ccc;border-radius:5px;}
      button{background:#007bff;color:#fff;padding:8px 12px;border:none;border-radius:5px;cursor:pointer;}
      .btn {
        background:#007bff; color:#fff; padding: 8px 12px; border-radius: 5px;
        text-decoration: none; font-size: 13.333px; font-family: Arial,sans-serif;
      }
    </style>
    <body>
      <div class="wrap">
        <h2>學生管理</h2> {% with messages = get_flashed_messages() %}
          {% if messages %}{% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <h3>新增學生</h3>
        <form method="post">
          <label>姓名:</label><input name="student_name" required>
          <label>Email:</label><input type="email" name="email" required>
          <button type="submit">新增</button>
        </form>

        <h3>學生清單 (Read)</h3>
        <table>
          <tr><th>ID</th><th>姓名</th><th>Email</th><th>操作</th></tr>
          {% for r in rows %}
          <tr>
            <td>{{r[0]}}</td>
            <td>{{r[1]}}</td>
            <td>{{r[2]}}</td>
            <td style="display: flex; align-items: center; gap: 8px;">
                <a class="btn" href="{{ url_for('edit_student', student_id=r[0]) }}">編輯</a>
                <span>|</span>
                <form method="post" action="{{ url_for('delete_student', student_id=r[0]) }}" onsubmit="return confirm('確定刪除這位學生嗎？');" style="margin: 0; padding: 0;">
                    <button type="submit">刪除</button>
                </form>
            </td>
          </tr>
          {% endfor %}
        </table>
        
        <hr style="margin-top:30px">
        <p>
          <a href="{{ url_for('manage_courses') }}">管理課程</a> | 
          <a href="{{ url_for('manage_enrollments') }}">管理選課</a> |
          <a href="{{ url_for('report_page') }}">查看選課報表</a> </p>
      </div>
    </body>
    """
    return render_template_string(tmpl, rows=rows)
# ======= 刪除學生 (Delete) =======
@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = None
    cur = None
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()
        # 我們也刪除相關的選課紀錄，避免資料庫錯誤
        cur.execute("DELETE FROM enrollments WHERE student_id = %s", (student_id,))
        cur.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()
        flash(f"✅ 學生 ID {student_id} 已被刪除")
    except mysql.connector.Error as e:
        flash(f"❌ 刪除失敗：{e}")
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()
    return redirect(url_for("manage_students"))
# ======= 
# 
# ======= 編輯學生 (Update: GET/POST) =======
@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    conn = None
    cur = None
    
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()

        # (POST) 處理表單提交
        if request.method == "POST":
            student_name = request.form.get("student_name", "").strip()
            email = request.form.get("email", "").strip()

            if not student_name or not email:
                flash("請輸入姓名和 Email")
            else:
                try:
                    cur.execute(
                        "UPDATE students SET student_name = %s, email = %s WHERE student_id = %s",
                        (student_name, email, student_id)
                    )
                    conn.commit()
                    flash(f"✅ 學生 {student_name} 更新成功")
                    return redirect(url_for("manage_students"))
                except mysql.connector.Error as e:
                    conn.rollback()
                    flash(f"❌ 更新失敗：{e}")
            
            # 如果 POST 失敗，停在原頁面，但需重新抓取原資料
            cur.execute("SELECT student_id, student_name, email FROM students WHERE student_id = %s", (student_id,))
            r = cur.fetchone()

        # (GET) 顯示編輯表單
        else:
            cur.execute("SELECT student_id, student_name, email FROM students WHERE student_id = %s", (student_id,))
            r = cur.fetchone()
            if not r:
                flash("❌ 找不到該學生")
                return redirect(url_for("manage_students"))

    except mysql.connector.Error as e:
        flash(f"❌ 讀取資料庫錯誤：{e}")
        return redirect(url_for("manage_students"))
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

    # (Template) 編輯頁面的模板
    tmpl = """
    <!doctype html>
    <title>編輯學生</title>
    <style>
      body{font-family:Arial,sans-serif;margin:40px;background:#f4f4f4;}
      .wrap{max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.1);}
      .flash{color:#c22;margin:10px 0;background:#fdd;padding:10px;border-radius:5px;}
      form{margin-top:20px;padding:15px;background:#f0f7ff;border-radius:8px;}
      input{padding:8px;margin:5px;border:1px solid #ccc;border-radius:5px;width:95%;}
      button{background:#007bff;color:#fff;padding:8px 12px;border:none;border-radius:5px;cursor:pointer;}
      a.btn{background:#6c757d;color:#fff;text-decoration:none;padding:8px 12px;border-radius:5px;}
    </style>
    <body>
      <div class="wrap">
        <h2>編輯學生 #{{r[0]}}</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}{% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <form method="post">
          <label>姓名:</label>
          <input name="student_name" value="{{r[1]}}" required>
          <label>Email:</label>
          <input type="email" name="email" value="{{r[2]}}" required>
          <br><br>
          <button type="submit">儲存更新</button>
          <a class="btn" href="{{ url_for('manage_students') }}">取消</a>
        </form>
      </div>
    </body>
    """
    return render_template_string(tmpl, r=r)
#
# ======= 課程管理 =======
@app.route("/courses", methods=["GET", "POST"])
def manage_courses():
    conn = None
    cur = None
    rows = []

    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()

        # (Create)
        if request.method == "POST":
            course_name = request.form.get("course_name", "").strip()
            teacher = request.form.get("teacher", "").strip()

            if not course_name:
                flash("請輸入課程名稱")
            else:
                try:
                    cur.execute(
                        "INSERT INTO courses (course_name, teacher) VALUES (%s, %s)",
                        (course_name, teacher)
                    )
                    conn.commit()
                    flash(f"✅ 課程 {course_name} 新增成功")
                except mysql.connector.Error as e:
                    conn.rollback()
                    flash(f"❌ 新增錯誤：{e}")
            return redirect(url_for("manage_courses"))

        # (Read)
        cur.execute("SELECT course_id, course_name, teacher FROM courses ORDER BY course_id")
        rows = cur.fetchall()

    except mysql.connector.Error as e:
        flash(f"❌ 讀取資料庫錯誤：{e}")
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

    # (Template)
    tmpl = """
    <!doctype html>
    <title>課程管理</title> <style>
      body{font-family:Arial,sans-serif;margin:40px;background:#f4f4f4;}
      .wrap{max-width:800px;margin:auto;background:#fff;padding:20px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.1);}
      .flash{color:#c22;margin:10px 0;background:#fdd;padding:10px;border-radius:5px;}
      table{border-collapse:collapse;width:100%;margin-top:20px;}
      th,td{border:1px solid #ddd;padding:10px;text-align:left;}
      th{background:#f9f9f9;}
      form{margin-top:20px;padding:15px;background:#f0f7ff;border-radius:8px;}
      input{padding:8px;margin:5px;border:1px solid #ccc;border-radius:5px;}
      button{background:#007bff;color:#fff;padding:8px 12px;border:none;border-radius:5px;cursor:pointer;}
      .btn {
        background:#007bff; color:#fff; padding: 8px 12px; border-radius: 5px;
        text-decoration: none; font-size: 13.333px; font-family: Arial,sans-serif;
      }
    </style>
    <body>
      <div class="wrap">
        <h2>課程管理</h2> {% with messages = get_flashed_messages() %}
          {% if messages %}{% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <h3>新增課程</h3>
        <form method="post">
          <label>課程名稱:</label><input name="course_name" required>
          <label>授課教師:</label><input name="teacher">
          <button type="submit">新增</button>
        </form>

        <h3>課程清單 (Read)</h3>
        <table>
          <tr><th>ID</th><th>課程名稱</th><th>授課教師</th><th>操作</th></tr>
          {% for r in rows %}
          <tr>
            <td>{{r[0]}}</td>
            <td>{{r[1]}}</td>
            <td>{{r[2]}}</td>
            <td style="display: flex; align-items: center; gap: 8px;">
                <a class="btn" href="{{ url_for('edit_course', course_id=r[0]) }}">編輯</a>
                <span>|</span>
                <form method="post" action="{{ url_for('delete_course', course_id=r[0]) }}" onsubmit="return confirm('確定刪除這門課嗎？');" style="margin: 0; padding: 0;">
                    <button type="submit">刪除</button>
                </form>
            </td>
          </tr>
          {% endfor %}
        </table>
        
        <hr style="margin-top:30px">
        <p>
          <a href="{{ url_for('manage_students') }}">管理學生</a> | 
          <a href="{{ url_for('manage_enrollments') }}">管理選課</a> |
          <a href="{{ url_for('report_page') }}">查看選課報表</a> </p>
      </div>
    </body>
    """
    return render_template_string(tmpl, rows=rows)
# ======= 刪除課程 (Delete) =======
@app.route("/delete_course/<int:course_id>", methods=["POST"])
def delete_course(course_id):
    conn = None
    cur = None
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM enrollments WHERE course_id = %s", (course_id,))
        cur.execute("DELETE FROM courses WHERE course_id = %s", (course_id,))
        conn.commit()
        flash(f"✅ 課程 ID {course_id} 已被刪除")
    except mysql.connector.Error as e:
        flash(f"❌ 刪除失敗：{e}")
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()
    return redirect(url_for("manage_courses"))

# ======= 編輯課程 (Update: GET/POST) =======
@app.route("/edit_course/<int:course_id>", methods=["GET", "POST"])
def edit_course(course_id):
    conn = None
    cur = None
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()

        # (POST)
        if request.method == "POST":
            course_name = request.form.get("course_name", "").strip()
            teacher = request.form.get("teacher", "").strip()

            if not course_name:
                flash("請輸入課程名稱")
            else:
                try:
                    cur.execute(
                        "UPDATE courses SET course_name = %s, teacher = %s WHERE course_id = %s",
                        (course_name, teacher, course_id)
                    )
                    conn.commit()
                    flash(f"✅ 課程 {course_name} 更新成功")
                    return redirect(url_for("manage_courses"))
                except mysql.connector.Error as e:
                    conn.rollback()
                    flash(f"❌ 更新失敗：{e}")
            
            cur.execute("SELECT course_id, course_name, teacher FROM courses WHERE course_id = %s", (course_id,))
            r = cur.fetchone()
        
        # (GET)
        else:
            cur.execute("SELECT course_id, course_name, teacher FROM courses WHERE course_id = %s", (course_id,))
            r = cur.fetchone()
            if not r:
                flash("❌ 找不到該課程")
                return redirect(url_for("manage_courses"))

    except mysql.connector.Error as e:
        flash(f"❌ 讀取資料庫錯誤：{e}")
        return redirect(url_for("manage_courses"))
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

    # (Template)
    tmpl = """
    <!doctype html>
    <title>編輯課程</title>
    <style>
      body{font-family:Arial,sans-serif;margin:40px;background:#f4f4f4;}
      .wrap{max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.1);}
      .flash{color:#c22;margin:10px 0;background:#fdd;padding:10px;border-radius:5px;}
      form{margin-top:20px;padding:15px;background:#f0f7ff;border-radius:8px;}
      input{padding:8px;margin:5px;border:1px solid #ccc;border-radius:5px;width:95%;}
      button{background:#007bff;color:#fff;padding:8px 12px;border:none;border-radius:5px;cursor:pointer;}
      a.btn{background:#6c757d;color:#fff;text-decoration:none;padding:8px 12px;border-radius:5px;}
    </style>
    <body>
      <div class="wrap">
        <h2>編輯課程 #{{r[0]}}</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}{% for m in messages %}<div class.flash">{{ m }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <form method="post">
          <label>課程名稱:</label>
          <input name="course_name" value="{{r[1]}}" required>
          <label>授課教師:</label>
          <input name="teacher" value="{{r[2]}}">
          <br><br>
          <button type="submit">儲存更新</button>
          <a class="btn" href="{{ url_for('manage_courses') }}">取消</a>
        </form>
      </div>
    </body>
    """
    return render_template_string(tmpl, r=r)
# ======= (Read) JOIN 報表 =======
@app.route("/report")
def report_page():
    conn = None
    cur = None
    rows = []
    
    sql = """
        SELECT
            s.student_name,
            c.course_name,
            c.teacher
        FROM
            enrollments AS e
        INNER JOIN
            students AS s ON e.student_id = s.student_id
        INNER JOIN
            courses AS c ON e.course_id = c.course_id
        ORDER BY
            s.student_name, c.course_name;
    """

    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
    except mysql.connector.Error as e:
        flash(f"❌ 讀取 JOIN 報表錯誤：{e}")
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

    # (Template) 報表模板
    tmpl = """
    <!doctype html>
    <title>選課報表</title> <style>
      body{font-family:Arial,sans-serif;margin:40px;background:#f4f4f4;}
      .wrap{max-width:800px;margin:auto;background:#fff;padding:20px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.1);}
      .flash{color:#c22;margin:10px 0;background:#fdd;padding:10px;border-radius:5px;}
      table{border-collapse:collapse;width:100%;margin-top:20px;}
      th,td{border:1px solid #ddd;padding:10px;text-align:left;}
      th{background:#f9f9f9;}
    </style>
    <body>
      <div class="wrap">
        <h2>選課報表</h2> {% with messages = get_flashed_messages() %}
          {% if messages %}{% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <table>
          <tr>
            <th>學生姓名</th>
            <th>課程名稱</th>
            <th>授課教師</th>
          </tr>
          {% for r in rows %}
          <tr>
            <td>{{r[0]}}</td>
            <td>{{r[1]}}</td>
            <td>{{r[2]}}</td>
          </tr>
          {% endfor %}
          {% if not rows %}
          <tr><td colspan="3" style="text-align:center;">目前沒有任何選課紀錄</td></tr>
          {% endif %}
        </table>
        
        <p style="margin-top:20px">
          <a href="{{ url_for('manage_students') }}">返回學生管理</a>
        </p>
      </div>
    </body>
    """
    return render_template_string(tmpl, rows=rows)
# ======= 選課管理 =======
@app.route("/enrollments", methods=["GET", "POST"])
def manage_enrollments():
    conn = None
    cur = None
    students_list = []
    courses_list = []
    enrollments_list = []

    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()

        # (Create) 處理 POST 請求：新增選課
        if request.method == "POST":
            student_id = request.form.get("student_id")
            course_id = request.form.get("course_id")

            if not student_id or not course_id:
                flash("請選擇學生和課程")
            else:
                try:
                    cur.execute(
                        "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)",
                        (student_id, course_id)
                    )
                    conn.commit()
                    flash(f"✅ 選課紀錄新增成功")
                except mysql.connector.Error as e:
                    conn.rollback()
                    if e.errno == 1062: # 違反 UNIQUE KEY
                         flash(f"❌ 新增錯誤：這位學生已經選過這門課了")
                    else:
                        flash(f"❌ 新增錯誤：{e}")
            return redirect(url_for("manage_enrollments"))

        # (Read) 處理 GET 請求：
        # 1. 抓取所有學生 (給下拉選單用)
        cur.execute("SELECT student_id, student_name FROM students")
        students_list = cur.fetchall()

        # 2. 抓取所有課程 (給下拉選單用)
        cur.execute("SELECT course_id, course_name FROM courses")
        courses_list = cur.fetchall()

        # 3. 抓取所有選課紀錄
        cur.execute("""
            SELECT e.enrollment_id, s.student_name, c.course_name
            FROM enrollments AS e
            JOIN students AS s ON e.student_id = s.student_id
            JOIN courses AS c ON e.course_id = c.course_id
            ORDER BY e.enrollment_id
        """)
        enrollments_list = cur.fetchall()

    except mysql.connector.Error as e:
        flash(f"❌ 讀取資料庫錯誤：{e}")
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

    # (Template)
    tmpl = """
    <!doctype html>
    <title>選課管理</title> <style>
      body{font-family:Arial,sans-serif;margin:40px;background:#f4f4f4;}
      .wrap{max-width:800px;margin:auto;background:#fff;padding:20px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.1);}
      .flash{color:#c22;margin:10px 0;background:#fdd;padding:10px;border-radius:5px;}
      table{border-collapse:collapse;width:100%;margin-top:20px;}
      th,td{border:1px solid #ddd;padding:10px;text-align:left;}
      th{background:#f9f9f9;}
      form{margin-top:20px;padding:15px;background:#f0f7ff;border-radius:8px;}
      input, select{padding:8px;margin:5px;border:1px solid #ccc;border-radius:5px;}
      button{background:#007bff;color:#fff;padding:8px 12px;border:none;border-radius:5px;cursor:pointer;}
      .btn {
        background:#007bff; color:#fff; padding: 8px 12px; border-radius: 5px;
        text-decoration: none; font-size: 13.333px; font-family: Arial,sans-serif;
      }
    </style>
    <body>
      <div class="wrap">
        <h2>選課管理</h2> {% with messages = get_flashed_messages() %}
          {% if messages %}{% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <h3>新增選課紀錄</h3>
        <form method="post">
          <label>學生:</label>
          <select name="student_id" required>
            <option value="">-- 選擇學生 --</option>
            {% for s in students %}
            <option value="{{s[0]}}">{{s[1]}}</option>
            {% endfor %}
          </select>

          <label>課程:</label>
          <select name="course_id" required>
            <option value="">-- 選擇課程 --</option>
            {% for c in courses %}
            <option value="{{c[0]}}">{{c[1]}}</option>
            {% endfor %}
          </select>
          
          <button type="submit">新增</button>
        </form>

        <h3>選課清單 (Read)</h3>
        <table>
          <tr><th>ID</th><th>學生姓名</th><th>課程名稱</th><th>操作</th></tr>
          {% for r in enrollments %}
          <tr>
            <td>{{r[0]}}</td>
            <td>{{r[1]}}</td>
            <td>{{r[2]}}</td>
            <td style="display: flex; align-items: center; gap: 8px;">
              <a class="btn" href="{{ url_for('edit_enrollment', enrollment_id=r[0]) }}">編輯</a>
              <span>|</span>
              <form method="post" action="{{ url_for('delete_enrollment', enrollment_id=r[0]) }}" onsubmit="return confirm('確定刪除這筆選課紀錄嗎？');" style="margin: 0; padding: 0;">
                <button type="submit">刪除</button>
              </form>
            </td>
          </tr>
          {% endfor %}
        </table>
        
        <hr style="margin-top:30px">
        <p>
          <a href="{{ url_for('manage_students') }}">管理學生</a> | 
          <a href="{{ url_for('manage_courses') }}">管理課程</a> |
          <a href="{{ url_for('report_page') }}">查看選課報表</a> </p>
      </div>
    </body>
    """
    # 傳送三個清單給模板
    return render_template_string(tmpl, students=students_list, courses=courses_list, enrollments=enrollments_list)
# ======= 刪除選課紀錄 (Delete) =======
@app.route("/delete_enrollment/<int:enrollment_id>", methods=["POST"])
def delete_enrollment(enrollment_id):
    conn = None
    cur = None
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM enrollments WHERE enrollment_id = %s", (enrollment_id,))
        conn.commit()
        flash(f"✅ 選課紀錄 ID {enrollment_id} 已被刪除")
    except mysql.connector.Error as e:
        flash(f"❌ 刪除失敗：{e}")
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()
    return redirect(url_for("manage_enrollments"))

# ======= 編輯選課紀錄 (Update: GET/POST) =======
@app.route("/edit_enrollment/<int:enrollment_id>", methods=["GET", "POST"])
def edit_enrollment(enrollment_id):
    conn = None
    cur = None
    
    try:
        conn = cnxpool.get_connection()
        cur = conn.cursor()

        # (POST) 處理表單提交
        if request.method == "POST":
            student_id = request.form.get("student_id")
            course_id = request.form.get("course_id")
            # grade = request.form.get("grade") or None # <-- 移除成績

            if not student_id or not course_id:
                flash("請選擇學生和課程")
            else:
                try:
                    # SQL 移除 grade
                    cur.execute(
                        "UPDATE enrollments SET student_id = %s, course_id = %s WHERE enrollment_id = %s",
                        (student_id, course_id, enrollment_id) # <-- 移除 grade
                    )
                    conn.commit()
                    flash(f"✅ 選課紀錄 {enrollment_id} 更新成功")
                    return redirect(url_for("manage_enrollments"))
                except mysql.connector.Error as e:
                    conn.rollback()
                    if e.errno == 1062:
                         flash(f"❌ 更新失敗：這位學生已經選過這門課了")
                    else:
                        flash(f"❌ 更新失敗：{e}")

            # 如果 POST 失敗，停在原頁面，需重新抓取所有資料
            # SQL 移除 grade
            cur.execute("SELECT student_id, course_id FROM enrollments WHERE enrollment_id = %s", (enrollment_id,))
            r = cur.fetchone()
            cur.execute("SELECT student_id, student_name FROM students")
            students_list = cur.fetchall()
            cur.execute("SELECT course_id, course_name FROM courses")
            courses_list = cur.fetchall()

        # (GET) 顯示編輯表單
        else:
            # SQL 移除 grade
            cur.execute("SELECT student_id, course_id FROM enrollments WHERE enrollment_id = %s", (enrollment_id,))
            r = cur.fetchone()
            if not r:
                flash("❌ 找不到該筆紀錄")
                return redirect(url_for("manage_enrollments"))
            
            # 抓取所有學生和課程 (給下拉選單用)
            cur.execute("SELECT student_id, student_name FROM students")
            students_list = cur.fetchall()
            cur.execute("SELECT course_id, course_name FROM courses")
            courses_list = cur.fetchall()

    except mysql.connector.Error as e:
        flash(f"❌ 讀取資料庫錯誤：{e}")
        return redirect(url_for("manage_enrollments"))
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

    # (Template) 編輯頁面的模板
    tmpl = """
    <!doctype html>
    <title>編輯選課紀錄</title>
    <style>
      body{font-family:Arial,sans-serif;margin:40px;background:#f4f4f4;}
      .wrap{max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:10px;box-shadow:0 4px 10px rgba(0,0,0,0.1);}
      .flash{color:#c22;margin:10px 0;background:#fdd;padding:10px;border-radius:5px;}
      form{margin-top:20px;padding:15px;background:#f0f7ff;border-radius:8px;}
      input, select{padding:8px;margin:5px;border:1px solid #ccc;border-radius:5px;width:95%;}
      button{background:#007bff;color:#fff;padding:8px 12px;border:none;border-radius:5px;cursor:pointer;}
      a.btn{background:#6c757d;color:#fff;text-decoration:none;padding:8px 12px;border-radius:5px;}
    </style>
    <body>
      <div class="wrap">
        <h2>編輯選課紀錄 #{{enrollment_id}}</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}{% for m in messages %}<div class="flash">{{ m }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <form method="post">
          <label>學生:</label>
          <select name="student_id" required>
            {% for s in students %}
            <option value="{{s[0]}}" {% if s[0] == r[0] %}selected{% endif %}>{{s[1]}}</option>
            {% endfor %}
          </select>
          
          <label>課程:</label>
          <select name="course_id" required>
            {% for c in courses %}
            <option value="{{c[0]}}" {% if c[0] == r[1] %}selected{% endif %}>{{c[1]}}</option>
            {% endfor %}
          </select>

          <br><br>
          <button typeD="submit">儲存更新</button>
          <a class="btn" href="{{ url_for('manage_enrollments') }}">取消</a>
        </form>
      </div>
    </body>
    """
    return render_template_string(tmpl, r=r, students=students_list, courses=courses_list, enrollment_id=enrollment_id)
# ======= 
# 
# ↓↓↓ 這就是你原本的結尾，不用動它 ↓↓↓
#
# =======

if __name__ == "__main__":
    app.run(debug=True)