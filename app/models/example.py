from pydantic import BaseModel

class ExampleRequest(BaseModel):
    text: str

class ExampleResponse(BaseModel):
    original: str
    transformed: str
