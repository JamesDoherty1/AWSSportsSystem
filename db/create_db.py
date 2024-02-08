import sqlite3 as db


conn = db.connect('user_data.db')

cursor = conn.cursor()

# Create Users table
create_users_table_query = '''
CREATE TABLE IF NOT EXISTS Users (
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL,
    Password TEXT NOT NULL,
    Contact TEXT NOT NULL,
    Email TEXT NOT NULL,
    Role TEXT NOT NULL,
    ApprovalStatus TEXT DEFAULT 'Pending',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

cursor.execute(create_users_table_query)
conn.commit()



# Create ClubMemberships table
create_club_memberships_table_query = '''
CREATE TABLE IF NOT EXISTS ClubMemberships (
    MembershipID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER,
    ClubID INTEGER,
    RequestStatus TEXT DEFAULT 'Pending',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (ClubID) REFERENCES Clubs(ClubID)
);
'''

cursor.execute(create_club_memberships_table_query)
conn.commit()


# Create Clubs table
create_clubs_table_query = '''
CREATE TABLE IF NOT EXISTS Clubs (
    ClubID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Description TEXT,
    ValidityStatus TEXT NOT NULL,
    CoordinatorID INTEGER,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CoordinatorID) REFERENCES Users(UserID)
);
'''

cursor.execute(create_clubs_table_query)
conn.commit()

# Create Events table
create_events_table_query = '''
CREATE TABLE IF NOT EXISTS Events (
    EventID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Description TEXT,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    Venue TEXT NOT NULL,
    ClubID INTEGER,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ClubID) REFERENCES Clubs(ClubID)
);
'''

cursor.execute(create_events_table_query)
conn.commit()

# Create EventRegistrations table
create_event_registrations_table_query = '''
CREATE TABLE IF NOT EXISTS EventRegistrations (
    RegistrationID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID INTEGER,
    EventID INTEGER,
    Status TEXT DEFAULT 'Pending',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (EventID) REFERENCES Events(EventID)
);
'''

cursor.execute(create_event_registrations_table_query)
conn.commit()

# Insert sample user data
insert_user_query = '''
INSERT INTO Users (Username, Password, Contact, Email, Role, ApprovalStatus)
VALUES (?, ?, ?, ?, ?, ?)
'''


# Close the cursor and connection
cursor.close()
conn.close()
