INSERT INTO Criminals(Criminal_ID, Last, First, Street, City, State, Zip, Phone,
    V_status, P_status)
VALUES
(1, "Habersham", "Daleek", "178 Lexington Avenue", "New York", 'NY', '10016',
    '2128398300', 'N', 'Y'),
(2, "Laboy", "Anthony", "197 1st Avenue", "New York", 'NY', '10003',
    '2123587912', 'Y', 'Y'),
(3, "O'Garro", "Ronald", "306 Gold Street", "Brooklyn", 'NY', '11201', 
    '7188558088', 'Y', 'N'),
(4, "Wu", "Henry", "64-16 Fresh Pond Rd", "Queens", 'NY', '11385', 
    '7184170300', 'N', 'Y'),
(5, "Eberman", "Jason", "115 East 14th St", "New York", 'NY', '10003', 
    '2122532227', 'N', 'Y'),
(6, "Haffner", "John", "128 Montague Street", "Brooklyn", 'NY', '11201', 
    '3472940179', 'Y', 'Y'),
(7, "Dent", "Harvey", "61 Delancey Street", "New York", 'NY', '10002', 
    '6464943630', 'Y', 'N'),
(8, "Chill", "Joe", "1617 York Ave", "New York", 'NY', '10028', '2125354480', 
    'Y', 'N'),
(9, "Feeley", "Marvin", "459 Second Avenue", "New York", 'NY', '10010', 
    '2126793665', 'N', 'Y'),
(10, "Picciano", "Ernest", "86 University Pl", "New York", 'NY', '10003', 
    '2122559378', 'Y', 'N');

INSERT INTO Alias(Alias_ID, Criminal_ID, Alias)
VALUES 
(1, 7, "Two-Face"),
(2, 3, "Deadshot"),
(3, 5, "Riddler"),
(4, 8, "Bob Kane"),
(5, 4, "Tombstone"),
(6, 6, "Mr. Freeze"),
(7, 2, "Mad Hatter"),
(8, 10, "Penguin"),
(9, 1, "Firefly"),
(10, 9, "Mr. Negative");

INSERT INTO Crimes(Crime_ID, Criminal_ID, Classification, Date_charged, Status,
    Hearing_date, Appeal_cut_date)
VALUES 
(1, 2, 'F', '2020-07-20', 'CL', '2020-07-27', '2020-09-25'),
(2, 3, 'F', '2005-04-15', 'CL', '2005-04-22', '2005-06-21'),
(3, 1, 'M', '2024-02-23', 'CA', '2024-04-08', '2024-06-07'),
(4, 6, 'F', '2021-06-10', 'CL', '2021-06-17', '2021-08-16'),
(5, 3, 'F', '2008-08-23', 'CL', '2008-08-25', '2008-10-24'),
(6, 10, 'F', '2010-10-23', 'CL', '2010-10-30', '2010-12-29'),
(7, 4, 'F', '2023-03-14', 'IA', '2023-03-21', '2023-05-20'),
(8, 7, 'F', '2024-02-01', 'CA', '2024-02-08', '2024-04-08'),
(9, 8, 'F', '2020-05-17', 'CL', '2020-05-24', '2020-07-23'),
(10, 5, 'F', '2024-04-01', 'CA', '2024-04-04', '2024-06-03'),
(11, 9, 'F', '2024-01-30', 'CL', '2024-02-06', '2024-04-06'),
(12, 5, 'O', '2024-02-05', 'IA', '2024-02-12', '2024-04-12'),
(13, 3, 'F', '2016-02-02', 'CL', '2016-02-05', '2016-04-05'),
(14, 9, 'U', '2024-02-25', 'IA', '2024-03-04', '2024-05-02'),
(15, 10, 'O', '2024-02-05', 'IA', '2024-02-12', '2024-04-12'),
(16, 1, 'U', '2023-08-06', 'CL', '2023-08-13', '2023-10-12');

INSERT INTO Prob_officer(Prob_ID, Last, First, Street, City, State, Zip, Phone,
    Email, Status)
VALUES 
(1, "Gordon", "James", "409 Fulton St", "Brooklyn", 'NY', '11201', 
    '7183077590', 'james.g@gmail.com', 'I'),
(2, "Macaluso", "Vincent", "724 Broadway", "New York", 'NY', '10003',
    '2125299660', 'vincent.m@yahoo.com', 'A'),
(3, "Tompkins", "Joseph", "20 Astor Pl", "New York", 'NY', '10003', 
    '2126599981', 'joseph.t@hotmail.com', 'A'),
(4, "Howard", "Philip", "150 E 14th St", "New York", 'NY', '10003',
    '6464426471', 'philip.h@aol.com', 'I'),
(5, "Laboy", "Elizabeth", "2561 Hylan Blvd", "Staten Island", 'NY', '10306',
    '7186689200', 'elizabeth.l@gmail.com', 'A'),
(6, "Peña", "Javier", "490 8th Ave", "New York", 'NY', '10001', '2129470771',
    'javier.p@gmail.com', 'A'),
(7, "Nivar", "Ana", "234 W 42nd St", "New York", 'NY', '10036', '2123917414',
    'ana.n@hotmail.com', 'A'),
(8, "Ricci", "Brian", "39 Union Square W", "New York", 'NY', '10003',
    '4422228660', 'brian.r@aol.com', 'A'),
(9, "Fletcher", "William", "56 W 14th St", "New York", 'NY', '10011', 
    '2126752229', 'william.f@yahoo.com', 'A'),
(10, "Reyes", "Nathalie", "32 St Marks Pl", "New York", 'NY', '10003',
    '8456432183', 'nathalie.r@gmail.com', 'I');

