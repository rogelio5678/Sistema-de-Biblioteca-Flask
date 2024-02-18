DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS book_in_library;
DROP TABLE IF EXISTS user_up;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS provided_book;

CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    email TEXT UNIQUE NOT NULL, 
    password TEXT NOT NULL
);

CREATE TABLE book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    year_publication INT,
    up_for INT NOT NULL,
    FOREIGN KEY (up_for) REFERENCES admin(id)
);

CREATE TABLE book_in_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    items INTEGER NOT NULL,
    id_book INTEGER NOT NULL,
    id_user INTEGER NOT NULL, 
    FOREIGN KEY (id_user) REFERENCES admin (id), 
    FOREIGN KEY (id_book) REFERENCES book (id)
);

CREATE TABLE user_up(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment TEXT,
    email TEXT UNIQUE NOT NULL,
    id_admin INT NOT NULL,
    status BOOLEAN NOT NULL,
    FOREIGN KEY (id_admin) REFERENCES admin (id)
); 

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    id_user_up INTEGER NOT NULL,
    FOREIGN KEY (id_user_up) REFERENCES user_up (id) ON DELETE CASCADE
); 

CREATE TABLE provided_book(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    id_book INTEGER NOT NULL, 
    id_user INTEGER NOT NULL,
    id_admin INTEGER NOT NULL,
    date_request DATETIME NOT NULL,
    date_end DATETIME,
    FOREIGN KEY (id_book) REFERENCES book_in_library (id),
    FOREIGN KEY (id_admin) REFERENCES admin (id),
    FOREIGN KEY (id_user) REFERENCES user (id)
);



