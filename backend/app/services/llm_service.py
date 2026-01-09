"""
LLM service for interacting with language models (SageMaker or OpenAI)
"""
import boto3
import json
from typing import Dict, Optional, List
from app.config import settings
import openai


class LLMService:
    """Service for LLM inference"""

    def __init__(self):
        self.sagemaker_client = None
        self.endpoint_name = settings.SAGEMAKER_ENDPOINT_NAME
        self.use_openai = settings.USE_OPENAI_FALLBACK

        # Initialize SageMaker client if credentials available
        try:
            self.sagemaker_client = boto3.client(
                'sagemaker-runtime',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            print(f"Warning: Could not initialize SageMaker client: {e}")
            self.use_openai = True

        # Set OpenAI API key
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY

    async def generate(
        self,
        prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        stop_sequences: Optional[List[str]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text using LLM

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

        if self.use_openai or not self.sagemaker_client:
            return await self._generate_openai(prompt, temperature, max_tokens, stop_sequences, system_prompt)
        else:
            try:
                return await self._generate_sagemaker(prompt, temperature, max_tokens, stop_sequences)
            except Exception as e:
                print(f"SageMaker inference failed: {e}, falling back to OpenAI")
                return await self._generate_openai(prompt, temperature, max_tokens, stop_sequences, system_prompt)

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
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({"role": "system", "content": "You are an expert career coach."})

            messages.append({"role": "user", "content": prompt})

            response = openai.ChatCompletion.create(
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
