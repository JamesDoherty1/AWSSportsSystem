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

# cursor.execute(create_users_table_query)
# conn.commit()


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

# cursor.execute(create_club_memberships_table_query)
# conn.commit()


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

# cursor.execute(create_clubs_table_query)
# conn.commit()

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

# cursor.execute(create_events_table_query)
# conn.commit()

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

# cursor.execute(create_event_registrations_table_query)
# conn.commit()

# Insert sample user data
insert_club_query = '''
INSERT INTO Clubs (Name, Description, ValidityStatus, CoordinatorID)
VALUES (?, ?, ?, ?)
'''
# cursor.execute(insert_club_query, ("Outdoor Pursuits", "Explore the outdoors", "Valid", 5))
# conn.commit()


insert_event_query = '''
INSERT INTO Events (Title, Description, Date, Time, Venue, ClubID)
VALUES (?, ?, ?, ?, ?, ?)
'''
# cursor.execute(insert_event_query, ("Outdoor Pursuits climbing", "Wednesday bouldering and top rope climbing", "21/02/2024", "19:00","UL climbing wall", 3))
# conn.commit()

insert_event_registrations_query = '''
INSERT INTO EventRegistrations ( UserID, EventID)
VALUES (?, ?)
'''

# Define CREATE VIEW queries for each view
create_view_queries = [
    '''
    CREATE VIEW IF NOT EXISTS UserClubMemberships AS
    SELECT Users.UserID, Users.Username, Users.Contact, Users.Email, Users.Role,
           ClubMemberships.MembershipID, ClubMemberships.ClubID, ClubMemberships.RequestStatus
    FROM Users
    LEFT JOIN ClubMemberships ON Users.UserID = ClubMemberships.UserID;
    ''',

    '''
    CREATE VIEW IF NOT EXISTS ClubDetails AS
    SELECT Clubs.ClubID, Clubs.Name, Clubs.Description, Clubs.ValidityStatus,
           Users.Username AS CoordinatorName
    FROM Clubs
    LEFT JOIN Users ON Clubs.CoordinatorID = Users.UserID;
    ''',

    '''
    CREATE VIEW IF NOT EXISTS EventDetails AS
    SELECT Events.EventID, Events.Title, Events.Description, Events.Date, Events.Time,
           Events.Venue, Events.ClubID,
           Clubs.Name AS ClubName, Clubs.Description AS ClubDescription
    FROM Events
    LEFT JOIN Clubs ON Events.ClubID = Clubs.ClubID;
    ''',

    '''
    CREATE VIEW IF NOT EXISTS EventRegistrationsDetails AS
    SELECT EventRegistrations.RegistrationID, EventRegistrations.UserID, EventRegistrations.EventID,
           Users.Username AS UserName, Users.Contact AS UserContact, Users.Email AS UserEmail,
           Events.Title AS EventTitle, Events.Date AS EventDate, Events.Time AS EventTime, Events.Venue AS EventVenue
    FROM EventRegistrations
    LEFT JOIN Users ON EventRegistrations.UserID = Users.UserID
    LEFT JOIN Events ON EventRegistrations.EventID = Events.EventID;
    ''',

    '''
    CREATE VIEW IF NOT EXISTS UserUpcomingEvents AS
    SELECT Users.UserID, Users.Username, Users.Email,
           Events.EventID, Events.Title AS EventTitle, Events.Date AS EventDate, Events.Time AS EventTime, Events.Venue AS EventVenue
    FROM Users
    JOIN EventRegistrations ON Users.UserID = EventRegistrations.UserID
    JOIN Events ON EventRegistrations.EventID = Events.EventID
    WHERE Events.Date >= DATE('now')
    ORDER BY Events.Date;
    '''
]

# Execute each CREATE VIEW query
for create_query in create_view_queries:
    cursor.execute(create_query)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Views have been created and saved to the database.")
