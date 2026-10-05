from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
DB = "library.db"

HTML = """
<!doctype html>
<html>
<head>
    <title>Library Management</title>
    <style>
        body { font-family: Arial; margin: 30px; background: #f5f5f5; }
        h1 { color: #222; }
        form { background: white; padding: 15px; margin-bottom: 20px; }
        input, button { padding: 8px; margin: 4px; }
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { padding: 9px; border: 1px solid #ccc; text-align: left; }
        th { background: #eee; }
        a { margin-right: 8px; }
    </style>
</head>
<body>
<h1>Library Management System</h1>

<form method="post" action="/add">
    <h3>Add Book</h3>
    <input name="title" placeholder="Title" required>
    <input name="author" placeholder="Author" required>
    <input name="category" placeholder="Category">
    <input name="isbn" placeholder="ISBN">
    <input name="publisher" placeholder="Publisher">
    <input name="quantity" type="number" min="1" value="1">
    <button type="submit">Add Book</button>
</form>

<form method="get" action="/">
    <input name="search" value="{{ search }}" placeholder="Search title/author/category">
    <button type="submit">Search</button>
    <a href="/">View All</a>
</form>

<table>
<tr>
    <th>ID</th><th>Title</th><th>Author</th><th>Category</th>
    <th>ISBN</th><th>Publisher</th><th>Quantity</th><th>Available</th><th>Actions</th>
</tr>
{% for b in books %}
<tr>
    <td>{{ b[0] }}</td><td>{{ b[1] }}</td><td>{{ b[2] }}</td><td>{{ b[3] }}</td>
    <td>{{ b[4] }}</td><td>{{ b[5] }}</td><td>{{ b[6] }}</td>
    <td>{{ b[7] }}</td>
    <td>
        <a href="/issue/{{ b[0] }}">Issue</a>
        <a href="/return/{{ b[0] }}">Return</a>
        <a href="/delete/{{ b[0] }}">Delete</a>
    </td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

def get_db():
    conn = sqlite3.connect(DB)
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT,
            isbn TEXT,
            publisher TEXT,
            quantity INTEGER NOT NULL,
            available INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    conn = get_db()
    if search:
        like = f"%{search}%"
        books = conn.execute("""
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
            ORDER BY id
        """, (like, like, like)).fetchall()
    else:
        books = conn.execute("SELECT * FROM books ORDER BY id").fetchall()
    conn.close()
    return render_template_string(HTML, books=books, search=search)

@app.post("/add")
def add_book():
    data = request.form
    quantity = max(1, int(data.get("quantity", 1)))
    conn = get_db()
    conn.execute("""
        INSERT INTO books(title, author, category, isbn, publisher, quantity, available)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (data["title"], data["author"], data.get("category", ""),
          data.get("isbn", ""), data.get("publisher", ""), quantity, quantity))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    conn = get_db()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/issue/<int:book_id>")
def issue_book(book_id):
    conn = get_db()
    row = conn.execute("SELECT available FROM books WHERE id = ?", (book_id,)).fetchone()
    if row and row[0] > 0:
        conn.execute("UPDATE books SET available = available - 1 WHERE id = ?", (book_id,))
        conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/return/<int:book_id>")
def return_book(book_id):
    conn = get_db()
    row = conn.execute("SELECT quantity, available FROM books WHERE id = ?", (book_id,)).fetchone()
    if row and row[1] < row[0]:
        conn.execute("UPDATE books SET available = available + 1 WHERE id = ?", (book_id,))
        conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.get("/health")
def health():
    return {"status": "ok"}

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
