"""
Enhanced Gemini Client with PDF support.
Optimized based on latest SDK best practices.
"""

from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import json
import io
from typing import Type, Optional, Any, Union
from pydantic import BaseModel, ValidationError
from pathlib import Path
from config import Config

load_dotenv()


class GeminiClientWithPDF:
    """
    Enhanced Gemini client that supports direct PDF upload.
    
    Optimizations:
    - Uses io.BytesIO for in-memory file handling (no temp files)
    - Leverages Streamlit's built-in MIME type detection
    - Compatible with latest Google GenAI SDK
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Optional API key. If not provided, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it in .env file or pass to constructor."
            )
        
        # Initialize the client
        self.client = genai.Client(api_key=self.api_key)

    def upload_streamlit_file(self, uploaded_file) -> Any:
        """
        Upload a Streamlit UploadedFile to Gemini.
        
        Optimized approach:
        - Uses io.BytesIO (no disk I/O)
        - Uses Streamlit's built-in MIME type detection
        - Works on all platforms
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Uploaded file object from Gemini
        """
        # 1. Get MIME type from Streamlit (it detects automatically)
        mime_type = uploaded_file.type if hasattr(uploaded_file, 'type') else None
        
        # 2. Fallback to extension-based detection if Streamlit doesn't provide type
        if not mime_type:
            suffix = Path(uploaded_file.name).suffix.lower()
            mime_type_map = {
                '.pdf': 'application/pdf',
                '.txt': 'text/plain',
                '.md': 'text/markdown',
                '.html': 'text/html',
                '.json': 'application/json',
            }
            mime_type = mime_type_map.get(suffix, 'application/pdf')
        
        # 3. Upload using BytesIO (no temp file needed)
        file_bytes = io.BytesIO(uploaded_file.getbuffer())
        
        # Try different API syntaxes based on SDK version
        try:
            # Method 1: Try with UploadFileConfig (newest SDK)
            uploaded = self.client.files.upload(
                file=file_bytes,
                config=types.UploadFileConfig(
                    mime_type=mime_type,
                    display_name=uploaded_file.name
                )
            )
        except (TypeError, AttributeError):
            # Method 2: Fallback to direct mime_type parameter
            try:
                uploaded = self.client.files.upload(
                    file=file_bytes,
                    mime_type=mime_type
                )
            except TypeError:
                # Method 3: Last resort - without explicit mime_type
                # (Some SDK versions might auto-detect)
                uploaded = self.client.files.upload(file=file_bytes)
        
        return uploaded

    def upload_file(self, file_path: str) -> Any:
        """
        Upload a file from disk to Gemini File API.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            Uploaded file object
        """
        # Determine mime type from file extension
        suffix = Path(file_path).suffix.lower()
        mime_type_map = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.html': 'text/html',
            '.json': 'application/json',
        }
        mime_type = mime_type_map.get(suffix, 'application/pdf')
        
        # Read file and upload using BytesIO
        with open(file_path, 'rb') as f:
            file_bytes = io.BytesIO(f.read())
        
        # Try different API syntaxes
        try:
            uploaded = self.client.files.upload(
                file=file_bytes,
                config=types.UploadFileConfig(
                    mime_type=mime_type,
                    display_name=Path(file_path).name
                )
            )
        except (TypeError, AttributeError):
            try:
                uploaded = self.client.files.upload(
                    file=file_bytes,
                    mime_type=mime_type
                )
            except TypeError:
                uploaded = self.client.files.upload(file=file_bytes)
        
        return uploaded

    def generate_with_file(
        self,
        prompt: str,
        file: Any,
        model: str = "gemini-2.0-flash-exp"
    ) -> str:
        """
        Generate response with a file (PDF) as context.
        
        Args:
            prompt: The prompt/instruction
            file: Uploaded file object from upload_file() or upload_streamlit_file()
            model: Gemini model identifier
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_uri(
                        file_uri=file.uri,
                        mime_type=file.mime_type
                    ),
                    prompt
                ]
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error with file: {str(e)}")

    def extract_json_from_pdf(
        self,
        prompt: str,
        uploaded_file,  # Streamlit UploadedFile
        schema: Optional[Type[BaseModel]] = None,
        model: str=Config.PRO_MODEL,
        strict: bool = True
    ) -> Any:
        """
        Extract JSON from a PDF using Gemini's native PDF understanding.
        
        Args:
            prompt: Extraction prompt (should instruct model to return JSON)
            uploaded_file: Streamlit UploadedFile object (PDF)
            schema: Optional Pydantic model for validation
            model: Gemini model to use
            strict: If True, raise exception on validation failure
            
        Returns:
            - If schema provided and validation succeeds: Pydantic model instance
            - If schema provided but strict=False and validation fails: raw dict
            - If no schema: raw dict
        """
        # Upload PDF to Gemini (optimized method)
        gemini_file = self.upload_streamlit_file(uploaded_file)
        
        # Generate with PDF context
        raw_text = self.generate_with_file(prompt, gemini_file, model)
        
        # Parse JSON
        try:
            parsed_json = json.loads(raw_text)
        except json.JSONDecodeError as e:
            # Try to extract JSON from markdown code blocks
            if "```json" in raw_text:
                try:
                    json_start = raw_text.index("```json") + 7
                    json_end = raw_text.index("```", json_start)
                    json_str = raw_text[json_start:json_end].strip()
                    parsed_json = json.loads(json_str)
                except (ValueError, json.JSONDecodeError):
                    raise ValueError(
                        f"Model did not return valid JSON: {e}\n\nRaw output:\n{raw_text[:500]}..."
                    )
            else:
                raise ValueError(
                    f"Model did not return valid JSON: {e}\n\nRaw output:\n{raw_text[:500]}..."
                )

        # Validate against schema if provided
        if schema:
            try:
                validated = schema.model_validate(parsed_json)
                return validated
            except ValidationError as e:
                if strict:
                    raise ValueError(f"Schema validation failed: {e}")
                else:
                    return parsed_json

        return parsed_json

    # Keep original text-based methods for backward compatibility
    def generate(self, prompt: str, model: str = "gemini-2.0-flash-exp") -> str:
        """Generate a raw text response from a Gemini model."""
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def extract_json(
        self,
        prompt: str,
        schema: Optional[Type[BaseModel]] = None,
        model: str = "gemini-2.0-flash-exp",
        strict: bool = True
    ) -> Any:
        """Extract JSON from text prompt."""
        raw_text = self.generate(prompt, model)
        
        try:
            parsed_json = json.loads(raw_text)
        except json.JSONDecodeError as e:
            if "```json" in raw_text:
                try:
                    json_start = raw_text.index("```json") + 7
                    json_end = raw_text.index("```", json_start)
                    json_str = raw_text[json_start:json_end].strip()
                    parsed_json = json.loads(json_str)
                except (ValueError, json.JSONDecodeError):
                    raise ValueError(f"Model did not return valid JSON: {e}")
            else:
                raise ValueError(f"Model did not return valid JSON: {e}")

        if schema:
            try:
                validated = schema.model_validate(parsed_json)
                return validated
            except ValidationError as e:
                if strict:
                    raise ValueError(f"Schema validation failed: {e}")
                else:
                    return parsed_json

        return parsed_json