"""
Report generator — creates summary reports from real data.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from app.analytics.analytics_engine import AnalyticsService
from app.repositories.repositories import CandidateRepository, ScoreRepository

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate text-based and structured reports from the database."""

    @staticmethod
    def generate_summary_report() -> str:
        """Full statistical summary report."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("       گزارش خلاصه سامانه سنجش")
        lines.append(f"       تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)

        ca = AnalyticsService.get_candidate_analytics()
        sa = AnalyticsService.get_score_analytics()

        lines.append("")
        lines.append("── آمار کلی داوطلبان ──")
        lines.append(f"  تعداد کل داوطلبان:       {ca.total}")
        lines.append(f"  تجربی:                    {ca.total_tajrobi}")
        lines.append(f"  ریاضی:                    {ca.total_riazi}")
        lines.append(f"  مرد:                      {ca.total_male}")
        lines.append(f"  زن:                       {ca.total_female}")
        lines.append(f"  شرکت‌کنندگان مجدد:        {ca.total_with_previous}")
        lines.append(f"  میانگین سن:               {ca.avg_age}")
        if ca.age_stats:
            lines.append(f"  حداقل سن:                 {ca.age_stats.minimum}")
            lines.append(f"  حداکثر سن:                {ca.age_stats.maximum}")
            lines.append(f"  انحراف معیار سن:          {ca.age_stats.std_dev}")

        lines.append("")
        lines.append("── آمار کلی نمرات ──")
        lines.append(f"  تعداد نمرات ثبت شده:     {sa.total_score_records}")
        lines.append(f"  تعداد داوطلبان با نمره:  {sa.candidates_with_scores}")
        if sa.total_score_records > 0:
            lines.append(f"  میانگین نمرات:            {sa.overall_avg}")
            lines.append(f"  میانگین نمرات:            {sa.overall_median}")
            lines.append(f"  انحراف معیار نمرات:       {sa.overall_std}")
            lines.append(f"  حداقل نمره:               {sa.overall_min}")
            lines.append(f"  حداکثر نمره:              {sa.overall_max}")

        if sa.subject_averages:
            lines.append("")
            lines.append("── میانگین نمرات بر اساس درس ──")
            for subject, avg in sorted(sa.subject_averages.items()):
                lines.append(f"  {subject:<20s}  {avg:.1f}%")

        if sa.subject_stats:
            lines.append("")
            lines.append("── تحلیل تفصیلی دروس ──")
            for subject, s in sorted(sa.subject_stats.items()):
                lines.append(f"  {subject}:")
                lines.append(f"    تعداد: {s.count} | میانگین: {s.mean} | میانگین: {s.median}")
                lines.append(f"    انحراف معیار: {s.std_dev} | حداقل: {s.minimum} | حداکثر: {s.maximum}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def generate_candidate_report(candidate_id: int) -> str | None:
        """Detailed report for a single candidate."""
        from app.models.entities import Candidate
        from app.database.engine import get_session

        with get_session() as session:
            candidate = session.get(Candidate, candidate_id)
            if not candidate:
                return None

        from app.repositories.repositories import ScoreRepository
        scores = ScoreRepository.get_scores(candidate_id)
        lines: list[str] = []
        lines.append(f"گزارش داوطلب: {candidate.name}")
        lines.append(f"کد ملی: {candidate.national_id}")
        lines.append(f"سن: {candidate.age}")
        lines.append(f"جنسیت: {candidate.gender}")
        lines.append(f"رشته: {candidate.field}")
        lines.append(f"شرکت مجدد: {candidate.previous_exam}")
        lines.append(f"سال آزمون: {candidate.exam_year}")
        lines.append(f"کد رهگیری: {candidate.tracking_code}")
        lines.append(f"زمان ثبت: {candidate.register_time}")
        lines.append("")
        if scores:
            lines.append("نمرات:")
            for subj, pct in scores.items():
                lines.append(f"  {subj}: {pct}%")
            avg = sum(scores.values()) / len(scores)
            lines.append(f"\n  میانگین نمرات: {avg:.1f}%")
        else:
            lines.append("نمره‌ای ثبت نشده است.")
        return "\n".join(lines)

    @staticmethod
    def generate_subject_report() -> str:
        """Subject performance comparison report."""
        comp = AnalyticsService.get_subject_comparison()
        lines: list[str] = []
        lines.append("گزارش مقایسه عملکرد دروس")
        lines.append("-" * 50)
        for subject, data in sorted(comp.items()):
            lines.append(f"\n{subject}:")
            lines.append(f"  تعداد نمره: {int(data['count'])}")
            lines.append(f"  میانگین: {data['mean']:.1f}%")
            lines.append(f"  میانگین: {data['median']:.1f}%")
            lines.append(f"  انحراف معیار: {data['std_dev']:.1f}")
            lines.append(f"  محدوده: {data['min']:.1f}% - {data['max']:.1f}%")
        return "\n".join(lines)

    @staticmethod
    def generate_year_comparison_report() -> str:
        """Year-over-year comparison report."""
        comp = AnalyticsService.get_year_comparison()
        lines: list[str] = []
        lines.append("گزارش مقایسه سال‌های آزمون")
        lines.append("=" * 60)
        for year, data in sorted(comp.items()):
            lines.append(f"\nسال {year}:")
            lines.append(f"  تعداد داوطلب: {data['candidate_count']}")
            lines.append(f"  میانگین سن: {data['avg_age']}")
            lines.append(f"  مرد/زن: {data['male_count']}/{data['female_count']}")
            lines.append(f"  میانگین نمره: {data['overall_avg']}")
            lines.append(f"  میانگین نمره: {data['overall_median']}")
            lines.append(f"  انحراف معیار: {data['overall_std']}")
            if data["subject_averages"]:
                lines.append("  نمرات دروس:")
                for subj, avg in data["subject_averages"].items():
                    lines.append(f"    {subj}: {avg}%")
        return "\n".join(lines)

    @staticmethod
    def save_report(content: str, filepath: Path) -> bool:
        """Save report text to a file."""
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(content)
            logger.info("Report saved to %s", filepath)
            return True
        except Exception as exc:
            logger.error("Report save failed: %s", exc)
            return False
