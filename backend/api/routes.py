"""API routes for all endpoints."""

import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from .schemas import (
    GenerateRequest, GenerateResponse,
    AnalyzeRequest, AnalysisResponse,
    AutocompleteRequest, AutocompleteResponse,
    SimilarityRequest, SimilarityResponse,
    LanguagesResponse,
)
from ..services.code_generator import generate_code, generate_autocomplete
from ..services.code_analyzer import analyze_code
from ..services.similarity_checker import check_similarity
from ..utils.language_support import detect_language
from ..config import SUPPORTED_LANGUAGES, FILE_EXTENSIONS

router = APIRouter(prefix="/api", tags=["code-analysis"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_endpoint(request: GenerateRequest):
    """Generate code from natural language input."""
    try:
        result = generate_code(
            prompt=request.prompt,
            language=request.language,
            max_length=request.max_length,
        )
        return GenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(request: AnalyzeRequest):
    """Analyze code with all metrics."""
    try:
        if not request.code.strip():
            raise HTTPException(status_code=400, detail="Code cannot be empty")

        result = analyze_code(
            code=request.code,
            language=request.language,
        )
        return AnalysisResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/upload")
async def upload_endpoint(
    file: UploadFile = File(...),
    language: str = Form(default="auto"),
):
    """Upload a code file for analysis."""
    try:
        # Validate file extension
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in FILE_EXTENSIONS and ext.lower() not in ('.py', '.java', '.cpp', '.c', '.h'):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Supported: .py, .java, .cpp, .c"
            )

        # Read file content
        content = await file.read()
        code = content.decode('utf-8', errors='replace')

        if not code.strip():
            raise HTTPException(status_code=400, detail="File is empty")

        # Auto-detect language
        if language == "auto":
            language = detect_language(code, file.filename)

        # Run analysis
        result = analyze_code(code=code, language=language)
        result["filename"] = file.filename

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload analysis failed: {str(e)}")


@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_endpoint(request: AutocompleteRequest):
    """Generate code auto-completion suggestions."""
    try:
        suggestions = generate_autocomplete(
            code=request.code,
            language=request.language,
        )
        return AutocompleteResponse(suggestions=suggestions, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autocomplete failed: {str(e)}")


@router.post("/similarity", response_model=SimilarityResponse)
async def similarity_endpoint(request: SimilarityRequest):
    """Compare two code snippets for similarity."""
    try:
        if not request.code1.strip() or not request.code2.strip():
            raise HTTPException(status_code=400, detail="Both code snippets are required")

        result = check_similarity(
            code1=request.code1,
            code2=request.code2,
            language=request.language,
        )
        return SimilarityResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity check failed: {str(e)}")


@router.get("/languages", response_model=LanguagesResponse)
async def languages_endpoint():
    """Get supported programming languages."""
    return LanguagesResponse(
        languages=SUPPORTED_LANGUAGES,
        file_extensions=FILE_EXTENSIONS,
    )
