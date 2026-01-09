# Resume Coach - Implementation Guide (Part 2)

## Continuation from Phase 3...

### 3.3 Implement LangChain Orchestration

**3.3.1 Prompt Templates** (`app/chains/prompts.py`)

```python
# (Use the final prompts from Phase 2 experiments)

OVERALL_FIT_ANALYSIS_PROMPT = """You are an expert technical recruiter with 15 years of experience.

Your task is to evaluate how well a candidate's resume matches a specific job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

EVALUATION CRITERIA:
1. Technical Skills Match (40%)
2. Experience Level (30%)
3. Domain Expertise (20%)
4. Education & Credentials (10%)

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

SKILL_GAP_ANALYSIS_PROMPT = """You are a technical talent assessor. Identify skill gaps between the candidate and job requirements.

CANDIDATE'S RESUME:
{resume_text}

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
   - Learning resources

OUTPUT FORMAT:
## Skills Inventory
### Present Skills ✓
- [Skill]: [Evidence]

### Partial Skills ~
- [Skill]: [Details]

### Missing Skills ✗
- [Skill]: [Details]

## Gap Analysis by Priority
### CRITICAL GAPS
[List with learning recommendations]

### IMPORTANT GAPS
[List with learning recommendations]

### MINOR GAPS
[List with learning recommendations]
"""

STRENGTHS_IDENTIFICATION_PROMPT = """You are a career strategist helping a candidate position themselves effectively.

CANDIDATE'S RESUME:
{resume_text}

TARGET JOB:
{job_description}

TASK:
Identify the candidate's UNIQUE STRENGTHS that make them stand out for THIS specific role.

OUTPUT FORMAT:
## Top 5 Unique Strengths

### Strength 1: [Title]
**Evidence**: [Specific achievement or experience]
**Why it matters**: [Relevance to role]
**How to highlight**: [Application advice]

[Repeat for each strength]

## Positioning Statement
[2-3 sentence elevator pitch]
"""

COACHING_ADVICE_PROMPT = """You are a senior career coach providing actionable advice.

CONTEXT:
- Overall Fit: {overall_fit}
- Match Score: {match_score}/100
- Key Gaps: {gaps_summary}
- Key Strengths: {strengths_summary}

TASK:
Provide strategic advice in these categories:

1. Resume Optimization
2. Cover Letter Strategy
3. Skill Development
4. Interview Preparation
5. Application Timing

Be specific, actionable, and encouraging but realistic.
"""

CHAT_PROMPT = """You are a supportive career coach engaging in a conversation with a job seeker.

CONTEXT:
The user has uploaded their resume and received a coaching report for a specific job.

Resume Summary:
{resume_summary}

Job Title:
{job_title}

Previous Analysis:
{analysis_summary}

Conversation History:
{chat_history}

Current Question:
{user_question}

INSTRUCTIONS:
- Answer based on the context provided
- Be encouraging and supportive
- Provide specific, actionable advice
- Keep responses concise (2-4 paragraphs)
- Use bullet points for lists

Response:
"""
```

**3.3.2 Analysis Chain** (`app/chains/analysis_chain.py`)

