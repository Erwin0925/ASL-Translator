-- Create the database
CREATE DATABASE ASL_Translator;

-- Use the newly created database
USE ASL_Translator;

CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(255) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    security_question NVARCHAR(255) NOT NULL,
    security_question_answer NVARCHAR(255) NOT NULL,
    badge NVARCHAR(255) NOT NULL
);
