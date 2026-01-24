from app.utils.gemini_client import GeminiClient
from app.schemas.trial import (
    TrialObject, 
    SegmentedSections,
    EligibilityCriteriaDetail
)
from pathlib import Path
import json
from typing import Dict, Any


class ProtocolOrchestrator:
    """
    Orchestrates multi-stage extraction of clinical trial information
    from unstructured protocol documents.
    
    Supports two extraction paths:
    1. Single-pass: Direct extraction to complete TrialObject
    2. Multi-stage fallback: Section segmentation → criteria extraction
    """

    def __init__(self, model: str = "gemini-3-flash-preview"):
        """
        Initialize orchestrator.
        
        Args:
            model: Gemini model identifier to use for extraction
        """
        self.client = GeminiClient()
        self.model = model
        self.prompts_dir = Path("app/prompts")

    # ========== PRIMARY PATH: Single-pass extraction ==========

    def _extract_trial_object(self, protocol_text: str) -> Dict[str, Any]:
        """
        Extract complete trial object in a single pass.
        
        Args:
            protocol_text: Full protocol document text
            
        Returns:
            dict: Complete trial object as dictionary
            
        Raises:
            ValueError: If extraction fails or returns invalid structure
        """
        prompt_path = self.prompts_dir / "extract_trial_object.txt"
        prompt_template = prompt_path.read_text(encoding='utf-8')
        prompt = prompt_template.replace("{protocol_text}", protocol_text)

        # Extract with schema validation
        trial_obj = self.client.extract_json(
            prompt=prompt,
            schema=TrialObject,
            model=self.model,
            strict=True
        )

        # Convert Pydantic model to dict for consistent interface
        trial_dict = trial_obj.model_dump() if hasattr(trial_obj, 'model_dump') else trial_obj

        # Validate structure
        if not self._is_valid_trial_object(trial_dict):
            raise ValueError("Extracted trial object is missing required fields")

        return trial_dict

    def _is_valid_trial_object(self, trial: Dict) -> bool:
        """
        Validate that trial object has all required top-level keys.
        
        Args:
            trial: Trial object dictionary
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_keys = [
            "trial_metadata",
            "study_design",
            "population",
            "eligibility",
            "interventions",
            "endpoints",
            "study_timeline",
            "safety",
            "sponsors_locations"
        ]
        
        if not isinstance(trial, dict):
            return False
            
        for key in required_keys:
            if key not in trial:
                return False
                
        # Additional validation: eligibility must have inclusion/exclusion
        if "eligibility" in trial:
            eligibility = trial["eligibility"]
            if not isinstance(eligibility, dict):
                return False
            if "inclusion" not in eligibility or "exclusion" not in eligibility:
                return False
                
        return True

    # ========== FALLBACK PATH: Multi-stage extraction ==========

    def _fallback_pipeline(self, protocol_text: str) -> Dict[str, Any]:
        """
        Legacy multi-step extraction pipeline.
        
        Used as fallback when single-pass extraction fails.
        
        Args:
            protocol_text: Full protocol document text
            
        Returns:
            dict: Partial extraction result with sections and eligibility
        """
        # Stage 1: Segment sections
        sections = self._segment_sections(protocol_text)
        
        # Stage 2: Extract eligibility criteria
        eligibility = self._extract_eligibility(sections)

        return {
            "sections": sections,
            "eligibility": eligibility,
            "extraction_method": "fallback_pipeline",
            "note": "Multi-stage fallback extraction used (single-pass failed)"
        }

    def _segment_sections(self, protocol_text: str) -> Dict[str, Any]:
        """
        Stage 1: Extract semantic sections from protocol.
        
        Args:
            protocol_text: Full protocol document text
            
        Returns:
            dict: Segmented sections with metadata
        """
        prompt_path = self.prompts_dir / "01_section_segmentation.txt"
        prompt_template = prompt_path.read_text(encoding='utf-8')
        prompt = prompt_template.replace("{protocol_text}", protocol_text)

        # Extract without strict schema validation (more permissive)
        result = self.client.extract_json(
            prompt=prompt,
            schema=None,  # Don't enforce strict schema here
            model=self.model,
            strict=False
        )

        # Validate and extract sections
        if isinstance(result, dict) and "sections" in result:
            return result["sections"]
        
        # Fallback: return empty sections
        return {
            "inclusion_criteria": {"text": "", "confidence": 0.0, "source_sections": []},
            "exclusion_criteria": {"text": "", "confidence": 0.0, "source_sections": []},
            "objectives": {"text": "", "confidence": 0.0, "source_sections": []},
            "endpoints": {"text": "", "confidence": 0.0, "source_sections": []}
        }

    def _extract_eligibility(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 2: Extract structured eligibility criteria from segmented sections.
        
        Args:
            sections: Segmented sections from stage 1
            
        Returns:
            dict: Structured eligibility criteria
        """
        return {
            "inclusion": self._extract_single_criteria(
                section=sections.get("inclusion_criteria", {}),
                prompt_filename="02_inclusion_criteria_extraction.txt"
            ),
            "exclusion": self._extract_single_criteria(
                section=sections.get("exclusion_criteria", {}),
                prompt_filename="03_exclusion_criteria_extraction.txt"
            )
        }

    def _extract_single_criteria(
        self, 
        section: Dict[str, Any], 
        prompt_filename: str
    ) -> Dict[str, Any]:
        """
        Extract atomic criteria from a single section (inclusion or exclusion).
        
        Args:
            section: Section dictionary with 'text' key
            prompt_filename: Name of prompt file to use
            
        Returns:
            dict: Extracted criteria with metadata
        """
        # Get section text
        text = section.get("text", "").strip()
        
        # If no text, return empty result
        if not text:
            return {
                "criteria": [],
                "confidence": 0.0,
                "source_sections": section.get("source_sections", [])
            }

        # Load prompt template
        prompt_path = self.prompts_dir / prompt_filename
        prompt_template = prompt_path.read_text(encoding='utf-8')
        prompt = prompt_template.replace("{text}", text)

        # Extract criteria WITH schema validation to enforce source_evidence
        try:
            result_obj = self.client.extract_json(
                prompt=prompt,
                schema=EligibilityCriteriaDetail,  # ← Use schema to enforce structure!
                model=self.model,
                strict=False  # Allow partial data but validate structure
            )
            
            # Convert to dict
            result = result_obj.model_dump() if hasattr(result_obj, 'model_dump') else result_obj
            
        except Exception as e:
            # Fallback if schema validation fails
            print(f"⚠️ Schema validation failed for {prompt_filename}: {e}")
            result = self.client.extract_json(
                prompt=prompt,
                schema=None,
                model=self.model,
                strict=False
            )

        # Return with default values if extraction incomplete
        return {
            "criteria": result.get("criteria", []),
            "confidence": result.get("confidence", 0.0),
            "source_sections": result.get("source_sections", section.get("source_sections", []))
        }

    # ========== PUBLIC API ==========

    def run(self, protocol_text: str, prefer_fallback: bool = False) -> Dict[str, Any]:
        """
        Execute protocol extraction.
        
        Attempts single-pass extraction by default, falls back to multi-stage
        pipeline on failure.
        
        Args:
            protocol_text: Full protocol document text
            prefer_fallback: If True, skip single-pass and use fallback directly
            
        Returns:
            dict: Extracted trial information
            
        Raises:
            ValueError: If both extraction methods fail
        """
        # Validate input
        if not protocol_text or not protocol_text.strip():
            raise ValueError("Protocol text is empty")

        # Option to force fallback (useful for testing)
        if prefer_fallback:
            return self._fallback_pipeline(protocol_text)

        # Try single-pass extraction first
        try:
            result = self._extract_trial_object(protocol_text)
            result["extraction_method"] = "single_pass"
            return result
            
        except Exception as single_pass_error:
            # Log the error (in production, use proper logging)
            print(f"Single-pass extraction failed: {single_pass_error}")
            
            # Try fallback pipeline
            try:
                fallback_result = self._fallback_pipeline(protocol_text)
                fallback_result["single_pass_error"] = str(single_pass_error)
                return fallback_result
                
            except Exception as fallback_error:
                # Both methods failed
                raise ValueError(
                    f"All extraction methods failed.\n"
                    f"Single-pass error: {single_pass_error}\n"
                    f"Fallback error: {fallback_error}"
                )

    def ask_question(self, trial_json: Dict[str, Any], question: str) -> str:
        """
        Answer a question about an extracted trial.
        
        Args:
            trial_json: Extracted trial object
            question: Question to answer
            
        Returns:
            str: Answer based on trial data
        """
        prompt_path = self.prompts_dir / "ask_from_trial.txt"
        prompt_template = prompt_path.read_text(encoding='utf-8')
        
        prompt = prompt_template.replace("{trial_json}", json.dumps(trial_json, indent=2))
        prompt = prompt.replace("{question}", question)
        
        return self.client.generate(prompt, model=self.model)
