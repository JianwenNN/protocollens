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
    
    def run(self, protocol_text: str) -> dict:
        """
        Run the full analysis pipeline on raw protocol text.

        Args:
            protocol_text (str): Full clinical trial protocol text

        Returns:
            dict: Structured analysis result
        """
        sections = self._segment_sections(protocol_text)

        inclusion = self._extract_inclusion(sections)

        return {
            "sections_detected": list(sections.keys()),
            "criteria": inclusion
        }
    
    def _segment_sections(self, protocol_text: str) -> dict:
        """
        Identify and extract major semantic sections from the protocol.
        """
        prompt = open("app/prompts/01_section_segmentation.txt").read()
        
        response = self.client.extract_json(
            prompt.format(protocol_text=protocol_text)
        )
        return response.get("sections",{})
    
    def _extract_inclusion(self, sections: dict) -> list:
        inclusion_text = sections.get("inclusion_criteria", "")
        if not inclusion_text:
            return []
        
        prompt = open("app/prompts/02_inclusion_criteria_extraction.txt").read()
        return self.client.extract_json(prompt.format(text=inclusion_text))["criteria"]