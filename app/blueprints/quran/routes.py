from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime

from app.blueprints.quran import quran_bp
from app.extensions import db
from app.models.quran import QuranProgress, QuranSession
from app.models.student import Student
from app.models.teacher import Teacher

# 114 Surahs of the Quran
SURAHS = [
    (1, 'Al-Fatihah'), (2, 'Al-Baqarah'), (3, "Ali 'Imran"), (4, 'An-Nisa'),
    (5, "Al-Ma'idah"), (6, "Al-An'am"), (7, "Al-A'raf"), (8, 'Al-Anfal'),
    (9, 'At-Tawbah'), (10, 'Yunus'), (11, 'Hud'), (12, 'Yusuf'),
    (13, 'Ar-Ra\'d'), (14, 'Ibrahim'), (15, 'Al-Hijr'), (16, 'An-Nahl'),
    (17, 'Al-Isra'), (18, 'Al-Kahf'), (19, 'Maryam'), (20, 'Ta-Ha'),
    (21, 'Al-Anbiya'), (22, 'Al-Hajj'), (23, 'Al-Mu\'minun'), (24, 'An-Nur'),
    (25, 'Al-Furqan'), (26, 'Ash-Shu\'ara'), (27, 'An-Naml'), (28, 'Al-Qasas'),
    (29, 'Al-\'Ankabut'), (30, 'Ar-Rum'), (31, 'Luqman'), (32, 'As-Sajdah'),
    (33, 'Al-Ahzab'), (34, 'Saba'), (35, 'Fatir'), (36, 'Ya-Sin'),
    (37, 'As-Saffat'), (38, 'Sad'), (39, 'Az-Zumar'), (40, 'Ghafir'),
    (41, 'Fussilat'), (42, 'Ash-Shura'), (43, 'Az-Zukhruf'), (44, 'Ad-Dukhan'),
    (45, 'Al-Jathiyah'), (46, 'Al-Ahqaf'), (47, 'Muhammad'), (48, 'Al-Fath'),
    (49, 'Al-Hujurat'), (50, 'Qaf'), (51, 'Adh-Dhariyat'), (52, 'At-Tur'),
    (53, 'An-Najm'), (54, 'Al-Qamar'), (55, 'Ar-Rahman'), (56, 'Al-Waqi\'ah'),
    (57, 'Al-Hadid'), (58, 'Al-Mujadila'), (59, 'Al-Hashr'), (60, 'Al-Mumtahanah'),
    (61, 'As-Saf'), (62, 'Al-Jumu\'ah'), (63, 'Al-Munafiqun'), (64, 'At-Taghabun'),
    (65, 'At-Talaq'), (66, 'At-Tahrim'), (67, 'Al-Mulk'), (68, 'Al-Qalam'),
    (69, 'Al-Haqqah'), (70, 'Al-Ma\'arij'), (71, 'Nuh'), (72, 'Al-Jinn'),
    (73, 'Al-Muzzammil'), (74, 'Al-Muddaththir'), (75, 'Al-Qiyamah'), (76, 'Al-Insan'),
    (77, 'Al-Mursalat'), (78, "An-Naba'"), (79, 'An-Nazi\'at'), (80, "'Abasa"),
    (81, 'At-Takwir'), (82, 'Al-Infitar'), (83, 'Al-Mutaffifin'), (84, 'Al-Inshiqaq'),
    (85, 'Al-Buruj'), (86, 'At-Tariq'), (87, 'Al-A\'la'), (88, 'Al-Ghashiyah'),
    (89, 'Al-Fajr'), (90, 'Al-Balad'), (91, 'Ash-Shams'), (92, 'Al-Layl'),
    (93, 'Ad-Duha'), (94, 'Ash-Sharh'), (95, 'At-Tin'), (96, 'Al-\'Alaq'),
    (97, 'Al-Qadr'), (98, 'Al-Bayyinah'), (99, 'Az-Zalzalah'), (100, 'Al-\'Adiyat'),
    (101, "Al-Qari'ah"), (102, 'At-Takathur'), (103, 'Al-\'Asr'), (104, 'Al-Humazah'),
    (105, 'Al-Fil'), (106, 'Quraysh'), (107, 'Al-Ma\'un'), (108, 'Al-Kawthar'),
    (109, 'Al-Kafirun'), (110, 'An-Nasr'), (111, 'Al-Masad'), (112, 'Al-Ikhlas'),
    (113, 'Al-Falaq'), (114, 'An-Nas'),
]

def _teacher_of_current_user():
    """Return the Teacher record linked to the currently logged-in user, or None."""
    if hasattr(current_user, 'teacher_profile') and current_user.teacher_profile:
        return current_user.teacher_profile
    return None


