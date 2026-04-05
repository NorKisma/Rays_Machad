from app.extensions import db
from datetime import datetime
from app.models.mixins import SchoolContextMixin


class QuranProgress(db.Model, SchoolContextMixin):
    """Tracks a student's current Quran memorization progress."""
    __tablename__ = 'quran_progress'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)

    # Current position
    current_juz = db.Column(db.Integer, default=1)           # 1-30
    current_surah = db.Column(db.String(100), default='Al-Fatihah')
    current_surah_number = db.Column(db.Integer, default=1)  # 1-114
    current_aya = db.Column(db.Integer, default=1)

    # Mode
    mode = db.Column(db.String(20), default='Nazira')        # Nazira, Hifz, Muraja'a
    total_pages_memorized = db.Column(db.Integer, default=0)
    total_juz_completed = db.Column(db.Integer, default=0)

    notes = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', backref=db.backref('quran_progress', uselist=False), lazy=True)
    teacher = db.relationship('Teacher', backref='quran_students', lazy=True)
    sessions = db.relationship('QuranSession', backref='progress', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<QuranProgress student_id={self.student_id} juz={self.current_juz}>'


class QuranSession(db.Model, SchoolContextMixin):
    """Records a single Quran teaching/recitation session."""
    __tablename__ = 'quran_sessions'

    id = db.Column(db.Integer, primary_key=True)
    progress_id = db.Column(db.Integer, db.ForeignKey('quran_progress.id'), nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=True)

    session_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # What was covered this session
    session_type = db.Column(db.String(20), default='Nazira')   # Nazira, Hifz, Muraja'a, Test
    surah_from = db.Column(db.String(100))
    aya_from = db.Column(db.Integer, default=1)
    surah_to = db.Column(db.String(100))
    aya_to = db.Column(db.Integer, default=1)

    pages_covered = db.Column(db.Integer, default=0)

    # Evaluation
    rating = db.Column(db.String(10), default='Good')  # Excellent, Good, Average, Poor
    mistakes_count = db.Column(db.Integer, default=0)
    teacher_notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    teacher = db.relationship('Teacher', backref='quran_sessions_taught', lazy=True)

    def __repr__(self):
        return f'<QuranSession date={self.session_date} type={self.session_type}>'
