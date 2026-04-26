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

@app.route("/")
def home():
    # URL'deki ?search= kelimesini yakalar
    search_query = request.args.get('search') 
    
    if search_query:
        # Veritabanında isim veya yazar içinde bu kelimeyi ara
        books = Book.query.filter(
            (Book.name.ilike(f"%{search_query}%")) | 
            (Book.author.ilike(f"%{search_query}%"))
        ).all()
    else:
        # Arama yoksa tüm kitapları getir
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
        image = request.form["image"]  # 🔥 YENİ EKLENDİ

        new_book = Book(
            name=name,
            author=author,
            price=price,
            image=image   # 🔥 BURAYA EKLENDİ
        )

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
    # 1. Mevcut sepeti al, yoksa veya liste ise boş bir sözlük yarat
    current_cart = session.get("cart", {})
    if not isinstance(current_cart, dict):
        current_cart = {}

    # 2. Kitap ID'sini string'e çevir (JSON anahtarları için daha güvenlidir)
    book_id_str = str(book_id)

    # 3. Sayıyı artır
    if book_id_str in current_cart:
        current_cart[book_id_str] += 1
    else:
        current_cart[book_id_str] = 1
        
    # 4. KRİTİK NOKTA: Session'ı yeni bir sözlükle tamamen güncelle
    # Bu, Flask'ın "değişiklik var" uyarısını tetiklemesini sağlar.
    session["cart"] = dict(current_cart) 
    session.modified = True
    
    return redirect("/")

@app.route("/cart")
def cart():
    # Eğer sepet yoksa VEYA sepet hala eski tipte (liste) ise, hatayı önlemek için sepeti boşalt ve sözlük yap
    if "cart" not in session or not isinstance(session["cart"], dict):
        session["cart"] = {}
        return render_template("cart.html", items=[], total=0)

    cart = session["cart"]
    cart_items = []
    total = 0

    # Artık güvenle .items() kullanabiliriz çünkü yukarıda liste olup olmadığını kontrol ettik
    for book_id, quantity in cart.items():
        book = Book.query.get(int(book_id))
        if book:
            item_total = book.price * quantity
            total += item_total
            
            # Kitap nesnesine geçici bilgiler ekleyelim (Template'de kullanmak için)
            book.quantity = quantity
            book.item_total = item_total
            cart_items.append(book)

    return render_template("cart.html", items=cart_items, total=total)


@app.route("/remove_from_cart/<int:book_id>")
def remove_from_cart(book_id):
    if "cart" in session:
        cart = session["cart"]
        book_id_str = str(book_id)
        
        if book_id_str in cart:
            del cart[book_id_str] # Kitabı sözlükten tamamen kaldır
            session["cart"] = cart
            session.modified = True
            
    return redirect("/cart")

# CHECKOUT
@app.route("/checkout")
def checkout():
    if "cart" not in session or not session["cart"]:
        return redirect("/")

    cart = session["cart"]
    for book_id, quantity in cart.items():
        book = Book.query.get(int(book_id))
        if book:
            book.sold_count += quantity # Adet kadar artırıyoruz

    db.session.commit()
    session.pop("cart", None) # Sepeti temizle
    return redirect("/")

# RESET 🔥
@app.route("/reset_system")
def reset_system():
    if "role" not in session or session["role"] != "admin":
        return "Yetkisiz!"

    db.drop_all()
    db.create_all()

    admin = User(username="admin", password="1234iklim+", role="admin")
    db.session.add(admin)

    demo_books = [
        Book(name="Nutuk", 
            author="Mustafa Kemal Atatürk", 
            price=150, 
            image="static/images/kitap1.jpg"),

        Book(name="1984", 
            author="George Orwell", 
            price=100, 
            image="static/images/kitap2.jpg"),
        
        Book(name="Simyacı", 
            author="Paulo Coelho", 
            price=120, 
            image="static/images/kitap3.jpg"),
        
        Book(name="Suç ve Ceza", 
            author="Dostoyevski", 
            price=140, 
            image="static/images/kitap4.jpg"),
        
        Book(name="Sefiller", 
            author="Victor Hugo", 
            price=160, 
            image="static/images/kitap5.jpg"),
        
        Book(name="Hayvan Çiftliği", 
            author="George Orwell", 
            price=80, 
            image="static/images/kitap6.jpg"),
        
        Book(name="Kürk Mantolu Madonna", 
            author="Sabahattin Ali", 
            price=90, 
            image="static/images/kitap7.jpg"),
        
        Book(name="Fahrenheit 451",     
            author="Ray Bradbury", 
            price=110, 
            image="static/images/kitap8.jpg"),
        
        Book(name="Cesur Yeni Dünya", 
            author="Aldous Huxley", 
            price=115, 
            image="static/images/kitap9.jpg"),
        
        Book(name="Şeker Portakalı", 
            author="Jose Mauro de Vasconcelos", 
            price=85, 
            image="static/images/kitap10.jpg"),
        
        Book(name="Küçük Prens", 
            author="Antoine de Saint-Exupéry", 
            price=70, 
            image="static/images/kitap11.jpg"),
        
        Book(name="Yabancı", 
            author="Albert Camus", 
            price=95, 
            image="static/images/kitap12.jpg"),
        
        Book(name="Dönüşüm", 
            author="Franz Kafka", 
            price=75, 
            image="static/images/kitap13.jpg"),
        
        Book(name="Martin Eden", 
            author="Jack London", 
            price=130, 
            image="static/images/kitap14.jpg"),
        
        Book(name="Tutunamayanlar", 
            author="Oğuz Atay", 
            price=180, 
            image="static/images/kitap15.jpg")
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