# ─────────────────────────────────────────────────────────────
# INDEX – overview dashboard
# ─────────────────────────────────────────────────────────────
@quran_bp.route('/')
@login_required
def index():
    # If Student, redirect to their own progress
    if current_user.role == 'U' and hasattr(current_user, 'student_profile') and current_user.student_profile:
        progress = QuranProgress.query.filter_by(student_id=current_user.student_profile.id).first()
        if progress:
            return redirect(url_for('quran.student_progress', progress_id=progress.id))
        else:
            flash(_('Your Quran progress record is not yet initialized. Please contact your teacher.'), 'info')
            return redirect(url_for('auth.dashboard'))

    # If Parent, we might show their children or first child
    if current_user.role == 'P':
        children = Student.query.filter_by(parent_id=current_user.id).all()
        if len(children) == 1:
            progress = QuranProgress.query.filter_by(student_id=children[0].id).first()
            if progress:
                return redirect(url_for('quran.student_progress', progress_id=progress.id))
        return redirect(url_for('auth.my_children'))

    query = QuranProgress.query

    # Teachers see only their own students
    teacher = _teacher_of_current_user()
    if current_user.role == 'T' and teacher:
        query = query.filter_by(teacher_id=teacher.id)

    mode_filter = request.args.get('mode', '')
    if mode_filter:
        query = query.filter_by(mode=mode_filter)

    search = request.args.get('search', '').strip()
    if search:
        query = query.join(Student).filter(Student.full_name.ilike(f'%{search}%'))

    records = query.join(Student).order_by(Student.full_name).all()

    # Stats
    total = QuranProgress.query.count()
    hifz_count = QuranProgress.query.filter_by(mode='Hifz').count()
    nazira_count = QuranProgress.query.filter_by(mode='Nazira').count()
    muraja_count = QuranProgress.query.filter_by(mode="Muraja'a").count()

    return render_template(
        'quran/index.html',
        records=records,
        total=total,
        hifz_count=hifz_count,
        nazira_count=nazira_count,
        muraja_count=muraja_count,
        mode_filter=mode_filter,
        search=search,
        SURAHS=SURAHS,
    )


# ─────────────────────────────────────────────────────────────
# ADD / EDIT PROGRESS
# ─────────────────────────────────────────────────────────────
@quran_bp.route('/progress/add', methods=['GET', 'POST'])
@login_required
def add_progress():
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        # Check for duplicate
        existing = QuranProgress.query.filter_by(student_id=student_id).first()
        if existing:
            flash('This student already has a Quran progress record. Please edit it instead.', 'warning')
            return redirect(url_for('quran.index'))

        teacher = _teacher_of_current_user()
        teacher_id = teacher.id if teacher else request.form.get('teacher_id', type=int)

        progress = QuranProgress(
            student_id=student_id,
            teacher_id=teacher_id,
            current_juz=request.form.get('current_juz', 1, type=int),
            current_surah=request.form.get('current_surah', 'Al-Fatihah'),
            current_surah_number=request.form.get('current_surah_number', 1, type=int),
            current_aya=request.form.get('current_aya', 1, type=int),
            mode=request.form.get('mode', 'Nazira'),
            total_pages_memorized=request.form.get('total_pages_memorized', 0, type=int),
            total_juz_completed=request.form.get('total_juz_completed', 0, type=int),
            notes=request.form.get('notes', ''),
        )
        db.session.add(progress)
        db.session.commit()
        flash('Quran progress record created successfully!', 'success')
        return redirect(url_for('quran.student_progress', progress_id=progress.id))

    students = Student.query.filter_by(status='Active').order_by(Student.full_name).all()
    teachers = Teacher.query.filter_by(status='Active').order_by(Teacher.full_name).all()
    return render_template('quran/add_progress.html', students=students, teachers=teachers, SURAHS=SURAHS)


