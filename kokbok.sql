-- CREATE DATABASE KOKBOK;

USE KOKBOK;

START TRANSACTION;

DROP TABLE IF EXISTS Author_Recipe;
DROP TABLE IF EXISTS Comment_Author;
DROP TABLE IF EXISTS Recipe_Comment;

DROP TABLE IF EXISTS Recipe;
DROP TABLE IF EXISTS Author;
DROP TABLE IF EXISTS Comment;
DROP TABLE IF EXISTS RecipeCategory;

--
CREATE TABLE Recipe (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Title varchar(256) NOT NULL,
       CookingTimePrepMinutes int,
       CookingTimeCookMinutes int,
       Dimension int,
       Description varchar(65000),
       Version int
);


CREATE TABLE Author (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Name varchar(512)
);

CREATE TABLE Author_Recipe (
       AuthorID int,
       RecipeID int,
       FOREIGN KEY (AuthorID) REFERENCES Author(ID),
       FOREIGN KEY (RecipeID) REFERENCES Recipe(ID),
       PRIMARY KEY(AuthorID, RecipeID)
);

CREATE TABLE Comment (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Date date not null,
       Text varchar(65000)
);

CREATE TABLE Comment_Author (
       AuthorID int,
       CommentID int,
       FOREIGN KEY (AuthorID) REFERENCES Author(ID),
       FOREIGN KEY (CommentID) REFERENCES Comment(ID),
       PRIMARY KEY(AuthorID, CommentID)
);

CREATE TABLE Recipe_Comment (
       RecipeID int,
       CommentID int,
       FOREIGN KEY (RecipeID) REFERENCES Recipe(ID),
       FOREIGN KEY (CommentID) REFERENCES Comment(ID),
       PRIMARY KEY(RecipeID, CommentID)
);


-- E.g. dinner, snack...
CREATE TABLE RecipeCategory (
       ID int PRIMARY KEY auto_increment,
       Name varchar(256)
);

COMMIT;
