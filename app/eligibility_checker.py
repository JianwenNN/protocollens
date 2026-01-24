"""
Intelligent Eligibility Checker for Clinical Trials

This module provides smart eligibility assessment that:
1. Matches patient profile against inclusion criteria
2. Identifies which criteria are satisfied, uncertain, or violated
3. Provides structured, actionable feedback
"""

from typing import Dict, List, Any, Optional
from app.utils.gemini_client import GeminiClient
import json


class EligibilityChecker:
    """
    Smart eligibility checker that provides detailed assessment
    based on partial patient information.
    """
    
    def __init__(self, model: str = "gemini-3-flash-preview"):
        self.client = GeminiClient()
        self.model = model
    
    def check_eligibility(
        self,
        trial_data: Dict[str, Any],
        patient_profile: Dict[str, Any],
        user_role: str = "patient"
    ) -> Dict[str, Any]:
        """
        Perform intelligent eligibility check.
        
        Args:
            trial_data: Complete trial object with inclusion/exclusion criteria
            patient_profile: Patient information provided by user
            user_role: Role of the user (patient, physician, researcher)
            
        Returns:
            Structured eligibility assessment
        """
        prompt = self._build_eligibility_prompt(trial_data, patient_profile, user_role)
        
        response_text = self.client.generate(prompt, model=self.model)
        
        # Try to parse as JSON, fallback to text
        try:
            # Extract JSON if wrapped in markdown
            if "```json" in response_text:
                start = response_text.index("```json") + 7
                end = response_text.index("```", start)
                json_str = response_text[start:end].strip()
                result = json.loads(json_str)
            else:
                result = json.loads(response_text)
        except:
            # Fallback to text response
            result = {"raw_response": response_text}
        
        return result
    
    def _build_eligibility_prompt(
        self,
        trial_data: Dict[str, Any],
        patient_profile: Dict[str, Any],
        user_role: str
    ) -> str:
        """Build the eligibility assessment prompt"""
        
        # Extract criteria
        eligibility = trial_data.get("eligibility", {})
        inclusion = eligibility.get("inclusion", {}).get("criteria", [])
        exclusion = eligibility.get("exclusion", {}).get("criteria", [])
        
        # Format criteria for prompt
        inclusion_text = self._format_criteria_list(inclusion, "INC")
        exclusion_text = self._format_criteria_list(exclusion, "EXC")
        
        # Format patient profile
        profile_text = self._format_patient_profile(patient_profile)
        
        # Build role-specific instructions
        role_instructions = self._get_role_instructions(user_role)
        
        prompt = f"""You are an expert clinical trial eligibility assessor.

{role_instructions}

TRIAL INCLUSION CRITERIA:
{inclusion_text}

TRIAL EXCLUSION CRITERIA:
{exclusion_text}

PATIENT PROFILE PROVIDED:
{profile_text}

YOUR TASK:
Analyze the patient profile against the trial criteria and provide a structured assessment.

CRITICAL RULES:
1. Only assess criteria where you have relevant information
2. Be explicit about what you CANNOT assess due to missing information
3. Do NOT make assumptions or guesses about missing information
4. Be conservative - when in doubt, mark as "cannot assess"
5. Provide clear reasoning for each assessment

OUTPUT FORMAT (JSON):
{{
  "inclusion_assessment": [
    {{
      "criterion_id": "INC_01",
      "criterion_text": "Age >= 18 years",
      "status": "satisfied|not_satisfied|cannot_assess",
      "reasoning": "Patient is 65 years old, which satisfies the >= 18 requirement",
      "patient_value": "65 years"
    }}
  ],
  "exclusion_assessment": [
    {{
      "criterion_id": "EXC_01",
      "criterion_text": "Pregnant or breastfeeding",
      "status": "triggered|not_triggered|cannot_assess",
      "reasoning": "Cannot assess - pregnancy status not provided",
      "patient_value": "unknown"
    }}
  ],
  "overall_assessment": {{
    "likely_eligible": true|false|uncertain,
    "confidence": "high|medium|low",
    "summary": "Brief summary of eligibility status",
    "missing_critical_info": ["List of critical missing information"],
    "next_steps": "Recommended next steps for the user"
  }}
}}

Respond ONLY with valid JSON. Do not include any text before or after the JSON.
"""
        
        return prompt
    
    def _format_criteria_list(self, criteria: List[Dict], prefix: str) -> str:
        """Format criteria list for prompt"""
        if not criteria:
            return "None specified"
        
        formatted = []
        for i, criterion in enumerate(criteria, 1):
            crit_id = criterion.get("id", f"{prefix}_{i:02d}")
            text = criterion.get("text", "N/A")
            category = criterion.get("category", "other")
            formatted.append(f"{crit_id}. [{category}] {text}")
        
        return "\n".join(formatted)
    
    def _format_patient_profile(self, profile: Dict[str, Any]) -> str:
        """Format patient profile for prompt"""
        if not profile:
            return "No information provided"
        
        formatted = []
        for key, value in profile.items():
            if value:  # Only include non-empty values
                formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted) if formatted else "No information provided"
    
    def _get_role_instructions(self, role: str) -> str:
        """Get role-specific instructions"""
        if role == "patient":
            return """You are speaking to a PATIENT who wants to know if they might qualify for this trial.
- Use clear, compassionate language
- Avoid medical jargon where possible
- Emphasize the need to consult with their doctor
- Be encouraging but honest about eligibility"""
        
        elif role == "physician":
            return """You are speaking to a PHYSICIAN who is screening a patient for this trial.
- Use precise medical terminology
- Provide detailed clinical reasoning
- Highlight specific tests or assessments needed
- Note any borderline cases that need clinical judgment"""
        
        elif role == "researcher":
            return """You are speaking to a CLINICAL RESEARCHER who is reviewing trial recruitment.
- Focus on protocol compliance
- Highlight any protocol ambiguities
- Provide statistical context where relevant
- Note any criteria that may need clarification"""
        
        else:
            return "Provide a balanced, professional assessment."


