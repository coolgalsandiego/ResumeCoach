"""
Data processing service for text cleaning, skill extraction, etc.
"""
import re
from typing import Dict, List
import spacy


class DataProcessor:
    """Process and extract information from text"""

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, use blank English model
            self.nlp = spacy.blank("en")

        self.skill_keywords = self._load_skill_keywords()

    def _load_skill_keywords(self) -> List[str]:
        """Load comprehensive list of technical skills"""
        return [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php',
            'go', 'rust', 'kotlin', 'swift', 'scala', 'r', 'matlab', 'perl',
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'vue.js', 'node.js', 'express',
            'django', 'flask', 'fastapi', 'spring', 'asp.net', 'jquery',
            # Data & ML
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'data science', 'big data', 'data analysis',
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'terraform',
            'jenkins', 'git', 'github', 'gitlab', 'ci/cd', 'linux', 'bash',
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'dynamodb', 'cassandra', 'oracle', 'sql server',
            # Other
            'api', 'rest', 'restful', 'graphql', 'microservices', 'agile', 'scrum',
            'tdd', 'testing', 'unit testing', 'integration testing'
        ]

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)\:\;]', '', text)
        return text.strip()

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        if not text:
            return []

        text_lower = text.lower()
        found_skills = []

        for skill in self.skill_keywords:
            if skill in text_lower:
                found_skills.append(skill)

        return list(set(found_skills))

    def extract_years_of_experience(self, text: str) -> int:
        """Extract years of experience from text"""
        if not text:
            return 0

        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?',
            r'(\d+)\s*to\s*(\d+)\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]

        max_years = 0
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        # Take the upper bound
                        years = max([int(y) for y in match if y.isdigit()])
                    else:
                        years = int(match)
                    max_years = max(max_years, years)

        return max_years

    def identify_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract resume sections"""
        if not text:
            return {}

        sections = {}

        # Define section headers
        section_patterns = {
            'summary': r'(?:professional\s+)?(?:summary|objective|profile)',
            'experience': r'(?:work\s+)?(?:experience|employment\s+history)',
            'education': r'(?:education|academic\s+background|qualifications)',
            'skills': r'(?:skills|technical\s+skills|competencies|expertise)',
            'projects': r'(?:projects|portfolio)',
            'certifications': r'(?:certifications?|licenses?|credentials)',
            'achievements': r'(?:achievements|awards|accomplishments)'
        }

        # Split text into lines
        lines = text.split('\n')
        current_section = None
        section_content = []

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            line_lower = line_stripped.lower()

            # Check if line is a section header
            matched_section = None
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line_lower):
                    matched_section = section_name
                    break

            if matched_section:
                # Save previous section
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                # Start new section
                current_section = matched_section
                section_content = []
            elif current_section:
                section_content.append(line_stripped)

        # Save last section
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)

        return sections

    def chunk_long_text(self, text: str, max_tokens: int = 2000) -> List[str]:
        """Chunk long text into smaller pieces"""
        if not text:
            return []

        # Rough approximation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4

        if len(text) <= max_chars:
            return [text]

        # Split by paragraphs
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para_length = len(para)
            if current_length + para_length > max_chars:
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length

        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def summarize_long_text(self, text: str, max_length: int = 1000) -> str:
        """Create a simple extractive summary of long text"""
        if len(text) <= max_length:
            return text

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)

        # Take first and last sentences, and some from middle
        if len(sentences) <= 5:
            return text[:max_length]

        summary_sentences = [
            sentences[0],  # First sentence
            *sentences[len(sentences)//3:len(sentences)//3+2],  # Some middle
            sentences[-1]  # Last sentence
        ]

        summary = '. '.join([s.strip() for s in summary_sentences if s.strip()])

        if len(summary) > max_length:
            return summary[:max_length] + "..."

        return summary

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from text"""
        contact_info = {}

        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]

        # Phone
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = phones[0] if isinstance(phones[0], str) else ''.join(phones[0])

        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            contact_info['linkedin'] = linkedin[0]

        # GitHub
        github_pattern = r'github\.com/[\w-]+'
        github = re.findall(github_pattern, text.lower())
        if github:
            contact_info['github'] = github[0]

        return contact_info

    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4
