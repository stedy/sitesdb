DROP TABLE IF EXISTS demo;
CREATE TABLE demo (upn text, uw_id text, initials text, dob date,
                    hispanic text, gender text, amer_ind text,
                    asian text, hipac text, black text, white text,
                    unknown_race text, pt_userid text,
                    txtype text, pre_screening_date date,
                    arrival_date date, consent text, consent_reason text,
                    consent_comments text, randomize date, baseline text,
                    allocation text, txdate date, injection1 date
                  injection2p date, injection2a date,
                  injection3p date, injection3a date,
                  injection4p date, injection4a date,
                  injection5p date, injection5a date,
                  injection6p date, injection6a date,
                  injection7p date, injection7a date
                );


DROP TABLE IF EXISTS checks;
CREATE TABLE checks (amount text, checkdate date, check_no text,
                      upn text);
