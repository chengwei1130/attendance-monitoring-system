from flask import Flask, render_template, Response, request, redirect, url_for, flash, session
from db import check_admin, insert_staff, get_records, delete_record, get_all_staff_details, delete_staff
from camera import generate_frame
import os
from functools import wraps
from dotenv import load_dotenv
import csv
import io

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') 

# ==================== AUTHENTICATION ====================

@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        admin_id = request.form.get('admin_id', '').strip()
        admin_pass = request.form.get('admin_pass', '').strip()

        if not admin_id or not admin_pass:
            flash('Please enter both admin ID and password', 'error')
            return render_template('login.html')

        if check_admin(admin_id, admin_pass):
            session['logged_in'] = True
            session['admin_id'] = admin_id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid admin ID or password', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # remove all session info
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('You need to login first!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
# ==================== STAFF REGISTRATION ====================

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Staff registration page"""
    if request.method == 'POST':
        staffname = request.form.get('staffname', '').strip()
        staff_id = request.form.get('staff_id', '').strip()
        photo = request.files.get('photo')

        # Validation
        if not staffname or not staff_id:
            flash('Staff name and ID are required', 'error')
            return render_template('register.html')

        if not photo or photo.filename == '':
            flash('Please upload a staff photo', 'error')
            return render_template('register.html')

        # Save photo
        upload_dir = 'static/uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        # Use staff_id in filename to avoid conflicts
        file_ext = os.path.splitext(photo.filename)[1]
        photo_filename = f"{staff_id}{file_ext}"
        photo_path = os.path.join(upload_dir, photo_filename).replace("\\", "/")
        photo.save(photo_path)

        # Insert into database
        try:
            insert_staff(staffname, staff_id, photo_path)
            flash(f'Staff {staffname} registered successfully!', 'success')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f'Error registering staff: {str(e)}', 'error')
            return render_template('register.html')

    return render_template('register.html')

# ==================== ATTENDANCE & DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/staff')
@login_required
def staff_list():
    """View all registered staff"""
    staff_members = get_all_staff_details()
    return render_template('staff_list.html', staff_members=staff_members)

@app.route('/delete_staff/<staff_id>', methods=['POST'])
@login_required
def delete_staff_route(staff_id):
    """Delete a staff member"""
    try:
        delete_staff(staff_id)
        flash('Staff deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting staff: {str(e)}', 'error')
    return redirect(url_for('staff_list'))

@app.route('/attendance')
@login_required
def attendance():
    """Live attendance monitoring page"""
    return render_template('attendance.html')

@app.route('/video_feed')   
@login_required
def video_feed():
    """Video stream endpoint for face recognition"""
    return Response(
        generate_frame(),
        mimetype='multipart/x-mixed-replace; boundary=frame',
        headers={
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    )

# ==================== RECORD MANAGEMENT ====================

@app.route('/record', methods=['GET'])
@login_required
def record():
    """View attendance records with optional date filter"""
    selected_date = request.args.get('date')
    records = get_records(date=selected_date)
    return render_template('record.html', records=records, selected_date=selected_date)

@app.route('/delete_record/<int:record_id>', methods=['POST'])
@login_required
def delete_record_route(record_id):
    """Delete an attendance record"""
    try:
        delete_record(record_id)
        flash('Record deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting record: {str(e)}', 'error')
    return redirect(url_for('record'))

@app.route('/update_remark/<int:record_id>', methods=['POST'])
@login_required
def update_remark(record_id):
    """Update remark for a specific record"""
    from db import update_remark as db_update_remark
    remark = request.form.get('remark', '').strip()
    try:
        db_update_remark(record_id, remark)
        flash('Remark updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating remark: {str(e)}', 'error')
    return redirect(url_for('record'))

@app.route('/download_csv')
@login_required
def download_csv():
    """Download attendance records as CSV, optionally filtered by date"""
    selected_date = request.args.get('date')
    records = get_records(date=selected_date)

    if not records:
        flash('No records found to download', 'error')
        return redirect(url_for('record', date=selected_date))

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Staff Name', 'Staff ID', 'Date', 'Check-In', 'Check-Out', 'Remark'])

    for r in records:
        writer.writerow([
            r.get('employee_name', ''),
            r.get('employee_id', ''),
            r.get('date', ''),
            r['in_time'].strftime('%Y-%m-%d %H:%M:%S') if r.get('in_time') else '',
            r['out_time'].strftime('%Y-%m-%d %H:%M:%S') if r.get('out_time') else '',
            r.get('remarks', '')
        ])

    csv_data = output.getvalue()
    output.close()

    filename = f"attendance_records_{selected_date}.csv" if selected_date else "attendance_records_all.csv"

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )
# ==================== UTILITY / DEBUG ====================

@app.route('/test_cam')
@login_required
def test_cam():
    """Test camera connectivity"""
    from camera import camera
    success, frame = camera.read()
    if success:
        return "✓ Camera is working properly!"
    else:
        return "✗ Camera not found or not accessible!"

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
@login_required
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
@login_required
def internal_error(e):
    return render_template('500.html'), 500

# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('temp_frames', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)