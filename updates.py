import sqlite3 as db
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import jinja2
import ast
from flask_login import current_user


def updateClubMember():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT Role FROM Users WHERE UserID = ?', (current_user.id,))
    user_data = cursor.fetchone()
    cursor.execute('SELECT CoordinatorID FROM Clubs WHERE ClubID = ?', (int(request.form['clubID']),))
    club_owner_id = cursor.fetchone()
    if user_data[0] == "Coordinator" and current_user.id == club_owner_id[0]:
        if request.form['approval'] is not None and request.form['approval'] == 'on':
            approved = 'Approved'
            cursor.execute('UPDATE ClubMemberships SET RequestStatus = ? WHERE UserID = ? AND ClubID = ?',
                           (approved, int(request.form['userID']), int(request.form['clubID'])))
        elif request.form['approval'] != 'on':
            cursor.execute('REMOVE FROM ClubMemberships WHERE UserID=?', (int(request.form['userID']),))
        conn.commit()
        return redirect(url_for('myclub'))
    else:
        return redirect(url_for('home'))

def deleteUserFromClub():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ClubMemberships WHERE UserID=?', (int(request.form['userID']),))
    conn.commit()
    return redirect(url_for('myclub'))

def deleteUserFromClubEvents():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM EventRegistrations WHERE (UserID, EventID)=(?,?)', (int(request.form['userID']), int(ast.literal_eval(request.form['eventID'])[0])))
    conn.commit()
    return redirect(url_for('myclub'))
def updateClubMemberEvent():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT Role FROM Users WHERE UserID = ?', (current_user.id,))
    user_data = cursor.fetchone()
    cursor.execute('SELECT CoordinatorID FROM Clubs WHERE ClubID = ?', (int(request.form['clubID']),))
    club_owner_id = cursor.fetchone()

    if user_data[0] == "Coordinator" and current_user.id == club_owner_id[0]:
        if request.form['approval'] is not None and request.form['approval'] == 'on':
            approved = 'Approved'
            cursor.execute('UPDATE EventRegistrations SET Status = ? WHERE UserID = ? AND EventID = ?',
                           (approved, int(request.form['userID']), int(request.form['eventID'][1])))
            conn.commit()

        return redirect(url_for('myclub'))
    else:
        return redirect(url_for('home'))


def updateMember():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT Role FROM Users WHERE UserID = ?', (current_user.id,))
    user_data = cursor.fetchone()
    if user_data[0] == "Admin":

        approved = ''
        if request.form['approval'] is not None and request.form['approval'] == 'on':
            approved = 'Approved'
            cursor.execute('UPDATE Users SET Role = ?, ApprovalStatus = ? WHERE UserID = ?',
                           (request.form['role'], approved, int(request.form['userID'])))
            conn.commit()
        else:
            cursor.execute('UPDATE Users SET Role = ? WHERE UserID = ?',
                           (request.form['role'], int(request.form['userID'])))
            conn.commit()

        return redirect(url_for('admin'))
    else:
        return redirect(url_for('home'))


def updateUserDetails():
    conn = db.connect('db/user_data.db')
    cursor = conn.cursor()

    with conn:
        cursor.execute('UPDATE Users SET Username=?, Contact=?, Email=? WHERE UserID=?',
                       (request.form['Username'], request.form['mobileNumber'], request.form['Email'], current_user.id))
    return redirect(url_for('profile'))

