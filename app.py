import MySQLdb, os, hashlib
from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

# Mengatur ekstensi yang diperbolehkan untuk diupload
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

app = Flask(__name__)

# Setting flask-mail untuk gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'ravencase.testflaskmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'testflaskmail'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# Mengatur lokasi folder untuk menempatkan file yang akan diupload
# './static/images/uploads/mockups' and './static/images/uploads/banners'
app.config['MOCKUPS_UPLOAD_FOLDER'] = '\\'.join('./static/images/uploads/mockups'.split("/"))
app.config['BANNERS_UPLOAD_FOLDER'] = '\\'.join('./static/images/uploads/banners'.split("/"))

app.config['SECRET_KEY'] = 'ravencase_##$@%%'

# Mengatur lamanya session akan tersimpan (opsional)
app.permanent_session_lifetime = timedelta(days=1)

# Mengatur konfigurasi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tugasflask'

mysql = MySQL(app)

@app.route('/')
def index():
    # Menampilkan file html add_product.html, dan mengirim data title
    # Jika use login, maka akan menampilkan menu khusus saat user telah login
    if "name" in session:
        session["loggedin"] = True
    # Sebaliknya, maka akan menampilkan menu untuk login/register
    else:
        session["loggedin"] = False
    return render_template('index.html', title="100% QUALITY CUSTOM CASES", home_status="active", nav_place="fixed-top")

@app.route('/login', methods=['GET','POST'])
def login():
    # Proses login
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        email = request.form['email']
        # Mengubah password yang diketik dari tipe teks ke md5
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        # Proses komunikasi dengan database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        result = cursor.fetchone()
        # Apabila inputan sama dengan atau cocok dengan data pada database,
        # Maka statemen berikut akan diset
        if result:
            # Session user
            # Menyalakan timer session
            session.permanent = True
            # Fungsi loggedin ini sebagai statemen untuk menampilkan menu khusus saat user sudah login
            session['loggedin'] = True
            session['id'] = result['id']
            session['name'] = result['name']
            return redirect(url_for('index'))
        # Apabila tidak cocok maka akan tampil pesan flash berikut
        else:
            flash('Incorrect username/password!')
    else:
        # User akan diredirect ke page index apalagi mengakses halaman login pada saat user tsb sudah login
        if "name" in session:
            return redirect(url_for('index'))
    # Apabila requestnya GET, maka sistem akan menampilkan form login
    return render_template('auth/login.html', footer_place="fixed-bottom", login_status="active")

@app.route('/logout')
def logout():
    # Proses logout
    # Mengatur agar tombol login/register tampil kembali
    session['loggedin'] = False
    # Menghapus semua data session
    session.pop('id', None)
    session.pop('name', None)
    # Kemudian kembali ke landing page
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    # Proses register
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form:
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        id = None
        role_id = None
        name = request.form['name']
        email = request.form['email']
        # Mengubah password yang diketik dari tipe teks ke md5
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (id, role_id, name, email, password, created_at, updated_at)
        # Proses komunikasi dengan database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        users = cursor.fetchone()
        # Jika data yang diinput sudah ada di database, maka akan muncul pesan berikut
        if users:
            flash('Email already registered!')
            return redirect(url_for('register'))
        # Jika data yang diinput unik, maka data akan dikirim ke database
        else:
            cursor.execute("""INSERT INTO users VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s")""" % data)
            mysql.connection.commit()
            cursor.close()
            flash('Successfully registered! You can login now!')

            # Mengirim email greetings new user
            msg = Message("Registration Success! 🎉", sender=("Raven Case Team", app.config.get("MAIL_USERNAME")),
                          recipients=[(name, email)])
            msg.html = render_template('email/welcome_user.html')

            try:
                mail = Mail(app)
                mail.connect()
                mail.send(msg)
                print('Email sent!')
                return redirect(url_for('login'))
            except:
                return print('Failed to send email!')
    # Apabila requestnya GET, maka sistem akan menampilkan form register
    else:
        return render_template('auth/register.html', footer_place="fixed-bottom", register_status="active")

@app.route('/products', methods=['GET','POST'])
def products():
    # Fungsi untuk menampilkan produk
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()

    # Fungsi untuk menampilkan banner
    # Proses komunikasi dengan database
    cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor2.execute("SELECT * FROM banners")
    result2 = cursor2.fetchall()
    return render_template('products/index.html', title="100% QUALITY CUSTOM CASES", cases_status="active", nav_place="fixed-top",
                           products=result, banners=result2, filename='/static/images/')

@app.template_filter()
def currencyFormat(value):
    # Fungsi untuk mengubah harga menjadi format Rupiah
    import locale
    locale.setlocale(locale.LC_NUMERIC, 'IND')
    rupiah = locale.format("%.*f", (0, value), True)
    return "Rp{}".format(rupiah)

