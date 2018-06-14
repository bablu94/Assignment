create table users(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,username VARCHAR(32),password_hash VARCHAR(128));

create table contacts (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,name VARCHAR(64),email VARCHAR(256),mobile BIGINT UNSIGNED, userid INT, INDEX (email,userid),INDEX(name,userid));
