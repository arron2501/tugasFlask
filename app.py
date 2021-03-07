import MySQLdb, os, hashlib
from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

app = Flask(__name__)
app.config['MOCKUPS_UPLOAD_FOLDER'] = './static/images/uploads/mockups'
app.config['BANNERS_UPLOAD_FOLDER'] = './static/images/uploads/banners'
app.config['SECRET_KEY'] = 'ravencase_##$@%%'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tugasflask'

mysql = MySQL(app)

@app.route('/')
def index():
    # Menampilkan file html add_product.html, dan mengirim data title
    return render_template('index.html', title="100% QUALITY CUSTOM CASES", home_status="active", nav_place="fixed-top")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        result = cursor.fetchone()
        if result:
            session['loggedin'] = True
            session['id'] = result['id']
            session['name'] = result['name']
            return redirect(url_for('index'))
        else:
            flash('Incorrect username/password!')
    return render_template('auth/login.html', footer_place="fixed-bottom", login_status="active")

@app.route('/logout')
def logout():
    session['loggedin'] = False
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form:
        id = None
        role_id = None
        name = request.form['name']
        email = request.form['email']
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (id, role_id, name, email, password, created_at, updated_at)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        users = cursor.fetchone()
        if users:
            flash('Email already registered!')
            return redirect(url_for('register'))
        else:
            cursor.execute("""INSERT INTO users VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s")""" % data)
            mysql.connection.commit()
            cursor.close()
            flash('Successfully registered! You can login now!')
            return redirect(url_for('login'))
    else:
        return render_template('auth/register.html', footer_place="fixed-bottom", register_status="active")

@app.route('/products', methods=['GET','POST'])
def products():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()

    cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor2.execute("SELECT * FROM banners")
    result2 = cursor2.fetchall()
    return render_template('products/index.html', title="100% QUALITY CUSTOM CASES", cases_status="active", nav_place="fixed-top",
                           products=result, banners=result2, filename='/static/images/')

@app.template_filter()
def currencyFormat(value):
    import locale
    locale.setlocale(locale.LC_NUMERIC, 'IND')
    rupiah = locale.format("%.*f", (0, value), True)
    return "Rp{}".format(rupiah)

