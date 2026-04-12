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

ALTER TABLE staff
ADD COLUMN department VARCHAR(100) AFTER staff_id,
ADD COLUMN employment_type ENUM('full_time', 'part_time') NOT NULL AFTER department,
ADD COLUMN monthly_salary DECIMAL(10.2) DEFAULT NULL AFTER employment_type,
ADD COLUMN hourly_rate DECIMAL(10,2) DEFAULT NULL AFTER monthly_salary;

ALTER TABLE record
ADD COLUMN work_hours DECIMAL(5,2) DEFAULT NULL AFTER out_time,
ADD COLUMN overtime_hours DECIMAL(5,2) DEFAULT 0 AFTER work_hours,
ADD COLUMN late_minutes INT DEFAULT 0 AFTER overtime_hours,
ADD COLUMN status VARCHAR(50) DEFAULT NULL AFTER late_minutes;