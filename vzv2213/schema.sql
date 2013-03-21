DROP TABLE IF EXISTS demo;
CREATE TABLE demo (upn text, uw_id text, initials text, dob date,
                    hispanic text, gender text, ethnicity text,
                    pt_userid text, txdate date,
                    txtype text, consent text, consent_reason text,
                    randomize text, baseline text,
                    allocation text, txtext text, injection1 date,
                  injection2p date, injection2a date,
                  injection3p date, injection3a date,
                  injection4p date, injection4a date,
                  injection5p date, injection5a date,
                  injection6p date, injection6a date,
                  injection7p date, injection7a date,
                  check1date date, check1amt text, check1no text,
                  check2date date, check2amt text, check2no text,
                  check3date date, check3amt text, check3no text,
                  check4date date, check4amt text, check4no text,
                  check5date date, check5amt text, check5no text,
                  check6date date, check6amt text, check6no text,
                  check7date date, check7amt text, check7no text
                );


DROP TABLE IF EXISTS user;
CREATE TABLE user (name text, user_id text);
