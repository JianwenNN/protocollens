import pytest
from app.orchestrator import ProtocolOrchestrator
from app.schemas.trial import TrialObject
import json


# Sample minimal protocol for testing
SAMPLE_PROTOCOL = """
CLINICAL TRIAL PROTOCOL

Title: A Phase 2 Study of Drug X in Non-Small Cell Lung Cancer

Study Design:
This is a randomized, double-blind, placebo-controlled Phase 2 study.

Eligibility Criteria:

Inclusion Criteria:
1. Age ≥ 18 years
2. Histologically confirmed non-small cell lung cancer (NSCLC)
3. ECOG performance status 0-1
4. Adequate organ function

Exclusion Criteria:
1. Prior treatment with Drug X
2. Active brain metastases
3. Pregnant or breastfeeding women
4. Uncontrolled intercurrent illness

Primary Endpoint:
Progression-free survival (PFS) at 6 months

Secondary Endpoints:
1. Overall survival
2. Objective response rate
3. Safety and tolerability
"""


class TestProtocolOrchestrator:
    """Test suite for ProtocolOrchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing"""
        return ProtocolOrchestrator(model="gemini-3-flash-preview")
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes correctly"""
        assert orchestrator is not None
        assert orchestrator.client is not None
        assert orchestrator.model == "gemini-3-flash-preview"
    
    def test_is_valid_trial_object(self, orchestrator):
        """Test trial object validation"""
        valid_trial = {
            "trial_metadata": {},
            "study_design": {},
            "population": {},
            "eligibility": {"inclusion": {}, "exclusion": {}},
            "interventions": [],
            "endpoints": {},
            "study_timeline": {},
            "safety": {},
            "sponsors_locations": {}
        }
        assert orchestrator._is_valid_trial_object(valid_trial) is True
        
        # Test invalid trial (missing keys)
        invalid_trial = {"trial_metadata": {}}
        assert orchestrator._is_valid_trial_object(invalid_trial) is False
        
        # Test invalid trial (wrong type)
        assert orchestrator._is_valid_trial_object("not a dict") is False
    
    @pytest.mark.skip(reason="Requires API key and makes real API calls")
    def test_run_extraction(self, orchestrator):
        """Test full extraction pipeline (requires API key)"""
        result = orchestrator.run(SAMPLE_PROTOCOL)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "extraction_method" in result
        
        # If single-pass succeeded, check structure
        if result.get("extraction_method") == "single_pass":
            assert "eligibility" in result
            assert "trial_metadata" in result
    
    @pytest.mark.skip(reason="Requires API key and makes real API calls")
    def test_fallback_pipeline(self, orchestrator):
        """Test fallback extraction pipeline (requires API key)"""
        result = orchestrator.run(SAMPLE_PROTOCOL, prefer_fallback=True)
        
        assert isinstance(result, dict)
        assert result.get("extraction_method") == "fallback_pipeline"
        assert "sections" in result
        assert "eligibility" in result
    
    def test_empty_protocol_handling(self, orchestrator):
        """Test handling of empty protocol text"""
        with pytest.raises(ValueError, match="Protocol text is empty"):
            orchestrator.run("")
        
        with pytest.raises(ValueError, match="Protocol text is empty"):
            orchestrator.run("   ")
    
    @pytest.mark.skip(reason="Requires API key and makes real API calls")
    def test_ask_question(self, orchestrator):
        """Test Q&A functionality (requires API key)"""
        # First extract trial
        result = orchestrator.run(SAMPLE_PROTOCOL)
        
        # Then ask a question
        answer = orchestrator.ask_question(
            result, 
            "What is the study phase?"
        )
        
        assert isinstance(answer, str)
        assert len(answer) > 0


class TestTrialObjectSchema:
    """Test Pydantic schema validation"""
    
    def test_trial_object_creation(self):
        """Test creating a minimal valid TrialObject"""
        from app.schemas.trial import (
            TrialObject, EligibilityCriteria, 
            EligibilityCriteriaDetail
        )
        
        trial = TrialObject(
            eligibility=EligibilityCriteria(
                inclusion=EligibilityCriteriaDetail(
                    criteria=[],
                    confidence=0.0,
                    source_sections=[]
                ),
                exclusion=EligibilityCriteriaDetail(
                    criteria=[],
                    confidence=0.0,
                    source_sections=[]
                )
            )
        )
        
        assert trial is not None
        assert trial.eligibility is not None
    
    def test_atomic_criterion_creation(self):
        """Test creating AtomicCriterion"""
        from app.schemas.trial import AtomicCriterion
        
        criterion = AtomicCriterion(
            id="INC_01",
            text="Age >= 18 years",
            category="age",
            operator=">=",
            value="18",
            confidence=1.0
        )
        
        assert criterion.id == "INC_01"
        assert criterion.category == "age"
        assert criterion.confidence == 1.0
    
    def test_confidence_validation(self):
        """Test that confidence is validated to be between 0 and 1"""
        from app.schemas.trial import AtomicCriterion
        from pydantic import ValidationError
        
        # Valid confidence
        criterion = AtomicCriterion(
            id="INC_01",
            text="Test",
            category="other",
            operator="none",
            value="",
            confidence=0.5
        )
        assert criterion.confidence == 0.5
        
        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            AtomicCriterion(
                id="INC_01",
                text="Test",
                category="other",
                operator="none",
                value="",
                confidence=1.5
            )
        
        # Invalid confidence (negative)
        with pytest.raises(ValidationError):
            AtomicCriterion(
                id="INC_01",
                text="Test",
                category="other",
                operator="none",
                value="",
                confidence=-0.1
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
