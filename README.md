Team 19

Tutorial how to run codes in the Software folder.

Download the folder called final website which can be found in 'Software', inside there is a subfolder called templates, these are all the web pages and php files needed to run the wesbite. We recommend using xampp to run the site.

Make sure that the files "models","ml_model_runner.py" and "simulate_data.py" are in the same folder.



HOW TO SIMULATE DATA

1. Open XAMPP Control Panel 
     Start Apache and MySQL
     Open Phpadmin in browser http://localhost/phpmyadmin/
     Create database using sql code below:


CREATE DATABASE IF NOT EXISTS rakusens;

USE rakusens;

-- Table for Line 4 sensors (8 sensors: r01 to r08)
CREATE TABLE IF NOT EXISTS line4_sensors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    r01 FLOAT NOT NULL,
    r02 FLOAT NOT NULL,
    r03 FLOAT NOT NULL,
    r04 FLOAT NOT NULL,
    r05 FLOAT NOT NULL,
    r06 FLOAT NOT NULL,
    r07 FLOAT NOT NULL,
    r08 FLOAT NOT NULL
);

-- Table for Line 5 sensors (17 sensors: r01 to r17)
CREATE TABLE IF NOT EXISTS line5_sensors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    r01 FLOAT NOT NULL,
    r02 FLOAT NOT NULL,
    r03 FLOAT NOT NULL,
    r04 FLOAT NOT NULL,
    r05 FLOAT NOT NULL,
    r06 FLOAT NOT NULL,
    r07 FLOAT NOT NULL,
    r08 FLOAT NOT NULL,
    r09 FLOAT NOT NULL,
    r10 FLOAT NOT NULL,
    r11 FLOAT NOT NULL,
    r12 FLOAT NOT NULL,
    r13 FLOAT NOT NULL,
    r14 FLOAT NOT NULL,
    r15 FLOAT NOT NULL,
    r16 FLOAT NOT NULL,
    r17 FLOAT NOT NULL
);

 CREATE TABLE IF NOT EXISTS `admins` (
   `id` INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   `username` VARCHAR(50) NOT NULL UNIQUE,
   `password` VARCHAR(255) NOT NULL,
   `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
 INSERT INTO `admins` (`id`, `username`, `password`, `created_at`) VALUES ('1', 'admin1', 'adminpass', current_timestamp());
 -- Users table (for regular users)
 CREATE TABLE IF NOT EXISTS `users` (
   `id` INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
   `username` VARCHAR(50) NOT NULL UNIQUE,
   `email` VARCHAR(100) NOT NULL UNIQUE,
   `password` VARCHAR(255) NOT NULL,
   `created_by` INT(11) UNSIGNED,
   `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (`created_by`) REFERENCES `admins`(`id`) ON DELETE SET NULL
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
 
 CREATE TABLE IF NOT EXISTS sensor_flags (
     id INT AUTO_INCREMENT PRIMARY KEY,
     line_number INT NOT NULL,
     sensor_id VARCHAR(4) NOT NULL,
     status ENUM('green', 'amber', 'red') NOT NULL,
     timestamp DATETIME NOT NULL
DELETE FROM `users` WHERE `id` = 1;  /* Replace 1 with actual user_id */


1 create a python environment in vscode and make sure the files "models","ml_model_runner.py" and "simulate_data.py" are in the   same folder and create a python environment in vs code and make sure it is in the python environment workspace in vscode 

2. Open simulate_data.py in vscode
   
3. type python --version   inside vscode terminal to check if you have python
   if error you need to download or make the right path

4. type   pip install mysql-connector-python    inside vscode terminal
   
5. type pip install flask      inside vscode terminal

6. type   pip install numpy     inside vscode terminal

7. Run the code (Every 30 seconds will insert data into database check on phpadmin if it works.)

8. You can stop the code by killing the terminal




HOW TO FLAG DATA UNSING ML

1. Open ml_model_runner.py in vs code

2. Make sure the folder with the ml models called "models" is in the same folder as ml_model_runner.py

3. type   pip install pandas     inside vscode terminal ( Do Step 4. and 5. from above if you haven't done it already.) 

4. type   pip install joblib

5. type   pip install prophet

6. type pip install flask

7. run the code (if 30 seconds is too quick last line of the code change the number 30 to whatever u want)

