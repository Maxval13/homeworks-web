from pydantic import BaseModel

class CreateAds(BaseModel):
    heading: str
    description: str
    owner: str