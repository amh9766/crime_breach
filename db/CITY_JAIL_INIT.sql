CREATE TABLE Criminals(
    Criminal_ID NUMERIC(6,0), 
    Last VARCHAR(15), 
    First VARCHAR(10), 
    Street VARCHAR(30), 
    City VARCHAR(20), 
    State CHAR(2), 
    Zip CHAR(5), 
    Phone CHAR(10), 
    V_status CHAR(1), 
    P_status CHAR(1), 
    PRIMARY KEY (Criminal_ID)
);

CREATE TABLE Alias(
    Alias_ID NUMERIC(6,0), 
    Criminal_ID NUMERIC(6,0) REFERENCES Criminals(Criminal_ID), 
    Alias VARCHAR(20), 
    PRIMARY KEY (Alias_ID)
);

CREATE TABLE Crimes(
    Crime_ID NUMERIC(9,0), 
    Criminal_ID NUMERIC(6,0) REFERENCES Criminals(Criminal_ID), 
    Classification CHAR(1) DEFAULT 'U', 
    Date_charged DATE, 
    Status CHAR(2) NOT NULL, 
    Hearing_date DATE, 
    Appeal_cut_date DATE, 
    PRIMARY KEY (Crime_ID),
    CONSTRAINT check_hearing_charged_date CHECK(Hearing_date > Date_charged)
);

CREATE TABLE Prob_officer(
    Prob_ID NUMERIC(5,0),  
    Last VARCHAR(15), 
    First VARCHAR(10), 
    Street VARCHAR(30), 
    City VARCHAR(20), 
    State CHAR(2), 
    Zip CHAR(5), 
    Phone CHAR(10), 
    Email VARCHAR(30), 
    Status CHAR(1) NOT NULL, 
    PRIMARY KEY (Prob_ID)
);

CREATE TABLE Sentences(
    Sentence_ID NUMERIC(6,0),
    Criminal_ID NUMERIC(6,0) REFERENCES Criminals(Criminal_ID),
    Type CHAR(1),
    Prob_ID NUMERIC(5,0) REFERENCES Prob_officer(Prob_ID), 
    Start_date DATE,
    End_Date DATE,
    Violations NUMERIC(3,0) NOT NULL, 
    PRIMARY KEY (Sentence_ID),
    CONSTRAINT check_end_start_date CHECK(End_date > Start_date)
);

CREATE TABLE Crime_codes(
    Crime_code NUMERIC(3,0) NOT NULL,  
    Code_description VARCHAR(30) NOT NULL UNIQUE, 
    PRIMARY KEY (Crime_code)
);

CREATE TABLE Crime_charges(
    Charge_ID NUMERIC(10,0),
    Crime_ID NUMERIC(9,0) REFERENCES Crimes(Crime_ID),
    Crime_code NUMERIC(3,0) REFERENCES Crime_codes(Crime_code), 
    Charge_status CHAR(2), 
    Fine_amount NUMERIC(7,2), 
    Court_fee NUMERIC(7,2), 
    Amount_paid NUMERIC(7,2), 
    Pay_due_date DATE, 
    PRIMARY KEY (Charge_ID)
);

CREATE TABLE Officers(
    Officer_ID NUMERIC(8,0),  
    Last VARCHAR(15), 
    First VARCHAR(10), 
    Precinct CHAR(4) NOT NULL, 
    Badge VARCHAR(14) UNIQUE, 
    Phone CHAR(10), 
    Status CHAR(1) DEFAULT 'A', 
    PRIMARY KEY (Officer_ID)
);

CREATE TABLE Crime_officers(
    Crime_ID NUMERIC(9,0) REFERENCES Crimes(Crime_ID),  
    Officer_ID NUMERIC(8,0) REFERENCES Officers(Officer_ID), 
    PRIMARY KEY (Crime_ID, Officer_ID)
);

CREATE TABLE Appeals(
    Appeal_ID NUMERIC(5,0),  
    Crime_ID NUMERIC(9,0) REFERENCES Crimes(Crime_ID), 
    Filing_date DATE, 
    Hearing_date DATE, 
    Status CHAR(1) DEFAULT 'P', 
    PRIMARY KEY (Appeal_ID)
);

CREATE TABLE Users(
    Username VARCHAR(10),
    Password VARCHAR(256),
    PRIMARY KEY (Username)
);

CREATE VIEW criminals_publicview AS
SELECT Criminals.Criminal_ID AS "ID", Last AS "Last Name", 
    First AS "First Name", V_status AS "Violent Offender?", 
    P_status AS "On Probation?"
FROM Criminals;

CREATE VIEW alias_publicview AS
SELECT Alias.Criminal_ID AS "ID", Alias
FROM Alias;

CREATE VIEW sentences_publicview AS
SELECT Sentences.Criminal_ID AS "ID", Start_date AS "Start",
    End_date AS "End", Type
FROM Sentences;

CREATE VIEW officer_publicview AS
SELECT Badge AS "Badge #", Last AS "Last Name", First AS "First Name", Precinct,
    Status
FROM Officers;

CREATE VIEW crime_publicview AS
SELECT Criminals.Criminal_ID AS "Criminal ID", Last AS "Last Name", First AS "First Name",
    Classification, Date_charged AS "Date Charged", Status, Hearing_date AS "Hearing Date",
    Crimes.Crime_ID AS "Crime ID"
FROM Crimes
INNER JOIN Criminals
ON Crimes.Criminal_ID = Criminals.Criminal_ID;

CREATE VIEW charges_publicview AS
SELECT Crime_charges.Crime_ID AS "ID", Crime_codes.Crime_code AS "Code",
    Code_description AS "Description", Charge_status AS "Status"
FROM Crime_charges 
INNER JOIN Crime_codes
ON Crime_charges.Crime_code = Crime_codes.Crime_code;

CREATE OR REPLACE USER "administrator"@"%" IDENTIFIED BY "adm!n";
CREATE OR REPLACE USER "everyone"@"%" IDENTIFIED BY "every1";

GRANT SELECT ON criminals_publicview TO everyone@'%';
GRANT SELECT ON alias_publicview TO everyone@'%';
GRANT SELECT ON sentences_publicview TO everyone@'%';
GRANT SELECT ON officer_publicview TO everyone@'%';
GRANT SELECT ON crime_publicview TO everyone@'%';
GRANT SELECT on charges_publicview TO everyone@'%';

GRANT ALL ON Alias TO administrator@'%';
GRANT ALL ON Criminals TO administrator@'%';
GRANT ALL ON Crimes TO administrator@'%';
GRANT ALL ON Sentences TO administrator@'%';
GRANT ALL ON Prob_officer TO administrator@'%';
GRANT ALL ON Crime_charges TO administrator@'%';
GRANT ALL ON Crime_officers TO administrator@'%';
GRANT ALL ON Officers TO administrator@'%';
GRANT ALL ON Appeals TO administrator@'%';
GRANT ALL ON Crime_codes TO administrator@'%';
GRANT SELECT ON Users TO administrator@'%';

FLUSH PRIVILEGES;
