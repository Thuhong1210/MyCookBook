CREATE DATABASE IF NOT EXISTS MyCookBook
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE MyCookBook;

CREATE TABLE cuisines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuisine_type VARCHAR(255) NOT NULL
);

CREATE TABLE meals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    meal_type VARCHAR(255) NOT NULL
);

CREATE TABLE diets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    diet_type VARCHAR(255) NOT NULL
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_name VARCHAR(255) NOT NULL,
    description TEXT,
    cuisine_type VARCHAR(255),
    meal_type VARCHAR(255),
    cooking_time VARCHAR(100),
    diet_type VARCHAR(255),
    servings VARCHAR(50),
    ingredients JSON,
    directions JSON,
    author INT NOT NULL,
    image VARCHAR(500),
    FOREIGN KEY (author) REFERENCES users(id)
);

CREATE TABLE user_recipes (
    user_id INT,
    recipe_id INT,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);
