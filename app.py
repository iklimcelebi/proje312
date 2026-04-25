from flask import Flask, render_template, request, redirect, session
from models import db, User, Book # <-- Book buraya eklendi

app = Flask(__name__)
app.secret_key = "secret123"

# VERİTABANI BAĞLANTISI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

# DATABASE OLUŞTUR (Tabloları hazırlar)
with app.app_context():
    db.create_all()
    # Admin oluştur (Eğer yoksa)
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="1234", role="admin")
        db.session.add(admin)
        db.session.commit()

# --- ROUTES (SAYFALAR) ---

@app.route("/")
def home():
    books = Book.query.all() # Veritabanındaki tüm kitapları çek
    return render_template("home.html", books=books)

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

@app.route("/admin")
def admin():
    if "role" not in session or session["role"] != "admin":
        return "Yetkisiz erişim!"
    
    books = Book.query.all() # Admin sayfasında satışları göstermek için kitapları çekiyoruz
    return render_template("admin.html", books=books)

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    # Güvenlik Kontrolü: Sadece admin girebilir
    if "role" not in session or session["role"] != "admin":
        return "Kitap eklemek için admin yetkisi gerekir!"

    if request.method == "POST":
        name = request.form["name"]
        author = request.form["author"]
        price = float(request.form["price"])

        new_book = Book(name=name, author=author, price=price)
        db.session.add(new_book)
        db.session.commit()
        return "Kitap başarıyla eklendi! <a href='/'>Ana Sayfa</a>"

    return render_template("add_book.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/add_to_cart/<int:book_id>")
def add_to_cart(book_id):
    if "cart" not in session:
        session["cart"] = []
    
    # Sepete kitap ID'sini ekle
    temp_cart = session["cart"]
    temp_cart.append(book_id)
    session["cart"] = temp_cart
    return redirect("/")

@app.route("/checkout")
def checkout():
    if "cart" not in session or not session["cart"]:
        return "Sepetiniz boş!"

    for book_id in session["cart"]:
        book = Book.query.get(book_id)
        if book:
            book.sold_count += 1 # Satılan adedi artır
    
    db.session.commit()
    session.pop("cart", None) # Sepeti temizle
    return "Satın alma başarılı! <a href='/'>Ana Sayfa</a>"

@app.route("/reset_system")
def reset_system():
    # Güvenlik kontrolü: Sadece admin sıfırlayabilsin
    if "role" not in session or session["role"] != "admin":
        return "Bu işlem için admin girişi yapmalısınız!"

    # 1. Mevcut veritabanını tamamen temizle
    db.drop_all()
    db.create_all()

    # 2. Tertemiz ilk verileri (Admin ve Demo Kitaplar) ekle
    admin = User(username="admin", password="1234", role="admin")
    db.session.add(admin)

    demo_kitaplar = [
        Book(name="Nutuk", author="Mustafa Kemal Atatürk", price=150.0, sold_count=0),
        Book(name="Simyacı", author="Paulo Coelho", price=120.0, sold_count=0),
        Book(name="1984", author="George Orwell", price=100.0, sold_count=0)
    ]
    db.session.add_all(demo_kitaplar)
    
    db.session.commit()
    
    # Sıfırlama sonrası ana sayfaya yönlendir
    session.clear() # Güvenlik için oturumu kapatıyoruz
    return "Sistem sıfırlandı! <a href='/login'>Tekrar Giriş Yap</a>"

# BU SATIR HER ZAMAN EN SONDA OLMALI!
if __name__ == "__main__":
    app.run(debug=True)