# models/mws_part.py

from . import db
from sqlalchemy.dialects.mysql import ENUM # type: ignore

class MwsPart(db.Model):
    __tablename__ = 'mws_parts'

    # Primary Key 
    id = db.Column(db.Integer, primary_key=True)
    
    # Kolom-kolom data
    part_number = db.Column(db.String(50))
    serial_number = db.Column(db.String(50))
    ref = db.Column(db.String(255))
    customer = db.Column(db.String(255))
    ac_type = db.Column(db.String(50))
    wbs_no = db.Column(db.String(50))
    worksheet_no = db.Column(db.String(50))
    iwo_no = db.Column(db.String(50))
    shop_area = db.Column(db.String(100))
    revision = db.Column(db.String(10))
    tittle = db.Column(db.String(255), nullable=False)
    job_type = db.Column(db.String(100))
    status = db.Column(ENUM('pending', 'in_progress', 'completed'), default='pending')
    current_step = db.Column(db.Integer, default=0)
    target_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    finish_date = db.Column(db.Date)
    prepared_date = db.Column(db.Date)
    approved_date = db.Column(db.Date)
    verified_date = db.Column(db.Date)

    # Foreign Keys
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    prepared_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    steps = db.relationship('MwsStep', back_populates='part', cascade="all, delete-orphan", lazy=True)
    
    # Relasi ke User, butuh foreign_keys karena ada banyak kolom yang menunjuk ke tabel yang sama
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])
    prepared_by = db.relationship('User', foreign_keys=[prepared_by_id])
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    verified_by = db.relationship('User', foreign_keys=[verified_by_id])

    def __repr__(self):
        return f'<MwsPart {self.part_number}>'