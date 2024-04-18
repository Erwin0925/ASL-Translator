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

ALTER TABLE users
ADD test_correct INT NOT NULL DEFAULT 0;

ALTER TABLE users
ADD total_test INT NOT NULL DEFAULT 0;

EXEC sp_rename 'ASL_Translator.dbo.users.total_wrong', 'test_wrong', 'COLUMN';
