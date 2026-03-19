import mysql.connector
from dotenv import load_dotenv
import os
from datetime import date, datetime

load_dotenv()

def get_db():
    """Create and return a database connection"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ==================== ADMIN FUNCTIONS ====================

def check_admin(admin_id, admin_pass):
    """Verify admin credentials"""
    db = get_db()
    cursor = db.cursor()
    sql = "SELECT * FROM admin WHERE admin_id=%s AND admin_pass=%s"
    cursor.execute(sql, (admin_id, admin_pass))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result

# ==================== STAFF FUNCTIONS ====================

def insert_staff(staffname, staff_id, photo_path):
    """Register a new staff member"""
    db = get_db()
    cursor = db.cursor()
    sql = "INSERT INTO staff (staffname, staff_id, photo) VALUES (%s, %s, %s)"
    cursor.execute(sql, (staffname, staff_id, photo_path))
    db.commit()
    cursor.close()
    db.close()

def get_all_staff():
    """Retrieve all staff members"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT staff_id, staffname, photo FROM staff")
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def get_staff_by_id(staff_id):
    """Get one staff member by staff_id"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT staff_id, staffname, photo FROM staff WHERE staff_id = %s", (staff_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result
# ==================== ATTENDANCE FUNCTIONS ====================

def get_today_record(staff_id):
    """Check if staff has a record for today
    Returns: tuple (id,) if record exists, None otherwise
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id FROM record WHERE employee_id=%s AND date=CURDATE()",
        (staff_id,)
    )
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result

def insert_check_in(staff_id):
    """Mark check-in time for staff"""
    staff = get_staff_by_id(staff_id)
    if not staff:
        raise Exception("Staff not found")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO record (employee_id, employee_name, date, in_time) VALUES (%s, %s, CURDATE(), NOW())",
        (staff_id, staff["staffname"])
    )
    db.commit()
    cursor.close()
    db.close()

def update_check_out(staff_id):
    """Mark check-out time for staff"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE record SET out_time=NOW() WHERE employee_id=%s AND date=CURDATE()",
        (staff_id,)
    )
    db.commit()
    cursor.close()
    db.close()

# ==================== RECORD MANAGEMENT ====================

def get_records(date=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if date:
        cursor.execute("""
            SELECT id, employee_id, employee_name, date, in_time, out_time, remarks
            FROM record
            WHERE date = %s
            ORDER BY in_time DESC
        """, (date,))
    else:
        cursor.execute("""
            SELECT id, employee_id, employee_name, date, in_time, out_time, remarks
            FROM record
            ORDER BY date DESC, in_time DESC
        """)

    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def delete_record(record_id):
    """Delete a specific attendance record"""
    db = get_db()
    cursor = db.cursor()
    sql = "DELETE FROM record WHERE id = %s"
    cursor.execute(sql, (record_id,))
    db.commit()
    cursor.close()
    db.close()

def update_remark(record_id, remark):
    """Update the remark for a specific record"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE record SET remarks=%s WHERE id=%s", (remark, record_id))
    db.commit()
    cursor.close()
    db.close()

def get_all_staff_details():
    """Retrieve all staff details for listing page"""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT staff_id, staffname, photo
        FROM staff
        ORDER BY staffname ASC
    """)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def delete_staff(staff_id):
    """Delete a staff member by staff_id"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM staff WHERE staff_id = %s", (staff_id,))
    db.commit()
    cursor.close()
    db.close()