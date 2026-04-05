"""Add Quran module tables

Revision ID: c84fb17686a1
Revises: 98eb02870a87
Create Date: 2026-03-30 08:30:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c84fb17686a1'
down_revision = '98eb02870a87'
branch_labels = None
depends_on = None


def upgrade():
    # quran_progress table
    op.create_table('quran_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=True),
        sa.Column('current_juz', sa.Integer(), nullable=True),
        sa.Column('current_surah', sa.String(length=100), nullable=True),
        sa.Column('current_surah_number', sa.Integer(), nullable=True),
        sa.Column('current_aya', sa.Integer(), nullable=True),
        sa.Column('mode', sa.String(length=20), nullable=True),
        sa.Column('total_pages_memorized', sa.Integer(), nullable=True),
        sa.Column('total_juz_completed', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('school_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quran_progress_student_id'), 'quran_progress', ['student_id'], unique=False)
    op.create_index(op.f('ix_quran_progress_school_id'), 'quran_progress', ['school_id'], unique=False)

    # quran_sessions table
    op.create_table('quran_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('progress_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=True),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('session_type', sa.String(length=20), nullable=True),
        sa.Column('surah_from', sa.String(length=100), nullable=True),
        sa.Column('aya_from', sa.Integer(), nullable=True),
        sa.Column('surah_to', sa.String(length=100), nullable=True),
        sa.Column('aya_to', sa.Integer(), nullable=True),
        sa.Column('pages_covered', sa.Integer(), nullable=True),
        sa.Column('rating', sa.String(length=10), nullable=True),
        sa.Column('mistakes_count', sa.Integer(), nullable=True),
        sa.Column('teacher_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('school_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['progress_id'], ['quran_progress.id'], ),
        sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quran_sessions_progress_id'), 'quran_sessions', ['progress_id'], unique=False)
    op.create_index(op.f('ix_quran_sessions_school_id'), 'quran_sessions', ['school_id'], unique=False)


def downgrade():
    op.drop_table('quran_sessions')
    op.drop_table('quran_progress')