@app.route('/products/<string:id>', methods=['GET','POST'])
def showProduct(id):
    # Fungsi untuk menampilkan detail produk
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    result = cursor.fetchall()

    # Fungsi untuk menampilkan device
    # Proses komunikasi dengan database
    cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor2.execute("SELECT * FROM devices")
    result2 = cursor2.fetchall()
    return render_template('products/show.html', cases_status="active", nav_place="fixed-top", footer_place="fixed-bottom", products=result, devices=result2)

def allowed_file(filename):
    # Fungsi untuk mengecek filename dari data yang diinput
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    # Fungsi untuk menambahkan produk
    if request.method == 'POST':
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        id = None
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        # Jika form kosong, maka akan muncul pesan berikut
        if 'mockup' not in request.files:
            flash('Please upload mockups!')
            return redirect(url_for('addproduct'))
        mockup = request.files['mockup']
        # Jika form mockup kosong, maka muncul pesan berikut
        if mockup.filename == '':
            flash('No selected file')
            return redirect(url_for('addproduct'))
        # Jika form mockup diisi, maka filename mockup akan diubah menjadi format berikut
        if mockup and allowed_file(mockup.filename):
            filename = secure_filename(mockup.filename)
            mockup.save(os.path.join(app.config['MOCKUPS_UPLOAD_FOLDER'], filename))
        mockup = "uploads/mockups/"+(mockup.filename).replace(" ", "_")
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (id, title, description, price, mockup, created_at, updated_at)
        # Proses komunikasi dengan database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''INSERT INTO products VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s")''' % data)
        mysql.connection.commit()
        cursor.close()
        flash('Success add product!')
        return redirect(url_for('addproduct'))
    # Apabila requestnya GET, maka sistem akan menampilkan form tambah produk
    else:
        return render_template('admin/products/add_product.html')

@app.route('/manageproduct', methods=['GET','POST'])
def manageproduct():
    # Fungsi untuk menampilkan list produk
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()
    return render_template('admin/products/manage_product.html', products=result)

@app.route('/editproduct/<id>', methods=['GET','POST'])
def editproduct(id):
    # Fungsi untuk mengedit produk
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id='%s'" % id)
    result = cursor.fetchone()
    if request.method == 'POST':
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        mockup = request.files['mockup']
        # Jika form mockup diisi, maka filename mockup akan diubah menjadi format berikut
        if mockup and allowed_file(mockup.filename):
            filename = secure_filename(mockup.filename)
            mockup.save(os.path.join(app.config['MOCKUPS_UPLOAD_FOLDER'], filename))
        mockup = "uploads/mockups/"+(mockup.filename).replace(" ", "_")
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Proses komunikasi dengan database
        cursor.execute('''
            UPDATE products SET title="%s", description="%s", price="%s", mockup="%s", updated_at="%s"
            WHERE id="%s"
        ''' % (title, description, price, mockup, updated_at, id))
        mysql.connection.commit()
        cursor.close()
        flash('Success update product!')
        return redirect(url_for('manageproduct'))
    # Apabila requestnya GET, maka sistem akan menampilkan form edit produk
    else:
        cursor.close()
        return render_template('admin/products/edit_product.html', data=result)

@app.route('/deleteproduct/<id>', methods=['GET','POST'])
def deleteproduct(id):
    # Fungsi untuk menghapus produk
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM products WHERE id='%s'" % id)
    mysql.connection.commit()
    cursor.close()
    flash('Successfully deleted!')
    return redirect(url_for('manageproduct'))

@app.route('/managedevice', methods=['GET','POST'])
def managedevice():
    # Fungsi untuk menampilkan list device
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM devices")
    result = cursor.fetchall()
    return render_template('admin/devices/manage_device.html', devices=result)

@app.route('/adddevice', methods=['GET','POST'])
def adddevice():
    # Fungsi untuk menambahkan device
    if request.method == 'POST':
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        id = None
        name = request.form['name']
        # Jika form kosong, maka akan muncul pesan berikut
        if name == '':
            flash('Please input device name!')
            return redirect(url_for('adddevice'))
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (id, name, created_at, updated_at)
        # Proses komunikasi dengan database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''INSERT INTO devices VALUES("%s", "%s", "%s", "%s")''' % data)
        mysql.connection.commit()
        cursor.close()
        flash('Success add device!')
        return redirect(url_for('managedevice'))
    # Apabila requestnya GET, maka sistem akan menampilkan form tambah device
    else:
        return render_template('admin/devices/add_device.html')

