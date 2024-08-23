from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class LeafClassification(BaseModel):
    code: str
    ucid: str

class LeafClassificationsDict(BaseModel):
    no_classification_data: List[str] = []
    classifications: Dict[str, List[str]] = {}

class Checkpoint(BaseModel):
    last_processed_ucid: Optional[str] = None
