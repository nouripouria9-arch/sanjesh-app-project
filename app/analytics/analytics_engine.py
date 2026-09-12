"""
Professional statistical analytics engine.
All calculations use real database data via repository layer.
"""

from __future__ import annotations

import logging
import statistics as stats_mod
from dataclasses import dataclass, field
from typing import Any

from app.repositories.repositories import CandidateRepository, ScoreRepository

logger = logging.getLogger(__name__)


@dataclass
class BasicStats:
    """Basic descriptive statistics for a numeric list."""
    count: int = 0
    mean: float = 0.0
    median: float = 0.0
    std_dev: float = 0.0
    minimum: float = 0.0
    maximum: float = 0.0
    variance: float = 0.0
    q1: float = 0.0
    q3: float = 0.0
    iqr: float = 0.0
    range_val: float = 0.0


@dataclass
class CandidateAnalytics:
    """Aggregate candidate statistics."""
    total: int = 0
    total_tajrobi: int = 0
    total_riazi: int = 0
    total_male: int = 0
    total_female: int = 0
    total_with_previous: int = 0
    avg_age: float = 0.0
    field_distribution: dict[str, int] = field(default_factory=dict)
    gender_distribution: dict[str, int] = field(default_factory=dict)
    year_distribution: dict[int, int] = field(default_factory=dict)
    previous_exam_distribution: dict[str, int] = field(default_factory=dict)
    age_stats: BasicStats = field(default_factory=BasicStats)


@dataclass
class ScoreAnalytics:
    """Aggregate score statistics."""
    total_score_records: int = 0
    candidates_with_scores: int = 0
    overall_avg: float = 0.0
    overall_median: float = 0.0
    overall_std: float = 0.0
    overall_min: float = 0.0
    overall_max: float = 0.0
    subject_averages: dict[str, float] = field(default_factory=dict)
    subject_stats: dict[str, BasicStats] = field(default_factory=dict)
    score_distribution: dict[str, int] = field(default_factory=dict)
    year_subject_averages: dict[int, dict[str, float]] = field(default_factory=dict)


