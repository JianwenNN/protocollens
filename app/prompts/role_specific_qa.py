"""
Role-specific Q&A prompt generation.

This module generates context-aware prompts based on user role
(patient, physician, or researcher) for answering protocol questions.
"""

from typing import Dict, List, Any


# Role-specific contexts
ROLE_CONTEXTS = {
    "patient": """You are answering for a PATIENT who wants to understand the trial.
- Use clear, simple language (avoid jargon)
- Focus on practical information (what they need to know/do)
- Do NOT provide medical advice
- Encourage consulting with healthcare professionals
- Be compassionate and supportive""",
    
    "physician": """You are answering for a PHYSICIAN who is screening patients.
- Use precise medical terminology
- Focus on protocol-specified criteria and procedures
- Provide exact protocol requirements
- Note any ambiguities that require investigator judgment
- Be concise and factual""",
    
    "researcher": """You are answering for a CLINICAL RESEARCHER analyzing the protocol.
- Use analytical language
- Compare to standard trial designs when relevant
- Identify restrictive vs permissive elements
- Note unusual or noteworthy features
- Provide context on protocol design choices"""
}


def format_criteria_list(criteria: List[Dict[str, Any]]) -> str:
    """
    Format a list of criteria into readable text.
    
    Args:
        criteria: List of criterion dictionaries
        
    Returns:
        Formatted string of criteria
    """
    if not criteria:
        return "Not specified"
    
    formatted = []
    for i, crit in enumerate(criteria, 1):
        text = crit.get('text', 'N/A')
        category = crit.get('category', 'N/A')
        formatted.append(f"{i}. {text} (Category: {category})")
    
    return "\n".join(formatted)


def get_role_specific_qa_prompt(
    question: str, 
    trial_json: Dict[str, Any], 
    user_role: str
) -> str:
    """
    Generate a role-specific Q&A prompt.
    
    Args:
        question: User's question about the protocol
        trial_json: Complete trial object as dictionary
        user_role: One of 'patient', 'physician', or 'researcher'
        
    Returns:
        Complete prompt string for LLM
    """
    # Extract key information
    eligibility = trial_json.get('eligibility', {})
    inclusion = eligibility.get('inclusion', {}).get('criteria', [])
    exclusion = eligibility.get('exclusion', {}).get('criteria', [])
    metadata = trial_json.get('trial_metadata', {})
    design = trial_json.get('study_design', {})
    endpoints = trial_json.get('endpoints', {})
    timeline = trial_json.get('study_timeline', {})
    population = trial_json.get('population', {})
    
    # Format criteria
    inclusion_str = format_criteria_list(inclusion)
    exclusion_str = format_criteria_list(exclusion)
    
    # Get role-specific context
    context = ROLE_CONTEXTS.get(user_role, ROLE_CONTEXTS["researcher"])
    
    # Build prompt
    prompt = f"""{context}

TRIAL INFORMATION:

Study Details:
- Title: {metadata.get('title', 'Not specified')}
- Phase: {metadata.get('phase', 'Not specified')}
- Design: {design.get('type', 'Not specified')}
- Indication: {population.get('indication', 'Not specified')}

INCLUSION CRITERIA:
{inclusion_str}

EXCLUSION CRITERIA:
{exclusion_str}

ENDPOINTS:
- Primary: {', '.join(endpoints.get('primary', [])) if endpoints.get('primary') else 'Not specified'}
- Secondary: {', '.join(endpoints.get('secondary', [])[:3]) if endpoints.get('secondary') else 'Not specified'}

STUDY TIMELINE:
- Treatment Duration: {timeline.get('treatment_duration', 'Not specified')}
- Follow-up: {timeline.get('follow_up_duration', 'Not specified')}

USER'S QUESTION:
{question}

INSTRUCTIONS:
1. Answer based ONLY on the protocol information provided above
2. If the question asks for comparison or analysis (e.g., "Is this restrictive?"), provide thoughtful analysis with specific examples
3. If the information is not in the protocol, say "Not specified in the protocol"
4. For clinical researcher questions about restrictiveness/design, compare to typical trials in this phase and indication
5. Do NOT make up information
6. Do NOT provide medical advice or clinical decisions
7. End with: "This information is from the protocol and does not constitute medical advice."

YOUR ANSWER:"""
    
    return prompt


def get_role_description(role: str) -> str:
    """
    Get a brief description of what each role focuses on.
    
    Args:
        role: User role (patient, physician, researcher)
        
    Returns:
        Description string
    """
    descriptions = {
        "patient": "Simple language, practical information, what you need to know",
        "physician": "Medical terminology, exact requirements, clinical procedures",
        "researcher": "Analytical perspective, protocol design, comparative analysis"
    }
    return descriptions.get(role, descriptions["researcher"])
