# type: ignore
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash 
import json
import os
from datetime import datetime
import hashlib
import hashlib

from config.settings import Config
from models import db
from models.user import User


app = Flask(__name__)
app.jinja_env.loader.searchpath = [
    'templates', 'templates/shared', 'templates/auth', 
    'templates/admin', 'templates/mechanic', 'templates/quality', 'templates/mws'
]

# Memuat konfigurasi dari objek Config
app.config.from_object(Config)

# Inisialisasi database dengan aplikasi
db.init_app(app)

# Data storage 
DATA_FILE = 'worksheet_data.json'
JOB_STEPS_TEMPLATES = {
    "F.Test": [
        {"no": 1, "description": "Incoming Record",  "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""},
        {"no": 2, "description": "Functional Test",  "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""},
        {"no": 3, "description": "Fault Isolation",  "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""},
        {"no": 4, "description": "Disassembly",      "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""},
        {"no": 5, "description": "Cleaning",         "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""},
        {"no": 6, "description": "Check",            "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""},
        {"no": 7, "description": "Assembly",         "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""},
        {"no": 8, "description": "Functional Test",  "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""},
        {"no": 9, "description": "FOD Control",      "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""},
        {"no": 10, "description": "Final Inspection","details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""}
    ],
    "Repair": [
        {"no": i+1, "description": desc, "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""}
        for i, desc in enumerate([
            "Incoming Record", "Functional Test", "Fault Isolation", "Disassembly",
            "Cleaning", "Check", "Assembly", "Functional Test", "FOD Control", "Final Inspection"
        ])
    ],
    "Overhaul": [
        {"no": i+1, "description": desc, "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""}
        for i, desc in enumerate([
            "Incoming Record", "Functional Test", "Fault Isolation", "Disassembly",
            "Cleaning", "Check", "Assembly", "Functional Test", "FOD Control", "Final Inspection"
        ])
    ],
    "IRAN": [
        {"no": i+1, "description": desc, "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""}
        for i, desc in enumerate([
            "Incoming Record", "Functional Test", "Fault Isolation", "Disassembly",
            "Cleaning", "Check", "Assembly", "Functional Test", "FOD Control", "Final Inspection"
        ])
    ],
    "Recharging": [
        {"no": i+1, "description": desc, "details": [], "status": "pending", "completedBy": "", "completedDate": "", "man": "", "hours": "", "tech": "", "insp": ""}
        for i, desc in enumerate([
            "Incoming Record", "Functional Test", "Fault Isolation", "Disassembly",
            "Cleaning", "Check", "Assembly", "Functional Test", "FOD Control", "Final Inspection"
        ])
    ]
}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return get_default_data()

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Tampilan Error
def render_error_page(error):
    """Fungsi generik untuk menampilkan halaman error."""
    error_map = {
        403: ("Akses Ditolak", "Anda tidak memiliki izin untuk mengakses halaman ini."),
        404: ("Halaman Tidak Ditemukan", "Maaf, kami tidak dapat menemukan halaman yang Anda cari. Mungkin URL salah ketik."),
        500: ("Terjadi Masalah di Server", "Tim kami telah diberitahu tentang masalah ini. Silakan coba lagi nanti.")
    }
    
    error_code = getattr(error, 'code', 500)
    error_title, error_message = error_map.get(error_code, error_map[500])
    return render_template(
        'errors/error.html', 
        error_code=error_code,
        error_title=error_title,
        error_message=error_message
    ), error_code

@app.errorhandler(403)
def forbidden(e):
    return render_error_page(e)

@app.errorhandler(404)
def page_not_found(e):
    return render_error_page(e)

@app.errorhandler(500)
def internal_server_error(e):
    return render_error_page(e)

# Landing Page
@app.route('/')
def index():
    data = load_data()
    return render_template('shared/index.html', parts=data['parts'])

def get_users_from_db():
    """Mengambil semua user dari DB dan mengubahnya ke format dictionary."""
    all_users = User.query.all()
    users_dict = {user.nik: {
        'nik': user.nik,
        'name': user.name,
        'role': user.role,
        'position': user.position,
        'description': user.description
    } for user in all_users}
    return users_dict


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nik = request.form.get('nik')
        password = request.form.get('password')

        # [PERBAIKAN] Tambahkan validasi di sini untuk mencegah input kosong
        if not nik or not password:
            flash('NIK dan password wajib diisi!', 'error')
            return redirect(url_for('login'))

        # Kode di bawah ini hanya akan berjalan jika NIK dan password sudah diisi
        user = User.query.filter_by(nik=nik).first()

        if user and user.check_password(password):
            session['user'] = {
                'nik': user.nik, 'name': user.name, 'role': user.role,
                'position': user.position, 'description': user.description
            }
            flash(f"Selamat datang kembali, {user.name}!", 'success')
            return redirect(url_for('dashboard'))
        
        flash('NIK atau password salah!', 'error')
        return redirect(url_for('login'))
    
    return render_template('auth/login.html')

# Logout (Tidak ada perubahan, sudah benar)
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Dahboard (Tidak ada perubahan, sudah benar)
@app.route('/dashboard')
def dashboard():
    return redirect(url_for('role_dashboard'))

# Admin
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('login'))
    
    # Logika diubah: Mengambil data parts dari JSON, tapi data users dari DB
    data = load_data()
    users = get_users_from_db()
    
    user_parts = data.get('parts', {})
    
    return render_template('admin/admin_dashboard.html', user=session['user'], parts=user_parts, users=users)

# Route untuk halaman utama manajemen pengguna
@app.route('/users')
def manage_users():
    if 'user' not in session or session['user']['role'] not in ['admin', 'superadmin']:
        return "Unauthorized", 403
    
    # Logika diubah: Mengambil data users dari DB
    all_users_from_db = get_users_from_db()
    return render_template('user-management/manage_user.html', users=all_users_from_db, session=session)

# Route untuk mengambil data satu pengguna (untuk form edit)
@app.route('/get_user/<nik>')
def get_user(nik):
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
        
    # Logika diubah: Mengambil satu user dari DB
    user = User.query.get(nik)

    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Mengembalikan data dalam format JSON
    return jsonify({
        'nik': user.nik, 'name': user.name, 'role': user.role,
        'position': user.position, 'description': user.description
    })

# Route untuk menyimpan (menambah atau mengedit) pengguna
@app.route('/save_user', methods=['POST'])
def save_user():
    if 'user' not in session or session['user']['role'] not in ['admin', 'superadmin']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    req_data = request.get_json()
    nik = req_data.get('nik')
    nik_original = req_data.get('nik_original')

    if not nik:
        return jsonify({'success': False, 'error': 'NIK tidak boleh kosong.'}), 400

    if nik_original:  # Mode Edit
        user_to_update = User.query.get(nik_original)
        if not user_to_update: return jsonify({'success': False, 'error': 'Pengguna tidak ditemukan.'}), 404
        if nik != nik_original and User.query.get(nik): return jsonify({'success': False, 'error': f'NIK {nik} sudah ada.'}), 400
        
        user_to_update.nik = nik
        user_to_update.name = req_data.get('name')
        user_to_update.role = req_data.get('role')
        user_to_update.position = req_data.get('position')
        user_to_update.description = req_data.get('description')
        if req_data.get('password'):
            user_to_update.set_password(req_data.get('password'))
    else:  # Mode Tambah
        if User.query.get(nik): return jsonify({'success': False, 'error': f'NIK {nik} sudah ada.'}), 400
        if not req_data.get('password'): return jsonify({'success': False, 'error': 'Password wajib diisi untuk pengguna baru.'}), 400
        new_user = User(
            nik=nik, name=req_data.get('name'), role=req_data.get('role'),
            position=req_data.get('position'), description=req_data.get('description')
        )
        new_user.set_password(req_data.get('password'))
        db.session.add(new_user)
        
    db.session.commit()
    return jsonify({'success': True})

# Route untuk menghapus pengguna
@app.route('/delete_user/<nik>', methods=['DELETE'])
def delete_user(nik):
    if 'user' not in session or session['user']['role'] not in ['admin', 'superadmin']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    user_to_delete = User.query.get(nik)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'User not found'}), 404

# Dashboard Mechanic
@app.route('/mechanic-dashboard')
def mechanic_dashboard():
    if 'user' not in session or session['user']['role'] != 'mechanic':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('login'))
    
    user_nik = session['user']['nik']
    data = load_data()
    # Logika diubah: Users tidak perlu diambil lagi di sini kecuali akan ditampilkan
    # Kita hanya perlu filter parts berdasarkan NIK dari session
    user_parts = {k: v for k, v in data.get('parts', {}).items() if v.get('assignedTo') == user_nik}
    
    return render_template('mechanic/mechanic_dashboard.html', user=session['user'], parts=user_parts)

# Dashboard Quality Inspector 1
@app.route('/quality1-dashboard')
def quality1_dashboard():
    if 'user' not in session or session['user']['role'] != 'quality1':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('login'))
    
    data = load_data()
    users = get_users_from_db() # Ambil user dari DB untuk ditampilkan
    
    return render_template('quality/quality1_dashboard.html', user=session['user'], parts=data.get('parts', {}), users=users)

# Dashboard Quality Inspector 2
@app.route('/quality2-dashboard')
def quality2_dashboard():
    if 'user' not in session or session['user']['role'] != 'quality2':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('login'))
        
    data = load_data()
    users = get_users_from_db() 
    return render_template('quality/quality2_dashboard.html', user=session['user'], parts=data.get('parts', {}), users=users)

# Dashboard Superadmin
@app.route('/superadmin-dashboard')
def superadmin_dashboard():
    if 'user' not in session or session['user']['role'] != 'superadmin':
        flash('Akses ditolak!', 'error')
        return redirect(url_for('login'))
    
    data = load_data()
    users = get_users_from_db() # Ambil user dari DB untuk ditampilkan
    
    return render_template('superadmin/superadmin_dashboard.html', user=session['user'], parts=data.get('parts', {}), users=users)

# Pengarah Dashboard berdasarkan Role (Tidak ada perubahan, sudah benar)
@app.route('/role-dashboard')
def role_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    role = session['user']['role']
    
    dashboard_map = {
        'admin': 'admin_dashboard',
        'mechanic': 'mechanic_dashboard',
        'quality1': 'quality1_dashboard',
        'quality2': 'quality2_dashboard',
        'superadmin': 'superadmin_dashboard'
    }
    
    if role in dashboard_map:
        return redirect(url_for(dashboard_map[role]))
    else:
        flash('Role tidak dikenali!', 'error')
        return redirect(url_for('logout'))
    

# MWS
@app.route('/create_mws')
def create_mws():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Hanya Admin yang dapat membuat MWS baru!', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('admin/create_mws.html', user=session['user'])

# --- Rute untuk Membuat MWS ---
@app.route('/create_mws', methods=['POST'])
def create_mws_post():
    if 'user' not in session or session['user']['role'] not in ['admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Memproses data dari form yang dikirim oleh JavaScript
    req_data = request.get_json()
    
    data = load_data()
    part_count = len(data.get('parts', {})) + 1
    part_id = f"MWS-{part_count:03d}"
    
    # Mengambil jobType dari objek tittle yang bersarang
    tittle_obj = req_data.get('tittle', {})
    job_type = tittle_obj.get('jobType')
    
    # Mengambil template langkah kerja berdasarkan jobType
    steps_template = JOB_STEPS_TEMPLATES.get(job_type, [])

    # Membuat entri MWS baru dengan struktur yang benar
    new_mws = {
        'partNumber': req_data.get('partNumber'),
        'serialNumber': req_data.get('serialNumber'),
        'tittle': tittle_obj,  
        'ref': req_data.get('ref'),
        'customer': req_data.get('customer'),
        'acType': req_data.get('acType'),
        'wbsNo': req_data.get('wbsNo'),
        'worksheetNo': req_data.get('worksheetNo'),
        'iwoNo': req_data.get('iwoNo'),
        'shopArea': req_data.get('shopArea'),
        'revision': req_data.get('revision', '1'),
        'status': 'pending',
        'currentStep': 0,
        'assignedTo': '',
        'startDate': '',
        'finishDate': '',
        'targetDate': req_data.get('targetDate'),
        'preparedBy': '', 'preparedDate': '',
        'approvedBy': '', 'approvedDate': '',
        'verifiedBy': '', 'verifiedDate': '',
        'steps': steps_template
    }
    
    if 'parts' not in data:
        data['parts'] = {}
    data['parts'][part_id] = new_mws
    save_data(data)
    
    return jsonify({'success': True, 'partId': part_id})

@app.route('/delete_mws/<part_id>', methods=['DELETE'])
def delete_mws(part_id):
    # Keamanan: Pastikan hanya admin yang bisa menghapus
    if 'user' not in session or session['user']['role'] not in ['admin']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    data = load_data()

    if part_id in data.get('parts', {}):
        # Hapus part dari dictionary
        del data['parts'][part_id]
        save_data(data)
        return jsonify({'success': True, 'message': 'MWS berhasil dihapus.'})
    else:
        return jsonify({'success': False, 'error': 'MWS tidak ditemukan.'}), 404

@app.route('/mws/<part_id>')
def mws_detail(part_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    data = load_data() # Tetap pakai ini untuk data MWS dari JSON
    
   # Ambil data pengguna dari database
    users = get_users_from_db() 
    
    part = data.get('parts', {}).get(part_id)
    if not part:
        flash('MWS tidak ditemukan!', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('mws/mws_detail.html', user=user, part=part, part_id=part_id, users=users)

@app.route('/update_step_field', methods=['POST'])
def update_step_field():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    user = session['user']
    req_data = request.json
    part_id = req_data.get('partId')
    step_no = req_data.get('stepNo')
    field = req_data.get('field')
    value = req_data.get('value')
    
    data = load_data()
    
    if part_id not in data['parts']:
        return jsonify({'success': False, 'error': 'Part not found'}), 404
    
    part = data['parts'][part_id]
    step = next((s for s in part['steps'] if s['no'] == step_no), None)
    
    if not step:
        return jsonify({'success': False, 'error': 'Step not found'}), 404
    
    # Check permissions
    # Mekanik yang ditugaskan boleh mengedit
    if field in ['man', 'hours', 'tech']:
        if user['role'] != 'mechanic' or part.get('assignedTo') != user['nik']:
            return jsonify({'success': False, 'error': 'Hanya mekanik yang ditugaskan yang dapat mengubah MAN, Hours, dan TECH'}), 403
    
    if field == 'insp' and user['role'] != 'quality1':
        return jsonify({'success': False, 'error': 'Hanya Quality Inspector yang dapat mengubah INSP'}), 403
    
    step[field] = value
    save_data(data)
    return jsonify({'success': True})


@app.route('/update_step_status', methods=['POST'])
def update_step_status():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    user = session['user']
    req_data = request.get_json()
    part_id = req_data.get('partId')
    step_no = req_data.get('stepNo')
    new_status = req_data.get('status')
    
    data = load_data()
    
    if part_id not in data.get('parts', {}):
        return jsonify({'success': False, 'error': 'Part tidak ditemukan'}), 404
    
    part = data['parts'][part_id]
    step = next((s for s in part['steps'] if s['no'] == step_no), None)
    
    if not step:
        return jsonify({'success': False, 'error': 'Langkah kerja tidak ditemukan'}), 404
    
    # [PERBAIKAN LOGIKA] Validasi kini dilakukan saat mekanik mengirim ke inspector (status -> in_progress)
    # Ini adalah lapisan keamanan kedua setelah validasi di frontend.
    if user['role'] == 'mechanic' and new_status == 'in_progress':
        # Periksa apakah field yang wajib diisi oleh mekanik sudah terisi
        if not step.get('man') or not step.get('hours') or not step.get('tech'):
            return jsonify({'success': False, 'error': 'Server validation: Harap isi MAN, Hours, dan TECH sebelum mengirim ke inspector.'}), 400

    # Update status
    step['status'] = new_status
    
    if new_status == 'completed':
        step['completedBy'] = user['nik']
        step['completedDate'] = datetime.now().strftime('%Y-%m-%d')
        
        # Cek apakah semua langkah sudah selesai untuk mengubah status MWS
        all_steps_completed = all(s['status'] == 'completed' for s in part['steps'])
        if all_steps_completed:
            part['status'] = 'completed'
    
    elif new_status == 'in_progress':
        # Update status MWS keseluruhan jika ini adalah langkah pertama yang dimulai
        if part['status'] == 'pending':
            part['status'] = 'in_progress'
        # Update langkah kerja saat ini
        if step_no > part.get('currentStep', 0):
            part['currentStep'] = step_no
    
    save_data(data)
    return jsonify({'success': True})




# 2. Tambahkan rute API baru ini di mana saja di dalam app.py
@app.route('/update_step_details', methods=['POST'])
def update_step_details():
    # Keamanan: Pastikan hanya admin yang bisa melakukan aksi ini
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    req_data = request.get_json()
    part_id = req_data.get('partId')
    step_no = req_data.get('stepNo')
    new_details = req_data.get('details') # Ini adalah sebuah array dari frontend

    if not all([part_id, step_no is not None, isinstance(new_details, list)]):
        return jsonify({'success': False, 'error': 'Data tidak lengkap atau format salah'}), 400

    data = load_data()
    
    if part_id not in data.get('parts', {}):
        return jsonify({'success': False, 'error': 'Part tidak ditemukan'}), 404
    
    part = data['parts'][part_id]
    
    # Cari langkah kerja (step) yang sesuai berdasarkan nomornya
    step_found = False
    for step in part.get('steps', []):
        if step.get('no') == step_no:
            # Ganti seluruh array 'details' dengan yang baru dari frontend
            step['details'] = new_details
            step_found = True
            break
            
    if not step_found:
        return jsonify({'success': False, 'error': 'Langkah kerja tidak ditemukan'}), 404

    save_data(data)
    
    return jsonify({'success': True, 'message': 'Catatan berhasil diperbarui.'})


@app.route('/assign_part', methods=['POST'])
def assign_part():
    if 'user' not in session or session['user']['role'] not in ['admin', 'superadmin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    part_id = request.json.get('partId')
    assigned_to = request.json.get('assignedTo')
    
    data = load_data()
    
    if part_id not in data['parts']:
        return jsonify({'error': 'Part not found'}), 404
    
    data['parts'][part_id]['assignedTo'] = assigned_to
    if not data['parts'][part_id]['startDate']:
        data['parts'][part_id]['startDate'] = datetime.now().strftime('%Y-%m-%d')
    
    save_data(data)
    return jsonify({'success': True})

@app.route('/update_dates', methods=['POST'])
def update_dates():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = session['user']
    part_id = request.json.get('partId')
    field = request.json.get('field')
    value = request.json.get('value')
    
    # Only mechanic can update start and finish dates
    if user['role'] != 'mechanic':
        return jsonify({'error': 'Only mechanic can update dates'}), 403
    
    data = load_data()
    
    if part_id not in data['parts']:
        return jsonify({'error': 'Part not found'}), 404
    
    data['parts'][part_id][field] = value
    save_data(data)
    
    return jsonify({'success': True})

@app.route('/sign_document', methods=['POST'])
def sign_document():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = session['user']
    part_id = request.json.get('partId')
    sign_type = request.json.get('type')
    
    data = load_data()
    
    if part_id not in data['parts']:
        return jsonify({'error': 'Part not found'}), 404
    
    part = data['parts'][part_id]
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Check permissions and sign
    if sign_type == 'prepared' and user['role'] == 'admin':
        part['preparedBy'] = user['nik']
        part['preparedDate'] = current_date
    elif sign_type == 'approved' and user['role'] == 'superadmin':
        part['approvedBy'] = user['nik']
        part['approvedDate'] = current_date
    elif sign_type == 'verified' and user['role'] == 'quality2':
        part['verifiedBy'] = user['nik']
        part['verifiedDate'] = current_date
    else:
        return jsonify({'error': 'Unauthorized for this signature type'}), 403
    
    save_data(data)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)