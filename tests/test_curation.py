import os
import sys
import pytest
from pydantic import ValidationError

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
from models import CurationResult, CurationDetailsResult, FindingClassification, FindingDetail

def test_curation_result_validation():
    data = {
        "classifications": [
            {
                "id": 1,
                "slug": "test-slug",
                "title": "Test Title",
                "verdict": "do now",
                "why_this_verdict": "Because why not\\nIt is good.",  # Escaped newline
                "touches": "Comp",
                "severity": "minor",
                "confidence": "high",
                "tags": ["tag1"],
                "action_plan": "Test plan\\nStep two."  # Escaped newline
            }
        ],
        "breaking_marker_detected": True
    }
    
    result = CurationResult.model_validate(data)
    assert result.breaking_marker_detected is True
    assert len(result.classifications) == 1
    c = result.classifications[0]
    assert c.slug == "test-slug"
    # Verify escaped newlines were replaced with real newlines by the validator
    assert c.why_this_verdict == "Because why not\nIt is good."
    assert c.action_plan == "Test plan\nStep two."

def test_curation_result_invalid():
    # Missing required field 'slug'
    invalid_data = {
        "classifications": [
            {
                "id": 1,
                "title": "Test Title",
                "verdict": "do now",
                "why_this_verdict": "Why",
                "touches": "Comp",
                "severity": "minor",
                "confidence": "high",
                "tags": [],
                "action_plan": "Plan"
            }
        ],
        "breaking_marker_detected": False
    }
    with pytest.raises(ValidationError):
        CurationResult.model_validate(invalid_data)

def test_curation_details_validation():
    data = {
        "findings": [
            {
                "slug": "test-slug",
                "finding_content": "# Title\\n**Verdict:** parking\\n\\n## Summary\\nSomething.",
                "memory_entry_content": "---\\nname: parked-test-slug\\n---"
            }
        ]
    }
    result = CurationDetailsResult.model_validate(data)
    assert len(result.findings) == 1
    f = result.findings[0]
    assert f.slug == "test-slug"
    assert f.finding_content == "# Title\n**Verdict:** parking\n\n## Summary\nSomething."
    assert f.memory_entry_content == "---\nname: parked-test-slug\n---"
