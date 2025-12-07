from flask import Flask, request, redirect, url_for, render_template, flash
import pymongo
from bson.objectid import ObjectId  # 這是用來處理 MongoDB ID 的重要工具
import os

app = Flask(__name__)
app.secret_key = "dev_hw3_mongo"

# ======= MongoDB 連線設定 (請修改這裡) =======
# 1. 先嘗試從環境變數抓 (這是給 Render 用的)
CONNECTION_STRING = os.environ.get("MONGO_CONNECTION_STRING")

# 2. 如果抓不到 (代表你現在是用自己電腦在跑)，就用這串直接連
if not CONNECTION_STRING:
    print("⚠️ 本地開發模式：使用寫死的連線字串")
    # 👇 請把你的 MongoDB 完整連線字串貼在下面引號裡 (包含帳號密碼)
    CONNECTION_STRING = "mongodb+srv://hw3_user:hw3_userpassword@cluster0.4oe0smy.mongodb.net/?appName=Cluster0"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client["db_2025"] # 資料庫名稱
# 我們會有三個集合 (Collections): students, courses, enrollments

print("MongoDB 連線設定完成")

# ======= 主頁面 =======
@app.route("/")
def home():
    return redirect(url_for("manage_students"))

# ======= [作業要求] insert_many 功能 =======
@app.route("/init_data")
def init_data():
    """
    這就是作業要求的 insert_many 功能。
    執行這個路由會一次新增多筆假資料。
    """
    students_col = db["students"]
    
    # 準備多筆資料
    new_students = [
        {"student_name": "範例學生A", "email": "a@test.com"},
        {"student_name": "範例學生B", "email": "b@test.com"},
        {"student_name": "範例學生C", "email": "c@test.com"}
    ]
    
    try:
        # 關鍵指令：insert_many
        students_col.insert_many(new_students)
        flash("✅ 成功使用 insert_many 批次新增了 3 位學生！")
    except Exception as e:
        flash(f"❌ insert_many 失敗：{e}")

    return redirect(url_for("manage_students"))

# ======= 學生管理 (CRUD) =======
@app.route("/students", methods=["GET", "POST"])
def manage_students():
    students_col = db["students"]

    # (Create) 新增學生
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        email = request.form.get("email", "").strip()

        if not student_name or not email:
            flash("請輸入姓名和 Email")
        else:
            # MongoDB 新增語法
            students_col.insert_one({
                "student_name": student_name, 
                "email": email
            })
            flash(f"✅ 學生 {student_name} 新增成功")
        return redirect(url_for("manage_students"))

    # (Read) 讀取所有學生
    # 轉成 list 方便模板使用
    rows = list(students_col.find())

    # 2. 改這裡：直接回傳 HTML 檔案，不用再貼一長串字串了！
    return render_template("students.html", rows=rows)



# ======= 刪除學生 (Delete) =======
# 注意：MongoDB 的 ID 是字串，所以這裡移除了 <int: ...>
@app.route("/delete_student/<student_id>", methods=["POST"])
def delete_student(student_id):
    try:
        # 需要把字串轉回 ObjectId 才能刪除
        db["students"].delete_one({"_id": ObjectId(student_id)})
        # 連帶刪除相關選課紀錄 (模擬 Cascade Delete)
        db["enrollments"].delete_many({"student_id": student_id}) 
        flash(f"✅ 學生已刪除")
    except Exception as e:
        flash(f"❌ 刪除失敗：{e}")
    return redirect(url_for("manage_students"))

