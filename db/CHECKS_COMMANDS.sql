ALTER TABLE Criminals
ADD CONSTRAINT check_v_status_domain 
CHECK(V_status LIKE 'Y' OR V_status LIKE 'N');

ALTER TABLE Criminals
ADD CONSTRAINT check_p_status_domain 
CHECK(P_status LIKE 'Y' OR P_status LIKE 'N');

ALTER TABLE Crimes
ADD CONSTRAINT check_classification_domain
CHECK(Classification LIKE 'F' OR
    Classification LIKE 'M' OR
    Classification LIKE 'O' OR
    Classification LIKE 'U');

ALTER TABLE Crimes
ADD CONSTRAINT check_status_domain
CHECK(Status LIKE 'CL' OR
    Status LIKE 'CA' OR
    Status LIKE 'IA');

ALTER TABLE Sentences
ADD CONSTRAINT check_type_domain
CHECK(Type LIKE 'J' OR
    Type LIKE 'H' OR
    Type LIKE 'P');

ALTER TABLE Prob_officer
ADD CONSTRAINT check_status_domain
CHECK(Status LIKE 'A' OR Status LIKE 'I');

ALTER TABLE Crime_charges
ADD CONSTRAINT check_charge_status_domain
CHECK(Charge_status LIKE 'PD' OR
    Charge_status LIKE 'GL' OR
    Charge_status LIKE 'NG');

ALTER TABLE Officers
ADD CONSTRAINT check_status_domain
CHECK(Status LIKE 'A' OR Status LIKE 'I');

ALTER TABLE Appeals
ADD CONSTRAINT check_status_domain
CHECK(Status LIKE 'P' OR
    Status LIKE 'A' OR
    Status LIKE 'D');

DELIMITER $$
CREATE OR REPLACE TRIGGER cascade_crime_deletion
AFTER DELETE ON Crimes
FOR EACH ROW
BEGIN
    DELETE
    FROM Crime_officers
    WHERE Crime_officers.Crime_ID = OLD.Crime_ID;

    DELETE
    FROM Appeals
    WHERE Appeals.Crime_ID = OLD.Crime_ID;

    DELETE
    FROM Crime_charges
    WHERE Crime_charges.Crime_ID = OLD.Crime_ID;
END$$
DELIMITER ;

DELIMITER $$
CREATE OR REPLACE TRIGGER cascade_criminal_deletion
AFTER DELETE ON Criminals
FOR EACH ROW
BEGIN
    DELETE
    FROM Alias
    WHERE Alias.Criminal_ID = OLD.Criminal_ID;

    DELETE
    FROM Crimes
    WHERE Crimes.Criminal_ID = OLD.Criminal_ID;

    DELETE
    FROM Sentences
    WHERE Sentences.Criminal_ID = OLD.Criminal_ID;
END$$
DELIMITER ;
