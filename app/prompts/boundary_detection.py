"""
Boundary detection for unsupported questions.

This module detects questions that require clinical judgment
or fall outside ProtocolLens's scope.
"""

from typing import Tuple


# Patterns that indicate clinical judgment questions
UNSUPPORTED_PATTERNS = [
    'should i enroll',
    'should i join', 
    'am i eligible',
    'can i join this',
    'is this safe for',
    'better than',
    'will this work',
    'what are my chances',
    'prognosis',
    'should this patient',
    'is this patient eligible',
    'recommend enrolling'
]


def is_unsupported_question(question: str) -> Tuple[bool, str]:
    """
    Check if a question requires clinical judgment.
    
    Args:
        question: User's question text
        
    Returns:
        Tuple of (is_unsupported, reason)
        - is_unsupported: True if question is unsupported
        - reason: Type of unsupported question ('clinical_judgment' or 'personal_eligibility')
    """
    question_lower = question.lower()
    
    # Check for clinical judgment patterns
    is_clinical_judgment = any(
        pattern in question_lower 
        for pattern in UNSUPPORTED_PATTERNS
    )
    
    # Check for personal eligibility questions with "I" statements
    is_personal_eligibility = (
        ('am i' in question_lower or 'can i' in question_lower) and 
        ('eligible' in question_lower or 'qualify' in question_lower or 'join' in question_lower)
    )
    
    if is_clinical_judgment:
        return True, 'clinical_judgment'
    elif is_personal_eligibility:
        return True, 'personal_eligibility'
    else:
        return False, ''


def get_unsupported_message(reason: str = '') -> str:
    """
    Get the appropriate message for unsupported questions.
    
    Args:
        reason: Type of unsupported question
        
    Returns:
        Message explaining why question is unsupported
    """
    base_message = """ProtocolLens can tell you *what the protocol specifies*, but not:
- Whether a specific patient is eligible (investigator's role)
- Whether someone should enroll (personal/medical decision)
- Treatment safety or effectiveness (clinical assessment)

Would you like to rephrase your question to focus on what the protocol states?"""
    
    if reason == 'personal_eligibility':
        return """ProtocolLens cannot determine individual eligibility.

**What ProtocolLens CAN do:**
- Tell you what the protocol's eligibility criteria are
- Explain what tests or requirements are needed
- Clarify specific protocol terms

**What requires a healthcare professional:**
- Determining if YOU specifically are eligible
- Interpreting your medical records
- Making enrollment recommendations

Try asking: "What are the eligibility criteria?" or "What tests are required?"""
    
    elif reason == 'clinical_judgment':
        return """This question requires clinical judgment that ProtocolLens cannot provide.

**ProtocolLens provides:**
- What the protocol explicitly states
- Eligibility criteria as written
- Required procedures and tests

**Requires healthcare professional:**
- Patient-specific eligibility decisions
- Treatment recommendations
- Safety assessments
- Enrollment advice

Try rephrasing to ask about protocol requirements, not clinical decisions."""
    
    return base_message


def get_supported_question_examples(role: str) -> list:
    """
    Get example supported questions for each role.
    
    Args:
        role: User role (patient, physician, researcher)
        
    Returns:
        List of example questions
    """
    examples = {
        "patient": [
            "What are the eligibility criteria?",
            "What tests will I need?",
            "How long is the study?",
            "What is the visit schedule?"
        ],
        "physician": [
            "What is the minimum hemoglobin level required?",
            "Are patients with ECOG 2 excluded?",
            "What washout period is required?",
            "What assessments are done at baseline?"
        ],
        "researcher": [
            "Is this inclusion/exclusion too restrictive?",
            "Which criteria allow investigator discretion?",
            "What biomarkers define eligibility?",
            "Are there any unusual protocol requirements?"
        ]
    }
    return examples.get(role, examples["researcher"])


def get_unsupported_question_examples() -> list:
    """
    Get examples of unsupported questions.
    
    Returns:
        List of example unsupported questions
    """
    return [
        "Should patient X be enrolled? (investigator decision)",
        "What's the expected outcome? (speculative)"
    ]