# ======= [HW4] 批量刪除功能 (Bulk Delete) =======
@app.route("/delete_many_students", methods=["POST"])
def delete_many_students():
    students_col = db["students"]
    
    # 1. 從前端表單抓取所有被勾選的 checkbox 值 (這會是一個 list)
    #HTML裡的 name="selected_ids"
    selected_ids = request.form.getlist("selected_ids") 
    
    if not selected_ids:
        flash("❌ 你沒有勾選任何學生！")
        return redirect(url_for("manage_students"))

    try:
        # 2. 將字串 ID 轉換成 ObjectId 列表
        object_ids = [ObjectId(oid) for oid in selected_ids]
        
        # 3. 使用 $in 運算子進行批量刪除
        # 意思：刪除 _id 在 object_ids 列表裡面的所有資料
        result = students_col.delete_many({"_id": {"$in": object_ids}})
        
        # (選擇性) 連帶刪除選課紀錄
        db["enrollments"].delete_many({"student_id": {"$in": selected_ids}})

        flash(f"✅ 成功刪除 {result.deleted_count} 位學生 (批量刪除)")
    except Exception as e:
        flash(f"❌ 批量刪除失敗：{e}")

    return redirect(url_for("manage_students"))

# ======= 編輯學生 (Update) =======
@app.route("/edit_student/<student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    students_col = db["students"]

    if request.method == "POST":
        student_name = request.form.get("student_name")
        email = request.form.get("email")
        
        # MongoDB 更新語法
        students_col.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"student_name": student_name, "email": email}}
        )
        flash("✅ 更新成功")
        return redirect(url_for("manage_students"))

    # 讀取單筆資料
    r = students_col.find_one({"_id": ObjectId(student_id)})

    # 3. 改這裡
    return render_template("edit.html", r=r)
    


# ======= 課程管理 (CRUD) =======
@app.route("/courses", methods=["GET", "POST"])
def manage_courses():
    courses_col = db["courses"]

    if request.method == "POST":
        course_name = request.form.get("course_name")
        teacher = request.form.get("teacher")
        courses_col.insert_one({"course_name": course_name, "teacher": teacher})
        flash(f"✅ 課程 {course_name} 新增成功")
        return redirect(url_for("manage_courses"))

    rows = list(courses_col.find())

    tmpl = """
    <!doctype html>
    <title>課程管理</title>
    <style>body{font-family:Arial;margin:40px;}.flash{color:red;}</style>
    <body>
      <h2>課程管理</h2>
      {% with messages = get_flashed_messages() %}
          {% if messages %}{% for m in messages %}<p class="flash">{{ m }}</p>{% endfor %}{% endif %}
      {% endwith %}
      <form method="post">
        課程: <input name="course_name" required>
        教師: <input name="teacher">
        <button type="submit">新增</button>
      </form>
      <table border="1" cellpadding="5" style="margin-top:10px; border-collapse:collapse; width:100%">
        <tr><th>ID</th><th>課程名稱</th><th>教師</th><th>操作</th></tr>
        {% for r in rows %}
        <tr>
          <td>{{ r['_id'] }}</td>
          <td>{{ r['course_name'] }}</td>
          <td>{{ r['teacher'] }}</td>
          <td>
             <form method="post" action="{{ url_for('delete_course', course_id=r['_id']) }}">
                <button onclick="return confirm('刪除？')">刪除</button>
             </form>
          </td>
        </tr>
        {% endfor %}
      </table>
      <p><a href="{{ url_for('manage_students') }}">回學生管理</a></p>
    </body>
    """
    return render_template("courses.html", rows=rows)

@app.route("/delete_course/<course_id>", methods=["POST"])
def delete_course(course_id):
    db["courses"].delete_one({"_id": ObjectId(course_id)})
    db["enrollments"].delete_many({"course_id": course_id})
    flash("✅ 課程已刪除")
    return redirect(url_for("manage_courses"))


