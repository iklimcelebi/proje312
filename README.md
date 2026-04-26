# 📚 Kitabevi Online Satış Sistemi (Flask)

Bu proje, Python ve Flask kullanılarak geliştirilmiş basit bir **kitap satış (e-ticaret) web uygulamasıdır**.
Kullanıcılar kitapları görüntüleyebilir, sepete ekleyebilir ve satın alma işlemi gerçekleştirebilir.
Admin kullanıcı ise kitap yönetimi ve satış takibini yapabilir.

---

## 🚀 Özellikler

###  Kullanıcı İşlemleri

* Kayıt olma ve giriş yapma
* Kitapları listeleme
* Kitap arama (isim veya yazar)
* Sepete ürün ekleme
* Sepetten ürün çıkarma
* Satın alma (checkout)

###  Sepet Sistemi

* Session tabanlı sepet yönetimi
* Ürün adet takibi
* Toplam fiyat hesaplama

###  Admin Paneli

* Kitap ekleme
* Kitap silme
* Satış raporu görüntüleme
* Sistem sıfırlama (demo veriler yüklenir)


---

##  Kullanılan Teknolojiler

* Python
* Flask
* SQLite
* SQLAlchemy
* HTML / CSS

---

##  Proje Yapısı

```
proje312/
│
├── app.py
├── models.py
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── cart.html
│   ├── admin.html
│   └── add_book.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
│
├── instance/
│   └── database.db  (gitignore içinde)
│
└── .gitignore
```

---

##  Varsayılan Admin Bilgileri

```
Kullanıcı adı: admin
Şifre: 1234admin
```

---

##  Notlar

* Bu proje eğitim amaçlı geliştirilmiştir.
* Şifreler düz metin (plain text) olarak tutulmaktadır.
* Gerçek projelerde şifreler hashlenmelidir.

---
