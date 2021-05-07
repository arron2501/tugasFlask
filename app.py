import MySQLdb, os, hashlib, pdfkit, jinja2
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
app.config['MAIL_ASCII_ATTACHMENTS'] = True

# Mengatur lokasi folder untuk menempatkan file yang akan diupload
# './static/images/uploads/mockups' and './static/images/uploads/banners'
app.config['MOCKUPS_UPLOAD_FOLDER'] = '\\'.join('./static/images/uploads/mockups'.split("/"))
app.config['BANNERS_UPLOAD_FOLDER'] = '\\'.join('./static/images/uploads/banners'.split("/"))

app.config['SECRET_KEY'] = 'ravencase_##$@%%'

# Mengatur lamanya session akan tersimpan (opsional)
app.permanent_session_lifetime = timedelta(days=1)

# Konfigurasi pdfkit
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
app.config['PDF_FOLDER'] = os.path.realpath('.') + \
   '/static/pdf'

# Mengatur konfigurasi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tugasflask'

mysql = MySQL(app)

@app.route('/')
def index():
    # Menampilkan file html add_product.html, dan mengirim data title
    # Jika user login, maka akan menampilkan menu khusus saat user telah login
    if "name" in session:
        session["loggedin"] = True
    # Sebaliknya, maka akan menampilkan menu untuk login/register
    else:
        session["loggedin"] = False
    return render_template('index.html', title="100% QUALITY CUSTOM CASES", home_status="active", nav_place="fixed-top")

@app.route('/contactus', methods=['GET','POST'])
def contactus():
    # Harus login terlebih dahulu
    if session["loggedin"] == True:
        if request.method == 'POST':
            # Mengambil data dari form
            subject = request.form['subject']
            message = request.form['message']
            # Proses mengirim email
            msg = Message(subject, sender=(session.get('name'), app.config.get("MAIL_USERNAME")),
                          recipients=[("Raven Case Team", "ravencase.testflaskmail@gmail.com")])
            msg.body = message
            try:
                mail = Mail(app)
                mail.connect()
                mail.send(msg)
                print('Email sent!')
                flash('Your email has been sent to our customer service, and will be responded soonly!')
                return redirect(url_for('contactus'))
            except:
                flash('Failed to send ticket email!')
                return render_template('contactus.html', title="100% QUALITY CUSTOM CASES", contact_status="active", footer_place="fixed-bottom")
        else:
            return render_template('contactus.html', title="100% QUALITY CUSTOM CASES", contact_status="active", footer_place="fixed-bottom")
    # Apabila belum login akan redirect kehalaman login
    else:
        flash('You must logged in!')
        return redirect(url_for('login'))

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
            session['email'] = result['email']
            session['role_id'] = result['role_id']
            # Jika role_id nya 1 (member), maka otomatis akan redirect ke halaman khusus client
            if session.get('role_id') == 1:
                return redirect(url_for('index'))
            # Jika role_id nya 0 (admin), maka otomatis akan redirect ke halaman khusus admin
            if session.get('role_id') == 0:
                return redirect(url_for('admin'))
        # Apabila tidak cocok maka akan tampil pesan flash berikut
        else:
            flash('Incorrect username/password!')
    else:
        # User dan admin akan diredirect ke page indexnya masing-masing apabila,
        # mengakses halaman login pada saat user/admin tsb sudah login
        if "name" in session:
            # Jika role_id nya 1 (member), maka otomatis akan redirect ke halaman khusus client
            if session.get('role_id') == 1:
                return redirect(url_for('index'))
            # Jika role_id nya 0 (admin), maka otomatis akan redirect ke halaman khusus admin
            if session.get('role_id') == 0:
                return redirect(url_for('admin'))
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
    session.pop('email', None)
    session.pop('role_id', None)
    # Kemudian kembali ke landing page
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    # Proses register
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form:
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        id = None
        # Set role_id ke 1, dimana role_id tsb dikhususkan untuk member
        role_id = 1
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
            msg.html = render_template('email/welcome_user.html', name=name)
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