# ======= 選課管理 (關聯處理) =======
@app.route("/enrollments", methods=["GET", "POST"])
def manage_enrollments():
    enroll_col = db["enrollments"]

    if request.method == "POST":
        student_id = request.form.get("student_id") # 這是存字串ID
        course_id = request.form.get("course_id")   # 這是存字串ID
        
        if student_id and course_id:
            enroll_col.insert_one({
                "student_id": student_id,
                "course_id": course_id
            })
            flash("✅ 選課成功")
        return redirect(url_for("manage_enrollments"))

    # 準備下拉選單需要的資料
    all_students = list(db["students"].find())
    all_courses = list(db["courses"].find())
    
    # 讀取選課紀錄 (這裡需要稍微手動處理一下 Join 來顯示名字)
    raw_enrollments = list(enroll_col.find())
    display_enrollments = []
    
    for e in raw_enrollments:
        # 透過 ID 去查詢學生和課程的詳細資料
        # 注意：如果找不到資料(可能被刪了)，要給預設值
        stu = db["students"].find_one({"_id": ObjectId(e['student_id'])})
        cou = db["courses"].find_one({"_id": ObjectId(e['course_id'])})
        
        display_enrollments.append({
            "_id": e['_id'],
            "student_name": stu['student_name'] if stu else "未知學生",
            "course_name": cou['course_name'] if cou else "未知課程"
        })

    tmpl = """
    <!doctype html>
    <title>選課管理</title>
    <style>body{font-family:Arial;margin:40px;}</style>
    <body>
      <h2>選課管理</h2>
      <form method="post">
        學生: 
        <select name="student_id">
            {% for s in students %}
            <option value="{{ s['_id'] }}">{{ s['student_name'] }}</option>
            {% endfor %}
        </select>
        課程: 
        <select name="course_id">
            {% for c in courses %}
            <option value="{{ c['_id'] }}">{{ c['course_name'] }}</option>
            {% endfor %}
        </select>
        <button type="submit">選課</button>
      </form>

      <table border="1" cellpadding="5" style="margin-top:10px; width:100%">
        <tr><th>紀錄ID</th><th>學生</th><th>課程</th><th>操作</th></tr>
        {% for r in enrollments %}
        <tr>
            <td>{{ r['_id'] }}</td>
            <td>{{ r['student_name'] }}</td>
            <td>{{ r['course_name'] }}</td>
            <td>
                <form method="post" action="{{ url_for('delete_enrollment', eid=r['_id']) }}">
                    <button>退選</button>
                </form>
            </td>
        </tr>
        {% endfor %}
      </table>
      <p><a href="{{ url_for('manage_students') }}">回學生管理</a></p>
    </body>
    """
    return render_template("enrollments.html", students=all_students, courses=all_courses, enrollments=display_enrollments)


@app.route("/delete_enrollment/<eid>", methods=["POST"])
def delete_enrollment(eid):
    db["enrollments"].delete_one({"_id": ObjectId(eid)})
    flash("已退選")
    return redirect(url_for("manage_enrollments"))


# ======= 報表頁面 (Report) =======
@app.route("/report")
def report_page():
    # 使用 Python 迴圈來模擬 SQL JOIN (適合小資料量)
    enrollments = list(db["enrollments"].find())
    report_data = []

    for e in enrollments:
        stu = db["students"].find_one({"_id": ObjectId(e['student_id'])})
        cou = db["courses"].find_one({"_id": ObjectId(e['course_id'])})
        
        if stu and cou:
            report_data.append({
                "student_name": stu['student_name'],
                "course_name": cou['course_name'],
                "teacher": cou['teacher']
            })
    
    # 排序 (Python sort)
    report_data.sort(key=lambda x: x['student_name'])

    tmpl = """
    <!doctype html>
    <title>報表</title>
    <style>body{font-family:Arial;margin:40px;} table{width:100%; border-collapse:collapse;} td,th{border:1px solid #ccc; padding:8px;}</style>
    <body>
      <h2>選課報表 (MongoDB 版)</h2>
      <table>
        <tr><th>學生</th><th>課程</th><th>教師</th></tr>
        {% for r in rows %}
        <tr>
            <td>{{ r['student_name'] }}</td>
            <td>{{ r['course_name'] }}</td>
            <td>{{ r['teacher'] }}</td>
        </tr>
        {% endfor %}
      </table>
      <p><a href="{{ url_for('manage_students') }}">回首頁</a></p>
    </body>
    """
    return render_template("report.html", rows=report_data)

'''if __name__ == "__main__":
    app.run(debug=True)'''

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")