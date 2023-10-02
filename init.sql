DROP TABLE IF EXISTS prep_users;
CREATE TABLE prep_users (user_id serial PRIMARY KEY, user_name VARCHAR(50));

INSERT INTO prep_users VALUES (0, 'test');