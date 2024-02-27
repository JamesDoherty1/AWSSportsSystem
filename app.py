
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3 as db
# flask --app app.py --debug run
import hashlib
import auth
import clubs
import events
import static
import updates, permissionpages

app = Flask(__name__)
app.config['SECRET_KEY'] = '1d8f6b8beff5'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import other files

# Permission based pages
app.add_url_rule('/myclub', view_func=permissionpages.myclub)
app.add_url_rule('/admin', view_func=permissionpages.admin)


# Update queries
app.add_url_rule('/updateClubMember', methods=['GET', 'POST'], view_func=updates.updateClubMember)
app.add_url_rule('/updateClubMemberEvent', methods=['GET', 'POST'], view_func=updates.updateClubMemberEvent)
app.add_url_rule('/updateMember', methods=['GET', 'POST'], view_func=updates.updateMember)
app.add_url_rule('/updateUserDetails', methods=['GET', 'POST'], view_func=updates.updateUserDetails)

# Club based pages
app.add_url_rule('/joinClub', methods=['GET', 'POST'], view_func=clubs.joinClub)
app.add_url_rule('/createClub', methods=['GET', 'POST'], view_func=clubs.createClub)
app.add_url_rule('/explore/<int:id>', view_func=clubs.clubpage)
app.add_url_rule('/explore', view_func=clubs.explore)
app.add_url_rule("/events", view_func=events.eventsPage)
app.add_url_rule("/createEvent", methods=['GET', 'POST'], view_func=events.createEvent)
app.add_url_rule("/joinEvent", methods=['GET', 'POST'], view_func=events.joinEvent)

# Static pages
app.add_url_rule('/', view_func=static.home)
app.add_url_rule('/home', view_func=static.home)
app.add_url_rule('/contact', view_func=static.contact)
app.add_url_rule('/about', view_func=static.about)
app.add_url_rule('/login', view_func=static.login)
app.add_url_rule('/register', view_func=static.register)
app.add_url_rule('/events', view_func=static.events)

# Authentication
app.add_url_rule("/profile", view_func=auth.profile)
app.add_url_rule("/logout", view_func=auth.logout)
app.add_url_rule("/retrieveData/<int:id>", methods=['GET', 'POST'], view_func=auth.retrieve_user_data)
app.add_url_rule("/registerProcess", methods=['POST'], view_func=auth.registerDataProcess)
app.add_url_rule("/loginProcess", methods=['GET', 'POST'], view_func=auth.loginDataProcess)

@login_manager.user_loader
def load_user(user_id):
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE UserID = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        return auth.User(user_data[0], user_data[1])

@app.context_processor
def utility_processor():
    def current_user_data():
        if current_user.is_authenticated:
            conn = db.connect('db/user_data.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE UserID = ?', (current_user.id,))
            currentUsrData = cursor.fetchone()
            cursor.close()
            conn.close()
            clubname = None
            if currentUsrData[5] == "Coordinator":
                conn = db.connect('db/user_data.db')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM Clubs WHERE CoordinatorID=?',(current_user.id,))
                clubname = cursor.fetchone()[1]
            print(clubname)
            userData = auth.USERDATA(
                currentUsrData[1],
                currentUsrData[3],
                currentUsrData[4],
                currentUsrData[5],
                currentUsrData[6],
                clubname
            )
            return userData
        return auth.USERDATA(
            None,
            None,
            None,
            None,
            None,
            None
        )

    return dict(user_data=current_user_data())

if __name__ == '__main__':
    app.run(debug=True)
