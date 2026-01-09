"""
Chat endpoints for conversational coaching
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
from app.services.llm_service import LLMService
from app.models.schemas import ChatMessage, ChatResponse, ChatHistory
from app.chains.prompts import get_prompt
from app.api.routes.analysis import analyses_db
from datetime import datetime

router = APIRouter(prefix="/chat")

llm_service = LLMService()

# In-memory chat sessions (use database/Redis in production)
chat_sessions = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(chat_msg: ChatMessage):
    """
    Send message to chatbot

    Args:
        chat_msg: Chat message with session_id, message, and analysis_id

    Returns:
        AI response
    """
    session_id = chat_msg.session_id
    analysis_id = chat_msg.analysis_id

    # Get analysis data
    if analysis_id not in analyses_db:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis_data = analyses_db[analysis_id]
    analysis = analysis_data['analysis']

    # Initialize or get chat session
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            'analysis_id': analysis_id,
            'messages': []
        }

    session = chat_sessions[session_id]

    # Build context from analysis
    resume_summary = _build_resume_summary(analysis_data['resume_data'])
    job_title = analysis.get('job_title', 'the position')
    analysis_summary = _build_analysis_summary(analysis)
    chat_history = _format_chat_history(session['messages'])

    # Generate response
    try:
        prompt = get_prompt(
            'chat',
            resume_summary=resume_summary,
            job_title=job_title,
            analysis_summary=analysis_summary,
            chat_history=chat_history,
            user_question=chat_msg.message
        )

        response_text = await llm_service.generate(
            prompt,
            temperature=0.7,  # Slightly higher for conversational
            max_tokens=500
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat generation failed: {str(e)}"
        )

    # Save to session history
    session['messages'].append({
        'role': 'user',
        'content': chat_msg.message,
        'timestamp': datetime.utcnow().isoformat()
    })
    session['messages'].append({
        'role': 'assistant',
        'content': response_text,
        'timestamp': datetime.utcnow().isoformat()
    })

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        timestamp=datetime.utcnow()
    )


@router.get("/history/{session_id}", response_model=ChatHistory)
async def get_history(session_id: str):
    """
    Get chat history for a session

    Args:
        session_id: Session identifier

    Returns:
        Chat history
    """
    if session_id not in chat_sessions:
        return ChatHistory(session_id=session_id, messages=[])

    session = chat_sessions[session_id]

    return ChatHistory(
        session_id=session_id,
        messages=session['messages']
    )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str) -> Dict:
    """
    Clear chat session

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    if session_id in chat_sessions:
        del chat_sessions[session_id]

    return {"message": "Session cleared successfully"}


@router.get("/")
async def list_sessions() -> Dict:
    """
    List all chat sessions (for demo purposes)

    Returns:
        List of session IDs
    """
    return {
        "count": len(chat_sessions),
        "sessions": [
            {
                "session_id": sid,
                "analysis_id": data['analysis_id'],
                "message_count": len(data['messages'])
            }
            for sid, data in chat_sessions.items()
        ]
    }


def _build_resume_summary(resume_data: Dict) -> str:
    """Build brief resume summary for context"""
    parsed = resume_data['parsed_data']

    parts = []

    # Skills
    skills = parsed.get('skills', [])
    if skills:
        parts.append(f"Key skills: {', '.join(skills[:5])}")

    # Experience
    years = parsed.get('years_experience', 0)
    if years > 0:
        parts.append(f"{years}+ years of experience")

    # Sections
    sections = parsed.get('sections', {})
    if sections:
        parts.append(f"Resume sections: {', '.join(sections.keys())}")

    return ". ".join(parts) if parts else "Resume parsed successfully"


def _build_analysis_summary(analysis: Dict) -> str:
    """Build brief analysis summary for context"""
    summary = analysis.get('summary', {})

    parts = [
        f"Overall Fit: {summary.get('overall_fit', 'Unknown')}",
        f"Match Score: {summary.get('match_score', 0)}/100"
    ]

    critical_gaps = summary.get('critical_gaps', [])
    if critical_gaps:
        parts.append(f"Critical gaps: {', '.join(critical_gaps[:3])}")

    top_strengths = summary.get('top_strengths', [])
    if top_strengths:
        parts.append(f"Top strengths: {', '.join(top_strengths[:3])}")

    return ". ".join(parts)


def _format_chat_history(messages: list) -> str:
    """Format chat history for prompt"""
    if not messages:
        return "No previous conversation."

    # Take last 10 messages
    recent = messages[-10:]

    formatted = []
    for msg in recent:
        role = "User" if msg['role'] == 'user' else "Coach"
        formatted.append(f"{role}: {msg['content']}")

    return "\n".join(formatted)
