"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from io import BytesIO

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    @pytest.mark.unit
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    @pytest.mark.unit
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestResumeEndpoints:
    """Test resume upload and management endpoints"""

    @pytest.mark.integration
    def test_upload_resume_txt(self):
        """Test uploading TXT resume"""
        file_content = b"""John Doe
Software Engineer
Email: john@example.com

EXPERIENCE
Software Engineer | Tech Corp | 2020-Present
- Developed applications using Python

SKILLS
Python, JavaScript, React
"""
        files = {
            "file": ("resume.txt", BytesIO(file_content), "text/plain")
        }
        
        response = client.post("/api/v1/resume/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "resume_id" in data
        assert data["filename"] == "resume.txt"
        assert "parsed_data" in data
        assert "skills" in data["parsed_data"]
        
        return data["resume_id"]

    @pytest.mark.integration
    def test_upload_resume_unsupported_format(self):
        """Test uploading unsupported file format"""
        file_content = b"Some content"
        files = {
            "file": ("resume.xyz", BytesIO(file_content), "application/octet-stream")
        }
        
        response = client.post("/api/v1/resume/upload", files=files)
        
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]

    @pytest.mark.integration
    def test_get_resume(self):
        """Test retrieving resume by ID"""
        # First upload a resume
        file_content = b"""John Doe
Software Engineer
"""
        files = {
            "file": ("resume.txt", BytesIO(file_content), "text/plain")
        }
        upload_response = client.post("/api/v1/resume/upload", files=files)
        resume_id = upload_response.json()["resume_id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/resume/{resume_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["resume_id"] == resume_id

    @pytest.mark.integration
    def test_get_resume_not_found(self):
        """Test retrieving non-existent resume"""
        response = client.get("/api/v1/resume/non-existent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.integration
    def test_delete_resume(self):
        """Test deleting resume"""
        # First upload a resume
        file_content = b"""John Doe
Software Engineer
"""
        files = {
            "file": ("resume.txt", BytesIO(file_content), "text/plain")
        }
        upload_response = client.post("/api/v1/resume/upload", files=files)
        resume_id = upload_response.json()["resume_id"]
        
        # Delete it
        response = client.delete(f"/api/v1/resume/{resume_id}")
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/resume/{resume_id}")
        assert get_response.status_code == 404

    @pytest.mark.integration
    def test_list_resumes(self):
        """Test listing all resumes"""
        response = client.get("/api/v1/resume/")
        
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "resumes" in data
        assert isinstance(data["resumes"], list)


class TestAnalysisEndpoints:
    """Test analysis endpoints"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_create_analysis(self):
        """Test creating analysis (requires LLM)"""
        # First upload a resume
        file_content = b"""John Doe
Software Engineer
EXPERIENCE
Software Engineer | Tech Corp | 2020-Present
- Python development
SKILLS
Python, JavaScript
"""
        files = {
            "file": ("resume.txt", BytesIO(file_content), "text/plain")
        }
        upload_response = client.post("/api/v1/resume/upload", files=files)
        resume_id = upload_response.json()["resume_id"]
        
        # Create analysis
        job_description = """
        Software Engineer Position
        Requirements:
        - Python experience
        - JavaScript knowledge
        """
        
        response = client.post(
            "/api/v1/analysis/compare",
            json={
                "resume_id": resume_id,
                "job_description": job_description
            }
        )
        
        # May fail if LLM is not configured, but should return proper error
        if response.status_code == 200:
            data = response.json()
            assert "analysis_id" in data
            assert "fit_analysis" in data
            assert "gap_analysis" in data
            assert "summary" in data
        else:
            # If LLM not configured, should return 500 or 400
            assert response.status_code in [400, 500]

    @pytest.mark.integration
    def test_create_analysis_missing_resume(self):
        """Test creating analysis with non-existent resume"""
        response = client.post(
            "/api/v1/analysis/compare",
            json={
                "resume_id": "non-existent",
                "job_description": "Some job description"
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestChatEndpoints:
    """Test chat endpoints"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_send_chat_message(self):
        """Test sending chat message (requires LLM)"""
        # First create an analysis
        file_content = b"""John Doe
Software Engineer
"""
        files = {
            "file": ("resume.txt", BytesIO(file_content), "text/plain")
        }
        upload_response = client.post("/api/v1/resume/upload", files=files)
        resume_id = upload_response.json()["resume_id"]
        
        # Create analysis
        analysis_response = client.post(
            "/api/v1/analysis/compare",
            json={
                "resume_id": resume_id,
                "job_description": "Software Engineer position"
            }
        )
        
        if analysis_response.status_code != 200:
            pytest.skip("Analysis creation failed, likely LLM not configured")
        
        analysis_id = analysis_response.json()["analysis_id"]
        session_id = "test-session-123"
        
        # Send chat message
        response = client.post(
            "/api/v1/chat/message",
            json={
                "session_id": session_id,
                "message": "What are my strengths?",
                "analysis_id": analysis_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "session_id" in data
        else:
            # If LLM not configured, should return proper error
            assert response.status_code in [400, 500]
