from pydantic import BaseModel

class VersionOut(BaseModel):
    id: int
    note_id: int
    version_number: int
    content_snapshot: str
    editor_id: int
    timestamp: str

class Config:
        from_attributes = True