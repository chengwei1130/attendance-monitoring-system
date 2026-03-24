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

4. Setup database:
   Install MySQL WorkBench
   Create a new connection (Port: 3306)
   Import and run: 
   database/AMS_schema.sql
   database/sample_data.sql

6. Create .env file (based on .env.example)
   Change password and secret_key

8. Run the app:
   python app.py

## Author

Loh Cheng Wei
