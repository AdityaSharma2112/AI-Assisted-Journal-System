from pydantic import BaseModel,BeforeValidator, Field
from typing import List, Annotated, Optional

# PyObjectId = Annotated[str, BeforeValidator(str)]

class Journal(BaseModel):
    userId: str 
    ambience: str
    text: str 

class Analyze(BaseModel):
    text: str