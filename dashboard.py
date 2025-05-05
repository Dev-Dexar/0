from flask import Flask, render_template, request, redirect, url_for, send_file, session
from pymongo import MongoClient
import csv
import io
from config import MONGO_URI, ADMIN_SECRET

app = Flask(__name__)
app.secret_key = 'ADMIN_SECRET'  # ⚠️ Change this to a strong secret in production!

client = MongoClient(MONGO_URI)
db = client["subscription_bot"]
users = db["users"]
paid = db["paid_users"]

# 🔐 Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_SECRET:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        return render_template("login.html", error="Invalid password")
    return render_template("login.html")

# 🚪 Logout route
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# 📊 Dashboard page
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))

    search_user = request.args.get("user")
    if search_user:
        user = paid.find_one({"user_id": int(search_user)})
        return render_template("user.html", user=user)

    all_users = list(paid.find({}))
    return render_template("dashboard.html", users=all_users)

# 📁 CSV Export route
@app.route('/export_csv')
def export_csv():
    if not session.get('admin'):
        return redirect(url_for('login'))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["User ID", "Plan", "Status", "Next Due", "Payment Link"])

    for u in paid.find({}):
        writer.writerow([
            u.get("user_id"),
            u.get("plan_type", "N/A"),
            u.get("status", "N/A"),
            u.get("next_due_on", "N/A"),
            u.get("payment_link", "N/A")
        ])

    output.seek(0)
    return send_file(io.BytesIO(output.read().encode()), download_name="paid_users.csv", as_attachment=True)

# 🏁 Call this in main.py
def run_dashboard():
    app.run(debug=False, port=8080, use_reloader=False)
