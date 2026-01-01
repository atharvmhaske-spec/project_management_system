from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key_for_flash_messages"
DATABASE = "projects.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')
    # Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                    project_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    member1 TEXT NOT NULL,
                    member2 TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ AUTH ROUTES ------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = username
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "error")
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# ------------------ PROJECT ROUTES ------------------

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    projects = conn.execute("SELECT * FROM projects").fetchall()
    conn.close()
    return render_template('index.html', projects=projects, username=session['username'])

@app.route('/add', methods=['POST'])
def add_project():
    if 'username' not in session:
        return redirect(url_for('login'))
    project_id = request.form['project_id']
    name = request.form['project_name']
    description = request.form['project_desc']
    status = request.form['project_status']
    member1 = request.form['member1']
    member2 = request.form['member2']

    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO projects (project_id, name, description, status, member1, member2) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, name, description, status, member1, member2)
        )
        conn.commit()
        flash("Project added successfully!", "success")
    except sqlite3.IntegrityError:
        flash("Project ID already exists!", "error")
    conn.close()
    return redirect(url_for('index'))

@app.route('/update/<int:project_id>', methods=['POST'])
def update_status(project_id):
    new_status = request.form['status']
    conn = get_db_connection()
    conn.execute("UPDATE projects SET status = ? WHERE project_id = ?", (new_status, project_id))
    conn.commit()
    conn.close()
    flash("Project status updated!", "success")
    return redirect(url_for('index'))

@app.route('/delete/<int:project_id>')
def delete_project(project_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
    conn.commit()
    conn.close()
    flash("Project deleted successfully!", "success")
    return redirect(url_for('index'))

@app.route('/view/<int:project_id>')
def view_project(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
    conn.close()
    if project:
        return render_template('view_project.html', project=project)
    else:
        flash("Project not found!", "error")
        return redirect(url_for('index'))

@app.route('/members/<int:project_id>')
def view_members(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
    conn.close()
    if project:
        members = [project['member1'], project['member2']]
        return render_template('members.html', project=project, members=members)
    else:
        flash("Project not found!", "error")
        return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
