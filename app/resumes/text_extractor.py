from pathlib import Path

import fitz

from app.core.exceptions import ValidationError

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def extract_resume_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValidationError(
            "Unsupported resume file type",
            details={"extension": suffix, "supported": sorted(SUPPORTED_EXTENSIONS)},
        )

    if not file_path.exists():
        raise ValidationError("Resume file does not exist", details={"file_path": str(file_path)})

    if suffix == ".pdf":
        return _extract_pdf_text(file_path)

    return file_path.read_text(encoding="utf-8").strip()


def _extract_pdf_text(file_path: Path) -> str:
    text_parts: list[str] = []
    with fitz.open(file_path) as document:
        for page in document:
            text_parts.append(page.get_text("text"))

    return "\n".join(text_parts).strip()
