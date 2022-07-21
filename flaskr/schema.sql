DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS stest;
DROP TABLE IF EXISTS ptest;


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE stest (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  q1 INTEGER NOT NULL,
  q2 INTEGER NOT NULL,
  q3 INTEGER NOT NULL,
  q4 INTEGER NOT NULL,
  q5 INTEGER NOT NULL,
  q6 INTEGER NOT NULL,
  q7 INTEGER NOT NULL,
  q8 INTEGER NOT NULL,
  q9 INTEGER NOT NULL,
  q10 INTEGER NOT NULL,
  q11 INTEGER NOT NULL,
  q12 INTEGER NOT NULL,
  q13 INTEGER NOT NULL,
  q14 INTEGER NOT NULL,
  q15 INTEGER NOT NULL,
  q16 INTEGER NOT NULL,
  q17 INTEGER NOT NULL,
  q18 INTEGER NOT NULL,
  q19 INTEGER NOT NULL,
  q20 INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)

);

CREATE TABLE ptest (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  target_username TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  q1 INTEGER NOT NULL,
  q2 INTEGER NOT NULL,
  q3 INTEGER NOT NULL,
  q4 INTEGER NOT NULL,
  q5 INTEGER NOT NULL,
  q6 INTEGER NOT NULL,
  q7 INTEGER NOT NULL,
  q8 INTEGER NOT NULL,
  q9 INTEGER NOT NULL,
  q10 INTEGER NOT NULL,
  q11 INTEGER NOT NULL,
  q12 INTEGER NOT NULL,
  q13 INTEGER NOT NULL,
  q14 INTEGER NOT NULL,
  q15 INTEGER NOT NULL,
  q16 INTEGER NOT NULL,
  q17 INTEGER NOT NULL,
  q18 INTEGER NOT NULL,
  q19 INTEGER NOT NULL,
  q20 INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
