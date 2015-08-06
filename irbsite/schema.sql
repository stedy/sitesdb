DROP TABLE IF EXISTS user;
CREATE TABLE user (user_id integer primary key autoincrement, username string,
                      email string, pw_hash string);
