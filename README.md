# Attendance Monitoring System (AMS)

A Flask-based attendance system using face recognition.

## Features
- Admin login
- Staff management
- Face detection (DeepFace)
- Check-in / Check-out system
- Attendance records
- CSV export

## Tech Stack
- Flask
- OpenCV
- DeepFace
- MySQL

## Setup

1. Clone repository

2. Create virtual environment:
   python -m venv venv
   venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Create .env file (based on .env.example)
   Change password and secret_key


## Setup database

1. Install MySQL WorkBench
   
2. Create a new connection with port 3306
   
3. Import and run create_table.sql, insert_admin.sql

4. Run the code - 
   python app.py

## Author

Loh Cheng Wei
