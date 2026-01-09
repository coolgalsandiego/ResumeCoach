"""
Tests for AnalysisService
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.analysis_service import AnalysisService


@pytest.fixture
def analysis_service():
    """Create AnalysisService instance"""
    return AnalysisService()


@pytest.fixture
def sample_resume_text():
    """Sample resume text"""
    return """
    John Doe
    Software Engineer
    
    EXPERIENCE
    Software Engineer | Tech Corp | 2020-Present
    - Developed web applications using Python and React
    - Led team of 5 developers
    
    SKILLS
    Python, JavaScript, React, Docker, AWS
    """


@pytest.fixture
def sample_job_description():
    """Sample job description"""
    return """
    Software Engineer Position
    
    Requirements:
    - 3+ years of experience with Python
    - Experience with React and JavaScript
    - Knowledge of AWS and cloud services
    - Strong problem-solving skills
    """


class TestAnalysisService:
    """Test cases for AnalysisService"""

    @pytest.mark.unit
    def test_handle_long_text_short(self, analysis_service):
        """Test handling short text"""
        text = "Short text"
        result = analysis_service._handle_long_text(text, max_tokens=1500)
        assert result == text

    @pytest.mark.unit
    def test_handle_long_text_long(self, analysis_service):
        """Test handling long text"""
        long_text = "A" * 10000  # Very long text
        result = analysis_service._handle_long_text(long_text, max_tokens=100)
        assert len(result) < len(long_text)
        assert "[Document truncated" in result

    @pytest.mark.unit
    def test_extract_fit_score(self, analysis_service):
        """Test extracting fit score from analysis"""
        fit_analysis = """
        Overall Assessment:
        Fit Rating: Good
        Match Score: 75/100
        
        The candidate shows good alignment...
        """
        
        overall_fit, match_score = analysis_service._extract_fit_score(fit_analysis)
        
        assert overall_fit == "Good"
        assert match_score == 75

    @pytest.mark.unit
    def test_extract_fit_score_missing(self, analysis_service):
        """Test extracting fit score when missing"""
        fit_analysis = "No score information here"
        
        overall_fit, match_score = analysis_service._extract_fit_score(fit_analysis)
        
        assert overall_fit == "Unknown"
        assert match_score == 0

    @pytest.mark.unit
    def test_summarize_gaps(self, analysis_service):
        """Test summarizing gaps"""
        gap_analysis = """
        ### CRITICAL GAPS
        - Missing Skill: Kubernetes
        - Missing Certification: AWS Solutions Architect
        
        ### IMPORTANT GAPS
        - Limited experience with: Microservices
        """
        
        summary = analysis_service._summarize_gaps(gap_analysis)
        
        assert "Kubernetes" in summary or "Missing Skill" in summary
        assert len(summary) > 0

    @pytest.mark.unit
    def test_summarize_gaps_empty(self, analysis_service):
        """Test summarizing gaps when none exist"""
        gap_analysis = "No gaps identified"
        
        summary = analysis_service._summarize_gaps(gap_analysis)
        
        assert "No significant gaps" in summary

    @pytest.mark.unit
    def test_extract_critical_gaps(self, analysis_service):
        """Test extracting critical gaps list"""
        gap_analysis = """
        ### CRITICAL GAPS
        - Kubernetes: Not mentioned in resume
        - AWS Certification: Missing
        """
        
        gaps = analysis_service._extract_critical_gaps(gap_analysis)
        
        assert len(gaps) > 0
        assert any("Kubernetes" in gap or "AWS" in gap for gap in gaps)

    @pytest.mark.unit
    def test_extract_top_strengths(self, analysis_service):
        """Test extracting top strengths"""
        strengths_analysis = """
        ### Strength 1: Strong Python experience
        ### Strength 2: Excellent problem-solving skills
        ### Strength 3: Good team leadership
        """
        
        strengths = analysis_service._extract_top_strengths(strengths_analysis)
        
        assert len(strengths) == 3
        assert "Python" in strengths[0] or "experience" in strengths[0]

    @pytest.mark.integration
    @pytest.mark.slow
    @patch('app.services.analysis_service.LLMService')
    async def test_analyze_resume_mock_llm(
        self, 
        mock_llm_class, 
        analysis_service, 
        sample_resume_text, 
        sample_job_description
    ):
        """Test full analysis with mocked LLM"""
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate = AsyncMock(side_effect=[
            "Fit Rating: Good\nMatch Score: 75",
            "### CRITICAL GAPS\n- Missing: Kubernetes",
            "### Strength 1: Python expertise",
            "Coaching advice: Focus on learning Kubernetes"
        ])
        analysis_service.llm_service = mock_llm
        
        result = await analysis_service.analyze_resume(
            sample_resume_text,
            sample_job_description,
            model_params={'temperature': 0.5, 'max_tokens': 800}
        )
        
        assert 'fit_analysis' in result
        assert 'gap_analysis' in result
        assert 'strengths_analysis' in result
        assert 'coaching_advice' in result
        assert 'summary' in result
        
        assert result['summary']['overall_fit'] in ['Poor', 'Fair', 'Good', 'Excellent', 'Unknown']
        assert 0 <= result['summary']['match_score'] <= 100
        
        # Verify LLM was called
        assert mock_llm.generate.call_count == 4

    @pytest.mark.unit
    def test_summarize_strengths(self, analysis_service):
        """Test summarizing strengths"""
        strengths_analysis = """
        ### Strength 1: Python expertise
        ### Strength 2: React development
        ### Strength 3: Team leadership
        """
        
        summary = analysis_service._summarize_strengths(strengths_analysis)
        
        assert "Python" in summary or "expertise" in summary
        assert len(summary) > 0
