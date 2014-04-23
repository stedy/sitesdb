DROP TABLE IF EXISTS demo;
CREATE TABLE demo (Subject_ID text, pt_init text, Name text,
                    uwid text, conditioning_start_date text,
                    Status text, txdate text, Donrep text);

DROP TABLE IF EXISTS events;
CREATE TABLE events (Subject_ID text, event text,
                     eventdate date, blooddraw text,
                     bloodprocessed, comments text);

DROP TABLE IF EXISTS user;
CREATE TABLE user (name text, user_id text);

DROP TABLE IF EXISTS kit;
CREATE TABLE kit (Subject_ID text, kit_event text, kit_eventdate date,
                  id integer PRIMARY KEY AUTOINCREMENT);

DROP TABLE IF EXISTS checks;
CREATE TABLE checks (Subject_ID text, amount text, purpose text, checkno text,
                     checkdeliver text, eventdate date);
