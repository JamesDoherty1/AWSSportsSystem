from flask import Flask, render_template, request, jsonify, url_for, flash
import sqlite3
from flask_login import current_user, login_required

from werkzeug.utils import redirect

app = Flask(__name__)


# Flask route to handle event registration
def createEvent():
    conn = sqlite3.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM Users WHERE UserID = ?', (current_user.id,))
    if cursor.fetchone()[0] != 'Coordinator':
        return redirect(url_for('events'))
    club_name = request.form['clubName']
    event_date_time = request.form['eventDateTime']
    information = request.form['information']
    print(current_user)

    # Insert event into the database

    cursor.execute('INSERT INTO Events (Title, Description, Date, Time, Venue) VALUES (?, ?, ?, ?, ?)',
                   (club_name, information, event_date_time.split('T')[0], event_date_time.split('T')[1], 'Your Venue'))
    conn.commit()
    conn.close()

    return redirect(url_for('events'))


# Flask route to render the events page
@login_required
def eventsPage():
    print(current_user.id)
    conn = sqlite3.connect('db/user_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Events')
    data = cursor.fetchall()

    for i, item in enumerate(data):
        cursor.execute('SELECT * FROM EventRegistrations WHERE EventID = ? AND UserID = ?', (item[0], current_user.id))
        exists = cursor.fetchone()

        if exists:
            item = list(item)
            item.append(True)
            data[i] = tuple(item)
        else:
            item = list(item)
            item.append(False)
            data[i] = tuple(item)

    return render_template('/events.html', events=data, current_user=current_user)


@login_required
def joinEvent():
    userId = request.form['userId']
    eventId = request.form['eventId']

    conn = sqlite3.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT ClubID FROM Events WHERE EventID = ?', (eventId,))
    clubId = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM EventRegistrations WHERE EventID = ? AND UserID = ?', (eventId, userId))
    exists = cursor.fetchone()

    if exists:
        return redirect(url_for('events'))
    else:
        print(clubId,userId)
        cursor.execute('SELECT * FROM ClubMemberships WHERE (UserID,ClubID)=(?,?)', (userId, clubId))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO EventRegistrations (EventID, UserID) VALUES (?,?)',
                           (eventId, userId))
        else:
            cursor.execute('INSERT INTO EventRegistrations (EventID, UserID, Status) VALUES (?,?,?)',
                           (eventId, userId, "Approved"))

        conn.commit()
        return redirect(url_for('events'))


if __name__ == '__main__':
    app.run(debug=True)