class AnalyticsService:
    """Professional statistical analysis using real data."""

    @staticmethod
    def calc_basic_stats(values: list[float]) -> BasicStats:
        """Compute descriptive statistics for a numeric list."""
        if not values:
            return BasicStats()
        s = BasicStats(
            count=len(values),
            mean=round(stats_mod.mean(values), 2),
            median=round(stats_mod.median(values), 2),
            minimum=round(min(values), 2),
            maximum=round(max(values), 2),
            range_val=round(max(values) - min(values), 2),
        )
        if len(values) >= 2:
            s.std_dev = round(stats_mod.stdev(values), 2)
            s.variance = round(stats_mod.variance(values), 2)
        sorted_v = sorted(values)
        n = len(sorted_v)
        q1_idx = n // 4
        q3_idx = (3 * n) // 4
        s.q1 = round(sorted_v[q1_idx], 2)
        s.q3 = round(sorted_v[min(q3_idx, n - 1)], 2)
        s.iqr = round(s.q3 - s.q1, 2)
        return s

    @staticmethod
    def get_candidate_analytics() -> CandidateAnalytics:
        """Full candidate-level analytics from the database."""
        analytics = CandidateAnalytics()
        analytics.field_distribution = CandidateRepository.count_by_field()
        analytics.gender_distribution = CandidateRepository.count_by_gender()
        analytics.year_distribution = CandidateRepository.count_by_year()
        analytics.previous_exam_distribution = CandidateRepository.count_previous_exam()
        analytics.total = CandidateRepository.count()
        analytics.total_tajrobi = analytics.field_distribution.get("تجربی", 0)
        analytics.total_riazi = analytics.field_distribution.get("ریاضی", 0)
        analytics.total_male = analytics.gender_distribution.get("مرد", 0)
        analytics.total_female = analytics.gender_distribution.get("زن", 0)
        analytics.total_with_previous = analytics.previous_exam_distribution.get("بله", 0)
        candidates = CandidateRepository.get_all()
        if candidates:
            ages = [float(c.age) for c in candidates]
            analytics.avg_age = round(stats_mod.mean(ages), 1)
            analytics.age_stats = AnalyticsService.calc_basic_stats(ages)
        return analytics

    @staticmethod
    def get_score_analytics(exam_year: int | None = None) -> ScoreAnalytics:
        """Full score-level analytics, optionally filtered by exam year."""
        from sqlalchemy import func, select
        from app.database.engine import get_session
        from app.models.entities import Score, Candidate

        sa = ScoreAnalytics()
        sa.total_score_records = ScoreRepository.count()
        sa.candidates_with_scores = ScoreRepository.count_candidates_with_scores()
        sa.subject_averages = (
            ScoreRepository.average_by_subject_year(exam_year)
            if exam_year
            else ScoreRepository.average_by_subject()
        )

        with get_session() as session:
            stmt = select(Score.percent)
            if exam_year:
                stmt = stmt.join(Candidate, Score.candidate_id == Candidate.id).where(
                    Candidate.exam_year == exam_year
                )
            all_percents = [float(p) for p in session.execute(stmt).scalars().all()]
            if exam_year:
                sa.total_score_records = len(all_percents)
                sa.candidates_with_scores = session.execute(
                    select(func.count(func.distinct(Score.candidate_id)))
                    .join(Candidate, Score.candidate_id == Candidate.id)
                    .where(Candidate.exam_year == exam_year)
                ).scalar_one()

        if all_percents:
            overall = AnalyticsService.calc_basic_stats(all_percents)
            sa.overall_avg = overall.mean
            sa.overall_median = overall.median
            sa.overall_std = overall.std_dev
            sa.overall_min = overall.minimum
            sa.overall_max = overall.maximum

        with get_session() as session:
            stmt = select(Score.subject, Score.percent)
            if exam_year:
                stmt = stmt.join(Candidate, Score.candidate_id == Candidate.id).where(
                    Candidate.exam_year == exam_year
                )
            subject_scores: dict[str, list[float]] = {}
            for subject, percent in session.execute(stmt).all():
                subject_scores.setdefault(subject, []).append(float(percent))
            for subject, scores_list in subject_scores.items():
                sa.subject_stats[subject] = AnalyticsService.calc_basic_stats(scores_list)

        buckets = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
        for p in all_percents:
            if p < 20:
                buckets["0-20"] += 1
            elif p < 40:
                buckets["20-40"] += 1
            elif p < 60:
                buckets["40-60"] += 1
            elif p < 80:
                buckets["60-80"] += 1
            else:
                buckets["80-100"] += 1
        sa.score_distribution = buckets

        return sa

    @staticmethod
    def get_subject_comparison() -> dict[str, dict[str, float]]:
        """Subject-level comparison: avg, median, std per subject."""
        from sqlalchemy import select
        from app.database.engine import get_session
        from app.models.entities import Score

        result: dict[str, dict[str, float]] = {}
        with get_session() as session:
            subject_scores: dict[str, list[float]] = {}
            for subject, percent in session.execute(select(Score.subject, Score.percent)).all():
                subject_scores.setdefault(subject, []).append(float(percent))
        for subject, scores_list in subject_scores.items():
            bs = AnalyticsService.calc_basic_stats(scores_list)
            result[subject] = {
                "mean": bs.mean,
                "median": bs.median,
                "std_dev": bs.std_dev,
                "min": bs.minimum,
                "max": bs.maximum,
                "count": bs.count,
            }
        return result

    @staticmethod
    def get_year_comparison() -> dict[int, dict[str, Any]]:
        """Compare metrics across exam years."""
        from sqlalchemy import func, select
        from app.database.engine import get_session
        from app.models.entities import Candidate, Score

        result: dict[int, dict[str, Any]] = {}
        years = CandidateRepository.distinct_years()
        with get_session() as session:
            for year in years:
                cand_count = session.execute(
                    select(func.count(Candidate.id)).where(Candidate.exam_year == year)
                ).scalar_one()
                avg_age = session.execute(
                    select(func.avg(Candidate.age)).where(Candidate.exam_year == year)
                ).scalar()
                male_count = session.execute(
                    select(func.count(Candidate.id)).where(
                        Candidate.exam_year == year, Candidate.gender == "مرد"
                    )
                ).scalar_one()
                score_avgs = {}
                for subject, avg in session.execute(
                    select(Score.subject, func.avg(Score.percent))
                    .join(Candidate, Score.candidate_id == Candidate.id)
                    .where(Candidate.exam_year == year)
                    .group_by(Score.subject)
                ).all():
                    score_avgs[subject] = round(float(avg), 2)

                all_scores = session.execute(
                    select(Score.percent)
                    .join(Candidate, Score.candidate_id == Candidate.id)
                    .where(Candidate.exam_year == year)
                ).scalars().all()
                all_scores = [float(s) for s in all_scores]

                result[year] = {
                    "candidate_count": cand_count,
                    "avg_age": round(float(avg_age or 0), 1),
                    "male_count": male_count,
                    "female_count": cand_count - male_count,
                    "subject_averages": score_avgs,
                    "overall_avg": round(stats_mod.mean(all_scores), 2) if all_scores else 0,
                    "overall_median": round(stats_mod.median(all_scores), 2) if all_scores else 0,
                    "overall_std": round(stats_mod.stdev(all_scores), 2) if len(all_scores) >= 2 else 0,
                }
        return result
