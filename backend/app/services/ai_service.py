import httpx
import json
import asyncio
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class AIService:
    """Service for interacting with OpenRouter AI models"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.models = [
            get_settings().primary_model,
            get_settings().secondary_model,
            get_settings().backup_model
        ]
        self.current_model_index = 0
        self.rate_limit_delay = 5  # seconds between requests
        
    async def generate_unit_tests(
        self, 
        source_code: str, 
        language: str, 
        framework: str,
        file_path: str,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """Generate unit tests for a given source code file"""
        
        prompt = self._create_test_generation_prompt(
            source_code, language, framework, file_path, dependencies
        )
        
        try:
            response = await self._make_ai_request(prompt)
            return self._extract_test_code(response, language)
            
        except Exception as e:
            logger.error(f"Error generating tests for {file_path}: {e}")
            raise
    
    async def analyze_code_structure(
        self, 
        source_code: str, 
        language: str,
        file_path: str
    ) -> Dict[str, Any]:
        """Analyze code structure to identify functions, classes, and dependencies"""
        
        prompt = self._create_analysis_prompt(source_code, language, file_path)
        
        try:
            response = await self._make_ai_request(prompt)
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Error analyzing code structure for {file_path}: {e}")
            raise
    
    async def generate_mock_objects(
        self, 
        dependencies: List[str], 
        language: str,
        framework: str
    ) -> str:
        """Generate mock objects for external dependencies"""
        
        prompt = self._create_mock_generation_prompt(dependencies, language, framework)
        
        try:
            response = await self._make_ai_request(prompt)
            return self._extract_mock_code(response, language)
            
        except Exception as e:
            logger.error(f"Error generating mocks: {e}")
            raise
    
    def _create_test_generation_prompt(
        self, 
        source_code: str, 
        language: str, 
        framework: str,
        file_path: str,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """Create a prompt for test generation"""
        
        framework_config = get_settings().supported_languages[language]
        
        prompt = f"""You are an expert software testing engineer. Generate comprehensive unit tests for the following {language} code using {framework}.

Source File: {file_path}
Framework: {framework}

Source Code:
```{language}
{source_code}
```

Requirements:
1. Follow the AAA pattern (Arrange, Act, Assert)
2. Test both positive and negative scenarios
3. Include edge cases and boundary testing
4. Use proper mocking for external dependencies
5. Ensure high test coverage
6. Write clear, readable test names
7. Follow {framework} best practices

{f'Dependencies to mock: {", ".join(dependencies) if dependencies else "None"}'}

Generate only the test code without any explanations. The test should be ready to run immediately."""

        return prompt
    
    def _create_analysis_prompt(self, source_code: str, language: str, file_path: str) -> str:
        """Create a prompt for code structure analysis"""
        
        prompt = f"""Analyze the following {language} code and provide a JSON response with the following structure:

```json
{{
    "functions": [
        {{
            "name": "function_name",
            "parameters": ["param1", "param2"],
            "return_type": "return_type",
            "complexity": "low|medium|high",
            "dependencies": ["dep1", "dep2"]
        }}
    ],
    "classes": [
        {{
            "name": "class_name",
            "methods": ["method1", "method2"],
            "properties": ["prop1", "prop2"],
            "inheritance": "parent_class",
            "dependencies": ["dep1", "dep2"]
        }}
    ],
    "dependencies": ["external_dep1", "external_dep2"],
    "complexity_score": 1-10,
    "test_scenarios": [
        "scenario1",
        "scenario2"
    ]
}}
```

Source Code:
```{language}
{source_code}
```

File: {file_path}

Provide only the JSON response without any additional text."""

        return prompt
    
    def _create_mock_generation_prompt(
        self, 
        dependencies: List[str], 
        language: str,
        framework: str
    ) -> str:
        """Create a prompt for mock generation"""
        
        prompt = f"""Generate mock objects for the following {language} dependencies using {framework}:

Dependencies: {", ".join(dependencies)}

Requirements:
1. Create realistic mock responses
2. Handle different scenarios (success, error, edge cases)
3. Use proper {framework} mocking syntax
4. Include type hints if applicable
5. Make mocks reusable and maintainable

Generate only the mock code without explanations."""

        return prompt
    
    async def _make_ai_request(self, prompt: str) -> str:
        """Make a request to the AI model with fallback strategy"""
        
        for attempt in range(len(self.models)):
            model = self.models[self.current_model_index]
            
            try:
                logger.info(f"Attempting AI request with model: {model}")
                async with httpx.AsyncClient(timeout=30.0) as client:  # Reduced timeout to 30 seconds
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://ai-unit-testing-agent.com",
                            "X-Title": "AI Unit Testing Agent"
                        },
                        json={
                            "model": model,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are an expert software testing engineer specializing in unit testing and test automation."
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "max_tokens": get_settings().max_tokens_per_request,
                            "temperature": get_settings().temperature
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"AI request successful with model: {model}")
                        return data["choices"][0]["message"]["content"]
                    
                    elif response.status_code == 429:  # Rate limit
                        logger.warning(f"Rate limit hit for model {model}, trying next model")
                        self.current_model_index = (self.current_model_index + 1) % len(self.models)
                        await asyncio.sleep(self.rate_limit_delay)
                        continue
                    
                    else:
                        logger.error(f"API request failed for model {model}: {response.status_code} - {response.text}")
                        self.current_model_index = (self.current_model_index + 1) % len(self.models)
                        continue
                        
            except Exception as e:
                logger.error(f"Error with model {model}: {e}")
                self.current_model_index = (self.current_model_index + 1) % len(self.models)
                continue
        
        raise Exception("All AI models failed to respond")
    
    def _extract_test_code(self, response: str, language: str) -> str:
        """Extract test code from AI response"""
        # Remove markdown code blocks if present
        if "```" in response:
            lines = response.split("\n")
            in_code_block = False
            code_lines = []
            
            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    code_lines.append(line)
            
            return "\n".join(code_lines)
        
        return response.strip()
    
    def _extract_mock_code(self, response: str, language: str) -> str:
        """Extract mock code from AI response"""
        return self._extract_test_code(response, language)
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the analysis response from AI"""
        try:
            # Try to extract JSON from the response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis response: {e}")
            # Return a default structure
            return {
                "functions": [],
                "classes": [],
                "dependencies": [],
                "complexity_score": 5,
                "test_scenarios": []
            }
