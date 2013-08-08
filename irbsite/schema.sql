DROP TABLE IF EXISTS createdby;
CREATE TABLE createdby (
  Protocol text,
  user_id text,
  pub_date integer
);

DROP TABLE IF EXISTS studystaff;
CREATE TABLE studystaff (
  Protocol text,
  Name text,
  role text,
  id Integer PRIMARY KEY AUTOINCREMENT
);
