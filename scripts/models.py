from pydantic import BaseModel, field_validator
from typing import List

class FindingClassification(BaseModel):
    id: int
    slug: str
    title: str
    verdict: str
    why_this_verdict: str
    touches: str
    severity: str
    confidence: str
    tags: List[str]
    action_plan: str
    
    @field_validator('why_this_verdict', 'action_plan', mode='before')
    @classmethod
    def clean_escaped_newlines(cls, v):
        if isinstance(v, str) and '\\n' in v and '\n' not in v:
            return v.replace('\\n', '\n')
        return v

class CurationResult(BaseModel):
    classifications: List[FindingClassification]
    breaking_marker_detected: bool

class FindingDetail(BaseModel):
    slug: str
    finding_content: str
    memory_entry_content: str
    
    @field_validator('finding_content', 'memory_entry_content', mode='before')
    @classmethod
    def clean_escaped_newlines(cls, v):
        if isinstance(v, str) and '\\n' in v and '\n' not in v:
            return v.replace('\\n', '\n')
        return v

class CurationDetailsResult(BaseModel):
    findings: List[FindingDetail]
