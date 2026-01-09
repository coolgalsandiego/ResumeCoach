"""
Resume parsing service supporting PDF, DOCX, and TXT formats
"""
import io
from typing import Dict
import PyPDF2
import pdfplumber
import docx
from app.services.data_processor import DataProcessor


class ResumeParser:
    """Parse resumes and extract structured information"""

    def __init__(self):
        self.data_processor = DataProcessor()

    async def parse_file(self, file_content: bytes, filename: str) -> Dict:
        """
        Parse resume file and extract structured information

        Args:
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Dictionary with parsed resume data
        """
        # Determine file type
        file_extension = filename.split('.')[-1].lower()

        # Extract text based on file type
        if file_extension == 'pdf':
            raw_text = self._parse_pdf(file_content)
        elif file_extension == 'docx':
            raw_text = self._parse_docx(file_content)
        elif file_extension == 'txt':
            raw_text = file_content.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        # Process text
        cleaned_text = self.data_processor.clean_text(raw_text)
        sections = self.data_processor.identify_sections(cleaned_text)
        skills = self.data_processor.extract_skills(cleaned_text)
        years_exp = self.data_processor.extract_years_of_experience(cleaned_text)
        contact_info = self.data_processor.extract_contact_info(cleaned_text)

        return {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'sections': sections,
            'skills': skills,
            'years_experience': years_exp,
            'contact_info': contact_info,
            'metadata': {
                'filename': filename,
                'file_type': file_extension,
                'length': len(cleaned_text),
                'word_count': len(cleaned_text.split()),
                'section_count': len(sections)
            }
        }

    def _parse_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF"""
        try:
            # Method 1: pdfplumber (better for complex layouts)
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    return text
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")

        # Fallback to PyPDF2
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")

    def _parse_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            raise Exception(f"Failed to parse DOCX: {str(e)}")

    def get_resume_summary(self, parsed_resume: Dict) -> str:
        """Generate a brief summary of the resume"""
        skills = parsed_resume.get('skills', [])
        years_exp = parsed_resume.get('years_experience', 0)
        sections = parsed_resume.get('sections', {})

        summary_parts = []

        if years_exp > 0:
            summary_parts.append(f"{years_exp}+ years of experience")

        if skills:
            top_skills = skills[:5]
            summary_parts.append(f"Skills: {', '.join(top_skills)}")

        if 'education' in sections:
            summary_parts.append("Education details available")

        return "; ".join(summary_parts) if summary_parts else "Resume parsed successfully"
