"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Resume Models
class ResumeUploadResponse(BaseModel):
    """Response after resume upload"""
    resume_id: str
    filename: str
    parsed_data: Dict[str, Any]
    s3_url: Optional[str] = None
    message: str = "Resume uploaded and parsed successfully"


class ParsedResume(BaseModel):
    """Structured resume data"""
    raw_text: str
    cleaned_text: str
    sections: Dict[str, str]
    skills: List[str]
    years_experience: int
    contact_info: Dict[str, str]
    metadata: Dict[str, Any]


# Job Models
class JobDescription(BaseModel):
    """Job description input"""
    job_id: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    location: Optional[str] = None


class JobSearchRequest(BaseModel):
    """Job search parameters"""
    query: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)


# Analysis Models
class AnalysisRequest(BaseModel):
    """Request for resume analysis"""
    resume_id: str
    job_id: Optional[str] = None
    job_description: Optional[str] = None
    model_params: Optional[Dict[str, Any]] = None


class AnalysisSummary(BaseModel):
    """Summary of analysis results"""
    overall_fit: str  # Poor, Fair, Good, Excellent
    match_score: int  # 0-100
    critical_gaps: List[str]
    top_strengths: List[str]


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    analysis_id: str
    resume_id: str
    job_title: Optional[str] = None
    fit_analysis: str
    gap_analysis: str
    strengths_analysis: str
    coaching_advice: str
    summary: AnalysisSummary
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Chat Models
class ChatMessage(BaseModel):
    """Chat message from user"""
    session_id: str
    message: str
    analysis_id: str


class ChatResponse(BaseModel):
    """Chat response from AI"""
    response: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistory(BaseModel):
    """Chat conversation history"""
    session_id: str
    messages: List[Dict[str, str]]


# Model Parameters
class ModelParameters(BaseModel):
    """LLM model parameters"""
    temperature: float = Field(default=0.5, ge=0.0, le=1.0)
    max_tokens: int = Field(default=800, ge=100, le=2000)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: int = Field(default=50, ge=1, le=100)


# Error Response
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    status_code: int


# Health Check
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
