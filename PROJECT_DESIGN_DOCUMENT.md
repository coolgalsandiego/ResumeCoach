# Resume Coach - Project Design Document

## Executive Summary

Resume Coach is an AI-powered web application that analyzes resumes against job descriptions, providing personalized coaching advice to improve job application success rates. The system leverages Large Language Models (LLMs), specifically Llama 2, deployed on AWS infrastructure with a user-friendly web interface.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [LLM Strategy](#llm-strategy)
6. [Prompt Engineering Framework](#prompt-engineering-framework)
7. [Innovation & Creativity Features](#innovation--creativity-features)
8. [Deployment Architecture](#deployment-architecture)
9. [Cost Optimization Strategy](#cost-optimization-strategy)
10. [Quality Assurance](#quality-assurance)

---

## 1. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│              (React.js with Material-UI/Tailwind)                │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ HTTPS/REST API
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                    Backend API Layer                             │
│              (FastAPI/Flask - Python 3.10+)                      │
├──────────────────────────────────────────────────────────────────┤
│  • Authentication & Session Management                           │
│  • File Upload Handler (PDF/DOCX/TXT)                           │
│  • Job Search Integration                                        │
│  • Chat Context Manager                                          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│              LangChain Orchestration Layer                       │
├──────────────────────────────────────────────────────────────────┤
│  • Prompt Templates & Chain Management                           │
│  • Document Processing & Chunking                                │
│  • Memory Management (Conversation Buffer)                       │
│  • RAG Implementation (Vector Store)                             │
└───────────┬────────────────────────────┬────────────────────────┘
            │                            │
            │                            │
┌───────────▼──────────┐    ┌───────────▼─────────────────────────┐
│  LLM Endpoint         │    │    Supporting Services              │
│  (SageMaker)          │    ├─────────────────────────────────────┤
├───────────────────────┤    │  • S3 (Document Storage)            │
│  • Llama 2 7B/13B     │    │  • DynamoDB (Session/User Data)     │
│  • Custom Endpoint    │    │  • ElastiCache (Caching)            │
│  • Auto-scaling       │    │  • CloudWatch (Monitoring)          │
└───────────────────────┘    └─────────────────────────────────────┘
```

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    VPC (Virtual Private Cloud)           │   │
│  │                                                           │   │
│  │  ┌──────────────────┐        ┌──────────────────┐       │   │
│  │  │  Public Subnet   │        │  Private Subnet  │       │   │
│  │  │                  │        │                  │       │   │
│  │  │  ┌────────────┐  │        │  ┌────────────┐ │       │   │
│  │  │  │ Application│  │        │  │  SageMaker │ │       │   │
│  │  │  │    Load    │  │        │  │  Endpoint  │ │       │   │
│  │  │  │  Balancer  │  │        │  └────────────┘ │       │   │
│  │  │  └──────┬─────┘  │        │                  │       │   │
│  │  │         │        │        │  ┌────────────┐ │       │   │
│  │  │  ┌──────▼─────┐  │        │  │ ElastiCache│ │       │   │
│  │  │  │   EC2      │  │        │  └────────────┘ │       │   │
│  │  │  │  (Docker)  │  │        │                  │       │   │
│  │  │  │            │  │        │  ┌────────────┐ │       │   │
│  │  │  │  Backend + │  │        │  │ DynamoDB   │ │       │   │
│  │  │  │  Frontend  │  │        │  └────────────┘ │       │   │
│  │  │  └────────────┘  │        │                  │       │   │
│  │  └──────────────────┘        └──────────────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   S3 Buckets                             │   │
│  │  • resume-uploads/  • job-descriptions/  • models/      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Frontend
- **Framework**: React.js 18+ with TypeScript
- **UI Library**: Material-UI (MUI) or Tailwind CSS + Shadcn/ui
- **State Management**: Redux Toolkit / Zustand
- **API Client**: Axios with interceptors
- **File Upload**: React-Dropzone
- **Markdown Rendering**: React-Markdown
- **Charts**: Recharts / Chart.js

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Alternative**: Flask with Flask-RESTX
- **Authentication**: JWT tokens
- **File Processing**:
  - PyPDF2 / pdfplumber (PDF parsing)
  - python-docx (DOCX parsing)
  - spaCy (NLP preprocessing)
- **Job Scraping**: BeautifulSoup4 / Selenium (if needed)

### LLM & AI Stack
- **Model**: Meta Llama 2 (7B or 13B Chat)
- **Orchestration**: LangChain 0.1+
- **Embeddings**: HuggingFace Embeddings (all-MiniLM-L6-v2)
- **Vector Store**: FAISS / Chroma
- **Model Deployment**: AWS SageMaker (Jumpstart or DLC)
- **Fine-tuning**: Hugging Face Transformers, PEFT/LoRA

### DevOps & Infrastructure
- **Containerization**: Docker + Docker Compose
- **Container Registry**: AWS ECR
- **Compute**: AWS EC2 (t3.medium or larger)
- **Model Hosting**: AWS SageMaker
- **Storage**: AWS S3
- **Database**: AWS DynamoDB (NoSQL)
- **Caching**: AWS ElastiCache (Redis)
- **Monitoring**: AWS CloudWatch, Prometheus
- **CI/CD**: GitHub Actions / AWS CodePipeline

---

## 3. Component Design

### 3.1 Frontend Components

#### Main Application Components

```
src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── Sidebar.tsx
│   ├── resume/
│   │   ├── ResumeUploader.tsx
│   │   ├── ResumeViewer.tsx
│   │   └── ResumeParser.tsx
│   ├── job/
│   │   ├── JobSearch.tsx
│   │   ├── JobSelector.tsx
│   │   └── JobViewer.tsx
│   ├── analysis/
│   │   ├── AnalysisReport.tsx
│   │   ├── SkillsGapAnalysis.tsx
│   │   ├── MatchScore.tsx
│   │   └── Recommendations.tsx
│   ├── chat/
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   └── InputBox.tsx
│   └── settings/
│       ├── ModelParameters.tsx
│       └── UserPreferences.tsx
├── pages/
│   ├── HomePage.tsx
│   ├── AnalysisPage.tsx
│   └── ChatPage.tsx
├── services/
│   ├── api.service.ts
│   ├── auth.service.ts
│   └── websocket.service.ts
└── store/
    ├── resumeSlice.ts
    ├── jobSlice.ts
    └── chatSlice.ts
```

### 3.2 Backend API Endpoints

```python
# Core Endpoints
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/profile

# Resume Management
POST   /api/v1/resume/upload          # Upload resume (PDF/DOCX/TXT)
GET    /api/v1/resume/{resume_id}     # Get parsed resume
DELETE /api/v1/resume/{resume_id}     # Delete resume

# Job Management
GET    /api/v1/jobs/search             # Search jobs (optional scraping)
POST   /api/v1/jobs/manual             # Manually input job description
GET    /api/v1/jobs/{job_id}           # Get job details

# Analysis
POST   /api/v1/analysis/compare        # Compare resume to job
GET    /api/v1/analysis/{analysis_id}  # Get analysis report
POST   /api/v1/analysis/regenerate     # Regenerate with different params

# Chat
POST   /api/v1/chat/message            # Send message to chatbot
GET    /api/v1/chat/history/{session_id}  # Get chat history
DELETE /api/v1/chat/session/{session_id} # Clear session

# Model Configuration
GET    /api/v1/model/parameters        # Get available parameters
POST   /api/v1/model/parameters        # Update model parameters
```

### 3.3 LangChain Architecture

```python
# Chain Structure

┌─────────────────────────────────────────────────────┐
│              Main Orchestration Chain                │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴──────────┐
        │                      │
┌───────▼────────┐   ┌────────▼──────────┐
│  Document      │   │   Analysis        │
│  Processing    │   │   Chain           │
│  Chain         │   │                   │
├────────────────┤   ├───────────────────┤
│ • Parse PDF    │   │ • Match Analysis  │
│ • Extract Text │   │ • Gap Analysis    │
│ • Chunk Docs   │   │ • Strength ID     │
│ • Summarize    │   │ • Advice Gen      │
└────────────────┘   └─────────┬─────────┘
                               │
                     ┌─────────▼──────────┐
                     │  Conversational    │
                     │  Chain (Chat)      │
                     ├────────────────────┤
                     │ • Context Memory   │
                     │ • RAG over Report  │
                     │ • Follow-up QA     │
                     └────────────────────┘
```

---

## 4. Data Flow

### 4.1 Resume Analysis Flow

```
1. User uploads resume (PDF)
   ↓
2. Backend receives file → Store in S3
   ↓
3. PDF Parser extracts text and structure
   ↓
4. Text Preprocessor cleans and structures data
   ↓
5. User provides/selects job description
   ↓
6. LangChain orchestrates LLM calls:
   a. Summarize resume (if too long)
   b. Summarize job description (if too long)
   c. Match analysis prompt
   d. Gap analysis prompt
   e. Strength identification prompt
   f. Coaching advice prompt
   ↓
7. Aggregate results into structured report
   ↓
8. Store report in DynamoDB
   ↓
9. Create vector embeddings of report for RAG
   ↓
10. Return report to frontend
```

### 4.2 Chat Flow

```
1. User sends message in chat
   ↓
2. Backend retrieves:
   - Chat history from memory/DynamoDB
   - Resume context
   - Job description context
   - Analysis report
   ↓
3. LangChain RAG retrieves relevant sections
   ↓
4. Construct prompt with:
   - System context
   - Conversation history
   - Retrieved context
   - User question
   ↓
5. Send to LLM endpoint
   ↓
6. Stream response back to frontend
   ↓
7. Update conversation memory
```

---

## 5. LLM Strategy

### 5.1 Model Selection

**Primary Model**: Meta Llama 2 13B Chat

**Rationale**:
- Strong instruction-following capabilities
- Good balance of quality and cost
- Can be deployed on SageMaker with reasonable instance costs
- Supports commercial use

**Fallback**: Llama 2 7B Chat (for cost optimization)

### 5.2 Deployment Strategy

#### SageMaker Deployment Options

**Option 1: SageMaker JumpStart** (Recommended for beginners)
- Pre-configured Llama 2 models
- Simple deployment process
- Built-in optimization

**Option 2: SageMaker DLC (Deep Learning Containers)** (Recommended for production)
- More control over inference configuration
- Custom optimization (quantization, TensorRT)
- Better cost-performance tradeoff

**Instance Recommendations**:
- Development: ml.g5.2xlarge (1 GPU, cost-effective)
- Production: ml.g5.4xlarge (1 GPU, better performance)
- High-scale: ml.g5.12xlarge (4 GPUs) with auto-scaling

### 5.3 Model Optimization

1. **Quantization**: Use 4-bit or 8-bit quantization (bitsandbytes)
2. **TensorRT**: Apply TensorRT optimization for inference
3. **Batch Processing**: Enable dynamic batching
4. **Caching**: Cache common prompts/responses
5. **Auto-scaling**: Configure based on request rate

### 5.4 Fine-tuning Strategy

**Approach**: Parameter-Efficient Fine-Tuning (PEFT) with LoRA

**Dataset Preparation**:
```json
{
  "instruction": "Compare this resume to the job description and identify skill gaps.",
  "input": "Resume: [resume_text]\n\nJob Description: [job_text]",
  "output": "Based on the analysis, the candidate has the following gaps..."
}
```

**Training Configuration**:
- LoRA rank: 8-16
- Learning rate: 3e-4
- Batch size: 4-8 (with gradient accumulation)
- Epochs: 3-5
- Training samples: 500-1000 examples

---

## 6. Prompt Engineering Framework

### 6.1 Prompt Design Principles

1. **Clarity**: Explicit instructions with minimal ambiguity
2. **Context**: Provide sufficient background information
3. **Structure**: Use consistent formatting for inputs/outputs
4. **Examples**: Include few-shot examples when needed
5. **Constraints**: Specify output format, length, tone

### 6.2 Core Prompts

#### Prompt 1: Overall Fit Analysis

```python
OVERALL_FIT_PROMPT = """You are an expert career coach specializing in resume analysis.

Your task is to evaluate how well a candidate's resume matches a specific job description.

**Resume:**
{resume_text}

**Job Description:**
{job_description}

**Analysis Instructions:**
1. Assess the overall fit (Poor/Fair/Good/Excellent)
2. Provide a match score (0-100)
3. Explain your reasoning in 2-3 paragraphs
4. Consider:
   - Years of experience match
   - Technical skills alignment
   - Domain expertise relevance
   - Education requirements
   - Soft skills indicators

**Output Format:**
Overall Fit: [Poor/Fair/Good/Excellent]
Match Score: [0-100]/100

Reasoning:
[Your detailed analysis]
"""
```

#### Prompt 2: Skill Gap Analysis

```python
SKILL_GAP_PROMPT = """You are an expert technical recruiter.

Analyze the skill gaps between the candidate's resume and the job requirements.

**Resume:**
{resume_text}

**Job Requirements:**
{job_requirements}

**Instructions:**
1. Identify REQUIRED skills from the job description that are NOT mentioned in the resume
2. Identify PREFERRED skills from the job description that are NOT mentioned in the resume
3. For each gap, assess:
   - Criticality (Critical/Important/Nice-to-have)
   - How easy it is to learn (Easy/Moderate/Difficult)
   - Recommended learning resources

**Output Format:**
## Critical Gaps
- [Skill Name]: [Why it's critical] | Learnability: [Easy/Moderate/Difficult] | Resources: [Brief recommendation]

## Important Gaps
- [Skill Name]: [Why it's important] | Learnability: [Easy/Moderate/Difficult] | Resources: [Brief recommendation]

## Nice-to-Have Gaps
- [Skill Name]: [Brief note]
"""
```

#### Prompt 3: Unique Strengths Identification

```python
STRENGTHS_PROMPT = """You are a career strategist helping candidates position themselves effectively.

Identify the candidate's unique strengths that are particularly relevant to this job.

**Resume:**
{resume_text}

**Job Description:**
{job_description}

**Instructions:**
1. Find experiences or skills in the resume that are ESPECIALLY valuable for this role
2. Identify unique combinations of skills that set the candidate apart
3. Note any achievements or metrics that are impressive
4. Highlight transferable skills from different domains

**Output Format:**
## Key Strengths to Emphasize

### Strength 1: [Title]
- **What it is**: [Description]
- **Why it matters for this role**: [Relevance]
- **How to highlight it**: [Application strategy]

[Repeat for 3-5 strengths]
"""
```

#### Prompt 4: Application Strategy Advice

```python
COACHING_ADVICE_PROMPT = """You are a senior career coach providing actionable advice.

Given the analysis of the candidate's fit for the role, provide strategic advice for their application.

**Context:**
- Overall Fit: {overall_fit}
- Match Score: {match_score}/100
- Key Gaps: {identified_gaps}
- Key Strengths: {identified_strengths}

**Instructions:**
Provide advice in these categories:

1. **Resume Optimization**: Specific changes to make the resume more appealing
2. **Cover Letter Strategy**: Key points to emphasize in the cover letter
3. **Skill Development**: Priority skills to develop before or after applying
4. **Interview Preparation**: Likely questions and how to address weaknesses
5. **Application Timing**: Whether to apply now or after building certain skills

Be specific, actionable, and encouraging but realistic.

**Output Format:**
## Resume Optimization
[Bullet points with specific recommendations]

## Cover Letter Strategy
[Paragraph with key themes to address]

## Skill Development
[Prioritized list with timeline estimates]

## Interview Preparation
[Likely questions and suggested responses]

## Application Timing
[Clear recommendation with reasoning]
"""
```

#### Prompt 5: Conversational Chat

```python
CHAT_PROMPT = """You are a supportive career coach engaging in a conversation with a job seeker.

**Context:**
The user has uploaded their resume and received a coaching report for a specific job.

**Resume Summary:**
{resume_summary}

**Job Title:**
{job_title}

**Previous Analysis:**
{analysis_summary}

**Conversation History:**
{chat_history}

**Current Question:**
{user_question}

**Instructions:**
- Answer the user's question based on the context provided
- Be encouraging and supportive
- Provide specific, actionable advice
- If the question is outside the context, politely redirect to relevant topics
- Keep responses concise (2-4 paragraphs) unless more detail is requested
- Use bullet points for lists

**Response:**
"""
```

### 6.3 Prompt Optimization Strategy

1. **A/B Testing**: Test multiple prompt variations
2. **Iterative Refinement**: Collect user feedback and improve
3. **Temperature Tuning**:
   - Analysis prompts: 0.3-0.5 (more deterministic)
   - Chat prompts: 0.7-0.8 (more creative)
4. **Length Management**: Truncate/summarize long documents
5. **Caching**: Cache prompt templates with parameter substitution

---

## 7. Innovation & Creativity Features

### 7.1 PDF Support & Document Processing

**Objective**: Extract structured information from various resume formats

**Implementation**:
```python
class ResumeParser:
    def __init__(self):
        self.pdf_parser = pdfplumber
        self.docx_parser = python_docx
        self.nlp = spacy.load("en_core_web_sm")

    def parse(self, file_path: str) -> Dict:
        """
        Extract structured data from resume
        Returns: {
            'raw_text': str,
            'sections': Dict[str, str],  # e.g., {'experience': '...', 'education': '...'}
            'contact_info': Dict,
            'skills': List[str],
            'experience_years': int
        }
        """
        # Extract text based on file type
        # Use NLP to identify sections
        # Extract key entities (dates, companies, skills)
        # Return structured data
```

**Features**:
- Support for PDF, DOCX, TXT formats
- Automatic section detection (Experience, Education, Skills, etc.)
- Entity extraction (companies, dates, locations)
- Skill extraction using custom NLP models

### 7.2 Job Search Integration

**Option 1: Pre-loaded Dataset** (Recommended for MVP)
- Use Kaggle LinkedIn/Indeed datasets
- Store in database with search index
- Filter by:
  - Job title
  - Location
  - Company
  - Required skills
  - Experience level

**Option 2: Live Scraping** (Advanced)
- Implement ethical scraping of job boards
- Respect robots.txt and rate limits
- Cache results to minimize requests

**Implementation**:
```python
class JobSearchService:
    def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        experience_level: Optional[str] = None,
        limit: int = 20
    ) -> List[Job]:
        """Search jobs from database or external API"""
        pass
```

### 7.3 Document Length Handling

**Challenge**: Resumes and job descriptions may exceed LLM context limits

**Solution: Intelligent Summarization**

```python
class DocumentProcessor:
    def __init__(self, llm, max_tokens=2000):
        self.llm = llm
        self.max_tokens = max_tokens
        self.summarizer = load_summarization_chain(llm, chain_type="map_reduce")

    def process_long_document(self, text: str, doc_type: str) -> str:
        """
        If document exceeds max_tokens:
        1. Split into semantic chunks
        2. Summarize each chunk
        3. Combine summaries
        4. Extract key information
        """
        if self.count_tokens(text) <= self.max_tokens:
            return text

        # Split into chunks
        chunks = self.semantic_chunker(text)

        # Summarize with focus on job-relevant info
        if doc_type == "resume":
            summary_prompt = "Summarize this resume section, focusing on skills, experience, and achievements."
        else:
            summary_prompt = "Summarize this job description section, focusing on requirements and responsibilities."

        summaries = [self.summarizer.run(chunk, prompt=summary_prompt) for chunk in chunks]

        return "\n\n".join(summaries)
```

### 7.4 Chat Context Management

**Challenge**: Maintain coherent conversation despite context limits

**Solution: Hierarchical Memory System**

```python
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory

class ContextManager:
    def __init__(self, llm):
        # Short-term memory: Last N messages (full detail)
        self.buffer_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output",
            input_key="input",
            k=10  # Last 10 messages
        )

        # Long-term memory: Older messages (summarized)
        self.summary_memory = ConversationSummaryMemory(
            llm=llm,
            memory_key="conversation_summary"
        )

        # Document memory: RAG over analysis report
        self.document_memory = VectorStoreMemory(
            vector_store=FAISS.from_documents(...),
            memory_key="relevant_context"
        )

    def get_context(self, user_query: str) -> Dict:
        """
        Retrieve relevant context for the query
        Returns:
        - Recent conversation history (buffer)
        - Summary of older conversation (if exists)
        - Relevant sections from analysis report (RAG)
        """
        return {
            "recent_messages": self.buffer_memory.load_memory_variables({}),
            "conversation_summary": self.summary_memory.load_memory_variables({}),
            "relevant_report_sections": self.document_memory.retrieve(user_query, k=3)
        }
```

### 7.5 Parameter Tuning Interface

**Feature**: Allow users to adjust LLM parameters for different outputs

**Parameters to Expose**:
- Temperature (0.0 - 1.0): Creativity vs consistency
- Max tokens: Length of response
- Analysis depth: Quick/Standard/Detailed
- Tone: Professional/Friendly/Direct

**Implementation**:
```python
class ModelConfigService:
    PRESETS = {
        "conservative": {"temperature": 0.3, "max_tokens": 500, "top_p": 0.9},
        "balanced": {"temperature": 0.5, "max_tokens": 800, "top_p": 0.95},
        "creative": {"temperature": 0.8, "max_tokens": 1000, "top_p": 0.95}
    }

    def apply_config(self, preset: str, custom_params: Dict = None):
        """Apply configuration to LLM calls"""
        pass
```

### 7.6 RAG (Retrieval-Augmented Generation)

**Purpose**: Answer user questions by retrieving relevant sections from the analysis report

**Implementation**:
```python
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None

    def index_report(self, report_text: str, report_id: str):
        """Create vector embeddings of report sections"""
        # Split report into sections
        sections = self.split_report(report_text)

        # Create embeddings
        texts = [s["content"] for s in sections]
        metadatas = [{"section": s["type"], "report_id": report_id} for s in sections]

        self.vector_store = FAISS.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )

    def retrieve_relevant_context(self, query: str, k: int = 3) -> List[str]:
        """Retrieve most relevant sections for user query"""
        docs = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
```

---

## 8. Deployment Architecture

### 8.1 Containerization Strategy

**Dockerfile Structure**:
```dockerfile
# Backend Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose** (for local development):
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AWS_REGION=us-east-1
      - SAGEMAKER_ENDPOINT=llama2-endpoint
    volumes:
      - ./backend:/app
    depends_on:
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### 8.2 EC2 Deployment

**Instance Specification**:
- Type: t3.large or t3.xlarge (for production)
- OS: Ubuntu 22.04 LTS
- Storage: 50GB EBS (gp3)
- Security Group: Allow 80, 443, 22

**Deployment Steps**:
1. Launch EC2 instance
2. Install Docker and Docker Compose
3. Pull application images from ECR
4. Configure environment variables
5. Set up Nginx as reverse proxy
6. Configure SSL with Let's Encrypt
7. Set up CloudWatch agent for monitoring

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name resumecoach.example.com;

    location / {
        proxy_pass http://localhost:3000;  # React app
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;  # FastAPI backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 8.3 SageMaker Model Deployment

**Deployment Script**:
```python
import boto3
import sagemaker
from sagemaker.huggingface import HuggingFaceModel

def deploy_llama2_model():
    """Deploy Llama 2 model to SageMaker"""

    role = "arn:aws:iam::YOUR_ACCOUNT:role/SageMakerRole"

    # Option 1: JumpStart deployment
    model = HuggingFaceModel(
        model_data="s3://jumpstart-cache-prod-us-east-1/huggingface-llm/huggingface-llm-llama-2-13b-chat-fp16/",
        role=role,
        transformers_version="4.26",
        pytorch_version="1.13",
        py_version="py39",
        env={
            'HF_MODEL_ID': 'meta-llama/Llama-2-13b-chat-hf',
            'SM_NUM_GPUS': '1',
            'MAX_INPUT_LENGTH': '2048',
            'MAX_TOTAL_TOKENS': '4096',
        }
    )

    # Deploy to endpoint
    predictor = model.deploy(
        initial_instance_count=1,
        instance_type="ml.g5.2xlarge",
        endpoint_name="llama2-13b-chat-endpoint"
    )

    return predictor
```

**Auto-scaling Configuration**:
```python
import boto3

client = boto3.client('application-autoscaling')

# Register scalable target
client.register_scalable_target(
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/llama2-13b-chat-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    MinCapacity=1,
    MaxCapacity=5
)

# Define scaling policy
client.put_scaling_policy(
    PolicyName='llama2-scaling-policy',
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/llama2-13b-chat-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 70.0,  # Target 70% invocations per instance
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
        },
        'ScaleInCooldown': 600,  # 10 minutes
        'ScaleOutCooldown': 300  # 5 minutes
    }
)
```

---

## 9. Cost Optimization Strategy

### 9.1 SageMaker Cost Management

**Strategies**:
1. **Right-sizing**:
   - Start with ml.g5.2xlarge ($1.21/hour)
   - Monitor utilization, downgrade to 7B model if 13B is overkill

2. **Spot Instances**:
   - Use SageMaker Managed Spot Training for fine-tuning (up to 70% savings)

3. **Auto-scaling**:
   - Scale down during low-traffic hours
   - Set up scheduled scaling (e.g., scale to 0 instances at night)

4. **Inference Optimization**:
   - Batch multiple requests when possible
   - Use quantized models (4-bit/8-bit)
   - Implement request caching for common queries

5. **Alternative Endpoints**:
   - For development: Use Replicate or OpenAI API (pay-per-token)
   - For production: Self-hosted SageMaker

**Cost Monitoring**:
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Set billing alarm
cloudwatch.put_metric_alarm(
    AlarmName='SageMaker-High-Cost',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=1,
    MetricName='EstimatedCharges',
    Namespace='AWS/Billing',
    Period=21600,  # 6 hours
    Statistic='Maximum',
    Threshold=100.0,  # Alert if estimated charges > $100
    ActionsEnabled=True,
    AlarmActions=['arn:aws:sns:us-east-1:ACCOUNT_ID:billing-alerts']
)
```

### 9.2 EC2 Cost Management

**Strategies**:
1. Use Reserved Instances for predictable workload (up to 72% savings)
2. Use Spot Instances for non-critical workloads
3. Right-size based on actual usage (start small, scale up)
4. Use EBS gp3 volumes (cheaper than gp2 with better performance)
5. Enable EBS optimization only when needed

### 9.3 Storage Cost Management

**S3 Lifecycle Policies**:
```python
s3_client.put_bucket_lifecycle_configuration(
    Bucket='resume-uploads',
    LifecycleConfiguration={
        'Rules': [
            {
                'Id': 'DeleteOldUploads',
                'Status': 'Enabled',
                'Expiration': {'Days': 90},
                'Prefix': 'uploads/',
                'Transitions': [
                    {'Days': 30, 'StorageClass': 'STANDARD_IA'},
                    {'Days': 60, 'StorageClass': 'GLACIER'}
                ]
            }
        ]
    }
)
```

---

## 10. Quality Assurance

### 10.1 Testing Strategy

**Unit Tests**:
- Test PDF parsing logic
- Test prompt construction
- Test API endpoints

**Integration Tests**:
- Test end-to-end flow (upload → analysis → chat)
- Test SageMaker endpoint integration
- Test database operations

**Load Tests**:
- Use Locust or JMeter
- Simulate 100 concurrent users
- Test response times under load

### 10.2 Prompt Evaluation

**Metrics**:
1. **Relevance**: Does the output address the prompt?
2. **Accuracy**: Are the identified gaps/strengths correct?
3. **Actionability**: Is the advice specific and practical?
4. **Consistency**: Similar inputs produce similar outputs?

**Evaluation Process**:
1. Create test set of 50 resume-job pairs
2. Generate outputs with different prompts
3. Have domain experts rate outputs (1-5 scale)
4. Calculate average scores
5. Iterate on prompt design

### 10.3 Monitoring & Observability

**Key Metrics**:
- API response time (p50, p95, p99)
- SageMaker endpoint latency
- Error rates
- User satisfaction (thumbs up/down)
- Cost per analysis

**Monitoring Stack**:
- CloudWatch for AWS metrics
- Application logs (structured JSON)
- Custom dashboards for business metrics

---

## Conclusion

This design document provides a comprehensive blueprint for building a production-grade Resume Coach application. The architecture is designed to:

1. ✅ Score maximum points on all rubric criteria
2. ✅ Be scalable and cost-effective
3. ✅ Deliver exceptional user experience
4. ✅ Demonstrate advanced AI/ML engineering skills
5. ✅ Be fully deployable on AWS

The next step is to follow the detailed implementation guide to build each component systematically.
