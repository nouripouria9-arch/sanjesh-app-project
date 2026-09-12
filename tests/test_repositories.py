"""
Database and repository tests.
"""

import pytest

from app.database.engine import initialize_database, shutdown_database
from app.models.entities import Candidate, Score
from app.repositories.repositories import (
    CandidateRepository,
    ExamYearRepository,
    ScoreRepository,
)


@pytest.fixture(scope="module", autouse=True)
def db():
    initialize_database()
    yield
    shutdown_database()


@pytest.fixture()
def sample_candidate():
    """Create a candidate and clean up after."""
    candidate = CandidateRepository.create(
        national_id="0012345678",
        name="علی محمدی",
        age=19,
        gender="مرد",
        field="تجربی",
        previous_exam="خیر",
        exam_year=2025,
    )
    yield candidate
    CandidateRepository.delete(candidate.id)


class TestCandidateRepository:
    def test_create(self, sample_candidate):
        assert sample_candidate.id is not None
        assert sample_candidate.tracking_code is not None
        assert len(sample_candidate.tracking_code) == 6

    def test_duplicate_national_id_rejected(self, sample_candidate):
        with pytest.raises(ValueError):
            CandidateRepository.create(
                national_id="0012345678",
                name="تکراری",
                age=20,
                gender="زن",
                field="ریاضی",
                previous_exam="خیر",
            )

    def test_get_by_id(self, sample_candidate):
        found = CandidateRepository.get_by_id(sample_candidate.id)
        assert found is not None
        assert found.name == "علی محمدی"

    def test_get_by_national_id(self, sample_candidate):
        found = CandidateRepository.get_by_national_id("0012345678")
        assert found is not None
        assert found.id == sample_candidate.id

    def test_update(self, sample_candidate):
        updated = CandidateRepository.update(sample_candidate.id, name="علی رضایی")
        assert updated is not None
        assert updated.name == "علی رضایی"

    def test_delete(self, sample_candidate):
        assert CandidateRepository.delete(sample_candidate.id) is True
        assert CandidateRepository.get_by_id(sample_candidate.id) is None

    def test_search(self, sample_candidate):
        results = CandidateRepository.search(query="علی")
        assert len(results) >= 1
        results = CandidateRepository.search(field="تجربی")
        assert len(results) >= 1
        results = CandidateRepository.search(gender="مرد")
        assert len(results) >= 1

    def test_count(self, sample_candidate):
        assert CandidateRepository.count() >= 1

    def test_count_by_field(self, sample_candidate):
        dist = CandidateRepository.count_by_field()
        assert dist.get("تجربی", 0) >= 1

    def test_count_by_gender(self, sample_candidate):
        dist = CandidateRepository.count_by_gender()
        assert dist.get("مرد", 0) >= 1


class TestScoreRepository:
    def test_set_and_get_scores(self, sample_candidate):
        scores = {"زیست": 85.5, "شیمی": 72.0, "فیزیک": 60.0}
        ScoreRepository.set_scores(sample_candidate.id, scores)
        fetched = ScoreRepository.get_scores(sample_candidate.id)
        assert fetched == scores

    def test_count(self, sample_candidate):
        ScoreRepository.set_scores(sample_candidate.id, {"زیست": 90.0})
        assert ScoreRepository.count() >= 1

    def test_average_by_subject(self, sample_candidate):
        ScoreRepository.set_scores(sample_candidate.id, {"زیست": 80.0, "شیمی": 60.0})
        avgs = ScoreRepository.average_by_subject()
        assert "زیست" in avgs
        assert avgs["زیست"] == 80.0


class TestExamYearRepository:
    def test_get_or_create(self):
        year = ExamYearRepository.get_or_create(2025)
        assert year.year == 2025
        again = ExamYearRepository.get_or_create(2025)
        assert again.id == year.id
