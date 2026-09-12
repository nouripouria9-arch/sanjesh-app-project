"""
Analytics engine tests — verify statistical calculations.
"""

import pytest

from app.analytics.analytics_engine import AnalyticsService
from app.database.engine import initialize_database, shutdown_database
from app.repositories.repositories import CandidateRepository, ScoreRepository


@pytest.fixture(scope="module", autouse=True)
def db():
    initialize_database()
    yield
    shutdown_database()


@pytest.fixture()
def populated():
    """Create candidates with known scores."""
    ids = []
    data = [
        ("1111111111", "آزمون ۱", 18, "مرد", "تجربی", {"زیست": 90, "شیمی": 80}),
        ("2222222222", "آزمون ۲", 20, "زن", "ریاضی", {"حسابان": 70, "فیزیک": 60}),
        ("3333333333", "آزمون ۳", 22, "مرد", "تجربی", {"زیست": 50, "شیمی": 40}),
        ("4444444444", "آزمون ۴", 25, "زن", "ریاضی", {"حسابان": 30, "فیزیک": 20}),
    ]
    for nid, name, age, gender, field, scores in data:
        c = CandidateRepository.create(
            national_id=nid, name=name, age=age,
            gender=gender, field=field, previous_exam="خیر",
        )
        ScoreRepository.set_scores(c.id, scores)
        ids.append(c.id)
    yield ids
    for cid in ids:
        CandidateRepository.delete(cid)


class TestBasicStats:
    def test_empty(self):
        s = AnalyticsService.calc_basic_stats([])
        assert s.count == 0
        assert s.mean == 0.0

    def test_single_value(self):
        s = AnalyticsService.calc_basic_stats([50.0])
        assert s.count == 1
        assert s.mean == 50.0
        assert s.minimum == 50.0
        assert s.maximum == 50.0

    def test_known_values(self):
        s = AnalyticsService.calc_basic_stats([10, 20, 30, 40, 50])
        assert s.mean == 30.0
        assert s.median == 30.0
        assert s.minimum == 10.0
        assert s.maximum == 50.0
        assert s.range_val == 40.0


class TestCandidateAnalytics:
    def test_total(self, populated):
        ca = AnalyticsService.get_candidate_analytics()
        assert ca.total >= 4
        assert ca.total_male >= 2
        assert ca.total_female >= 2

    def test_field_distribution(self, populated):
        ca = AnalyticsService.get_candidate_analytics()
        assert ca.total_tajrobi >= 2
        assert ca.total_riazi >= 2

    def test_avg_age(self, populated):
        ca = AnalyticsService.get_candidate_analytics()
        assert 18 <= ca.avg_age <= 25


class TestScoreAnalytics:
    def test_overall_stats(self, populated):
        sa = AnalyticsService.get_score_analytics()
        assert sa.total_score_records >= 8
        assert sa.overall_avg > 0
        assert sa.overall_min <= sa.overall_max

    def test_subject_averages(self, populated):
        sa = AnalyticsService.get_score_analytics()
        assert "زیست" in sa.subject_averages
        # زیست scores: 90, 50 → avg 70
        assert sa.subject_averages["زیست"] == 70.0

    def test_score_distribution(self, populated):
        sa = AnalyticsService.get_score_analytics()
        total = sum(sa.score_distribution.values())
        assert total == sa.total_score_records


class TestSubjectComparison:
    def test_comparison(self, populated):
        comp = AnalyticsService.get_subject_comparison()
        assert "زیست" in comp
        assert comp["زیست"]["mean"] == 70.0
        assert comp["زیست"]["count"] == 2


class TestYearComparison:
    def test_year_comparison(self, populated):
        comp = AnalyticsService.get_year_comparison()
        assert len(comp) >= 1
        for year, data in comp.items():
            assert data["candidate_count"] >= 1
            assert "overall_avg" in data
