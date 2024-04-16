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

CREATE VIEW criminals_publicview AS
SELECT Last AS "Last Name", First AS "First Name", V_status AS 
    "Violent Offender?", P_status AS "On Probation?", Alias
FROM Criminals
LEFT JOIN Alias
ON Criminals.Criminal_ID = Alias.Criminal_ID;

CREATE VIEW officer_publicview AS
SELECT Badge AS "Badge #", Last AS "Last Name", First AS "First Name", Precinct,
    Status
FROM Officers;

CREATE VIEW crime_publicview AS
SELECT Last AS "Last Name", First AS "First Name", Alias, Classification,
    Date_charged AS "Date Charged", Status, Hearing_date AS "Hearing Date",
    Charge_status AS "Charge Status"
FROM Crimes
LEFT JOIN Crime_charges
ON Crimes.Crime_ID = Crime_charges.Crime_ID
INNER JOIN Criminals
ON Crimes.Criminal_ID = Criminals.Criminal_ID
LEFT JOIN Alias
ON Criminals.Criminal_ID = Alias.Criminal_ID;

CREATE VIEW criminals_privateview AS (SELECT Criminals.Criminal_ID AS "Criminal ID", Criminals.Last AS "Criminal Last", Criminals.First AS "Criminal First", 
Criminals.Street AS "Criminal Street", Criminals.City AS "Criminal City", Criminals.State AS "Criminal State", Criminals.Zip AS "Criminal Zip", Criminals.Phone AS "Criminal Phone", 
V_Status AS "Violent Offender?", P_Status AS "On Probation?", Alias, Alias_ID AS "Alias ID", Sentence_ID AS "Sentence ID", Type, Sentences.Prob_ID AS "Probation ID", 
Start_date AS "Start Date", End_date AS "End Date", Violations, Prob_officer.Last AS "Probation Officer Last", Prob_officer.First AS "Probation Officer First", 
Prob_officer.Street AS "Probation Officer Street", Prob_officer.City AS "Probation Officer City", Prob_officer.State AS "Probation Officer State", 
Prob_officer.Zip AS "Probation Officer Zip", Prob_officer.Phone AS "Probation Officer Phone", Email AS "Probation Officer Email", 
Status AS "Probation Offier Status" FROM Criminals INNER JOIN Alias ON Criminals.Criminal_ID = Alias.Criminal_ID INNER JOIN Sentences ON Criminals.Criminal_ID = Sentences.Criminal_ID 
INNER JOIN Prob_officer ON Sentences.Prob_ID = Prob_officer.Prob_ID);

CREATE VIEW officer_privateview AS
SELECT Officer_ID AS "Officer ID", Last AS "Last Name", First AS "First Name", Badge AS "Badge #", Phone AS "Phone Number", Precinct, Status
FROM Officers;

CREATE VIEW crime_privateview AS SELECT Crimes.Crime_ID AS "Crime ID", Crimes.Criminal_ID AS "Criminal ID", Classification, Date_charged AS "Date Charged", Crimes.Status AS "Crime Status", Crimes.Hearing_date AS "Crime Hearing Date", Appeal_cut_date AS "Appeal Cut Date", Charge_ID AS "Charge ID", Charge_status AS "Charge Status", Fine_amount AS "Fine Amount", Court_fee AS "Court Fee", Amount_paid AS "Amount Paid", Pay_due_date AS "Pay Due Date", Crime_officers.Officer_ID AS "Officer ID", Code_description AS "Code Description", Appeal_ID AS "Appeal ID", Filing_date AS "Filing Date", Appeals.Hearing_date AS "Appeal Hearing Date", Appeals.Status AS "Appeal Status"
FROM Crimes
INNER JOIN Crime_charges ON Crimes.Crime_ID = Crime_charges.Crime_ID
INNER JOIN Crime_officers ON Crimes.Crime_ID = Crime_officers.Crime_ID
INNER JOIN Appeals ON Crimes.Crime_ID = Appeals.Crime_ID
INNER JOIN Crime_codes ON Crime_charges.Crime_code = Crime_codes.Crime_code;

CREATE ROLE administrator;
CREATE ROLE everyone;

GRANT SELECT ON Alias TO everyone;
GRANT SELECT ON Criminals TO everyone;
GRANT SELECT ON Crime_charges TO everyone;
GRANT SELECT ON Officers TO everyone;
GRANT SELECT ON Crimes TO everyone;
