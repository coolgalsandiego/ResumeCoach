# Resume Coach - Step-by-Step Implementation Guide

## Overview

This guide provides a detailed, phase-by-phase approach to building the Resume Coach application. Each phase is designed to be completed sequentially, with clear milestones and deliverables.

**Estimated Total Time**: 4-6 weeks (depending on experience level)

---

## Table of Contents

1. [Phase 0: Environment Setup & Prerequisites](#phase-0-environment-setup--prerequisites)
2. [Phase 1: Data Collection & EDA](#phase-1-data-collection--eda)
3. [Phase 2: Initial LLM Experimentation](#phase-2-initial-llm-experimentation)
4. [Phase 3: Backend Development](#phase-3-backend-development)
5. [Phase 4: LLM Deployment on SageMaker](#phase-4-llm-deployment-on-sagemaker)
6. [Phase 5: Frontend Development](#phase-5-frontend-development)
7. [Phase 6: Integration & Testing](#phase-6-integration--testing)
8. [Phase 7: AWS Deployment](#phase-7-aws-deployment)
9. [Phase 8: Documentation & Final Testing](#phase-8-documentation--final-testing)

---

## Phase 0: Environment Setup & Prerequisites

### Duration: 1-2 days

### Objectives
- Set up development environment
- Configure AWS account and services
- Install necessary tools
- Create project structure

### Tasks

#### 0.1 Install Development Tools

**Required Software**:
```bash
# Python 3.10+
python --version  # Should be 3.10 or higher

# Node.js 18+
node --version

# Docker
docker --version

# Git
git --version

# AWS CLI
aws --version
```

**Python Environment**:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 0.2 Configure AWS Account

**Steps**:
1. Create AWS account (if not exists)
2. Request educational credits (if applicable)
3. Configure AWS CLI:
```bash
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format: json
```

4. Create IAM role for SageMaker:
```bash
aws iam create-role \
  --role-name SageMakerExecutionRole \
  --assume-role-policy-document file://trust-policy.json

# trust-policy.json:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

# Attach policies
aws iam attach-role-policy \
  --role-name SageMakerExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy \
  --role-name SageMakerExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

#### 0.3 Create Project Structure

```bash
# Create directory structure
mkdir -p ResumeCoach/{backend,frontend,data,notebooks,deployment,docs}

# Backend structure
cd ResumeCoach/backend
mkdir -p {app,tests}/{api,services,models,utils,chains}
touch app/__init__.py app/main.py

# Frontend structure
cd ../frontend
npx create-react-app . --template typescript
mkdir -p src/{components,pages,services,store,types}

# Data structure
cd ../data
mkdir -p {raw,processed,job_postings,resumes,embeddings}

# Notebooks structure
cd ../notebooks
touch 01_eda.ipynb 02_prompt_experiments.ipynb 03_model_testing.ipynb

# Deployment structure
cd ../deployment
mkdir -p {docker,terraform,scripts}
touch docker/{Dockerfile.backend,Dockerfile.frontend,docker-compose.yml}

# Docs structure
cd ../docs
touch {architecture.md,api_docs.md,deployment_guide.md,user_manual.md}
```

#### 0.4 Initialize Git Repository

```bash
cd ResumeCoach
git init
git add .
git commit -m "Initial project structure"

# Create .gitignore
cat > .gitignore << EOF
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg-info/
dist/
build/

# Node
node_modules/
build/
.env.local

# IDE
.vscode/
.idea/
*.swp

# AWS
.aws/
*.pem

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Models
models/*.bin
models/*.safetensors

# Environment
.env
*.env

# Logs
*.log
EOF

git add .gitignore
git commit -m "Add gitignore"
```

#### 0.5 Install Dependencies

**Backend Requirements** (`backend/requirements.txt`):
```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# AWS SDK
boto3==1.29.7
sagemaker==2.198.0

# LangChain
langchain==0.0.340
langchain-community==0.0.3

# Document Processing
PyPDF2==3.0.1
pdfplumber==0.10.3
python-docx==1.1.0
python-magic==0.4.27

# NLP
spacy==3.7.2
transformers==4.35.2
sentence-transformers==2.2.2

# Vector Store
faiss-cpu==1.7.4
chromadb==0.4.18

# Database
boto3-dynamodb==0.1.0

# Utilities
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Monitoring
prometheus-client==0.19.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

Install:
```bash
cd backend
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

**Frontend Dependencies**:
```bash
cd frontend
npm install axios react-router-dom @reduxjs/toolkit react-redux
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
npm install react-dropzone react-markdown recharts
npm install --save-dev @types/react-router-dom
```

### Deliverables
- ✅ Fully configured development environment
- ✅ AWS account with proper IAM roles
- ✅ Project structure created
- ✅ All dependencies installed
- ✅ Git repository initialized

---

## Phase 1: Data Collection & EDA

### Duration: 3-4 days

### Objectives
- Collect resume samples and job postings
- Perform exploratory data analysis
- Understand data patterns and requirements
- Prepare data for model training/fine-tuning

### Tasks

#### 1.1 Data Collection

**1.1.1 Job Postings Dataset**

**Option A: Use Kaggle Datasets** (Recommended)
```bash
# Install Kaggle CLI
pip install kaggle

# Download job postings dataset
# Example: LinkedIn Job Postings dataset
kaggle datasets download -d arshkon/linkedin-job-postings
unzip linkedin-job-postings.zip -d data/raw/job_postings/

# Alternative: Indeed Job Postings
# Search on Kaggle: "indeed job postings"
```

**Option B: Create Custom Dataset**
- Manually collect 50-100 job postings from LinkedIn/Indeed
- Save as CSV with columns: job_id, title, company, description, requirements, location

**1.1.2 Resume Samples**

**Sources**:
1. Use your own resume and those of friends/colleagues (with permission)
2. Generate synthetic resumes using templates
3. Use public resume datasets (ensure compliance with privacy laws)

**Format**: Collect at least 20-30 resumes in PDF, DOCX, and TXT formats

**Storage Structure**:
```
data/raw/resumes/
├── pdf/
│   ├── resume_001.pdf
│   ├── resume_002.pdf
│   └── ...
├── docx/
│   ├── resume_001.docx
│   └── ...
└── txt/
    ├── resume_001.txt
    └── ...
```

#### 1.2 Exploratory Data Analysis

**1.2.1 Create EDA Notebook** (`notebooks/01_eda.ipynb`)

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# Load job postings
jobs_df = pd.read_csv('../data/raw/job_postings/postings.csv')

# Display basic info
print("Dataset Shape:", jobs_df.shape)
print("\nColumn Names:", jobs_df.columns.tolist())
print("\nData Types:\n", jobs_df.dtypes)
print("\nMissing Values:\n", jobs_df.isnull().sum())

# Display sample
jobs_df.head()
```

**1.2.2 Analyze Job Postings**

```python
# Analysis 1: Job Title Distribution
title_counts = jobs_df['title'].value_counts().head(20)
plt.figure(figsize=(12, 6))
title_counts.plot(kind='barh')
plt.title('Top 20 Job Titles')
plt.xlabel('Count')
plt.tight_layout()
plt.show()

# Analysis 2: Description Length Distribution
jobs_df['desc_length'] = jobs_df['description'].str.len()
plt.figure(figsize=(10, 6))
jobs_df['desc_length'].hist(bins=50)
plt.title('Job Description Length Distribution')
plt.xlabel('Character Count')
plt.ylabel('Frequency')
plt.show()

print(f"Mean description length: {jobs_df['desc_length'].mean():.0f} characters")
print(f"Median description length: {jobs_df['desc_length'].median():.0f} characters")
print(f"Max description length: {jobs_df['desc_length'].max():.0f} characters")

# Analysis 3: Common Skills/Keywords
def extract_skills(text):
    """Extract common technical skills from text"""
    skills = [
        'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'docker',
        'kubernetes', 'react', 'node.js', 'machine learning', 'data science',
        'tensorflow', 'pytorch', 'nlp', 'computer vision', 'agile', 'scrum'
    ]
    found_skills = []
    text_lower = text.lower()
    for skill in skills:
        if skill in text_lower:
            found_skills.append(skill)
    return found_skills

jobs_df['skills'] = jobs_df['description'].apply(extract_skills)
all_skills = [skill for skills_list in jobs_df['skills'] for skill in skills_list]
skill_counts = Counter(all_skills)

plt.figure(figsize=(12, 6))
pd.Series(skill_counts).sort_values(ascending=True).tail(20).plot(kind='barh')
plt.title('Most In-Demand Skills')
plt.xlabel('Frequency')
plt.tight_layout()
plt.show()

# Analysis 4: Experience Level Distribution
def classify_experience_level(description):
    """Classify experience level from job description"""
    desc_lower = description.lower()
    if 'senior' in desc_lower or '5+ years' in desc_lower or '7+ years' in desc_lower:
        return 'Senior'
    elif 'junior' in desc_lower or 'entry level' in desc_lower or '0-2 years' in desc_lower:
        return 'Junior'
    else:
        return 'Mid-Level'

jobs_df['experience_level'] = jobs_df['description'].apply(classify_experience_level)
jobs_df['experience_level'].value_counts().plot(kind='pie', autopct='%1.1f%%')
plt.title('Experience Level Distribution')
plt.ylabel('')
plt.show()
```

**1.2.3 Analyze Resume Data**

```python
import os
from PyPDF2 import PdfReader
import docx

def load_resumes(directory):
    """Load all resumes from directory"""
    resumes = []

    # Load PDFs
    pdf_dir = os.path.join(directory, 'pdf')
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            try:
                reader = PdfReader(os.path.join(pdf_dir, filename))
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                resumes.append({'filename': filename, 'text': text, 'format': 'pdf'})
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    # Load DOCX
    docx_dir = os.path.join(directory, 'docx')
    for filename in os.listdir(docx_dir):
        if filename.endswith('.docx'):
            try:
                doc = docx.Document(os.path.join(docx_dir, filename))
                text = "\n".join([para.text for para in doc.paragraphs])
                resumes.append({'filename': filename, 'text': text, 'format': 'docx'})
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    return pd.DataFrame(resumes)

# Load resumes
resumes_df = load_resumes('../data/raw/resumes')

# Analysis 1: Resume Length Distribution
resumes_df['length'] = resumes_df['text'].str.len()
plt.figure(figsize=(10, 6))
resumes_df['length'].hist(bins=30)
plt.title('Resume Length Distribution')
plt.xlabel('Character Count')
plt.ylabel('Frequency')
plt.show()

# Analysis 2: Common Sections
def identify_sections(text):
    """Identify common resume sections"""
    sections = {
        'experience': bool(re.search(r'experience|work history', text, re.I)),
        'education': bool(re.search(r'education|academic', text, re.I)),
        'skills': bool(re.search(r'skills|technical skills', text, re.I)),
        'projects': bool(re.search(r'projects|portfolio', text, re.I)),
        'certifications': bool(re.search(r'certifications|licenses', text, re.I)),
    }
    return sections

section_data = resumes_df['text'].apply(identify_sections)
section_df = pd.DataFrame(section_data.tolist())
section_presence = section_df.sum() / len(section_df) * 100

plt.figure(figsize=(10, 6))
section_presence.plot(kind='bar')
plt.title('Resume Section Presence (%)')
plt.ylabel('Percentage of Resumes')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

**1.2.4 Key Insights Documentation**

Create `docs/eda_insights.md`:

```markdown
# EDA Insights

## Job Postings Dataset

- **Total job postings**: [NUMBER]
- **Average description length**: [NUMBER] characters
- **Most common job titles**: [LIST TOP 5]
- **Most in-demand skills**: [LIST TOP 10]
- **Experience level distribution**: Junior (X%), Mid (Y%), Senior (Z%)

## Resume Dataset

- **Total resumes**: [NUMBER]
- **Average resume length**: [NUMBER] characters
- **Common sections**: Experience (X%), Education (Y%), Skills (Z%)
- **Format distribution**: PDF (X%), DOCX (Y%), TXT (Z%)

## Key Findings

1. **Context Length Considerations**:
   - X% of job descriptions exceed 2000 characters
   - Y% of resumes exceed 3000 characters
   - **Implication**: Need document summarization for long inputs

2. **Skill Extraction**:
   - Identified [N] common technical skills
   - Skills appear in [location] sections of resumes/job descriptions
   - **Implication**: Can use regex/NLP for skill matching

3. **Section Structure**:
   - Most resumes follow standard structure (Experience → Education → Skills)
   - Some resumes have non-standard sections
   - **Implication**: Need robust section detection algorithm

## Recommendations for Model

1. Implement intelligent chunking for documents > 2000 tokens
2. Create skill taxonomy for better matching
3. Train section classifier for better resume parsing
4. Use extractive summarization for long documents
```

#### 1.3 Data Preprocessing

**1.3.1 Create Data Processing Pipeline**

Create `backend/app/services/data_processor.py`:

```python
import re
from typing import Dict, List
import spacy

class DataProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.skill_keywords = self._load_skill_keywords()

    def _load_skill_keywords(self) -> List[str]:
        """Load comprehensive list of skills"""
        return [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php',
            'go', 'rust', 'kotlin', 'swift', 'scala', 'r',
            # Frameworks & Libraries
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
            'spring', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas',
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
            'git', 'ci/cd', 'linux', 'bash',
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'dynamodb', 'cassandra',
            # Concepts
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'data science', 'big data', 'etl', 'api', 'rest', 'graphql',
            'microservices', 'agile', 'scrum', 'tdd'
        ]

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)]', '', text)
        return text.strip()

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        text_lower = text.lower()
        found_skills = []
        for skill in self.skill_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        return list(set(found_skills))

    def extract_years_of_experience(self, text: str) -> int:
        """Extract years of experience from text"""
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?',
            r'(\d+)\s*to\s*(\d+)\s*years?'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                if isinstance(matches[0], tuple):
                    return int(matches[0][1])  # Take upper bound
                return int(matches[0])
        return 0

    def identify_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract resume sections"""
        sections = {}

        # Define section headers
        section_patterns = {
            'experience': r'(?:work\s+)?experience|employment\s+history',
            'education': r'education|academic\s+background',
            'skills': r'skills|technical\s+skills|competencies',
            'projects': r'projects|portfolio',
            'certifications': r'certifications?|licenses?',
            'summary': r'summary|objective|profile'
        }

        # Split text into lines
        lines = text.split('\n')
        current_section = None
        section_content = []

        for line in lines:
            line_lower = line.lower().strip()

            # Check if line is a section header
            matched_section = None
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line_lower):
                    matched_section = section_name
                    break

            if matched_section:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(section_content)
                # Start new section
                current_section = matched_section
                section_content = []
            elif current_section:
                section_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(section_content)

        return sections

    def chunk_long_text(self, text: str, max_tokens: int = 2000) -> List[str]:
        """Chunk long text into smaller pieces"""
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
```

**1.3.2 Test Data Processing**

Create `notebooks/02_data_processing_test.ipynb`:

```python
from backend.app.services.data_processor import DataProcessor

processor = DataProcessor()

# Test with sample resume
sample_resume = """
John Doe
Software Engineer

EXPERIENCE
Senior Software Engineer at TechCorp (2020-Present)
- Developed microservices using Python and FastAPI
- Deployed applications on AWS using Docker and Kubernetes
- Led team of 5 engineers

Software Engineer at StartupXYZ (2018-2020)
- Built React applications
- Worked with PostgreSQL and MongoDB

EDUCATION
BS in Computer Science, MIT (2018)

SKILLS
Python, JavaScript, React, AWS, Docker, Kubernetes, PostgreSQL
"""

# Test cleaning
cleaned = processor.clean_text(sample_resume)
print("Cleaned Text Length:", len(cleaned))

# Test skill extraction
skills = processor.extract_skills(sample_resume)
print("\nExtracted Skills:", skills)

# Test section identification
sections = processor.identify_sections(sample_resume)
print("\nIdentified Sections:", list(sections.keys()))
for section, content in sections.items():
    print(f"\n{section.upper()}:")
    print(content[:200])  # Print first 200 chars

# Test years of experience
years = processor.extract_years_of_experience(sample_resume)
print(f"\nEstimated Years of Experience: {years}")
```

#### 1.4 Prepare Fine-tuning Dataset

**1.4.1 Create Training Data Format**

Create `notebooks/03_prepare_finetuning_data.ipynb`:

```python
import json
import random
from typing import List, Dict

def create_training_example(resume: str, job_description: str) -> Dict:
    """
    Create a training example in the format expected by Llama 2
    """
    # Format: instruction-input-output
    return {
        "instruction": "You are a career coach. Analyze how well this resume matches the job description.",
        "input": f"Resume:\n{resume}\n\nJob Description:\n{job_description}",
        "output": "This will be replaced with human-annotated coaching advice"
    }

# Load your data
resumes = []  # Load your resumes
jobs = []     # Load your job descriptions

# Create pairs
training_data = []
for resume in resumes[:50]:  # Use first 50 resumes
    # Randomly pair with jobs
    job = random.choice(jobs)
    example = create_training_example(resume, job)
    training_data.append(example)

# Save in JSONL format
with open('../data/processed/finetuning_data.jsonl', 'w') as f:
    for example in training_data:
        f.write(json.dumps(example) + '\n')

print(f"Created {len(training_data)} training examples")
```

**Note**: For the actual project, you would need to manually annotate these examples with high-quality coaching advice, or use GPT-4 to generate initial annotations that you then refine.

### Deliverables
- ✅ Collected dataset of resumes and job postings
- ✅ Comprehensive EDA with visualizations
- ✅ Documentation of key insights
- ✅ Data processing pipeline implemented
- ✅ Fine-tuning dataset prepared (structure, not fully annotated)
- ✅ Clear understanding of data characteristics and challenges

---

## Phase 2: Initial LLM Experimentation

### Duration: 3-4 days

### Objectives
- Experiment with different prompts
- Test with OpenAI API or Replicate (for rapid iteration)
- Develop and refine prompt templates
- Establish baseline performance
- Document prompt engineering process

### Tasks

#### 2.1 Set Up Experimentation Environment

**2.1.1 Configure API Access**

Create `backend/.env`:
```env
# OpenAI (for quick experiments)
OPENAI_API_KEY=your_openai_key_here

# Replicate (alternative)
REPLICATE_API_TOKEN=your_replicate_token_here

# Model settings
DEFAULT_MODEL=gpt-3.5-turbo
DEFAULT_TEMPERATURE=0.5
DEFAULT_MAX_TOKENS=800
```

**2.1.2 Create Experiment Tracking Notebook**

Create `notebooks/04_prompt_experiments.ipynb`:

```python
import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv('../backend/.env')
openai.api_key = os.getenv('OPENAI_API_KEY')

class PromptExperiment:
    def __init__(self):
        self.experiments = []

    def run_experiment(
        self,
        name: str,
        prompt_template: str,
        resume: str,
        job_description: str,
        temperature: float = 0.5,
        model: str = "gpt-3.5-turbo"
    ):
        """Run a single experiment"""
        # Fill in the prompt
        prompt = prompt_template.format(
            resume=resume,
            job_description=job_description
        )

        # Call API
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert career coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=1000
        )

        result = {
            "experiment_name": name,
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "temperature": temperature,
            "prompt": prompt,
            "response": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens
        }

        self.experiments.append(result)
        return result

    def save_experiments(self, filename: str):
        """Save all experiments to file"""
        with open(filename, 'w') as f:
            json.dump(self.experiments, f, indent=2)

    def compare_experiments(self, exp_names: List[str]):
        """Compare results from multiple experiments"""
        for name in exp_names:
            exps = [e for e in self.experiments if e['experiment_name'] == name]
            if exps:
                print(f"\n{'='*80}")
                print(f"Experiment: {name}")
                print(f"{'='*80}")
                print(exps[0]['response'])

# Initialize
tracker = PromptExperiment()
```

#### 2.2 Design and Test Prompts

**2.2.1 Experiment 1: Basic Matching Prompt**

```python
# Load sample data
sample_resume = """
Jane Smith
Senior Data Scientist

EXPERIENCE
Senior Data Scientist at DataCorp (2020-Present)
- Built machine learning models for customer churn prediction (95% accuracy)
- Led team of 3 data scientists
- Technologies: Python, TensorFlow, AWS SageMaker, SQL

Data Scientist at AnalyticsCo (2018-2020)
- Developed NLP models for sentiment analysis
- Created data pipelines using Apache Spark

EDUCATION
MS in Data Science, Stanford University (2018)
BS in Statistics, UC Berkeley (2016)

SKILLS
Python, R, TensorFlow, PyTorch, SQL, AWS, Docker, Scikit-learn, Pandas
"""

sample_job = """
Title: Senior Machine Learning Engineer

Company: TechGiant Inc.

Requirements:
- 5+ years of experience in machine learning
- Strong programming skills in Python
- Experience with deep learning frameworks (TensorFlow/PyTorch)
- Experience deploying models to production (AWS/Azure)
- Experience with NLP is a plus
- Strong communication skills

Responsibilities:
- Design and implement ML models for recommendation systems
- Deploy models to production using cloud infrastructure
- Collaborate with cross-functional teams
- Mentor junior engineers
"""

# Experiment 1: Concise Prompt
prompt_v1 = """
Compare this resume to the job description and assess the candidate's fit.

Resume:
{resume}

Job Description:
{job_description}

Provide:
1. Overall fit rating (Poor/Fair/Good/Excellent)
2. Match score (0-100)
3. Brief explanation
"""

result1 = tracker.run_experiment(
    name="v1_concise",
    prompt_template=prompt_v1,
    resume=sample_resume,
    job_description=sample_job,
    temperature=0.3
)

print(result1['response'])
```

**2.2.2 Experiment 2: Detailed Structured Prompt**

```python
prompt_v2 = """
You are an expert technical recruiter with 15 years of experience.

Your task is to evaluate how well a candidate's resume matches a specific job description.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

EVALUATION CRITERIA:
1. Technical Skills Match (40%)
   - Required skills present in resume
   - Depth of experience with key technologies

2. Experience Level (30%)
   - Years of relevant experience
   - Leadership/mentorship experience
   - Project complexity

3. Domain Expertise (20%)
   - Industry experience relevance
   - Specific domain knowledge

4. Education & Credentials (10%)
   - Education level
   - Relevant certifications

OUTPUT FORMAT:
## Overall Assessment
- Fit Rating: [Poor/Fair/Good/Excellent]
- Match Score: [0-100]/100

## Detailed Analysis

### Technical Skills Match (X/40 points)
[Analysis]

### Experience Level (X/30 points)
[Analysis]

### Domain Expertise (X/20 points)
[Analysis]

### Education & Credentials (X/10 points)
[Analysis]

## Summary
[2-3 sentence summary]
"""

result2 = tracker.run_experiment(
    name="v2_structured",
    prompt_template=prompt_v2,
    resume=sample_resume,
    job_description=sample_job,
    temperature=0.3
)

print(result2['response'])
```

**2.2.3 Experiment 3: Few-Shot Learning**

```python
prompt_v3 = """
You are an expert career coach. Analyze how well a resume matches a job description.

EXAMPLE 1:
Resume: Software engineer with 3 years Python experience, built web apps with Django...
Job: Senior Python Developer, 5+ years required...
Analysis: FAIR FIT (60/100). Candidate has relevant Python skills but lacks seniority. Missing: 2 years experience, leadership, system design expertise.

EXAMPLE 2:
Resume: Data Scientist with 6 years exp, ML models, TensorFlow, AWS deployment...
Job: ML Engineer, 5+ years, production ML systems, cloud deployment...
Analysis: EXCELLENT FIT (90/100). Strong alignment. Has required years, ML expertise, cloud experience. Minor gap: no mention of specific deployment tools like Kubernetes.

NOW ANALYZE THIS CANDIDATE:

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

ANALYSIS:
"""

result3 = tracker.run_experiment(
    name="v3_fewshot",
    prompt_template=prompt_v3,
    resume=sample_resume,
    job_description=sample_job,
    temperature=0.4
)

print(result3['response'])
```

**2.2.4 Experiment 4: Chain-of-Thought Prompting**

```python
prompt_v4 = """
You are an expert career coach. Let's analyze this resume step by step.

RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

ANALYSIS PROCESS:

Step 1: Extract key requirements from job description
Think: What are the must-have skills, experiences, and qualifications?
[Your analysis]

Step 2: Extract candidate's qualifications from resume
Think: What are the candidate's key skills, years of experience, and achievements?
[Your analysis]

Step 3: Compare and identify matches
Think: Which requirements does the candidate clearly meet?
[Your analysis]

Step 4: Identify gaps
Think: What requirements are missing or weak in the resume?
[Your analysis]

Step 5: Assess overall fit
Think: Considering all factors, how well does this candidate fit?
[Your final assessment with score]
"""

result4 = tracker.run_experiment(
    name="v4_chain_of_thought",
    prompt_template=prompt_v4,
    resume=sample_resume,
    job_description=sample_job,
    temperature=0.4
)

print(result4['response'])
```

#### 2.3 Test Skill Gap Analysis Prompts

```python
gap_analysis_prompt = """
You are a technical talent assessor. Identify skill gaps between the candidate and job requirements.

CANDIDATE'S RESUME:
{resume}

JOB REQUIREMENTS:
{job_description}

TASK:
1. List all technical skills explicitly required in the job description
2. For each required skill, indicate:
   - ✓ if clearly present in resume (with evidence)
   - ~ if partially present or implied
   - ✗ if missing

3. Categorize gaps by priority:
   - CRITICAL: Must-have skills that are missing
   - IMPORTANT: Preferred skills that are missing
   - MINOR: Nice-to-have skills that are missing

4. For each gap, suggest:
   - How quickly it can be learned (Days/Weeks/Months)
   - Learning resources (courses, books, projects)

OUTPUT FORMAT:
## Skills Inventory

### Present Skills ✓
- [Skill]: [Evidence from resume]

### Partial Skills ~
- [Skill]: [What's present and what's missing]

### Missing Skills ✗
- [Skill]: [Why it's needed]

## Gap Analysis by Priority

### CRITICAL GAPS
[List with learning recommendations]

### IMPORTANT GAPS
[List with learning recommendations]

### MINOR GAPS
[List with learning recommendations]

## Recommendations
[Overall advice on addressing gaps]
"""

gap_result = tracker.run_experiment(
    name="gap_analysis_v1",
    prompt_template=gap_analysis_prompt,
    resume=sample_resume,
    job_description=sample_job,
    temperature=0.3
)

print(gap_result['response'])
```

#### 2.4 Test Strength Identification Prompts

```python
strength_prompt = """
You are a career strategist helping a candidate position themselves effectively.

CANDIDATE'S RESUME:
{resume}

TARGET JOB:
{job_description}

TASK:
Identify the candidate's UNIQUE STRENGTHS that make them stand out for THIS specific role.

CRITERIA FOR IDENTIFYING STRENGTHS:
1. Skills/experiences that are highly relevant to the job
2. Achievements with quantifiable results
3. Unique combinations of skills (e.g., technical + leadership)
4. Experiences that go beyond minimum requirements

AVOID:
- Generic statements ("good communicator")
- Skills that merely meet minimum requirements
- Strengths not relevant to this specific role

OUTPUT FORMAT:
## Top 5 Unique Strengths

### Strength 1: [Specific, compelling title]
**Evidence**: [Quote from resume or specific achievement]
**Why it matters**: [How this directly benefits the target role]
**How to highlight**: [Specific advice for cover letter/interview]

[Repeat for each strength]

## Positioning Statement
[Draft a 2-3 sentence "elevator pitch" for this candidate]
"""

strength_result = tracker.run_experiment(
    name="strength_identification_v1",
    prompt_template=strength_prompt,
    resume=sample_resume,
    job_description=sample_job,
    temperature=0.6
)

print(strength_result['response'])
```

#### 2.5 Temperature and Parameter Testing

```python
# Test different temperatures
temperatures = [0.1, 0.3, 0.5, 0.7, 0.9]

for temp in temperatures:
    result = tracker.run_experiment(
        name=f"temperature_test_{temp}",
        prompt_template=prompt_v2,  # Use structured prompt
        resume=sample_resume,
        job_description=sample_job,
        temperature=temp
    )
    print(f"\n{'='*80}")
    print(f"Temperature: {temp}")
    print(f"{'='*80}")
    print(result['response'][:500])  # Print first 500 chars

# Analysis: Which temperature gives best results?
# - Low (0.1-0.3): More consistent, factual, but may be repetitive
# - Medium (0.5-0.6): Good balance
# - High (0.7-0.9): More creative but potentially less accurate
```

#### 2.6 Document Prompt Engineering Process

Create `docs/prompt_engineering.md`:

```markdown
# Prompt Engineering Documentation

## Experimentation Process

### Methodology
1. Started with simple prompt
2. Iteratively added structure and detail
3. Tested different techniques (few-shot, chain-of-thought)
4. Compared outputs across experiments
5. Measured quality based on: relevance, accuracy, actionability, consistency

### Experiments Conducted

#### Experiment 1: Concise Prompt (v1)
- **Approach**: Simple, direct instruction
- **Results**: Basic output, lacks detail
- **Token usage**: ~300
- **Rating**: 3/5

#### Experiment 2: Structured Prompt (v2)
- **Approach**: Detailed evaluation framework with scoring
- **Results**: Comprehensive analysis, well-organized
- **Token usage**: ~600
- **Rating**: 4.5/5

#### Experiment 3: Few-Shot Learning (v3)
- **Approach**: Provided examples before actual task
- **Results**: Output format more consistent with examples
- **Token usage**: ~500
- **Rating**: 4/5

#### Experiment 4: Chain-of-Thought (v4)
- **Approach**: Step-by-step reasoning process
- **Results**: Transparent reasoning, detailed analysis
- **Token usage**: ~700
- **Rating**: 4.5/5

### Best Prompt Selection

**Winner**: Structured Prompt (v2) with temperature 0.3

**Rationale**:
- Most comprehensive output
- Consistent format for easy parsing
- Actionable insights
- Good balance of detail vs token usage

### Optimal Parameters

Based on testing:
- **Temperature**: 0.3-0.5 for analysis tasks (deterministic)
- **Temperature**: 0.6-0.7 for chat/creative tasks
- **Max tokens**: 500-800 for analysis, 300-500 for chat
- **Top-p**: 0.9-0.95

### Prompt Templates (Final Versions)

[Include your finalized prompts]

### Lessons Learned

1. **Specificity matters**: Detailed instructions yield better results
2. **Structure helps**: Asking for specific format improves consistency
3. **Context is key**: Providing role/persona improves relevance
4. **Temperature tuning**: Lower for factual, higher for creative
5. **Examples work**: Few-shot learning improves output quality
```

### Deliverables
- ✅ 10+ prompt experiments conducted and documented
- ✅ Finalized prompt templates for all major functions
- ✅ Optimal parameter settings identified
- ✅ Comprehensive prompt engineering documentation
- ✅ Baseline performance established

---

## Phase 3: Backend Development

### Duration: 5-7 days

### Objectives
- Build FastAPI backend with all required endpoints
- Implement document processing (PDF, DOCX parsing)
- Integrate LangChain for LLM orchestration
- Implement RAG for chat functionality
- Create session management and caching

### Tasks

#### 3.1 Set Up FastAPI Project Structure

Already created in Phase 0, now implement:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── resume.py
│   │   │   ├── jobs.py
│   │   │   ├── analysis.py
│   │   │   └── chat.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── resume_parser.py
│   │   ├── job_service.py
│   │   ├── llm_service.py
│   │   ├── analysis_service.py
│   │   ├── chat_service.py
│   │   └── data_processor.py  # Created in Phase 1
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── analysis_chain.py
│   │   ├── chat_chain.py
│   │   └── prompts.py         # Prompt templates
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py         # Pydantic models
│   │   └── database.py        # Database models
│   └── utils/
│       ├── __init__.py
│       ├── aws_utils.py
│       └── cache.py
├── tests/
│   ├── __init__.py
│   ├── test_resume_parser.py
│   └── test_api.py
├── .env
├── requirements.txt
└── pytest.ini
```

#### 3.2 Implement Core Services

**3.2.1 Configuration Management** (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Resume Coach"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"

    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # SageMaker
    SAGEMAKER_ENDPOINT_NAME: str = "llama2-13b-chat-endpoint"

    # S3
    S3_BUCKET_RESUMES: str = "resume-coach-resumes"
    S3_BUCKET_JOBS: str = "resume-coach-jobs"

    # DynamoDB
    DYNAMODB_TABLE_USERS: str = "resume-coach-users"
    DYNAMODB_TABLE_ANALYSES: str = "resume-coach-analyses"
    DYNAMODB_TABLE_SESSIONS: str = "resume-coach-sessions"

    # LLM Settings
    DEFAULT_TEMPERATURE: float = 0.5
    DEFAULT_MAX_TOKENS: int = 800
    CONTEXT_WINDOW_SIZE: int = 4096

    # OpenAI (for development/fallback)
    OPENAI_API_KEY: Optional[str] = None

    # Redis (caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**3.2.2 Resume Parser Service** (`app/services/resume_parser.py`)

```python
from typing import Dict, Optional
import PyPDF2
import pdfplumber
import docx
import io
from app.services.data_processor import DataProcessor

class ResumeParser:
    def __init__(self):
        self.data_processor = DataProcessor()

    async def parse_file(self, file_content: bytes, filename: str) -> Dict:
        """
        Parse resume file and extract structured information

        Returns:
            {
                'raw_text': str,
                'cleaned_text': str,
                'sections': Dict[str, str],
                'skills': List[str],
                'years_experience': int,
                'contact_info': Dict,
                'metadata': Dict
            }
        """
        # Determine file type
        file_extension = filename.split('.')[-1].lower()

        # Extract text based on file type
        if file_extension == 'pdf':
            raw_text = self._parse_pdf(file_content)
        elif file_extension == 'docx':
            raw_text = self._parse_docx(file_content)
        elif file_extension == 'txt':
            raw_text = file_content.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        # Process text
        cleaned_text = self.data_processor.clean_text(raw_text)
        sections = self.data_processor.identify_sections(cleaned_text)
        skills = self.data_processor.extract_skills(cleaned_text)
        years_exp = self.data_processor.extract_years_of_experience(cleaned_text)

        return {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'sections': sections,
            'skills': skills,
            'years_experience': years_exp,
            'contact_info': self._extract_contact_info(cleaned_text),
            'metadata': {
                'filename': filename,
                'file_type': file_extension,
                'length': len(cleaned_text),
                'word_count': len(cleaned_text.split())
            }
        }

    def _parse_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF"""
        try:
            # Method 1: pdfplumber (better for complex layouts)
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
                return text
            except Exception as e2:
                raise Exception(f"Failed to parse PDF: {str(e2)}")

    def _parse_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise Exception(f"Failed to parse DOCX: {str(e)}")

    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information from resume"""
        import re

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
            contact_info['phone'] = phones[0]

        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            contact_info['linkedin'] = linkedin[0]

        return contact_info
```

**3.2.3 LLM Service** (`app/services/llm_service.py`)

```python
import boto3
import json
from typing import Dict, Optional, List
from app.config import settings
import openai

class LLMService:
    def __init__(self):
        self.sagemaker_client = boto3.client('sagemaker-runtime', region_name=settings.AWS_REGION)
        self.endpoint_name = settings.SAGEMAKER_ENDPOINT_NAME
        self.use_sagemaker = True  # Toggle for development

        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY

    async def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """
        Generate text using LLM

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stop_sequences: Sequences to stop generation

        Returns:
            Generated text
        """
        temperature = temperature or settings.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or settings.DEFAULT_MAX_TOKENS

        if self.use_sagemaker:
            return await self._generate_sagemaker(prompt, temperature, max_tokens, stop_sequences)
        else:
            return await self._generate_openai(prompt, temperature, max_tokens, stop_sequences)

    async def _generate_sagemaker(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        stop_sequences: Optional[List[str]]
    ) -> str:
        """Generate using SageMaker endpoint"""
        # Format prompt for Llama 2 Chat
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }

        if stop_sequences:
            payload["parameters"]["stop"] = stop_sequences

        try:
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Body=json.dumps(payload)
            )

            result = json.loads(response['Body'].read().decode())

            # Parse response (format may vary based on deployment)
            if isinstance(result, list) and len(result) > 0:
                return result[0]['generated_text']
            elif 'generated_text' in result:
                return result['generated_text']
            else:
                return str(result)

        except Exception as e:
            raise Exception(f"SageMaker inference failed: {str(e)}")

    async def _generate_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        stop_sequences: Optional[List[str]]
    ) -> str:
        """Generate using OpenAI API (fallback/development)"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert career coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop_sequences
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API failed: {str(e)}")

    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough approximation: 1 token ≈ 4 characters
        # More accurate: use tiktoken library for OpenAI models
        return len(text) // 4
```

---

**Due to length constraints, I'll continue the implementation guide in the next file. Let me create a continuation document.**

### Deliverables (Phase 3)
- ✅ FastAPI backend with all core services
- ✅ Document parsing (PDF, DOCX, TXT)
- ✅ LLM service with SageMaker integration
- ✅ Analysis service with prompt orchestration
- ✅ Chat service with RAG implementation
- ✅ API endpoints for all functionality
- ✅ Unit tests for core services

---

*This implementation guide continues in IMPLEMENTATION_GUIDE_PART2.md*
