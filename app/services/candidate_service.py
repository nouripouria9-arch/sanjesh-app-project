"""
Business-logic services for candidate management.
Thin layer between UI and repository.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Any

from app.models.entities import Candidate
from app.repositories.repositories import (
    ActivityLogRepository,
    CandidateRepository,
    ScoreRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class RegistrationResult:
    success: bool
    message: str
    candidate: Candidate | None = None


class CandidateService:
    """All candidate-related business operations."""

    @staticmethod
    def register(
        national_id: str,
        name: str,
        age: int,
        gender: str,
        field: str,
        previous_exam: str,
        exam_year: int | None = None,
    ) -> RegistrationResult:
        # Validation
        national_id = national_id.strip()
        name = name.strip()
        if not national_id:
            return RegistrationResult(False, "کد ملی نمی‌تواند خالی باشد.")
        if len(national_id) != 10 or not national_id.isdigit():
            return RegistrationResult(False, "کد ملی باید دقیقاً ۱۰ رقم باشد.")
        if not name:
            return RegistrationResult(False, "نام نمی‌تواند خالی باشد.")
        if age < 14 or age > 100:
            return RegistrationResult(False, "سن باید بین ۱۴ تا ۱۰۰ باشد.")
        if not gender:
            return RegistrationResult(False, "جنسیت انتخاب نشده است.")
        if not field:
            return RegistrationResult(False, "رشته انتخاب نشده است.")
        if not previous_exam:
            return RegistrationResult(False, "وضعیت شرکت مجدد مشخص نشده است.")
        try:
            candidate = CandidateRepository.create(
                national_id=national_id,
                name=name,
                age=age,
                gender=gender,
                field=field,
                previous_exam=previous_exam,
                exam_year=exam_year,
            )
            return RegistrationResult(True, "ثبت نام با موفقیت انجام شد.", candidate)
        except ValueError as exc:
            return RegistrationResult(False, str(exc))
        except Exception as exc:
            logger.exception("Registration failed")
            return RegistrationResult(False, f"خطا در ثبت نام: {exc}")

    @staticmethod
    def get(candidate_id: int) -> Candidate | None:
        return CandidateRepository.get_by_id(candidate_id)

    @staticmethod
    def get_all() -> list[Candidate]:
        return CandidateRepository.get_all()

    @staticmethod
    def search(
        query: str = "",
        field: str | None = None,
        gender: str | None = None,
        exam_year: int | None = None,
        limit: int = 500,
    ) -> list[Candidate]:
        return CandidateRepository.search(query, field, gender, exam_year, limit)

    @staticmethod
    def update(candidate_id: int, **kwargs: Any) -> bool:
        try:
            result = CandidateRepository.update(candidate_id, **kwargs)
            return result is not None
        except Exception:
            logger.exception("Candidate update failed: %s", candidate_id)
            return False

    @staticmethod
    def delete(candidate_id: int) -> bool:
        return CandidateRepository.delete(candidate_id)

    @staticmethod
    def import_bulk(data: list[dict]) -> tuple[int, int, list[str]]:
        """Import candidates from a list of dicts. Returns (imported, skipped, errors)."""
        imported = 0
        skipped = 0
        errors: list[str] = []
        for i, row in enumerate(data):
            try:
                result = CandidateService.register(
                    national_id=str(row.get("national_id", "")),
                    name=str(row.get("name", "")),
                    age=int(row.get("age", 0)),
                    gender=str(row.get("gender", "")),
                    field=str(row.get("field", "")),
                    previous_exam=str(row.get("previous_exam", "خیر")),
                    exam_year=int(row.get("exam_year", 0)) or None,
                )
                if result.success:
                    imported += 1
                else:
                    skipped += 1
                    errors.append(f"سطر {i + 2}: {result.message}")
            except Exception as exc:
                skipped += 1
                errors.append(f"سطر {i + 2}: {exc}")
        return imported, skipped, errors


class ScoreService:
    """Score management operations."""

    @staticmethod
    def set_scores(candidate_id: int, scores: dict[str, float]) -> bool:
        try:
            ScoreRepository.set_scores(candidate_id, scores)
            return True
        except Exception as exc:
            logger.exception("Score save failed")
            return False

    @staticmethod
    def get_scores(candidate_id: int) -> dict[str, float]:
        return ScoreRepository.get_scores(candidate_id)

    @staticmethod
    def count() -> int:
        return ScoreRepository.count()

    @staticmethod
    def count_candidates_with_scores() -> int:
        return ScoreRepository.count_candidates_with_scores()
