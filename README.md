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
   Run database/AMS_schema.sql
   Run database/sample_data.sql

5. Create .env file (based on .env.example)

6. Run the app:
   python app.py

#Author

Loh Cheng Wei
