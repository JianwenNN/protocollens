from app.utils.gemini_client import GeminiClient

class ProtocolOrchestrator:
    """
    Orchestrates a multi-stage analysis pipeline for clinical trial protocols.
    Stages:
        1. Section segmentation
        2. Inclusion criteria extraction
        3. Exclusion criteria extraction
    """

    def __init__(self):
        self.client = GeminiClient()

    def _segment_sections(self, protocol_text: str) -> dict:
        """
        Identify and extract major semantic sections from the protocol.
        Returns each section text + source sections + confidence placeholder.
        """
        with open("app/prompts/01_section_segmentation.txt") as f:
            prompt_template = f.read()
        prompt = prompt_template.replace("{protocol_text}", protocol_text)

        result = self.client.extract_json(prompt)

        # Build safe structure
        sections = {}
        for key in ["inclusion_criteria", "exclusion_criteria", "objectives", "endpoints"]:
            text = result.get("sections", {}).get(key, "")
            source = result.get("sections", {}).get(f"{key}_source_sections", [])
            confidence = result.get("sections", {}).get(f"{key}_confidence", 1.0)
            sections[key] = {
                "text": text,
                "confidence": confidence,
                "source_sections": source
            }
        print(sections)
        return sections

    def _extract_inclusion(self, sections: dict) -> dict:
        inclusion_text = sections.get("inclusion_criteria", {}).get("text", "")
        
        if isinstance(inclusion_text, dict) and "text" in inclusion_text:
            inclusion_text = inclusion_text["text"]

        if isinstance(inclusion_text, dict) and "text" in inclusion_text:
            inclusion_text = inclusion_text["text"]
        
        if not inclusion_text:
            return {"text": "", "confidence": 1.0, "source_sections": []}

        with open("app/prompts/02_inclusion_criteria_extraction.txt") as f:
            prompt_template = f.read()
        print(inclusion_text)
        prompt = prompt_template.replace("{text}", inclusion_text)

        result = self.client.extract_json(prompt)

        return {
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0.0),
            "source_sections": result.get("source_sections", [])
        }

    def _extract_exclusion(self, sections: dict) -> dict:
        exclusion_text = sections.get("exclusion_criteria", {}).get("text", "")

        if isinstance(exclusion_text, dict) and "text" in exclusion_text:
            exclusion_text = exclusion_text["text"]

        if isinstance(exclusion_text, dict) and "text" in exclusion_text:
            exclusion_text = exclusion_text["text"]

        if not exclusion_text:
            return {"text": "", "confidence": 1.0, "source_sections": []}

        with open("app/prompts/03_exclusion_criteria_extraction.txt") as f:
            prompt_template = f.read()

        prompt = prompt_template.replace("{text}", exclusion_text)

        result = self.client.extract_json(prompt)

        return {
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0.0),
            "source_sections": result.get("source_sections", [])
        }

    def run(self, protocol_text: str) -> dict:
        """
        Full orchestrator pipeline.
        """
        print("Starting to run.....\n")
        sections = self._segment_sections(protocol_text)
        inclusion = self._extract_inclusion(sections)
        exclusion = self._extract_exclusion(sections)

        return {
            "sections": sections,
            "inclusion_criteria": inclusion,
            "exclusion_criteria": exclusion
        }
