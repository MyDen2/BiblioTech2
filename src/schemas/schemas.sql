-- CREATE SCHEMA IF NOT EXISTS bibliotech;

-- CREATE TABLE IF NOT EXISTS bibliotech.users (
-- 	user_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
--     email VARCHAR(50) UNIQUE NOT NULL,
--     pseudo VARCHAR(50) UNIQUE NOT NULL,
--     user_password VARCHAR(55) NOT NULL, 
-- 	first_name VARCHAR(50) NOT NULL, 
-- 	last_name VARCHAR(50) NOT NULL,
--     birth_date DATE NOT NULL,
--     gender BOOLEAN
-- );

-- CREATE TABLE IF NOT EXISTS bibliotech.books (
-- 	book_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
--     title VARCHAR(100) NOT NULL,
--     summary VARCHAR(500) NOT NULL,
--     release_year INT NOT NULL,
--     number_pages INT NOT NULL 
-- );

-- CREATE TABLE IF NOT EXISTS bibliotech.grades (
-- 	book_id INT NOT NULL,
-- 	user_id INT NOT NULL,
-- 	grade INT NOT NULL CHECK (grade BETWEEN 0 AND 5),
-- 	CONSTRAINT pk_grade PRIMARY KEY (book_id, user_id),
-- 	CONSTRAINT fk_book_id FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id),
-- 	CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES bibliotech.users(user_id)
-- );

-- CREATE TABLE IF NOT EXISTS bibliotech.genres (
-- 	genre_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
--     genre VARCHAR(20) UNIQUE NOT NULL
-- );

-- CREATE TABLE IF NOT EXISTS bibliotech.authors (
-- 	author_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
-- 	first_name VARCHAR(50) NOT NULL, 
-- 	last_name VARCHAR(50) NOT NULL,
--     birth_date DATE NOT NULL,
--     nationality VARCHAR(50) NOT NULL
-- );

-- CREATE TABLE IF NOT EXISTS bibliotech.book_author (
--     book_id INT NOT NULL,
--     author_id INT NOT NULL,
--     CONSTRAINT pk_book_author PRIMARY KEY (book_id, author_id),
--     CONSTRAINT fk_book_author_book FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id),
--     CONSTRAINT fk_book_author_author FOREIGN KEY (author_id) REFERENCES bibliotech.authors(author_id)
-- );

-- CREATE TABLE IF NOT EXISTS bibliotech.book_genre (
--     book_id INT NOT NULL,
--     genre_id INT NOT NULL,
--     CONSTRAINT pk_book_genre PRIMARY KEY (book_id, genre_id),
--     CONSTRAINT fk_book_genre_book FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id),
--     CONSTRAINT fk_book_genre_genre FOREIGN KEY (genre_id) REFERENCES bibliotech.genres(genre_id)
-- );

CREATE SCHEMA IF NOT EXISTS bibliotech;

CREATE TABLE IF NOT EXISTS bibliotech.users (
    user_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    pseudo VARCHAR(50) UNIQUE NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS bibliotech.books (
    book_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    summary TEXT NOT NULL,
    release_year INT NOT NULL,
    number_pages INT NOT NULL CHECK (number_pages > 0)
);

CREATE TABLE IF NOT EXISTS bibliotech.authors (
    author_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    nationality VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS bibliotech.genres (
    genre_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS bibliotech.themes (
    theme_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS bibliotech.book_author (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES bibliotech.authors(author_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bibliotech.book_genre (
    book_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES bibliotech.genres(genre_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bibliotech.book_theme (
    book_id INT NOT NULL,
    theme_id INT NOT NULL,
    PRIMARY KEY (book_id, theme_id),
    FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (theme_id) REFERENCES bibliotech.themes(theme_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bibliotech.grades (
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    grade INT NOT NULL CHECK (grade BETWEEN 0 AND 5),
    grade_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, user_id),
    FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES bibliotech.users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bibliotech.interactions (
    interaction_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    interaction_type VARCHAR(30) NOT NULL,
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES bibliotech.users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bibliotech.recommendations (
    recommendation_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    score DECIMAL(5,4) NOT NULL,
    reason TEXT,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES bibliotech.users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id) ON DELETE CASCADE
);

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS bibliotech.book_embeddings (
    book_id INT PRIMARY KEY,
    vector VECTOR(1536) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES bibliotech.books(book_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bibliotech.user_embeddings (
    user_id INT PRIMARY KEY,
    vector VECTOR(1536) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES bibliotech.users(user_id) ON DELETE CASCADE
);