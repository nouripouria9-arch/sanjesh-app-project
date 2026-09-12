"""
Repository layer — all database access is centralized here.
UI and services never execute raw SQL directly.
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime
from typing import Any

from sqlalchemy import func, or_, select

from app.database.engine import get_session
from app.models.entities import ActivityLog, Candidate, ExamYear, Score

logger = logging.getLogger(__name__)


class CandidateRepository:
    """CRUD + query operations for candidates."""

    # ── Create ───────────────────────────────────────────────

    @staticmethod
    def create(
        national_id: str,
        name: str,
        age: int,
        gender: str,
        field: str,
        previous_exam: str,
        exam_year: int | None = None,
    ) -> Candidate:
        with get_session() as session:
            existing = session.execute(
                select(Candidate).where(Candidate.national_id == national_id)
            ).scalar_one_or_none()
            if existing:
                raise ValueError(f"کد ملی {national_id} قبلاً ثبت شده است.")

            tracking_code = CandidateRepository._new_tracking_code(session)
            candidate = Candidate(
                national_id=national_id,
                name=name,
                age=age,
                gender=gender,
                field=field,
                previous_exam=previous_exam,
                exam_year=exam_year or datetime.now().year,
                tracking_code=tracking_code,
                register_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            session.add(candidate)
            session.flush()
            session.add(ActivityLog(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                action="ثبت داوطلب",
                detail=f"{name} — {national_id}",
            ))
            logger.info("Candidate created: %s (%s)", name, national_id)
            return candidate

    @staticmethod
    def _new_tracking_code(session) -> str:
        """Return a unique six-digit tracking code within the current transaction."""
        for _ in range(100):
            candidate_code = f"{secrets.randbelow(900000) + 100000}"
            exists = session.execute(
                select(Candidate.id).where(Candidate.tracking_code == candidate_code)
            ).scalar_one_or_none()
            if exists is None:
                return candidate_code
        raise RuntimeError("امکان تولید کد پیگیری یکتا وجود ندارد.")

    # ── Read ─────────────────────────────────────────────────

    @staticmethod
    def get_by_id(candidate_id: int) -> Candidate | None:
        with get_session() as session:
            return session.get(Candidate, candidate_id)

    @staticmethod
    def get_by_national_id(national_id: str) -> Candidate | None:
        with get_session() as session:
            return session.execute(
                select(Candidate).where(Candidate.national_id == national_id)
            ).scalar_one_or_none()

    @staticmethod
    def get_by_tracking_code(tracking_code: str) -> Candidate | None:
        with get_session() as session:
            return session.execute(
                select(Candidate).where(Candidate.tracking_code == tracking_code)
            ).scalar_one_or_none()

    @staticmethod
    def get_all() -> list[Candidate]:
        with get_session() as session:
            return list(session.execute(select(Candidate)).scalars().all())

    @staticmethod
    def search(
        query: str = "",
        field: str | None = None,
        gender: str | None = None,
        exam_year: int | None = None,
        limit: int = 500,
    ) -> list[Candidate]:
        """Search with optional filters. Returns up to `limit` rows."""
        with get_session() as session:
            stmt = select(Candidate)
            if query:
                like = f"%{query}%"
                stmt = stmt.where(or_(
                    Candidate.name.like(like),
                    Candidate.national_id.like(like),
                    Candidate.tracking_code.like(like),
                ))
            if field:
                stmt = stmt.where(Candidate.field == field)
            if gender:
                stmt = stmt.where(Candidate.gender == gender)
            if exam_year:
                stmt = stmt.where(Candidate.exam_year == exam_year)
            stmt = stmt.order_by(Candidate.id.desc()).limit(limit)
            return list(session.execute(stmt).scalars().all())

    @staticmethod
    def count() -> int:
        with get_session() as session:
            return session.execute(select(func.count(Candidate.id))).scalar_one()

    @staticmethod
    def count_by_field() -> dict[str, int]:
        with get_session() as session:
            rows = session.execute(
                select(Candidate.field, func.count(Candidate.id))
                .group_by(Candidate.field)
            ).all()
            return {field: count for field, count in rows}

    @staticmethod
    def count_by_gender() -> dict[str, int]:
        with get_session() as session:
            rows = session.execute(
                select(Candidate.gender, func.count(Candidate.id))
                .group_by(Candidate.gender)
            ).all()
            return {gender: count for gender, count in rows}

    @staticmethod
    def count_by_year() -> dict[int, int]:
        with get_session() as session:
            rows = session.execute(
                select(Candidate.exam_year, func.count(Candidate.id))
                .group_by(Candidate.exam_year)
            ).all()
            return {year: count for year, count in rows}

    @staticmethod
    def count_previous_exam() -> dict[str, int]:
        with get_session() as session:
            rows = session.execute(
                select(Candidate.previous_exam, func.count(Candidate.id))
                .group_by(Candidate.previous_exam)
            ).all()
            return {prev: count for prev, count in rows}

    @staticmethod
    def distinct_years() -> list[int]:
        with get_session() as session:
            rows = session.execute(
                select(Candidate.exam_year).distinct().order_by(Candidate.exam_year)
            ).scalars().all()
            return list(rows)

    # ── Update ───────────────────────────────────────────────

    @staticmethod
    def update(candidate_id: int, **fields: Any) -> Candidate | None:
        with get_session() as session:
            candidate = session.get(Candidate, candidate_id)
            if candidate is None:
                return None
            national_id = fields.get("national_id")
            if national_id and national_id != candidate.national_id:
                duplicate = session.execute(
                    select(Candidate.id).where(
                        Candidate.national_id == national_id,
                        Candidate.id != candidate_id,
                    )
                ).scalar_one_or_none()
                if duplicate is not None:
                    raise ValueError(f"کد ملی {national_id} قبلاً ثبت شده است.")
            for key, value in fields.items():
                if hasattr(candidate, key) and value is not None:
                    setattr(candidate, key, value)
            session.add(ActivityLog(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                action="ویرایش داوطلب",
                detail=f"{candidate.name} — {candidate.national_id}",
            ))
            logger.info("Candidate %s updated", candidate_id)
            return candidate

    # ── Delete ───────────────────────────────────────────────

    @staticmethod
    def delete(candidate_id: int) -> bool:
        with get_session() as session:
            candidate = session.get(Candidate, candidate_id)
            if candidate is None:
                return False
            session.delete(candidate)
            session.add(ActivityLog(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                action="حذف داوطلب",
                detail=f"{candidate.name} — {candidate.national_id}",
            ))
            logger.info("Candidate %s deleted", candidate_id)
            return True


class ScoreRepository:
    """CRUD for candidate scores."""

    @staticmethod
    def set_scores(candidate_id: int, scores: dict[str, float]) -> None:
        """Upsert scores for a candidate (replaces existing)."""
        with get_session() as session:
            candidate = session.get(Candidate, candidate_id)
            if candidate is None:
                raise ValueError("داوطلب یافت نشد.")
            # Remove existing scores
            for score in list(candidate.scores):
                session.delete(score)
            session.flush()
            for subject, percent in scores.items():
                session.add(Score(
                    candidate_id=candidate_id,
                    subject=subject,
                    percent=float(percent),
                ))
            session.add(ActivityLog(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                action="ثبت نمرات",
                detail=f"{candidate.name} — {len(scores)} درس",
            ))
            logger.info("Scores saved for candidate %s", candidate_id)

    @staticmethod
    def get_scores(candidate_id: int) -> dict[str, float]:
        with get_session() as session:
            rows = session.execute(
                select(Score).where(Score.candidate_id == candidate_id)
            ).scalars().all()
            return {s.subject: s.percent for s in rows}

    @staticmethod
    def get_all() -> list[Score]:
        with get_session() as session:
            return list(session.execute(select(Score)).scalars().all())

    @staticmethod
    def count() -> int:
        with get_session() as session:
            return session.execute(select(func.count(Score.id))).scalar_one()

    @staticmethod
    def count_candidates_with_scores() -> int:
        with get_session() as session:
            return session.execute(
                select(func.count(func.distinct(Score.candidate_id)))
            ).scalar_one()

    @staticmethod
    def average_by_subject() -> dict[str, float]:
        with get_session() as session:
            rows = session.execute(
                select(Score.subject, func.avg(Score.percent))
                .group_by(Score.subject)
            ).all()
            return {subject: round(avg, 2) for subject, avg in rows}

    @staticmethod
    def average_by_subject_year(year: int) -> dict[str, float]:
        with get_session() as session:
            rows = session.execute(
                select(Score.subject, func.avg(Score.percent))
                .join(Candidate, Score.candidate_id == Candidate.id)
                .where(Candidate.exam_year == year)
                .group_by(Score.subject)
            ).all()
            return {subject: round(avg, 2) for subject, avg in rows}


class ExamYearRepository:
    """Metadata for exam years."""

    @staticmethod
    def get_or_create(year: int) -> ExamYear:
        with get_session() as session:
            exam_year = session.execute(
                select(ExamYear).where(ExamYear.year == year)
            ).scalar_one_or_none()
            if exam_year is None:
                exam_year = ExamYear(year=year)
                session.add(exam_year)
                session.flush()
            return exam_year

    @staticmethod
    def get_all() -> list[ExamYear]:
        with get_session() as session:
            return list(session.execute(select(ExamYear).order_by(ExamYear.year)).scalars().all())

    @staticmethod
    def years() -> list[int]:
        with get_session() as session:
            return list(session.execute(
                select(ExamYear.year).order_by(ExamYear.year)
            ).scalars().all())


class ActivityLogRepository:
    """Recent activity feed."""

    @staticmethod
    def recent(limit: int = 20) -> list[ActivityLog]:
        with get_session() as session:
            return list(session.execute(
                select(ActivityLog).order_by(ActivityLog.id.desc()).limit(limit)
            ).scalars().all())

    @staticmethod
    def log(action: str, detail: str | None = None) -> None:
        with get_session() as session:
            session.add(ActivityLog(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                action=action,
                detail=detail,
            ))