INSERT INTO Sentences(Sentence_ID, Criminal_ID, Type, Prob_ID, Start_date, 
    End_date, Violations)
VALUES
(1, 2, 'H', 3, '2020-08-03', '2020-08-24', 0),
(2, 3, 'J', 6, '2008-09-01', '2010-09-01', 2),
(3, 7, 'P', 7, '2024-02-15', '2024-05-16', 1),
(4, 10, 'H', 10, '2010-11-06', '2011-05-07', 3),
(5, 8, 'J', 4, '2020-05-31', '2024-05-30', 4),
(6, 9, 'J', 5, '2024-02-13', '2025-08-13', 6),
(7, 4, 'H', 2, '2023-03-28', '2023-07-27', 1),
(8, 3, 'J', 8, '2016-02-05', '2021-02-03', 3),
(9, 6, 'P', 1, '2021-06-24', '2022-06-24', 1),
(10, 5, 'H', 9, '2024-04-11', '2026-04-11', 2),
(11, 9, 'H', 1, '2024-03-10', '2024-12-08', 5),
(12, 5, 'J', 4, '2024-02-12', '2024-10-12', 3),
(13, 10, 'H', 10, '2024-02-18', '2026-09-24', 2);

INSERT INTO Crime_codes(Crime_code, Code_description)
VALUES
(150, "Arson"), 
(120, "Assault"), 
(200, "Bribery"),
(140, "Burglary"),
(190, "Criminal Impersonation"),
(170, "Forgery"),
(125, "Murder"),
(156, "Computer Tampering"),
(225, "Fraud"),
(105, "Conspiracy");

INSERT INTO Crime_charges(Charge_ID, Crime_ID, Crime_code, Charge_status, 
    Fine_amount, Court_fee, Amount_paid, Pay_due_date)
VALUES
(1, 4, 140, 'GL', 4000.00, 492.29, 4492.29, '2020-08-06'),
(2, 3, 200, 'PD', 2400.00, 303.18, 1303.18, '2024-06-14'),
(3, 2, 105, 'NG', 6500.00, 312.19, 312.19, '2005-06-23'),
(4, 1, 140, 'GL', 3200.00, 458.10, 3658.10, '2020-10-05'),
(5, 5, 125, 'GL', 15670.00, 416.61, 16086.61, '2008-11-23'),
(6, 7, 225, 'GL', 7500.00, 412.82, 7912.82, '2023-06-19'),
(7, 6, 190, 'GL', 2340.00, 493.55, 2833.55, '2011-01-14'),
(8, 8, 156, 'GL', 3789.00, 405.62, 4194.62, '2024-05-31'),
(9, 10, 150, 'PD', 10000.00, 419.17, 2419.17, '2024-06-07'),
(10, 11, 120, 'GL', 1500.00, 399.04, 1899.04, '2024-05-21'),
(11, 9, 125, 'GL', 20560.00, 404.46, 20964.46, '2020-09-07'),
(12, 12, 225, 'GL', 5000.00, 490.39, 5490.39, '2024-04-21'),
(13, 14, 190, 'GL', 2342.00, 477.74, 2819.74, '2024-05-16'),
(14, 15, 170, 'GL', 2000.00, 471.98, 2471.98, '2024-05-08'),
(15, 13, 125, 'GL', 17850.00, 483.88, 18333.88, '2016-04-20'),
(16, 16, 225, 'NG', 6000.00, 487.25, 487.25, '2023-11-19');

INSERT INTO Officers(Officer_ID, Last, First, Precinct, Badge, Phone, Status)
VALUES
(1, "Lafargue", "Roberto", 'MIDS', "CJ19353", "2127761830", 'A'),
(2, "Medina", "Nelson", '17TH', "CJ22851", "2122602604", 'A'),
(3, "Martinez", "Miguel", 'MIDN', "CJ7838", "6469645984", 'I'),
(4, "Quarshie", "Isaac", '01ST', "CJ21243", "2124810034", 'A'),
(5, "Lamaida", "Vincent", '17TH', "CJ11721", "2124398301", 'I'),
(6, "Lanier", "Kayla", 'MIDN', "CJ20948", "6468337073", 'A'),
(7, "Gomez", "Fausto", 'CENP', "CJ13157", "2126792273", 'A'),
(8, "Nelson", "Chulsy", '01ST', "CJ19279", "6467984285", 'I'),
(9, "Batista", "Hannoy", '10TH', "CJ2089", "7186236000", 'A'),
(10, "Jaquez", "Raymundo", '23RD', "CJ1083", "7185522652", 'A');

INSERT INTO Crime_officers(Crime_ID, Officer_ID)
VALUES 
(1, 1),
(2, 6),
(3, 1),
(4, 7),
(5, 8),
(6, 8),
(7, 10),
(8, 6),
(9, 7),
(10, 8),
(11, 8),
(12, 1),
(13, 5),
(14, 4),
(15, 5),
(16, 8),
(5, 7),
(10, 3),
(13, 4);

INSERT INTO Appeals(Appeal_ID, Crime_ID, Filing_date, Hearing_date, Status)
VALUES
(1, 7, '2023-04-30', '2023-05-12', 'D'),
(2, 12, '2024-04-04', '2024-04-09', 'P'),
(3, 6, '2010-11-23', '2010-11-27', 'A'),
(4, 11, '2024-03-03', '2024-03-16', 'A'),
(5, 14, '2024-04-03', '2024-04-11', 'P'),
(6, 9, '2020-06-02', '2020-06-09', 'D'),
(7, 13, '2016-04-02', '2016-04-10', 'D'),
(8, 15, '2024-03-31', '2024-04-08', 'P'),
(9, 1, '2020-08-08', '2020-08-12', 'D'),
(10, 5, '2008-09-27', '2008-10-17', 'D');