```python
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.llms.base import BaseLLM
from typing import Dict, List
from app.chains.prompts import (
    OVERALL_FIT_ANALYSIS_PROMPT,
    SKILL_GAP_ANALYSIS_PROMPT,
    STRENGTHS_IDENTIFICATION_PROMPT,
    COACHING_ADVICE_PROMPT
)

class AnalysisChain:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self._build_chains()

    def _build_chains(self):
        """Build all analysis chains"""

        # Chain 1: Overall Fit Analysis
        self.fit_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["resume_text", "job_description"],
                template=OVERALL_FIT_ANALYSIS_PROMPT
            ),
            output_key="fit_analysis"
        )

        # Chain 2: Skill Gap Analysis
        self.gap_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["resume_text", "job_description"],
                template=SKILL_GAP_ANALYSIS_PROMPT
            ),
            output_key="gap_analysis"
        )

        # Chain 3: Strengths Identification
        self.strengths_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["resume_text", "job_description"],
                template=STRENGTHS_IDENTIFICATION_PROMPT
            ),
            output_key="strengths_analysis"
        )

    async def analyze(
        self,
        resume_text: str,
        job_description: str,
        model_params: Dict = None
    ) -> Dict:
        """
        Run complete analysis

        Returns:
            {
                'fit_analysis': str,
                'gap_analysis': str,
                'strengths_analysis': str,
                'coaching_advice': str,
                'summary': Dict
            }
        """
        # Handle long documents
        resume_processed = self._handle_long_text(resume_text, max_tokens=1500)
        job_processed = self._handle_long_text(job_description, max_tokens=1500)

        inputs = {
            "resume_text": resume_processed,
            "job_description": job_processed
        }

        # Run chains
        fit_result = await self.fit_analysis_chain.arun(**inputs)
        gap_result = await self.gap_analysis_chain.arun(**inputs)
        strengths_result = await self.strengths_chain.arun(**inputs)

        # Extract key info for coaching advice
        overall_fit, match_score = self._extract_fit_score(fit_result)
        gaps_summary = self._summarize_gaps(gap_result)
        strengths_summary = self._summarize_strengths(strengths_result)

        # Generate coaching advice
        coaching_result = await self._generate_coaching_advice(
            overall_fit=overall_fit,
            match_score=match_score,
            gaps_summary=gaps_summary,
            strengths_summary=strengths_summary
        )

        return {
            'fit_analysis': fit_result,
            'gap_analysis': gap_result,
            'strengths_analysis': strengths_result,
            'coaching_advice': coaching_result,
            'summary': {
                'overall_fit': overall_fit,
                'match_score': match_score,
                'critical_gaps': self._extract_critical_gaps(gap_result),
                'top_strengths': self._extract_top_strengths(strengths_result)
            }
        }

    def _handle_long_text(self, text: str, max_tokens: int) -> str:
        """Truncate or summarize long text"""
        estimated_tokens = len(text) // 4
        if estimated_tokens <= max_tokens:
            return text

        # Simple truncation (can be improved with summarization)
        max_chars = max_tokens * 4
        return text[:max_chars] + "\n\n[... truncated for length ...]"

    def _extract_fit_score(self, fit_analysis: str) -> tuple:
        """Extract overall fit rating and match score from analysis"""
        import re

        # Extract fit rating
        fit_match = re.search(r'Fit Rating:\s*(Poor|Fair|Good|Excellent)', fit_analysis, re.I)
        overall_fit = fit_match.group(1) if fit_match else "Unknown"

        # Extract match score
        score_match = re.search(r'Match Score:\s*(\d+)/100', fit_analysis)
        match_score = int(score_match.group(1)) if score_match else 0

        return overall_fit, match_score

    def _summarize_gaps(self, gap_analysis: str) -> str:
        """Extract summary of critical and important gaps"""
        # Simple extraction - can be improved
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

        return '\n'.join(summary_lines)

    def _summarize_strengths(self, strengths_analysis: str) -> str:
        """Extract summary of top strengths"""
        # Extract strength titles
        import re
        strengths = re.findall(r'### Strength \d+: (.+)', strengths_analysis)
        return ', '.join(strengths[:3])  # Top 3

    async def _generate_coaching_advice(
        self,
        overall_fit: str,
        match_score: int,
        gaps_summary: str,
        strengths_summary: str
    ) -> str:
        """Generate final coaching advice"""
        coaching_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["overall_fit", "match_score", "gaps_summary", "strengths_summary"],
                template=COACHING_ADVICE_PROMPT
            )
        )

        return await coaching_chain.arun(
            overall_fit=overall_fit,
            match_score=match_score,
            gaps_summary=gaps_summary,
            strengths_summary=strengths_summary
        )

    def _extract_critical_gaps(self, gap_analysis: str) -> List[str]:
        """Extract list of critical gaps"""
        import re
        # Find critical gaps section
        critical_section = re.search(r'### CRITICAL GAPS(.*?)(?:###|$)', gap_analysis, re.DOTALL)
        if not critical_section:
            return []

        # Extract bullet points
        gaps = re.findall(r'-\s*([^:]+):', critical_section.group(1))
        return gaps

    def _extract_top_strengths(self, strengths_analysis: str) -> List[str]:
        """Extract list of top strengths"""
        import re
        strengths = re.findall(r'### Strength \d+: (.+)', strengths_analysis)
        return strengths
```

