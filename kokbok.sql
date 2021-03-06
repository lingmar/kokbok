CREATE DATABASE IF NOT EXISTS %(dbname)s;

USE %(dbname)s;

START TRANSACTION;

DROP TABLE IF EXISTS Author_Recipe;
DROP TABLE IF EXISTS Comment_Author;
DROP TABLE IF EXISTS Recipe_Comment;
DROP TABLE IF EXISTS IngredientList_Ingredient;
DROP TABLE IF EXISTS Recipe_Instruction;
DROP TABLE IF EXISTS Recipe_Picture;
DROP TABLE IF EXISTS Ingredient_IngredientCategory;

DROP TABLE IF EXISTS IngredientList;
DROP TABLE IF EXISTS Recipe;
DROP TABLE IF EXISTS Author;
DROP TABLE IF EXISTS Comment;
DROP TABLE IF EXISTS Instruction;
DROP TABLE IF EXISTS RecipeCategory;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS IngredientCategory;
DROP TABLE IF EXISTS Picture;

CREATE TABLE Recipe (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Title varchar(256) NOT NULL,
       CookingTimePrepMinutes int,
       CookingTimeCookMinutes int,
       Servings int,
       Description text,
       Version int
);

CREATE TABLE Author (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Name varchar(512) UNIQUE NOT NULL
);

CREATE TABLE Author_Recipe (
       AuthorID int,
       RecipeID int,
       FOREIGN KEY (AuthorID) REFERENCES Author(ID) ON DELETE CASCADE,
       FOREIGN KEY (RecipeID) REFERENCES Recipe(ID) ON DELETE CASCADE,
       PRIMARY KEY(AuthorID, RecipeID)
);

CREATE TABLE Comment (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Date date not null,
       Text TEXT
);

CREATE TABLE Comment_Author (
       AuthorID int,
       CommentID int,
       FOREIGN KEY (AuthorID) REFERENCES Author(ID) ON DELETE CASCADE,
       FOREIGN KEY (CommentID) REFERENCES Comment(ID) ON DELETE CASCADE,
       PRIMARY KEY(AuthorID, CommentID)
);

CREATE TABLE Recipe_Comment (
       RecipeID int,
       CommentID int,
       FOREIGN KEY (RecipeID) REFERENCES Recipe(ID) ON DELETE CASCADE,
       FOREIGN KEY (CommentID) REFERENCES Comment(ID) ON DELETE CASCADE,
       PRIMARY KEY(RecipeID, CommentID)
);

-- E.g. dinner, snack...
CREATE TABLE RecipeCategory (
       ID int PRIMARY KEY auto_increment,
       Name varchar(256)
);

CREATE TABLE IngredientList (
       ID int PRIMARY KEY auto_increment,
       Title varchar(256),
       RecipeID int,
       FOREIGN KEY (RecipeID) REFERENCES Recipe(ID) ON DELETE CASCADE
);

CREATE TABLE Ingredient (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Name varchar(1024) UNIQUE NOT NULL,
       Price int UNSIGNED,
       Energy int UNSIGNED,
       Fat int UNSIGNED,
       Protein int UNSIGNED,
       Carbohydrate int UNSIGNED,
       GramsPerMilliliter int UNSIGNED,
       GramsPerUnit int UNSIGNED
);

CREATE TABLE IngredientList_Ingredient (
       IngredientListID int,
       IngredientID int,
       PrepNotes varchar(2048),
       Magnitude int UNSIGNED,
       Unit enum('g', 'ml', 'pcs'),
       FOREIGN KEY (IngredientListID) REFERENCES IngredientList(ID) ON DELETE CASCADE,
       FOREIGN KEY (IngredientID) REFERENCES Ingredient(ID),
       PRIMARY KEY(IngredientListID, IngredientID)
);

CREATE TABLE IngredientCategory (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Name varchar(256)
);

CREATE TABLE Ingredient_IngredientCategory (
       IngredientID int,
       IngredientCategoryID int,
       FOREIGN KEY (IngredientID) REFERENCES Ingredient(ID) ON DELETE CASCADE,
       FOREIGN KEY (IngredientCategoryID) REFERENCES IngredientCategory(ID) ON DELETE CASCADE,
       PRIMARY KEY(IngredientID, IngredientCategoryID)
);

CREATE TABLE Instruction (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Text TEXT
);

CREATE TABLE Recipe_Instruction (
       RecipeID int,
       InstructionID int,
       Step int,
       FOREIGN KEY (RecipeID) REFERENCES Recipe(ID) ON DELETE CASCADE,
       FOREIGN KEY (InstructionID) REFERENCES Instruction(ID) ON DELETE CASCADE,
       PRIMARY KEY(RecipeID, InstructionID)
);

CREATE TABLE Picture (
       ID int PRIMARY KEY AUTO_INCREMENT,
       Filename varchar(256) UNIQUE NOT NULL
);

CREATE TABLE Recipe_Picture (
       RecipeID int,
       PictureID int,
       FOREIGN KEY (RecipeID) REFERENCES Recipe(ID) ON DELETE CASCADE,
       FOREIGN KEY (PictureID) REFERENCES Picture(ID) ON DELETE CASCADE,
       PRIMARY KEY(RecipeID, PictureID)
);

COMMIT;
