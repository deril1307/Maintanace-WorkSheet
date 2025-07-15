from app import app          # Impor aplikasi Flask utama Anda dari app.py
from models import db, User  # Impor objek db dan Model User dari models.py

# Data pengguna awal yang akan dimasukkan ke database
initial_users_data = [
    {'nik': '001', 'name': 'Ahmad Wijaya', 'password': '123', 'role': 'admin', 'position': 'Admin (A)', 'description': 'Pengguna A - Membuat MWS dan Prepared By'},
    {'nik': '002', 'name': 'Budi Santoso', 'password': '123', 'role': 'mechanic', 'position': 'Mekanik (U1)', 'description': 'User 1 - Mengisi MAN, Hours, TECH dan Start/Finish Date'},
    {'nik': '003', 'name': 'Sari Indah', 'password': '123', 'role': 'quality1', 'position': 'Quality Inspector (U2)', 'description': 'User 2 - Inspeksi setiap langkah kerja'},
    {'nik': '004', 'name': 'Dewi Lestari', 'password': '123', 'role': 'quality2', 'position': 'Quality CUDR (U3)', 'description': 'User 3 - Verified By'},
    {'nik': '005', 'name': 'Eko Prasetyo', 'password': '123', 'role': 'superadmin', 'position': 'Super Admin (S.A)', 'description': 'Super Admin - Approved By'},
]

def seed_users():
    """
    Fungsi untuk mengisi (seeding) data awal ke tabel 'users'.
    Ini hanya perlu dijalankan sekali.
    """
    # `with app.app_context()` diperlukan agar SQLAlchemy tahu 
    # database mana yang harus digunakan berdasarkan konfigurasi di app.py.
    with app.app_context():
        # 1. Kosongkan tabel users terlebih dahulu untuk memulai dari awal
        print("Menghapus data pengguna lama...")
        db.session.query(User).delete()
        db.session.commit()
        print("Data pengguna lama berhasil dihapus.")

        print("\nMemulai proses seeding untuk tabel 'users'...")
        
        # 2. Loop melalui setiap data pengguna
        for user_data in initial_users_data:
            # Buat objek User baru dari model
            new_user = User(
                nik=user_data['nik'],
                name=user_data['name'],
                role=user_data['role'],
                position=user_data['position'],
                description=user_data['description']
            )
            
            # 3. Gunakan metode set_password untuk hashing yang aman
            new_user.set_password(user_data['password'])
            
            # 4. Tambahkan objek user baru ke dalam sesi database
            db.session.add(new_user)
            print(f"-> Menambahkan pengguna: {user_data['name']} ({user_data['nik']})")

        # 5. Commit semua perubahan ke database
        db.session.commit()
        print("\nSeeding untuk tabel 'users' selesai.")

# Ini memastikan fungsi seed_users() hanya berjalan saat file ini dieksekusi langsung
if __name__ == "__main__":
    seed_users()