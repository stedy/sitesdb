drop table if exists test;
create table test (
  id integer,
  title string not null);

drop table if exists user;
create table user (
  fullname string not null,
  username string not null,
  email string not null,
  password string not null
);
