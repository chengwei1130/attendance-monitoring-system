CREATE DATABASE IF NOT EXISTS AMS;
USE AMS;

CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staffname VARCHAR(100) NOT NULL,
    staff_id VARCHAR(50) NOT NULL UNIQUE,
    photo VARCHAR(255) NOT NULL
);

CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    adminname VARCHAR(100) NOT NULL,
    admin_id VARCHAR(50) NOT NULL UNIQUE,
    admin_pass VARCHAR(50) NOT NULL
);

CREATE TABLE record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    in_time DATETIME NOT NULL,
    out_time DATETIME,
    remarks VARCHAR(255),
    FOREIGN KEY (employee_id) REFERENCES staff(staff_id)
);

ALTER TABLE record 
ADD COLUMN employee_name VARCHAR(100) NOT NULL AFTER employee_id;

UPDATE record r
JOIN staff s ON r.employee_id = s.staff_id
SET r.employee_name = s.staffname;