**3.3.3 Chat Chain with RAG** (`app/chains/chat_chain.py`)

```python
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.base import BaseLLM
from typing import Dict, List
from app.chains.prompts import CHAT_PROMPT

class ChatChain:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        self.vector_store = None

    async def initialize_context(
        self,
        resume_text: str,
        job_description: str,
        analysis_report: Dict
    ):
        """
        Initialize chat context by creating vector embeddings of relevant documents
        """
        # Combine all context documents
        documents = [
            f"RESUME:\n{resume_text}",
            f"JOB DESCRIPTION:\n{job_description}",
            f"FIT ANALYSIS:\n{analysis_report.get('fit_analysis', '')}",
            f"GAP ANALYSIS:\n{analysis_report.get('gap_analysis', '')}",
            f"STRENGTHS:\n{analysis_report.get('strengths_analysis', '')}",
            f"COACHING ADVICE:\n{analysis_report.get('coaching_advice', '')}"
        ]

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

        chunks = []
        for doc in documents:
            chunks.extend(text_splitter.split_text(doc))

        # Create vector store
        self.vector_store = FAISS.from_texts(
            texts=chunks,
            embedding=self.embeddings
        )

    async def chat(
        self,
        user_message: str,
        session_id: str,
        resume_summary: str = "",
        job_title: str = ""
    ) -> str:
        """
        Process user message and return response

        Args:
            user_message: The user's question
            session_id: Session identifier
            resume_summary: Brief summary of resume
            job_title: Job title being analyzed

        Returns:
            AI response
        """
        if not self.vector_store:
            raise ValueError("Chat context not initialized. Call initialize_context first.")

        # Retrieve relevant context
        relevant_docs = self.vector_store.similarity_search(user_message, k=3)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])

        # Build prompt
        prompt = PromptTemplate(
            input_variables=["resume_summary", "job_title", "analysis_summary", "chat_history", "user_question"],
            template=CHAT_PROMPT
        )

        # Format chat history
        chat_history = self._format_chat_history()

        # Generate response
        formatted_prompt = prompt.format(
            resume_summary=resume_summary,
            job_title=job_title,
            analysis_summary=context,
            chat_history=chat_history,
            user_question=user_message
        )

        response = await self.llm.agenerate([formatted_prompt])
        answer = response.generations[0][0].text

        # Save to memory
        self.memory.save_context(
            {"input": user_message},
            {"output": answer}
        )

        return answer

    def _format_chat_history(self) -> str:
        """Format chat history for prompt"""
        messages = self.memory.load_memory_variables({})
        if not messages.get('chat_history'):
            return "No previous conversation."

        formatted = []
        for msg in messages['chat_history']:
            role = "User" if msg.type == "human" else "Coach"
            formatted.append(f"{role}: {msg.content}")

        return "\n".join(formatted[-10:])  # Last 10 messages

    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
```

### 3.4 Implement API Routes

**3.4.1 Resume Routes** (`app/api/routes/resume.py`)

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict
from app.services.resume_parser import ResumeParser
from app.services.aws_utils import S3Service
import uuid

router = APIRouter(prefix="/resume", tags=["resume"])

