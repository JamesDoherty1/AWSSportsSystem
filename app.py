from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3 as db
# flask --app app.py --debug run
import hashlib
import jinja2


def calculate_sha256(input_data):
    sha256_hash = hashlib.sha256(input_data.encode()).hexdigest()
    return sha256_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = '1d8f6b8beff5'


@app.route("/contact-us")
def contact():
    return render_template('/contact.html')


@app.route("/about-us")
def about():
    return render_template('/about.html')


@app.route("/")
@app.route("/home")
def home():
    return render_template('/home.html')


@app.route("/login")
def login():
    return render_template('/login.html')


@app.route('/register')
def register():
    return render_template('/register.html')

@app.route("/admin")
def admin():
    # fetch role of current user
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE UserID = ?', (current_user.id,))
    role_data = cursor.fetchone()

    # fetch users data
    cursor.execute('SELECT userid, username, email, contact, role, approvalstatus FROM Users WHERE Role != \'Admin\'')
    user_data = cursor.fetchall()

    print(user_data)

    return render_template('/admin.html', current_user=current_user, role=role_data[5], user_data=user_data)

@app.route('/explore')
def explore():
    return render_template('/explore.html')


login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE UserID = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        return User(user_data[0], user_data[1])


@app.route("/loginProcess", methods=['GET', 'POST'])
def loginDataProcess():
    username = request.form.get('loginName')
    password = request.form.get('loginPassword')
    hashedPass = calculate_sha256(password)
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE Username = ? AND Password = ?', (username, hashedPass))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        user = User(user_data[0], user_data[1])
        login_user(user)
        return redirect(url_for('profile'))
    else:
        flash('Incorrect username or password. Please try again.', 'error')
    return redirect(url_for('login'))


@app.route('/registerProcess', methods=['POST'])
def registerDataProcess():
    username = request.form.get('Username')
    password = request.form.get('Password')
    hashedPass = calculate_sha256(password)
    email = request.form.get('Email')
    contact = request.form.get('mobileNumber')
    print(username,password,hashedPass,email,contact)

    password_repeat = request.form.get('RepeatPassword')

    if not username or not password or not password_repeat or password != password_repeat:
        flash('Invalid registration data. Please check your inputs.', 'error')
        return redirect(url_for('register'))

    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Users WHERE Username = ?', (username,))
    user_data = cursor.fetchone()

    if user_data:
        flash('Username already exists. Please choose a different username.', 'error')
        conn.close()
        return redirect(url_for('register'))
    else:
        # Insert the new user into the loginInfo table
        cursor.execute('INSERT INTO Users (Username, Password, Contact, Email, Role) VALUES (?, ?, ?, ?, ?)', (username, hashedPass,contact,email,"Student"))
        conn.commit()

        cursor.execute('SELECT UserID FROM Users WHERE Username = ?', (username,))
        user_id = cursor.fetchone()[0]
        print(type(user_id))
        if user_id == 1:
            cursor.execute('UPDATE Users SET Role = "Admin" WHERE UserID = 1')
            conn.commit()
        conn.close()
        user = User(user_id, username)
        login_user(user)

        return redirect(url_for('profile'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


class USERDATA():
    def __init__(self, first_name, last_name, phone_number, address) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.address = address


@app.route('/profile')
@login_required
def profile():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE UserID = ?', (current_user.id,))
    currentUsrData = cursor.fetchone()
    userData = USERDATA(
        currentUsrData[0],
        currentUsrData[1],
        currentUsrData[2],
        currentUsrData[3],
    )
    return render_template('/profile.html', data=userData)


if __name__ == '__main__':
    app.run(debug=True)
