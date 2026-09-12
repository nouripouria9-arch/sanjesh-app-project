"""
Import/Export service — handles CSV, Excel, and JSON data exchange.
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

from app.repositories.repositories import CandidateRepository

logger = logging.getLogger(__name__)


class ImportService:
    """Import candidates from CSV, Excel, or JSON files."""

    REQUIRED_COLUMNS = {"national_id", "name", "age", "gender", "field"}

    @staticmethod
    def import_csv(filepath: Path, encoding: str = "utf-8") -> tuple[list[dict], list[str]]:
        """Import CSV → list of dicts. Returns (data, errors)."""
        rows: list[dict] = []
        errors: list[str] = []
        try:
            with open(filepath, "r", encoding=encoding, newline="") as fh:
                reader = csv.DictReader(fh)
                if reader.fieldnames is None:
                    return [], ["فایل خالی است یا هدر ندارد."]
                for i, row in enumerate(reader, start=2):
                    required_check = {k for k in ImportService.REQUIRED_COLUMNS if k in row}
                    if required_check != ImportService.REQUIRED_COLUMNS:
                        missing = ImportService.REQUIRED_COLUMNS - required_check
                        errors.append(f"سطر {i}: ستون‌های مورد نیاز وجود ندارند: {missing}")
                        continue
                    try:
                        row["age"] = int(row.get("age", 0))
                    except (ValueError, TypeError):
                        errors.append(f"سطر {i}: مقدار سن نامعتبر است")
                        continue
                    rows.append(row)
            logger.info("Imported %d rows from CSV: %s", len(rows), filepath)
        except UnicodeDecodeError:
            try:
                with open(filepath, "r", encoding="cp1256", newline="") as fh:
                    reader = csv.DictReader(fh)
                    for i, row in enumerate(reader, start=2):
                        try:
                            row["age"] = int(row.get("age", 0))
                        except (ValueError, TypeError):
                            continue
                        rows.append(row)
                logger.info("Imported %d rows (cp1256) from CSV: %s", len(rows), filepath)
            except Exception as exc:
                errors.append(f"خطا در خواندن فایل: {exc}")
        except Exception as exc:
            errors.append(f"خطا در خواندن فایل CSV: {exc}")
        return rows, errors

    @staticmethod
    def import_excel(filepath: Path) -> tuple[list[dict], list[str]]:
        """Import Excel via pandas → list of dicts."""
        try:
            import pandas as pd
            df = pd.read_excel(filepath)
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            rows = df.where(df.notna(), None).to_dict(orient="records")
            errors = []
            for i, row in enumerate(rows, start=2):
                try:
                    row["age"] = int(float(row.get("age", 0)))
                except (ValueError, TypeError):
                    errors.append(f"سطر {i}: مقدار سن نامعتبر")
            logger.info("Imported %d rows from Excel: %s", len(rows), filepath)
            return rows, errors
        except Exception as exc:
            return [], [f"خطا در خواندن فایل Excel: {exc}"]

    @staticmethod
    def import_json(filepath: Path) -> tuple[list[dict], list[str]]:
        """Import JSON file → list of dicts."""
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                data = [data]
            rows = []
            errors = []
            for i, row in enumerate(data, start=1):
                try:
                    row["age"] = int(row.get("age", 0))
                except (ValueError, TypeError):
                    errors.append(f"ردیف {i}: مقدار سن نامعتبر")
                    continue
                rows.append(row)
            return rows, errors
        except Exception as exc:
            return [], [f"خطا در خواندن فایل JSON: {exc}"]


class ExportService:
    """Export candidates and scores to CSV, Excel, or JSON."""

    @staticmethod
    def export_csv(
        filepath: Path,
        candidates: list | None = None,
        encoding: str = "utf-8-sig",
    ) -> bool:
        """Export candidates to CSV."""
        try:
            if candidates is None:
                candidates = CandidateRepository.get_all()
            if not candidates:
                return False
            headers = [
                "national_id", "name", "age", "gender", "field",
                "previous_exam", "exam_year", "tracking_code", "register_time",
            ]
            with open(filepath, "w", encoding=encoding, newline="") as fh:
                writer = csv.writer(fh)
                writer.writerow(headers)
                for c in candidates:
                    writer.writerow([
                        c.national_id, c.name, c.age, c.gender, c.field,
                        c.previous_exam, c.exam_year, c.tracking_code, c.register_time,
                    ])
            logger.info("Exported %d candidates to CSV: %s", len(candidates), filepath)
            return True
        except Exception as exc:
            logger.error("CSV export failed: %s", exc)
            return False

    @staticmethod
    def export_excel(filepath: Path, candidates: list | None = None) -> bool:
        """Export candidates to Excel."""
        try:
            import pandas as pd
            if candidates is None:
                candidates = CandidateRepository.get_all()
            if not candidates:
                return False
            data = [{
                "کد ملی": c.national_id,
                "نام": c.name,
                "سن": c.age,
                "جنسیت": c.gender,
                "رشته": c.field,
                "شرکت مجدد": c.previous_exam,
                "سال آزمون": c.exam_year,
                "کد رهگیری": c.tracking_code,
                "زمان ثبت": c.register_time,
            } for c in candidates]
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False)
            logger.info("Exported %d candidates to Excel: %s", len(candidates), filepath)
            return True
        except Exception as exc:
            logger.error("Excel export failed: %s", exc)
            return False

    @staticmethod
    def export_json(filepath: Path, candidates: list | None = None) -> bool:
        """Export candidates to JSON."""
        try:
            if candidates is None:
                candidates = CandidateRepository.get_all()
            if not candidates:
                return False
            data = [{
                "national_id": c.national_id,
                "name": c.name,
                "age": c.age,
                "gender": c.gender,
                "field": c.field,
                "previous_exam": c.previous_exam,
                "exam_year": c.exam_year,
                "tracking_code": c.tracking_code,
                "register_time": c.register_time,
            } for c in candidates]
            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
            logger.info("Exported %d candidates to JSON: %s", len(candidates), filepath)
            return True
        except Exception as exc:
            logger.error("JSON export failed: %s", exc)
            return False
