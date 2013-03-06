DROP TABLE IF EXISTS demo;
CREATE TABLE demo (upn text, uw_id text, initials text, dob date,
                    txtype text, pre_screeing_date date,
                    arrival_date date, consent text, consent_reason text,
                    consent_comments text, randomize date, baseline text,
                    allocation text, txdate date, injection1 date);


DROP TABLE IF EXISTS checks;
CREATE TABLE checks (amount text, checkdate date, check_no text,
                      upn text);
