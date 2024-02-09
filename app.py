from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
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

    return render_template('/admin.html', current_user=current_user, role=role_data[5], users_data=user_data)

@app.route('/explore')
def explore():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Clubs')
    club_data = cursor.fetchall()
    return render_template('/explore.html', club_data=club_data)

@app.route('/explore/<int:id>')
def clubpage(id):
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Clubs WHERE clubid = ?', (id,))
    club_data = cursor.fetchone()

    cursor.execute('SELECT * FROM Users WHERE userid = ?', (club_data[4],))
    owner_data = cursor.fetchone()
    return render_template('clubpage.html', club_data=club_data, owner_data=owner_data)


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


class USERDATA:
    def __init__(self, username, mobile, email, role, accountStatus) -> None:
        self.username = username
        self.mobile = mobile
        self.email = email
        self.role = role
        self.accountStatus = accountStatus


@app.context_processor
def utility_processor():
    def current_user_data():
        if current_user.is_authenticated:
            conn = db.connect('db/user_data.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE UserID = ?', (current_user.id,))
            currentUsrData = cursor.fetchone()
            userData = USERDATA(
                currentUsrData[1],
                currentUsrData[3],
                currentUsrData[4],
                currentUsrData[5],
                currentUsrData[6]
            )
            print(userData.role)
            return userData
        return USERDATA(
                None,
                None,
                None,
                None,
                None
            )
    return dict(user_data=current_user_data())

@app.route('/profile')
@login_required
def profile():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE UserID = ?', (current_user.id,))
    currentUsrData = cursor.fetchone()
    return render_template('/profile.html')

@app.route('/joinClub', methods=["GET", "POST"])
def joinClub():
    # check if user is a member of the club already
    clubid = request.form['club']
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ClubMemberships WHERE UserID = ? AND ClubID = ?', (current_user.id, clubid))
    exists = cursor.fetchone()

    if exists:
        print("User already member!")
    else:
        cursor.execute('INSERT INTO ClubMemberships (UserID,ClubID ) VALUES (?, ?)', (current_user.id,clubid))
        conn.commit()

        print("User added to club.")

    return redirect(url_for('profile'))
@login_required
@app.route("/retrieveData/<int:id>", methods=['GET', 'POST'])
def retrieve_user_data(id):
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE UserID = ?', (current_user.id,))
    user_data = cursor.fetchone()
    if user_data[5] == "Admin":
        cursor.execute('SELECT * FROM Users WHERE UserID = ?', (id,))
        user_data = cursor.fetchone()
        return jsonify(user_data)
    else:
        return 'Unauthorised Access'

@login_required
@app.route("/updateMember", methods=['GET', 'POST'])
def updateMember():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE UserID = ?', (current_user.id,))
    user_data = cursor.fetchone()
    if user_data[5] == "Admin":
        print(request.form['userID'], request.form['role'])
        cursor.execute('UPDATE Users SET Role = ? WHERE UserID = ?', (request.form['role'],int(request.form['userID'])))
        conn.commit()
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
