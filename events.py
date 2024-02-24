from flask import Flask, render_template, request, jsonify, url_for
import sqlite3
from flask_login import current_user, login_required

from werkzeug.utils import redirect

app = Flask(__name__)


# Flask route to handle event registration
def createEvent():
    club_name = request.form['clubName']
    event_date_time = request.form['eventDateTime']
    information = request.form['information']
    print(club_name, event_date_time, information)

    # Insert event into the database
    conn = sqlite3.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Events (Title, Description, Date, Time, Venue) VALUES (?, ?, ?, ?, ?)',
                   (club_name, information, event_date_time.split('T')[0], event_date_time.split('T')[1], 'Your Venue'))
    conn.commit()
    conn.close()

    return redirect(url_for('events'))


# Flask route to render the events page
@login_required
def eventsPage():
    conn = sqlite3.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Events')
    data = cursor.fetchall()
    return render_template('/events.html', events=data)


if __name__ == '__main__':
    app.run(debug=True)
