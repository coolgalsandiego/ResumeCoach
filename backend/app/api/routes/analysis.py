"""
Analysis endpoints for resume-job matching
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict
import uuid
from datetime import datetime
from app.services.analysis_service import AnalysisService
from app.models.schemas import AnalysisRequest, AnalysisResponse, AnalysisSummary
from app.api.routes.resume import resumes_db

router = APIRouter(prefix="/analysis")

analysis_service = AnalysisService()

# In-memory storage for analyses (use database in production)
analyses_db = {}


@router.post("/compare", response_model=AnalysisResponse)
async def create_analysis(request: AnalysisRequest):
    """
    Analyze resume against job description

    Performs comprehensive analysis including:
    - Overall fit assessment
    - Skill gap analysis
    - Strengths identification
    - Coaching advice

    Args:
        request: Analysis request with resume_id and job details

    Returns:
        Complete analysis report
    """
    # Fetch resume
    if request.resume_id not in resumes_db:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume_data = resumes_db[request.resume_id]
    resume_text = resume_data['parsed_data']['cleaned_text']

    # Get job description
    if not request.job_description and not request.job_id:
        raise HTTPException(
            status_code=400,
            detail="Either job_description or job_id must be provided"
        )

    if request.job_id:
        # In production, fetch from jobs database
        raise HTTPException(
            status_code=501,
            detail="Job ID lookup not yet implemented. Please provide job_description."
        )

    job_description = request.job_description

    # Run analysis
    try:
        print(f"Starting analysis for resume {request.resume_id}...")
        result = await analysis_service.analyze_resume(
            resume_text=resume_text,
            job_description=job_description,
            model_params=request.model_params
        )
        print("Analysis completed successfully!")

    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

    # Generate unique ID
    analysis_id = str(uuid.uuid4())

    # Extract job title from job description (simple heuristic)
    job_title = _extract_job_title(job_description)

    # Create summary object
    summary = AnalysisSummary(
        overall_fit=result['summary']['overall_fit'],
        match_score=result['summary']['match_score'],
        critical_gaps=result['summary']['critical_gaps'],
        top_strengths=result['summary']['top_strengths']
    )

    # Create response
    analysis_response = AnalysisResponse(
        analysis_id=analysis_id,
        resume_id=request.resume_id,
        job_title=job_title,
        fit_analysis=result['fit_analysis'],
        gap_analysis=result['gap_analysis'],
        strengths_analysis=result['strengths_analysis'],
        coaching_advice=result['coaching_advice'],
        summary=summary,
        created_at=datetime.utcnow()
    )

    # Store in database
    analyses_db[analysis_id] = {
        'analysis': analysis_response.dict(),
        'resume_data': resume_data,
        'job_description': job_description
    }

    return analysis_response


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str):
    """
    Retrieve analysis by ID

    Args:
        analysis_id: Unique analysis identifier

    Returns:
        Analysis report
    """
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis_data = analyses_db[analysis_id]['analysis']
    return AnalysisResponse(**analysis_data)


@router.post("/{analysis_id}/regenerate", response_model=AnalysisResponse)
async def regenerate_analysis(
    analysis_id: str,
    model_params: Dict = Body(None)
):
    """
    Regenerate analysis with different parameters

    Args:
        analysis_id: Existing analysis ID
        model_params: New model parameters (temperature, max_tokens)

    Returns:
        New analysis report
    """
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Get original data
    original = analyses_db[analysis_id]
    resume_data = original['resume_data']
    job_description = original['job_description']

    # Create new analysis request
    request = AnalysisRequest(
        resume_id=resume_data['resume_id'],
        job_description=job_description,
        model_params=model_params
    )

    return await create_analysis(request)


@router.get("/")
async def list_analyses() -> Dict:
    """
    List all analyses (for demo purposes)

    Returns:
        List of analysis IDs and summaries
    """
    return {
        "count": len(analyses_db),
        "analyses": [
            {
                "analysis_id": aid,
                "resume_id": data['analysis']['resume_id'],
                "job_title": data['analysis'].get('job_title', 'Unknown'),
                "match_score": data['analysis']['summary']['match_score'],
                "created_at": data['analysis']['created_at']
            }
            for aid, data in analyses_db.items()
        ]
    }


def _extract_job_title(job_description: str) -> str:
    """Extract job title from job description (simple heuristic)"""
    lines = job_description.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line and not line.startswith(('Job', 'Position', 'Location', 'Company')):
            # Likely the job title
            if len(line) < 100:  # Reasonable length for a title
                return line

    return "Position"
