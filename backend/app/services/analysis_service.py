"""
Analysis service for resume-job matching analysis
"""
import re
import time
from typing import Dict, List, Optional
from app.services.llm_service import LLMService
from app.services.data_processor import DataProcessor
from app.chains.prompts import get_prompt
from app.logger import get_logger

logger = get_logger("analysis_service")


class AnalysisService:
    """Service for analyzing resume-job fit"""

    def __init__(self):
        self.llm_service = LLMService()
        self.data_processor = DataProcessor()

    async def analyze_resume(
        self,
        resume_text: str,
        job_description: str,
        model_params: Optional[Dict] = None
    ) -> Dict:
        """
        Perform complete resume analysis

        Args:
            resume_text: Cleaned resume text
            job_description: Job description text
            model_params: Optional model parameters (temperature, max_tokens)

        Returns:
            Dictionary with complete analysis
        """
        total_start_time = time.time()
        logger.info("=" * 50)
        logger.info("Starting resume analysis")
        logger.info(f"Resume length: {len(resume_text)} chars, Job description length: {len(job_description)} chars")
        
        # Handle long documents
        resume_processed = self._handle_long_text(resume_text, max_tokens=1500)
        job_processed = self._handle_long_text(job_description, max_tokens=1500)
        logger.debug(f"Processed resume: {len(resume_processed)} chars, job: {len(job_processed)} chars")

        # Extract model parameters
        temperature = model_params.get('temperature', 0.5) if model_params else 0.5
        max_tokens = model_params.get('max_tokens', 800) if model_params else 800
        logger.debug(f"Model params: temperature={temperature}, max_tokens={max_tokens}")

        # Run analyses in sequence
        logger.info("[1/4] Running fit analysis...")
        step_start = time.time()
        fit_analysis = await self._run_fit_analysis(
            resume_processed, job_processed, temperature, max_tokens
        )
        logger.info(f"[1/4] Fit analysis completed in {time.time() - step_start:.2f}s")

        logger.info("[2/4] Running gap analysis...")
        step_start = time.time()
        gap_analysis = await self._run_gap_analysis(
            resume_processed, job_processed, temperature, max_tokens
        )
        logger.info(f"[2/4] Gap analysis completed in {time.time() - step_start:.2f}s")

        logger.info("[3/4] Running strengths analysis...")
        step_start = time.time()
        strengths_analysis = await self._run_strengths_analysis(
            resume_processed, job_processed, temperature, max_tokens
        )
        logger.info(f"[3/4] Strengths analysis completed in {time.time() - step_start:.2f}s")

        # Extract key information
        overall_fit, match_score = self._extract_fit_score(fit_analysis)
        gaps_summary = self._summarize_gaps(gap_analysis)
        strengths_summary = self._summarize_strengths(strengths_analysis)
        logger.debug(f"Extracted: fit={overall_fit}, score={match_score}")

        # Generate coaching advice
        logger.info("[4/4] Generating coaching advice...")
        step_start = time.time()
        coaching_advice = await self._generate_coaching_advice(
            overall_fit, match_score, gaps_summary, strengths_summary,
            temperature, max_tokens
        )
        logger.info(f"[4/4] Coaching advice completed in {time.time() - step_start:.2f}s")

        total_time = time.time() - total_start_time
        logger.info(f"Analysis completed successfully in {total_time:.2f}s")
        logger.info(f"Result: {overall_fit} fit, {match_score}% match score")
        logger.info("=" * 50)
        
        return {
            'fit_analysis': fit_analysis,
            'gap_analysis': gap_analysis,
            'strengths_analysis': strengths_analysis,
            'coaching_advice': coaching_advice,
            'summary': {
                'overall_fit': overall_fit,
                'match_score': match_score,
                'critical_gaps': self._extract_critical_gaps(gap_analysis),
                'top_strengths': self._extract_top_strengths(strengths_analysis)
            }
        }

    async def _run_fit_analysis(
        self, resume: str, job: str, temperature: float, max_tokens: int
    ) -> str:
        """Run overall fit analysis"""
        prompt = get_prompt('fit_analysis', resume_text=resume, job_description=job)
        return await self.llm_service.generate(prompt, temperature, max_tokens)

    async def _run_gap_analysis(
        self, resume: str, job: str, temperature: float, max_tokens: int
    ) -> str:
        """Run skill gap analysis"""
        prompt = get_prompt('gap_analysis', resume_text=resume, job_description=job)
        return await self.llm_service.generate(prompt, temperature, max_tokens)

    async def _run_strengths_analysis(
        self, resume: str, job: str, temperature: float, max_tokens: int
    ) -> str:
        """Run strengths identification"""
        prompt = get_prompt('strengths', resume_text=resume, job_description=job)
        return await self.llm_service.generate(prompt, temperature, max_tokens)

    async def _generate_coaching_advice(
        self,
        overall_fit: str,
        match_score: int,
        gaps_summary: str,
        strengths_summary: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate coaching advice"""
        prompt = get_prompt(
            'coaching',
            overall_fit=overall_fit,
            match_score=match_score,
            gaps_summary=gaps_summary,
            strengths_summary=strengths_summary
        )
        return await self.llm_service.generate(prompt, temperature, max_tokens)

    def _handle_long_text(self, text: str, max_tokens: int) -> str:
        """Handle long documents by truncating or summarizing"""
        estimated_tokens = self.data_processor.count_tokens(text)

        if estimated_tokens <= max_tokens:
            return text

        # Simple truncation for now (could be improved with summarization)
        max_chars = max_tokens * 4
        if len(text) > max_chars:
            return text[:max_chars] + "\n\n[Document truncated for length...]"

        return text

    def _extract_fit_score(self, fit_analysis: str) -> tuple:
        """Extract overall fit rating and match score from analysis"""
        # Extract fit rating
        fit_match = re.search(r'Fit Rating:\s*(Poor|Fair|Good|Excellent)', fit_analysis, re.I)
        overall_fit = fit_match.group(1) if fit_match else "Unknown"

        # Extract match score
        score_match = re.search(r'Match Score:\s*(\d+)(?:/100)?', fit_analysis)
        match_score = int(score_match.group(1)) if score_match else 0

        return overall_fit, match_score

    def _summarize_gaps(self, gap_analysis: str) -> str:
        """Extract summary of critical and important gaps"""
        lines = gap_analysis.split('\n')
        summary_lines = []
        in_critical = False
        in_important = False

        for line in lines:
            if 'CRITICAL GAPS' in line.upper():
                in_critical = True
                in_important = False
                continue
            elif 'IMPORTANT GAPS' in line.upper():
                in_critical = False
                in_important = True
                continue
            elif 'MINOR GAPS' in line.upper():
                break

            if (in_critical or in_important) and line.strip().startswith('-'):
                summary_lines.append(line.strip())
                if len(summary_lines) >= 5:  # Limit to top 5
                    break

        return '\n'.join(summary_lines) if summary_lines else "No significant gaps identified"

    def _summarize_strengths(self, strengths_analysis: str) -> str:
        """Extract summary of top strengths"""
        strengths = re.findall(r'### Strength \d+: (.+)', strengths_analysis)
        return ', '.join(strengths[:3]) if strengths else "Various relevant strengths"

    def _extract_critical_gaps(self, gap_analysis: str) -> List[str]:
        """Extract list of critical gaps"""
        critical_section = re.search(
            r'### CRITICAL GAPS(.*?)(?:###|$)',
            gap_analysis,
            re.DOTALL
        )
        if not critical_section:
            return []

        # Extract skill names from bullet points
        gaps = re.findall(r'-\s*([^:]+):', critical_section.group(1))
        return [gap.strip() for gap in gaps]

    def _extract_top_strengths(self, strengths_analysis: str) -> List[str]:
        """Extract list of top strengths"""
        strengths = re.findall(r'### Strength \d+: (.+)', strengths_analysis)
        return [s.strip() for s in strengths]
