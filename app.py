from flask import Flask, render_template, request, redirect, session
from models import db, User, Book

app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

# DATABASE
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="1234", role="admin")
        db.session.add(admin)
        db.session.commit()

# HOME
@app.route("/")
def home():
    books = Book.query.all()
    return render_template("home.html", books=books)

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user"] = user.username
            session["role"] = user.role
            return redirect("/admin") if user.role == "admin" else redirect("/")

        return "Hatalı giriş!"

    return render_template("login.html")

# REGISTER 🔥
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "Bu kullanıcı zaten var!"

        new_user = User(username=username, password=password, role="user")
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

# ADMIN
@app.route("/admin")
def admin():
    if "role" not in session or session["role"] != "admin":
        return "Yetkisiz erişim!"

    books = Book.query.all()
    return render_template("admin.html", books=books)

# ADD BOOK
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if "role" not in session or session["role"] != "admin":
        return "Yetkisiz!"

    if request.method == "POST":
        name = request.form["name"]
        author = request.form["author"]
        price = float(request.form["price"])

        new_book = Book(name=name, author=author, price=price)
        db.session.add(new_book)
        db.session.commit()

        return redirect("/admin")

    return render_template("add_book.html")

# DELETE BOOK 🔥
@app.route("/delete_book/<int:book_id>")
def delete_book(book_id):
    if "role" not in session or session["role"] != "admin":
        return "Yetkisiz!"

    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()

    return redirect("/admin")

# CART
@app.route("/add_to_cart/<int:book_id>")
def add_to_cart(book_id):
    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]
    cart.append(book_id)
    session["cart"] = cart

    return redirect("/")

# CHECKOUT
@app.route("/checkout")
def checkout():
    if "cart" not in session or not session["cart"]:
        return "Sepet boş!"

    for book_id in session["cart"]:
        book = Book.query.get(book_id)
        if book:
            book.sold_count += 1

    db.session.commit()
    session.pop("cart", None)

    return redirect("/")

# RESET 🔥
@app.route("/reset_system")
def reset_system():
    if "role" not in session or session["role"] != "admin":
        return "Yetkisiz!"

    db.drop_all()
    db.create_all()

    admin = User(username="admin", password="1234", role="admin")
    db.session.add(admin)

    demo_books = [
        Book(name="Nutuk", author="Atatürk", price=150),
        Book(name="1984", author="George Orwell", price=100),
        Book(name="Simyacı", author="Paulo Coelho", price=120)
    ]

    db.session.add_all(demo_books)
    db.session.commit()

    session.clear()
    return redirect("/login")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# BU SATIR HER ZAMAN EN SONDA OLMALI!
if __name__ == "__main__":
    app.run(debug=True)