@app.route('/checkout/<string:id>', methods=['GET','POST'])
def checkout(id):
    # Fungsi untuk menampilkan page checkout
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    result = cursor.fetchall()

    # Cek apakah device telah dipilih
    device = request.form.get('device')
    if session['loggedin'] == True:
        if device:
            return render_template('/products/checkout.html', cases_status="active", nav_place="fixed-top",
                                   footer_place="fixed-bottom", products=result, device=device)
        # Jika belum, akan muncul pesan flash
        else:
            flash('Please select a device!')
            return redirect(url_for('showProduct', id=id))
    else:
        flash('You must logged in!')
        return redirect(url_for('login'))

@app.route('/checkout_success/<string:id>', methods=['GET','POST'])
def checkout_success(id):
    # Fungsi untuk menampilkan page sukses checkout
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    result = cursor.fetchall()

    device = request.form.get('device')
    if session['loggedin'] == True:
        if device:
            # Mengambil data dari form untuk ditampilkan
            address = request.form['address']
            receiver_name = request.form['name']
            tel = request.form['tel']
            title = request.form['title']
            device = request.form['device']
            price = request.form['price']
            username = session.get('name')
            email = session.get('email')

            # Tanggal checkout
            checkout_at = datetime.now().strftime("%d %B %Y, %H:%M")

            # Inisialisasi direktori file pdf
            pdffile = app.config['PDF_FOLDER'] + '/invoice.pdf'

            # Untuk pdf
            name = request.form['name']

            # Proses render html dengan jinja template agar bisa dikonversi menjadi file pdf
            venv = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
            template = venv.get_template('templates/invoice.html')
            html_out = template.render(title=title, price=price, device=device, name=name, tel=tel, address=address, date=checkout_at)
            css = 'static/css/invoice.css'

            # Proses konversi menjadi file pdf
            pdfkit.from_string(html_out, pdffile, configuration=config, css=css)

            # Mengirim email detail order
            with app.open_resource(pdffile) as fp:
                # Proses mengirim email detail order
                # Custom file name attachment pdf
                filename = "INVOICE_" + username + "_" + datetime.now().strftime("%m%d%Y%H%M%S")
                msg = Message("Your Order Status 🚀", sender=("Raven Case Team", app.config.get("MAIL_USERNAME")),
                              recipients=[(username, email)])
                msg.html = render_template('email/order_success.html', name=username, title=title, price=price, device=device, receiver_name=receiver_name,
                                           address=address, tel=tel, date=checkout_at)
                msg.attach(filename, "application/pdf", fp.read())
                try:
                    mail = Mail(app)
                    mail.connect()
                    mail.send(msg)
                    print('Email sent!')
                    return render_template('/products/checkout_success.html', cases_status="active", nav_place="fixed-top",
                                           footer_place="fixed-bottom", products=result, device=device, address=address,
                                           name=receiver_name, tel=tel)
                except:
                    return print('Failed to send email!')
        else:
            flash('Please select a device!')
            return redirect(url_for('showProduct', id=id))
    else:
        flash('You must logged in!')
        return redirect(url_for('login'))

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
        if session['loggedin'] == True and session.get('role_id') == 0:
            return render_template('admin/products/add_product.html')
        else:
            print('Masuk dulu sebagai admin!')
            return redirect(url_for('admin'))

@app.route('/manageproduct', methods=['GET','POST'])
def manageproduct():
    # Fungsi untuk menampilkan list produk
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()

    # Memastikan apakah yang membuka halaman adalah admin
    if session['loggedin'] == True and session.get('role_id') == 0:
        return render_template('admin/products/manage_product.html', products=result)
    else:
        print('Masuk dulu sebagai admin!')
        return redirect(url_for('admin'))

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
        if session['loggedin'] == True and session.get('role_id') == 0:
            return render_template('admin/products/edit_product.html', data=result)
        else:
            print('Masuk dulu sebagai admin!')
            return redirect(url_for('admin'))

@app.route('/deleteproduct/<id>', methods=['GET','POST'])
def deleteproduct(id):
    # Fungsi untuk menghapus produk
    # Proses komunikasi dengan database
    if session['loggedin'] == True and session.get('role_id') == 0:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM products WHERE id='%s'" % id)
        mysql.connection.commit()
        cursor.close()
        flash('Successfully deleted!')
        return redirect(url_for('manageproduct'))
    else:
        print('Masuk dulu sebagai admin!')
        return redirect(url_for('admin'))

