"""Multilingual intelligence APIs."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, model_validator

from multilingual.detection.mixed_language_detector import MixedLanguageDetector
from multilingual.evaluation.multilingual_benchmarks import run_language_benchmark
from multilingual.localization.dashboard_translation import DashboardTranslation
from multilingual.normalization.unicode_normalizer import UnicodeNormalizer
from multilingual.ocr.scanned_doc_processor import ScannedDocProcessor
from multilingual.retrieval.multilingual_retriever import MultilingualRetriever
from multilingual.translation.translator_router import TranslatorRouter
from observability.metrics import multilingual_requests_total, multilingual_retrieval_confidence, ocr_accuracy_score, translation_latency

router = APIRouter(prefix="/multilingual", tags=["Multilingual"])


class DetectRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    target_language: str = Field("en", pattern="^(en|hi|mr)$")
    source_language: str | None = Field(None, pattern="^(en|hi|mr|unknown)$")


class RetrieveRequest(BaseModel):
    query: str | None = Field(None, min_length=2, max_length=3000)
    query_text: str | None = Field(None, min_length=2, max_length=3000)
    department: str = ""
    response_language: str | None = Field(None, pattern="^(en|hi|mr)$")
    languages: list[str] | None = None
    k: int = Field(5, ge=1, le=20)

    @model_validator(mode="after")
    def normalize_legacy_fields(self) -> "RetrieveRequest":
        if self.query is None:
            self.query = self.query_text
        if self.response_language is None and self.languages:
            self.response_language = self.languages[0]
        if self.query is None:
            raise ValueError("query is required")
        return self


class OCRRequest(BaseModel):
    path: str | None = Field(None, min_length=1)
    image_url: str | None = None
    language_hint: str | None = None
    languages: list[str] = Field(default_factory=lambda: ["eng", "hin", "mar"])


@router.post("/detect")
async def detect_language(payload: DetectRequest):
    normalized = UnicodeNormalizer().normalize(payload.text)
    result = MixedLanguageDetector().analyze(normalized)
    if _looks_marathi(normalized):
        result = {**result, "language": "mr", "confidence": max(float(result.get("confidence", 0.0)), 0.82)}
    multilingual_requests_total.labels(language=result.get("language", "unknown"), operation="detect").inc()
    return {"normalized_text": normalized, **result}


@router.post("/translate")
async def translate(payload: TranslateRequest, request: Request):
    mongo = getattr(request.app.state, "mongo", None)
    db = getattr(mongo, "db", None) if mongo else None
    result = await TranslatorRouter().translate(
        payload.text,
        target_language=payload.target_language,
        source_language=payload.source_language,
        db=db,
    )
    multilingual_requests_total.labels(language=result["source_language"], operation="translate").inc()
    translation_latency.labels(source_language=result["source_language"], target_language=payload.target_language).observe(result["latency_ms"] / 1000)
    return result


@router.post("/retrieve")
async def retrieve(payload: RetrieveRequest, request: Request):
    mongo = getattr(request.app.state, "mongo", None)
    db = getattr(mongo, "db", None) if mongo else None
    result = await MultilingualRetriever().retrieve(
        payload.query or "",
        department=payload.department,
        response_language=payload.response_language,
        k=payload.k,
        db=db,
    )
    language = result["detected_language"]["language"]
    multilingual_requests_total.labels(language=language, operation="retrieve").inc()
    multilingual_retrieval_confidence.labels(language=language).observe(result["confidence"])
    return result


@router.post("/ocr")
async def ocr(payload: OCRRequest):
    if payload.image_url:
        raise HTTPException(status_code=400, detail="Remote OCR URLs are not accepted; provide a local workspace path.")
    if not payload.path:
        raise HTTPException(status_code=400, detail="OCR path is required.")
    resolved = Path(payload.path).resolve()
    workspace = Path.cwd().resolve()
    tmp = Path("C:/tmp").resolve()
    if not (str(resolved).startswith(str(workspace)) or str(resolved).startswith(str(tmp))):
        raise HTTPException(status_code=400, detail="OCR path must be inside the workspace or C:/tmp")
    result = await ScannedDocProcessor().process(payload.path, payload.languages)
    language = result.get("language", {}).get("language", "unknown")
    multilingual_requests_total.labels(language=language, operation="ocr").inc()
    ocr_accuracy_score.labels(languages="+".join(payload.languages)).observe(result.get("confidence", 0.0))
    return result


def _looks_marathi(text: str) -> bool:
    marathi_markers = {
        "\u091d\u093e\u0932\u0947\u0932\u093e",
        "\u0915\u093f\u0924\u0940",
        "\u090f\u0915\u0942\u0923",
        "\u0916\u0930\u094d\u091a",
        "\u0905\u0902\u0924\u0930\u094d\u0917\u0924",
        "\u092a\u0941\u0923\u0947",
    }
    return any(marker in text for marker in marathi_markers)


@router.get("/stats")
async def stats(language: str = "en"):
    return {
        "supported_languages": ["en", "hi", "mr"],
        "supported_scripts": ["latin", "devanagari"],
        "ui": DashboardTranslation().translate_labels(language),
        "benchmark": run_language_benchmark(),
        "voice_ready": {"speech_to_text": "planned_adapter", "text_to_speech": "planned_adapter", "voice_rti": "workflow_ready"},
    }
