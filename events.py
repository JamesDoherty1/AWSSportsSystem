from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Flask route to handle event registration
@app.route('/events', methods=['POST'])
def register_event():
    club_name = request.form['clubName']
    event_date_time = request.form['eventDateTime']
    information = request.form['information']

    # Insert event into the database
    conn = sqlite3.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Events (Title, Description, Date, Time, Venue) VALUES (?, ?, ?, ?, ?)',
                   (club_name, information, event_date_time.split('T')[0], event_date_time.split('T')[1], 'Your Venue'))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

# Flask route to render the events page
@app.route('/events')
def events():
    conn = sqlite3.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Events')
    events = cursor.fetchall()
    conn.close()

    return render_template('events.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)