@app.route('/managedevice', methods=['GET','POST'])
def managedevice():
    # Fungsi untuk menampilkan list device
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM devices")
    result = cursor.fetchall()

    # Memastikan apakah yang membuka halaman adalah admin
    if session['loggedin'] == True and session.get('role_id') == 0:
        return render_template('admin/devices/manage_device.html', devices=result)
    else:
        print('Masuk dulu sebagai admin!')
        return redirect(url_for('admin'))

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
        if session['loggedin'] == True and session.get('role_id') == 0:
            return render_template('admin/devices/add_device.html')
        else:
            print('Masuk dulu sebagai admin!')
            return redirect(url_for('admin'))

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
        if session['loggedin'] == True and session.get('role_id') == 0:
            return render_template('admin/devices/edit_device.html', data=result)
        else:
            print('Masuk dulu sebagai admin!')
            return redirect(url_for('admin'))

@app.route('/deletedevice/<id>', methods=['GET','POST'])
def deletedevice(id):
    # Fungsi untuk menghapus device
    # Proses komunikasi dengan database
    if session['loggedin'] == True and session.get('role_id') == 0:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM devices WHERE id='%s'" % id)
        mysql.connection.commit()
        cursor.close()
        flash('Successfully deleted!')
        return redirect(url_for('managedevice'))
    else:
        print('Masuk dulu sebagai admin!')
        return redirect(url_for('admin'))

@app.route('/managebanner', methods=['GET','POST'])
def managebanner():
    # Fungsi untuk menampilkan list banner
    # Proses komunikasi dengan database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM banners")
    result = cursor.fetchall()

    # Memastikan apakah yang membuka halaman adalah admin
    if session['loggedin'] == True and session.get('role_id') == 0:
        return render_template('admin/banners/manage_banner.html', banners=result)
    else:
        print('Masuk dulu sebagai admin!')
        return redirect(url_for('admin'))

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
        if session['loggedin'] == True and session.get('role_id') == 0:
            return render_template('admin/banners/add_banner.html')
        else:
            print('Masuk dulu sebagai admin!')
            return redirect(url_for('admin'))

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
        if session['loggedin'] == True and session.get('role_id') == 0:
            return render_template('admin/banners/edit_banner.html', data=result)
        else:
            print('Masuk dulu sebagai admin!')
            return redirect(url_for('admin'))

@app.route('/deletebanner/<id>', methods=['GET','POST'])
def deletebanner(id):
    # Fungsi untuk menghapus banner
    # Proses komunikasi dengan database
    if session['loggedin'] == True and session.get('role_id') == 0:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("DELETE FROM banners WHERE id='%s'" % id)
        mysql.connection.commit()
        cursor.close()
        flash('Successfully deleted!')
        return redirect(url_for('managebanner'))
    else:
        print('Masuk dulu sebagai admin!')
        return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    # Menghalangi member agar tidak bisa masuk ke halaman admin
    if session['loggedin'] == True and session.get('role_id') != 0:
        print('Member not allowed to access admin page!')
        return redirect(url_for('index'))
    return render_template('/admin/index.html')

@app.route('/register_admin', methods=['GET','POST'])
def register_admin():
    # Proses register admin
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form:
        # Apabila requestnya POST, maka sistem akan mengambil value dari inputan dan mengirim ke database
        id = None
        # Set role_id ke 0, dimana role_id tsb dikhususkan untuk admin
        role_id = 0
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
            return redirect(url_for('register_admin'))
        # Jika data yang diinput unik, maka data akan dikirim ke database
        else:
            cursor.execute("""INSERT INTO users VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s")""" % data)
            mysql.connection.commit()
            cursor.close()
            flash('Successfully registered! You can login now!')
            return redirect(url_for('login'))
    # Apabila requestnya GET, maka sistem akan menampilkan form register admin
    else:
        return render_template('auth/register_admin.html', footer_place="fixed-bottom", register_status="active")

@app.route('/downloadpdf', methods=['GET','POST'])
def downloadpdf():
    # User akan diredirect ke link download file pdf
    return redirect("http://localhost:5000/static/pdf/invoice.pdf", code=302)

if __name__ == '__main__':
    app.run()
