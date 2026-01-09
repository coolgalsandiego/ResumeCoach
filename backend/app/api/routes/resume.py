"""
Resume upload and management endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import uuid
from app.services.resume_parser import ResumeParser
from app.models.schemas import ResumeUploadResponse, ErrorResponse
from app.config import settings

router = APIRouter(prefix="/resume")

resume_parser = ResumeParser()

# In-memory storage for demo (use database in production)
resumes_db = {}


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse resume

    Supports: PDF, DOCX, TXT formats

    Returns:
        - resume_id: Unique identifier for the resume
        - filename: Original filename
        - parsed_data: Extracted information from resume
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_extension = file.filename.split('.')[-1].lower()

    if file_extension not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(settings.allowed_extensions_list)}"
        )

    # Read file content
    try:
        file_content = await file.read()

        # Check file size
        if len(file_content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Parse resume
    try:
        parsed_data = await resume_parser.parse_file(file_content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

    # Generate unique ID
    resume_id = str(uuid.uuid4())

    # Store in database (in-memory for demo)
    resumes_db[resume_id] = {
        'resume_id': resume_id,
        'filename': file.filename,
        'parsed_data': parsed_data
    }

    return ResumeUploadResponse(
        resume_id=resume_id,
        filename=file.filename,
        parsed_data=parsed_data,
        message="Resume uploaded and parsed successfully"
    )


@router.get("/{resume_id}")
async def get_resume(resume_id: str) -> Dict:
    """
    Retrieve parsed resume by ID

    Args:
        resume_id: Unique resume identifier

    Returns:
        Parsed resume data
    """
    if resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resumes_db[resume_id]


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str) -> Dict:
    """
    Delete resume by ID

    Args:
        resume_id: Unique resume identifier

    Returns:
        Success message
    """
    if resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    del resumes_db[resume_id]

    return {"message": "Resume deleted successfully"}


@router.get("/")
async def list_resumes() -> Dict:
    """
    List all uploaded resumes (for demo purposes)

    Returns:
        List of resume IDs and filenames
    """
    return {
        "count": len(resumes_db),
        "resumes": [
            {
                "resume_id": rid,
                "filename": data['filename']
            }
            for rid, data in resumes_db.items()
        ]
    }
