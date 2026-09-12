"""
SQLAlchemy ORM models for the Sanjesh (Konkur) system.

Schema derived from the original project's requirements:
- candidates (applicants) with registration info
- scores per subject per candidate
- exam_years for year-based analytics
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.engine import Base


class Candidate(Base):
    """A Konkur candidate / applicant."""

    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    national_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    field: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_exam: Mapped[str] = mapped_column(String(5), nullable=False, default="خیر")
    exam_year: Mapped[int] = mapped_column(Integer, nullable=False, default=datetime.now().year)
    tracking_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    register_time: Mapped[str] = mapped_column(String(50), nullable=False)

    scores: Mapped[list["Score"]] = relationship(
        back_populates="candidate",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("age > 0 AND age < 120", name="ck_candidates_age"),
        CheckConstraint("gender IN ('مرد', 'زن')", name="ck_candidates_gender"),
        CheckConstraint("field IN ('تجربی', 'ریاضی')", name="ck_candidates_field"),
        CheckConstraint("previous_exam IN ('بله', 'خیر')", name="ck_candidates_prev_exam"),
        Index("ix_candidates_field", "field"),
        Index("ix_candidates_exam_year", "exam_year"),
        Index("ix_candidates_gender", "gender"),
    )

    def __repr__(self) -> str:
        return f"<Candidate {self.name} ({self.national_id})>"


class Score(Base):
    """A candidate's percentage score in one subject."""

    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    percent: Mapped[float] = mapped_column(Float, nullable=False)

    candidate: Mapped[Candidate] = relationship(back_populates="scores")

    __table_args__ = (
        CheckConstraint("percent >= 0 AND percent <= 100", name="ck_scores_percent"),
        UniqueConstraint("candidate_id", "subject", name="uq_candidate_subject"),
        Index("ix_scores_subject", "subject"),
    )

    def __repr__(self) -> str:
        return f"<Score {self.subject}: {self.percent}>"


class ExamYear(Base):
    """Metadata about a Konkur exam year."""

    __tablename__ = "exam_years"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1_200_000)
    tajrobi_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=700_000)
    riazi_capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=500_000)
    note: Mapped[str] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<ExamYear {self.year}>"


class ActivityLog(Base):
    """Audit trail of significant application actions."""

    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    detail: Mapped[str] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<ActivityLog {self.action} @ {self.timestamp}>"
