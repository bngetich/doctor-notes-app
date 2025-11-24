from pydantic import BaseModel
from typing import Literal
from typing import List, Dict, Any


class FhirBundleResponse(BaseModel):
    resourceType: Literal["Bundle"]
    type: str
    entry: List[Dict[str, Any]]