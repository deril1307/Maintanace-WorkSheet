# File: models/user.py

from . import db  # Impor 'db' dari file __init__.py di folder yang sama
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nik = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum('admin', 'superadmin', 'mechanic', 'quality1', 'quality2'), nullable=False)
    position = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)