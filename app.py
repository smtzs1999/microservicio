# app.py
from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, os

app = Flask(__name__)
app.secret_key = "secret123"

DB_PATH = "gym.db"

# ---- Crear base de datos si no existe ----
def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''CREATE TABLE users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            email TEXT UNIQUE,
                            password TEXT)''')
            conn.execute('''CREATE TABLE classes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            instructor TEXT,
                            spots INTEGER)''')
            conn.execute('''CREATE TABLE bookings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            class_id INTEGER,
                            FOREIGN KEY(user_id) REFERENCES users(id),
                            FOREIGN KEY(class_id) REFERENCES classes(id))''')
            conn.executemany(
                "INSERT INTO classes (name, instructor, spots) VALUES (?, ?, ?)",
                [
                    ("Yoga", "Alex", 10),
                    ("Pilates", "Maria", 5),
                    ("Crossfit", "John", 8),
                    ("Zumba", "Alice", 7)
                ]
            )
            conn.commit()
            print("✅ Base de datos creada con clases de ejemplo")

# ---- Ruta raíz (prueba del microservicio en JSON) ----
@app.route("/api")
def api_home():
    return jsonify({"message": "Hola desde el microservicio de reservas de gimnasio!"})

# ---- Home principal ----
@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')

# ---- Login ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
        if user:
            session['user'] = {'id': user[0], 'name': user[1], 'email': user[2]}
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Credenciales incorrectas")
    return render_template('login.html')

# ---- Registro ----
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        if password != confirm:
            return render_template('register.html', error="Las contraseñas no coinciden")
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)", (name, email, password))
                conn.commit()
            return redirect('/login')
        except:
            return render_template('register.html', error="El correo ya está registrado")
    return render_template('register.html')

# ---- Dashboard ----
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    with sqlite3.connect(DB_PATH) as conn:
        classes = conn.execute("SELECT * FROM classes").fetchall()
        user_id = session['user']['id']
        bookings = conn.execute("""SELECT c.name, c.instructor 
                                   FROM bookings b 
                                   JOIN classes c ON b.class_id = c.id 
                                   WHERE b.user_id=?""", (user_id,)).fetchall()
    return render_template('dashboard.html', user=session['user'], classes=classes, bookings=bookings)

# ---- Reservar clase ----
@app.route('/book/<int:class_id>')
def book_class(class_id):
    if 'user' not in session:
        return redirect('/login')
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO bookings (user_id,class_id) VALUES (?,?)", (session['user']['id'], class_id))
        conn.execute("UPDATE classes SET spots = spots - 1 WHERE id=? AND spots > 0", (class_id,))
        conn.commit()
    return redirect('/dashboard')

# ---- Cerrar sesión ----
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
