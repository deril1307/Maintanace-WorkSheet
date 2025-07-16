# models/mws_step.py

from . import db
from sqlalchemy.dialects.mysql import ENUM, JSON # type: ignore

class MwsStep(db.Model):
    __tablename__ = 'mws_steps'

    id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    details = db.Column(JSON)
    status = db.Column(ENUM('pending', 'in_progress', 'completed'), default='pending')
    man = db.Column(db.String(50))
    hours = db.Column(db.String(50))
    tech = db.Column(db.String(50))
    insp = db.Column(db.String(50))
    completed_date = db.Column(db.Date)

    # Foreign Keys
    mws_part_id = db.Column(db.Integer, db.ForeignKey('mws_parts.id'), nullable=False)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    part = db.relationship('MwsPart', back_populates='steps')
    completed_by = db.relationship('User', back_populates='completed_steps')

    def __repr__(self):
        return f'<MwsStep {self.id} for Part {self.mws_part_id}>'