@app.route('/products/<string:id>', methods=['GET','POST'])
def showProduct(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    result = cursor.fetchall()

    cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor2.execute("SELECT * FROM devices")
    result2 = cursor2.fetchall()
    return render_template('products/show.html', cases_status="active", nav_place="fixed-top", footer_place="fixed-bottom", products=result, devices=result2)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    if request.method == 'POST':
        id = None
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        if 'mockup' not in request.files:
            flash('Please upload mockups!')
            return redirect(url_for('addproduct'))
        mockup = request.files['mockup']
        if mockup.filename == '':
            flash('No selected file')
            return redirect(url_for('addproduct'))
        if mockup and allowed_file(mockup.filename):
            filename = secure_filename(mockup.filename)
            mockup.save(os.path.join(app.config['MOCKUPS_UPLOAD_FOLDER'], filename))
        mockup = "uploads/mockups/"+(mockup.filename).replace(" ", "_")
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (id, title, description, price, mockup, created_at, updated_at)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''INSERT INTO products VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s")''' % data)
        mysql.connection.commit()
        cursor.close()
        flash('Success add product!')
        return redirect(url_for('addproduct'))
    else:
        return render_template('admin/products/add_product.html')

@app.route('/manageproduct', methods=['GET','POST'])
def manageproduct():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()
    return render_template('admin/products/manage_product.html', products=result)

@app.route('/editproduct/<id>', methods=['GET','POST'])
def editproduct(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id='%s'" % id)
    result = cursor.fetchone()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        mockup = request.files['mockup']
        if mockup and allowed_file(mockup.filename):
            filename = secure_filename(mockup.filename)
            mockup.save(os.path.join(app.config['MOCKUPS_UPLOAD_FOLDER'], filename))
        mockup = "uploads/mockups/"+(mockup.filename).replace(" ", "_")
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            UPDATE products SET title="%s", description="%s", price="%s", mockup="%s", updated_at="%s"
            WHERE id="%s"
        ''' % (title, description, price, mockup, updated_at, id))
        mysql.connection.commit()
        cursor.close()
        flash('Success update product!')
        return redirect(url_for('manageproduct'))
    else:
        cursor.close()
        return render_template('admin/products/edit_product.html', data=result)

@app.route('/deleteproduct/<id>', methods=['GET','POST'])
def deleteproduct(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM products WHERE id='%s'" % id)
    mysql.connection.commit()
    cursor.close()
    flash('Successfully deleted!')
    return redirect(url_for('manageproduct'))

@app.route('/managedevice', methods=['GET','POST'])
def managedevice():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM devices")
    result = cursor.fetchall()
    return render_template('admin/devices/manage_device.html', devices=result)

@app.route('/adddevice', methods=['GET','POST'])
def adddevice():
    if request.method == 'POST':
        id = None
        name = request.form['name']
        if name == '':
            flash('Please input device name!')
            return redirect(url_for('adddevice'))
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (id, name, created_at, updated_at)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''INSERT INTO devices VALUES("%s", "%s", "%s", "%s")''' % data)
        mysql.connection.commit()
        cursor.close()
        flash('Success add device!')
        return redirect(url_for('managedevice'))
    else:
        return render_template('admin/devices/add_device.html')

@app.route('/editdevice/<id>', methods=['GET','POST'])
def editdevice(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM devices WHERE id='%s'" % id)
    result = cursor.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        if name == '':
            flash('Please input device name!')
            return redirect(url_for('editdevice', id=id))
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
                    UPDATE devices SET name="%s", updated_at="%s"
                    WHERE id="%s"
                ''' % (name, updated_at, id))
        mysql.connection.commit()
        cursor.close()
        flash('Success update device!')
        return redirect(url_for('managedevice'))
    else:
        cursor.close()
        return render_template('admin/devices/edit_device.html', data=result)

@app.route('/deletedevice/<id>', methods=['GET','POST'])
def deletedevice(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM devices WHERE id='%s'" % id)
    mysql.connection.commit()
    cursor.close()
    flash('Successfully deleted!')
    return redirect(url_for('managedevice'))

@app.route('/managebanner', methods=['GET','POST'])
def managebanner():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM banners")
    result = cursor.fetchall()
    return render_template('admin/banners/manage_banner.html', banners=result)

@app.route('/addbanner', methods=['GET','POST'])
def addbanner():
    if request.method == 'POST':
        id = None
        if 'banner' not in request.files:
            flash('Please upload banner!')
            return redirect(url_for('addbanner'))
        banner = request.files['banner']
        if banner.filename == '':
            flash('No selected file')
            return redirect(url_for('addbanner'))
        if banner and allowed_file(banner.filename):
            filename = secure_filename(banner.filename)
            banner.save(os.path.join(app.config['BANNERS_UPLOAD_FOLDER'], filename))
        banner = "uploads/banners/"+(banner.filename).replace(" ", "_")
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = (id, banner, created_at, updated_at)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''INSERT INTO banners VALUES("%s", "%s", "%s", "%s")''' % data)
        mysql.connection.commit()
        cursor.close()
        flash('Success add banner!')
        return redirect(url_for('managebanner'))
    else:
        return render_template('admin/banners/add_banner.html')

@app.route('/editbanner/<id>', methods=['GET','POST'])
def editbanner(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM banners WHERE id='%s'" % id)
    result = cursor.fetchone()
    if request.method == 'POST':
        if 'banner' not in request.files:
            flash('Please upload banner!')
            return redirect(url_for('editbanner', id=id))
        banner = request.files['banner']
        if banner.filename == '':
            flash('No selected file')
            return redirect(url_for('editbanner', id=id))
        if banner and allowed_file(banner.filename):
            filename = secure_filename(banner.filename)
            banner.save(os.path.join(app.config['BANNERS_UPLOAD_FOLDER'], filename))
        banner = "uploads/banners/"+(banner.filename).replace(" ", "_")
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
                    UPDATE banners SET banner="%s", updated_at="%s"
                    WHERE id="%s"
                ''' % (banner, updated_at, id))
        mysql.connection.commit()
        cursor.close()
        flash('Success update banner!')
        return redirect(url_for('managebanner'))
    else:
        cursor.close()
        return render_template('admin/banners/edit_banner.html', data=result)

@app.route('/deletebanner/<id>', methods=['GET','POST'])
def deletebanner(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM banners WHERE id='%s'" % id)
    mysql.connection.commit()
    cursor.close()
    flash('Successfully deleted!')
    return redirect(url_for('managebanner'))

@app.route('/admin')
def admin():
    return render_template('/admin/index.html')

if __name__ == '__main__':
    app.run()