@app.route('/editdevice/<id>', methods=['GET','POST'])
def editdevice(id):
    # Fungsi untuk mengedit device
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM devices WHERE id='%s'" % id)
    result = cursor.fetchone()
    if request.method == 'POST':
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        name = request.form['name']
        # Jika form kosong, maka akan muncul pesan berikut
        if name == '':
            flash('Please input device name!')
            return redirect(url_for('editdevice', id=id))
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Proses komunikasi dengan database
        cursor.execute('''
                    UPDATE devices SET name="%s", updated_at="%s"
                    WHERE id="%s"
                ''' % (name, updated_at, id))
        mysql.connection.commit()
        cursor.close()
        flash('Success update device!')
        return redirect(url_for('managedevice'))
    # Apabila requestnya GET, maka sistem akan menampilkan form edit device
    else:
        cursor.close()
        return render_template('admin/devices/edit_device.html', data=result)

@app.route('/deletedevice/<id>', methods=['GET','POST'])
def deletedevice(id):
    # Fungsi untuk menghapus device
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM devices WHERE id='%s'" % id)
    mysql.connection.commit()
    cursor.close()
    flash('Successfully deleted!')
    return redirect(url_for('managedevice'))

@app.route('/managebanner', methods=['GET','POST'])
def managebanner():
    # Fungsi untuk menampilkan list banner
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM banners")
    result = cursor.fetchall()
    return render_template('admin/banners/manage_banner.html', banners=result)

@app.route('/addbanner', methods=['GET','POST'])
def addbanner():
    # Fungsi untuk menambahkan banner
    if request.method == 'POST':
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        id = None
        # Jika form kosong, maka akan muncul pesan berikut
        if 'banner' not in request.files:
            flash('Please upload banner!')
            return redirect(url_for('addbanner'))
        banner = request.files['banner']
        # Jika form kosong, maka akan muncul pesan berikut
        if banner.filename == '':
            flash('No selected file')
            return redirect(url_for('addbanner'))
        # Jika form banner diisi, maka filename banner akan diubah menjadi format berikut
        if banner and allowed_file(banner.filename):
            filename = secure_filename(banner.filename)
            banner.save(os.path.join(app.config['BANNERS_UPLOAD_FOLDER'], filename))
        banner = "uploads/banners/"+(banner.filename).replace(" ", "_")
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (id, banner, created_at, updated_at)
        # Proses komunikasi dengan database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''INSERT INTO banners VALUES("%s", "%s", "%s", "%s")''' % data)
        mysql.connection.commit()
        cursor.close()
        flash('Success add banner!')
        return redirect(url_for('managebanner'))
    # Apabila requestnya GET, maka sistem akan menampilkan form edit device
    else:
        return render_template('admin/banners/add_banner.html')

@app.route('/editbanner/<id>', methods=['GET','POST'])
def editbanner(id):
    # Fungsi untuk mengedit banner
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM banners WHERE id='%s'" % id)
    result = cursor.fetchone()
    if request.method == 'POST':
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        # Jika form kosong, maka akan muncul pesan berikut
        if 'banner' not in request.files:
            flash('Please upload banner!')
            return redirect(url_for('editbanner', id=id))
        banner = request.files['banner']
        # Jika form kosong, maka akan muncul pesan berikut
        if banner.filename == '':
            flash('No selected file')
            return redirect(url_for('editbanner', id=id))
        # Jika form banner diisi, maka filename banner akan diubah menjadi format berikut
        if banner and allowed_file(banner.filename):
            filename = secure_filename(banner.filename)
            banner.save(os.path.join(app.config['BANNERS_UPLOAD_FOLDER'], filename))
        banner = "uploads/banners/"+(banner.filename).replace(" ", "_")
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Proses komunikasi dengan database
        cursor.execute('''
                    UPDATE banners SET banner="%s", updated_at="%s"
                    WHERE id="%s"
                ''' % (banner, updated_at, id))
        mysql.connection.commit()
        cursor.close()
        flash('Success update banner!')
        return redirect(url_for('managebanner'))
    # Apabila requestnya GET, maka sistem akan menampilkan form edit banner
    else:
        cursor.close()
        return render_template('admin/banners/edit_banner.html', data=result)

@app.route('/deletebanner/<id>', methods=['GET','POST'])
def deletebanner(id):
    # Fungsi untuk menghapus banner
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM banners WHERE id='%s'" % id)
    mysql.connection.commit()
    cursor.close()
    flash('Successfully deleted!')
    return redirect(url_for('managebanner'))

@app.route('/admin')
def admin():
    # Fungsi untuk menampilkan halaman admin
    return render_template('/admin/index.html')

if __name__ == '__main__':
    app.run()
