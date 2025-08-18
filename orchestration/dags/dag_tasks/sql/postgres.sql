

DROP TABLE IF EXISTS 
    sub16_healthinfo_test,
    sub16_healthinfo_test2,
    test, test2, test3,
    records_ptt,
    records_ptt2,
    reg16_healthinfo_test2;

CREATE TABLE IF NOT EXISTS reg16_healthinfo(
                            names VARCHAR,
                            sex VARCHAR,
                            birthdate DATE,
                            blood_group VARCHAR,
                            ssn VARCHAR,
                            mail VARCHAR,
                            jobs VARCHAR,
                            address VARCHAR,
                            residence VARCHAR,
                            diagnosis VARCHAR
                        );