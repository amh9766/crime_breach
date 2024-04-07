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


