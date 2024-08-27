# from pydantic import BaseModel, Field
# from typing import List, Dict, Optional

# class LeafClassification(BaseModel):
#     code: str
#     ucid: str

# class LeafClassificationsDict(BaseModel):
#     no_classification_data: List[str] = []
#     classifications: Dict[str, List[str]] = {}

# class Checkpoint(BaseModel):
#     last_processed_ucid: Optional[str] = None


# models.py
from pydantic import BaseModel
from typing import List, Dict

class LeafClassifications(BaseModel):
    classifications: Dict[str, List[str]]

class Patent(BaseModel):
    url: str
    ucid: str
