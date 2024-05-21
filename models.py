from pydantic import BaseModel

class Course(BaseModel):
    id: int
    name: str
    
class Discussion(BaseModel):
    id: int
    title: str
    
class Entry(BaseModel):
    message: str
    
class Assignment(BaseModel):
    id: int
    name: str
