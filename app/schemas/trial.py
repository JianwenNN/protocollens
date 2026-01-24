from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ---------- Source Evidence Schema ----------

class SourceEvidence(BaseModel):
    """
    Source attribution for extracted information.
    Enables verification and traceability of extractions.
    """
    section: str = Field(..., description="Section name where found (e.g., '4.1 Inclusion Criteria')")
    quote: str = Field(..., description="Verbatim quote from protocol (keep under 200 chars)")
    page: Optional[int] = Field(None, description="Approximate page number if available")


# ---------- Atomic Criterion Schema ----------

class AtomicCriterion(BaseModel):
    """
    Represents a single, independent eligibility criterion.
    """
    id: str = Field(..., description="Unique identifier (e.g., INC_01, EXC_01)")
    text: str = Field(..., description="Verbatim criterion text")
    category: str = Field(
        ...,
        description="Category: age, diagnosis, disease_stage, biomarker, performance_status, "
                   "prior_therapy, lab_value, comorbidity, medication, pregnancy, "
                   "infection, reproductive, consent, safety, other"
    )
    operator: str = Field(
        ...,
        description="Operator: >=, <=, =, in_range, required, prohibited, none"
    )
    value: str = Field(default="", description="Value if applicable, else empty string")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    source_evidence: List[SourceEvidence] = Field(
        default_factory=list,
        description="Source attribution - exact quotes and locations from protocol"
    )


# ---------- Eligibility Schema ----------

class EligibilityCriteriaDetail(BaseModel):
    """
    Container for inclusion or exclusion criteria.
    """
    criteria: List[AtomicCriterion] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_sections: List[str] = Field(default_factory=list)


class EligibilityCriteria(BaseModel):
    """
    Complete eligibility criteria for the trial.
    """
    inclusion: EligibilityCriteriaDetail
    exclusion: EligibilityCriteriaDetail


# ---------- Endpoint Schema ----------

class Endpoint(BaseModel):
    """
    Represents a study endpoint (primary, secondary, or exploratory).
    """
    name: str = Field(..., description="Endpoint name/description")
    type: Optional[str] = Field(None, description="primary, secondary, or exploratory")
    description: Optional[str] = Field(None, description="Detailed description if available")
    time_frame: Optional[str] = Field(None, description="Assessment timeframe")


# ---------- Intervention Schema ----------

class Intervention(BaseModel):
    """
    Represents a treatment arm or intervention.
    """
    arm_name: str = Field(default="", description="Treatment arm name")
    treatment: str = Field(default="", description="Treatment/drug name")
    dose: str = Field(default="", description="Dose information")
    route: str = Field(default="", description="Route of administration")
    schedule: str = Field(default="", description="Dosing schedule")


# ---------- Section Schema (for segmentation stage) ----------

class SectionExtraction(BaseModel):
    """
    Represents extracted text from a semantic section.
    """
    text: str = Field(default="", description="Verbatim extracted text")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_sections: List[str] = Field(default_factory=list)


class SegmentedSections(BaseModel):
    """
    Result of section segmentation stage.
    """
    sections: Dict[str, SectionExtraction] = Field(
        default_factory=dict,
        description="Keyed by: inclusion_criteria, exclusion_criteria, objectives, endpoints"
    )


# ---------- Top-level Trial Object Schema ----------

class TrialMetadata(BaseModel):
    """Trial identification and status"""
    title: str = Field(default="", description="Official study title")
    phase: str = Field(default="", description="Study phase (e.g., Phase 1, Phase 2/3)")
    status: str = Field(default="", description="Study status (recruiting, completed, etc.)")


class StudyDesign(BaseModel):
    """Study design characteristics"""
    type: str = Field(default="", description="Study type (randomized, observational, etc.)")
    randomization: str = Field(default="", description="randomized, non-randomized, or not specified")
    blinding: str = Field(default="", description="open-label, single-blind, double-blind")
    control: str = Field(default="", description="placebo, active comparator, none")


class Population(BaseModel):
    """Target patient population"""
    indication: str = Field(default="", description="Disease or condition under study")
    disease_stage: str = Field(default="", description="Disease stage if specified")
    biomarkers: List[str] = Field(default_factory=list, description="Required or relevant biomarkers")
    age_range: str = Field(default="", description="Age range (e.g., '18-75 years')")


class EndpointCollection(BaseModel):
    """Study endpoints by type"""
    primary: List[str] = Field(default_factory=list)
    secondary: List[str] = Field(default_factory=list)
    exploratory: List[str] = Field(default_factory=list)


class StudyTimeline(BaseModel):
    """Study duration and visit schedule"""
    treatment_duration: str = Field(default="", description="Total planned treatment length")
    follow_up_duration: str = Field(default="", description="Follow-up period")
    visit_schedule: List[str] = Field(default_factory=list, description="Visit timepoints")


class Safety(BaseModel):
    """Safety monitoring information"""
    known_risks: List[str] = Field(default_factory=list, description="Explicitly mentioned risks")
    monitoring: List[str] = Field(default_factory=list, description="Safety assessments")


class SponsorsLocations(BaseModel):
    """Sponsor and site information"""
    sponsor: str = Field(default="", description="Sponsoring organization")
    locations: List[str] = Field(default_factory=list, description="Study locations")


# ---------- Complete Trial Object ----------

class TrialObject(BaseModel):
    """
    Canonical clinical trial knowledge object.
    
    This schema represents the complete structured representation
    of a clinical trial protocol after extraction.
    """
    trial_metadata: TrialMetadata = Field(default_factory=TrialMetadata)
    study_design: StudyDesign = Field(default_factory=StudyDesign)
    population: Population = Field(default_factory=Population)
    eligibility: EligibilityCriteria
    interventions: List[Intervention] = Field(default_factory=list)
    endpoints: EndpointCollection = Field(default_factory=EndpointCollection)
    study_timeline: StudyTimeline = Field(default_factory=StudyTimeline)
    safety: Safety = Field(default_factory=Safety)
    sponsors_locations: SponsorsLocations = Field(default_factory=SponsorsLocations)

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "trial_metadata": {
                    "title": "A Phase 2 Study of Drug X in NSCLC",
                    "phase": "Phase 2",
                    "status": "Recruiting"
                },
                "eligibility": {
                    "inclusion": {
                        "criteria": [
                            {
                                "id": "INC_01",
                                "text": "Age >= 18 years",
                                "category": "age",
                                "operator": ">=",
                                "value": "18",
                                "confidence": 1.0,
                                "source_evidence": [
                                    {
                                        "section": "4.1 Inclusion Criteria",
                                        "quote": "Males and female subjects aged 18 to 75 years at Screening",
                                        "page": 12
                                    }
                                ]
                            }
                        ],
                        "confidence": 0.95,
                        "source_sections": ["Eligibility Criteria"]
                    },
                    "exclusion": {
                        "criteria": [],
                        "confidence": 0.0,
                        "source_sections": []
                    }
                }
            }
        }