@quran_bp.route('/progress/<int:progress_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_progress(progress_id):
    progress = QuranProgress.query.get_or_404(progress_id)
    if request.method == 'POST':
        progress.current_juz = request.form.get('current_juz', 1, type=int)
        progress.current_surah = request.form.get('current_surah', 'Al-Fatihah')
        progress.current_surah_number = request.form.get('current_surah_number', 1, type=int)
        progress.current_aya = request.form.get('current_aya', 1, type=int)
        progress.mode = request.form.get('mode', 'Nazira')
        progress.total_pages_memorized = request.form.get('total_pages_memorized', 0, type=int)
        progress.total_juz_completed = request.form.get('total_juz_completed', 0, type=int)
        progress.notes = request.form.get('notes', '')
        teacher_id = request.form.get('teacher_id', type=int)
        if teacher_id:
            progress.teacher_id = teacher_id
        progress.last_updated = datetime.utcnow()
        db.session.commit()
        flash('Progress updated successfully!', 'success')
        return redirect(url_for('quran.student_progress', progress_id=progress.id))

    students = Student.query.filter_by(status='Active').order_by(Student.full_name).all()
    teachers = Teacher.query.filter_by(status='Active').order_by(Teacher.full_name).all()
    return render_template('quran/edit_progress.html', progress=progress, students=students, teachers=teachers, SURAHS=SURAHS)


# ─────────────────────────────────────────────────────────────
# STUDENT DETAIL – progress + sessions
# ─────────────────────────────────────────────────────────────
@quran_bp.route('/progress/<int:progress_id>')
@login_required
def student_progress(progress_id):
    progress = QuranProgress.query.get_or_404(progress_id)
    sessions = progress.sessions.order_by(QuranSession.session_date.desc()).all()
    teachers = Teacher.query.filter_by(status='Active').order_by(Teacher.full_name).all()

    # Juz completion percentage
    juz_pct = int((progress.total_juz_completed / 30) * 100) if progress.total_juz_completed else 0
    page_pct = int((progress.total_pages_memorized / 604) * 100) if progress.total_pages_memorized else 0

    # Rating counts
    from sqlalchemy import func
    rating_stats = db.session.query(
        QuranSession.rating, func.count(QuranSession.id)
    ).filter_by(progress_id=progress_id).group_by(QuranSession.rating).all()

    return render_template(
        'quran/student_progress.html',
        progress=progress,
        sessions=sessions,
        juz_pct=juz_pct,
        page_pct=page_pct,
        rating_stats=dict(rating_stats),
        teachers=teachers,
        SURAHS=SURAHS,
        now=datetime.utcnow()
    )


# ─────────────────────────────────────────────────────────────
# ADD SESSION
# ─────────────────────────────────────────────────────────────
@quran_bp.route('/progress/<int:progress_id>/session/add', methods=['POST'])
@login_required
def add_session(progress_id):
    progress = QuranProgress.query.get_or_404(progress_id)
    teacher = _teacher_of_current_user()

    session_date_str = request.form.get('session_date')
    session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date() if session_date_str else date.today()

    qs = QuranSession(
        progress_id=progress_id,
        teacher_id=teacher.id if teacher else request.form.get('teacher_id', type=int),
        session_date=session_date,
        session_type=request.form.get('session_type', 'Nazira'),
        surah_from=request.form.get('surah_from', ''),
        aya_from=request.form.get('aya_from', 1, type=int),
        surah_to=request.form.get('surah_to', ''),
        aya_to=request.form.get('aya_to', 1, type=int),
        pages_covered=request.form.get('pages_covered', 0, type=int),
        rating=request.form.get('rating', 'Good'),
        mistakes_count=request.form.get('mistakes_count', 0, type=int),
        teacher_notes=request.form.get('teacher_notes', ''),
    )
    db.session.add(qs)

    # Auto-update progress position
    if request.form.get('update_position') == '1':
        progress.current_surah = request.form.get('surah_to', progress.current_surah)
        progress.current_surah_number = request.form.get('surah_to_number', progress.current_surah_number, type=int)
        progress.current_aya = request.form.get('aya_to', progress.current_aya, type=int)
        # Update pages
        pages = request.form.get('pages_covered', 0, type=int)
        progress.total_pages_memorized = min(604, (progress.total_pages_memorized or 0) + pages)
        progress.last_updated = datetime.utcnow()

    db.session.commit()
    flash('Session recorded successfully!', 'success')
    return redirect(url_for('quran.student_progress', progress_id=progress_id))


# ─────────────────────────────────────────────────────────────
# DELETE SESSION
# ─────────────────────────────────────────────────────────────
@quran_bp.route('/session/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_session(session_id):
    qs = QuranSession.query.get_or_404(session_id)
    progress_id = qs.progress_id
    db.session.delete(qs)
    db.session.commit()
    flash('Session deleted.', 'success')
    return redirect(url_for('quran.student_progress', progress_id=progress_id))


# ─────────────────────────────────────────────────────────────
# DELETE PROGRESS RECORD
# ─────────────────────────────────────────────────────────────
@quran_bp.route('/progress/<int:progress_id>/delete', methods=['POST'])
@login_required
def delete_progress(progress_id):
    progress = QuranProgress.query.get_or_404(progress_id)
    db.session.delete(progress)
    db.session.commit()
    flash('Quran progress record deleted.', 'warning')
    return redirect(url_for('quran.index'))