resume_parser = ResumeParser()
s3_service = S3Service()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)) -> Dict:
    """
    Upload and parse resume

    Returns:
        {
            'resume_id': str,
            'parsed_data': Dict,
            's3_url': str
        }
    """
    # Validate file type
    allowed_extensions = ['pdf', 'docx', 'txt']
    file_extension = file.filename.split('.')[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Read file content
    file_content = await file.read()

    # Parse resume
    try:
        parsed_data = await resume_parser.parse_file(file_content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

    # Generate unique ID
    resume_id = str(uuid.uuid4())

    # Upload to S3
    s3_key = f"resumes/{resume_id}/{file.filename}"
    s3_url = await s3_service.upload_file(
        file_content,
        bucket="resume-coach-resumes",
        key=s3_key
    )

    # Store metadata in DynamoDB (implement separately)
    # await db_service.store_resume_metadata(resume_id, parsed_data, s3_url)

    return {
        'resume_id': resume_id,
        'parsed_data': parsed_data,
        's3_url': s3_url
    }

@router.get("/{resume_id}")
async def get_resume(resume_id: str) -> Dict:
    """Retrieve parsed resume by ID"""
    # Implement: Fetch from DynamoDB
    pass

@router.delete("/{resume_id}")
async def delete_resume(resume_id: str) -> Dict:
    """Delete resume from S3 and database"""
    # Implement: Delete from S3 and DynamoDB
    pass
```

**3.4.2 Analysis Routes** (`app/api/routes/analysis.py`)

```python
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Optional
from pydantic import BaseModel
from app.chains.analysis_chain import AnalysisChain
from app.services.llm_service import LLMService
import uuid

router = APIRouter(prefix="/analysis", tags=["analysis"])

llm_service = LLMService()
# TODO: Wrap LLMService in LangChain LLM interface
analysis_chain = AnalysisChain(llm=None)  # Initialize with LLM

class AnalysisRequest(BaseModel):
    resume_id: str
    job_id: Optional[str] = None
    job_description: Optional[str] = None
    model_params: Optional[Dict] = None

@router.post("/compare")
async def create_analysis(request: AnalysisRequest) -> Dict:
    """
    Analyze resume against job description

    Returns:
        {
            'analysis_id': str,
            'fit_analysis': str,
            'gap_analysis': str,
            'strengths_analysis': str,
            'coaching_advice': str,
            'summary': Dict
        }
    """
    # Fetch resume (from DB or previous upload)
    # resume_data = await get_resume_from_db(request.resume_id)

    # Fetch or use provided job description
    if request.job_id:
        # job_data = await get_job_from_db(request.job_id)
        job_description = "..."  # Fetch from DB
    elif request.job_description:
        job_description = request.job_description
    else:
        raise HTTPException(status_code=400, detail="Either job_id or job_description required")

    # Run analysis
    try:
        result = await analysis_chain.analyze(
            resume_text="resume_data['cleaned_text']",  # Replace with actual data
            job_description=job_description,
            model_params=request.model_params or {}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Generate unique ID
    analysis_id = str(uuid.uuid4())

    # Store results in DynamoDB
    # await store_analysis_results(analysis_id, result)

    return {
        'analysis_id': analysis_id,
        **result
    }

@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str) -> Dict:
    """Retrieve analysis by ID"""
    # Implement: Fetch from DynamoDB
    pass
```

**3.4.3 Chat Routes** (`app/api/routes/chat.py`)

```python
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List
from pydantic import BaseModel
from app.chains.chat_chain import ChatChain
from app.services.llm_service import LLMService

router = APIRouter(prefix="/chat", tags=["chat"])

# Store chat sessions in memory (use Redis/DynamoDB in production)
chat_sessions = {}

class ChatMessage(BaseModel):
    session_id: str
    message: str
    analysis_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/message")
async def send_message(chat_msg: ChatMessage) -> ChatResponse:
    """
    Send message to chatbot

    Returns:
        {
            'response': str,
            'session_id': str
        }
    """
    session_id = chat_msg.session_id

    # Get or create chat session
    if session_id not in chat_sessions:
        # Initialize new chat session
        llm_service = LLMService()
        chat_chain = ChatChain(llm=None)  # Initialize with LLM wrapper

        # Fetch analysis report
        # analysis_data = await get_analysis_from_db(chat_msg.analysis_id)

        # Initialize context
        await chat_chain.initialize_context(
            resume_text="...",  # From analysis
            job_description="...",  # From analysis
            analysis_report={}  # Full analysis report
        )

        chat_sessions[session_id] = chat_chain
    else:
        chat_chain = chat_sessions[session_id]

    # Generate response
    try:
        response = await chat_chain.chat(
            user_message=chat_msg.message,
            session_id=session_id,
            resume_summary="...",  # Summary from analysis
            job_title="..."  # From job description
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

    return ChatResponse(
        response=response,
        session_id=session_id
    )

@router.delete("/session/{session_id}")
async def clear_session(session_id: str) -> Dict:
    """Clear chat session"""
    if session_id in chat_sessions:
        chat_sessions[session_id].clear_memory()
        del chat_sessions[session_id]

    return {"message": "Session cleared"}

@router.get("/history/{session_id}")
async def get_history(session_id: str) -> Dict:
    """Get chat history"""
    if session_id not in chat_sessions:
        return {"history": []}

    # Implement: Return formatted chat history
    pass
```

**3.4.4 Main Application** (`app/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import resume, analysis, chat, jobs
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router, prefix=settings.API_V1_PREFIX)
app.include_router(analysis.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
# app.include_router(jobs.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "Resume Coach API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.5 Test Backend

**Run Backend**:
```bash
cd backend
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs for Swagger UI
```

**Test Endpoints**:
```bash
# Test resume upload
curl -X POST "http://localhost:8000/api/v1/resume/upload" \
  -F "file=@sample_resume.pdf"

# Test analysis
curl -X POST "http://localhost:8000/api/v1/analysis/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": "test-resume-id",
    "job_description": "Senior Python Developer with 5+ years..."
  }'
```

---

## Phase 4: LLM Deployment on SageMaker

### Duration: 3-4 days

### Objectives
- Deploy Llama 2 model to SageMaker
- Configure auto-scaling
- Optimize for cost and performance
- Test endpoint integration

### Tasks

#### 4.1 Prepare Model Deployment

**4.1.1 Create Deployment Script** (`deployment/scripts/deploy_llama2.py`)

```python
import boto3
import sagemaker
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
import json

def deploy_llama2_jumpstart():
    """Deploy Llama 2 using SageMaker JumpStart"""

    session = boto3.Session(region_name='us-east-1')
    sm_session = sagemaker.Session(boto_session=session)
    role = "arn:aws:iam::YOUR_ACCOUNT_ID:role/SageMakerExecutionRole"

    # Llama 2 13B Chat model from JumpStart
    model_id = "meta-textgeneration-llama-2-13b-f"
    model_version = "*"

    # Deploy
    from sagemaker.jumpstart.model import JumpStartModel

    model = JumpStartModel(
        model_id=model_id,
        model_version=model_version,
        role=role,
        sagemaker_session=sm_session
    )

    predictor = model.deploy(
        initial_instance_count=1,
        instance_type="ml.g5.2xlarge",
        endpoint_name="llama2-13b-chat-endpoint",
        model_data_download_timeout=3600,
        container_startup_health_check_timeout=600
    )

    print(f"Endpoint deployed: {predictor.endpoint_name}")
    return predictor

def deploy_llama2_custom():
    """Deploy Llama 2 using custom DLC (more control)"""

    session = sagemaker.Session()
    role = "arn:aws:iam::YOUR_ACCOUNT_ID:role/SageMakerExecutionRole"

    # Get HuggingFace LLM DLC image
    image_uri = get_huggingface_llm_image_uri("huggingface", version="1.1.0")

    # Model configuration
    hub = {
        'HF_MODEL_ID': 'meta-llama/Llama-2-13b-chat-hf',
        'SM_NUM_GPUS': '1',
        'MAX_INPUT_LENGTH': '2048',
        'MAX_TOTAL_TOKENS': '4096',
        'HF_MODEL_QUANTIZE': '4bit',  # 4-bit quantization for cost savings
    }

    # Create HuggingFace Model
    huggingface_model = HuggingFaceModel(
        image_uri=image_uri,
        env=hub,
        role=role,
        transformers_version="4.28",
        pytorch_version="2.0",
        py_version="py310"
    )

    # Deploy
    predictor = huggingface_model.deploy(
        initial_instance_count=1,
        instance_type="ml.g5.2xlarge",
        endpoint_name="llama2-13b-chat-optimized",
        model_data_download_timeout=3600
    )

    print(f"Endpoint deployed: {predictor.endpoint_name}")
    return predictor

def test_endpoint(endpoint_name: str):
    """Test deployed endpoint"""

    runtime = boto3.client('sagemaker-runtime', region_name='us-east-1')

    payload = {
        "inputs": "<s>[INST] What is machine learning? [/INST]",
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps(payload)
    )

    result = json.loads(response['Body'].read().decode())
    print("Response:", result)

if __name__ == "__main__":
    # Option 1: JumpStart (easier)
    # predictor = deploy_llama2_jumpstart()

    # Option 2: Custom DLC (more control, better optimization)
    predictor = deploy_llama2_custom()

    # Test
    test_endpoint(predictor.endpoint_name)
```

**Run Deployment**:
```bash
python deployment/scripts/deploy_llama2.py
```

#### 4.2 Configure Auto-Scaling

**Create Auto-Scaling Script** (`deployment/scripts/setup_autoscaling.py`)

```python
import boto3

def configure_autoscaling(endpoint_name: str):
    """Configure auto-scaling for SageMaker endpoint"""

    client = boto3.client('application-autoscaling', region_name='us-east-1')

    # Register scalable target
    response = client.register_scalable_target(
        ServiceNamespace='sagemaker',
        ResourceId=f'endpoint/{endpoint_name}/variant/AllTraffic',
        ScalableDimension='sagemaker:variant:DesiredInstanceCount',
        MinCapacity=1,
        MaxCapacity=5
    )

    print("Registered scalable target")

    # Define scaling policy
    policy_response = client.put_scaling_policy(
        PolicyName=f'{endpoint_name}-scaling-policy',
        ServiceNamespace='sagemaker',
        ResourceId=f'endpoint/{endpoint_name}/variant/AllTraffic',
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

    print(f"Created scaling policy: {policy_response['PolicyARN']}")

if __name__ == "__main__":
    configure_autoscaling("llama2-13b-chat-optimized")
```

#### 4.3 Optimize for Cost

**Cost Optimization Strategies**:

1. **Use Spot Instances for Training** (not inference):
```python
# When fine-tuning
estimator = HuggingFace(
    ...
    use_spot_instances=True,
    max_wait=3600
)
```

2. **Enable Serverless Inference** (for low-traffic):
```python
from sagemaker.serverless import ServerlessInferenceConfig

serverless_config = ServerlessInferenceConfig(
    memory_size_in_mb=6144,
    max_concurrency=10
)

predictor = model.deploy(
    serverless_inference_config=serverless_config
)
```

3. **Scheduled Scaling** (scale down at night):
```python
# Create scheduled action to scale down at night
client.put_scheduled_action(
    ServiceNamespace='sagemaker',
    ScheduledActionName='scale-down-night',
    ResourceId=f'endpoint/{endpoint_name}/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    Schedule='cron(0 22 * * ? *)',  # 10 PM UTC
    ScalableTargetAction={
        'MinCapacity': 0,
        'MaxCapacity': 1
    }
)
```

#### 4.4 Monitor and Log

**Create CloudWatch Dashboard** (`deployment/scripts/create_dashboard.py`)

```python
import boto3
import json

def create_dashboard(endpoint_name: str):
    """Create CloudWatch dashboard for monitoring"""

    cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "ModelLatency", {"stat": "Average"}],
                        [".", ".", {"stat": "p99"}]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "Model Latency",
                    "yAxis": {"left": {"label": "Milliseconds"}}
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "Invocations", {"stat": "Sum"}],
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                    "title": "Invocations"
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "ModelSetupTime"],
                        [".", "Invocation4XXErrors"],
                        [".", "Invocation5XXErrors"]
                    ],
                    "period": 300,
                    "region": "us-east-1",
                    "title": "Errors"
                }
            }
        ]
    }

    cloudwatch.put_dashboard(
        DashboardName=f'{endpoint_name}-dashboard',
        DashboardBody=json.dumps(dashboard_body)
    )

    print(f"Dashboard created: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name={endpoint_name}-dashboard")

if __name__ == "__main__":
    create_dashboard("llama2-13b-chat-optimized")
```

---

## Phase 5: Frontend Development

### Duration: 5-7 days

### Objectives
- Build React frontend with TypeScript
- Implement all user-facing features
- Integrate with backend API
- Create responsive, user-friendly UI

### Tasks

#### 5.1 Set Up React Project Structure

Already initialized in Phase 0, now implement components:

**5.1.1 Configure API Client** (`frontend/src/services/api.service.ts`)

```typescript
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // Resume endpoints
  async uploadResume(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.client.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }

  async getResume(resumeId: string) {
    return this.client.get(`/resume/${resumeId}`);
  }

  // Analysis endpoints
  async createAnalysis(data: {
    resume_id: string;
    job_id?: string;
    job_description?: string;
  }) {
    return this.client.post('/analysis/compare', data);
  }

  async getAnalysis(analysisId: string) {
    return this.client.get(`/analysis/${analysisId}`);
  }

  // Chat endpoints
  async sendChatMessage(data: {
    session_id: string;
    message: string;
    analysis_id: string;
  }) {
    return this.client.post('/chat/message', data);
  }

  async getChatHistory(sessionId: string) {
    return this.client.get(`/chat/history/${sessionId}`);
  }
}

export default new ApiService();
```

**5.1.2 Create Resume Uploader Component** (`frontend/src/components/resume/ResumeUploader.tsx`)

```typescript
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Button, LinearProgress, Alert } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ApiService from '../../services/api.service';

interface ResumeUploaderProps {
  onUploadSuccess: (data: any) => void;
}

const ResumeUploader: React.FC<ResumeUploaderProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploading(true);
    setError(null);

    try {
      const response = await ApiService.uploadResume(file);
      onUploadSuccess(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload resume');
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
  });

  return (
    <Box>
      <Box
        {...getRootProps()}
        sx={{
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.400',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: 'pointer',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.2s',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop your resume here' : 'Upload your resume'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Drag & drop or click to select (PDF, DOCX, TXT)
        </Typography>
      </Box>

      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress />
          <Typography variant="body2" align="center" sx={{ mt: 1 }}>
            Uploading and parsing resume...
          </Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default ResumeUploader;
```

**5.1.3 Create Analysis Report Component** (`frontend/src/components/analysis/AnalysisReport.tsx`)

```typescript
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Divider,
  Grid,
  LinearProgress,
} from '@mui/material';
import ReactMarkdown from 'react-markdown';

interface AnalysisReportProps {
  analysis: {
    fit_analysis: string;
    gap_analysis: string;
    strengths_analysis: string;
    coaching_advice: string;
    summary: {
      overall_fit: string;
      match_score: number;
      critical_gaps: string[];
      top_strengths: string[];
    };
  };
}

const AnalysisReport: React.FC<AnalysisReportProps> = ({ analysis }) => {
  const { summary } = analysis;

  const getFitColor = (fit: string) => {
    const colors: Record<string, string> = {
      Excellent: 'success',
      Good: 'info',
      Fair: 'warning',
      Poor: 'error',
    };
    return colors[fit] || 'default';
  };

  return (
    <Box>
      {/* Summary Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            Analysis Summary
          </Typography>

          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Overall Fit
              </Typography>
              <Chip
                label={summary.overall_fit}
                color={getFitColor(summary.overall_fit) as any}
                size="medium"
                sx={{ mt: 1 }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Match Score
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography variant="h4" sx={{ mr: 2 }}>
                  {summary.match_score}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  / 100
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={summary.match_score}
                sx={{ mt: 1, height: 8, borderRadius: 4 }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Detailed Sections */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Fit Analysis
          </Typography>
          <Divider sx={{ my: 2 }} />
          <ReactMarkdown>{analysis.fit_analysis}</ReactMarkdown>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Skill Gaps
          </Typography>
          <Divider sx={{ my: 2 }} />
          <ReactMarkdown>{analysis.gap_analysis}</ReactMarkdown>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Your Strengths
          </Typography>
          <Divider sx={{ my: 2 }} />
          <ReactMarkdown>{analysis.strengths_analysis}</ReactMarkdown>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Coaching Advice
          </Typography>
          <Divider sx={{ my: 2 }} />
          <ReactMarkdown>{analysis.coaching_advice}</ReactMarkdown>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AnalysisReport;
```

**5.1.4 Create Chat Interface** (`frontend/src/components/chat/ChatInterface.tsx`)

```typescript
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Avatar,
  CircularProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ApiService from '../../services/api.service';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  sessionId: string;
  analysisId: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId, analysisId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await ApiService.sendChatMessage({
        session_id: sessionId,
        message: input,
        analysis_id: analysisId,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      {/* Messages */}
      <Paper
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          mb: 2,
          bgcolor: 'grey.50',
        }}
      >
        {messages.length === 0 && (
          <Typography variant="body2" color="text.secondary" align="center">
            Ask me anything about your resume analysis!
          </Typography>
        )}

        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'flex-start',
              mb: 2,
              flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
            }}
          >
            <Avatar
              sx={{
                bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                mx: 1,
              }}
            >
              {message.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
            </Avatar>

            <Paper
              sx={{
                p: 2,
                maxWidth: '70%',
                bgcolor: message.role === 'user' ? 'primary.light' : 'white',
              }}
            >
              <Typography variant="body1">{message.content}</Typography>
            </Paper>
          </Box>
        ))}

        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ bgcolor: 'secondary.main', mx: 1 }}>
              <SmartToyIcon />
            </Avatar>
            <CircularProgress size={24} />
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Paper>

      {/* Input */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          multiline
          maxRows={4}
        />
        <Button
          variant="contained"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          endIcon={<SendIcon />}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default ChatInterface;
```

**5.1.5 Main Analysis Page** (`frontend/src/pages/AnalysisPage.tsx`)

```typescript
import React, { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  TextField,
  Box,
  CircularProgress,
} from '@mui/material';
import ResumeUploader from '../components/resume/ResumeUploader';
import AnalysisReport from '../components/analysis/AnalysisReport';
import ChatInterface from '../components/chat/ChatInterface';
import ApiService from '../services/api.service';
import { v4 as uuidv4 } from 'uuid';

const steps = ['Upload Resume', 'Job Description', 'Analysis', 'Chat'];

const AnalysisPage: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [resumeId, setResumeId] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [analysis, setAnalysis] = useState<any>(null);
  const [analysisId, setAnalysisId] = useState('');
  const [sessionId] = useState(uuidv4());
  const [loading, setLoading] = useState(false);

  const handleResumeUpload = (data: any) => {
    setResumeId(data.resume_id);
    setActiveStep(1);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const response = await ApiService.createAnalysis({
        resume_id: resumeId,
        job_description: jobDescription,
      });
      setAnalysis(response.data);
      setAnalysisId(response.data.analysis_id);
      setActiveStep(2);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Failed to analyze. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" align="center" gutterBottom>
        Resume Coach
      </Typography>
      <Typography variant="subtitle1" align="center" color="text.secondary" gutterBottom>
        AI-powered career coaching for better job applications
      </Typography>

      <Stepper activeStep={activeStep} sx={{ my: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Paper sx={{ p: 3, minHeight: '400px' }}>
        {activeStep === 0 && (
          <Box>
            <Typography variant="h5" gutterBottom>
              Step 1: Upload Your Resume
            </Typography>
            <ResumeUploader onUploadSuccess={handleResumeUpload} />
          </Box>
        )}

        {activeStep === 1 && (
          <Box>
            <Typography variant="h5" gutterBottom>
              Step 2: Provide Job Description
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={15}
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              sx={{ my: 2 }}
            />
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button onClick={() => setActiveStep(0)}>Back</Button>
              <Button
                variant="contained"
                onClick={handleAnalyze}
                disabled={!jobDescription.trim() || loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Analyze'}
              </Button>
            </Box>
          </Box>
        )}

        {activeStep === 2 && analysis && (
          <Box>
            <AnalysisReport analysis={analysis} />
            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
              <Button variant="contained" onClick={() => setActiveStep(3)}>
                Continue to Chat
              </Button>
            </Box>
          </Box>
        )}

        {activeStep === 3 && (
          <Box>
            <Typography variant="h5" gutterBottom>
              Chat with Your Career Coach
            </Typography>
            <ChatInterface sessionId={sessionId} analysisId={analysisId} />
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default AnalysisPage;
```

---

**Continue in IMPLEMENTATION_GUIDE_PART3.md for phases 6-8...**
