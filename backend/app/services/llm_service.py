"""
LLM service for interacting with language models (OpenAI, Ollama, or SageMaker)
"""
import boto3
import json
import httpx
import time
from typing import Dict, Optional, List
from app.config import settings
from openai import OpenAI
from app.logger import get_logger

logger = get_logger("llm_service")


class LLMService:
    """Service for LLM inference with fallback support"""

    def __init__(self):
        self.sagemaker_client = None
        self.endpoint_name = settings.SAGEMAKER_ENDPOINT_NAME
        self.openai_client = None
        self.ollama_available = False
        self.ollama_model = getattr(settings, 'OLLAMA_MODEL', 'llama2')
        self.ollama_url = getattr(settings, 'OLLAMA_URL', 'http://localhost:11434')
        
        # Determine which LLM provider to use
        self.provider = self._determine_provider()
        print(f"LLM Service initialized with provider: {self.provider}")

    def _determine_provider(self) -> str:
        """Determine which LLM provider to use based on availability"""
        
        # 1. Try OpenAI first if API key is provided and looks valid
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.startswith('sk-'):
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                # Quick validation - just create the client, don't make a call yet
                logger.info("OpenAI API key found and configured")
                return "openai"
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
        
        # 2. Try Ollama (local LLM)
        if self._check_ollama():
            logger.info(f"Ollama is available with model: {self.ollama_model}")
            return "ollama"
        
        # 3. Try SageMaker
        try:
            self.sagemaker_client = boto3.client(
                'sagemaker-runtime',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            logger.info("SageMaker client initialized")
            return "sagemaker"
        except Exception as e:
            logger.warning(f"SageMaker initialization failed: {e}")
        
        # 4. Fallback - will error when called
        logger.error("No LLM provider available!")
        return "none"
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running locally"""
        try:
            response = httpx.get(f"{self.ollama_url}/api/tags", timeout=2.0)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if not models:
                    logger.warning("Ollama is running but no models are installed")
                    return False
                
                # Get full model names (including :tag)
                model_names = [m.get('name', '') for m in models]
                logger.debug(f"Available Ollama models: {model_names}")
                
                # Check if requested model exists
                for name in model_names:
                    if self.ollama_model in name or name.split(':')[0] == self.ollama_model:
                        self.ollama_model = name  # Use full name with tag
                        self.ollama_available = True
                        logger.info(f"Using Ollama model: {self.ollama_model}")
                        return True
                
                # Use first available model as fallback
                self.ollama_model = model_names[0]
                self.ollama_available = True
                logger.info(f"Requested model not found, using: {self.ollama_model}")
                return True
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
        return False

    async def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        stop_sequences: Optional[List[str]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text using LLM with automatic fallback

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stop_sequences: Sequences to stop generation
            system_prompt: System prompt for context

        Returns:
            Generated text
        """
        temperature = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
        max_tokens = max_tokens if max_tokens is not None else settings.DEFAULT_MAX_TOKENS

        # Try providers in order with fallback
        providers = self._get_provider_order()
        last_error = None
        
        logger.debug(f"Starting LLM generation with provider order: {providers}")
        logger.debug(f"Prompt length: {len(prompt)} chars, temp: {temperature}, max_tokens: {max_tokens}")
        
        for provider in providers:
            try:
                start_time = time.time()
                logger.info(f"Attempting generation with {provider}...")
                
                if provider == "openai":
                    result = await self._generate_openai(prompt, temperature, max_tokens, stop_sequences, system_prompt)
                elif provider == "ollama":
                    result = await self._generate_ollama(prompt, temperature, max_tokens, stop_sequences, system_prompt)
                elif provider == "sagemaker":
                    result = await self._generate_sagemaker(prompt, temperature, max_tokens, stop_sequences)
                else:
                    continue
                
                elapsed = time.time() - start_time
                logger.info(f"✓ {provider} succeeded in {elapsed:.2f}s, response length: {len(result)} chars")
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.warning(f"✗ {provider} failed after {elapsed:.2f}s: {e}")
                last_error = e
                continue
        
        logger.error(f"All LLM providers failed. Last error: {last_error}")
        raise Exception(f"All LLM providers failed. Last error: {last_error}")
    
    def _get_provider_order(self) -> List[str]:
        """Get ordered list of providers to try"""
        if self.provider == "openai":
            return ["openai", "ollama", "sagemaker"]
        elif self.provider == "ollama":
            return ["ollama", "openai", "sagemaker"]
        elif self.provider == "sagemaker":
            return ["sagemaker", "openai", "ollama"]
        return ["ollama", "openai", "sagemaker"]
    
    async def _generate_ollama(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        stop_sequences: Optional[List[str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate using Ollama (local LLM)"""
        if not self.ollama_available:
            raise Exception("Ollama is not available")
        
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are an expert career coach."})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if stop_sequences:
            payload["options"]["stop"] = stop_sequences
        
        logger.debug(f"Calling Ollama model: {self.ollama_model}")
        logger.debug(f"Ollama payload: model={self.ollama_model}, messages={len(messages)}, temp={temperature}")
        
        try:
            # 5 minute timeout for complex prompts with local models
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json=payload
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"Ollama returned {response.status_code}: {error_text}")
                    raise Exception(f"Ollama returned {response.status_code}: {error_text}")
                
                result = response.json()
                content = result.get("message", {}).get("content", "")
                
                if not content:
                    logger.error(f"Ollama returned empty response: {result}")
                    raise Exception(f"Ollama returned empty response: {result}")
                
                # Log token usage if available
                eval_count = result.get("eval_count", "N/A")
                total_duration = result.get("total_duration", 0) / 1e9  # Convert to seconds
                logger.debug(f"Ollama response: {len(content)} chars, {eval_count} tokens, {total_duration:.2f}s")
                
                return content
                
        except httpx.TimeoutException:
            logger.error("Ollama request timed out (300s)")
            raise Exception("Ollama request timed out (300s). The model may be loading or the prompt is too long.")
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self.ollama_url}")
            raise Exception(f"Cannot connect to Ollama at {self.ollama_url}. Is it running?")
        except Exception as e:
            logger.error(f"Ollama API failed: {str(e)}")
            raise Exception(f"Ollama API failed: {str(e)}")

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
                if isinstance(result[0], dict) and 'generated_text' in result[0]:
                    return result[0]['generated_text']
                return str(result[0])
            elif isinstance(result, dict) and 'generated_text' in result:
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
        stop_sequences: Optional[List[str]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate using OpenAI API (fallback/development)"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY.")

            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({"role": "system", "content": "You are an expert career coach."})

            messages.append({"role": "user", "content": prompt})

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
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
        return len(text) // 4

    async def batch_generate(
        self,
        prompts: List[str],
        temperature: float = None,
        max_tokens: int = None
    ) -> List[str]:
        """Generate for multiple prompts (simple sequential for now)"""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, temperature, max_tokens)
            results.append(result)
        return results
