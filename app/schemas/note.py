from pydantic import BaseModel, validator
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str

    @validator('title', 'content')
    def must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field must not be empty')
            return v

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CollaboratorAdd(BaseModel):  # New for collaborators
    username: str

class SearchQuery(BaseModel):  # New for search
    query: str  # Search term for title/content