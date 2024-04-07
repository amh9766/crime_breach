ALTER TABLE Criminals
ADD CONSTRAINT check_v_status_domain 
CHECK(V_status LIKE 'Y' OR V_status LIKE 'N');

ALTER TABLE Criminals
ADD CONSTRAINT check_p_status_domain 
CHECK(P_status LIKE 'Y' OR V_status LIKE 'N');

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