def format_eligibility_result(result: Dict[str, Any], user_role: str) -> str:
    """
    Format eligibility result for display in Streamlit.
    
    Args:
        result: The eligibility assessment result
        user_role: Role of the user (for customized formatting)
        
    Returns:
        Markdown-formatted string for display
    """
    if "raw_response" in result:
        # Fallback if JSON parsing failed
        return result["raw_response"]
    
    output = []
    
    # Overall assessment
    overall = result.get("overall_assessment", {})
    likely_eligible = overall.get("likely_eligible", "uncertain")
    confidence = overall.get("confidence", "unknown")
    summary = overall.get("summary", "")
    
    # Header based on eligibility
    if likely_eligible == True:
        output.append("## ✅ Likely Eligible")
        output.append(f"**Confidence:** {confidence.upper()}")
    elif likely_eligible == False:
        output.append("## ❌ Likely Not Eligible")
        output.append(f"**Confidence:** {confidence.upper()}")
    else:
        output.append("## ⚠️ Eligibility Uncertain")
        output.append(f"**Confidence:** {confidence.upper()}")
    
    output.append(f"\n{summary}\n")
    
    # Inclusion criteria assessment
    output.append("### ✅ Inclusion Criteria Assessment")
    inclusion = result.get("inclusion_assessment", [])
    
    if inclusion:
        satisfied = [c for c in inclusion if c.get("status") == "satisfied"]
        not_satisfied = [c for c in inclusion if c.get("status") == "not_satisfied"]
        cannot_assess = [c for c in inclusion if c.get("status") == "cannot_assess"]
        
        if satisfied:
            output.append("\n**✅ Satisfied:**")
            for c in satisfied:
                output.append(f"- **{c['criterion_id']}**: {c['criterion_text']}")
                output.append(f"  - *{c['reasoning']}*")
        
        if not_satisfied:
            output.append("\n**❌ Not Satisfied:**")
            for c in not_satisfied:
                output.append(f"- **{c['criterion_id']}**: {c['criterion_text']}")
                output.append(f"  - *{c['reasoning']}*")
        
        if cannot_assess:
            output.append("\n**⚠️ Cannot Assess (Missing Information):**")
            for c in cannot_assess:
                output.append(f"- **{c['criterion_id']}**: {c['criterion_text']}")
                output.append(f"  - *{c['reasoning']}*")
    else:
        output.append("No inclusion criteria assessed")
    
    # Exclusion criteria assessment
    output.append("\n### ❌ Exclusion Criteria Assessment")
    exclusion = result.get("exclusion_assessment", [])
    
    if exclusion:
        triggered = [c for c in exclusion if c.get("status") == "triggered"]
        not_triggered = [c for c in exclusion if c.get("status") == "not_triggered"]
        cannot_assess = [c for c in exclusion if c.get("status") == "cannot_assess"]
        
        if triggered:
            output.append("\n**⛔ Triggered (Disqualifying):**")
            for c in triggered:
                output.append(f"- **{c['criterion_id']}**: {c['criterion_text']}")
                output.append(f"  - *{c['reasoning']}*")
        
        if not_triggered:
            output.append("\n**✅ Not Triggered:**")
            for c in not_triggered:
                output.append(f"- **{c['criterion_id']}**: {c['criterion_text']}")
                output.append(f"  - *{c['reasoning']}*")
        
        if cannot_assess:
            output.append("\n**⚠️ Cannot Assess:**")
            for c in cannot_assess:
                output.append(f"- **{c['criterion_id']}**: {c['criterion_text']}")
    else:
        output.append("No exclusion criteria assessed")
    
    # Missing critical information
    missing = overall.get("missing_critical_info", [])
    if missing:
        output.append("\n### 📋 Missing Critical Information")
        for item in missing:
            output.append(f"- {item}")
    
    # Next steps
    next_steps = overall.get("next_steps", "")
    if next_steps:
        output.append(f"\n### 🎯 Recommended Next Steps")
        output.append(next_steps)
    
    return "\n".join(output)
